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

import datetime
import click
from click_datetime import Datetime
import six
from smipyping import SimplePingList, PingsTable, ProgramsTable, UsersTable, \
    datetime_display_str, compute_startend_dates
from smipyping._common import get_list_index, fold_cell
from smipyping._logging import AUDIT_LOGGER_NAME, get_logger

from .smicli import cli, CMD_OPTS_TXT
from ._click_common import print_table, validate_prompt, get_target_id

# default sort order for weekly table is the company row
DEFAULT_WEEKLY_TBL_SORT = 'Company'


@cli.group('history', options_metavar=CMD_OPTS_TXT)
def history_group():
    """
    Command group manages history(pings) table.

    The history command group processes the database pings table.

    The pings table maintains entries with the results of the ``cimping all
    -s`` subcommand.  Each history entry contains the target id, the timestamp
    for the test, and the results of the test.

    It includes commands to clean the pings table and also to create various
    reports and tables of the history of tests on the WBEM servers in the
    targets table that are stored in the Pings table.

    Because the pings table can be very large, there are subcommands to clean
    entries out of the table based on program id, dates, etc.

    Rather than a simple list subcommand this subcommand includes a number of
    reports to view the table for:

      - changes to status for particular targets.
      - Consolidated history over time periods
      - Snapshots of the full set of entries over periods of time.
    """
    pass


# @history_group.command('create', options_metavar=CMD_OPTS_TXT)
# @click.option('-i', '--ids', default=None, type=int,
#              required=False,
#              help="Optional list of ids. If not supplied, all id's are used")
# @click.option('-d', '--datetime', type=Datetime(format='%-M:%-H:%d/%m/%y'),
#              default=datetime.datetime.now(),
#              required=False,
#              help='Timestamp for the ping history. format for input is'
#                   'min:hour:day/month/year. The minute and hour are optional.'
#                   ' Default current datetime')
# @click.pass_obj
# def history_create(context, **options):  # pylint: disable=redefined-builtin
#    """
#    TODO: Delete this or move somewhere in a test catagory.#
#
#    """
#    context.execute_cmd(lambda: cmd_history_create(context, options))


@history_group.command('list', options_metavar=CMD_OPTS_TXT)
@click.option('-s', '--startdate', type=Datetime(format='%d/%m/%y'),
              default=None,
              required=False,
              help='Start date for ping records included. Format is dd/mm/yy'
                   ' where dd and mm are zero padded (ex. 01) and year is'
                   ' without century (ex. 17). Default is oldest record')
@click.option('-e', '--enddate', type=Datetime(format='%d/%m/%y'),
              default=None,
              required=False,
              help='End date for ping records included. Format is dd/mm/yy'
                   ' where dd and dm are zero padded (ex. 01) and year is'
                   ' without century (ex. 17). Default is current datetime')
# TODO make this test for positive int
@click.option('-n', '--numberofdays', type=int,
              required=False,
              help='Alternative to enddate. Number of days to report from'
                   ' startdate. "enddate" ignored if "numberofdays" set')
@click.option('-t', '--targetId', type=str,
              required=False,
              help='Get results only for the defined targetID. If the value '
                   'is "?" a select list is provided to the console to select '
                   'the target WBEM server from the targets table.')
@click.option('-r', 'result', type=click.Choice(['full', 'changes', 'status',
                                                 '%ok', 'count']),
              default='status',
              help='Display history records or status info on records. '
                   '"full" displays all records, "changes" displays records '
                   'that change status, "status"(default) displays '
                   'status summary by target. "%ok" reports '
                   'percentage pings OK by Id and total count.')
#  TODO determine if there is any reason for this
# @click.option('-S', '--summary', is_flag=True, required=False, default=False,
#               help='If set only a summary is generated.')
@click.pass_obj
def history_list(context, **options):  # pylint: disable=redefined-builtin
    """
    List history of pings in database.

    The listing may be filtered a date range with the --startdate, --enddate,
    and --numberofdays options.  It may also be filtered to only show a single
    target WBEM server from the targets table with the `--targetid` option

    The output of this subcommand is determined by the `--result` option which
    provides for:

      * `full` - all records defined by the input parameters

      * `status` - listing records by status (i.e. OK, etc.) and
        count of records for that status

      * `%ok` - listing the percentage of records that have 'OK' status and
        the total number of ping records

      * `count` - count of records within the defined date/time range
    """
    context.execute_cmd(lambda: cmd_history_list(context, options))


