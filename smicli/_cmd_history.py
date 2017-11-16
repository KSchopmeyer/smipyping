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

from smipyping import SimplePingList, PingsTable, ProgramsTable, UsersTable
from .smicli import cli, CMD_OPTS_TXT
from ._click_common import fold_cell, print_table

from smipyping._common import get_list_index

# default sort order for weekly table is the company row
DEFAULT_WEEKLY_TBL_SORT = 'Company'


@cli.group('history', options_metavar=CMD_OPTS_TXT)
def history_group():
    """
    Command group to process the history (pings) table in the
    database.

    Includes commands to clean the table and also to create various reports
    and tables of the history of tests on the WBEM servers in the
    targets table that are stored in the Pings table.

    """
    pass


@history_group.command('create', options_metavar=CMD_OPTS_TXT)
@click.option('-i', '--ids', default=None, type=int,
              required=False,
              help="Optional list of ids. If not supplied, all id's are used")
@click.option('-d', '--datetime', type=Datetime(format='%-M:%-H:%d/%m/%y'),
              default=datetime.datetime.now(),
              required=False,
              help='Timestamp for the ping history. format for input is'
                   'min:hour:day/month/year. The minute and hour are optional. '
                   'Default current datetime')
@click.pass_obj
def history_create(context, **options):  # pylint: disable=redefined-builtin
    """
    TODO: Delete this or move somewhere in a test catagory.

    """
    context.execute_cmd(lambda: cmd_history_create(context, options))


@history_group.command('list', options_metavar=CMD_OPTS_TXT)
# @click.option('-i', '--targetIDs', default=None, type=int,
#              multiple=True,
#              required=False,
#              help='Optional list of ids. If not supplied, all ids are used')
# TODO move to multiple IDs.
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
@click.option('-t', '--targetId', type=int,
              required=False,
              help='Get results only for the defined targetID')
@click.option('-r', 'result', type=click.Choice(['full', 'status', '%ok']),
              default='status',
              help='Display. "full" displays all records, "status" displays '
                   'status summary by id. Default=status. "%ok" reports '
                   'percentage pings OK by Id and total count.')
@click.option('-S' '--summary', is_flag=True, required=False, default=False,
              help='If set only a summary is generated.')
@click.pass_obj
def history_list(context, **options):  # pylint: disable=redefined-builtin
    """
    List history of pings from database

    List pings history from database within a time range.  This allows listing
    full list of pings, status summary or percetage OK responses.

    """
    context.execute_cmd(lambda: cmd_history_list(context, options))


@history_group.command('stats', options_metavar=CMD_OPTS_TXT)
@click.option('-S', '--summary', is_flag=True, required=False, default=False,
              help='If set only a summary is generated.')
@click.pass_obj
def history_stats(context, **options):  # pylint: disable=redefined-builtin
    """
    Get stats on pings in database.

    TODO. This could well be just another option in list.

    """
    context.execute_cmd(lambda: cmd_history_stats(context, options))


@history_group.command('delete', options_metavar=CMD_OPTS_TXT)
@click.option('-s', '--startdate', type=Datetime(format='%d/%m/%y'),
              default=datetime.datetime.now(),
              required=False,
              help='Start date for pings to be deleted. Format is dd/mm/yy')
@click.option('-e', '--enddate', type=Datetime(format='%d/%m/%y'),
              default=datetime.datetime.now(),
              required=False,
              help='End date for pings to be deleted. Format is dd/mm/yy')
@click.option('-t', '--targetID', type=int,
              required=False,
              help='Optional targetID. If included, delete ping records only '
                   'for the defined targetID. Otherwise all ping records in '
                   'the defined time period are deleted.')
@click.pass_obj
def history_delete(context, **options):  # pylint: disable=redefined-builtin
    """
    Delete records from history file.

    Delete records from the history file based on start date and end date
    options

    ex. smicli history delete --startdate 09/09/17 --endate 09/10/17

    """
    context.execute_cmd(lambda: cmd_history_delete(context, options))


@history_group.command('weekly', options_metavar=CMD_OPTS_TXT)
@click.option('-d', '--date', type=Datetime(format='%d/%m/%y'),
              default=datetime.datetime.today(),
              required=False,
              help='Optional date to be used as basis for report in form '
                   ' dd/mm/yy. Default is the today. This option '
                   'allows reports to be generated for previous periods.')
@click.option('-o', '--order', required=False, type=str,
              default=DEFAULT_WEEKLY_TBL_SORT,
              help='Sort order of the columns for the report output.  This '
                   'can be any of the column headers (case independent). '
                    'Default: {}'.format(DEFAULT_WEEKLY_TBL_SORT))
