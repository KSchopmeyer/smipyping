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
from ._dbtablebase import DBTableBase
from ._mysqldbmixin import MySQLDBMixin

#
#  ScanID=1, LastScan=2016-10-28 09:00:01
#


class LastScanTable(DBTableBase):
    """
    Abstract class for LastScanTable
    This table contains a single entry, the last time a scan was executed.
    """
    key_field = 'ScanID'
    fields = [key_field, 'LastScan']
    table_name = 'LastScan'
    def __init__(self, db_dict, db_type, verbose):
        super(LastScanTable, self).__init__(db_dict, db_type, verbose)

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
                  % (db_dict, db_type, verbose))
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


class MySQLLastScanTable(LastScanTable, MySQLDBMixin):

    def __init__(self, db_dict, dbtype, verbose):
        """Read the input file into a dictionary."""

        super(MySQLLastScanTable, self).__init__(db_dict, dbtype, verbose)

        self.connectdb(db_dict, verbose)

        self._load_table()

    def update(self, timestamp):
        "UPDATE LastScan SET LastScan = '$DateTime' WHERE ScanID = 1"
        pass
