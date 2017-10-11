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

from smipyping import CompaniesTable
from .smicli import cli, CMD_OPTS_TXT
from ._tableoutput import TableFormatter


@cli.group('companies', options_metavar=CMD_OPTS_TXT)
def companies_group():
    """
    Command group processs the companies table

    Includes commands to list and modify the Companies table in the database
    """
    pass


@companies_group.command('list', options_metavar=CMD_OPTS_TXT)
@click.pass_obj
def users_list(context):  # pylint: disable=redefined-builtin
    """
    List Companies in the database.
    """
    context.execute_cmd(lambda: cmd_companies_list(context))

######################################################################
#
#    Action functions
#
######################################################################


def cmd_companies_list(context):
    """
    List existing Companies
    """
    companies_tbl = CompaniesTable.factory(context.db_info, context.db_type,
                                           context.verbose)

    headers = CompaniesTable.fields
    tbl_rows = []
    for co_id, data in six.iteritems(companies_tbl):
        row = [data[field] for field in headers]
        tbl_rows.append(row)

    tbl_rows.sort(key=lambda x:x[0])

    context.spinner.stop()
    table = TableFormatter(tbl_rows, headers,
                           title=('Companies Table'),
                           table_format=context.output_format)
    click.echo(table.build_table())