@click.pass_obj
def history_weekly(context, **options):  # pylint: disable=redefined-builtin
    """
    Generate weekly report. This report includes percentage OK for each
    target for today, this week, and the program and overall information on
    the target (company, product, SMIversion, contacts.)

    """
    context.execute_cmd(lambda: cmd_history_weekly(context, options))


@history_group.command('timeline', options_metavar=CMD_OPTS_TXT)
@click.argument('IDs', type=int, metavar='TargetIDs', required=True, nargs=-1)
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
@click.option('-t', '--targetId', type=int,
              required=False,
              help='Get results only for the defined targetID')
@click.option('-r', 'result', type=click.Choice(['full', 'status', '%ok']),
              default='status',
              help='Display. "full" displays all records, "status" displays '
                   'status summary by id. Default=status. "%ok" reports '
                   'percentage pings OK by Id and total count.')
@click.option('-S' '--summary', is_flag=True, required=False, default=False,
              help='If set only a summary is generated.')
@click.pass_obj
def history_timeline(context, ids, **options):
    # pylint: disable=redefined-builtin
    """
    Show history of status changes for IDs

    Show a timeline of the history of status changes for the IDs listed.

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
    print('cmd_history options %s context %s' % (options, context))
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

    percentok_today = pings_tbl.get_percentok_by_id(report_date)

    week_start = report_date - datetime.timedelta(days=report_date.weekday())

    percentok_week = pings_tbl.get_percentok_by_id(
        week_start)

    percentok_ytd = pings_tbl.get_percentok_by_id(
        cp['StartDate'],
        end_date=cp['EndDate'])

    headers = ['target\nid', 'IP', 'Company', 'Product', '%\nToday', '%\nWeek',
               '%\nPgm', 'Contacts']

    report_order = options['order']

    try:
        col_index = get_list_index(headers, report_order)
    except ValueError:
        raise click.ClickException('Error; report_order not valid report '
                                   ' column %s' % report_order)

    tbl_rows = []
    for target_id, value in six.iteritems(percentok_ytd):
        if target_id in context.target_data:
            target = context.target_data[target_id]
            company = target.get('CompanyName', 'empty')
            company = fold_cell(company, 15)
            product = target.get('Product', 'empty')
            product = fold_cell(product, 15)
            ip = target.get('IPAddress', 'empty')
            smi_version = target.get('SMIVersion', 'empty')
            smi_version = fold_cell(smi_version, 15)
            company_id = target.get('CompanyID', 'empty')
            # get users list
            email_list = users_tbl.get_emails_for_company(company_id)

            emails = "\n".join(email_list) if email_list else 'unassigned'
        else:
            company = "No target"
            ip = ''
            product = ''
            smi_version = ''
            emails = ''
        if target_id in percentok_today:
            today_percent = percentok_today[target_id][0]
        else:
            today_percent = 0

        if target_id in percentok_week:
            week_percent = percentok_week[target_id][0]
        else:
            week_percent = 0

        row = [target_id, ip, company, product, today_percent, week_percent,
               value[0], emails]
        tbl_rows.append(row)

        # sort by the company column
        tbl_rows.sort(key=lambda x: x[col_index])

    context.spinner.stop()

    print_table(tbl_rows, headers,
                title=('Server Status: Report-date=%s '
                       'program=%s start: %s end: '
                       '%s' %
                       (report_date,
                        cp['ProgramName'],
                        cp['StartDate'],
                        cp['EndDate'])),
                table_format=context.output_format)


def cmd_history_delete(context, options):
    """
        Delete records from the pings table based on start date, end date,
        and optional id.

    """
    target_id = options['targetid']

    # TODO standard function for target_id valid test
    if target_id:
        try:
            context.target_data.get_target(target_id)  # noqa: F841
        except KeyError:
            raise click.ClickException('Invalid Target: target_id=%s not in '
                                       'database %s.' %
                                       (target_id, context.target_data))

    pings_tbl = PingsTable.factory(context.db_info, context.db_type,
                                   context.verbose)

    record_count = pings_tbl.record_count()

    # TODO Verify that you have correct data

    try:
        pings_tbl.delete_by_daterange(
            options['startdate'],
            end_date=options['enddate'],
            number_of_days=options['numberofdays'],
            target_id=target_id)

        context.spinner.stop()
        click.echo('Delete finished. removed %s records' %
                   (pings_tbl.record_count() - record_count))
    except Exception as ex:
        raise click.ClickException("Exception on db update; %s: %s" %
                                   (ex.__class__.__name__, ex))


def cmd_history_stats(context, options):
    """
    Get overall information on the pings table.
    """
    tbl_inst = PingsTable.factory(context.db_info, context.db_type,
                                  context.verbose)
    count = tbl_inst.record_count()
    oldest = tbl_inst.get_oldest_ping()
    newest = tbl_inst.get_newest_ping()
    context.spinner.stop()
    click.echo('Total=%s records\noldest: %s\nnewest: %s' %
               (count, oldest, newest))
    # TODO add by pgm, etc. options

    # get first and last record.
    # if verbose output, get count by program


def cmd_history_create(context, options):
    """
    Create a set of ping records in the database.  This is a test function
    """
    # construct cimping for the complete set of targets
    simple_ping_list = SimplePingList(context.target_data,
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

    # print results of the scan.
    headers = ['id', 'addr', 'result', 'exception', 'time', 'company']
    rows = []
    for result in results:
        target_id = result[0]
        target = context.target_data[target_id]
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


def cmd_history_list(context, options):
    """
    Show history for the defined start and end dates
    """
    target_id = options['targetid']
    if target_id:
        try:
            context.target_data.get_target(target_id)  # noqa: F841
        except KeyError:
            raise click.ClickException('Invalid Target: target_id=%s not in '
                                       'database %s.' %
                                       (target_id, context.target_data))

    pings_tbl = PingsTable.factory(context.db_info, context.db_type,
                                   context.verbose)
    # if full, show all records in base that match options
    if options['result'] == 'full':
        headers = ['Pingid', 'Id', 'Ip', 'Company', 'Timestamp', 'Status']

        rows = pings_tbl.select_by_daterange(
            options['startdate'],
            end_date=options['enddate'],
            number_of_days=options['numberofdays'],
            target_id=target_id)
        tbl_rows = []
        for row in rows:
            target_id = row[1]
            ping_id = row[0]
            if target_id in context.target_data:
                target = context.target_data[target_id]
                company = target.get('CompanyName', ' empty')
                ip = target.get('IPAddress', 'empty')
            else:
                company = "%s id unknown" % target_id
                ip = '??'
            timestamp = datetime.datetime.strftime(row[2], '%d/%m/%y:%H:%M:%S')
            status = row[3]
            tbl_row = [ping_id, target_id, ip, company, timestamp, status]
            tbl_rows.append(tbl_row)

    # if status show counts of ping records by status
    elif options['result'] == 'status':
        headers = ['id', 'ip', 'company', 'status', 'count']

        results = pings_tbl.get_status_by_id(
            options['startdate'],
            end_date=options['enddate'],
            number_of_days=options['numberofdays'],
            target_id=target_id)
        # find all status and convert to report format
        tbl_rows = []
        for target_id, value in six.iteritems(results):
            if target_id in context.target_data:
                target = context.target_data[target_id]
                company = target.get('CompanyName', ' empty')
                ip = target.get('IPAddress', 'empty')
            else:
                company = "%s id unknown" % target_id
                ip = '??'
            for key in value:
                # restrict status output to 20 char.
                status = (key[:20] + '..') if len(key) > 20 else key
                row = [target_id, ip, company, status, value[key]]
                tbl_rows.append(row)

    elif options['result'] == '%ok':
        headers = ['id', 'ip', 'company', 'product', '%OK', 'total']

        percentok_dict = pings_tbl.get_percentok_by_id(
            options['startdate'],
            end_date=options['enddate'],
            number_of_days=options['numberofdays'],
            target_id=target_id)
        # create report of id,  company, product and %ok / total counts
        tbl_rows = []
        for target_id, value in six.iteritems(percentok_dict):
            if target_id in context.target_data:
                target = context.target_data[target_id]
                company = target.get('CompanyName', 'empty')
                product = target.get('Product', 'empty')
                ip = target.get('IPAddress', 'empty')
            else:
                company = "No target"
                ip = ''
                product = ''
            row = [target_id, ip, company, product, value[0], value[2]]
            tbl_rows.append(row)

    else:
        raise click.ClickException('Invalid result: %s'
                                   % (options['result']))

    context.spinner.stop()
    print_table(tbl_rows, headers,
                title=('Ping Status for %s to %s' %
                       (options['startdate'],
                        options['enddate'])),
                table_format=context.output_format)


def cmd_history_timeline(context, ids, options):
    """
    Output a table that shows just the history records that represent changes
    in status for the ids defined
    """

    for id_ in ids:
        try:
            context.target_data.get_target(id_)  # noqa: F841
        except KeyError:
            raise click.ClickException('Invalid Target: target_id=%s not in '
                                       'database %s.' %
                                       (id_, context.target_data))

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
                if target_id in context.target_data:
                    target = context.target_data[target_id]
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
    start_date, end_date = pings_tbl.compute_dates(
        options['startdate'], options['enddate'],
        options['numberofdays'])

    title = ('Ping status timeline for %s to %s; ids %s' %
             (start_date, end_date, ','.join(map(str, ids))))

    print_table(tbl_rows, headers, title,
                table_format=context.output_format)
