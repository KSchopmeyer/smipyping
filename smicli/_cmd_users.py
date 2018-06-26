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
from ._click_common import validate_prompt, print_table


@cli.group('users', options_metavar=CMD_OPTS_TXT)
def users_group():
    """
    Command group to handle users table.

    Includes subcommands to list entries in the users table in the
    database and to create, modify, delete specific entries.
    """
    pass


@users_group.command('add', options_metavar=CMD_OPTS_TXT)
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
@click.option('-n', '--no_verify', default=False, is_flag=True,
              help='Disable verification prompt before the change is '
                   'executed.')
@click.pass_obj
def users_add(context, **options):  # pylint: disable=redefined-builtin
    """
    Add a new user in the user table.

    Creates a new user with the defined parameters for the company defined
    by the required parameter companyID.

    Verification that the operation is correct is requested before the change
    is executed unless the `--no-verify' parameter is set.

    """
    context.execute_cmd(lambda: cmd_users_add(context, options))


@users_group.command('list', options_metavar=CMD_OPTS_TXT)
@click.pass_obj
def users_list(context):  # pylint: disable=redefined-builtin
    """
    List users in the database.
    """
    context.execute_cmd(lambda: cmd_users_list(context))


@users_group.command('delete', options_metavar=CMD_OPTS_TXT)
@click.argument('ID', type=int, metavar='UserID', required=True, nargs=1)
@click.option('-n', '--no-verify', is_flag=True, default=False,
              help='Disable verification prompt before the delete is '
                   'executed.')
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
@click.option('-n', '--no-verify', is_flag=True, default=False,
              help='Disable verification prompt before the change is '
                   'executed.')
@click.pass_obj
def users_modify(context, id, **options):  # pylint: disable=redefined-builtin
    """
    Create fake cimping results in pings database.

    Execute simple cim ping against the list of ids provided for target servers
    in the database defined by each id in the list of ids creates a table
    showing result.

    ex. smicli cimping ids 5 8 9

    """
    context.execute_cmd(lambda: cmd_users_modify(context, options))


@users_group.command('activate', options_metavar=CMD_OPTS_TXT)
@click.argument('ID', type=int, metavar='UserID', required=True, nargs=1)
@click.option('--active/--inactive', default=False, required=False,
              help='Set the active/inactive state in the database for this '
              'user. Default is to attempt set user to inactive')
@click.pass_obj
def users_activate(context, id, **options):
    """
    Activate or deactivate a user.

    This sets the user defined by the UserID argument to either active
    or Inactive.  When a user is inactive they are no longer shown in
    tables that involve user information such as the weekly report.
    """
    context.execute_cmd(lambda: cmd_users_activate(context, id, options))


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

    # TODO modify all this so we get name field as standard
    headers = UsersTable.fields
    tbl_rows = []
    for user_id, data in six.iteritems(users_tbl):
        row = [data[field] for field in headers]
        tbl_rows.append(row)

    tbl_rows.sort(key=lambda x: x[0])

    context.spinner.stop()

    print_table(tbl_rows, headers, title=('Users Table'),
                table_format=context.output_format)


def cmd_users_add(context, options):
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

    context.spinner.stop()
    # TODO sept 2017 expand to include active and notify
    if company_id in companies_tbl:
        company = companies_tbl[company_id]['CompanyName']
        # TODO add verify before adding
        click.echo('Adding %s %s in company=%s(%s), email=%s' %
                   (first_name, last_name, company, company_id, email))

        if options['no_verify']:
            users_tbl.insert(first_name, last_name, email, company_id,
                             active=active,
                             notify=notify)
        else:
            if validate_prompt('Validate add this user?'):
                users_tbl.insert(first_name, last_name, email, company_id,
                                 active=active,
                                 notify=notify)
            else:
                click.echo('Aborted Operation')
                return
    else:
        raise click.ClickException('The companyID %s is not a valid companyID '
                                   'in companies table' % company_id)


def cmd_users_delete(context, id, options):
    """Delete a user from the database."""

    users_tbl = UsersTable.factory(context.db_info, context.db_type,
                                   context.verbose)
    user_id = id

    if user_id in users_tbl:
        if options['no_verify']:
            users_tbl.delete(user_id)
        else:
            user = users_tbl[user_id]
            context.spinner.stop()
            click.echo(user)
            if validate_prompt('Delete user id %s' % user_id):
                users_tbl.delete(user_id)
            else:
                click.echo('Abort Operation')
                return

    else:
        raise click.ClickException('The UserID %s is not in the table' %
                                   user_id)


def cmd_users_modify(context, id, options):
    """Delete a user from the database."""

    context.spinner.stop()
    click.echo('Modify not implemented')
    return

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
        Set the user active flag if change required
    """

    users_tbl = UsersTable.factory(context.db_info, context.db_type,
                                   context.verbose)
    user_id = id
    is_active = users_tbl.is_active(user_id)
    active_flag = options['active']
    context.spinner.stop()
    if user_id in users_tbl:
        if active_flag and is_active:
            click.echo('User %s already active' % user_id)
            return
        elif not active_flag and not is_active:
            click.echo('User %s already inactive' % user_id)
            return
        else:
            users_tbl.activate(user_id, active_flag)
            active_flag = users_tbl.is_active(user_id)
            click.echo('User %s set %s' % (user_id,
                                           users_tbl.is_active_str(user_id)))
