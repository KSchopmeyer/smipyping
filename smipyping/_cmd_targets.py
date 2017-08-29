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
smicli commands based on python click for operations on the smipyping
data file.
"""
from __future__ import print_function, absolute_import

import click

from .smicli import cli, CMD_OPTS_TXT
from ._tableoutput import TableFormatter


@cli.group('targets', options_metavar=CMD_OPTS_TXT)
def targets_group():
    """
    Command group for managing targets data.

    This command group enables operations for viewing and management of
    data on the target providers as defined in a database.

    The targets database defines the providers to be pinged, tested, etc.
    including all information to access the provider and links to other
    data such as company, etc.
    """
    pass


@targets_group.command('list', options_metavar=CMD_OPTS_TXT)
@click.option('-f', '--fields', multiple=True, type=str, default=None,
              help='Define specific fields for output. It always includes '
                   ' TargetID. Ex. -f TargetID -f CompanyName '
                   'Default: a Standard list of fields')
# @click.option('-c', '--company', type=str, default=None,
#              help='regex filter to filter selected companies.')
@click.option('-d', '--disabled', default=False, is_flag=True, required=False,
              help='Show disabled targets. Otherwise only targets that are '
                   'set enabled in the database are shown.'
                   ' ' + '(Default: %s.' % False)
@click.option('-o', '--order', type=str, default=None,
              help='sort by the defined field name. NOT IMPLEMENTED')
# TODO sort by a particular field
@click.pass_obj
def targets_list(context, **options):
    """
    Display the entries in the targets database.
    """
    context.execute_cmd(lambda: cmd_targets_list(context, options))


@targets_group.command('info', options_metavar=CMD_OPTS_TXT)
@click.pass_obj
def targets_info(context):
    """
    Show target database config information
    """
    context.execute_cmd(lambda: cmd_targets_info(context))


@targets_group.command('fields', options_metavar=CMD_OPTS_TXT)
@click.pass_obj
def targets_fields(context):
    """
    Display field names in targets database.
    """
    context.execute_cmd(lambda: cmd_targets_fields(context))


@targets_group.command('get', options_metavar=CMD_OPTS_TXT)
@click.argument('TargetID', type=int, metavar='TargetID', required=True)
@click.pass_obj
def targets_get(context, targetid, **options):
    """
    display details of a single record from Targets database.
    """
    context.execute_cmd(lambda: cmd_targets_get(context, targetid, options))


@targets_group.command('disable', options_metavar=CMD_OPTS_TXT)
@click.argument('TargetID', type=int, metavar='TargetID', required=True)
@click.option('-e', '--enable', is_flag=True,
              help='Enable the Target if it is disabled.')
@click.pass_obj
def targets_disable(context, targetid, enable, **options):
    """
    Disable a provider from scanning. This changes the database.
    """
    context.execute_cmd(lambda: cmd_targets_disable(context, targetid,
                                                    enable, options))


##############################################################
#  targets processing commands
##############################################################


def cmd_targets_disable(context, targetid, enable, options):
    """Display the information fields for the targets dictionary."""

    try:
        target_record = context.target_data.get_target(targetid)

        # TODO add test to see if already in correct state
        next_state = 'Enabled' if enable else 'Disabled'
        click.echo('Current Status=%s proposed change=%s'
                   % (target_record['ScanEnabled'], next_state))
        if target_record['ScanEnabled'] == next_state:
            click.echo('State already same as proposed change')
            return
        return

        if target_record is not None:
            target_record['ScanEnabled'] = False if enable is True else True
            context.provider_data.write_updated_record(targetid)
        else:
            click.echo('Id %s invalid or not in table' % targetid)

    except Exception as ex:
        raise click.ClickException("%s: %s" % (ex.__class__.__name__, ex))


def cmd_targets_info(context):
    """Display information on the targets config and data file."""

    click.echo('\nDB Info:\n  type=%s\n  config_file=%s' %
               (context.target_data.db_type, context.config_file))

    if context.db_info:
        for key in context.db_info:
            click.echo('  %s=%s' % (key, context.db_info[key]))

    else:
        click.echo('context %r' % context)


def cmd_targets_fields(context):
    """Display the information fields for the providers dictionary."""
    fields = context.target_data.get_field_list()
    rows = []
    for field in fields:
        rows.append([field])
    headers = 'Table Fields'
    tbl = TableFormatter(rows, headers, title='Target table fields',
                         table_format=context.output_format)

    click.echo(tbl.build_table())


def cmd_targets_get(context, targetid, options):
    """Display the fields of a single provider record."""

    try:
        target_record = context.target_data.get_target(targetid)

        # TODO need to order output.
        for key in target_record:
            click.echo('%s: %s' % (key, target_record[key]))

    except KeyError as ke:
        click.echo('TargetID %s not in the database.' % targetid)
        raise click.ClickException("%s: %s" % (ke.__class__.__name__, ke))

    except Exception as ex:
        raise click.ClickException("%s: %s" % (ex.__class__.__name__, ex))


def cmd_targets_list(context, options):
    """
    List the smi providers in the database. Allows listing particular
    field names and sorting by field name
    """
    fields = list(options['fields'])

    if fields:
        if 'TargetID' not in fields:
            fields.insert(0, 'TargetID')  # always show TargetID

    try:
        context.target_data.test_fieldnames(fields)
    except KeyError as ke:
        raise click.ClickException("%s: Invalid field name: %s" %
                                   (ke.__class__.__name__, ke))

    try:
        context.target_data.display_all(list(fields),
                                        show_disabled=options['disabled'],
                                        company=None)

    except Exception as ex:
        raise click.ClickException("%s: %s" % (ex.__class__.__name__, ex))
