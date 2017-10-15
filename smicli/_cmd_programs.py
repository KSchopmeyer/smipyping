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
from ._click_common import print_table


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
@click.option('-p', '--programname', type=str,
              default=None,
              required=True,
              help='Descriptive name for program')
@click.pass_obj
def programs_new(context, **options):  # pylint: disable=redefined-builtin
    """
    Add new program to the database.

    """
    context.execute_cmd(lambda: cmd_programs_new(context, options))


@programs_group.command('list', options_metavar=CMD_OPTS_TXT)
@click.pass_obj
def programs_list(context):  # pylint: disable=redefined-builtin
    """
    List programs in the database.
    """
    context.execute_cmd(lambda: cmd_programs_list(context))


@programs_group.command('delete', options_metavar=CMD_OPTS_TXT)
@click.argument('ID', type=int, metavar='ProgramID', required=True, nargs=1)
@click.option('-v', '--verify', is_flag=True,
              help='Verify the deletion before deleting the program.')
@click.pass_obj
def programs_delete(context, id, options):  # pylint: disable=redefined-builtin
    """
    Delete a program from the database.

    Delete the program defined by the subcommand argument from the
    database.
    """
    context.execute_cmd(lambda: cmd_programs_delete(context))


@programs_group.command('current', options_metavar=CMD_OPTS_TXT)
@click.pass_obj
def programs_current(context):  # pylint: disable=redefined-builtin
    """
    Get info on current program.

    Search database for current program and display info on this program
    """
    context.execute_cmd(lambda: cmd_programs_current(context))

######################################################################
#
#    Action functions
#
######################################################################


def cmd_programs_current(context):
    """
    """
    programs_tbl = ProgramsTable.factory(context.db_info, context.db_type,
                                         context.verbose)

    if programs_tbl.current():
        cp = programs_tbl.current()
        click.echo('Current program=%s(id=%s) started=%s ends=%s' %
                   (cp['ProgramName'], cp['ProgramID'], cp['StartDate'],
                    cp['EndDate']))
    else:
        click.ClickException('Error, no current program defined')


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
    print_table(tbl_rows, headers, title=('Programs Table'),
                table_format=context.output_format)


def cmd_programs_new(context, options):
    click.echo('Programs new NOT IMPLEMENTED')


def cmd_programs_delete(context, options):
    """Delete a program from the database."""
    click.echo('Programs delete NOT IMPLEMENTED')
