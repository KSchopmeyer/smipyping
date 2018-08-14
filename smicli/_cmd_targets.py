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

from collections import defaultdict
import click

from .smicli import cli, CMD_OPTS_TXT
from ._click_common import print_table, validate_prompt, get_target_id, \
    pick_multiple_from_list, pick_from_list
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
              metavar='FIELDNAME',
              help='Define specific fields for output. TargetID always '
                   'included. Multiple fields can be specified by repeating '
                   'the option. (Default: predefined list of fields).'
                   '\nEnter: "-f ?" to interactively select fields for display.'
                   '\nEx. "-f TargetID -f CompanyName"')
# @click.option('-c', '--company', type=str, default=None,
#              help='regex filter to filter selected companies.')
@click.option('-d', '--disabled', default=False, is_flag=True, required=False,
              help='Show disabled targets. Otherwise only targets that are '
                   'set enabled in the database are shown.'
                   '(Default:Do not show disabled targets).')
@click.option('-o', '--order', type=str, default=None, metavar='FIELDNAME',
              help='Sort by the defined field name. Names are viewed with the '
                   'targets fields subcommand or "-o ?" to interactively '
                   'select field for sort')
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
    Display details of single database target.

    Use the `interactive` option or "?" for Target ID to select the target from
    a list presented.
    """
    context.execute_cmd(lambda: cmd_targets_get(context, targetid, options))


@targets_group.command('disable', options_metavar=CMD_OPTS_TXT)
@click.argument('TargetID', type=str, metavar='TargetID', required=True)
@click.option('-e', '--enable', is_flag=True, default=False,
              help='Enable the Target if it is disabled.')
@click.option('-i', '--interactive', is_flag=True, default=False,
              help='If set, presents list of targets to chose.')
@click.pass_obj
def target_disable(context, targetid, enable, **options):
    """
    Disable a provider from scanning. This changes the database.

    Use the `interactive` option  or "?" for target id to select the target
    from a list presented.
    """
    context.execute_cmd(lambda: cmd_target_disable(context, targetid,
                                                   enable, options))


@targets_group.command('modify', options_metavar=CMD_OPTS_TXT)
@click.argument('TargetID', type=str, metavar='TargetID', required=True)
@click.option('-e', '--enable', is_flag=True, default=False,
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
@click.option('-n', '--namespace', type=str,
              required=False,
              help='Modify the namespace field.')
@add_options(no_verify_option)
@click.pass_obj
def target_modify(context, targetid, enable, **options):
    """
    Modify fields target database record.

    This subcommand changes the database permanently. It normally allows the
    user to verify all changes before they are committed to the database. All
    changes to the database are recorded in the audit log.

    Use the `interactive` option or "?" for Target ID to select the target from
    a list presented.

    Not all fields are defined for modification. Today the fields of
    CompanyName, SMIVersion, CimomVersion, ScanEnabled, NotifyUsers
    Notify, and enable cannot be modified with this subcommand.

    TODO: Expand for other fields in the targets table.
    """
    context.execute_cmd(lambda: cmd_target_modify(context, targetid, options))

# TODO fields not included in modify.
# CompanyName
# SMIVersion
# Protocol
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

def display_cols(target_table, fields, show_disabled=True, order=None,
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
        if 'ScanEnabled' not in fields:
            fields.append('ScanEnabled')

    table_width = target_table.get_output_width(fields) + len(fields)
    # TODO. the above is incorrect in that some fields are of indeterminate
    # length.  The definition in targetstable is not correct.
    fold = False if table_width < 80 else True

    if show_disabled:
        target_ids = sorted(target_table.keys())
    else:
        target_ids = sorted(target_table.get_enabled_targetids())

    # If order defined check to see if valid field
    if order:
        if order not in target_table.get_field_list():
            raise click.ClickException("--order option defines invalid field %s"
                                       % order)

        # create dictionary with order value as key and list of targetids as
        # value. List because the order fields are not unique
        order_dict = defaultdict(list)
        for targetid in target_ids:
            order_dict[target_table[targetid][order]].append(targetid)
        # order_dict = {target_table[targetid][order]: targetid
        #               for targetid in target_ids}
        # TODO this may be inefficient means to sort by keys and get values
        # into list
        target_ids = []
        for key in sorted(order_dict.keys()):
            target_ids.extend(order_dict[key])

    rows = []
    for targetid in target_ids:
        rows.append(target_table.format_record(targetid, fields, fold))

    headers = target_table.tbl_hdr(fields)
    title = 'Target Providers Overview: '
    if show_disabled:
        title = '%s including disabled targets' % title

    print_table(rows, headers=headers, title=title,
                table_format=output_format)


STANDARD_FIELDS_DISPLAY_LIST = ['TargetID', 'IPAddress', 'Port', 'Protocol',
                                'CompanyName', 'Product', 'CimomVersion']


def display_all(target_table, fields=None, company=None, order=None,
                show_disabled=True, output_format=None):
    """Display all entries in the base. If fields does not exist,
       display a standard list of fields from the database.
    """
    if not fields:
        # list of default fields for display
        fields = STANDARD_FIELDS_DISPLAY_LIST
    else:
        fields = fields
    display_cols(target_table, fields, show_disabled=show_disabled, order=order,
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
    changes['InteropNamespace'] = options.get('interopnamespace', None)
    changes['Namespace'] = options.get('namespace', None)

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
                   (targetid, target_record['CompanyName'],
                    target_record['Product']))
        for key, value in changes.items():
            click.echo('  %s: "%s" to "%s"' % (targetid,
                                               target_record[key],
                                               value))
        if validate_prompt('Modify target id %s' % targetid):
            context.targets_tbl.update_fields(targetid, changes)
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
    rows = [[field] for field in fields]
    headers = 'Target Fields'

    context.spinner.stop()
    print_table(rows, headers, title='Target table fields from database:',
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
    field_selects = context.targets_tbl.fields
    # TODO This is temp since we really want companyname butthat
    # is not part of normal fields but from join.
    if 'CompanyID' in field_selects:
        field_selects.remove('CompanyID')
        field_selects.append('CompanyName')
    if fields:
        if fields[0] == "?":
            indexes = pick_multiple_from_list(context, field_selects,
                                              "Select fields to report")
            if not indexes:
                click.echo("Abort cmd, no fields selected")
                return
            fields = [context.targets_tbl.fields[index] for index in indexes]

        if 'TargetID' not in fields:
            fields.insert(0, 'TargetID')  # always show TargetID

    if 'order' in options and options['order'] == "?":
        index = pick_from_list(context, field_selects, "Select field for order")
        order = context.targets_tbl.fields[index]
    else:
        order = options['order']

    try:
        context.targets_tbl.test_fieldnames(fields)
    except KeyError as ke:
        raise click.ClickException("%s: Invalid field name: %s" %
                                   (ke.__class__.__name__, ke))
    context.spinner.stop()

    try:
        display_all(context.targets_tbl, list(fields),
                    show_disabled=options['disabled'], order=order,
                    company=None, output_format=context.output_format)

    except Exception as ex:
        raise click.ClickException("%s: %s" % (ex.__class__.__name__, ex))
