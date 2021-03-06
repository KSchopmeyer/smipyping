#!/usr/bin/env python
# (C) Copyright 2017 Inova Development Inc.
# All Rights Reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Define the user base and its data"""

# TODO change ip_address to hostname where host name is name : port

from __future__ import print_function, absolute_import

import datetime
import csv
import os
import six

from mysql.connector import Error as mysqlerror
from ._logging import AUDIT_LOGGER_NAME, get_logger
from ._dbtablebase import DBTableBase
from ._mysqldbmixin import MySQLDBMixin
from ._common import compute_startend_dates

__all__ = ['PingsTable']


class PingsTable(DBTableBase):
    """
    `PingID` int(11) unsigned NOT NULL AUTO_INCREMENT,
    `TargetID` int(11) unsigned NOT NULL,
    `Timestamp` datetime NOT NULL,
    `Status` varchar(255) NOT NULL,
    """
    key_field = 'PingID'
    fields = [key_field, 'targetID', 'Timestamp', 'Status']
    table_name = 'Pings'

    @classmethod
    def factory(cls, db_dict, db_type, verbose):
        """Factory method to select subclass based on database type.
           Currently the types sql and csv are supported.

           Returns instance object of the defined type.
        """

        inst = None
        if verbose:
            print('pingdata factory datafile %s dbtype %s verbose %s'
                  % (db_dict, db_type, verbose))
        if db_type == ('csv'):
            inst = CsvPingsTable(db_dict, db_type, verbose)

        elif db_type == ('mysql'):
            inst = MySQLPingsTable(db_dict, db_type, verbose)
        else:
            ValueError('Invalid pingstable factory db_type %s' % db_type)

        if verbose:
            print('Resulting pingtable factory inst %r' % inst)

        return inst


class CsvPingsTable(PingsTable):
    """
        Ping Table functions for csv based table
    """
    def __init__(self, db_dict, dbtype, verbose):
        super(CsvPingsTable, self).__init__(db_dict, dbtype, verbose)
        fn = db_dict['pingsfilename']
        self.filename = fn

        print('init csvpingtable %s %s' % (self.filename, dbtype))

        # If the filename is not a full directory, the data file must be
        # either in the local directory or the same directory as the
        # config file defined by the db_dict entry directory
        if os.path.isabs(fn):
            if not os.path.isfile(fn):
                ValueError('CSV lastscan data file %s does not exist ' % fn)
            else:
                self.filename = fn
        else:
            if os.path.isfile(fn):
                self.filename = fn
            else:
                full_fn = os.path.join(db_dict['directory'], fn)
                if not os.path.isfile(full_fn):
                    ValueError('CSV pingtable file %s does not exist '
                               'in local directory or config directory %s' %
                               (fn, db_dict['directory']))
                else:
                    self.filename = full_fn

        with open(self.filename) as input_file:
            reader = csv.DictReader(input_file)
            # create dictionary (id = key) with dictionary for
            # each set of entries
            result = {}
            for row in reader:
                key = int(row['PingID'])
                if key in result:
                    # duplicate row handling
                    print('ERROR. Duplicate Id in table: %s\nrow=%s' %
                          (key, row))
                    raise ValueError('Input Error. duplicate Id')
                else:
                    result[key] = row

        self.data_dict = result

    def get_last_ping_id(self):  # pylint: disable=no-self-use
        """Get the newest ping by timestamp"""
        with open(file, "rb") as f:
            f.readline()               # Read the first line.
            f.seek(-2, 2)              # Jump to the second last byte.
            while f.read(1) != b"\n":  # Until EOL is found...
                f.seek(-2, 1)          # ...jump back, read byte plus one more.
            last = f.readline()        # Read last line.
            return last

    def append(self, target_id, timestamp, status):
        """ Write a single record into the table"""
        ping_id = self.get_last_ping_id()
        print('csv ping %s %s %s %s' % (ping_id, target_id, timestamp,
                                        self.filename))
        with open(self.filename, 'a') as ping_file:
            print("%s,%s,%s,'%s'" % (ping_id, target_id,
                                     datetime.datetime.now(),
                                     status), file=ping_file)


