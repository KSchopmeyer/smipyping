#!/usr/bin/env python
#
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

"""Define the user base and its data"""

# TODO change ip_address to hostname where host name is name : port

from __future__ import print_function, absolute_import
import csv

# required for main
import argparse as _argparse
import sys
from _cliutils import SmartFormatter as _SmartFormatter

class UserDataEntry(object):
    """Manage individual properties in a UserData entry"""

    def __init__(self, entry):
        self.entry = entry

    @property
    def id(self):
        return self.entry['Id']
    @property
    def ip_address(self):
        """Access to the ip_address property"""
        return self.entry['IPAddress']
    @property
    def company_name(self):
        return self.entry['CompanyName']
    @property
    def product(self):
        return self.entry['Product']
    @property
    def port(self):
        return self.entry['Port']
    @property
    def protocol(self):
        return self.entry['Protocol']
    @property
    def version(self):
        return self.entry['CimomVersion']
    @property
    def interop_ns(self):
        return self.entry['InteropNamespace']
    @property
    def principal(self):
        return self.entry['Principal']
    @property
    def credential(self):
        return self.entry['Credential']


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
                'InteropNamespace,Protocol,Port'
        self.expected_fields = self.expected_field_names.split(',')
        self.args = None
        self.verbose = True

    def __str__(self):
        print('count=%s' % len(self.userdict))

    def get_expected_fields(self):
        """Return list of the base field names"""
        return self.expected_fields

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
                return UserDataEntry(value)
        
        return None

    def get_dict_entry(self, entry_id):
        """If an entry for `host_data` exists return that entry. Else
            return None
        """
        if entry_id in self.userdict:
            return self.userdict[entry_id]
        else:
            raise ValueError("Invalid id %s" % entry_id)

    def get_dict_for_host(self, host):
        """ For a host address, get the dictionary entry"""

        for entry_id, value in self.userdict.iteritems():
            if value['IPAddress'] == host:
                return value
        raise ValueError('IP %s not in list' % host)

    def filter_user_data(self, ip_filter=None, company_name_filter=None):
        if ip_filter:
            fd = dict((k, v) for k, v in self.userdict.items() if ip_filter == k)
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

    def display_tbl_hdr(self):
        print ('%-2.2s %-12.12s %-16.16s %-18.18s %-4.4s %-6.6s %-10.10s' %
               ('Id', 'IP', 'Company', 'Product', 'Port', 'Protocol', 'Version'))

    def display_entry(self, entry_id):
        """ Display the field entries for a single ip_address:port.
            The address is ip_address:port
        """

        entry = self.get_dict_entry(entry_id)
        if entry is not None:
            print('%-2.2s %-12.12s %-16.16s %-18.18s %-4.4s %-6.6s %-4.14s'
                  % (entry["Id"],
                     entry['IPAddress'],
                     entry['CompanyName'],
                     entry['Product'],
                     entry['Port'],
                     entry['Protocol'],
                     entry['CimomVersion']))
        else:
            print('None')

    def display_all(self):
        """Display all entries in the base"""

        for entry_id in self.userdict:
            self.display_entry(entry_id)

    def write_new(self, file_name):
        """Write the current user base to the named file"""

        with open(file_name, 'wb') as f:
            writer = csv.DictWriter(f, fieldnames=self.expected_fields)
            writer.writeheader()
            # write each row dictionary
            for key, value in self.userdict.iteritems():
                ln = [key]
                for ik, iv in value.iteritems():
                    ln.append(ik)
                    ln.extend([v for v in iv])
                writer.writerow(ln)


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
   fields      list the fields in the user data repostiory
   hosts
""")
        #a = RunUserData()
        #subcommands = a.__dict__.keys()
        argparser.add_argument(
            'command', metavar='cmd', help='Subcommand to run')

        args = argparser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print('Unrecognized command %s ' % args.command)
            argparser.print_help()
            exit(1)

        # use dispatch pattern to invoke method with same name
        getattr(self, args.command)()

    def display(self):

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
        args = disp_parser.parse_args(sys.argv[2:])
        print('display, file=%s' % args.file)

        user_data = CsvUserData(args.file)

        print('\n')
        user_data.display_tbl_hdr()
        user_data.display_all()

    def fields(self):
        parser = _argparse.ArgumentParser(
            description='List fields in file')
        # prefixing the argument with -- means it's optional

        parser.add_argument('-f', '--file',
                            default='userdata_example.csv',
                            help='Filename to display')
        args = parser.parse_args(sys.argv[2:])
        user_data = CsvUserData(args.file)
        print('%s' % user_data.expected_field_names)


    def find(self):
        parser = _argparse.ArgumentParser(
            description='Find a particular host')
        # prefixing the argument with -- means it's optional
        parser.add_argument('server',
                            help='Filename to display')
        parser.add_argument('-f', '--file',
                            default='userdata_example.csv',
                            help='Filename to display')
        args = parser.parse_args(sys.argv[2:])
        user_data = CsvUserData(args.file)
        entry = user_data.get_dict_entry(args.server)
        #TODO separate get entry from display entry.
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
        args = parser.parse_args(sys.argv[2:])
        user_data = CsvUserData(args.file)
        # TODO get host ids from table
        entry = user_data.get_dict_entry(args.server)
        #TODO separate get entry from display entry.
        if entry is None:
            print('%s not found' % args.server)
        else:
            print('%s found\n%s' % (args.server, entry))

if __name__ == '__main__':
    main()


