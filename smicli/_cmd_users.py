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

from mysql.connector import Error as MySQLError

from smipyping import UsersTable, CompaniesTable
from smipyping._logging import AUDIT_LOGGER_NAME, get_logger

from .smicli import cli, CMD_OPTS_TXT
from ._click_common import validate_prompt, print_table, pick_from_list
from ._common_options import add_options, no_verify_option
from ._cmd_companies import get_companyid


def pick_userid(context, users_tbl):
    """
    Interactive selection of target id from list presented on the console.

      Parameters ()
         The click_context which contains target data information.

      Returns:
        target_id selected or None if user enter ctrl-C
    """
    users_keys = users_tbl.keys()
    display_options = []

    companies_tbl = CompaniesTable.factory(context.db_info, context.db_type,
                                           context.verbose)

    for t in users_keys:
        user_item = users_tbl[t]
        if not user_item['CompanyID'] in companies_tbl:
            # TODO log error
            click.echo('DB ERROR: Company ID %s does not exist' %
                       user_item['CompanyID'])
            audit_logger = get_logger(AUDIT_LOGGER_NAME)
            audit_logger.error('DB Error: UserTable. Company ID %s in userID %s'
                               'does not exist.',
                               user_item['CompanyID'], t)
            # TODO removed because we did not use company name in display
            # company_name = "%s_missing" % user_item['CompanyID']
        # else:
            # company_name = companies_tbl[user_item['CompanyID']]
            # ['CompanyName']
        display_options.append(u'   id=%s, %s %s, %s' %
                               (t, user_item['FirstName'],
                                user_item['Lastname'],
                                user_item['Email']))
    try:
        index = pick_from_list(context, display_options, "Pick UserID:")
    except ValueError:
        pass
    if index is None:
        click.echo('Abort command')
        return None
    return users_keys[index]


def get_userid(context, users_tbl, userid, options=None):
    """
        Get the user based on the value of userid or the value of the
        interactive option.  If userid is an
        integer, it directly and generate exception if this fails.
        If it is ? use the interactive pick_target_id.
        If options exist test for 'interactive' option and if set, call
        pick_target_id
        This function executes the pick function if the targetid is "?" or
        if options is not None and the interactive flag is set

        This support function always tests the userid to against the
        targets table.

        Returns:
            Returns integer user_id of a valid targetstbl TargetID

        raises:
          KeyError if user_id not in table
    """
    context.spinner.stop()
    if options and 'interactive' in options and options['interactive']:
        context.spinner.stop()
        userid = pick_userid(context, users_tbl)
    elif isinstance(userid, six.integer_types):
        try:
            userid = users_tbl[userid]
            context.spinner.start()
            return userid
        except KeyError as ke:
            raise click.ClickException("UserID %s  not valid: exception %s" %
                                       (userid, ke))
    elif isinstance(userid, six.string_types):
        if userid == "?":
            context.spinner.stop()
            userid = pick_userid(context, users_tbl)
        else:
            try:
                userid = int(userid)
            except ValueError:
                raise click.ClickException('UserID must be integer or "?" '
                                           'not %s' % userid)
            try:
                # test if userid in table
                users_tbl[userid]  # pylint: disable=pointless-statement
                context.spinner.start()
                return userid
            except KeyError as ke:
                raise click.ClickException("UserID %s  not found in Users "
                                           "table: exception %s" %
                                           (userid, ke))
    else:
        raise click.ClickException('UserID %s. Requires UserID, ? or '
                                   '--interactive option' % userid)
    if userid is None:
        click.echo("Operation aborted by user.")
    context.spinner.start()
    return userid


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
@click.option('-c', '--companyID', type=str,
              default=None,
              required=True,
              help='CompanyID for the company attached to this user. Enter ? '
                   'to use selection list to get company id')
@click.option('--inactive', default=False, is_flag=True,
              help='Set the active/inactive state in the database for this '
              'user. An inactive user is ignored. Default is active')
@click.option('--disable', default=False, is_flag=True,
              help='Disable notifications in the database for this '
              'user. Default is enabled')
@add_options(no_verify_option)
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
@click.argument('UserID', type=str, metavar='UserID', required=False)
@click.option('-n', '--no-verify', is_flag=True, default=False,
              help='Disable verification prompt before the delete is '
                   'executed.')
@click.option('-i', '--interactive', is_flag=True, default=False,
              help='If set, presents list of users from which one can be '
                   'chosen.')
@click.pass_obj
def users_delete(context, userid, **options):
    """
    Delete a user from the database.

    Delete the program user by the subcommand argument from the
    database.

    The user to be deleted may be specified by a) specific user id, b) the
    interactive mode option, or c) using '?' as the user id argument which also
    initiates the interactive mode options
    """
    context.execute_cmd(lambda: cmd_users_delete(context, userid, options))


@users_group.command('modify', options_metavar=CMD_OPTS_TXT)
@click.argument('UserID', type=str, metavar='UserID', required=False)
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
@click.option('-c', '--CompanyID', type=int, default=None, required=False,
              help='CompanyID for the company attached to this user')
@click.option('--no_notifications', is_flag=True, default=False,
              help='Disable the notify state in the database for this '
              'user if this flag set.')
@click.option('-n', '--no-verify', is_flag=True, default=False,
              help='Disable verification prompt before the change is '
                   'executed.')
@click.option('-i', '--interactive', is_flag=True, default=False,
              help='If set, presents list of users from which one can be '
                   'chosen.')
