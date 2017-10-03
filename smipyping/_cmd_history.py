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

from smipyping import SimplePingList, PingsTable
from .smicli import cli, CMD_OPTS_TXT
from ._tableoutput import TableFormatter


@cli.group('history', options_metavar=CMD_OPTS_TXT)
def history_group():
    """
    Command group to process the history (pings) table in the
    database.

    Includes commands to clean the table and also to create various reports
    and tables of the history of tests on the WBEM servers in the
    targets database.

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
                   'min:hour:day/month/year. Default current datetime')
@click.pass_obj
def history_create(context, **options):  # pylint: disable=redefined-builtin
    """
    Create fake cimping results in pings database.

    Execute simple cim ping against the list of ids provided for target servers
    in the database defined by each id in the list of ids creates a table
    showing result.

    ex. smicli cimping ids 5 8 9

    """
    context.execute_cmd(lambda: cmd_history_create(context, options))


@history_group.command('list', options_metavar=CMD_OPTS_TXT)
# @click.option('-i', '--targetIDs', default=None, type=int,
#              multiple=True,
#              required=False,
#              help='Optional list of ids. If not supplied, all ids are used')
# TODO change this to get epoch record for datetime
@click.option('-s', '--startdate', type=Datetime(format='%d/%m/%y'),
              default=None,
              required=False,
              help='Start date for ping records included. Format is %d/%m/%y'
                   ' where %d and %m are zero padded (ex. 01) and year is'
                   ' without century (ex. 17). Default is oldest record')
@click.option('-e', '--enddate', type=Datetime(format='%d/%m/%y'),
              default=None,
              required=False,
              help='End date for ping records included. Format is %d/%m/%y'
                   ' where %d and %m are zero padded (ex. 01) and year is'
                   ' without century (ex. 17). Default is current datetime')
@click.option('-n', '--numberofdays', type=int,
              required=False,
              help='Alternative to enddate. Number of days to report from'
                   ' startdate. enddate ignored if numberofdays set')
@click.option('-t', '--targetId', type=int,
              required=False,
              help='Get results only for the defined targetID')
@click.option('-r', 'result', type=click.Choice(['full', 'status', '%ok']),
              default='status',
              help='Display. Full displays all records, status displays'
                   ' status summary by id. Default=status')
@click.option('-S' '--summary', is_flag=True, required=False, default=False,
              help='If set only a summary is generated.')
@click.pass_obj
def history_list(context, **options):  # pylint: disable=redefined-builtin
    """
    Cimping a list of targets from database.

    Execute simple cim ping against the list of ids provided for target servers
    in the database defined by each id in the list of ids creates a table
    showing result.

    ex. smicli cimping ids 5 8 9

    """
    context.execute_cmd(lambda: cmd_history_list(context, options))


@history_group.command('stats', options_metavar=CMD_OPTS_TXT)
@click.option('-S', '--summary', is_flag=True, required=False, default=False,
              help='If set only a summary is generated.')
@click.pass_obj
def history_stats(context, **options):  # pylint: disable=redefined-builtin
    """
    Cimping a list of targets from database.

    Execute simple cim ping against the list of ids provided for target servers
    in the database defined by each id in the list of ids creates a table
    showing result.

    ex. smicli cimping ids 5 8 9

    """
    context.execute_cmd(lambda: cmd_history_stats(context, options))


@history_group.command('delete', options_metavar=CMD_OPTS_TXT)
# @click.option('-i', '--targetIDs', default=None, type=int,
#              multiple=True,
#              required=False,
#              help='Optional list of ids. If not supplied, all ids are used')
# TODO change this to get epoch record for datetime
@click.option('-s', '--startdate', type=Datetime(format='%d/%m/%y'),
              default=datetime.datetime.now(),
              required=False,
              help='Start date for pings to be deleted. Format is %d/%m/%y')
@click.option('-e', '--enddate', type=Datetime(format='%d/%m/%y'),
              default=datetime.datetime.now(),
              required=False,
              help='End date for pings to be deleted. Format is %d/%m/%y')
@click.option('-t', '--targetID', type=int,
              required=False,
              help='Delete only for the defined targetID')
@click.pass_obj
def history_delete(context, **options):  # pylint: disable=redefined-builtin
    """
    Delete records from history file.

    Delete records from the history file based on start date and end date

    ex. smicli cimping ids 5 8 9

    """
    context.execute_cmd(lambda: cmd_history_delete(context, options))


######################################################################
#
#    Action functions
#
######################################################################

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

    # Verify that you have correct data

    try:
        pings_tbl.delete_by_daterange()
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

    # get first and last record.
    # if verbose output, get count by program


def cmd_history_create(context, options):
    """
    Create a set of ping records in the database.  This is a test function
    """
    print('create options %s' % options)
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
                     TableFormatter.fold_cell(exception, 12),
                     test_result.execution_time,
                     TableFormatter.fold_cell(target['Product'], 12)])
    context.spinner.stop()

    table = TableFormatter(rows, headers,
                           title='FAKE CIMPing Results:',
                           table_format=context.output_format)
    click.echo(table.build_table())


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
        headers = ['pingid', 'id', 'ip', 'company', 'timestamp', 'status']

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
    table = TableFormatter(tbl_rows, headers,
                           title=('Ping Status for %s to %s' %
                                  (options['startdate'],
                                   options['enddate'])),
                           table_format=context.output_format)
    click.echo(table.build_table())
