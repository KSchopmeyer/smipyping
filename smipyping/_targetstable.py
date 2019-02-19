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
Define the base of targets (i.e. systems to be tested)
    TargetID = Column(Integer(11), primary_key=True)
    IPAddress = Column(String(15), nullable=False)
    CompanyID = Column(Integer(11), ForeignKey("Companies.CompanyID"))
    Namespace = Column(String(30), nullable=False)
    SMIVersion = Column(String(15), nullable=False)
    Product = Column(String(30), nullable=False)
    Principal = Column(String(30), nullable=False)
    Credential = Column(String(30), nullable=False)
    CimomVersion = Column(String(30), nullable=False)
    InteropNamespace = Column(String(30), nullable=False)
    Notify = Column(Enum('Enabled', 'Disabled'), default='Disabled')
    NotifyUsers = Column(String(12), nullable=False)
    ScanEnabled = Column(Enum('Enabled', 'Disabled'), default='Enabled')
    Protocol = Column(String(10), default='http')
    Port = Column(String(10), nullable=False)
"""

# TODO change ip_address to hostname where host name is name : port

from __future__ import print_function, absolute_import

import os
import csv
import re
from collections import OrderedDict
from textwrap import wrap
import six
from mysql.connector import Error as mysqlerror

from ._dbtablebase import DBTableBase
from ._mysqldbmixin import MySQLDBMixin
from ._common import get_url_str
from ._logging import AUDIT_LOGGER_NAME, get_logger
from ._companiestable import CompaniesTable

__all__ = ['TargetsTable']


class TargetsTable(DBTableBase):
    """
    Class representing the targets db table.

    This base contains information on the targets, host systems, etc. in the
    environment.

    The factory method should be used to construct a new TargetsTable object
    since that creates the correct object for the defined database type.
    """
    table_name = 'Targets'

    key_field = 'TargetID'

    # Fields that are required to create new records
    required_fields = [
        'IPAddress', 'CompanyID', 'Namespace',
        'SMIVersion', 'Product', 'Principal', 'Credential',
        'CimomVersion', 'InteropNamespace', 'Notify', 'NotifyUsers',
        'ScanEnabled', 'Protocol', 'Port']

    # All fields in each record.
    fields = [key_field] + required_fields

    join_fields = ['CompanyName']
    all_fields = fields + join_fields

    hints = {
        'IPAddress': "Host name or ip address",
        'CompanyID': "DB id of company",
        'Namespace': "User namespace",
        'SMIVersion': "SMI version",
        'Product': "Product name",
        'Principal': "User Name to access target",
        'Credential': "User password to access target",
        'CimomVersion': "Version of CIMOM",
        'InteropNamespace': "Interop Namespace name",
        'Notify': "'Enabled' if users to be notified of issues, else "
                  "'Disabled'",
        'NotifyUsers': "List of UserIDs to notify",
        'ScanEnabled': "Enabled if this  target to be scanned",
        'Protocol': '"http" or "https"',
        'Port': "Integer defining WBEM server port."}

    # # Defines each record for the data base and outputs.
    # # The Name is the database name for the property
    # # The value tuple is display name and max width for the record
    table_format_dict = OrderedDict([
        ('TargetID', ('ID', 2, int)),
        ('CompanyName', ('CompanyName', 12, str)),
        ('Namespace', ('Namespace', 12, str)),
        ('SMIVersion', ('SMIVersion', 12, str)),
        ('Product', ('Product', 15, str)),
        ('Principal', ('Principal', 12, str)),
        ('Credential', ('Credential', 12, str)),
        ('CimomVersion', ('CimomVersion', 15, str)),
        ('IPAddress', ('IPAddress', 12, str)),
        ('InteropNamespace', ('Interop', 8, str)),
        ('Notify', ('Notify', 12, str)),
        ('NotifyUsers', ('NotifyUsers', 12, str)),
        ('Protocol', ('Prot', 5, str)),
        ('Port', ('Port', 4, int)),
        ('ScanEnabled', ('Enabled', 6, str)),
        ])  # noqa: E123

    def __init__(self, db_dict, db_type, verbose, output_format):
        """Initialize the abstract Targets instance.

        This controls all other
        target bases. This defines the common definition of all targets bases
        including field names, and common methods.

        Parameters:
          db_dict (:term: `dictionary')
            Dictionary containing all of the parameters to open the database
            defined by the db_dict attribute.

          db_type (:term: `string`)
            String defining one of the allowed database types for the
            target database.

          verbose (:class:`py:bool`)
            Boolean. If true detailed info is displayed on the processing
            of the TargetData class

          output_format (:term:`string`)
            String defining one of the legal report output formats.  If not
            provided, the default is a simple report format.
        """

        super(TargetsTable, self).__init__(db_dict, db_type, verbose)

        self.output_format = output_format

    def __str__(self):
        # TODO this and __repr__ do not really match.
        """String info on targetdata. TODO. Put more info here"""
        return ('type=%s db=%s, len=%s' % (self.db_type, self.get_dbdict(),
                                           len(self.data_dict)))

    def __repr__(self):
        """Rep of target data"""
        return ('Targetdata db_type %s, rep count=%s' %
                (self.db_type, len(self.data_dict)))

    def test_fieldnames(self, fields):
        """Test a list of field names. This test generates an exception,
           KeyError if a field in fields is not in the table
        """
        for field in fields:
            self.table_format_dict[field]  # pylint: disable=pointless-statement

    def get_dbdict(self):
        """Get string for the db_dict"""
        return '%s' % self.db_dict

    @classmethod
    def factory(cls, db_dict, db_type, verbose, output_format='simple'):
        """Factory method to select subclass based on database type (db_type).
           Currently the types sql and csv are supported.

           Returns instance object of the defined provider type.
        """

        inst = None
        if verbose:
            print('targetdata factory datafile %s dbtype %s verbose %s'
                  % (db_dict, db_type, verbose))
        if db_type == ('csv'):
            inst = CsvTargetsTable(db_dict, db_type, verbose,
                                   output_format=output_format)
        elif db_type == ('mysql'):
            inst = MySQLTargetsTable(db_dict, db_type, verbose,
                                     output_format=output_format)
        else:
            ValueError('Invalid targets factory db_type %s' % db_type)

        if verbose:
            print('Resulting targets factory inst %r' % inst)

        return inst

    def get_field_list(self):
        """Return a list of the base table field names in the order defined."""
        return list(self.table_format_dict)

    def get_format_dict(self, name):
        """Return tuple of display name and length for name."""
        return self.table_format_dict[name]

    def get_enabled_targetids(self):
        """Get list of target ids that are marked enabled."""
        return [x for x in self.data_dict
                if not self.disabled_target_id(x)]

    def get_disabled_targetids(self):
        """Get list of target ids that are marked disabled"""
        return [x for x in self.data_dict
                if self.disabled_target_id(x)]

    # TODO we have multiple of these. See get dict_for_host,get_hostid_list
    def get_targets_host(self, host_data):
        """
        If an record for `host_data` exists return that record,
        otherwise return None.

        There may be multiple ipaddress, port entries for a
        single ipaddress, port in the database

        Parameters:

          host_id(tuple of hostname or ipaddress and port)

        Returns list of targetdata keys
        """
        # TODO clean up for PY 3
        return_list = []
        for key, value in self.data_dict.iteritems():
            port = value["Port"]
            # TODO port from database is a string. Should be int internal.
            if value["IPAddress"] == host_data[0] and int(port) == host_data[1]:
                return_list.append(key)

        return return_list

    def get_target(self, target_id):
        """
        Get the target data for the parameter target_id.

        This is alternate to using [id] directly. It does an additonal check
        for correct type for target_id

        Returns:
            target as dictionary

        Exceptions:
            KeyError if target not in targets dictionary
        """
        if not isinstance(target_id, six.integer_types):
            target_id = int(target_id)

        return self.data_dict[target_id]

    def filter_targets(self, ip_filter=None, company_name_filter=None):
        """
        Filter for match of ip_filter and companyname filter if they exist
        and return list of any targets that match.

        The filters are regex strings.
        """
        rtn = OrderedDict()
        for key, value in self.data_dict.items():
            if ip_filter and re.match(ip_filter, value['IPAddress']):
                rtn[key] = value
            if company_name_filter and \
                    re.match(value['CompanyName'], company_name_filter):
                rtn[key] = value

        return rtn

    def build_url(self, targetid):
        """Get the string representing the url for targetid. Gets the
        Protocol, IPaddress and port and uses the common get_url_str to
        create a string.  Port info is included only if it is not the
        WBEM CIM-XML standard definitions.
        """
        target = self[targetid]

        return get_url_str(target['Protocol'], target['IPAddress'],
                           target['Port'])

    def get_hostid_list(self, ip_filter=None, company_name_filter=None):
        """
        Get all WBEM Server ipaddresses in the targets base.

        Returns list of IP addresses:port entries.
           TODO: Does not include port right now.
        """

        output_list = []
        # TODO clean up for python 3

        for _id, value in self.data_dict.items():
            if self.verbose:
                print('get_hostid_list value %s' % (value,))
            output_list.append(value['IPAddress'])
        return output_list

    def tbl_hdr(self, record_list):
        """Return a list of all the column headers from the record_list."""
        hdr = []
        for name in record_list:
            value = self.get_format_dict(name)
            hdr.append(value[0])
        return hdr

    def get_notifyusers(self, targetid):
        """
        Get list of entries in the notify users field and split into python
        list.
        """
        notify_users = self[targetid]
        if notify_users:
            notify_users_list = notify_users.split('/')
            return notify_users_list
        return None

    def format_record(self, record_id, fields, fold=False):
        """Return the fields defined in field_list for the record_id in
        display format.
        String fields will be folded if their width is greater than the
        specification in the format_dictionary and fold=True
        """
        # TODO can we make this a std cvt function.

        target = self.get_target(record_id)

        line = []

        for field_name in fields:
            field_value = target[field_name]
            fmt_value = self.get_format_dict(field_name)
            max_width = fmt_value[1]
            field_type = fmt_value[2]
            if isinstance(field_type, six.string_types) and field_value:
                if max_width < len(field_value):
                    line.append('\n'.join(wrap(field_value, max_width)))
                else:
                    line.append('%s' % field_value)
            else:
                line.append('%s' % field_value)
        return line

    def disabled_target(self, target_record):  # pylint: disable=no-self-use
        """
        If target_record disabled, return true, else return false.
        """
        val = target_record['ScanEnabled'].lower()
        if val == 'enabled':
            return False
        elif val == 'disabled':
            return True
        else:
            ValueError('ScanEnabled field must contain "Enabled" or "Disabled'
                       ' string. %s is invalid.' % val)

    def disabled_target_id(self, target_id):
        """
        Return True if target recorded for this target_id marked
        disabled. Otherwise return True

        Parameters:

            target_id(:term:`integer`)
                Valid target Id for the Target_Tableue .

        Returns: (:class:`py:bool`)
            True if this target id disabled

        Exceptions:
            KeyError if target_id not in database
        """
        return(self.disabled_target(self.data_dict[target_id]))

    def get_output_width(self, col_list):
        """
        Get the width of a table from the column names in the list
        """
        total_width = 0
        for name in col_list:
            value = self.get_format_dict(name)
            total_width += value[1]
        return total_width

    def get_unique_creds(self):
        """
        Get the set of Credentials and Principal that represents the
        unique combination of both.  The result could be used to test with
        all Principals/Credentials knows in the db.

        Return list of targetIDs that represent unique sets of Principal and
        Credential
        """
        creds = {k: '%s%s' % (v['Principal'], v['Credential'])
                 for k, v in self.data_dict.iteritems()}
        ucreds = dict([[v, k] for k, v in creds.items()])
        unique_keys = dict([[v, k] for k, v in ucreds.items()])

        unique_creds = [(self.data_dict[k]['Principal'],
                         self.data_dict[k]['Credential']) for k in unique_keys]

        return unique_creds

    # def db_info(self):
        # """get info on the database used"""
        # pass


class SQLTargetsTable(TargetsTable):
    """
    Subclass of Targets data for all SQL databases.  Subclasses of this class
    support specialized sql databases.
    """
    def __init__(self, db_dict, dbtype, verbose, output_format):
        """Pass through to SQL"""
        if verbose:
            print('SQL Database type %s  verbose=%s' % (db_dict, verbose))
        super(SQLTargetsTable, self).__init__(db_dict, dbtype, verbose,
                                              output_format)
        self.connection = None


class MySQLTargetsTable(SQLTargetsTable, MySQLDBMixin):
    """
    This subclass of TargetsTable process targets infromation from an sql
    database.

    Generate the targetstable from the sql database targets table and
    the companies table, by mapping the data to the dictionary defined
    for targets
    """
    # TODO filename is config file name, not actual file name.
    def __init__(self, db_dict, dbtype, verbose, output_format):
        """Read the input file into a dictionary."""
        super(MySQLTargetsTable, self).__init__(db_dict, dbtype, verbose,
                                                output_format)

        self.connectdb(db_dict, verbose)
        self._load_table()
        self._load_joins()

    def _load_joins(self):
        """
        Load the tables that would normally be joins.  In this case it is the
        companies table. Move the companyName into the targets table
        TODO we should not be doing this in this manner but with a
        join.
        """
        # Get companies table and insert into targets table:
        # TODO in smipyping name is db_dict. Elsewhere it is db_info
        companies_tbl = CompaniesTable.factory(self.db_dict,
                                               self.db_type,
                                               self.verbose)
        try:
            # set the companyname into the targets table
            for target_key in self.data_dict:
                target = self.data_dict[target_key]
                if target['CompanyID'] in companies_tbl:
                    company = companies_tbl[target['CompanyID']]
                    target['CompanyName'] = company['CompanyName']
                else:
                    target['CompanyName'] = "TableError CompanyID %s" % \
                        target['CompanyID']

        except Exception as ex:
            raise ValueError('Error: putting Company Name in table %r error %s'
                             % (self.db_dict, ex))

    def update_fields(self, target_id, changes):
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

        values.append(target_id)
        sql = "Update Targets " + set_names

        # append targetid component
        sql = sql + " WHERE TargetID=%s"

        # Record the original data for the audit log.
        original_data = {}
        target_record = self.get_target(target_id)
        for change in changes:
            original_data[change] = target_record[change]
        try:
            cursor.execute(sql, tuple(values))
            self.connection.commit()
            audit_logger = get_logger(AUDIT_LOGGER_NAME)

            audit_logger.info('TargetsTable TargetID: %s, update fields: %s, '
                              'original fields: %s',
                              target_id, changes, original_data)
        except Exception as ex:
            self.connection.rollback()
            audit_logger = get_logger(AUDIT_LOGGER_NAME)
            audit_logger.error('TargetsTable TargetID: %s failed SQL update. '
                               'SQL: %s Changes: %s Exception: %s',
                               target_id, sql, changes, ex)
            raise ex
        finally:
            self._load_table()
            self._load_joins()
            cursor.close()

    def activate(self, targetid, activate_flag):
        """
        Activate or deactivate the table entry defined by the
        targetid parameter to the value defined by the activate_flag

        Parameters:

          targetid (:term:`py:integer`):
            The database key property for this table

          activate_flag (:class:`py:bool`):
            Next state that will be set into the database for this target.

            Since the db field is an enum it actually sete Active or Inactive
            strings into the field
        """
        cursor = self.connection.cursor()

        enabled_kw = 'Enabled' if activate_flag else 'Disabled'
        sql = 'UPDATE Targets SET ScanEnabled = %s WHERE TargetID = %s'

        try:
            cursor.execute(sql, (enabled_kw, targetid))  # noqa F841
            self.connection.commit()
            audit_logger = get_logger(AUDIT_LOGGER_NAME)

            audit_logger.info('TargetTable TargetId %s,set scanEnabled  to %s',
                              targetid, enabled_kw)
        except mysqlerror as ex:
            audit_logger = get_logger(AUDIT_LOGGER_NAME)
            audit_logger.error('TargetTable userid %s failed SQL change '
                               'ScanEnabled. SQL=%s '
                               'Change to %s exception %s: %s',
                               targetid, sql, enabled_kw, ex.__class__.__name__,
                               ex)
            self.connection.rollback()
            raise ex
        finally:
            self._load_table()
            self._load_joins()

    def delete(self, targetid):
        """
        Delete the target in the targets table defined by the  targetid
        """
        cursor = self.connection.cursor()

        sql = "DELETE FROM Targets WHERE TargetID=%s"
        try:
            # pylint: disable=unused-variable
            mydata = cursor.execute(sql, (targetid,))  # noqa F841
            self.connection.commit()
            audit_logger = get_logger(AUDIT_LOGGER_NAME)
            audit_logger.info('TargetTable TargetId %s Deleted', targetid)
        except mysqlerror as ex:
            audit_logger = get_logger(AUDIT_LOGGER_NAME)
            audit_logger.error('TargetTable targetid %s failed SQL DELETE. '
                               'SQL=%s exception %s: %s',
                               targetid, sql, ex.__class__.__name__, ex)
            self.connection.rollback()
            raise ex
        finally:
            self._load_table()
            self._load_joins()
            self.connection.close()

    def insert(self, fields):
        """
        Write a new record to the database containing the fields defined in
        the input.

        Parameters:
          field_data ()
            Dictionary of fields to be inserted into the table.  There is
            one entry in the dictionary for each field to be inserted.

        Exceptions:

        """
        cursor = self.connection.cursor()

        placeholders = ', '.join(['%s'] * len(fields))
        columns = ', '.join(fields.keys())
        sql = "INSERT INTO %s ( %s ) VALUES ( %s )" % (self.table_name,
                                                       columns,
                                                       placeholders)

        try:
            cursor.execute(sql, fields.values())
            self.connection.commit()
            new_targetid = cursor.lastrowid
            audit_logger = get_logger(AUDIT_LOGGER_NAME)
            audit_logger.info('TargetsTable TargetId %s added. %s',
                              new_targetid, fields)
        except mysqlerror as ex:
            audit_logger = get_logger(AUDIT_LOGGER_NAME)
            audit_logger.error('TargetTable INSERT failed SQL update. SQL=%s. '
                               'data=%s. Exception %s: %s', sql, fields,
                               ex.__class__.__name__, ex)
            self.connection.rollback()
            raise ex
        finally:
            self._load_table()
            self._load_joins()
            self.connection.close()


class CsvTargetsTable(TargetsTable):
    """Comma Separated Values form of the Target base."""

    def __init__(self, db_dict, dbtype, verbose, output_format):
        """Read the input file into a dictionary."""
        super(CsvTargetsTable, self).__init__(db_dict, dbtype, verbose,
                                              output_format)

        fn = db_dict['targetsfilename']
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

    def write_updated_record(self, record_id):
        """Backup the existing file and write the new one.
        with cvs it writes the whole file back
        """
        backfile = '%s.bak' % self.filename
        # TODO does this cover directories/clean up for possible exceptions.
        if os.path.isfile(backfile):
            os.remove(backfile)
        os.rename(self.filename, backfile)
        self.write_file(self.filename)

    def write_file(self, file_name):
        """Write the current Target base to the named file."""
        with open(file_name, 'wb') as f:
            writer = csv.DictWriter(f, fieldnames=self.get_field_list())
            writer.writeheader()
            for key, value in sorted(self.data_dict.iteritems()):
                writer.writerow(value)
