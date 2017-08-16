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
    ProgramID = Column(Integer, primary_key=True)
    ProgramName = Column(String(15), nullable=False)
    StartDate = Column(Date, nullable=False)
    EndDate = Column(Date, nullable=False)

"""

from __future__ import print_function, absolute_import

import os
import csv
import six
from mysql.connector import MySQLConnection

__all__ = ['ProgramsTable']


class ProgramsTable(object):
    """
    Abstract class for ProgramsTable
    This table contains a single entry, the last time a scan was executed.
    """
    key_field = 'ProgramID'
    fields = [key_field, 'ProgramName', 'StartDate', 'EndDate']
    table_name = 'Program'

    def __init__(self, db_dict, db_type, verbose):
        self.db_dict = db_dict
        self.db_type = db_type
        self.verbose = verbose
        self.data_dict = {}

    def __str__(self):
        """String info on Programstable. TODO. Put more info her"""
        return ('len %s' % len(self.data_dict))

    def __repr__(self):
        """Rep of Companiestable data"""
        return ('Companies db_type %s db len %s' %
                (self.db_type, len(self.data_dict)))

    @classmethod
    def factory(cls, db_dict, db_type, verbose):
        """Factory method to select subclass based on database type.
           Currently the types sql and csv are supported.

           Returns instance object of the defined type.
        """

        inst = None
        if verbose:
            print('notification factory datafile %s dbtype %s verbose %s'
                  % (db_dict,
                     db_type,
                     verbose))
        if db_type == 'csv':
            inst = CsvProgramsTable(db_dict, db_type, verbose)
        elif db_type == 'mysql':
            inst = MySQLProgramsTable(db_dict, db_type, verbose)
        else:
            ValueError('Invalid companiestable factory db_type %s' % db_type)

        if verbose:
            print('Programs table factory inst %r' % inst)

        return inst

    def __contains__(self, record_id):
        """Determine if record_id is in data dictionary."""
        return record_id in self.data_dict

    def __iter__(self):
        """iterator for targets."""
        return six.iterkeys(self.data_dict)

    def iteritems(self):
        """
        Iterate through the property names (in their original lexical case).

        Returns key and value
        """
        for key, val in self.data_dict.iteritems():
            yield (key, val)

    def keys(self):
        """get all of the target_ids as a list"""
        return list(self.data_dict.keys())

    def __getitem__(self, record_id):
        """Return the record for the defined record_id from the targets."""
        return self.data_dict[record_id]

    def __delitem__(self, record_id):
        del self.data_dict[record_id]

    def __len__(self):
        """Return number of targets"""
        return len(self.data_dict)


class CsvProgramsTable(ProgramsTable):
    """
        Programs Table functions for csv based table
    """
    def __init__(self, db_dict, dbtype, verbose):
        super(CsvProgramsTable, self).__init__(db_dict, dbtype, verbose)

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


class SQLProgramsTable(ProgramsTable):
    """"
    Table representing the Programs database table
    This table supports a single dictionary that contains the data
    when the table is intialized.
    """

    def __init__(self, db_dict, dbtype, verbose):
        """Pass through to SQL"""
        if verbose:
            print('SQL Database type %s  verbose=%s' % (db_dict, verbose))
        super(SQLProgramsTable, self).__init__(db_dict, dbtype, verbose)
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


class MySQLProgramsTable(ProgramsTable):
    """ Class representing the connection with a mysql database"""
    def __init__(self, db_dict, dbtype, verbose):
        """Read the input file into a dictionary."""
        super(MySQLProgramsTable, self).__init__(db_dict, dbtype, verbose)

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

            # fetchall returns tuple so need index to fields, not names
            fields = ', '.join(self.fields)
            select_statement = 'SELECT %s FROM %s' % (fields, self.table_name)
            cursor.execute(select_statement)
            rows = cursor.fetchall()
            for row in rows:
                key = row[self.key_field]
                self.data_dict[key] = row

        except Exception as ex:
            raise ValueError('Error: setup sql based targets table %r. '
                             'Exception: %r'
                             % (db_dict, ex))
