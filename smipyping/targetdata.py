#!/usr/bin/env python
##

"""
Define the base of targets (i.e. systems to be testested)

"""

# TODO change ip_address to hostname where host name is name : port

from __future__ import print_function, absolute_import

import os
import sys as _sys
import csv
import argparse as _argparse
from configparser import ConfigParser
from collections import OrderedDict
import six
from mysql.connector import MySQLConnection, Error

from smipyping._cliutils import SmartFormatter as _SmartFormatter
from smipyping._terminaltable import print_terminal_table, fold_cell
from smipyping.config import DEFAULT_CONFIG_FILE

__all__ = ['TargetsData', 'ProcessTargetDataCli']


def read_config(filename, section):
    """
    Read configuration file for section and return a dictionary object if that
    section is found

    :param filename: name of the configuration file
    :param section: name of the section (ex. mysql)
    :return: a dictionary of database parameters
    """
    # create parser and read ini configuration file
    print('read_config file %s, section %s' % (filename, section))
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

    def __init__(self, filename, args):
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
        self.args = args
        self.verbose = args.verbose
        self.targets_dict = {}
        self.filename = filename
        self.args = args
        self.verbose = True
        # # Defines each record for the data base and outputs.
        # # The Name is the database name for the property
        # # The value tuple is display name and max width for the record
        # # TODO this should be class level.
        self.table_format_dict = OrderedDict([
            ('Id', ('Id', 2, int)),
            ('CompanyName', ('Company', 13, str)),
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
    def factory(cls, filename, args, type):
        """Factory method to select subclass based on database type.
           Currently the types sql and csv are supported
        """

        inst = None
        if type == ('csv'):
            print('type is csv %s' % type)
            inst = CsvTargetsData(filename, args)

        elif type == ('sql'):
            inst = SQLTargetsData(filename, args)

        else:
            ValueError('Invalid target factory type %s' % type)

        return inst


    def __str__(self):
        """String info on targetdata. TODO. Put more info her"""
        print('count=%s' % len(self.targetsdict))

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

        Else return None.
            Record IDs are string
        """
        if not isinstance(requested_id, six.integer_types):
            requested_id = int(requested_id)

        for record_id in self.targetsdict:
            if int(record_id) == requested_id:
                return self.targetsdict[record_id]
        return None

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
        if ip_filter:
            fd = dict((k, v) for k, v in self.targetsdict.items()
                if ip_filter == k)
            return fd
        # TODO fix this

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
        col_list = ['Id', 'IPAddress', 'CompanyName', 'Product',
                    'Port', 'Protocol', 'CimomVersion']

        self.display_cols(col_list)

class SQLTargetsData(TargetsData):
    """Source is sql data"""
    # TODO filename is config file name, not actual file name.
    def __init__(self, filename, args=None):
        """Read the input file into a dictionary."""
        super(CsvTargetsData, self).__init__(filename, args)

        try:
            db_config = read_config(filename, 'mysql')
            connection = MySQLConnection(**db_config)

            if connection.is_connected():
                print('connection established.')
            else:
                print('connection failed.')
                raise ValueError('Connection to database failed')
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM Targets')
            row = cursor.fetchone()
            result = {}
            while row is not None:
                key = int(row['TargetID'])
                result[key] = row
                row = cursor.fetchone()
        except Exception as ex:
            print('Could not initialize sql database')

        self.targetsdict = result
        # TODO need to build Company into targets dict.
        self.args = args


class CsvTargetsData(TargetsData):
    """Comma Separated Values form of the Target base."""

    def __init__(self, filename, args=None):
        """Read the input file into a dictionary."""
        # print('csvtargetsdata iconfig filename = %s' % filename)
        csv_config = read_config(filename, 'csv')
        # print('csv_config %s ' % csv_config)
        super(CsvTargetsData, self).__init__(filename, args)
        self.filename = csv_config['filename']
        # print('CSV FILENAME %s' % self.filename)


        with open(self.filename) as input_file:
            reader = csv.DictReader(input_file)
            # create dictionary (id = key) with dictionary for
            # each set of entries
            result = {}
            for row in reader:
                key = int(row['Id'])
                if key in result:
                    # duplicate row handling
                    print('ERROR. Duplicate Id in table: %s\nrow=%s' %
                          (key, row))
                    raise ValueError('Input Error. duplicate Id')
                else:
                    result[key] = row

        self.targetsdict = result
        self.args = args

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


class ProcessTargetDataCli(object):
    """
    This class is part of the cli for Target data.

    It creates the argparse list
    and parses input in two separate functions.
    TODO: This should probably be in the cli itself but we are trying to
    create test tools for the cli so put here.
    Also split into separate functions to allow testing each.
    """

    def __init__(self, prog):
        argparser = _argparse.ArgumentParser(
            prog=prog,
            description='Manage Target data',
            formatter_class=_SmartFormatter,
            usage="""targetdata <command> [<args>]
The commands are:
   display     Display entries in the Targets data repository
   disable     Disable an record  in the table
   fields      list the fields in the target data repostiory
   record      Display the record for a particular target_id
   disabled    list all records disabled (i.e. ScanEnabled = False)
""")
        # a = RunTargetData()
        # subcommands = a.__dict__.keys()
        argparser.add_argument(
            'command', metavar='cmd', help='Subcommand to run')

        argparser.add_argument(
            '-f', '--config_file', metavar='CONFIG_FILE',
            default=DEFAULT_CONFIG_FILE,
            help=('Configuration file to use for config information. '
            'Default=%s' % DEFAULT_CONFIG_FILE))
        argparser.add_argument(
            '-v', '--verbose', action='store_true', default=False)

        argparser.add_argument(
            '-d', '--dbtype', choices=('csv', 'sql'), default=csv,
            help='Choice of database type')

        args = argparser.parse_args(_sys.argv[1:2])
        if not hasattr(self, args.command):
            print('Unrecognized command %s ' % args.command)
            argparser.print_help()
            exit(1)

        # TODO test if type is actually supported in config file
        

        target_data = TargetsData.factory(args.config_file, args, 'csv')

        # use dispatch pattern to invoke method with same name
        getattr(self, args.command)(target_data)

    def display(self, target_data):
        """
        Function to display table data.

        gets the arguments for the display and display the  Table data.
        """
        disp_parser = _argparse.ArgumentParser(
            description='Display target data repository')
        # prefixing the argument with -- means it's optional
        disp_parser.add_argument('-f', '--file',
                                 default='targetdata_example.csv',
                                 help='Filename to display')

        disp_parser.add_argument('-s', '--sort',
                                 default='IP',
                                 help='Sort by field')

        # now that we're inside a subcommand, ignore the first
        # TWO argvs, ie the command and the subcommand
        args = disp_parser.parse_args(_sys.argv[2:])

        print('keys %s'  % list(target_data.table_format_dict))

        print('\n')
        target_data.display_all()

    def disable(self, target_data):
        """Function to mark a particular targetdata record disabled."""
        disable_parser = _argparse.ArgumentParser(
            description='Disable record  in the repository')
        # prefixing the argument with -- means it's optional
        disable_parser.add_argument(
            'Id',
            help='Set or reset the disable flag for the defined record ')

        # prefixing the argument with -- means it's optional
        disable_parser.add_argument(
            '-f', '--file',
            default='targetdata_example.csv',
            help='Filename to display')

        disable_parser.add_argument(
            '-l', '--list',
            action='store_true', default=False,
            help='List all the disabled entries')

        disable_parser.add_argument(
            '-e', '--enable',
            action='store_true', default=False,
            help='Set the disable flag to enable the '
                 'record  rather than disable it')

        # now that we're inside a subcommand, ignore the first
        # TWO argvs, ie the command and the subcommand
        args = disable_parser.parse_args(_sys.argv[2:])

        host_record = target_data.get_dict_record(args.Id)

        # TODO add test to see if already in correct state

        if host_record is not None:

            current_state = host_record['EnableScan']

            host_record['EnableScan'] = False if args.enable is True else True
            target_data.write_updated()
        else:
            print('Id %s invalid or not in table' % args.Id)

        if args.list is True:
            target_data.display_disabled()

    def disabled(self, target_data):
        #~ disp_parser = _argparse.ArgumentParser(
            #~ description='Display disabled')
        #~ # prefixing the argument with -- means it's optional
        #~ disp_parser.add_argument('-f', '--file',
                                 #~ default='targetdata_example.csv',
                                 #~ help='Filename to display')
        #~ args = disp_parser.parse_args(_sys.argv[2:])
        target_data.display_disabled()

    def fields(self, target_data):
        """Display the fields in the targetdata file."""
        parser = _argparse.ArgumentParser(
            description='List fields in file')
        # prefixing the argument with -- means it's optional
        args = parser.parse_args(_sys.argv[2:])

        print('\n'.join(target_data.get_field_list()))

    def find(self, target_data):
        parser = _argparse.ArgumentParser(
            description='Find a particular host')
        parser.add_argument('server',
                            help='Server IP address to find')
        parser.add_argument('-f', '--file',
                            default='targetdata_example.csv',
                            help='Filename to display')
        args = parser.parse_args(_sys.argv[2:])
        record = target_data.get_dict_record(args.server)

        # TODO separate get record  from display record .
        if record is None:
            print('%s not found' % args.server)
        else:
            print('%s found\n%s' % (args.server, record))

    def record(self, target_data):
        """
        Parse an input cli for hosts.
        """
        parser = _argparse.ArgumentParser(
            description='List info on single record_id')
        # prefixing the argument with -- means it's optional
        parser.add_argument('record_id', type=int,
                            help='Record Id from the database. Integers')
        parser.add_argument('-f', '--file',
                            default='targetdata_example.csv',
                            help='Filename to display')
        args = parser.parse_args(_sys.argv[2:])

        record_id = "%2.2s" % args.record_id
        # TODO get host ids from table
        record = target_data.get_dict_record(record_id)
        # TODO separate get record  from display record .
        if record is None:
            print('Record %s not found in Targets data.' % record_id)
        else:
            max_len = 0
            for key in record:
                if max_len < len(key):
                    max_len = len(key)
            for key in record:
                print('%*s : %s' % (max_len, key, record[key]))
