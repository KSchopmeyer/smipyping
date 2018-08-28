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
from collections import defaultdict

from mysql.connector import Error as MySQLError

from smipyping import UsersTable, CompaniesTable

from .smicli import cli, CMD_OPTS_TXT
from ._click_common import validate_prompt, print_table, pick_from_list, \
    pick_multiple_from_list, test_db_updates_allowed
from ._common_options import add_options, no_verify_option
from ._cmd_companies import get_companyid


def build_userid_display(userid, user_item):
    """Build and return the string to display for selecting a user.
       Displays info from users table so user can pick the ids.
    """
    return u'   id=%-3s %-20s %-16s %-16s %s' % (userid,
                                                 user_item['CompanyName'],
                                                 user_item['FirstName'],
                                                 user_item['Lastname'],
                                                 user_item['Email'],)


def pick_multiple_user_ids(context, users_tbl, active=None):
    """
    Interactive selection of user ids from list presented on the console.

      Parameters ()
         The click_context which contains user data information.

      Returns:
        userid selected or None if user enter ctrl-C
    """
    if active is None:
        userids = users_tbl.keys()
    else:
        userids = users_tbl.get_active_userids(active)

    display_txt = [build_userid_display(userid, users_tbl[userid],)
                   for userid in userids]
    try:
        indexes = pick_multiple_from_list(context, display_txt,
                                          "Pick TargetIDs:")
    except ValueError:
        pass
    if indexes is None:
        click.echo('Abort command')
        return None
    return [userids[index] for index in indexes]


def get_multiple_user_ids(context, userids, users_tbl, options=None,
                          allow_none=False, active=None):
    """
        Get the users based on the value of userid or the value of the
        interactive option.  If userid is an
        integer, get userid directly and generate exception if this fails.
        If it is ? use the interactive pick_target_id.
        If options exist test for 'interactive' option and if set, call
        pick_target_id
        This function executes the pick function if the userid is "?" or
        if options is not None and the interactive flag is set

        This is a support function for any subcommand requiring the target id

        This support function always tests the target_id to against the
        targets table.

        Parameters:

          context(): Current click context

          userids(list of :term:`string` or list of:term:`integer` or None):
            The userids as a string or integer or the
            string "?" or the value None. If string or int userids are provided
            they are used as the basis for testing against table and returned
            as list of valid integer userids.

          options: The click options.  Used to determine if --interactive mode
            is defined

          allow_none (:class:`py:bool`):
            If True, None is allowed as a value and returned. Otherwise
            None is considered invalid. This is used to separate the cases
            where the user id is an option that may have a None value vs.
            those cases where it is a required parameter.

          active (:class:`py:bool`):
            Boolean used to filter the returned list.

            * If `True`, only userids for active users are returned

            * If `False`, only userids for inactive users are returned.

            * if `None`, all user ids are returned

        Returns:
            Returns integer target_id of a valid targetstbl TargetID

        raises:
          KeyError if target_id not in table and allow_none is False
    """
    if allow_none and userids is None or userids == []:
        return userids
    context.spinner.stop()
    int_user_ids = []
    if options and 'interactive' in options and options['interactive']:
        context.spinner.stop()
        int_user_ids = pick_multiple_user_ids(context, users_tbl)
    elif isinstance(userids, (list, tuple)):
        if len(userids) == 1 and userids[0] == "?":
            context.spinner.stop()
            int_user_ids = pick_multiple_user_ids(context, users_tbl, active)
        else:
            for userid in userids:
                if isinstance(userid, six.integer_types):
                    pass
                elif isinstance(userid, six.string_types):
                    try:
                        userid = int(userid)
                    except ValueError:
                        raise click.ClickException('UserID must be integer. '
                                                   '"%s" cannot be mapped to '
                                                   'integer' % userid)
                else:
                    raise click.ClickException('List of User Ids invalid')
                try:
                    users_tbl[userid]
                except KeyError as ke:
                    raise click.ClickException('User ID %s not in database. '
                                               'Exception: %s: %s' %
                                               (userid,
                                                ke.__class__.__name__, ke))
                int_user_ids.append(userid)

            context.spinner.start()
            return int_user_ids

    if int_user_ids == []:
        click.echo("No users selected.")
    context.spinner.start()
    return int_user_ids


def pick_userid(context, users_tbl):
    """
    Interactive selection of target id from list presented on the console.

      Parameters ()
         The click_context which contains target data information.

      Returns:
        target_id selected or None if user enter ctrl-C
    """
    users_keys = users_tbl.keys()

    display_options = [build_userid_display(key, users_tbl[key])
                       for key in users_keys]
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
        This function executes the pick function if the userid is "?" or
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
@click.option('-f', '--fields', multiple=True, type=str, default=None,
              metavar='FIELDNAME',
              help='Define specific fields for output. UserID always '
                   'included. Multiple fields can be specified by repeating '
                   'the option. (Default: predefined list of fields).'
                   '\nEnter: "-f ?" to interactively select fields for display.'
                   '\nEx. "-f UserID -f CompanyName"')
