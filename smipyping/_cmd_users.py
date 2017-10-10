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
import six

from smipyping import UsersTable, CompaniesTable
from .smicli import cli, CMD_OPTS_TXT
from ._tableoutput import TableFormatter


@cli.group('users', options_metavar=CMD_OPTS_TXT)
def users_group():
    """
    Command group to process the history (pings) table in the
    database.

    Includes commands to clean the table and also to create various reports
    and tables of the history of tests on the WBEM servers in the
    targets database.

    """
    pass

# TODO make new program automatic extension of last


@users_group.command('new', options_metavar=CMD_OPTS_TXT)
@click.option('-f', '--firstname', type=str,
              required=True,
              help='User first name.')
@click.option('-l', '--lastname', type=str,
              default=None,
              required=True,
              help='User last name')
@click.option('-e', '--email', type=str,
              required=True,
              help='User email address.')
@click.option('-p', '--programID', type=int,
              default=None,
              required=True,
              help='CompanyID for the company attached to this user')
@click.pass_obj
def users_new(context, **options):  # pylint: disable=redefined-builtin
    """
    Create fake cimping results in pings database.

    Execute simple cim ping against the list of ids provided for target servers
    in the database defined by each id in the list of ids creates a table
    showing result.

    ex. smicli cimping ids 5 8 9

    """
    context.execute_cmd(lambda: cmd_users_new(context, options))


@users_group.command('list', options_metavar=CMD_OPTS_TXT)
@click.pass_obj
def users_list(context):  # pylint: disable=redefined-builtin
    """
    List users in the database.
    """
    context.execute_cmd(lambda: cmd_users_list(context))


@users_group.command('delete', options_metavar=CMD_OPTS_TXT)
@click.argument('ID', type=int, metavar='UserID', required=True, nargs=1)
@click.option('-v', '--verify', is_flag=True,
              help='Verify the deletion before deleting the program.')
@click.pass_obj
def users_delete(context, id, options):  # pylint: disable=redefined-builtin
    """
    Delete a program from the database.

    Delete the program defined by the subcommand argument from the
    database.
    """
    context.execute_cmd(lambda: cmd_users_delete(context))


######################################################################
#
#    Action functions
#
######################################################################


def cmd_users_list(context):
    """
    List existing users
    """
    users_tbl = UsersTable.factory(context.db_info, context.db_type,
                                   context.verbose)

    headers = UsersTable.fields
    tbl_rows = []
    for user_id, data in six.iteritems(users_tbl):
        row = [data[field] for field in headers]
        tbl_rows.append(row)

    context.spinner.stop()
    table = TableFormatter(tbl_rows, headers,
                           title=('Users Table'),
                           table_format=context.output_format)
    click.echo(table.build_table())


def cmd_users_new(context, options):
    click.echo('users new NOT IMPLEMENTED')

    first_name = options['firstname']
    last_name = options['lastname']
    email = options['email']
    company_id = options['companyid']

    companies_tbl = CompaniesTable.factory(context.db_info, context.db_type,
                                           context.verbose)
    #if company_id in companies_tbl:
    # TODO finish this


def cmd_users_delete(context, options):
    """Delete a user from the database."""
    click.echo('Users delete NOT IMPLEMENTED')
