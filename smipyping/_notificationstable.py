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

"""
Define the Notifications table and provide for import from multiple bases.
This table consists of the following fields
    NotificationID = Column(Integer, primary_key=True)
    NotifyTime = Column(DateTime, nullable=False)
    UserID = Column(Integer, ForeignKey("Users.UserID"))
    TargetID = Column(Integer(11), ForeignKey("Targets.TargetID"))
    Message = Column(String(100), nullable=False)

"""

from __future__ import print_function, absolute_import

import os
import csv
from mysql.connector import Error
from ._dbtablebase import DBTableBase
from ._mysqldbmixin import MySQLDBMixin
from ._common import compute_startend_dates
__all__ = ['NotificationsTable']


class NotificationsTable(DBTableBase):
    """
    Abstract class for NotificationsTable
    This table contains a single entry, the last time a scan was executed.
    """
    key_field = 'NotifyID'
    fields = [key_field, 'NotifyTime', 'UserID', 'TargetID', 'Message']
    table_name = 'Notifications'

    def __init__(self, db_dict, db_type, verbose):
        super(NotificationsTable, self).__init__(db_dict, db_type, verbose)

    @classmethod
    def factory(cls, db_dict, db_type, verbose):
        """Factory method to select subclass based on database type.
           Currently the types sql and csv are supported.

           Returns instance object of the defined type.
        """

        inst = None
        if verbose:
            print('notification factory datafile %s dbtype %s verbose %s'
                  % (db_dict, db_type, verbose))
        if db_type == 'csv':
            inst = CsvNotificationsTable(db_dict, db_type, verbose)
        elif db_type == 'mysql':
            inst = MySQLNotificationsTable(db_dict, db_type, verbose)
        else:
            ValueError('Invalid notifications table factory db_type %s' %
                       db_type)

        if verbose:
            print('Notifications table factory inst %r' % inst)

        return inst


class CsvNotificationsTable(NotificationsTable):
    """
        Notifications Table functions for csv based table
    """
    def __init__(self, db_dict, dbtype, verbose):
        super(CsvNotificationsTable, self).__init__(db_dict, dbtype, verbose)

        fn = db_dict['lastscanfilename']
        self.filename = fn

        # If the filename is not a full directory, the data file must be
        # either in the local directory or the same directory as the
        # config file defined by the db_dict entry directory

        if os.path.isabs(fn):
            if not os.path.isfile(fn):
                ValueError('CSV file %s does not exist ' % fn)
            else:
                self.filename = fn
        else:
            if os.path.isfile(fn):
                self.filename = fn
            else:
                full_fn = os.path.join(db_dict['directory'], fn)
                if not os.path.isfile(full_fn):
                    ValueError('CSV file %s does not exist '
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
                key = int(row['TargetID'])
                if key in result:
                    # duplicate row handling
                    print('ERROR. Duplicate Id in table: %s\nrow=%s' %
                          (key, row))
                    raise ValueError('Input Error. duplicate Id')
                else:
                    result[key] = row
        self.data_dict = result


class SQLNotificationsTable(NotificationsTable):
    """"
    Table representing the Notifications database table
    This table supports a single dictionary that contains the data
    when the table is intialized.
    """

    def __init__(self, db_dict, dbtype, verbose):
        """Pass through to SQL"""
        if verbose:
            print('SQL Database type %s  verbose=%s' % (db_dict, verbose))
        super(SQLNotificationsTable, self).__init__(db_dict, dbtype, verbose)
        self.connection = None

    def db_info(self):
        """
        Display the db info and Return info on the database used as a
        dictionary.
        """
        try:
            print('Database characteristics')
            for key in self.db_dict:
                print('%s: %s' % key, self.db_dict[key])
        except ValueError as ve:
            print('Invalid database configuration exception %s' % ve)
        return self.db_dict


class MySQLNotificationsTable(NotificationsTable, MySQLDBMixin):
    """ Class representing the connection with a mysql database"""
    def __init__(self, db_dict, dbtype, verbose):
        """Read the input file into a dictionary."""
        super(MySQLNotificationsTable, self).__init__(db_dict, dbtype, verbose)

        self.connectdb(db_dict, verbose)

        self._load_table()

    def select_by_daterange(self, start_date, end_date=None,
                            number_of_days=None, target_id=None):
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

          target_id(:term:`integer`):
            Optional Integer defining a target id in the target table. The
            result if filtered by this target id against the TargetID field
            in the Pings record if the value is not `None`.

        Returns:
            List of tuples representing rows in the Pings table. Each entry in
            the return is a field in the Pings table

        Exceptions:
            ValueError if input parameters incorrect.
        """
        start_date, end_date = compute_startend_dates(
            start_date,
            end_date=end_date,
            number_of_days=number_of_days)

        cursor = self.connection.cursor()
        try:
            if target_id is None:
                cursor.execute('SELECT * '
                               'FROM Notifications '
                               'WHERE NotifyTime BETWEEN %s AND %s',
                               (start_date, end_date))
            else:
                cursor.execute('SELECT * '
                               'FROM Notifications WHERE TargetID = %s AND '
                               'NotifyTime BETWEEN %s AND %s',
                               (target_id, start_date, end_date))

            rows = cursor.fetchall()
            return rows

        finally:
            cursor.close()

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
            try:
                if target_id is None:
                    cursor.execute('DELETE  '
                                   'FROM Notifications '
                                   'WHERE NotifyTime BETWEEN %s AND %s',
                                   (start_date, end_date))
                else:
                    cursor.execute('DELETE '
                                   'FROM Notifications WHERE TargetID = %s AND '
                                   'NotifyTime BETWEEN %s AND %s',
                                   (target_id, start_date, end_date))
            except Error as err:
                print(err)
                self.connection.rollback()
                raise

            self.connection.commit()

        finally:
            cursor.close()

    def record_count(self):
        """
        Get count of records in pings table
        """
        cursor = self.connection.cursor()
        query = "SELECT COUNT(*) from Notifications"
        cursor.execute(query)
        res = cursor.fetchone()
        return res[0]