@click.option('-d', '--disabled', default=False, is_flag=True, required=False,
              help='Show disabled tusers. Otherwise only users that are '
                   'set enabled in the database are shown.'
                   '(Default:Do not show disabled users).')
@click.option('-o', '--order', type=str, default=None, metavar='FIELDNAME',
              help='Sort by the defined field name. Names are viewed with the '
                   'targets fields subcommand or "-o ?" to interactively '
                   'select field for sort')
@click.pass_obj
def users_list(context, **options):  # pylint: disable=redefined-builtin
    """
    List users in the database.
    """
    context.execute_cmd(lambda: cmd_users_list(context, options))


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
@click.argument('UserIDs', type=str, metavar='UserID', required=False, nargs=-1)
@click.option('--active/--inactive', default=False, required=False,
              help='Set the active/inactive state in the database for this '
                   'user. Default is to attempt set user to inactive.')
@click.option('-i', '--interactive', is_flag=True, default=False,
              help='If set, presents list of users from which one can be '
                   'chosen.')
@click.option('-n', '--no-verify', is_flag=True, default=False,
              help='Disable verification prompt before the operation is '
                   'executed.')
@click.pass_obj
def users_activate(context, userids, **options):
    """
    Activate or deactivate multiple users.

    This sets the users defined by the userids argument to either active
    or inactive.  When a user is inactive they are no longer shown in
    tables that involve user information such as the weekly report.

    The users to be activated or deactivated may be specified by a) specific
    user ids, b) the interactive mode option, or c) using '?' as the user id
    argument which also initiates the interactive mode options.

    Each user selected activated separately and users already in the target
    state are bypassed. If the --no-verify option is not set each user to be
    changed causes a verification request before the change.

    Example:
        smicli users ? --activate
    """
    context.execute_cmd(lambda: cmd_users_activate(context, userids, options))


@users_group.command('fields', options_metavar=CMD_OPTS_TXT)
@click.pass_obj
def users_fields(context):
    """
    Display field names in targets database.
    """
    context.execute_cmd(lambda: cmd_users_fields(context))


######################################################################
#
#    Action functions
#
######################################################################

def display_cols(users_tbl, fields, show_disabled=True, order=None,
                 output_format=None):
    """
    Display the columns of data defined by the fields parameter.

    This gets the data from the targets data based on the col_list and prepares
    and displays a table based on those targets_tbl colums.

    Parameters:
      fields: list of strings defining the targets_data columns to be
        displayed.

      target_table: The targets table from the database

      order (:term: `string`): None or name of field upon which the table will
        be sorted for output

      show_disabled(:class:`py:bool`)
        If True, show disabled entries. If not True, entries marked disabled
        are ignored

    """
    if show_disabled:
        user_ids = sorted(users_tbl.keys())
    else:
        user_ids = sorted(users_tbl.get_active_usersids())

    # If order defined check to see if valid field
    if order:
        if order not in users_tbl.all_fields:
            raise click.ClickException("--order option defines invalid field %s"
                                       % order)

        # create dictionary with order value as key and list of targetids as
        # value. List because the order fields are not unique
        order_dict = defaultdict(list)
        for userid in user_ids:
            order_dict[users_tbl[userid][order]].append(userid)
        # order_dict = {target_table[targetid][order]: targetid
        #               for targetid in target_ids}
        # TODO this may be inefficient means to sort by keys and get values
        # into list
        user_ids = []
        for key in sorted(order_dict.keys()):
            user_ids.extend(order_dict[key])

    rows = []
    for userid in user_ids:
        rows.append(users_tbl.format_record(userid, fields))

    headers = users_tbl.tbl_hdr(fields)
    title = 'Users Overview: '
    if show_disabled:
        title = '%s including disabled users' % title

    print_table(rows, headers=headers, title=title,
                table_format=output_format)


STANDARD_FIELDS_DISPLAY_LIST = ['UserID', 'FirstName', 'Lastname', 'Email',
                                'CompanyName', 'Active', 'Notify']


def display_all(users_tbl, fields=None, company=None, order=None,
                show_disabled=True, output_format=None):
    """Display all entries in the base. If fields does not exist,
       display a standard list of fields from the database.
    """
    if not fields:
        # list of default fields for display
        fields = STANDARD_FIELDS_DISPLAY_LIST
    else:
        fields = fields
    display_cols(users_tbl, fields, show_disabled=show_disabled, order=order,
                 output_format=output_format)


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


