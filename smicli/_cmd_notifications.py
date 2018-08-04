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
smicli commands based on python click for examining and cleaning the
notifications table

    __tablename__ = 'Notifications'
    NotifyID = Column(Integer, primary_key=True)
    NotifyTime = Column(DateTime, nullable=False)
    UserID = Column(Integer, ForeignKey("Users.UserID"))
    TargetID = Column(Integer(11), ForeignKey("Targets.TargetID"))
    Message = Column(String(100), nullable=False)


"""
from __future__ import print_function, absolute_import

import datetime
import six
import click
from click_datetime import Datetime

from smipyping import UsersTable, NotificationsTable
from .smicli import cli, CMD_OPTS_TXT
from ._click_common import print_table, validate_prompt, get_target_id


@cli.group('notifications', options_metavar=CMD_OPTS_TXT)
def notifications_group():
    """
    Command group for notifications table.

    Includes commands to list and modify the Companies table in the database.

    This is largely an inernal table that keeps track of notifications make
    There is nothing to be done except to list notifications made and to
    clean up the table.
    """
    pass


@notifications_group.command('list', options_metavar=CMD_OPTS_TXT)
@click.option('-i', '--targetIDs', default=None, type=int,
              multiple=True,
              required=False,
              help='Optional list of ids. If not supplied, all ids are used.')
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
@click.option('-u', '--UserId', type=int,
              required=False,
              help='Get results only for the defined userID')
@click.option('-S' '--summary', is_flag=True, required=False, default=False,
              help='If set only a summary is generated.')
@click.pass_obj
def notifications_list(context, **options):  # pylint: disable=redefined-builtin
    """
    List Notifications in the database.

    List notifications for a date range and optionally a company or
    user.
    """
    context.execute_cmd(lambda: cmd_notifications_list(context, options))


@notifications_group.command('delete', options_metavar=CMD_OPTS_TXT)
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
def notifications_delete(context, **options):
    # pylint: disable=redefined-builtin
    """
    Delete records from notifications file.

    Delete records from the notifications file based on start date and end date
    options and the optional list of target ids provided.

    ex. smicli notifications delete --startdate 09/09/17 --endate 09/10/17

    Because this could accidently delete all history records, this command
    specifically requires that the user provide both the start date and either
    the enddate or number of days. It makes no assumptions about dates.

    It also requires verification before deleting any records.

    """
    context.execute_cmd(lambda: cmd_notifications_delete(context, options))

@notifications_group.command('stats', options_metavar=CMD_OPTS_TXT)
@click.pass_obj
def notifications_stats(context, **options):
    # pylint: disable=redefined-builtin
    """
    Get stats on pings in database.

    This subcommand only shows the count of records and the oldest and
    newest record in the pings database

    TODO we need to grow this output to more statistical information

    """
    context.execute_cmd(lambda: cmd_notifications_stats(context, options))

############################################################
#
#  Action functions
#
############################################################


def cmd_notifications_list(context, options):
    """
        List entries in the notfications table
    """
    notifications_tbl = NotificationsTable.factory(context.db_info,
                                                   context.db_type,
                                                   context.verbose)

    headers = ['Target\nID', 'IP', 'Company', 'User', 'Time', 'Message']

    target_ids = options['targetids']
    user_id = options['userid']

    for target_id in target_ids:
        try:
            context.targets_tbl.get_target(target_id)  # noqa: F841
        except KeyError:
            raise click.ClickException('Invalid Target: target_id=%s not in '
                                       'database %s.' %
                                       (target_id, context.targets_tbl))

    users_tbl = UsersTable.factory(context.db_info, context.db_type,
                                   context.verbose)
    if user_id:
        if user_id not in users_tbl:
            raise click.ClickException('Invalid User id: user_id=%s not in '
                                       'database %s.' %
                                       (user_id, context.user_tbl))

    user_notifications = []
    if user_id:
        for key, notification in six.iteritems(notifications_tbl):
                if notification['UserID'] == user_id:
                    user_notifications.append(key)

    target_notifications = []
    if target_ids:
        for target_id in target_ids:
            for key, notification in six.iteritems(notifications_tbl):
                if notification['TargetID'] == target_id:
                    target_notifications.append(key)

    # TODO: finish the coding of the filters for targets and users

    tbl_rows = []
    for key, notification in six.iteritems(notifications_tbl):
        if notification['UserID'] in users_tbl:
            user = users_tbl[notification['UserID']]
        else:
            user = "Unknown userid %s" % notification['UserID']
        if notification['TargetID'] in context.targets_tbl:
            target = context.targets_tbl[notification['TargetID']]
            row = [notification['TargetID'],
                   target['IPAddress'],
                   target['CompanyName'],
                   user,
                   notification['NotifyTime'],
                   notification['Message']]
        else:
            row = [notification['TargetID'],
                   '%s unknown' % notification['TargetID'],
                   "unknown",
                   user,
                   notification['NotifyTime'],
                   notification['Message']]
        tbl_rows.append(row)

    context.spinner.stop()
    print_table(tbl_rows, headers,
                title=('Notification Status for %s to %s' %
                       (options['startdate'],
                        options['enddate'])),
                table_format=context.output_format)


def cmd_notifications_delete(context, options):
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

    notifications_tbl = NotificationsTable.factory(context.db_info,
                                                   context.db_type,
                                                   context.verbose)
    before_record_count = notifications_tbl.record_count()
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
    rows = notifications_tbl.select_by_daterange(start_date, end_date,
                                                 target_id=targetid)
    count = len(rows)
    context.spinner.stop()
    target_display = targetid if targetid else "All Targets"
    if not validate_prompt('Delete %s records %s' % (count, target_display)):
        click.echo('Operation aborted by user.')
        return

    try:
        notifications_tbl.delete_by_daterange(start_date,
                                              end_date,
                                              target_id=targetid)

        click.echo('Delete finished. removed %s records' %
                   (notifications_tbl.record_count() - before_record_count))
    except Exception as ex:
        raise click.ClickException("Exception on db update; %s: %s" %
                                   (ex.__class__.__name__, ex))

def cmd_notifications_stats(context, options):
    """
    Get overall information on the pings table.
    """
    tbl_inst = NotificationsTable.factory(context.db_info, context.db_type,
                                  context.verbose)
    count = tbl_inst.record_count()
    # oldest = tbl_inst.get_oldest_ping()
    # newest = tbl_inst.get_newest_ping()
    context.spinner.stop()
    # click.echo('Total=%s records\noldest: %s\nnewest: %s' %
    #           (count, oldest, newest))
    click.echo('Total=%s' % (count))
    # TODO expand to show records by year.