@history_group.command('overview', options_metavar=CMD_OPTS_TXT)
@click.pass_obj
def history_overview(context, **options):  # pylint: disable=redefined-builtin
    """
    Get overview of pings in database.

    This subcommand only shows the count of records and the oldest and
    newest record in the pings database, and the number of pings by
    program.
    """
    context.execute_cmd(lambda: cmd_history_overview(context, options))


@history_group.command('delete', options_metavar=CMD_OPTS_TXT)
@click.option('-s', '--startdate', type=Datetime(format='%d/%m/%y'),
              required=True,
              help='Start date for pings to be deleted. Format is dd/mm/yy')
@click.option('-e', '--enddate', type=Datetime(format='%d/%m/%y'),
              required=True,
              help='End date for pings to be deleted. Format is dd/mm/yy')
@click.option('-n', '--numberofdays', type=int,
              required=False,
              help='Alternative to enddate. Number of days to report from'
                   ' startdate. "enddate" ignored if "numberofdays" set')
@click.option('-t', '--TargetID', type=int,
              required=False,
              help='Optional targetID. If included, delete ping records only '
                   'for the defined targetID. Otherwise all ping records in '
                   'the defined time period are deleted.')
@click.pass_obj
def history_delete(context, **options):  # pylint: disable=redefined-builtin
    """
    Delete records from history file.

    Delete records from the history file based on start date and end date
    options and the optional list of target ids provided.

    ex. smicli history delete --startdate 09/09/17 --endate 09/10/17

    Because this could accidently delete all history records, this command
    specifically requires that the user provide both the start date and either
    the enddate or number of days. It makes no assumptions about dates.

    It also requires verification before deleting any records.

    """
    context.execute_cmd(lambda: cmd_history_delete(context, options))


@history_group.command('weekly', options_metavar=CMD_OPTS_TXT)
@click.option('-d', '--date', type=Datetime(format='%d/%m/%y'),
              default=datetime.datetime.today(),
              required=False,
              help='Optional date to be used as basis for report in form '
                   ' dd/mm/yy. Default is today. This option '
                   'allows reports to be generated for previous periods.')
@click.option('-o', '--order', required=False, type=str,
              default=DEFAULT_WEEKLY_TBL_SORT,
              help='Sort order of the columns for the report output.  This '
                   'can be any of the column headers (case independent). '
                   'Default: {}'.format(DEFAULT_WEEKLY_TBL_SORT))
@click.pass_obj
def history_weekly(context, **options):  # pylint: disable=redefined-builtin
    """
    Generate weekly report from ping history.

    This subcommand generates a report on the status of each target id
    in the targets table filtered by the --date parameter. It generates
    a summary of the status for the current day, for the previous week and
    for the total program.

    The --date is optional. Normally the report is generated for the week
    ending at the time the report is generated but the --date pararameter
    allows the report to be generated for previous dates.


    This report includes percentage OK for each
    target for today, this week, and the program and overall information on
    the target (company, product, SMIversion, contacts.)

    """
    context.execute_cmd(lambda: cmd_history_weekly(context, options))


@history_group.command('timeline', options_metavar=CMD_OPTS_TXT)
@click.argument('IDs', type=int, metavar='TargetIDs', required=True, nargs=-1)
@click.option('-s', '--startdate', type=Datetime(format='%d/%m/%y'),
              default=None,
              required=False,
              help='Start date for ping records included. Format is dd/mm/yy '
                   'where dd and mm are zero padded (ex. 01) and year is '
                   'without century (ex. 17). Default is oldest record')
