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
Define the Users table and provide for import from multiple bases.
    UserID = Column(Integer(11), primary_key=True)
    Firstname = Column(String(30), nullable=False)
    Lastname = Column(String(30), nullable=False)
    Email = Column(String(50), nullable=False)
    CompanyID = Column(Integer, ForeignKey("Companies.CompanyID"))
    Active = Column(Enum('Active', 'Inactive'), nullable=False)
    Notify = Column(Enum('Enabled', 'Disabled'), nullable=False)

"""

from __future__ import print_function, absolute_import

import os
import csv
import six
from mysql.connector import MySQLConnection
from ._dbtablebase import DBTableBase
__all__ = ['UsersTable']


class UsersTable(DBTableBase):
    """
    Abstract class for UsersTable
    This table contains a single entry, the last time a scan was executed.
    """
    key_field = 'UserID'
    fields = [key_field, 'FirstName', 'Lastname', 'Email', 'CompanyID',
              'Active', 'Notify']
    table_name = 'Users'

    def __init__(self, db_dict, db_type, verbose):
        super(UsersTable, self).__init__(db_dict, db_type, verbose)

    def __str__(self):
        """String info on Userstable. TODO. Put more info her"""
        return ('len %s' % len(self.data_dict))

    def __repr__(self):
        """Rep of Users data"""
        return ('Users db_type %s db_dict len %s' %
                (self.db_type, len(self.data_dict)))

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
            inst = CsvUsersTable(db_dict, db_type, verbose)
        elif db_type == 'mysql':
            inst = MySQLUsersTable(db_dict, db_type, verbose)
        else:
            ValueError('Invalid users table factory db_type %s' % db_type)

        if verbose:
            print('Users table factory inst %r' % inst)

        return inst

    def filter_records(self, field, target_value):
        """Get the set of user records for a field in the table that
        where the field value matches the test_value provided.
        Return the result as a new dictionary where the key is
        userID and value is the user record.

        Parameters:

          field(:term:`string`):
            Name of field in the table on which the filtering occurs

          target_value():
            value to compare with value in user table field for equality.
            The datat type depends on the field being compared

        Returns:
          Dictionary of user table records that match where the UserID is
          the key and the value for that ID in the user table is the
          value.

        Returns:
            KeyError if the field is NOT in the user table.

        """
        # return {}
        return {key: value for key, value in six.iteritems(self)
                if value[field] == target_value}

    # add option for active
    def get_emails_for_company(self, company_id):
        """ Get all emails for a company id from the users base.  There will
            be typically multiple users returned.

            Parameters:
              company_id(:term:`integer`)
                The companyID for which all user records will be returned

            Returns:
                list of email addresses.
        """
        users = self.filter_records('CompanyID', company_id)
        # pylint: disable=unused-variable
        emails = [value['Email'] for key, value in six.iteritems(users)
                  if value['Active'] == 'Active']
        return emails

    def is_active(self, user_id):
        """
        Test if user_id is marked active

        Return:
            True if active. False if Inactive
        """
        return True if self[user_id]['Active'] == 'Active' else False

    def is_active_str(self, user_id):
        """ Get string value of active enum."""
        return self[user_id]['Active']


class CsvUsersTable(UsersTable):
    """
        Users Table functions for csv based table
    """
    def __init__(self, db_dict, dbtype, verbose):
        super(CsvUsersTable, self).__init__(db_dict, dbtype, verbose)

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
                    raise ValueError('Input Error. duplicate Id')
                else:
                    result[key] = row
        self.data_dict = result


class SQLUsersTable(UsersTable):
    """"
    Table representing the Users database table
    This table supports a single dictionary that contains the data
    when the table is intialized.
    """

    def __init__(self, db_dict, dbtype, verbose):
        """Pass through to SQL"""
        if verbose:
            print('SQL Database type %s  verbose=%s' % (db_dict, verbose))
        super(SQLUsersTable, self).__init__(db_dict, dbtype, verbose)
        self.connection = None

    def db_info(self):
        """
        Display the db info and Return info on the database used as a
        dictionary.
        """
        try:
            if self.verbose:
                print('Database characteristics')
                for key in self.db_dict:
                    print('%s: %s' % key, self.db_dict[key])
        except ValueError as ve:
            print('Invalid database configuration exception %s' % ve)
        return self.db_dict


class MySQLUsersTable(UsersTable):
    """ Class representing the connection with a mysql database"""
    def __init__(self, db_dict, dbtype, verbose):
        """Read the input file into a dictionary."""

        if verbose:
            print('MySQL Database type %s  verbose=%s' % (db_dict, verbose))
        super(MySQLUsersTable, self).__init__(db_dict, dbtype, verbose)

        try:
            connection = MySQLConnection(host=db_dict['host'],
                                         database=db_dict['database'],
                                         user=db_dict['user'],
                                         password=db_dict['password'])

            if connection.is_connected():
                self.connection = connection
                if verbose:
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

    def insert(self, firstname, lastname, email, company_id, active=True,
               notify=True):
        """
        Write a new record to the database containing the target_id,
        scan status and a timestamp

        Parameters:
          firstname(:term:`string`):
            User first name. Required

          lastname(:term:`string`):

          email(:term:`string`):

          company_id(:term:`integer`)

          active(:class:`py:bool`):

          notify(:class:`py:bool`):

        Exceptions:

        """
        cursor = self.connection.cursor()

        active = 'Active' if active else 'Inactive'
        notify = 'Enabled' if notify else 'Disabled'

        sql = ("INSERT INTO Users "
               "(Firstname, Lastname, Email, CompanyID, Active, Notify) "
               "VALUES (%s, %s, %s, %s, %s, %s)")
        data = (firstname, lastname, email, company_id, active,
                notify)

        try:
            cursor.execute(sql, data)
            self.connection.commit()
        except Exception as ex:
            print('userstable.append failed: exception %r' % ex)
            self.connection.rollback()
            raise ex
        finally:
            self._load()
            self.connection.close()

    def delete(self, user_id):
        """
        Delete the record defined by user_id
        """
        cursor = self.connection.cursor()

        sql = "DELETE FROM Users WHERE UserID=%s"
        try:
            # TODO what is return on execute??
            # pylint: disable=unused-variable
            mydata = cursor.execute(sql, (user_id,))  # noqa F841
            self.connection.commit()
        except Exception as ex:
            print('userstable.delete failed: exception %r' % ex)
            self.connection.rollback()
            raise ex
        finally:
            self._load()
            self.connection.close()

    def activate(self, user_id, activate_flag):
        """
        Activate or deactivate the table entry defined by the
        boolean activate parameter
        """
        cursor = self.connection.cursor()

        active_kw = 'Active' if activate_flag else 'Inactive'
        sql = 'UPDATE Users SET Active = %s WHERE UserID = %s'

        try:
            mydata = cursor.execute(sql, (active_kw, user_id))  # noqa F841
            self.connection.commit()
        except Exception as ex:
            print('userstable.activate id  %s failed: exception %r' % (user_id,
                                                                       ex))
            self.connection.rollback()
            raise ex
        finally:
            self._load()
            self.connection.close()

    def modify(self, user_id, firstname, lastname, email, company_id,
               active=True, notify=True):
        """
        Write a new record to the database containing the target_id,
        scan status and a timestamp

        Parameters:
          firstname(:term:`string`):
            User first name. Optional If not provided, this value will not
            be changed.

          lastname(:term:`string`):
            User last name. Optional If not provided, this value will not
            be changed.

          email(:term:`string`):
            User email address. Optional If not provided, this value will not
            be changed.

          company_id(:term:`integer`)
            User last name. Optional If not provided, this value will not
            be changed.

          active(:class:`py:bool`):

          notify(:class:`py:bool`):

        Exceptions:

        """
        cursor = self.connection.cursor()

        # TODO.  Need to account for 3 values, i.e. NONE also
        if active is not None:
            active = 'Active' if active else 'Inactive'

        if notify is not None:
            notify = 'Enabled' if notify else 'Disabled'

        # Create list of fields

        # create list of variables

        sql = ("UPDATE USERS "
               "set Firstname=%s, Lastname=%s, Email=%s, CompanyID=%s, "
               "Active=%s, Notify=%s) "
               "WHERE UserID = %s",
               (firstname, lastname, email, company_id, active,
                notify, user_id))
        try:
            cursor.execute(sql)
            self.connection.commit()
        except Exception as ex:
            print('userstable.append failed: exception %r' % ex)
            self.connection.rollback()
            raise ex
        finally:
            self._load()
            self.connection.close()
