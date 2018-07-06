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
Define the Companies table and provide for import from multiple bases.

  `CompanyID` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `CompanyName` varchar(30) NOT NULL,



"""

from __future__ import print_function, absolute_import

import os
import csv
from mysql.connector import MySQLConnection
from ._dbtablebase import DBTableBase

__all__ = ['CompaniesTable']


class CompaniesTable(DBTableBase):
    """
    Abstract class for CompaniesTable
    This table contains a single entry, the last time a scan was executed.
    """
    key_field = 'CompanyID'
    fields = [key_field, 'CompanyName']
    table_name = 'Companies'

    def __init__(self, db_dict, db_type, verbose):
        super(CompaniesTable, self).__init__(db_dict, db_type, verbose)

    def __str__(self):
        """String info on Companiestable. TODO. Put more info her"""
        return ('len %s' % len(self.data_dict))

    def __repr__(self):
        """Rep of Companies table data"""
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
            print('Companies factory table %s dbtype %s verbose %s'
                  % (db_dict, db_type, verbose))
        if db_type == 'csv':
            inst = CsvCompaniesTable(db_dict, db_type, verbose)
        elif db_type == 'mysql':
            inst = MySQLCompaniesTable(db_dict, db_type, verbose)
        else:
            ValueError('Invalid companiestable factory db_type %s' % db_type)

        if verbose:
            print('Companies table factory inst %r' % inst)

        return inst


class CsvCompaniesTable(CompaniesTable):
    """
        Companies Table functions for csv based table
    """
    def __init__(self, db_dict, dbtype, verbose):
        super(CsvCompaniesTable, self).__init__(db_dict, dbtype, verbose)

        fn = db_dict['companiesfilename']
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
                    raise ValueError('Input Error. duplicate Id in table: %s'
                                     '\nrow=%s' % (key, row))
                else:
                    result[key] = row
        self.data_dict = result


class SQLCompaniesTable(CompaniesTable):
    """"
    Table representing the Companies database table
    This table supports a single dictionary that contains the data
    when the table is intialized.
    """

    def __init__(self, db_dict, dbtype, verbose):
        """Pass through to SQL"""
        if verbose:
            print('SQL Database type %s  verbose=%s' % (db_dict, verbose))
        super(SQLCompaniesTable, self).__init__(db_dict, dbtype, verbose)
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


class MySQLCompaniesTable(CompaniesTable):
    """ Class representing the connection with a mysql database"""
    def __init__(self, db_dict, dbtype, verbose):
        """Read the input file into a dictionary."""

        super(MySQLCompaniesTable, self).__init__(db_dict, dbtype, verbose)

        try:
            connection = MySQLConnection(host=db_dict['host'],
                                         database=db_dict['database'],
                                         user=db_dict['user'],
                                         password=db_dict['password'])

            if connection.is_connected():
                self.connection = connection
                if self.verbose:
                    print('sql db connection established. host %s, db %s' %
                          (db_dict['host'], db_dict['database']))
            else:
                if self.verbose:
                    print('SQL database connection failed. host %s, db %s' %
                          (db_dict['host'], db_dict['database']))
                raise ValueError('Connection to host %s database %s failed.' %
                                 (db_dict['host'], db_dict['database']))
            self.connection = connection
        except Exception as ex:
            raise ValueError('Could not connect to sql database %r. '
                             ' Exception: %r'
                             % (db_dict, ex))

        self._load()

    def _load(self):
        """
        Load the internal dictionary from the database.
        """
        try:
            # python-mysql-connector-dictcursor  # noqa: E501
            cursor = self.connection.cursor(dictionary=True)

            # fetchall returns tuple so need index to fields, not names
            fields = ', '.join(self.fields)
            sql = 'SELECT %s FROM %s' % (fields, self.table_name)
            cursor.execute(sql)
            rows = cursor.fetchall()
            for row in rows:
                key = row[self.key_field]
                self.data_dict[key] = row

        except Exception as ex:
            raise ValueError('Error: setup sql based targets table %r. '
                             'Exception: %r'
                             % (self.db_dict, ex))

    def append(self, company_name):
        """
        Write a new record to the programs table of the database at the
        end of the database.

        Exceptions: Exception TODO clarify valid exceptions.

        """
        cursor = self.connection.cursor()

        # TODO insert new company fails  and inserts %s rather than name
        #      This is an issue only with single value table. Removing the
        #      quotes resutls in failure with SQL syntax programming error
        #      1064
        sql = ("INSERT INTO Companies "
               "(CompanyName) "
               "VALUES ('%s')")
        data = (company_name)

        try:
            cursor.execute(sql, data)
            self.connection.commit()
        except Exception as ex:
            print('Companies table.append failed: exception %r' % ex)
            self.connection.rollback()
            raise ex
        finally:
            self._load()
            self.connection.close()

    def delete(self, company_id):
        """
        Delete the record defined by user_id
        """
        cursor = self.connection.cursor()

        # TODO: For all deletes, we need to manage table integrity

        sql = "DELETE FROM Companies WHERE CompanyID=%s"
        try:
            # TODO what is return on execute??
            # pylint: disable=unused-variable
            mydata = cursor.execute(sql, (company_id,))  # noqa F841
            self.connection.commit()
        except Exception as ex:
            print('Companies table.delete failed: exception %r' % ex)
            self.connection.rollback()
            raise ex
        finally:
            self._load()
            self.connection.close()