@click.pass_obj
def users_modify(context, userid, **options):
    """
    Modify fields of a user in the user database.

    This allows modifications of the fields for a particular specified by
    the user id on input.

    The user to be modified may be specified by a) specific user id, b) the
    interactive mode option, or c) using '?' as the user id argument which also
    initiates the interactive mode options

    ex. smicli users modify 9 -n fred
    # changes the first name of the user with user id 9.

    """
    context.execute_cmd(lambda: cmd_users_modify(context, userid, options))


@users_group.command('activate', options_metavar=CMD_OPTS_TXT)
@click.argument('UserID', type=str, metavar='UserID', required=False)
@click.option('--active/--inactive', default=False, required=False,
              help='Set the active/inactive state in the database for this '
                   'user. Default is to attempt set user to inactive.')
@click.option('-i', '--interactive', is_flag=True, default=False,
              help='If set, presents list of users from which one can be '
                   'chosen.')
@click.pass_obj
def users_activate(context, userid, **options):
    """
    Activate or deactivate a user.

    This sets the user defined by the id argument to either active
    or Inactive.  When a user is inactive they are no longer shown in
    tables that involve user information such as the weekly report.

    The user to be activated or deactivated may be specified by a) specific
    user id, b) the interactive mode option, or c) using '?' as the user id
    argument which also initiates the interactive mode options.

    Example:
        smicli users ? --activate
    """
    context.execute_cmd(lambda: cmd_users_activate(context, userid, options))


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
    companyid = options['companyid']

    users_tbl = UsersTable.factory(context.db_info, context.db_type,
                                   context.verbose)
    companies_tbl = CompaniesTable.factory(context.db_info, context.db_type,
                                           context.verbose)

    active = not options['inactive']
    notify = not options['disable']

    if companyid == "?":
        companyid = get_companyid(context, companies_tbl, companyid, None)
        if companyid is None:
            return

    # TODO sept 2017 expand to include active and notify
    if companyid in companies_tbl:
        company = companies_tbl[companyid]['CompanyName']

        if not options['no_verify']:
            context.spinner.stop()
            click.echo('Adding %s %s in company=%s(%s), email=%s' %
                       (first_name, last_name, company, companyid, email))
            if validate_prompt('Validate add this user?'):
                pass
            else:
                click.echo('Aborted Operation')
                return
        try:
            users_tbl.insert(first_name, last_name, email, companyid,
                             active=active,
                             notify=notify)
        except MySQLError as ex:
            click.echo("INSERT Error %s: %s" % (ex.__class__.__name__,
                                                ex))
    else:
        raise click.ClickException('The companyID %s is not a valid companyID '
                                   'in companies table' % companyid)


def cmd_users_delete(context, userid, options):
    """Delete a user from the database."""
    users_tbl = UsersTable.factory(context.db_info, context.db_type,
                                   context.verbose)

    userid = get_userid(context, users_tbl, userid, options)
    if userid is None:
        return

    if userid in users_tbl:
        user = users_tbl[userid]

        if not options['no_verify']:
            context.spinner.stop()
            click.echo('id=%s %s %s; %s' % (userid, user['FirstName'],
                                            user['Lastname'], user['Email']))
            if not validate_prompt('Validate delete this user?'):
                click.echo('Aborted Operation')
                return

        context.spinner.stop()
        try:
            users_tbl.delete(userid)
        except MySQLError as ex:
            click.echo("Change failed, Database Error Exception: %s: %s"
                       % (ex.__class__.__name__, ex))

    else:
        raise click.ClickException('The UserID %s is not in the table' %
                                   userid)


def cmd_users_modify(context, userid, options):
    """Modify selected fields of a user in the database."""

    users_tbl = UsersTable.factory(context.db_info, context.db_type,
                                   context.verbose)

    userid = get_userid(context, users_tbl, userid, options)
    if userid is None:
        return

    changes = {}
    changes['FirstName'] = options.get('firstname', None)
    changes['Lastname'] = options.get('lastname', None)
    changes['Email'] = options.get('email', None)
    changes['CompanyID'] = options.get('companyid', None)

    for key, value in changes.items():
        if value is None:
            del changes[key]

    if not changes:
        click.echo('No changes requested')
        return

    user_record = users_tbl[userid]

    if not options['no_verify']:
        context.spinner.stop()
        click.echo('Proposed changes for id: %s, %s %s, email: %s:' %
                   (userid, user_record['FirstName'],
                    user_record['Lastname'],
                    user_record['Email']))
        for key, value in changes.items():
            click.echo('  %s: "%s" to "%s"' % (key,
                                               user_record[key],
                                               value))
        if not validate_prompt('Modify user id %s' % userid):
            click.echo('Operation aborted by user.')
            return

    context.spinner.stop()
    try:
        users_tbl.update_fields(userid, changes)
    except MySQLError as ex:
        click.echo("Change failed, Database Error Exception: %s: %s"
                   % (ex.__class__.__name__, ex))
        return


def cmd_users_activate(context, userid, options):
    """
        Set the user active flag if change required
    """

    users_tbl = UsersTable.factory(context.db_info, context.db_type,
                                   context.verbose)

    userid = get_userid(context, users_tbl, userid, options)
    if userid is None:
        return

    is_active = users_tbl.is_active(userid)
    active_flag = options['active']
    context.spinner.stop()
    if userid in users_tbl:
        if active_flag and is_active:
            click.echo('User %s already active' % userid)
            return
        elif not active_flag and not is_active:
            click.echo('User %s already inactive' % userid)
            return
        else:
            try:
                users_tbl.activate(userid, active_flag)
            except MySQLError as ex:
                click.echo("Activate failed, Database Error Exception: %s: %s"
                           % (ex.__class__.__name__, ex))
                return
            active_flag = users_tbl.is_active(userid)
            click.echo('User %s set %s' % (userid,
                                           users_tbl.is_active_str(userid)))
