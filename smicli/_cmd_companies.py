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

from smipyping import CompaniesTable, TargetsTable, UsersTable
from smipyping._common import build_table_struct
from .smicli import cli, CMD_OPTS_TXT
from ._click_common import print_table, validate_prompt


@cli.group('companies', options_metavar=CMD_OPTS_TXT)
def companies_group():
    """
    Command group handles companies table.

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
              required=True,
              help='Company name for company to add to table.')
@click.pass_obj
def companies_new(context, **options):  # pylint: disable=redefined-builtin
    """
    Create a new user in the user table.

    Creates a new user with the defined parameters.

    """
    context.execute_cmd(lambda: cmd_companies_new(context, options))


@companies_group.command('delete', options_metavar=CMD_OPTS_TXT)
@click.argument('ID', type=int, metavar='UserID', required=True, nargs=1)
@click.option('-n', '--no-verify', is_flag=True, default=False,
              help='Verify the deletion before deleting the user.')
@click.pass_obj
def companies_delete(context, id, **options):
    # pylint: disable=redefined-builtin
    """
    Delete a program from the database.

    Delete the program defined by the subcommand argument from the
    database.
    """
    context.execute_cmd(lambda: cmd_companies_delete(context, id, options))


@companies_group.command('modify', options_metavar=CMD_OPTS_TXT)
@click.argument('ID', type=int, metavar='UserID', required=True, nargs=1)
@click.option('-c', '--companyname', type=str,
              required=False,
              help='User first name.')
@click.option('-v', '--verify', is_flag=True, default=False,
              help='Verify the modification before modifying the user.')
@click.pass_obj
def companies_modify(context, id, **options):
    # pylint: disable=redefined-builtin
    """
    Create fake cimping results in pings database.

    Execute simple cim ping against the list of ids provided for target servers
    in the database defined by each id in the list of ids creates a table
    showing result.

    ex. smicli cimping ids 5 8 9

    """
    context.execute_cmd(lambda: cmd_companies_new(context, options))

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


def cmd_companies_delete(context, id, options):
    """Delete a user from the database."""

    companies_tbl = CompaniesTable.factory(context.db_info, context.db_type,
                                           context.verbose)
    company_id = id

    if company_id not in companies_tbl:
        raise click.ClickException('The CompanyID %s is not in the companies '
                                   'table' % company_id)

    # Validate not a companyID in targets table
    targets_tbl = TargetsTable.factory(context.db_info, context.db_type,
                                       context.verbose)

    # TODO this should all move to smipyping processing, not in cli
    for target in targets_tbl:
        if targets_tbl[target]['CompanyID'] == company_id:
            raise click.ClickException(
                'The CompanyID %s is used in the targets table %s' %
                (company_id, targets_tbl[target]))

    # validate not in users table
    users_tbl = UsersTable.factory(context.db_info, context.db_type,
                                   context.verbose)
    for user in users_tbl:
        if users_tbl[user]['CompanyID'] == company_id:
            raise click.ClickException(
                'The CompanyID %s is used in the users table %s' %
                (company_id, users_tbl[target]))

    if 'no_verify' in options:
        companies_tbl.delete(company_id)
    else:
        company = companies_tbl[company_id]
        context.spinner.stop()
        click.echo(company)
        if validate_prompt('Delete company id %s' % company_id):
            companies_tbl.delete(company_id)
        else:
            click.echo('Operation aborted by user')
            return


def cmd_company_modify(context, id, options):
    """Modify the company name from the database."""

    companies_tbl = CompaniesTable.factory(context.db_info, context.db_type,
                                           context.verbose)
    company_id = id

    company_name = options['companyname']

    if company_id not in companies_tbl:
        raise click.ClickException('The companyID %s is not a valid companyID '
                                   'in companies table' % company_id)

    if verify_operation(context, 'modify company name', company_name,
                        companies_tbl[company_id]):
        companies_tbl.modify(company_id, company_name)
    else:
        click.echo('Return without executing modification')


def verify_operation(context, action, modification, record):
    """Display the record and issue propmpt
    """
    click.echo('Verify_operation %s to %s\nRECORD: %s' % (action, modification,
                                                          record))
    context.spinner.stop()
    if validate_prompt():
        return True

    click.echo('Aborting Operation')
    return False


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
