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
        target bases. This defines the common defintion of all targets bases
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
    def factory(cls, db_dict, db_type,  verbose):
        """Factory method to select subclass based on database type.
           Currently the types sql and csv are supported.

           Returns instance object of the defined provider type.
        """

        inst = None
        if verbose:
            print('targetdata factory datafile %s type %s v %s'
                  % (db_dict,
                     db_type,
                     verbose))
        if db_type == ('csv'):
            inst = CsvTargetsData(db_dict, db_type, verbose)

        elif db_type == ('sql'):
            inst = SQLTargetsData(db_dict, db_type, verbose)

        else:
            ValueError('Invalid target factory db_type %s' % db_type)

        return inst

    def __str__(self):
        """String info on targetdata. TODO. Put more info her"""
        return ('count=%s' % len(self.targetsdict))

    def __repr__(self):
        """Rep of target data"""
        return ('Targetdata filename%s db_type %s, rep count=%s' %
                (self.filename, self.db_type, len(self.targetsdict)))

    def get_field_list(self):
        """Return a list of the base table file names in the order defined."""
        return list(self.table_format_dict)

    def get_format_dict(self, name):
        """Return tuple of display name and length for name."""
        return self.table_format_dict[name]

    def __contains__(self, record_id):
        """Determine if record_id is in targets dictionary."""
        return record_id in self.targetsdict

    def __iter__(self):
        """iterator for targets."""
        return six.iterkeys(self.targetsdict)

    def iteritems(self):
        """
        Iterate through the property names (in their original lexical case).

        Returns key and value
        """
        for key, val in self.targetsdict.iteritems():
            yield (key, val)

    def __getitem__(self, record_id):
        """Return the record for the defined record_id from the targets."""
        return self.targetsdict[record_id]

    def __delitem__(self, record_id):
        del self.targetsdict[record_id]

    def __len__(self):
        """Return number of targets"""
        return len(self.targetsdict)

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
        for key, value in self.targetsdict.iteritems():
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

        return self.targetsdict[requested_id]

    def get_target_for_host(self, target_addr):
        """
        For a host address, get the targets dictionary record if it exists.

        Parameters:
            target_addr: hostname/IPAddress of target

        Returns: None if not found or possibly multiple target_ids

        If not found. Does not work completely because of multiple IPs
        """
        targets = []
        for target_id, value in self.targetsdict.iteritems():
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
        for key, value in self.targetsdict.items():
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
        for _id, value in self.targetsdict.items():
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
        for record_id in sorted(self.targetsdict.iterkeys()):
            if self.disabled_record(self.targetsdict[record_id]):
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

        for record_id in sorted(self.targetsdict.iterkeys()):
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
    """Source is sql data"""
    # TODO filename is config file name, not actual file name.
    def __init__(self, db_dict, dbtype, verbose):
        """Read the input file into a dictionary."""

        print('SQL Database type %s %s' % (db_dict, verbose))
        super(SQLTargetsData, self).__init__(db_dict, dbtype, verbose)

        try:
            connection = MySQLConnection(**db_dict)

            if connection.is_connected():
                print('connection established.')
            else:
                print('SQL database connection failed.')
                raise ValueError('Connection to database failed')
            cursor = connection.cursor(dictionary=True)
            companies = {}
            cursor.execute('SELECT * FROM Companies')
            rows = cursor.fetchall()
            for row in rows:
                key = int(row['CompanyID'])
                # print('companies key %s value %s' % (key, row))
                companies[key] = row

            result = {}
            cursor.execute('SELECT * FROM Targets')
            rows = cursor.fetchall()
            for row in rows:
                key = int(row['TargetID'])
                # denormalize CompanyId by adding CompanyName
                row['CompanyName'] = companies[row['CompanyID']]['CompanyName']
                result[key] = row

            self.targetsdict = result

        except Exception as ex:
            print('Could not access sql database. Exception %s', str(ex))
            raise ValueError('Could not initialize sql database %r error %s'
                             % (db_dict, ex))

    def db_info(self):
        """ Return info on the database used"""
        try:

            db_config = read_config(self.filename, self.db_type)
        except ValueError as ve:
            print('Section %s not in configfile %s %ve' % (self.db_type,
                                                           self.filename,
                                                           ve))
        return db_config


class CsvTargetsData(TargetsData):
    """Comma Separated Values form of the Target base."""

    def __init__(self, db_dict, dbtype, verbose):
        """Read the input file into a dictionary."""
        super(CsvTargetsData, self).__init__(db_dict, dbtype, verbose)

        self.filename = db_dict['filename']

        if not os.path.isfile(self.filename):
            ValueError('CSV provider data file %s does not exist.' %
                       self.filename)

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

        self.targetsdict = result

    # TODO consolidate this to use predefined type.
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
            for key, value in sorted(self.targetsdict.iteritems()):
                writer.writerow(value)
