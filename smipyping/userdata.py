#!/usr/bin/env python
##

"""Define the user base and its data"""

# TODO change ip_address to hostname where host name is name : port

from __future__ import print_function, absolute_import

import os
import sys as _sys
import csv
import argparse as _argparse

import six

# required for main
from textwrap import wrap
from terminaltables import SingleTable
import ConfigParser

from smipyping._cliutils import SmartFormatter as _SmartFormatter
#from ._cliutils import SmartFormatter as _SmartFormatter

def get_config(config_file):
    config = ConfigParser.SafeConfigParser()

    config_file = 'smipyping.cfg'
    config.read(config_file)
    config.get('smppyping', 'userdatafile')

class UserData(object):
    """Abstract top level class for the User Base.  This base contains
    information on the users, host systems, etc. in the environment
    """

    def __init__(self):
        """Initialize the abstract UserData that controls all other
        user bases. This defines the common defintion of all users bases
        including field names, and common methods.
        """
        self.userdict = {}
        self.filename = None
        # TODO this should be class level
        self.expected_field_names = 'Id,CompanyName,Namespace,SMIVersion,' \
                'Product,Principal,Credential,CimomVersion,IPAddress,' \
                'InteropNamespace,Protocol,Port,Disable'
        self.expected_fields = self.expected_field_names.split(',')
        self.args = None
        self.verbose = True
        # Defines each table entry for the data base and outputs.
        # The Name is the database name for the property
        # The value tuple is display name and max width for the entry
        # TODO define means to create expected_name_fields
        # TODO this should be class level.
        self.table_format_dict = {'Id': ('Id', 2),
                                  'CompanyName': ('Company', 13),
                                  'Namespace': ('Namespace', 12),
                                  'SMIVersion': ('SMIVersion', 12),
                                  'Product': ('Product', 15),
                                  'Principal': ('Principal', 12),
                                  'Credential': ('Credential', 12),
                                  'CimomVersion': ('Version', 15),
                                  'IPAddress': ('IP', 12),
                                  'InteropNamespace': ('Interop', 8),
                                  'Protocol': ('Prot', 5),
                                  'Port': ('Port', 4),
                                  'Disable': ('Disabled', 4),
                                 }

    def __str__(self):
        print('count=%s' % len(self.userdict))

    def get_expected_fields(self):
        """Return list of the base field names"""
        return self.expected_fields

    def get_format_dict(self, name):
        """ return tuple of display name, length from dictionary for name"""
        return self.table_format_dict[name]

    # this one does not work because multiple ips in table
    # will need to return multiple
    def get_user_data_host(self, host_id):
        """If an entry for `host_data` exists return that entry. Else
            return None
            host_id = ipaddress:port
        """
        # TODO clean up for PY 3
        for key, value in self.userdict.iteritems():
            ip_address = value["IPAddress"]
            port = value["port"]
            this_host_id = '%s:%s' % (ip_address, port)
            if host_id in this_host_id:
                return value

        return None

    def get_dict_entry(self, entry_id):
        """If an entry for `host_data` exists return that entry. Else
            return None
        """
        if entry_id in self.userdict:
            return self.userdict[entry_id]
        else:
            return None

    def get_dict_for_host(self, host):
        """ For a host address, get the dictionary entry. Return None
            if not found. Does not work because of multiple IPs
        """

        for entry_id, value in self.userdict.iteritems():
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
        """

        output_list = []
        #print('userdict %s' % self.userdict)
        ## TODO clean up for python 3
        for _id, value in self.userdict.items():
            #print('_id %s, value %s' % (_id, value))
            output_list.append(value['IPAddress'])
        return output_list

    def tbl_hdr(self, entry_list):
        """ Return a list of all the column headers from the entry_list"""
        hdr = []
        for name in entry_list:
            value = self.get_format_dict(name)
            hdr.append(value[0])
        return hdr

    def tbl_entry(self, entry_id, entry_list):
        """ Return a list of entries for the entry_list"""

        entry = self.get_dict_entry(entry_id)

        line = []
        for name in entry_list:
            cell_str = entry[name]
            value = self.get_format_dict(name)
            if isinstance(value, six.string_types):
                max_width = value[1]
                if max_width < len(cell_str):
                    cell_str = '\n'.join(wrap(cell_str, max_width))
                line.append(cell_str)
            else:
                line.append('%s' % entry[name])
        return line

    def disabled_entry(self, entry):
        disable = entry['Disable']
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

        #TODO can we do this with list comprehension
        for entry_id in sorted(self.userdict.iterkeys()):
            if self.disabled_entry(self.userdict[entry_id]):
                table_data.append(self.tbl_entry(entry_id, col_list))

        #table_list = [self.userdict[id] for id in sorted(self.userdict.iterkeys())]

        #table_data = 

        self.print_table('Disabled hosts', table_data)

    def print_table(self, title, table_data):
        """ Print table data as an ascii table. The input is a dictionary
            of table data in the format used by terminaltable package
        """

        table_instance = SingleTable(table_data, title)
        table_instance. inner_column_border = False
        table_instance.outer_border = False

        print(table_instance.table)
        print()

    def display_cols(self, col_list):
        """ Display the columns of data defined by the col_list"""
        table_data = []

        table_data.append(self.tbl_hdr(col_list))

        for entry_id in sorted(self.userdict.iterkeys()):
            table_data.append(self.tbl_entry(entry_id, col_list))

        self.print_table('User data overviews', table_data)

    def display_all(self):
        """Display all entries in the base"""
        col_list = ['Id', 'IPAddress', 'CompanyName', 'Product',
                    'Port', 'Protocol', 'CimomVersion']

        self.display_cols(col_list)

    def write_updated(self):
        """ Backup the existing file and write the new one."""
        backfile = '%s.bak' % self.filename
        # TODO does this cover directories and clean up for possible exceptions.
        if os.path.isfile(backfile):
            os.remove(backfile)
        os.rename(self.filename, backfile)
        self.write_file(self.filename)

    def write_file(self, file_name):
        """Write the current user base to the named file"""

        with open(file_name, 'wb') as f:
            writer = csv.DictWriter(f, fieldnames=self.expected_fields)
            writer.writeheader()
            for key, value in sorted(self.userdict.iteritems()):
                writer.writerow(value)

class CsvUserData(UserData):
    """ Comma Separated Values form of the User base"""

    def __init__(self, filename, args=None):
        super(CsvUserData, self).__init__()
        self.filename = filename
        reader = csv.DictReader(open(self.filename))

        # create dictionary (ip_address = key) with dictionary for
        # each set ofentries
        result = {}
        for row in reader:
            key = row['Id']
            if key in result:
                # duplicate row handling
                print('ERROR. Duplicate Id in table: %s\nrow=%s' % \
                      (key, row))
                raise ValueError('Input Error. duplicate Id')
            else:
                result[key] = row

        self.userdict = result
        self.args = args

class main(object):

    def __init__(self):
        argparser = _argparse.ArgumentParser(
            prog='userdata',
            description='Manage user data',
            formatter_class=_SmartFormatter,
            usage="""userdata.py <command> [<args>]
