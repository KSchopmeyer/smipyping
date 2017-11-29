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

import click

from smipyping import CompaniesTable, TargetsTable
from smipyping._common import build_table_struct
from .smicli import cli, CMD_OPTS_TXT
from ._click_common import print_table


@cli.group('notifications', options_metavar=CMD_OPTS_TXT)
def notifications_group():
    """
    Command group for notifications table

    Includes commands to list and modify the Companies table in the database.

    This is largely an inernal table that keeps track of notifications make
    There is nothing to be done except to list notifications made and to
    clean up the table.
    """
    pass

@notifications_group.command('list', options_metavar=CMD_OPTS_TXT)
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
@click.option('-u', '--userId', type=int,
              required=False,
              help='Get results only for the defined userID')
@click.option('-S' '--summary', is_flag=True, required=False, default=False,
              help='If set only a summary is generated.')
@click.pass_obj
@click.pass_obj
def notifications_list(context):  # pylint: disable=redefined-builtin
    """
    List Notifications in the database.

    List notifications for a date range and optionally a company or
    user.
    """
    context.execute_cmd(lambda: cmd_notifications_list(context))

############################################################
#
#  Action functions
#
############################################################

def cmd_notifications_list(context):


    notifications_tbl = NotificationsTable.factory(context.db_info,
                                                    context.db_type,
                                                    context.verbose)

    headers = ['Target\nID', 'IP', 'Company', 'User', 'Time', 'Message']

    report_order = options['order']


    target_id = options['targetid']
    if target_id:
        try:
            context.target_data.get_target(target_id)  # noqa: F841
        except KeyError:
            raise click.ClickException('Invalid Target: target_id=%s not in '
                                       'database %s.' %
                                       (target_id, context.target_data))

    if user_id


    context.spinner.stop()
    print_table(tbl_rows, headers,
                title=('Notification Status for %s to %s' %
                       (options['startdate'],
                        options['enddate'])),
                table_format=context.output_format)




