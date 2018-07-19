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
from ._click_common import print_table, validate_prompt, get_target_id
from ._common_options import add_options, no_verify_option


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
@click.argument('TargetID', type=str, metavar='TargetID', required=False)
@click.option('-i', '--interactive', is_flag=True, default=False,
              help='If set, presents list of targets to chose.')
@click.pass_obj
def targets_get(context, targetid, **options):
    """
    Display details of single Targets database entry.

    Use the `interactive` option to select the target from a list presented.
    """
    context.execute_cmd(lambda: cmd_targets_get(context, targetid, options))


@targets_group.command('disable', options_metavar=CMD_OPTS_TXT)
@click.argument('TargetID', type=str, metavar='TargetID', required=True)
@click.option('-e', '--enable', is_flag=True, default=False,
              help='Enable the Target if it is disabled.')
@click.option('-i', '--interactive', is_flag=True,
              help='If set, presents list of targets to chose.')
@click.pass_obj
def target_disable(context, targetid, enable, **options):
    """
    Disable a provider from scanning. This changes the database.

    Use the `interactive` option to select the target from a list presented.
    """
    context.execute_cmd(lambda: cmd_target_disable(context, targetid,
                                                   enable, options))


@targets_group.command('modify', options_metavar=CMD_OPTS_TXT)
@click.argument('TargetID', type=str, metavar='TargetID', required=True)
@click.option('-e', '--enable', is_flag=True,
              help='Enable the Target if it is disabled.')
@click.option('-i', '--ipaddress', type=str,
              required=False,
              help='Modify the IP address if this option is included.')
@click.option('-p', '--port', type=str,    # TODO integer only
              required=False,
              help='Modify the port field. If 5988 or 5989, also sets the '
                   'protocol field to https if 5989 or http if 5988')
@click.option('-P', '--principal', type=str,
              required=False,
              help='Modify the Principal field.')
@click.option('-c', '--credential', type=str,
              required=False,
              help='Modify the Credential field.')
@click.option('-R', '--product', type=str,
              required=False,
              help='Modify the the Product field.')
@click.option('-I', '--interopnamespace', type=str,
              required=False,
              help='Modify the InteropNamespace field.')
@add_options(no_verify_option)
@click.pass_obj
def target_modify(context, targetid, enable, **options):
    """
    Modify the fields of an record in the Targets table.

    This changes the database permanently

    Use the `interactive` option to select the target from a list presented.
    """
    context.execute_cmd(lambda: cmd_target_modify(context, targetid, options))

# TODO fields not included in modify.
# CompanyName
# SMIVesion
# ProtocolError
# CompanyID
# CimomVersion
# Namespace
# ScanEnabled
# NotifyUsers
# Notify
# enable


##############################################################
#  targets processing commands
##############################################################

def display_cols(target_table, fields, show_disabled=True, output_format=None):
    """
    Display the columns of data defined by the fields parameter.

    This gets the
    data from the targets data based on the col_list and prepares a table
    based on those targets_tbl colums

    Parameters:
      fields: list of strings defining the targets_data columns to be
        displayed.

      show_disabled(:class:`py:bool`)

    """
    table_data = []

    if show_disabled:
        if 'ScanEnabled' not in fields:
            fields.append('ScanEnabled')

    table_width = target_table.get_output_width(fields) + len(fields)
    fold = False if table_width < 80 else True

    for record_id in sorted(target_table.keys()):
        if show_disabled:
            table_data.append(target_table.format_record(record_id,
                                                         fields,
                                                         fold))
        else:
            if not target_table.disabled_target_id(record_id):
                table_data.append(target_table.format_record(record_id,
                                                             fields,
                                                             fold))
    headers = target_table.tbl_hdr(fields)
    title = 'Target Providers Overview:'
    if show_disabled:
        title = '%s including disabled targets' % title
    print_table(table_data, headers=headers, title=title,
                table_format=output_format)


STANDARD_FIELDS_DISPLAY_LIST = ['TargetID', 'IPAddress', 'Port', 'Protocol',
                                'CompanyName', 'Product', 'CimomVersion']


def display_all(target_table, fields=None, company=None,
                show_disabled=True, output_format=None):
    """Display all entries in the base. If fields does not exist,
       display a standard list of fields from the database.
    """
    if not fields:
        # list of default fields for display
        fields = STANDARD_FIELDS_DISPLAY_LIST
    else:
        fields = fields
    display_cols(target_table, fields, show_disabled=show_disabled,
                 output_format=output_format)


