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

from datetime import timedelta
import click
from click_datetime import Datetime
from dateutil.relativedelta import relativedelta
import six
from mysql.connector import Error as mysqlerror

from smipyping import ProgramsTable, PingsTable, datetime_display_str
from .smicli import cli, CMD_OPTS_TXT
from ._click_common import print_table, validate_prompt, pick_from_list


def pick_programid(context, programs_tbl):
    """
    Interactive selection of target id from list presented on the console.

      Parameters ()
         The click_context which contains target data information.

      Returns:
        target_id selected or None if user enter ctrl-C
    """
    db_keys = programs_tbl.keys()
    display_options = []
    for t in db_keys:
        item = programs_tbl[t]

        display_options.append(u'   id=%s, %s %s, %s' %
                               (t, item['ProgramName'],
                                item['StartDate'],
                                item['StartDate']))
    try:
        index = pick_from_list(context, display_options, "Pick Program:")
    except ValueError:
        pass
    if index is None:
        click.echo('Abort command')
        return None
    return db_keys[index]


def get_programid(context, db_tbl, programid, options=None):
    """
        Get the user based on the value of programid or the value of the
        interactive option.  If programid is an
        integer, get it directly and generate exception if this fails.
        If it is ? use the interactive pick_target_id.
        If options exist test for 'interactive' option and if set, call
        pick_target_id
        This function executes the pick function if the targetid is "?" or
        if options is not None and the interactive flag is set

        This support function always tests the programid to against the
        targets table.

        Returns:
            Returns integer user_id of a valid targetstbl TargetID

        raises:
          KeyError if user_id not in table
    """
    context.spinner.stop()
    if options and 'interactive' in options and options['interactive']:
        context.spinner.stop()
        programid = pick_programid(context, db_tbl)
    elif isinstance(programid, six.integer_types):
        try:
            programid = db_tbl[programid]
            context.spinner.start()
            return programid
        except KeyError as ke:
            raise click.ClickException("ProgramID %s  not valid: exception %s" %
                                       (programid, ke))
    elif isinstance(programid, six.string_types):
        if programid == "?":
            context.spinner.stop()
            programid = pick_programid(context, db_tbl)
        else:
            try:
                programid = int(programid)
            except ValueError:
                raise click.ClickException('ProgramID must be integer or "?" '
                                           'not %s' % programid)
            try:
                # test if programid in table
                db_tbl[programid]  # pylint: disable=pointless-statement
                context.spinner.start()
                return programid
            except KeyError as ke:
                raise click.ClickException("ProgramID %s  not found in Users "
                                           "table: exception %s" %
                                           (programid, ke))
    else:
        raise click.ClickException('ProgramID %s. Requires ProgramID, ? or '
                                   '--interactive option' % programid)
    if programid is None:
        click.echo("Operation aborted by user.")
    context.spinner.start()
    return programid


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


@programs_group.command('add', options_metavar=CMD_OPTS_TXT)
@click.option('-s', '--startdate', type=Datetime(format='%d/%m/%y'),
              default=None,
              required=False,
              help='Start date for program. Format is dd/mm/yy '
                   'where dd and mm are zero padded (ex. 01) and year is '
                   'without century (ex. 17). This option is optional and if '
                   'not supplied the day after the end of the latest program '
                   'will be selected.')
@click.option('-e', '--enddate', type=Datetime(format='%d/%m/%y'),
              default=None,
              required=False,
              help='End date for program. Format is dd/mm/yy '
                   'where dd and mm are zero padded (ex. 01) and year is '
                   'without century (ex. 17). This field is optional and if '
                   'not defined on the command line 12 montsh - 1 day after '
                   'the start date will be used as the end date.')
@click.option('-p', '--programname', type=str,
              default=None,
              required=True,
              help='Descriptive name for program')
@click.pass_obj
def programs_add(context, **options):  # pylint: disable=redefined-builtin
    """
    Add new program to the database.

    """
    context.execute_cmd(lambda: cmd_programs_add(context, options))


@programs_group.command('list', options_metavar=CMD_OPTS_TXT)
@click.pass_obj
def programs_list(context):  # pylint: disable=redefined-builtin
    """
    List programs in the database.
    """
    context.execute_cmd(lambda: cmd_programs_list(context))


