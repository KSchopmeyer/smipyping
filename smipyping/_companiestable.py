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
from ._dbtablebase import DBTableBase
from ._logging import get_logger, AUDIT_LOGGER_NAME
from ._mysqldbmixin import MySQLDBMixin

__all__ = ['CompaniesTable']


class CompaniesTable(DBTableBase):
    """
    Abstract class for CompaniesTable
    This table contains a single entry, the last time a scan was executed.
    """
    key_field = 'CompanyID'
    fields = [key_field, 'CompanyName']
    table_name = 'Companies'

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


class MySQLCompaniesTable(CompaniesTable, MySQLDBMixin):
    """ Class representing the connection with a mysql database"""
    def __init__(self, db_dict, dbtype, verbose):
        """Read the input file into a dictionary."""

        super(MySQLCompaniesTable, self).__init__(db_dict, dbtype, verbose)

        self.connectdb(db_dict, verbose)

        self._load_table()

    def insert(self, company_name):
        """
        Write a new record to the programs table of the database at the
        end of the database.

        Exceptions: Exception TODO clarify valid exceptions.

        """
        cursor = self.connection.cursor()

        sql = ("INSERT INTO Companies "
               "(CompanyName) "
               "VALUES (%s)")
        data = company_name

        try:
            # NOTE that the data must be a tuple and it must have the
            # comma if single piece of data
            cursor.execute(sql, (data,))
            self.connection.commit()
            audit_logger = get_logger(AUDIT_LOGGER_NAME)
            audit_logger.info('Companies Table insert '
                              'CompanyName %s', company_name)
        except Exception as ex:
            audit_logger = get_logger(AUDIT_LOGGER_NAME)
            audit_logger.error('Companies Table append '
                               'CompanyName %s Failed. Exception %s',
                               company_name, ex)
            self.connection.rollback()
            raise ex
        finally:
            self._load_table()
            self.connection.close()

    def delete(self, company_id):
        """
        Delete the record defined by user_id
        """
        cursor = self.connection.cursor()

        # TODO: For all deletes, we need to manage table integrity. I.e.
        # check other tables that use company ID before delete.  That should
        # be sql responsibility

        sql = "DELETE FROM Companies WHERE CompanyID=%s"
        try:
            # pylint: disable=unused-variable
            mydata = cursor.execute(sql, (company_id,))  # noqa F841
            self.connection.commit()
            audit_logger = get_logger(AUDIT_LOGGER_NAME)
            audit_logger.info('Companies Table delete CompanyID %s', company_id)
        except Exception as ex:
            audit_logger = get_logger(AUDIT_LOGGER_NAME)
            audit_logger.error('Companies Table delete'
                               'CompanyID %s Failed. Exception %s',
                               company_id, ex)
            self.connection.rollback()
            raise ex
        finally:
            self._load_table()
            self.connection.close()

    def update_fields(self, companyid, changes):
        """
        Update the database record defined by target_id with the dictionary
        of items defined by changes where each item is an entry in the
        target record. Update does NOT test if the new value is the same
        as the original value.
        """
        cursor = self.connection.cursor()
        # dynamically build the update sql based on the changes dictionary
        set_names = "SET "
        values = []
        comma = False
        for key, value in changes.items():
            if comma:
                set_names = set_names + ", "
            else:
                comma = True
            set_names = set_names + "{0} = %s".format(key)
            values.append(value)

        values.append(companyid)
        sql = "Update Companies " + set_names

        # append targetid component
        sql = sql + " WHERE CompanyID=%s"

        change_str = ""
        for key, value in changes.items():
            change_str += "%s:%s " % (key, value)
        try:
            cursor.execute(sql, tuple(values))
            self.connection.commit()
            audit_logger = get_logger(AUDIT_LOGGER_NAME)

            audit_logger.info('CompaniesTable CompanyId %s,update fields %s',
                              companyid, change_str)
        except Exception as ex:
            audit_logger = get_logger(AUDIT_LOGGER_NAME)
            audit_logger.error('CompaniesTable CompanyId %s failed SQL update. '
                               'SQL=%s Changes %s exception %s',
                               companyid, sql, change_str, ex)
            self.connection.rollback()
            raise ex
        finally:
            self._load_table()
            cursor.close()