class SQLPingsTable(PingsTable):
    """
    PingsTable subclass for SQL. Implements functionality for general
    SQL table usage.
    """
    def __init__(self, db_dict, dbtype, verbose):
        """Init for sqlpingtable class"""
        super(SQLPingsTable, self).__init__(db_dict, dbtype, verbose)

        self.connection = None

    def db_info(self):
        """
        Display the db info and Return info on the database used as a
        dictionary.
        """
        try:
            print('database characteristics')
            for key in self.db_dict:
                print('%s: %s' % key, self.db_dict[key])
        except ValueError as ve:
            print('Invalid database configuration exception %s' % ve)
        return self.db_dict

    def get_data_for_day(self, year, month, day_of_month):
        """Get from the database the pings for a single day"""
        cursor = self.connection.cursor(dictionary=True)

        # fetchall returns tuple so need index to fields, not names

        select_statement = 'SELECT * FROM %s WHERE YEAR(Timestamp) = %s ' \
                           'and MONTH(Timestamp) = %s and ' \
                           'DAYOFMONTH(Timestamp) = %s' % \
                           (self.table_name, year, month, day_of_month)
        cursor.execute(select_statement)
        rows = cursor.fetchall()

        return rows


class MySQLPingsTable(SQLPingsTable, MySQLDBMixin):
    """
    Specialization for mysql databases. Specializes connection, etc for
    these databases.
    """
    def __init__(self, db_dict, dbtype, verbose):
        """Read the input file into a dictionary."""
        super(MySQLPingsTable, self).__init__(db_dict, dbtype, verbose)

        self.connectdb(db_dict, verbose)

    # This does not preload the pings table because it is probably too
    # big and primary functions are to append and select particular
    # entries

    # TODO - I do not believe we use this method
    def get_last_ping_id(self):
        """
        Get the id of the last inserted record
        """
        # TODO this probably gets last inserted, not last in table. They should
        # be the same.
        cursor = self.connection.cursor()
        last_ping_id = cursor.lastrowid
        return last_ping_id

    def get_last_timestamped(self):
        """
            Get the set of records with the last timestamp for all
            targets
        """
        last_ping = self.get_newest_ping()
        last_timestamp = last_ping[2]

        cursor = self.connection.cursor()
        try:
            # MySQL fails on Timestamp = %s but works with the BETWEEN
            # syntax/
            cursor.execute('SELECT * '
                           'FROM Pings WHERE Timestamp  BETWEEN %s AND %s',
                           (last_timestamp, last_timestamp))

            rows = cursor.fetchall()
            return rows
        except Exception as ex:
            print('get_last_timestamped failed %s' % ex)
            raise ex
        finally:
            self.close_connection()

    def record_count(self):
        """
        Get count of records in pings table
        """
        cursor = self.connection.cursor()
        query = "SELECT COUNT(*) from Pings"
        cursor.execute(query)
        res = cursor.fetchone()
        return res[0]

    def close_connection(self):
        """Close the connection"""
        if self.connection:
            self.connection.close()

    def select_by_daterange(self, start_date, end_date=None,
                            number_of_days=None, targetids=None):
        """
        Select records between two timestamps and return the set of
        records selected

        Parameters:

          start_date(:class:`py:datetime.datetime` or `None`):
            The starttime for the select statement. If `None' the oldest
            timestamp in the database is used.

          end_date(:class:`py:datetime.datetime` or `None`):
            The end datetime for the scan.  If `None`, the current date time
            is used

          days(:term:`py:integer`)
            Number of days from startdate to gather. If end_date is set also
            this is invalid.

          targetids(:term:`integer`): Optional integer or list of integers
          defining targetids in the target table. The result is filtered by
          these target ids against the TargetID field in the Pings record if
          the value is not `None`.

          If the value is None the result is not filtered by targetid

        Returns:
            List of tuples representing rows in the Pings table. Each entry in
            the return is a field in the Pings table

        Exceptions:
            ValueError if input parameters incorrect.
        """
        start_date, end_date = compute_startend_dates(
            start_date,
            end_date=end_date,
            number_of_days=number_of_days,
            oldest_date=self.get_oldest_ping()[2])

        cursor = self.connection.cursor()
        try:
            if targetids is None:
                sql = 'SELECT * ' \
                      'FROM Pings WHERE Timestamp BETWEEN %s AND %s'
                data = (start_date, end_date)

            elif isinstance(targetids, (list, tuple)):
                for i in targetids:
                    if not isinstance(i, int):
                        raise ValueError("TargetTable:select_by_daterange "
                                         "targetid must be integer or "
                                         "iterable of integer. %s not "
                                         "allowed" % targetids)
                # create string of %s,%s ...
                ids = ",".join(['%s'] * len(targetids))
                sql = 'SELECT * ' \
                      'FROM Pings WHERE TargetID in (%s)' % ids
                sql += ' AND Timestamp BETWEEN %s AND %s'
                data = (targetids, start_date, end_date)

            elif isinstance(targetids, int):
                sql = 'SELECT * ' \
                      'FROM Pings WHERE TargetID = %s AND ' \
                      'Timestamp BETWEEN %s AND %s'
                data = (targetids, start_date, end_date)
            else:
                raise ValueError("TargetTable:select_by_daterange targetid "
                                 "must be integer or iterable of integer. "
                                 "%s not allowed" % targetids)

            cursor.execute(sql, data)
            rows = cursor.fetchall()
            return rows
        except mysqlerror as err:
            audit_logger = get_logger(AUDIT_LOGGER_NAME)
            audit_logger.error('PingsTable SELECT failed. SQL=%s. '
                               'data=%s. Exception %s: %s', sql, data,
                               err.__class__.__name__, err)
            raise

        finally:
            cursor.close()

    def get_status_by_id(self, start_date, end_date=None, number_of_days=None,
                         target_id=None):
        """
        Select by date range and create a dictionary by id and status. If
        target_id is provided it acts as a filter.

        return:
           Dictionary where:
               target_id is key
               Value is dictionary where key is status and value is count
        """
        rows = self.select_by_daterange(start_date, end_date=end_date,
                                        number_of_days=number_of_days,
                                        targetids=target_id)

        # dictionary by id with subdictionary by status
        status_dict = {}
        for row in rows:
            target_id = row[1]
            status = row[3]
            if target_id in status_dict:
                x = status_dict[target_id]
                if status in x:
                    x[status] += 1
                else:
                    x[status] = 1
                status_dict[target_id] = x
            else:
                status_dict[target_id] = {status: 1}
        return status_dict

    def get_percentok_by_id(self, start_date, end_date=None,
                            number_of_days=None, target_id=None):
        """
        Create dictionary of percent OK and total pings by target_id

        Parameters:
            TODO

        Returns:
            dictionary where keys are target_id and value is tuple of
            percent of OK responses, count of OK responses  and total number
            of resposnes for the target_id
        """
        status_dict = self.get_status_by_id(
            start_date,
            end_date=end_date,
            number_of_days=number_of_days,
            target_id=target_id)

        # create dictionary by target_id with value of [oks, total]
        percent_dict = {}
        for target_id_, status_dict in six.iteritems(status_dict):
            ok_count = 0
            total = 0
            for key, status_count in six.iteritems(status_dict):
                if key == 'OK':
                    ok_count = status_count
                total += status_count
            percent_ok = (ok_count * 100) / total
            percent_dict[target_id_] = (percent_ok, ok_count, total)
        return percent_dict

    def delete_by_daterange(self, start_date, end_date, target_id=None):
        """
        Deletes records from the database based on start_date, end_date and
        optional target_id. This requires start date and end date explicitly
        and does not allow number of days paramter

        Parameters:

          start_date(:class:`py:datetime.datetime` or `None`):
            The starttime for the select statement. If `None' the oldest
            timestamp in the database is used.

          end_date(:class:`py:datetime.datetime` or `None`):
            The end datetime for the scan.

          Target_id: Optional target it to filter delete request.

        Exceptions:
            Database error if the execute failed.

        """
        cursor = self.connection.cursor()

        try:
            if target_id is None:
                sql = 'DELETE  ' \
                      'FROM Pings ' \
                      'WHERE Timestamp BETWEEN %s AND %s'
                data = (start_date, end_date)

            else:
                sql = 'DELETE ' \
                      'FROM Pings WHERE TargetID = %s AND ' \
                      'Timestamp BETWEEN %s AND %s'
                data = (target_id, start_date, end_date)

            cursor.execute(sql, data)
            self.connection.commit()

            audit_logger = get_logger(AUDIT_LOGGER_NAME)
            target_id_str = "" if not target_id else " for TargetID %s " % \
                            target_id
            audit_logger.info('PingsTable Delete %s by daterange from=%s '
                              'to=%s', target_id_str, start_date, end_date)

        except mysqlerror as err:
            self.connection.rollback()
            audit_logger = get_logger(AUDIT_LOGGER_NAME)
            audit_logger.error('PingsTable Delete failed SQL update. SQL=%s. '
                               'data=%s. Exception %s: %s', sql, data,
                               err.__class__.__name__, err)
            raise

        finally:
            cursor.close()

    # TODO this always returns an error and an incomplete end-date. the
    # input is correct however. Appears to be an issue with the SQL syntac
    # and in particular, the combination of COUNT and the WHERE clause
    def count_by_daterange(self, start_date, end_date=None,
                           number_of_days=None, target_id=None):
        """
        Counts the number of records by date range and ID

        """
        cursor = self.connection.cursor()

        start_date, end_date = compute_startend_dates(
            start_date,
            end_date=end_date,
            number_of_days=number_of_days,
            oldest_date=self.get_oldest_ping()[2])

        try:
            if target_id is None:
                cursor.execute('SELECT COUNT(*)  '
                               'FROM Pings '
                               'WHERE Timestamp BETWEEN %s AND %s',
                               (start_date, end_date))
            else:
                cursor.execute('SELECT COUNT(*) '
                               'FROM Pings '
                               'WHERE TargetID = %s AND '
                               'Timestamp BETWEEN %s AND %s',
                               (target_id, start_date, end_date))

            result = cursor.fetchone()
            return result[0]

        except Exception as ex:
            print('COUNT_BY_DATERANGE exception %s' % ex)
            raise ex
        finally:
            cursor.close()

    def get_oldest_ping(self, target_id=None):
        """Get the first record in the database. If target_id set, get
           oldest for this target_id.

           Parameters:
             target_id(:term:`integer`)
                Optional target_id for record.  If `None` oldest for
                Pings table returned.  If valid target, the oldest ping
                record for this targe returned.

            Returns:
                Returns the first record in the DB or the first record in the
                DB for the defined targetID. This returns the complete row
        """
        cursor = self.connection.cursor()

        try:
            if target_id is None:
                cursor.execute('SELECT * FROM Pings LIMIT 0, 1')
            else:
                cursor.execute('SELECT * FROM Pings WHERE TargetID = %s '
                               'LIMIT 0, 1',
                               target_id)
            # TODO optimize by using server side cursor if that works
            row = cursor.fetchone()
            if row:
                return row
            else:
                if target_id:
                    raise ValueError('TargetId %s not in Pings database.' %
                                     target_id)
                else:
                    raise ValueError('Error getting database oldest record. No'
                                     'records')

        finally:
            cursor.close()

    def get_newest_ping(self, target_id=None):
        """
        Get the record that represents the newest entry in the ping table
        """
        cursor = self.connection.cursor()

        try:
            if target_id is None:
                cursor.execute(
                    'SELECT * FROM Pings ORDER BY PingID DESC LIMIT 1')
            else:
                cursor.execute(
                    'SELECT * FROM Pings ORDER BY PingID DESC LIMIT 1'
                    ' WHERE TargetID = %s', target_id)

            # TODO optimize by using server side cursor if that works
            row = cursor.fetchone()
            if row:
                return row
            else:
                if target_id:
                    raise ValueError('TargetId %s not in Pings database.' %
                                     target_id)
                else:
                    raise ValueError('Error getting database oldest record. No'
                                     'records')

        finally:
            cursor.close()

    def append(self, target_id, status, timestamp):
        """
        Write a new record to the database containing the target_id,
        scan status and a timestamp

        Parameters:
          target_id :term:`integer`
            The database target_id of the wbem_server for which the
            status is being reported.

          status (:term:`string`):
            String containing the status of the last test of the wbem
            server.

          timestamp (TODO)
            The time stamp for the scan.  NOTE: This may not be exactly the
            time at which the last scan was run since the timestamp serves
            as a gathering point for scans so the same time stamp may be
            reported for a number of target_ids
        """
        cursor = self.connection.cursor()
        if status.type == 'OK' or status.type == 'PingFail':
            status_str = '%s' % (status.type)
        else:
            status_str = '%s %s' % (status.type, status.exception)
        sql = ("INSERT INTO Pings "
               "(TargetID, Timestamp, Status) "
               "VALUES (%s, %s, %s)")
        data = (target_id, timestamp, status_str)

        try:
            cursor.execute(sql, data)
            self.connection.commit()
            audit_logger = get_logger(AUDIT_LOGGER_NAME)
            audit_logger.info('PingsTable INSERT sql %s values %s ', sql, data)
        except mysqlerror as ex:
            self.connection.rollback()
            audit_logger = get_logger(AUDIT_LOGGER_NAME)
            audit_logger.error('PingsTable INSERT failed SQL update. SQL=%s. '
                               'data=%s. Exception %s: %s', sql, data,
                               ex.__class__.__name__, ex)
            raise ex
        finally:
            cursor.close()