def cmd_target_modify(context, targetid, options):
    """
    Modify the fields of a target.  Any of the field defined by options can
    be modified.
    """
    # get targetid if options are for interactive request and validate that
    # it is valid. Returns None if interactive request is aborted
    targetid = get_target_id(context, targetid, options)
    if targetid is None:
        return

    # create dictionary of changes requested
    changes = {}
    changes['IPAddress'] = options.get('ipaddress', None)
    changes['Port'] = options.get('port', None)
    changes['Principal'] = options.get('principal', None)
    changes['Credentials'] = options.get('credentials', None)
    changes['Product'] = options.get('product', None)

    for key, value in changes.items():
        if value is None:
            del changes[key]
    target_record = context.targets_tbl[targetid]

    if not changes:
        click.echo('No changes requested')
        return

    if 'Port' in changes:
        if changes['Port'] <= 0:
            click.ClickException("Port must be positive integer not %s" %
                                 changes['Port'])
        if changes['Port'] == 5988:
            changes['Protocol'] = 'http'
        elif changes['Port'] == 5989:
            changes['Protocol'] = 'https'

    if options['no_verify']:
        context.targets_tbl.update(targetid, changes)
    else:
        context.spinner.stop()
        click.echo('Proposed changes for id: %s company: %s, product: %s:' %
                   (targetid, target_record[targetid]['Company'],
                    target_record['Product']))
        for key, value in changes.items():
            click.echo('  %s: "%s" to "%s"' % (targetid,
                                               target_record[targetid],
                                               value))
        if validate_prompt('Modify target id %s' % targetid):
            context.targets_tbl.update(targetid, changes)
        else:
            click.echo('Operation aborted by user.')
            return


def cmd_target_disable(context, targetid, enable, options):
    """
        Set the disable flag in a defined targetid
    """
    targetid = get_target_id(context, targetid, options)
    if targetid is None:
        return

    target_record = context.targets_tbl[targetid]
    try:
        # TODO add test to see if already in correct state
        next_state = 'Enabled' if enable else 'Disabled'
        click.echo('Current Status=%s proposed change=%s'
                   % (target_record['ScanEnabled'], next_state))
        if target_record['ScanEnabled'] == next_state:
            click.echo('State already same as proposed change')
            return
        target_record['ScanEnabled'] = False if enable is True else True

        context.targets_tbl.write_updated_record(targetid)

    except Exception as ex:
        raise click.ClickException("%s: %s" % (ex.__class__.__name__, ex))


def cmd_targets_info(context):
    """Display information on the targets config and data file."""
    context.spinner.stop()
    click.echo('\nDB Info:\n  type=%s\n  config_file=%s' %
               (context.targets_tbl.db_type, context.config_file))

    if context.db_info:
        for key in context.db_info:
            click.echo('  %s=%s' % (key, context.db_info[key]))

    else:
        click.echo('context %r' % context)


def cmd_targets_fields(context):
    """Display the information fields for the providers dictionary."""
    fields = context.targets_tbl.get_field_list()
    context.spinner.stop()
    rows = []
    for field in fields:
        rows.append([field])
    headers = 'Table Fields'
    print_table(rows, headers, title='Target table fields',
                table_format=context.output_format)


def cmd_targets_get(context, targetid, options):
    """Display the fields of a single provider record."""

    targetid = get_target_id(context, targetid, options)
    if targetid is None:
        return

    context.spinner.start()
    try:
        target_record = context.targets_tbl.get_target(targetid)

        # TODO: Future need to order output.
        context.spinner.stop()
        for key in target_record:
            click.echo('%s: %s' % (key, target_record[key]))

    except KeyError as ke:
        raise click.ClickException("TargetID %s not in database: %s" %
                                   (targetid, ke))

    except Exception as ex:
        raise click.ClickException("%s: %s" % (ex.__class__.__name__, ex))


def cmd_targets_list(context, options):
    """
    List the smi providers in the database. Allows listing particular
    field names and sorting by field name
    """
    fields = list(options['fields'])

    context.spinner.stop()
    if fields:
        if 'TargetID' not in fields:
            fields.insert(0, 'TargetID')  # always show TargetID

    try:
        context.targets_tbl.test_fieldnames(fields)
    except KeyError as ke:
        raise click.ClickException("%s: Invalid field name: %s" %
                                   (ke.__class__.__name__, ke))

    try:
        display_all(context.targets_tbl, list(fields),
                    show_disabled=options['disabled'],
                    company=None, output_format=context.output_format)

    except Exception as ex:
        raise click.ClickException("%s: %s" % (ex.__class__.__name__, ex))
