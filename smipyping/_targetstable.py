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
from mysql.connector import MySQLConnection
from ._configfile import read_config
from ._dbtablebase import DBTableBase

__all__ = ['TargetsTable']


class TargetsTable(DBTableBase):
    """
    Class representing the targets db table.

    This base contains information on the targets, host systems, etc. in the
    environment.

    The factory method should be used to construct a new TargetsTable object
    since that creates the correct object for the defined database type.
    """

    key_field = 'TargetID'
    fields = [key_field, 'IPAddress', 'CompanyID', 'Namespace',
              'SMIVersion', 'Product', 'Principal', 'Credential',
              'CimomVersion', 'InteropNamespace', 'Notify', 'NotifyUsers',
              'ScanEnabled', 'Protocol', 'Port']
    table_name = 'Targets'

    # # Defines each record for the data base and outputs.
    # # The Name is the database name for the property
    # # The value tuple is display name and max width for the record
    # # TODO this should be class level.
    table_format_dict = OrderedDict([
        ('TargetID', ('ID', 2, int)),
        ('CompanyName', ('Company', 12, str)),
        ('Namespace', ('Namespace', 12, str)),
        ('SMIVersion', ('SMIVersion', 12, str)),
        ('Product', ('Product', 15, str)),
        ('Principal', ('Principal', 12, str)),
        ('Credential', ('Credential', 12, str)),
        ('CimomVersion', ('Version', 15, str)),
        ('IPAddress', ('IP', 12, str)),
        ('InteropNamespace', ('Interop', 8, str)),
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
        self.data_dict = {}
        self.db_dict = db_dict
        self.verbose = verbose
        self.output_format = output_format
        self.db_type = db_type

    def test_fieldnames(self, fields):
        """Test a list of field names"""
        for field in fields:
            self.table_format_dict[field]

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

    def __str__(self):
        """String info on targetdata. TODO. Put more info her"""
        return ('type=%s db=%s, len=%s' % (self.db_type, self.db_xxx(),
                                           len(self.data_dict)))

    def __repr__(self):
        """Rep of target data"""
        return ('Targetdata db_type %s, rep count=%s' %
                (self.db_type, len(self.data_dict)))

    def get_field_list(self):
        """Return a list of the base table field names in the order defined."""
        return list(self.table_format_dict)

    def __contains__(self, record_id):
        """Determine if record_id is in targets dictionary."""
        return record_id in self.data_dict

    def __iter__(self):
        """iterator for targets."""
        return six.iter(self.data_dict)

    def __iterkeys__(self):
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
        """Return the record for the defined record_id from the targets.

          Parameters:

            record_id(:term:`integer)
                Valid key in targets dictionary

          Returns:
            target record corresponding to the id

          Exceptions:
            KeyError if record_id not it table
        """
        return self.data_dict[record_id]

    def __delitem__(self, record_id):
        """Delete the record_id in the table"""
        del self.data_dict[record_id]

    def __len__(self):
        """Return number of targets"""
        return len(self.data_dict)

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
    def get_targets_host(self, host_id):
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
            ip_address = value["IPAddress"]
            port = value["Port"]
            # TODO port from database is a string. Should be int internal.
            if ip_address == host_id[0] and int(port) == host_id[1]:
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

    def get_target_for_host(self, target_addr):
        """
        For a host address, get the targets dictionary record if it exists.

        Parameters:
            target_addr: hostname/IPAddress of target

        Returns: None if not found or possibly multiple target_ids

        If not found. Does not work completely because of multiple IPs
        """
        targets = []
        for target_id, value in self.data_dict.iteritems():
            if value['IPAddress'] == target_addr:
                targets.append(target_id)
        return targets

    def filter_targets(self, ip_filter=None, company_name_filter=None):
        """
        Filter for match of ip_filter and companyname filter if they exist
        and return list of any providers that match.

        the filters may be exact matches or regex string
        """
        # TODO: ks fix this code. It is broken
        rtn = OrderedDict()
        for key, value in self.data_dict.items():
            if ip_filter and re.match(ip_filter, value['IPAddress']):
                rtn[key] = value
            if company_name_filter and \
                    re.match(value['CompanyName'], company_name_filter):
                rtn[key] = value

        return rtn

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

    # TODO This is a formatter and should probably not be in this file
    def format_record(self, record_id, fields, fold=False):
        """Return the fields defined in field_list for the record_id in
        display format.
        String fields will be folded if their width is greater than the
        specification in the format_dictionary and fold=True
        """
        # TODO can we make this a std cvt function.

        record = self.get_target(record_id)

        line = []

        for field_name in fields:
            field_value = record[field_name]
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

    def disabled_target(self, target_record):
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

    def db_info(self):
        """get info on the database used"""
        pass


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

    def db_xxx(self):
        return '%s' % self.db_dict

    def write_updated_record(self, recordid):
        """
        Update the database record
        """
        pass
        # TODO this untested.
        # cursor.execute ("""
        #   UPDATE tblTableName
        #   SET Year=%s, Month=%s, Day=%s, Hour=%s, Minute=%s
        #   WHERE Server=%s
        # """,
        # (Year, Month, Day, Hour, Minute, ServerID))

        # connect.commit()


class MySQLTargetsTable(SQLTargetsTable):
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
        if verbose:
            print('MySQL Database type %s  verbose=%s' % (db_dict, verbose))
        super(MySQLTargetsTable, self).__init__(db_dict, dbtype, verbose,
                                                output_format)

        # Connect to database
        try:
            connection = MySQLConnection(host=db_dict['host'],
                                         database=db_dict['database'],
                                         user=db_dict['user'],
                                         password=db_dict['password'])

            if connection.is_connected():
                if verbose:
                    print('sql db connection established. host %s, db %s' %
                          (db_dict['host'], db_dict['database']))
                self.connection = connection
            else:
                print('SQL database connection failed. host %s, db %s' %
                      (db_dict['host'], db_dict['database']))
                raise ValueError('Connection to database failed')
        except Exception as ex:
            raise ValueError('Could not connect to sql database %r. '
                             ' Exception: %r'
                             % (db_dict, ex))

        # get companies table
        try:
            # python-mysql-connector-dictcursor  # noqa: E501
            cursor = connection.cursor(dictionary=True)

            # get the companies table
            cursor.execute('SELECT CompanyID, CompanyName FROM Companies')
            rows = cursor.fetchall()
            companies = {}
            for row in rows:
                # required because the dictionary=True in cursor statement
                # only works in v2 mysql-connector
                assert isinstance(row, dict), "Issue with mysql-connection ver"

                key = row['CompanyID']
                companies[key] = row['CompanyName']

        except Exception as ex:
            raise ValueError('Could not create companies table %r Exception: %r'
                             % (rows, ex))
        # get targets table
        try:
            targets_dict = {}
            # fetchall returns tuple so need index to fields, not names
            fields = ', '.join(self.fields)
            select = 'SELECT %s FROM %s' % (fields, self.table_name)
            cursor.execute(select)
            rows = cursor.fetchall()
            for row in rows:
                key = row[self.key_field]
                targets_dict[key] = row

            # save the combined table for the other functions.
            self.data_dict = targets_dict
        except Exception as ex:
            raise ValueError('Error: setup sql based targets table %r. '
                             'Exception: %r'
                             % (db_dict, ex))
        try:
            # set the companyname into the targets table
            for target_key in self.data_dict:
                target = self.data_dict[target_key]
                target['CompanyName'] = companies[target['CompanyID']]

        except Exception as ex:
            raise ValueError('Error: putting Company Name in table %r error %s'
                             % (db_dict, ex))


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

    # TODO consolidate this to use predefined type.
    # TODO this is completely broken because filename applies to the
    # config file, not the data file.
    def db_info(self):
        try:
            db_config = read_config(self.filename, self.db_type)
        except ValueError as ve:
            print('Section %s not in configfile %s %s' % (self.db_type,
                                                          self.filename,
                                                          ve))
        return db_config

    def db_xxx(self):
        return '%s' % self.db_dict

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