@click.option('-e', '--enddate', type=Datetime(format='%d/%m/%y'),
              default=None,
              required=False,
              help='End date for ping records included. Format is dd/mm/yy '
                   'where dd and dm are zero padded (ex. 01) and year is '
                   'without century (ex. 17). Default  if neither `enddate` or '
                   '`numberofdays` are defined is current datetime')
# TODO make this test for positive int
@click.option('-n', '--numberofdays', type=int,
              required=False,
              help='Alternative to enddate. Number of days to report from'
                   ' startdate. "enddate" ignored if "numberofdays" set')
@click.option('-r', '--result', type=click.Choice(['full', 'status', '%ok']),
              default='status',
              help='"full" displays all records, "status" displays '
                   'status summary by id. "%ok" reports percentage '
                   'pings OK by Id and total count. Default="status". ')
# TODO this is worthless right now
# @click.option('-S', '--summary', is_flag=True, required=False, default=False,
#              help='If set only a summary is generated.')
@click.pass_obj
def history_timeline(context, ids, **options):
    # pylint: disable=redefined-builtin
    """
    Show history of status changes for IDs.

    Generates a report for the defined target IDs and the time period
    defined by the options of the historical status of the defined
    target ID. The --result option defines the report generated with
    options for 1) "full" full list of history records 2) summary
    status by target ID, or 3) "%OK" percentage of records that
    report OK and total records for the period by target ID.

    """
    context.execute_cmd(lambda: cmd_history_timeline(context, ids, options))


######################################################################
#
#    Action functions
#
######################################################################


def cmd_history_weekly(context, options):
    """
    Generate the standard weekly status report. This report generates status
    info on the current day, week, and program.
    """
    pings_tbl = PingsTable.factory(context.db_info, context.db_type,
                                   context.verbose)

    programs_tbl = ProgramsTable.factory(context.db_info, context.db_type,
                                         context.verbose)

    users_tbl = UsersTable.factory(context.db_info, context.db_type,
                                   context.verbose)

    report_date = options['date'] if options['date'] else datetime.date.today()

    try:
        cp = programs_tbl.for_date(report_date)
    except ValueError as ve:
        raise click.ClickException('Error; no program defined %s ' % ve)

    # set start date time to just after midnight for today
    report_date = report_date.replace(minute=0, hour=0, second=0)

    percentok_today = pings_tbl.get_percentok_by_id(report_date)

    week_start = report_date - datetime.timedelta(days=report_date.weekday())

    percentok_week = pings_tbl.get_percentok_by_id(week_start)

    percentok_ytd = pings_tbl.get_percentok_by_id(
        cp['StartDate'],
        end_date=cp['EndDate'])

    # Get last pings information from history (pings) table.
    # TODO the last scan uses current time so the postdated report is really
    # in error. Should be the report_date
    ping_rows = pings_tbl.get_last_timestamped()
    last_status = {ping[1]: ping[3] for ping in ping_rows}
    last_status_time = ping_rows[0][2]

    headers = ['target\nid', 'Uri', 'Company', 'Product', 'SMIVersion',
               'LastScan\nStatus',
               '%\nToday', '%\nWeek', '%\nPgm', 'Contacts']

    report_order = options['order']

    try:
        col_index = get_list_index(headers, report_order)
    except ValueError:
        raise click.ClickException('Error; report_order not valid report '
                                   ' column %s' % report_order)

    tbl_rows = []
    for target_id, value in six.iteritems(percentok_ytd):
        if target_id in context.targets_tbl:
            target = context.targets_tbl[target_id]
            company = target.get('CompanyName', 'empty')
            company = fold_cell(company, 15)
            product = target.get('Product', 'empty')
            product = fold_cell(product, 15)
            url = context.targets_tbl.build_url(target_id)
            smi_version = target.get('SMIVersion', 'empty')
            smi_version = smi_version.replace('/', ', ')
            smi_version = fold_cell(smi_version, 15)
            company_id = target.get('CompanyID', 'empty')
            # get users list
            email_list = users_tbl.get_emails_for_company(company_id)
            emails = "\n".join(email_list) if email_list else 'unassigned'
        else:
            company = u"No target"
            url = u''
            product = u''
            smi_version = u''
            emails = u''

        if target_id in percentok_today:
            today_percent = "%s" % percentok_today[target_id][0]
        else:
            today_percent = 0

        if target_id in percentok_week:
            week_percent = "%s" % percentok_week[target_id][0]
        else:
            week_percent = 0

        if target_id in last_status:
            last_scan_status = last_status[target_id]
            if last_scan_status.startswith('WBEMException'):
                last_scan_status = last_scan_status.split(':', 1)[0]
        else:
            last_scan_status = "Unknown"

        row = [target_id, url, company, product, smi_version,
               fold_cell(last_scan_status, 16),
               today_percent, week_percent, value[0], emails]
        tbl_rows.append(row)

        # sort by the company column
        tbl_rows.sort(key=lambda x: x[col_index])

    context.spinner.stop()

    print_table(tbl_rows, headers,
                title=('Server Status: Report-date=%s '
                       'program=%s start: %s end: '
                       '%s, LastScan: %s' %
                       (datetime_display_str(report_date),
                        cp['ProgramName'],
                        cp['StartDate'],
                        cp['EndDate'],
                        last_status_time)),
                table_format=context.output_format)


