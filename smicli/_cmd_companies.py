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

from smipyping import CompaniesTable, TargetsTable, UsersTable
from smipyping._common import build_table_struct
from .smicli import cli, CMD_OPTS_TXT
from ._click_common import print_table, validate_prompt, pick_from_list

# TODO: This could be common code if we separated the build of the
# select text from the basic pick code.


def pick_companyid(context, companies_tbl):
    """
    Interactive selection of company id from list presented on the console.

      Parameters ()
         The companies table.

      Returns:
        company_id selected or None if user enter ctrl-C
    """
    company_keys = companies_tbl.keys()

    display_options = []
    for t in company_keys:
        company_item = companies_tbl[t]
        display_options.append(u'   id=%s, %s' %
                               (t, company_item['CompanyName']))

    try:
        index = pick_from_list(context, display_options, "Pick CompanyID:")
    except ValueError:
        pass
    if index is None:
        click.echo('Abort command')
        return None
    return company_keys[index]


def get_companyid(context, companies_tbl, companyid, options=None):
    """
        Get the company based on the value of companyid or the value of the
        interactive option.  If userid is an
        integer, get targetid directly and generate exception if this fails.
        If it is ? use the interactive pick_target_id.
        If options exist test for 'interactive' option and if set, call
        pick_target_id
        This function executes the pick function if the targetid is "?" or
        if options is not None and the interactive flag is set

        This support function always tests the companyid against the
        targets table.

        Returns:
            Returns integer companyid of a valid targetstbl TargetID

        raises:
          KeyError if user_id not in table
    """
    context.spinner.stop()
    if options and 'interactive' in options and options['interactive']:
        context.spinner.stop()
        companyid = pick_companyid(context, companies_tbl)
    elif isinstance(companyid, six.integer_types):
        try:
            companyid = companies_tbl[companyid]
            context.spinner.start()
            return companyid
        except KeyError as ke:
            raise click.ClickException("CompanyID %s  not valid: exception %s" %
                                       (companyid, ke))
    elif isinstance(companyid, six.string_types):
        if companyid == "?":
            context.spinner.stop()
            companyid = pick_companyid(context, companies_tbl)
        else:
            try:
                companyid = int(companyid)
            except ValueError:
                raise click.ClickException('CompanyID must be integer or "?" '
                                           'not %s' % companyid)
            try:
                companies_tbl[companyid]
                context.spinner.start()
                return companyid
            except KeyError as ke:
                raise click.ClickException("CompanyID %s  not found in Users "
                                           "table: exception %s" %
                                           (companyid, ke))
    else:
        raise click.ClickException('CompanyID %s. Requires CompanyID, ? or '
                                   '--interactive option' % companyid)
    if companyid is None:
        click.echo("Operation aborted by user.")
    context.spinner.start()
    return companyid


@cli.group('companies', options_metavar=CMD_OPTS_TXT)
def companies_group():
    """
    Command group for Companies table.

    Includes commands to view and modify the Companies table in the database.
    """
    pass


@companies_group.command('list', options_metavar=CMD_OPTS_TXT)
@click.pass_obj
def companies_list(context):  # pylint: disable=redefined-builtin
    """
    List Companies in the database.
    """
    context.execute_cmd(lambda: cmd_companies_list(context))


@companies_group.command('new', options_metavar=CMD_OPTS_TXT)
@click.option('-c', '--companyname', type=str,
              required=False,
              help='Company name for company to add to table.')
@click.pass_obj
def companies_new(context, **options):  # pylint: disable=redefined-builtin
    """
    Create a new companyin the user table.

    Creates a new company with the defined parameters.
    """
    context.execute_cmd(lambda: cmd_companies_new(context, options))


@companies_group.command('delete', options_metavar=CMD_OPTS_TXT)
@click.argument('CompanyID', type=str, metavar='CompanyID', required=False,
                nargs=1)
@click.option('-i', '--interactive', is_flag=True, default=False,
              help='If set, presents list of users from which one can be '
                   'chosen.')
@click.option('-n', '--no-verify', is_flag=True, default=False,
              help='Verify the deletion before deleting the user.')
@click.pass_obj
def companies_delete(context, companyid, **options):
    # pylint: disable=redefined-builtin
    """
    Delete a company from the database.

    Delete the company defined by the subcommand argument from the
    database.

    smicli companies delete ?      # does select list to select company
                                     to delete from companies table
    """
    context.execute_cmd(lambda: cmd_companies_delete(context, companyid,
                                                     options))


