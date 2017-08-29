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
Argparse CLi for the temporary target script.

TODO: Remove this completely
"""
import os
import sys as _sys
import csv
import argparse as _argparse

from ._cliutils import SmartFormatter as _SmartFormatter
from ._targetdata import TargetsData
from .config import DEFAULT_CONFIG_FILE
from ._configfile import read_config

__all__ = ['ProcessTargetDataCli']


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

        DBTYPE = 'csv'

        db_config = read_config(args.config_file, DBTYPE)
        db_config['directory'] = os.path.dirname(args.config_file)
        target_data = TargetsData.factory(db_config, args, DBTYPE)

        # use dispatch pattern to invoke method with same name
        getattr(self, args.command)(target_data)

    def display(self, target_data):
        """
        Function to display table data.

        gets the arguments for the display and display the  Table data.
        """
        disp_parser = _argparse.ArgumentParser(
            description='Display target data repository')

        disp_parser.add_argument('-s', '--sort',
                                 default='IP',
                                 help='Sort by field')

        # now that we're inside a subcommand, ignore the first
        # TWO argvs, ie the command and the subcommand
        disp_parser.parse_args(_sys.argv[2:])

        print('keys %s' % list(target_data.table_format_dict))

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

        host_record = target_data.get_target(args.Id)

        # TODO add test to see if already in correct state

        if host_record is not None:
            host_record['EnableScan'] = False if args.enable is True else True
            target_data.write_updated()
        else:
            print('Id %s invalid or not in table' % args.Id)

        if args.list is True:
            target_data.display_disabled()

    def disabled(self, target_data):
        # ~ disp_parser = _argparse.ArgumentParser(
            # ~ description='Display disabled')
        # ~ # prefixing the argument with -- means it's optional
        # ~ disp_parser.add_argument('-f', '--file',
                                # ~ default='targetdata_example.csv',
                                # ~ help='Filename to display')
        # ~ args = disp_parser.parse_args(_sys.argv[2:])
        target_data.display_disabled()

    def fields(self, target_data):
        """Display the fields in the targetdata file."""
        # prefixing the argument with -- means it's optional

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
        record = target_data.get_target(args.server)

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
        record = target_data.get_target(record_id)
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
