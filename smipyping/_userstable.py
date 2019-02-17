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
from mysql.connector import Error as mysqlerror

from ._dbtablebase import DBTableBase
from ._mysqldbmixin import MySQLDBMixin

from ._logging import AUDIT_LOGGER_NAME, get_logger

__all__ = ['UsersTable']


class UsersTable(DBTableBase):
    """
    Abstract class for UsersTable
    This table contains a single entry, the last time a scan was executed.
    """
    key_field = 'UserID'
    table_name = 'Users'
    fields = [key_field, 'FirstName', 'Lastname', 'Email', 'CompanyID',
              'Active', 'Notify']

    join_fields = ['CompanyName']

    all_fields = fields + join_fields

    # In the following, The first entry corresponds to True and the second
    # to False
    active_field = ['Active', 'Inactive']  # db field is enum with two choices
    notify_field = ['Enabled', 'Disabled']  # db field is enum with two choices

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
            # pylint: disable=redefined-variable-type
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
        return {key: value for key, value in six.iteritems(self)
                if value[field] == target_value}

    def tbl_hdr(self, record_list):  # pylint: disable=no-self-use
        """Return a list of all the column headers from the record_list."""
        hdr = []
        for name in record_list:
            # value = self.get_format_dict(name)
            hdr.append(name)
        return hdr

    def format_record(self, userid, fields):
        """Return the fields defined in field_list for the record_id in
        display format.
        String fields will be folded if their width is greater than the
        specification in the format_dictionary and fold=True
        """
        # TODO can we make this a std cvt function.
        # TODO we have too many ways to access the data_dict.
        user = self.data_dict[userid]

        line = []
        for field_name in fields:
            field_value = user[field_name]
            line.append('%s' % field_value)
        return line

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

    def is_inactive(self, user_id):
        """
        Test if user_id is marked inactive

        Return:
            True if active. False if Inactive
        """
        return True if self[user_id]['Active'] == 'Inactive' else False

    def get_active_usersids(self, active=True):
        """Get list of userids filtered by whether they are active or not """

        if active:
            return [userid for userid in six.iterkeys(self.data_dict)
                    if self.is_active(userid)]

        return [userid for userid in six.iterkeys(self.data_dict)
                if self.is_inactive(userid)]

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
    when the table is intialized. It is a generalization for all database
    accesses.
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


