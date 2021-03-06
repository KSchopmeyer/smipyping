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
Define the PreviousScans table and provide for import from multiple bases.
This table consists of the following fields
    ScanID = Column(Integer, primary_key=True)
    TimeStamp = Column(DateTime, nullable=False)

"""

from __future__ import print_function, absolute_import

import os
import csv
from ._dbtablebase import DBTableBase
from ._mysqldbmixin import MySQLDBMixin

__all__ = ['PreviousScansTable']


class PreviousScansTable(DBTableBase):
    """
    Abstract class for PreviousScansTable
    This table contains a single entry, the last time a scan was executed.
    """
    key_field = 'ScanID'
    fields = [key_field, 'TimeStamp']
    table_name = 'PreviousScans'

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
            inst = CsvPreviousScansTable(db_dict, db_type, verbose)
        elif db_type == 'mysql':
            inst = MySQLPreviousScansTable(db_dict, db_type, verbose)
        else:
            ValueError('Invalid prevscan table factory db_type %s' % db_type)

        return inst


class CsvPreviousScansTable(PreviousScansTable):
    """
        PreviousScans Table functions for csv based table
    """
    def __init__(self, db_dict, dbtype, verbose):
        super(CsvPreviousScansTable, self).__init__(db_dict, dbtype, verbose)

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


class SQLPreviousScansTable(PreviousScansTable):
    """"
    Table representing the PreviousScans database table
    This table supports a single dictionary that contains the data
    when the table is intialized.
    """

    def __init__(self, db_dict, dbtype, verbose):
        """Pass through to SQL"""
        if verbose:
            print('SQL Database type %s  verbose=%s' % (db_dict, verbose))
        super(SQLPreviousScansTable, self).__init__(db_dict, dbtype, verbose)
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


class MySQLPreviousScansTable(PreviousScansTable, MySQLDBMixin):
    """ Class representing the connection with a mysql database"""
    def __init__(self, db_dict, dbtype, verbose):
        """Read the input file into a dictionary."""
        super(MySQLPreviousScansTable, self).__init__(db_dict, dbtype, verbose)

        self.connectdb(db_dict, verbose)

        self._load_table()