The commands are:
   display     Display entries in the user data repository
   disable     Disable an entry in the table
   fields      list the fields in the user data repostiory
   test        temp function to do whatever testing we build in
   hosts
   listdisabled
""")
        #a = RunUserData()
        #subcommands = a.__dict__.keys()
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

        print('\n')
        user_data.display_all()

    def disable(self):
        """ Function todisable a particular entry
        """

        disable_parser = _argparse.ArgumentParser(
            description='Disable entry in the repository')
        # prefixing the argument with -- means it's optional
        disable_parser.add_argument(
            'Id',
            help='Set or reset the disable flag for the defined entry')

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
                 'entry rather than disable it')

        # now that we're inside a subcommand, ignore the first
        # TWO argvs, ie the command and the subcommand
        args = disable_parser.parse_args(_sys.argv[2:])

        user_data = CsvUserData(args.file)

        host_entry = user_data.get_dict_entry(args.Id)

        # TODO add test to see if already in correct state

        if host_entry is not None:
            
            current_state = host_entry['Disable']
            
            host_entry['Disable'] = False if args.enable is True else True
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

    def test(self):
        """ Function to test other subfunctions.
        """

        disp_parser = _argparse.ArgumentParser(
            description='test something')

        disp_parser.add_argument(
            'server', metavar='server', nargs='?')

        disp_parser.add_argument(
            '-o', '--outputfile',
            help='output file')

        # prefixing the argument with -- means it's optional
        disp_parser.add_argument('-f', '--file',
                                 default='userdata_example.csv',
                                 help='Filename to display')

        # now that we're inside a subcommand, ignore the first
        # TWO argvs, ie the command and the subcommand
        opts = disp_parser.parse_args(_sys.argv[2:])

        print('opts = %s' % opts)

        print('outputfile %s' % opts.outputfile)

        if opts.outputfile is None:
            disp_parser.error('No output file specified')
        print('test, output=%s' % opts.outputfile)

        user_data = CsvUserData(opts.file)

        host_entry = user_data.get_dict_for_host(opts.server)
        if host_entry is not None:
            print('host_entry %s' % host_entry)
            host_entry['Disable'] = True
            user_data.write_new('tempnewfile.csv')
        else:
            print('host_entry for %s not found' % host_entry)

    def fields(self):
        parser = _argparse.ArgumentParser(
            description='List fields in file')
        # prefixing the argument with -- means it's optional

        parser.add_argument('-f', '--file',
                            default='userdata_example.csv',
                            help='Filename to display')
        args = parser.parse_args(_sys.argv[2:])
        user_data = CsvUserData(args.file)
        print('%s' % user_data.expected_field_names)

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
        entry = user_data.get_dict_entry(args.server)
        # TODO separate get entry from display entry.
        if entry is None:
            print('%s not found' % args.server)
        else:
            print('%s found\n%s' % (args.server, entry))

    def hosts(self):
        parser = _argparse.ArgumentParser(
            description='List fields in file')
        # prefixing the argument with -- means it's optional
        parser.add_argument('server',
                            help='Filename to display')
        parser.add_argument('-f', '--file',
                            default='userdata_example.csv',
                            help='Filename to display')
        args = parser.parse_args(_sys.argv[2:])
        user_data = CsvUserData(args.file)
        # TODO get host ids from table
        entry = user_data.get_dict_entry(args.server)
        # TODO separate get entry from display entry.
        if entry is None:
            print('%s not found' % args.server)
        else:
            print('%s found\n%s' % (args.server, entry))

if __name__ == '__main__' and __package__ is None:
    main()