def cmd_history_delete(context, options):
    """
        Delete records from the pings table based on start date, end date,
        and optional id.

        This command requires explicit start_date and end_date or number_of_days
        and does not allow making assumptions for these dates.
    """
    targetid = None
    if 'TargetID' in options:
        targetid = options['TargetID']
        targetid = get_target_id(context, targetid, options)

    pings_tbl = PingsTable.factory(context.db_info, context.db_type,
                                   context.verbose)

    before_record_count = pings_tbl.record_count()
    number_of_days = options['numberofdays']
    start_date = options['startdate']
    end_date = options['enddate']

    if number_of_days and end_date:
        raise ValueError('Simultaneous enddate %s and number of days %s '
                         'parameters not allowed' %
                         (end_date, number_of_days))

    if end_date is None and number_of_days is None:
        raise click.ClickException("Either explicit end-date or "
                                   "number-of-days required.")

    if number_of_days:
        end_date = start_date + datetime.timedelta(days=number_of_days)

    if targetid:
        click.echo('Proposed deletions for target_id=%s, startdate: %s, '
                   'end_date: %s' %
                   (targetid, start_date, end_date))
    else:
        click.echo('Proposed deletions for all targets: startdate: %s, '
                   'end_date: %s' % (start_date, end_date))

    # rmv_count = pings_tbl.count_by_daterange(start_date, end_date,
    #                                          target_id=targetid)
    rows = pings_tbl.select_by_daterange(start_date, end_date,
                                         target_id=targetid)
    count = len(rows)
    context.spinner.stop()
    target_display = targetid if targetid else "All Targets"
    if not validate_prompt('Delete %s records %s' % (count, target_display)):
        click.echo('Operation aborted by user.')
        return

    try:
        pings_tbl.delete_by_daterange(
            start_date,
            end_date,
            target_id=targetid)

        click.echo('Delete finished. removed %s records' %
                   (pings_tbl.record_count() - before_record_count))
    except Exception as ex:
        raise click.ClickException("Exception on db update; %s: %s" %
                                   (ex.__class__.__name__, ex))


def cmd_history_overview(context, options):
    """
    Get overall information on the pings table.
    """
    tbl_inst = PingsTable.factory(context.db_info, context.db_type,
                                  context.verbose)
    rows = []

    count = tbl_inst.record_count()
    oldest = tbl_inst.get_oldest_ping()
    newest = tbl_inst.get_newest_ping()
    context.spinner.stop()
    title = "General Information on History (Pings table))"
    headers = ['Attribute', 'Date or pings count']
    rows.append(['Total Records', count])
    rows.append(['Oldest Record', oldest[2]])
    rows.append(['Latest Record', newest[2]])

    programs_tbl = ProgramsTable.factory(context.db_info, context.db_type,
                                         context.verbose)

    for programid in programs_tbl:
        program = programs_tbl[programid]
        start = program['StartDate']
        end = program['EndDate']

        pings = tbl_inst.count_by_daterange(start, end)
        rows.append(["Records %s" % program['ProgramName'], pings])

    print_table(rows, headers,
                title=title,
                table_format=context.output_format)