class MySQLUsersTable(UsersTable, MySQLDBMixin):
    """ Class representing the connection with a mysql database"""
    def __init__(self, db_dict, dbtype, verbose):
        """Read the input file into a dictionary."""
        super(MySQLUsersTable, self).__init__(db_dict, dbtype, verbose)

        self.connectdb(db_dict, verbose)
        self._load_table()
        self._load_joins()

    def _load_joins(self):
        """
        Load the tables that would normally be joins.  In this case it is the
        companies table and move the companyName into the users table
        TODO we should not be doing this in this manner but with a
        join.
        """
        # Get companies table and insert into users table:

        # companies_tbl = CompaniesTable.factory(self.db_info,
        #                                       self.db_type,
        #                                       self.verbose)
        try:
            # TODO this should simply use the CompanyTable class (above)
            cursor = self.connection.cursor(dictionary=True)
            # get the companies table
            cursor.execute('SELECT CompanyID, CompanyName FROM Companies')
            rows = cursor.fetchall()

            companies_tbl = {}
            for row in rows:
                # required because the dictionary=True in cursor statement
                # only works in v2 mysql-connector
                assert isinstance(row, dict), "Issue with mysql-connection ver"
                key = row['CompanyID']
                companies_tbl[key] = row['CompanyName']
        except Exception as ex:
            raise ValueError('Could not create companies table. Exception: %r'
                             % (ex))

        try:
            # set the companyname into the users table
            for userid, user in six.iteritems(self.data_dict):
                if user['CompanyID'] in companies_tbl:
                    user['CompanyName'] = companies_tbl[user['CompanyID']]
                else:
                    user['CompanyName'] = "Table Error CompanyID %s" % \
                        user['CompanyID']
                    audit_logger = get_logger(AUDIT_LOGGER_NAME)
                    audit_logger.error('MYSQL DB Error: UserTable. Company ID '
                                       '%s in userID %s does not exist in '
                                       'CompaniesTable.', user['CompanyID'],
                                       userid)

        except Exception as ex:
            raise ValueError('Error: putting Company Name in table %r error %s'
                             % (self.db_dict, ex))

    def insert(self, firstname, lastname, email, company_id, active=True,
               notify=True):
        """
        Write a new record to the database containing the fields defined in
        the input.

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
            new_userid = cursor.lastrowid
            audit_logger = get_logger(AUDIT_LOGGER_NAME)
            audit_logger.info('UserTable userId %s added. Firstname=%s, '
                              'Lastname=%s Email=%s, CompanyID=%s, Active=%s, '
                              'Notify=%s', new_userid, firstname, lastname,
                              email, company_id, active, notify)
        except mysqlerror as ex:
            audit_logger = get_logger(AUDIT_LOGGER_NAME)
            audit_logger.error('UserTable INSERT failed SQL update. SQL=%s. '
                               'data=%s. Exception %s: %s', sql, data,
                               ex.__class__.__name__, ex)
            self.connection.rollback()
            raise ex
        finally:
            self._load_table()
            self._load_joins()
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
            audit_logger = get_logger(AUDIT_LOGGER_NAME)
            audit_logger.info('UserTable userId %s Deleted', user_id)
        except mysqlerror as ex:
            audit_logger = get_logger(AUDIT_LOGGER_NAME)
            audit_logger.error('UserTable userid %s failed SQL DELETE. SQL=%s '
                               'exception %s: %s',
                               user_id, sql, ex.__class__.__name__, ex)
            self.connection.rollback()
            raise ex
        finally:
            self._load_table()
            self._load_joins()
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
            cursor.execute(sql, (active_kw, user_id))  # noqa F841
            self.connection.commit()
            audit_logger = get_logger(AUDIT_LOGGER_NAME)

            audit_logger.info('UserTable userId %s,set active to %s',
                              user_id, active_kw)
        except mysqlerror as ex:
            audit_logger = get_logger(AUDIT_LOGGER_NAME)
            audit_logger.error('UserTable userid %s failed SQL change '
                               'activate. SQL=%s '
                               'Change to %s exception %s: %s',
                               user_id, sql, active_kw, ex.__class__.__name__,
                               ex)
            self.connection.rollback()
            raise ex
        finally:
            self._load_table()
            self._load_joins()
            # self.connection.close()

    def update_fields(self, userid, changes):
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

        values.append(userid)
        sql = "Update Users " + set_names

        # append targetid component
        sql = sql + " WHERE UserID=%s"

        change_str = ""
        for key, value in changes.items():
            change_str += "%s:%s " % (key, value)

        # Record the original data for the audit log.
        user_record = self.data_dict[userid]
        original_data = {change: user_record[change] for change in changes}
        original_str = ""
        for key, value in original_data.items():
            original_str += "%s:%s " % (key, value)
        try:
            cursor.execute(sql, tuple(values))
            self.connection.commit()
            audit_logger = get_logger(AUDIT_LOGGER_NAME)

            audit_logger.info('UserTable userId %s, update fields: %s, '
                              'original_fields: %s',
                              userid, change_str, original_str)
        except mysqlerror as ex:
            audit_logger = get_logger(AUDIT_LOGGER_NAME)
            audit_logger.error('UserTable userid %s failed SQL update. SQL=%s '
                               'Changes %s exception %s',
                               userid, sql, change_str, ex)
            self.connection.rollback()
            raise ex
        finally:
            self._load_table()
            self._load_joins()
            cursor.close()
