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

"""

# TODO change ip_address to hostname where host name is name : port

from __future__ import print_function, absolute_import

import os
import csv
import re
from collections import OrderedDict
import six
from mysql.connector import MySQLConnection
from ._terminaltable import print_terminal_table, fold_cell
from ._configfile import read_config

__all__ = ['TargetsData']


class TargetsData(object):
    """Abstract top level class for the Target Base.

    This base contains information on the targets, host systems, etc. in the
    environment.
    """

    def __init__(self, db_dict, db_type, verbose):
        """Initialize the abstract Targets instance.

        This controls all other
        target bases. This defines the common definition of all targets bases
        including field names, and common methods.

        Parameters:
          filename
            Name of file to be used

          args:
            argparse arguments to be saved in the instance
        """
        self.targets_dict = {}
        self.db_dict = db_dict
        self.verbose = verbose
        # # Defines each record for the data base and outputs.
        # # The Name is the database name for the property
        # # The value tuple is display name and max width for the record
        # # TODO this should be class level.
        self.table_format_dict = OrderedDict([
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

        self.db_type = db_type

    @classmethod
    def factory(cls, db_dict, db_type, verbose):
        """Factory method to select subclass based on database type.
           Currently the types sql and csv are supported.

           Returns instance object of the defined provider type.
        """

        inst = None
        if verbose:
            print('targetdata factory datafile %s dbtype %s verbose %s'
                  % (db_dict,
                     db_type,
                     verbose))
        if db_type == ('csv'):
            inst = CsvTargetsData(db_dict, db_type, verbose)

        elif db_type == ('mysql'):
            inst = SQLTargetsData(db_dict, db_type, verbose)
        else:
            ValueError('Invalid target factory db_type %s' % db_type)

        print('Resultingtarget factory inst %r' % inst)

        return inst

    def __str__(self):
        """String info on targetdata. TODO. Put more info her"""
        return ('count=%s' % len(self.targets_dict))

    def __repr__(self):
        """Rep of target data"""
        return ('Targetdata db_type %s, rep count=%s' %
                (self.db_type, len(self.targets_dict)))

    def get_field_list(self):
        """Return a list of the base table file names in the order defined."""
        return list(self.table_format_dict)

    def get_format_dict(self, name):
        """Return tuple of display name and length for name."""
        return self.table_format_dict[name]

    def __contains__(self, record_id):
        """Determine if record_id is in targets dictionary."""
        return record_id in self.targets_dict

    def __iter__(self):
        """iterator for targets."""
        return six.iterkeys(self.targets_dict)

    def iteritems(self):
        """
        Iterate through the property names (in their original lexical case).

        Returns key and value
        """
        for key, val in self.targets_dict.iteritems():
            yield (key, val)

    def __getitem__(self, record_id):
        """Return the record for the defined record_id from the targets."""
        return self.targets_dict[record_id]

    def __delitem__(self, record_id):
        del self.targets_dict[record_id]

    def __len__(self):
        """Return number of targets"""
        return len(self.targets_dict)

    # TODO we have multiple of these. See get dict_for_host,get_hostid_list
    def get_targets_host(self, host_id):
        """
        If an record for `host_data` exists return that record.

        otherwise return None.

        Host data is a tuple of ipaddress and port.

        Note that   there may be multiple ipaddress, port entries for a
        single ipaddress, port in the database
        Returns list of targetdata keys
        """
        # TODO clean up for PY 3
        return_list = []
        for key, value in self.targets_dict.iteritems():
            ip_address = value["IPAddress"]
            port = value["Port"]
            # TODO port from database is a string. Should be int internal.
            if ip_address == host_id[0] and int(port) == host_id[1]:
                return_list.append(key)

        return return_list

    # TODO remap this one to use get_item directly.
    def get_dict_record(self, requested_id):
        """
        If an entry for `record_data` exists return that record.

        else generate exception
        """
        if not isinstance(requested_id, six.integer_types):
            requested_id = int(requested_id)

        return self.targets_dict[requested_id]

    def get_target_for_host(self, target_addr):
        """
        For a host address, get the targets dictionary record if it exists.

        Parameters:
            target_addr: hostname/IPAddress of target

        Returns: None if not found or possibly multiple target_ids

        If not found. Does not work completely because of multiple IPs
        """
        targets = []
        for target_id, value in self.targets_dict.iteritems():
            if value['IPAddress'] == target_addr:
                targets.append(target_id)
        return targets

    def filter_targets(self, ip_filter=None, company_name_filter=None):
        """
        Filter for match of ip_filter and companyname filter if they exist
        and return list of any providers that match.

        the filters may be exact matches or regex string
        """

        rtn = OrderedDict()
        for key, value in self.targets_dict.items():
            if ip_filter and re.match(ip_filter, value['IPAddress']):
                rtn.append[key] = value
            if company_name_filter and \
                    re.match(value['CompanyName'], company_name_filter):
                rtn.append[key] = value

        return rtn

    def get_hostid_list(self, ip_filter=None, company_name_filter=None):
        """
        Get all WBEM Server ids in the targets base.

        Returns list of IP addresses:port entries.
           TODO: Does not include port right now.
        """
        output_list = []
        # TODO clean up for python 3

        for _id, value in self.targets_dict.items():
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

    def tbl_record(self, record_id, field_list):
        """Return the fields defined in field_list for the record_id."""
        # TODO can we make this a std cvt function.

        record = self.get_dict_record(record_id)

        line = []
        for name in field_list:
            # TODOcell_str = record[name]
            value = self.get_format_dict(name)
            if isinstance(name, six.string_types):
                # max_width = value[1]
                line.append(fold_cell(record[name], value[1]))
                # if max_width < len(cell_str):
                #    cell_str = '\n'.join(wrap(cell_str, max_width))
                # line.append(cell_str)
            else:
                line.append('%s' % record[name])
        return line

    def disabled_target(self, target_record):
        """If record disabled, return true, else return false."""
        val = target_record['ScanEnabled'].lower()
        if val == 'enabled':
            return False
        elif val == 'disabled':
            return True
        else:
            ValueError('ScanEnabled field must contain "Enabled" or "Disabled'
                       ' string. %s is invalid.' % val)

    def db_info(self):
        """get info on the database used"""
        print('Base class. No info')

    def display_disabled(self):
        """Display diabled entries."""
        col_list = ['Id', 'IPAddress', 'CompanyName', 'Product',
                    'Port', 'Protocol', 'ScanEnabled']

        table_data = []

        table_data.append(self.tbl_hdr(col_list))

        # TODO can we do this with list comprehension
        for record_id in sorted(self.targets_dict.iterkeys()):
            if self.disabled_record(self.targets_dict[record_id]):
                table_data.append(self.tbl_record(record_id, col_list))

        print_terminal_table('Disabled hosts', table_data)

    def display_cols(self, column_list):
        """
        Display the columns of data defined by the col_list.

        This gets the
        data from the targets data based on the col_list and prepares a table
        based on those target_data colums

        Parameters:
          column_list: list of strings defining the targets_data columns to be
            displayed.

        """
        table_data = []

        # terminaltables creates the table headers from
        table_data.append(self.tbl_hdr(column_list))

        for record_id in sorted(self.targets_dict.iterkeys()):
            table_data.append(self.tbl_record(record_id, column_list))

        print_terminal_table('Target Systems Overview', table_data)

    def display_all(self, fields=None, company=None):
        """Display all entries in the base."""
        print('fields %s' % fields)
        if not fields:
            # list of default fields for display
            col_list = ['TargetID', 'IPAddress', 'CompanyName', 'Product',
                        'Port', 'Protocol', 'CimomVersion']
        else:
            print('fields0 %s' % fields)
            col_list = fields

        print('fields %s' % fields)

        self.display_cols(col_list)


class SQLTargetsData(TargetsData):
    """
    This subclass of TargetsData process targets infromation from an sql
    database.

    Generate the targetstable from the sql database targets table and
    the companies table, by mapping the data to the dictionary defined
    for targets
    """
    # TODO filename is config file name, not actual file name.
    def __init__(self, db_dict, dbtype, verbose):
        """Read the input file into a dictionary."""

        print('SQL Database type %s  verbose=%s' % (db_dict, verbose))
        super(SQLTargetsData, self).__init__(db_dict, dbtype, verbose)

        try:
            connection = MySQLConnection(host=db_dict['host'],
                                         database=db_dict['database'],
                                         user=db_dict['user'],
                                         password=db_dict['password'])

            if connection.is_connected():
                print('sql db connection established. host %s, db %s' %
                      (db_dict['host'], db_dict['database']))
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
            cursor.execute('SELECT TargetID, IPAddress, CompanyID, Namespace, '
                           'SMIVersion, Product, Principal, Credential, '
                           'CimomVersion, InterOpNamespace, Notify, '
                           'NotifyUsers, ScanEnabled, Protocol, Port '
                           'FROM Targets')
            rows = cursor.fetchall()
            for row in rows:
                key = row['TargetID']
                targets_dict[key] = row

            # save the combined table for the other functions.
            self.targets_dict = targets_dict
        except Exception as ex:
            raise ValueError('Error: setup sql based targets table %r. '
                             'Exception: %r'
                             % (db_dict, ex))
        try:
            # set the companyname into the targets table
            for target_key in self.targets_dict:
                target = self.targets_dict[target_key]
                target['CompanyName'] = companies[target['CompanyID']]

        except Exception as ex:
            raise ValueError('Error: putting Company Name in table %r error %s'
                             % (db_dict, ex))

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


class CsvTargetsData(TargetsData):
    """Comma Separated Values form of the Target base."""

    def __init__(self, db_dict, dbtype, verbose):
        """Read the input file into a dictionary."""
        super(CsvTargetsData, self).__init__(db_dict, dbtype, verbose)

        fn = db_dict['filename']
        self.filename = fn

        # If the filename is not a full directory, the data file must be
        # either in the local directory or the same directory as the
        # config file defined by the db_dict entry directory
        if os.path.isabs(fn):
            if not os.path.isfile(fn):
                ValueError('CSV target data file %s does not exist ' % fn)
            else:
                self.filename = fn
        else:
            if os.path.isfile(fn):
                self.filename = fn
            else:
                full_fn = os.path.join(db_dict['directory'], fn)
                if not os.path.isfile(full_fn):
                    ValueError('CSV target data file %s does not exist '
                               'in local directory or config directory %s' %
                               (fn, db_dict['directory']))
                else:
                    self.filename = full_fn
        print('CSV database type ' % self)

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

        self.targets_dict = result

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

    def write_updated(self):
        """Backup the existing file and write the new one."""
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
            for key, value in sorted(self.targets_dict.iteritems()):
                writer.writerow(value)