def cmd_history_create(context, options):
    """
    Create a set of ping records in the database.  This is a test function
    """
    # construct cimping for the complete set of targets
    simple_ping_list = SimplePingList(context.targets_tbl,
                                      target_ids=options['ids'],
                                      logfile=context.log_file,
                                      log_level=context.log_level,
                                      verbose=context.verbose)

    results = simple_ping_list.create_fake_results()

    # put fake results into table
    pings_tbl = PingsTable.factory(context.db_info, context.db_type,
                                   context.verbose)
    timestamp = options['datetime']
    for result in results:
        print('ping data %s %s %s' % (result[0], result[1], timestamp))
        pings_tbl.append(result[0], result[1], timestamp)

    # displayresults of the scan.
    headers = ['id', 'addr', 'result', 'exception', 'time', 'company']
    rows = []
    for result in results:
        target_id = result[0]
        target = context.targets_tbl[target_id]
        test_result = result[1]

        addr = '%s://%s' % (target['Protocol'], target['IPAddress'])
        exception = '%s' % test_result.exception

        rows.append([target_id,
                     addr,
                     ('%s:%s' % (test_result.type, test_result.code)),
                     fold_cell(exception, 12),
                     test_result.execution_time,
                     fold_cell(target['Product'], 12)])
    context.spinner.stop()

    print_table(rows, headers,
                title='FAKE CIMPing Results:',
                table_format=context.output_format)


def get_target_info(context, target_id, ping_record):
    """Get the CompanyName,IP address, and product from the target table and
       return the data as a tuple
       This accounts for possible error in the tables in particular since the
       mysql db is fairly loose and all changes of targets are not accounted
       for in the pings history table.
    """
    if target_id in context.targets_tbl:
        target = context.targets_tbl[target_id]
        company = target.get('CompanyName', 'empty')
        product = target.get('Product', 'empty')
        try:
            url = context.targets_tbl.build_url(target_id)
        except KeyError:
            url = 'empty'
    else:
        audit_logger = get_logger(AUDIT_LOGGER_NAME)
        audit_logger.info('Pings Table invalid TargetID %s ping_record %r',
                          target_id, ping_record)
        company = "No target"
        product = ''
        url = ''
    return (company, url, product)


