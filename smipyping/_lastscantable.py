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
Define the LastScanTable.  This is a simpletable to just record a single value,
the time of the last scan.  It can be used to gather information about a
complete scan of the servers in a single request.

There is only a single function, the last scan update that updates the
time to the time provided by an input parameter.

"""

from __future__ import print_function, absolute_import

import os
import csv
from mysql.connector import MySQLConnection

#
#  ScanID=1, LastScan=2016-10-28 09:00:01
#


class LastScanTable(object):
    """
    Abstract class for LastScanTable
    This table contains a single entry, the last time a scan was executed.
    """
    def __init__(self, db_dict, db_type, verbose):
        self.db_dict = db_dict
        self.db_type = db_type
        self.verbose = verbose
        self.data_dict = {}
        self.last_scan = None

    def __str__(self):
        """String info on LastScantable. TODO. Put more info her"""
        return ('len %s' % len(self.data_dict))

    def __repr__(self):
        """Rep of lastscan data"""
        return ('LastScan db_type %s db_dict %s' %
                (self.db_type, self.data_dict))

    @classmethod
    def factory(cls, db_dict, db_type, verbose):
        """Factory method to select subclass based on database type.
           Currently the types sql and csv are supported.

           Returns instance object of the defined type.
        """

        inst = None
        if verbose:
            print('lastscan factory datafile %s dbtype %s verbose %s'
                  % (db_dict,
                     db_type,
                     verbose))
        if db_type == 'csv':
            inst = CsvLastScanTable(db_dict, db_type, verbose)
        elif db_type == 'mysql':
            inst = MySQLLastScanTable(db_dict, db_type, verbose)
        else:
            ValueError('Invalid lastscantable factory db_type %s' % db_type)

        if verbose:
            print('Resulting last scan table factory inst %r' % inst)

        return inst


class CsvLastScanTable(LastScanTable):
    """
        LastScan Table functions for csv based table
    """
    def __init__(self, db_dict, dbtype, verbose):
        super(CsvLastScanTable, self).__init__(db_dict, dbtype, verbose)

        fn = db_dict['lastscanfilename']
        self.filename = fn

        # If the filename is not a full directory, the data file must be
        # either in the local directory or the same directory as the
        # config file defined by the db_dict entry directory
        print('csv last scan file %s' % self.filename)

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
            rows = 0
            for row in reader:
                rows += 1
                assert(rows < 2)
                self.last_ping = row['LastPing']
                self.data_dict = row


class SQLLastScanTable(LastScanTable):

    def __init__(self, db_dict, dbtype, verbose):
        """Pass through to SQL"""
        if verbose:
            print('SQL Database type %s  verbose=%s' % (db_dict, verbose))
        super(SQLLastScanTable, self).__init__(db_dict, dbtype, verbose)
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


class MySQLLastScanTable(LastScanTable):

    def __init__(self, db_dict, dbtype, verbose):
        """Read the input file into a dictionary."""

        super(MySQLLastScanTable, self).__init__(db_dict, dbtype, verbose)

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
        try:
            # python-mysql-connector-dictcursor  # noqa: E501
            cursor = connection.cursor(dictionary=True)

            cursor.execute("SELECT LastScan FROM LastScan WHERE ScanID = 1")
            rows = cursor.fetchall()
            assert(len(rows) == 1)
            for row in rows:
                self.last_scan = row['LastScan']
                self.data_dict = row
        except Exception as ex:
            raise ValueError('Could not create LastScan table %r Exception: %r'
                             % (rows, ex))

    def update(self, timestamp):
        "UPDATE LastScan SET LastScan = '$DateTime' WHERE ScanID = 1"
        pass
