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
from ._click_common import print_table, validate_prompt


@cli.group('programs', options_metavar=CMD_OPTS_TXT)
def programs_group():
    """
    Command group to handle programs table.

    The programs table defines programs in terms of start and end dates so
    that other commands can use specific programs to manage their tables.
    Normally a program is one year long and includes it start date, end date,
    and a program name.

    There are subcommands to create,modify, delete program entries and a list
    command that shows all entries in the table.
    """
    pass

# TODO make new program automatic extension of last


@programs_group.command('new', options_metavar=CMD_OPTS_TXT)
@click.option('-s', '--startdate', type=Datetime(format='%d/%m/%y'),
              default=None,
              required=True,
              help='Start date for program. Format is dd/mm/yy'
                   ' where dd and mm are zero padded (ex. 01) and year is'
                   ' without century (ex. 17)')
@click.option('-e', '--enddate', type=Datetime(format='%d/%m/%y'),
              default=None,
              required=True,
              help='End date for program. Format is dd/mm/yy'
                   ' where dd and mm are zero padded (ex. 01) and year is'
                   ' without century (ex. 17)')
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
@click.option('-n', '--no-verify', is_flag=True,
              help='Do not verify the deletion before deleting the program.')
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
    """
    Create a new program in the Programs table
    """
    start_date = options['startdate']
    end_date = options['enddate']
    program_name = options['programname']

    programs_tbl = ProgramsTable.factory(context.db_info, context.db_type,
                                         context.verbose)

    click.echo('Adding program %s starts %s, ends %s' %
               (program_name, start_date, end_date))

    if validate_prompt('Validate add this program?'):
        programs_tbl.insert(program_name, start_date, end_date)


def cmd_programs_delete(context, id, options):
    """Delete a user from the database."""

    programs_tbl = ProgramsTable.factory(context.db_info, context.db_type,
                                         context.verbose)
    program_id = id

    if program_id in programs_tbl:
        if options['no_verify']:
            programs_tbl.delete(program_id)
        else:
            program = programs_tbl[program_id]
            context.spinner.stop()
            click.echo(program)
            if validate_prompt('Delete program id %s' % program_id):
                programs_tbl.delete(program_id)
            else:
                click.echo('Abort Operation')
                return

    else:
        raise click.ClickException('The ProgramID %s is not in the table' %
                                   program_id)
