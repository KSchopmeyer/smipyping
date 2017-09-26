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
smicli commands based on python click for executing sweeps of selected
targets to find WBEM servers.
"""
from __future__ import print_function, absolute_import

import click
from click_datetime import Datetime
import six

from smipyping import ProgramsTable
from .smicli import cli, CMD_OPTS_TXT
from ._tableoutput import TableFormatter


@cli.group('programs', options_metavar=CMD_OPTS_TXT)
def programs_group():
    """
    Command group to process the history (pings) table in the
    database.

    Includes commands to clean the table and also to create various reports
    and tables of the history of tests on the WBEM servers in the
    targets database.

    """
    pass

# TODO make new program automatic extension of last


@programs_group.command('new', options_metavar=CMD_OPTS_TXT)
@click.option('-s', '--startdate', type=Datetime(format='%d/%m/%y'),
              default=None,
              required=True,
              help='Start date for program.')
@click.option('-e', '--enddate', type=Datetime(format='%d/%m/%y'),
              default=None,
              required=True,
              help='End date for program')
@click.option('-', '--programname', type=str,
              default=None,
              required=True,
              help='Descriptive name for program')
@click.pass_obj
def programs_new(context, **options):  # pylint: disable=redefined-builtin
    """
    Create fake cimping results in pings database.

    Execute simple cim ping against the list of ids provided for target servers
    in the database defined by each id in the list of ids creates a table
    showing result.

    ex. smicli cimping ids 5 8 9

    """
    context.execute_cmd(lambda: cmd_programs_new(context, options))


@programs_group.command('list', options_metavar=CMD_OPTS_TXT)
@click.pass_obj
def programs_list(context):  # pylint: disable=redefined-builtin
    """
    Create fake cimping results in pings database.

    Execute simple cim ping against the list of ids provided for target servers
    in the database defined by each id in the list of ids creates a table
    showing result.

    ex. smicli cimping ids 5 8 9

    """
    context.execute_cmd(lambda: cmd_programs_list(context))


######################################################################
#
#    Action functions
#
######################################################################


def cmd_programs_list(context):
    """
    List existing programs
    """
    programs_tbl = ProgramsTable.factory(context.db_info, context.db_type,
                                         context.verbose)

    headers = ProgramsTable.fields
    tbl_rows = []
    for program, data in six.iteritems(programs_tbl):
        row = [data[field] for field in headers]
        tbl_rows.append(row)

    context.spinner.stop()
    table = TableFormatter(tbl_rows, headers,
                           title=('Programs Table'),
                           table_format=context.output_format)
    click.echo(table.build_table())


def cmd_programs_new(context, options):
    click.echo('NOT IMPLEMENTED')