@companies_group.command('modify', options_metavar=CMD_OPTS_TXT)
@click.argument('CompanyID', type=str, metavar='CompanyID', required=True,
                nargs=1)
@click.option('-c', '--companyname', type=str,
              required=True,
              help='New company name(required).')
@click.option('-i', '--interactive', is_flag=True, default=False,
              help='If set, presents list of users from which one can be '
                   'chosen.')
@click.option('-n', '--no-verify', is_flag=True, default=False,
              help='Disable verification prompt before the modify is executed.')
@click.pass_obj
def companies_modify(context, companyid, **options):
    # pylint: disable=redefined-builtin
    """
    Create fake cimping results in pings database.

    Execute simple cim ping against the list of ids provided for target servers
    in the database defined by each id in the list of ids creates a table
    showing result.

    ex. smicli companies modify 13 -c "NewCompany Name"

    """
    context.execute_cmd(lambda: cmd_companies_modify(context, companyid,
                                                     options))

######################################################################
#
#    Action functions
#
######################################################################


def cmd_companies_list(context):
    """
    List existing Companies in table format
    """
    companies_tbl = CompaniesTable.factory(context.db_info, context.db_type,
                                           context.verbose)

    headers = CompaniesTable.fields
    tbl_rows = build_table_struct(headers, companies_tbl, sort=True)

    context.spinner.stop()
    print_table(tbl_rows, headers, title=('Companies Table'),
                table_format=context.output_format)


def cmd_companies_delete(context, companyid, options):
    """Delete a user from the database."""

    companies_tbl = CompaniesTable.factory(context.db_info, context.db_type,
                                           context.verbose)

    companyid = get_companyid(context, companies_tbl, companyid, options)
    if companyid is None:
        return

    # Validate not a companyID in targets table
    targets_tbl = TargetsTable.factory(context.db_info, context.db_type,
                                       context.verbose)

    # TODO this should all move to smipyping processing, not in cli
    for target in targets_tbl:
        if targets_tbl[target]['CompanyID'] == companyid:
            raise click.ClickException(
                'The CompanyID %s is used in the targets table %s' %
                (companyid, targets_tbl[target]))

    # validate not in users table
    users_tbl = UsersTable.factory(context.db_info, context.db_type,
                                   context.verbose)
    for user in users_tbl:
        if users_tbl[user]['CompanyID'] == companyid:
            raise click.ClickException(
                'The CompanyID %s is used in the users table %s' %
                (companyid, users_tbl[user]))

    if 'no_verify' in options:
        companies_tbl.delete(companyid)
    else:
        company = companies_tbl[companyid]
        context.spinner.stop()
        click.echo(company)
        if validate_prompt('Delete company id %s' % companyid):
            companies_tbl.delete(companyid)
        else:
            click.echo('Operation aborted by user')
            return


def cmd_companies_modify(context, companyid, options):
    """Modify the company name from the database."""

    companies_tbl = CompaniesTable.factory(context.db_info, context.db_type,
                                           context.verbose)

    companyid = get_companyid(context, companies_tbl, companyid, options)
    if companyid is None:
        return

    print('COMPANYID %s' % companyid)

    changes = {}
    changes['CompanyName'] = options.get('companyname', None)

    company_record = companies_tbl[companyid]

    if options['no_verify']:
        companies_tbl.update_fields(companyid, changes)
    else:
        context.spinner.stop()
        click.echo('Proposed changes for id: %s, %s:' %
                   (companyid, company_record['CompanyName']))
        for key, value in changes.items():
            click.echo('  %s: "%s" to "%s"' % (key,
                                               company_record[key],
                                               value))
        if validate_prompt('Modify company id %s' % companyid):
            companies_tbl.update_fields(companyid, changes)
        else:
            click.echo('Operation aborted by user.')
            return


def cmd_companies_new(context, options):
    """
    Add a new company to the table.
    """
    companies_tbl = CompaniesTable.factory(context.db_info, context.db_type,
                                           context.verbose)

    company_name = options['companyname']
    context.spinner.stop()
    click.echo('Adding company "%s""' % company_name)

    if validate_prompt('Validate adding this company?'):
        try:
            companies_tbl.append(company_name)
        except Exception as ex:
            click.ClickException('Append of company=%s, '
                                 'into database failed. Exception %s' %
                                 (company_name, ex))
    else:
        click.echo('Operation aborted by user')
        return
