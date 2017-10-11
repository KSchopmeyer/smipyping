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
from ._common import validate_prompt, pick_from_list


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
@click.option('-c', '--companyID', type=int,
              default=None,
              required=True,
              help='CompanyID for the company attached to this user')
@click.option('--inactive', default=False, is_flag=True,
              help='Set the active/inactive state in the database for this '
              'user. Default is active')
@click.option('--disable', default=False, is_flag=True,
              help='Disable notifications in the database for this '
              'user. Default is enabled')
@click.pass_obj
def users_new(context, **options):  # pylint: disable=redefined-builtin
    """
    Create a new user in the user table.

    Creates a new user with the defined parameters.

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
@click.option('-v', '--verify', is_flag=True, default=False,
              help='Verify the deletion before deleting the user.')
@click.pass_obj
def users_delete(context, id, **options):  # pylint: disable=redefined-builtin
    """
    Delete a program from the database.

    Delete the program defined by the subcommand argument from the
    database.
    """
    context.execute_cmd(lambda: cmd_users_delete(context, id, options))


@users_group.command('modify', options_metavar=CMD_OPTS_TXT)
@click.argument('ID', type=int, metavar='UserID', required=True, nargs=1)
@click.option('-f', '--firstname', type=str,
              required=False,
              help='User first name.')
@click.option('-l', '--lastname', type=str,
              default=None,
              required=False,
              help='User last name')
@click.option('-e', '--email', type=str,
              required=False,
              help='User email address.')
@click.option('-p', '--programID', type=int, default=None, required=False,
              help='CompanyID for the company attached to this user')
@click.option('--inactive', is_flag=True, default=False,
              help='Set the inactive state in the database for this '
              'user if this flag set.')
@click.option('--no_notifications', is_flag=True, default=False,
              help='Disable the notify statein the database for this '
              'user if this flag set.')
@click.option('-v', '--verify', is_flag=True, default=False,
              help='Verify the deletion before modifying the user.')
@click.pass_obj
def users_modify(context, id, **options):  # pylint: disable=redefined-builtin
    """
    Create fake cimping results in pings database.

    Execute simple cim ping against the list of ids provided for target servers
    in the database defined by each id in the list of ids creates a table
    showing result.

    ex. smicli cimping ids 5 8 9

    """
    context.execute_cmd(lambda: cmd_users_new(context, options))


@users_group.command('activate', options_metavar=CMD_OPTS_TXT)
@click.argument('ID', type=int, metavar='UserID', required=True, nargs=1)
@click.option('--activate/deactivate', default=False,
              help='Set the activate/deactivate flag in the database for this '
              'user.')
def users_activate(context, id, **options):
    """
    """
    context.execute_cmd(lambda: cmd_users_activate(context, options))


######################################################################
#
#    Action functions
#
######################################################################


def _test_active(options):
    """
    Test the activate options. This has 3 possible values.
    """
    if options['active']:
        activate = True
    elif options['inactive']:
        activate = False
    else:
        activate = None
    return activate


def _test_notify(options):
    """
    Test the activate options. This has 3 possible values.
    """
    if options['enable']:
        notify = True
    elif options['disable']:
        notify = False
    else:
        notify = None
    return notify


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

    tbl_rows.sort(key=lambda x: x[0])

    context.spinner.stop()
    table = TableFormatter(tbl_rows, headers,
                           title=('Users Table'),
                           table_format=context.output_format)
    click.echo(table.build_table())


def cmd_users_new(context, options):
    """
    Add a new user to the table.
    """
    first_name = options['firstname']
    last_name = options['lastname']
    email = options['email']
    company_id = options['companyid']

    companies_tbl = CompaniesTable.factory(context.db_info, context.db_type,
                                           context.verbose)

    users_tbl = UsersTable.factory(context.db_info, context.db_type,
                                   context.verbose)

    active = not options['inactive']
    notify = not options['disable']

    # TODO sept 2017 expand to include active and notify
    if company_id in companies_tbl:
        users_tbl.insert(first_name, last_name, email, company_id,
                         active=active,
                         notify=notify)
    else:
        raise click.ClickException('The companyID %s is not a valid companyID '
                                   'in companies table' % company_id)


def cmd_users_delete(context, id, options):
    """Delete a user from the database."""

    users_tbl = UsersTable.factory(context.db_info, context.db_type,
                                   context.verbose)
    user_id = id

    if user_id in users_tbl:
        if options['verify']:
            user = users_tbl[user_id]
            click.echo(user)
            context.spinner.stop()
            if validate_prompt():
                users_tbl.delete(user_id)
            else:
                click.echo('Abort Operation')
                return
        else:
            users_tbl.delete(user_id)

    else:
        raise click.ClickException('The UserID %s is not in the table' %
                                   user_id)


def cmd_users_modify(context, id, options):
    """Delete a user from the database."""

    users_tbl = UsersTable.factory(context.db_info, context.db_type,
                                   context.verbose)
    user_id = id

    first_name = options['firstname']
    last_name = options['lastname']
    email = options['email']
    company_id = options['companyid']
    activate = _test_active(options)

    if user_id in users_tbl:
        # TODO validate data
        users_tbl.modify(user_id, first_name, last_name, email, company_id,
                         activate)
    else:
        raise click.ClickException('The UserID %s is not in the table' %
                                   user_id)


def cmd_users_activate(context, id, options):
    """
    """
    # TODO not implemented
    click.echo("Not implemented")
