#!/usr/bin/env python
##

"""Define the user base and its data"""

# TODO change ip_address to hostname where host name is name : port

from __future__ import print_function, absolute_import

import os
import sys as _sys
import csv
import argparse as _argparse
import ConfigParser
from collections import OrderedDict
import six

from smipyping._cliutils import SmartFormatter as _SmartFormatter
from smipyping._terminaltable import print_terminal_table, fold_cell

__all__ = ['UserData',  'CsvUserData']

def get_config(config_file):
    """ Get config file."""

    # TODO put in separate module
    config = ConfigParser.SafeConfigParser()

    config_file = 'smipyping.cfg'
    config.read(config_file)
    config.get('smppyping', 'userdatafile')


class UserData(object):
    """Abstract top level class for the User Base.  This base contains
    information on the users, host systems, etc. in the environment
    """

    def __init__(self, filename, args):
        """Initialize the abstract UserData that controls all other
        user bases. This defines the common defintion of all users bases
        including field names, and common methods.
        """
        self.userdict = {}
        self.filename = filename
        # TODO this should be class level
        self.args = None
        self.verbose = True
        # Defines each record for the data base and outputs.
        # The Name is the database name for the property
        # The value tuple is display name and max width for the record
        # TODO this should be class level.
        self.table_format_dict = OrderedDict([
            ('Id', ('Id', 2)),
            ('CompanyName', ('Company', 13)),
            ('Namespace', ('Namespace', 12)),
            ('SMIVersion', ('SMIVersion', 12)),
            ('Product', ('Product', 15)),
            ('Principal', ('Principal', 12)),
            ('Credential', ('Credential', 12)),
            ('CimomVersion', ('Version', 15)),
            ('IPAddress', ('IP', 12)),
            ('InteropNamespace', ('Interop', 8)),
            ('Protocol', ('Prot', 5)),
            ('Port', ('Port', 4)),
            ('Disable', ('Disabled', 4)),
            ])

    def __str__(self):
        print('count=%s' % len(self.userdict))

    def get_expected_fields(self):
        """Return a list of the base table file names in the order defined"""
        return list(self.table_format_dict)

    def get_format_dict(self, name):
        """ Return tuple of display name and length for name"""
        return self.table_format_dict[name]

    def __contains__(self, record_id):
        """Determine if record_id is in userdata dictionary"""
        # TODO assumes string record_id
        return record_id in self.userdict

    def __getitem__(self, record_id):
        """Return the record for the defined record_id from the userdata."""
        return self.userdict[record_id].value

    def __delitem__(self, record_id):
        del self.userdict[record_id]

    def __len__(self):
        """Return number of users"""
        return len(self.userdict)

    def __iter__(self):
        """ iterator for userdata."""
        return six.iterkeys(self.userdict)

    # TODO we have multiple of these. See get dict_for_host,get_hostid_list
    def get_user_data_host(self, host_id):
        """If an record for `host_data` exists return that record. Else
            return None.

            Host data is a tuple of ipaddress and port.

            Note that   there may be multiple ipaddress, port entries for a
            single ipaddress, port in the database
            Returns list of userdata keys
        """
        # TODO clean up for PY 3
        return_list = []
        for key, value in self.userdict.iteritems():
            ip_address = value["IPAddress"]
            port = value["Port"]
            # TODO port from database is a string. Should be int internal.
            if ip_address == host_id[0] and int(port) == host_id[1]:
                return_list.append(key)

        return return_list

    # TODO remap this one to use get_item directly.
    def get_dict_record(self, requested_id):
        """If an entry for `record_data` exists return that record. Else
            return None.
            Record IDs are string
        """
        if not isinstance(requested_id, six.integer_types):
            requested_id = int(requested_id)

        for record_id in self.userdict:
            if int(record_id) == requested_id:
                return self.userdict[record_id]
        return None

    def get_dict_for_host(self, host):
        """ For a host address, get the dictionary record . Return None
            if not found. Does not work completely because of multiple IPs
        """

        for record_id, value in self.userdict.iteritems():
            if value['IPAddress'] == host:
                return value

        return None

    def filter_user_data(self, ip_filter=None, company_name_filter=None):
        if ip_filter:
            fd = dict((k, v) for k, v in self.userdict.items() \
                if ip_filter == k)
            return fd
        #TODO fix this
    def get_hostid_list(self, ip_filter=None, company_name_filter=None):
        """Get all WBEM Server ids in the user base. Returns list of
           IP addresses:port entries.
           TODO: Does not include port right now.
        """

        output_list = []
        # TODO clean up for python 3
        for _id, value in self.userdict.items():
            #print('_id %s, value %s' % (_id, value))
            output_list.append(value['IPAddress'])
        return output_list

    def tbl_hdr(self, record_list):
        """ Return a list of all the column headers from the record_list"""
        hdr = []
        for name in record_list:
            value = self.get_format_dict(name)
            hdr.append(value[0])
        return hdr

    def tbl_record(self, record_id, field_list):
        """ Return the fields defined in field_list for the record_id."""

        # TODO can we make this a std cvt function.

        record = self.get_dict_record(record_id)

        line = []
        for name in field_list:
            #cell_str = record[name]
            value = self.get_format_dict(name)
            if isinstance(name, six.string_types):
                #max_width = value[1]
                line.append(fold_cell(record[name], value[1]))
                #if max_width < len(cell_str):
                #    cell_str = '\n'.join(wrap(cell_str, max_width))
                #line.append(cell_str)
            else:
                line.append('%s' % record[name])
        return line

    def disabled_record(self, record):
        disable = record['Disable'].lower()
        if isinstance(disable, six.string_types):
            return disable == 'true'
        else:
            return disable

    def display_disabled(self):
        """Display diabled entries"""

        col_list = ['Id', 'IPAddress', 'CompanyName', 'Product',
                    'Port', 'Protocol', 'Disable']

        table_data = []

        table_data.append(self.tbl_hdr(col_list))

        # TODO can we do this with list comprehension
        for record_id in sorted(self.userdict.iterkeys()):
            if self.disabled_record(self.userdict[record_id]):
                table_data.append(self.tbl_record(record_id, col_list))

        print_terminal_table('Disabled hosts', table_data)

    def display_cols(self, column_list):
        """
        Display the columns of data defined by the col_list. This gets the
        data from the user data based on the col_list and prepares a table
        based on those user_data colums

        Parameters:
          column_list: list of strings defining the user_data columns to be
            displayed.

        """
        table_data = []

        # terminaltables creates the table headers from
        table_data.append(self.tbl_hdr(column_list))

        for record_id in sorted(self.userdict.iterkeys()):
            table_data.append(self.tbl_record(record_id, column_list))

        print_terminal_table('User Data Overview', table_data)

    def display_all(self):
        """Display all entries in the base"""
        col_list = ['Id', 'IPAddress', 'CompanyName', 'Product',
                    'Port', 'Protocol', 'CimomVersion']

        self.display_cols(col_list)

    def write_updated(self):
        """ Backup the existing file and write the new one."""
        backfile = '%s.bak' % self.filename
        # TODO does this cover directories/clean up for possible exceptions.
        if os.path.isfile(backfile):
            os.remove(backfile)
        os.rename(self.filename, backfile)
        self.write_file(self.filename)

    def write_file(self, file_name):
        """Write the current user base to the named file"""

        with open(file_name, 'wb') as f:
            writer = csv.DictWriter(f, fieldnames=self.get_expected_fields())
            writer.writeheader()
            for key, value in sorted(self.userdict.iteritems()):
                writer.writerow(value)