def cmd_users_fields(context):
    """Display the information fields for the providers dictionary."""
    rows = [[field] for field in UsersTable.all_fields]
    headers = 'User Fields'

    context.spinner.stop()
    print_table(rows, headers, title='User table fields from database and '
                'joins:',
                table_format=context.output_format)


def cmd_users_list(context, options):
    """
    List users from the users table in a flexible format based on the
    options
    """
    fields = list(options['fields'])
    users_tbl = UsersTable.factory(context.db_info, context.db_type,
                                   context.verbose)

    # TODO. For now this is hidden capability.  Need to make public
    # Entering all as first field name causes all fields to be used.
    if fields and fields[0] == 'all':
        fields = users_tbl.all_fields[:]
    # TODO modify all this so we get name field as standard
    headers = UsersTable.all_fields[:]
    tbl_rows = []
    for userid, user in six.iteritems(users_tbl):
        row = [user[field] for field in headers]
        tbl_rows.append(row)

    field_selects = users_tbl.all_fields[:]
    # TODO This is temp since we really want companyname but that
    # is not part of normal fields but from join.
    if 'CompanyID' in field_selects:
        field_selects.remove('CompanyID')
        if 'CompanyName' not in field_selects:
            field_selects.append('CompanyName')
    if fields:
        if fields[0] == "?":
            indexes = pick_multiple_from_list(context, field_selects,
                                              "Select fields to report")
            if not indexes:
                click.echo("Abort cmd, no fields selected")
                return
            fields = [users_tbl.fields[index] for index in indexes]
        if 'UserID' not in fields:
            fields.insert(0, 'UserID')  # always show UserID

    if 'order' in options and options['order'] == "?":
        index = pick_from_list(context, field_selects, "Select field for order")
        order = users_tbl.fields[index]
    else:
        order = options['order']

    for field in fields:
        if field not in users_tbl.all_fields:
            raise click.ClickException("Invalid field name: %s" % field)

    context.spinner.stop()
    try:
        display_all(users_tbl, list(fields),
                    show_disabled=options['disabled'], order=order,
                    company=None, output_format=context.output_format)

    except Exception as ex:
        raise click.ClickException("%s: %s" % (ex.__class__.__name__, ex))


def cmd_users_add(context, options):
    """
    Add a new user to the table.
    """
    test_db_updates_allowed()

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
            click.ClickException("INSERT Error %s: %s" % (ex.__class__.__name__,
                                                          ex))
    else:
        raise click.ClickException('The companyID %s is not a valid companyID '
                                   'in companies table' % companyid)


def cmd_users_delete(context, userid, options):
    """Delete a user from the database."""
    test_db_updates_allowed()

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
    test_db_updates_allowed()

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


def cmd_users_activate(context, userids, options):
    """
        Set the user active flag if change required for the listed users
    """

    users_tbl = UsersTable.factory(context.db_info, context.db_type,
                                   context.verbose)

    userids = get_multiple_user_ids(context, userids, users_tbl, options)
    if userids is None:
        return

    for userid in userids:
        try:
            users_tbl[userid]  # noqa: F841
        except Exception as ex:
            raise click.ClickException('Invalid UserId=%s. Not in database. '
                                       '%s: %s' % (id,
                                                   ex.__class__.__name__, ex))
    context.spinner.stop()
    for userid in userids:
        usr_item = users_tbl[userid]
        is_active = users_tbl.is_active(userid)
        active_flag = options['active']
        if userid in users_tbl:
            if active_flag and is_active:
                click.echo('User %s already active' % userid)
                continue
            elif not active_flag and not is_active:
                click.echo('User %s already inactive' % userid)
                continue
            else:
                if not options['no_verify']:
                    first_name = usr_item['FirstName']
                    last_name = usr_item['Lastname']
                    email = usr_item['Email']
                    companyid = usr_item['CompanyID']
                    company_name = usr_item['CompanyName']
                    click.echo('Setting  %s %s in company=%s(%s), email=%s' %
                               (first_name, last_name, company_name, companyid,
                                email))
                    if validate_prompt('Validate change this user?'):
                        pass
                    else:
                        click.echo('Abort this change')
                        continue
                try:
                    users_tbl.activate(userid, active_flag)
                except MySQLError as ex:
                    click.echo('Activate failed, Database Error Exception: '
                               '%s: %s' % (ex.__class__.__name__, ex))
                    return
                active_flag = users_tbl.is_active(userid)
                click.echo('User %s set %s' % (userid,
                                               users_tbl.is_active_str(userid)))
