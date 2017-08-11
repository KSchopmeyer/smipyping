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

import os
import csv
import datetime
from mysql.connector import MySQLConnection

__all__ = ['PingTable']


class PingTable(object):
    """
    `PingID` int(11) unsigned NOT NULL AUTO_INCREMENT,
    `TargetID` int(11) unsigned NOT NULL,
    `Timestamp` datetime NOT NULL,
    `Status` varchar(255) NOT NULL,
    """
    key_field = 'PingID'
    fields = [key_field, 'targetID', 'Timestamp', 'Status']
    table_name = 'Pings'

    def __init__(self, db_dict, db_type, verbose):
        """Constructor for PingTable"""
        self.db_dict = db_dict
        self.verbose = verbose
        self.db_type = db_type
        self.data_dict = {}

    @classmethod
    def factory(cls, db_dict, db_type, verbose):
        """Factory method to select subclass based on database type.
           Currently the types sql and csv are supported.

           Returns instance object of the defined type.
        """

        inst = None
        if verbose:
            print('targetdata factory datafile %s dbtype %s verbose %s'
                  % (db_dict,
                     db_type,
                     verbose))
        if db_type == ('csv'):
            inst = CsvPingTable(db_dict, db_type, verbose)

        elif db_type == ('mysql'):
            inst = MySQLPingTable(db_dict, db_type, verbose)
        else:
            ValueError('Invalid pingtable factory db_type %s' % db_type)

        if verbose:
            print('Resulting pingtable factory inst %r' % inst)

        return inst

    def __str__(self):
        """String info on tpingtable. TODO. Put more info her"""
        return ('count=%s' % len(self.data_dict))

    def __repr__(self):
        """Rep of pings data. This is really an empty dictionary"""
        return ('Pingtable db_type %s, db_dict %s rep count=%s' %
                (self.db_type, self.db_dict, 0))


class CsvPingTable(PingTable):
    """
        Ping Table functions for csv based table
    """
    def __init__(self, db_dict, dbtype, verbose):
        super(CsvPingTable, self).__init__(db_dict, dbtype, verbose)
        fn = db_dict['filename']
        self.filename = fn

        print('init csvpingtable %s %s' % (self.filename, self.args))
        print('init csvlastscantable %s %s' % (self.filename, self.args))

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

    def get_last_ping_id(self):
        with open(file, "rb") as f:
            first = f.readline()      # Read the first line.
            f.seek(-2, 2)             # Jump to the second last byte.
            while f.read(1) != b"\n":  # Until EOL is found...
                f.seek(-2, 1)         # ...jump back, read byte plus one more.
            last = f.readline()       # Read last line.
            return last

    def append(self, target_id, status):
        """ Write a single record into the table"""
        ping_id = self.get_last_ping_id()
        with open(self.filename, 'a') as ping_file:
            print("%s,%s,%s,'%s'" % (ping_id, target_id,
                                     datetime.datetime.now(),
                                     status), file=ping_file)


class SQLPingTable(PingTable):
    def __init__(self, db_dict, dbtype, verbose):
        """Init for sqlpingtable class"""
        super(SQLPingTable, self).__init__(db_dict, dbtype, verbose)

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


class MySQLPingTable(PingTable):
    def __init__(self, db_dict, dbtype, verbose):
        """Read the input file into a dictionary."""
        super(MySQLPingTable, self).__init__(db_dict, dbtype, verbose)

        try:
            connection = MySQLConnection(host=db_dict['host'],
                                         database=db_dict['database'],
                                         user=db_dict['user'],
                                         password=db_dict['password'])

            if connection.is_connected():
                print('sql db connection established. host %s, db %s' %
                      (db_dict['host'], db_dict['database']))
                self.connection = connection
            else:
                print('SQL database connection failed. host %s, db %s' %
                      (db_dict['host'], db_dict['database']))
                raise ValueError('Connection to database failed')
            self.connection = connection
        except Exception as ex:
            raise ValueError('Could not connect to sql database %r. '
                             ' Exception: %r'
                             % (db_dict, ex))
        # This does not preload the pings table because it is probably too
        # big and primary functions are to append and select particular
        # entries

    def get_last_ping_id(self):
        """
        Get the id of the last inserted record
        """
        # TODO this probably gets last inserted, not last in table
        cursor = self.connection.cursor()
        last_ping_id = cursor.lastrowid
        return last_ping_id

    def select_for_timestamp(self, timestamp):
        #TODO
        pass

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
        try:

            timestamp = \
                datetime.datetime.fromtimestamp(timestamp).strftime(
                    '%Y-%m-%d %H:%M:%S')
            add_record = ("INSERT INTO Pings "
                          "(TargetID, Timestamp, Status) "
                          "VALUES (%s %s %s")
            data = (target_id, timestamp, status)
            cursor.execute(add_record, data)
            self.connection.commit()
        except:
            self.connection.rollback()
        cursor.close()