class CsvUserData(UserData):
    """ Comma Separated Values form of the User base"""

    def __init__(self, filename, args=None):
        """ Read the input file"""

        super(CsvUserData, self).__init__(filename, args)
        self.filename = filename
        reader = csv.DictReader(open(self.filename))

        # create dictionary (ip_address = key) with dictionary for
        # each set ofentries
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

        self.userdict = result
        self.args = args


class ProcessUserdataCli(object):
    """
    This class is part of the cli for userdata. It creates the argparse list
    and parses input in two separate functions.
    TODO: This should probably be in the cli itself but we are trying to
    create test tools for the cli so put here.
    Also split into separate functions to allow testing each.
    """

    def __init__(self, prog):
        argparser = _argparse.ArgumentParser(
            prog=prog,
            description='Manage user data',
            formatter_class=_SmartFormatter,
            usage="""userdata.py <command> [<args>]
The commands are:
   display     Display entries in the user data repository
   disable     Disable an record  in the table
   fields      list the fields in the user data repostiory
   record
   listdisabled
""")
        # a = RunUserData()
        # subcommands = a.__dict__.keys()
        argparser.add_argument(
            'command', metavar='cmd', help='Subcommand to run')

        args = argparser.parse_args(_sys.argv[1:2])
        if not hasattr(self, args.command):
            print('Unrecognized command %s ' % args.command)
            argparser.print_help()
            exit(1)

        # use dispatch pattern to invoke method with same name
        getattr(self, args.command)()

    def display(self):
        """ Function to get the arguments for the display and display the
            Table data
        """

        disp_parser = _argparse.ArgumentParser(
            description='Display user data repository')
        # prefixing the argument with -- means it's optional
        disp_parser.add_argument('-f', '--file',
                                 default='userdata_example.csv',
                                 help='Filename to display')

        disp_parser.add_argument('-s', '--sort',
                                 default='IP',
                                 help='Sort by field')

        # now that we're inside a subcommand, ignore the first
        # TWO argvs, ie the command and the subcommand
        args = disp_parser.parse_args(_sys.argv[2:])

        user_data = CsvUserData(args.file)

        # print('keys %s'  % list(user_data.table_format_dict))

        print('\n')
        user_data.display_all()

    def disable(self):
        """ Function to mark a particular userdata record disabled. """

        disable_parser = _argparse.ArgumentParser(
            description='Disable record  in the repository')
        # prefixing the argument with -- means it's optional
        disable_parser.add_argument(
            'Id',
            help='Set or reset the disable flag for the defined record ')

        # prefixing the argument with -- means it's optional
        disable_parser.add_argument(
            '-f', '--file',
            default='userdata_example.csv',
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

        user_data = CsvUserData(args.file)

        host_record = user_data.get_dict_record(args.Id)

        # TODO add test to see if already in correct state

        if host_record  is not None:

            current_state = host_record['Disable']

            host_record['Disable'] = False if args.enable is True else True
            user_data.write_updated()
        else:
            print('Id %s invalid or not in table' % args.Id)

        if args.list is True:
            user_data.display_disabled()

    def listdisabled(self):
        disp_parser = _argparse.ArgumentParser(
            description='Display disabled')
        # prefixing the argument with -- means it's optional
        disp_parser.add_argument('-f', '--file',
                                 default='userdata_example.csv',
                                 help='Filename to display')
        args = disp_parser.parse_args(_sys.argv[2:])

        user_data = CsvUserData(args.file)
        user_data.display_disabled()

    def fields(self):
        """
        Display the fields in the userdata file
        """

        parser = _argparse.ArgumentParser(
            description='List fields in file')
        # prefixing the argument with -- means it's optional

        parser.add_argument('-f', '--file',
                            default='userdata_example.csv',
                            help='Filename to display')
        args = parser.parse_args(_sys.argv[2:])
        user_data = CsvUserData(args.file)
        print('%s' % user_data.get_expected_fields())

    def find(self):
        parser = _argparse.ArgumentParser(
            description='Find a particular host')
            # prefixing the argument with -- means it's optional
        parser.add_argument('server',
                            help='Server IP address to find')
        parser.add_argument('-f', '--file',
                            default='userdata_example.csv',
                            help='Filename to display')
        args = parser.parse_args(_sys.argv[2:])
        user_data = CsvUserData(args.file)
        record = user_data.get_dict_record(args.server)
        # TODO separate get record  from display record .
        if record is None:
            print('%s not found' % args.server)
        else:
            print('%s found\n%s' % (args.server, record))

    def record(self):
        """
        Parse an input cli for hosts
        """
        parser = _argparse.ArgumentParser(
            description='List info on single record_id')
        # prefixing the argument with -- means it's optional
        parser.add_argument('record_id', type=int,
                            help='Record Id from the database. Integers')
        parser.add_argument('-f', '--file',
                            default='userdata_example.csv',
                            help='Filename to display')
        args = parser.parse_args(_sys.argv[2:])
        user_data = CsvUserData(args.file)
        record_id = "%2.2s" % args.record_id
        print('record %s' % record_id)
        # TODO get host ids from table
        record = user_data.get_dict_record(record_id)
        # TODO separate get record  from display record .
        if record is None:
            print('%s not found' % record_id)
        else:
            print('%s found\n%s' % (record_id, record))