@programs_group.command('delete', options_metavar=CMD_OPTS_TXT)
@click.argument('ProgramID', type=str, metavar='ProgramID', required=True,
                nargs=1)
@click.option('-n', '--no-verify', is_flag=True,
              help='Do not verify the deletion before deleting the program.')
@click.option('-i', '--interactive', is_flag=True, default=False,
              help='If set, presents list of programs from which one can be '
                   'chosen.')
@click.pass_obj
def programs_delete(context, programid, **options):
    # pylint: disable=redefined-builtin
    """
    Delete a program from the database.

    Delete the program defined by the subcommand argument from the
    database.  The program to delete can be input directly, or selected
    from a list of programs by entering the character "?" as program ID
    or including the --interactive option.
    """
    context.execute_cmd(lambda: cmd_programs_delete(context, programid,
                                                    options))


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
        raise click.ClickException('Error, no current program defined')


def cmd_programs_list(context):
    """
    List existing programs
    """
    programs_tbl = ProgramsTable.factory(context.db_info, context.db_type,
                                         context.verbose)

    headers = ProgramsTable.fields
    tbl_rows = []
    # TODO I think I have a std struct function in common to do this
    for program, data in six.iteritems(programs_tbl):
        row = [data[field] for field in headers]
        tbl_rows.append(row)

    context.spinner.stop()
    title = 'Programs Table: %s' % datetime_display_str()
    print_table(tbl_rows, headers, title=title,
                table_format=context.output_format)


def cmd_programs_add(context, options):
    """
    Create a new program in the Programs table. The start date and end date
    are both optional. If not supplied, the startdate is set as the next
    day after the end of the previous program and the end date as 12 months
    minus one day after that
    """
    programs_tbl = ProgramsTable.factory(context.db_info, context.db_type,
                                         context.verbose)
    if options['startdate']:
        start_date = options['startdate']
    else:
        datetimes = [programs_tbl[pgm]['StartDate'] for pgm in programs_tbl]
        start_date = max(datetimes)
        start_date = start_date + relativedelta(months=12)

    if options['enddate']:
        end_date = options['enddate']
    else:
        end_date = start_date + relativedelta(months=12) - timedelta(days=1)

    program_name = options['programname']

    context.spinner.stop()
    click.echo('Adding program "%s", starts "%s", ends "%s"' %
               (program_name, start_date, end_date))

    if validate_prompt('Validate adding this program?'):
        try:
            programs_tbl.insert(program_name, start_date, end_date)
        except Exception as ex:  # pylint: disable=broad-except
            raise click.ClickException('Insert of program=%s, start=%s, '
                                       'end=%s into database failed. '
                                       'Exception %s' %
                                       (program_name, start_date, end_date, ex))
    else:
        click.echo('Operation aborted by user')
        return


def cmd_programs_delete(context, programid, options):
    """Delete a user from the programs database."""

    programs_tbl = ProgramsTable.factory(context.db_info, context.db_type,
                                         context.verbose)

    programid = get_programid(context, programs_tbl, programid, options)
    if programid is None:
        return

    if programid not in programs_tbl:
        raise click.ClickException('The ProgramID %s is not in the table' %
                                   programid)
    program = programs_tbl[programid]
    start = program['StartDate']
    end = program['EndDate']

    tbl_inst = PingsTable.factory(context.db_info, context.db_type,
                                  context.verbose)
    pings = tbl_inst.count_by_daterange(start, end)
    if pings:
        click.echo("program programid: %s has %s pings in history table. "
                   'Use ""smicli history overview"" to see pings count and use '
                   '"smicli history delete to remove them' %
                   (programid, pings))
        # TODO actually ask and remove pings here. easier than forcing user
        # to do it manually

    if not options['no_verify']:
        context.spinner.stop()
        click.echo(programs_tbl[programid])
        if not validate_prompt('Delete program id %s' % programid):
            click.echo('Operation aborted by user')
            return

    try:
        programs_tbl.delete(programid)
    except mysqlerror as ex:
        click.echo("Change failed, Database Error Exception: %s: %s"
                   % (ex.__class__.__name__, ex))
