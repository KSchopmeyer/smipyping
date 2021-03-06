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
import datetime
from mysql.connector import Error as mysqlerror
from ._dbtablebase import DBTableBase
from ._mysqldbmixin import MySQLDBMixin
from ._pingstable import PingsTable


from ._logging import AUDIT_LOGGER_NAME, get_logger

__all__ = ['ProgramsTable']


class ProgramsTable(DBTableBase):
    """
    Abstract class for ProgramsTable
    This table contains a single entry, the last time a scan was executed.
    """
    key_field = 'ProgramID'
    fields = [key_field, 'ProgramName', 'StartDate', 'EndDate']
    table_name = 'Program'

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
            inst = CsvProgramsTable(db_dict, db_type, verbose)
        elif db_type == 'mysql':
            inst = MySQLProgramsTable(db_dict, db_type, verbose)
        else:
            ValueError('Invalid programs table factory db_type %s' % db_type)

        if verbose:
            print('Programs table factory inst %r' % inst)

        return inst

    # TODO: future, combine current and for_date into a single method
    def current(self):
        """Return record for current program if one exists.

        Returns:
            Program record of current program or None if there is no
            current program. The current program is one where the date today
            is ge the program start date and lt the program end date.

        Exceptions:
            ValueError if there is no current program
        """
        today = datetime.date.today()
        for program_id in self:
            pgm = self[program_id]
            if today <= pgm['EndDate'] and today >= pgm['StartDate']:
                return pgm

        raise ValueError("There is no current program")

    def for_date(self, date):
        """Return record for program containing date defined in variable.

        Parameters:
          date(:class:`py:datetime.datetime`)
            Gets program for the defined datetime or date.

        Returns:
            Program record of program or None if there is no
            program for `date`. The program is one where the date today
            is ge the program start date and le the program end date.

        Exceptions:
            ValueError if there is no current program
        """
        # allow datetime and convert to date
        if isinstance(date, datetime.datetime):
            date = date.date()

        # find program that encompasses the date parameter
        for program_id in self:
            pgm = self[program_id]
            if date <= pgm['EndDate'] and date >= pgm['StartDate']:
                return pgm

        raise ValueError("There is no program for date %s" % date)


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
                    raise ValueError('Input Error. duplicate Id in table:'
                                     '%s\nrow=%s' % (key, row))
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
            print('Database characteristics:')
            for key in self.db_dict:
                print('%s: %s' % key, self.db_dict[key])
        except ValueError as ve:
            print('Invalid database configuration exception %s' % ve)
        return self.db_dict


class MySQLProgramsTable(ProgramsTable, MySQLDBMixin):
    """ Class representing the connection with a mysql database"""
    def __init__(self, db_dict, dbtype, verbose):
        """Read the input file into a dictionary."""
        super(MySQLProgramsTable, self).__init__(db_dict, dbtype, verbose)

        self.connectdb(db_dict, verbose)

        self._load_table()

    def insert(self, program_name, start_date, end_date):
        """
        Write a new record to the programs table of the database at the
        end of the database.

        Exceptions: TODO

        """
        cursor = self.connection.cursor()

        sql = ("INSERT INTO Program "
               "(ProgramName, StartDate, EndDate) "
               "VALUES (%s, %s, %s)")
        data = (program_name, start_date, end_date)

        try:
            cursor.execute(sql, data)
            self.connection.commit()
            new_pgmid = cursor.lastrowid
            audit_logger = get_logger(AUDIT_LOGGER_NAME)
            audit_logger.info('ProgramsTable userId %s added. ProgramName=%s, '
                              'StartDate=%s EndDate=%s', new_pgmid,
                              program_name, start_date, end_date)
        except mysqlerror as ex:
            self.connection.rollback()
            audit_logger = get_logger(AUDIT_LOGGER_NAME)
            audit_logger.error('ProgramTable INSERT failed SQL update. SQL=%s. '
                               'data=%s. Exception %s: %s', sql, data,
                               ex.__class__.__name__, ex)
            raise ex
        finally:
            self._load_table()
            self.connection.close()

    def delete(self, programid):
        """
        Delete the record defined by programid
        """
        cursor = self.connection.cursor()

        # Test of there are pings in the pings table.
        # We will not delete the program with pings existing.
        # pings_tbl = PingsTable.factory(self.db_info, self.db_type,
        #                               False)
        # TODO confirm no pings before delete of prora

        sql = "DELETE FROM Program WHERE ProgramID=%s"
        try:
            cursor.execute(sql, (programid,))  # noqa F841
            self.connection.commit()
            audit_logger = get_logger(AUDIT_LOGGER_NAME)
            audit_logger.info('ProgramTable ProgramId %s Deleted', programid)
        except mysqlerror as ex:
            audit_logger = get_logger(AUDIT_LOGGER_NAME)
            audit_logger.error('UserTable userid %s failed SQL DELETE. SQL=%s '
                               'exception %s: %s',
                               programid, sql, ex.__class__.__name__, ex)
            self.connection.rollback()
            raise ex
        finally:
            self._load_table()
            self.connection.close()