def cmd_history_list(context, options):
    """
    Show history for the defined start and end dates
    """
    target_id = get_target_id(context, options['targetid'], options,
                              allow_none=True)

    pings_tbl = PingsTable.factory(context.db_info, context.db_type,
                                   context.verbose)
    output_tbl_rows = []
    # if full, show all records in base that match options
    if options['result'] == 'full' or options['result'] == 'changes':
        headers = ['Pingid', 'Id', 'Ip', 'Company', 'Timestamp', 'Status']

        pings = pings_tbl.select_by_daterange(
            options['startdate'],
            end_date=options['enddate'],
            number_of_days=options['numberofdays'],
            target_id=target_id)
        previous_status = None
        for ping in pings:
            target_id = ping[1]
            ping_id = ping[0]
            company, ip, product = get_target_info(context, target_id, ping)

            timestamp = datetime.datetime.strftime(ping[2], '%d/%m/%y:%H:%M:%S')
            status = ping[3]
            if options['result'] == 'changes' and previous_status == status:
                continue
            tbl_row = [ping_id, target_id, ip, company, timestamp, status]
            output_tbl_rows.append(tbl_row)
            previous_status = status

    # if result == status show counts of ping records by status by target
    elif options['result'] == 'status':
        headers = ['id', 'Url', 'company', 'status', 'count']

        results = pings_tbl.get_status_by_id(
            options['startdate'],
            end_date=options['enddate'],
            number_of_days=options['numberofdays'],
            target_id=target_id)
        # find all status and convert to report format
        for target_id, result in six.iteritems(results):
            company, url, product = get_target_info(context, target_id, result)

            for key in result:
                # restrict status output to 20 char.
                status = (key[:20] + '..') if len(key) > 20 else key
                row = [target_id, url, company, status, result[key]]
                output_tbl_rows.append(row)

    # Shows summary records indicating % ok for the period defined
    elif options['result'] == '%ok':
        headers = ['TargetId', 'Url', 'Company', 'Product', '%OK', 'Total']

        percentok_dict = pings_tbl.get_percentok_by_id(
            options['startdate'],
            end_date=options['enddate'],
            number_of_days=options['numberofdays'],
            target_id=target_id)
        # create report of id,  company, product and %ok / total counts
        for target_id, value in six.iteritems(percentok_dict):
            company, ip, product = get_target_info(context, target_id, value)

            row = [target_id, ip, company, product, value[0], value[2]]
            output_tbl_rows.append(row)

    # show count of records for date range
    elif options['result'] == 'count':
        headers = ['TargetID', 'Records', 'Company', 'Url']

        pings = pings_tbl.select_by_daterange(
            options['startdate'],
            end_date=options['enddate'],
            number_of_days=options['numberofdays'],
            target_id=target_id)
        count_tbl = {}
        for ping in pings:
            target_id = ping[1]
            company, ip, product = get_target_info(context, target_id, ping)
            if target_id in count_tbl:
                x = count_tbl[target_id]
                count_tbl[target_id] = (x[0] + 1, x[1], x[2])
            else:
                count_tbl[target_id] = (1, company, ip)

        for target_id, value in six.iteritems(count_tbl):
            row = [target_id, value[0], value[1], value[2]]
            output_tbl_rows.append(row)

    else:
        raise click.ClickException('Invalid result: %s'
                                   % (options['result']))

    context.spinner.stop()
    print_table(output_tbl_rows, headers,
                title=('Ping Status for %s to %s, table_type: %s' %
                       (options['startdate'],
                        options['enddate'],
                        options['result'])),
                table_format=context.output_format)


def cmd_history_timeline(context, ids, options):
    """
    Output a table that shows just the history records that represent changes
    in status for the ids defined
    """

    for id_ in ids:
        try:
            context.targets_tbl.get_target(id_)  # noqa: F841
        except KeyError:
            raise click.ClickException('Invalid Target: target_id=%s not in '
                                       'database %s.' %
                                       (id_, context.targets_tbl))

    pings_tbl = PingsTable.factory(context.db_info, context.db_type,
                                   context.verbose)
    headers = ['Pingid', 'Id', 'Ip', 'Company', 'Timestamp',
               'Status', 'time_diff']
    tbl_rows = []
    for target_id in ids:
        rows = pings_tbl.select_by_daterange(
            options['startdate'],
            end_date=options['enddate'],
            number_of_days=options['numberofdays'],
            target_id=target_id)

        prev_status = None
        prev_pingtime = None
        timediff = None
        for row in rows:
            target_id = row[1]
            ping_id = row[0]
            ping_time = row[2]
            timestamp = datetime.datetime.strftime(ping_time,
                                                   '%d/%m/%y:%H:%M:%S')
            status = row[3]
            if not status == prev_status:
                prev_status = status
                if prev_pingtime:
                    timediff = ping_time - prev_pingtime
                prev_pingtime = ping_time
                if target_id in context.targets_tbl:
                    target = context.targets_tbl[target_id]
                    company = target.get('CompanyName', ' empty')
                    ip = target.get('IPAddress', 'empty')
                else:
                    company = "%s id unknown" % target_id
                    ip = '??'

                status = (status[:20] + '..') if len(status) > 20 else status
                tbl_row = [ping_id, target_id, ip, company, timestamp, status,
                           timediff]
                tbl_rows.append(tbl_row)

    context.spinner.stop()
    start_date, end_date = compute_startend_dates(
        options['startdate'], options['enddate'],
        options['numberofdays'])

    title = ('Ping status timeline for %s to %s; ids %s' %
             (start_date, end_date, ','.join(map(str, ids))))

    print_table(tbl_rows, headers, title,
                table_format=context.output_format)
