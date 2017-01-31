#!/usr/bin/env python
##

"""
Define the base of targets (i.e. systems to be tested)

"""

# TODO change ip_address to hostname where host name is name : port

from __future__ import print_function, absolute_import

import os
import csv
import re
from collections import OrderedDict
from configparser import ConfigParser
import six
from mysql.connector import MySQLConnection, Error


from smipyping._terminaltable import print_terminal_table, fold_cell

__all__ = ['TargetsData']


def read_config(filename, section):
    """
    Read configuration file for section and return a dictionary object if that
    section is found

    :param filename: name of the configuration file
    :param section: name of the section (ex. mysql)
    :return: a dictionary of database parameters
    """
    # create parser and read ini configuration file
    parser = ConfigParser()
    parser.read(filename)

    # get section, default to mysql
    db = {}
    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            db[item[0]] = item[1]
    else:
        raise TypeError('{0} not found in the {1} file'.format(section,
                                                               filename))

    return db


class TargetsData(object):
    """Abstract top level class for the Target Base.

    This base contains information on the targets, host systems, etc. in the
    environment.
    """

    def __init__(self, filename, verbose):
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
        self.filename = filename
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

    @classmethod
    def factory(cls, filename, type, verbose):
        """Factory method to select subclass based on database type.
           Currently the types sql and csv are supported.

           Returns instance object of the defined provider type.
        """

        inst = None
        if verbose:
            print('targetdata factory file %s type %s v %s' % (filename, type,
                                                               verbose))
        if type == ('csv'):
            inst = CsvTargetsData(filename, verbose)

        elif type == ('sql'):
            inst = SQLTargetsData(filename, verbose)

        else:
            ValueError('Invalid target factory type %s' % type)

        inst.type_ = type

        return inst

    def __str__(self):
        """String info on targetdata. TODO. Put more info her"""
        return ('count=%s' % len(self.targetsdict))

    def __repr__(self):
        """Rep of target data"""
        return ('Targetdata rep count=%s' % len(self.targetsdict))

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

        Else return None.

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

    def get_dict_for_host(self, host):
        """
        For a host address, get the dictionary record .

        Return: None

        If not found. Does not work completely because of multiple IPs
        """
        for record_id, value in self.targetsdict.iteritems():
            if value['IPAddress'] == host:
                return value

        return None

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
            # print('_id %s, value %s' % (_id, value))
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

    def disabled_record(self, target_record):
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

    def display_all(self):
        """Display all entries in the base."""
        col_list = ['TargetID', 'IPAddress', 'CompanyName', 'Product',
                    'Port', 'Protocol', 'CimomVersion']

        self.display_cols(col_list)


class SQLTargetsData(TargetsData):
    """Source is sql data"""
    # TODO filename is config file name, not actual file name.
    def __init__(self, filename, verbose):
        """Read the input file into a dictionary."""

        print('SQL Database type %s %s' % (filename, verbose))
        super(SQLTargetsData, self).__init__(filename, verbose)

        try:
            db_config = read_config(filename, 'mysql')
            connection = MySQLConnection(**db_config)

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
                             % (db_config, ex))

    def db_info(self):
        db_config = read_config(self.filename, 'mysql')
        return db_config


class CsvTargetsData(TargetsData):
    """Comma Separated Values form of the Target base."""

    def __init__(self, filename, verbose):
        """Read the input file into a dictionary."""
        super(CsvTargetsData, self).__init__(filename, verbose)

        csv_config = read_config(filename, 'csv')
        self.filename = csv_config['filename']

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

    def db_info(self):
        db_config = read_config(self.filename, 'csv')
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
