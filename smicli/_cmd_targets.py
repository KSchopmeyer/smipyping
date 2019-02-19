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
import datetime
import click
import prompt_toolkit
from smipyping import datetime_display_str, CompaniesTable
from .smicli import cli, CMD_OPTS_TXT
from ._click_common import print_table, validate_prompt, get_target_id, \
    pick_multiple_from_list, pick_from_list, test_db_updates_allowed
from ._common_options import add_options, no_verify_option
from ._cmd_companies import pick_companyid


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
@click.argument('TargetID', type=str, metavar='TargetID', required=False)
@click.option('-e', '--enable', is_flag=True, default=False,
              help='Enable the Target if it is disabled.')
@click.option('-i', '--interactive', is_flag=True, default=False,
              help='If set, presents list of targets to chose.')
@add_options(no_verify_option)
@click.pass_obj
def targets_disable(context, targetid, enable, **options):
    """
    Disable a provider from scanning. This changes the database.

    Use the `interactive` option  or "?" for target id to select the target
    from a list presented.
    """
    context.execute_cmd(lambda: cmd_targets_disable(context, targetid,
                                                    enable, options))


@targets_group.command('modify', options_metavar=CMD_OPTS_TXT)
@click.argument('TargetID', type=str, metavar='TargetID', required=False)
@click.option('-a', '--all', is_flag=True, default=False,
              help='If set, presents each field with a prompt and requests '
                   'input. Hit enter to bypass or enter new value for each '
                   'field.')
@click.option('--ipaddress', type=str,
              required=False,
              help='Modify the IP address if this option is included.')
@click.option('--protocol', type=click.Choice(['http', 'https']),
              required=False,
              help='Modify the protocol string if this option is included.')
@click.option('--port', type=str,    # TODO integer only
              required=False,
              help='Modify the port field. This should be consistent with the '
                   'protocol field.  Normally port 5988 is http protocol and '
                   '5989 is https')
@click.option('--principal', type=str,
              required=False,
              help='Modify the Principal field.')
@click.option('--credential', type=str,
              required=False,
              help='Modify the Credential field.')
@click.option('--smiversion', type=str,
              required=False,
              help='Modify the the smiversion field.')
@click.option('--product', type=str,
              required=False,
              help='Modify the the Product field.')
@click.option('--interopnamespace', type=str,
              required=False,
              help='Modify the InteropNamespace field with a new interop '
                   'namespace.')
@click.option('--namespace', type=str,
              required=False,
              help='Modify the namespace field with a new namespace.')
@click.option('--cimonversion', type=str,
              required=False,
              help='Modify the cimomversion field with a new namespace.')
@click.option('--companyid', type=int,
              required=False,
              help='Modify the companyID field with the correct ID from the '
                   'Company Table. Entering "?" into this field enables the '
                   'interactive display of companies for selection of the '
                   'company id')
@click.option('--scanenabled', type=click.Choice(['Enabled', 'Disabled']),
              required=False,
              help='Modify the ScanEnabled field if this option is included.')
@click.option('--notifyusers', type=click.Choice(['Enabled', 'Disabled']),
              required=False,
              help='Modify the ScanEnabled field if this option is included.')
@click.option('-i', '--interactive', is_flag=True, default=False,
              help='If set, presents list of targets. Select one. '
                   'Alternatively setting the targetid to "?" presents the '
                   'list of targets for selection.')
@add_options(no_verify_option)
@click.pass_obj
def target_modify(context, targetid, **options):
    """
    Modify fields in a target database record.

    This subcommand changes the database permanently. It allows the
    user to verify all changes before they are committed to the database. All
    changes to the database are recorded in the audit log including both the
    original and new values. Values to be changed are defined by command
    line options.

    Use the `interactive` option or "?" for Target ID to select the target from
    a list presented.

    Not all fields are defined for modification. Today the fields of
    SMIVersion, CimomVersion, NotifyUsers and Notify
    cannot be modified with this subcommand.

    Example:
      smicli targets modify ? --ipaddress 10.2.3.4 --port 5988 --protocol https

    """
    context.execute_cmd(lambda: cmd_target_modify(context, targetid, options))

# TODO fields not included in modify.
# NotifyUsers
# Notify


# TODO set up so user can do a template for new target from existing target
@targets_group.command('new', options_metavar=CMD_OPTS_TXT)
@click.option('--template', type=str,
              required=True,
              help='Target record to use as input data for new target.')
@click.pass_obj
def target_new(context, **options):
    """
    Add a new target data base record.

    This allows the user to define all of the fields in a
    target to add a new target to the table.

    The syntax of the fields is generally validated but please be careful
    since the validation is primitive.

    The new target is permanently added to the target table
    """
    context.execute_cmd(lambda: cmd_target_new(context, options))


@targets_group.command('delete', options_metavar=CMD_OPTS_TXT)
@click.argument('TargetID', type=str, metavar='TargetID', required=False)
@click.option('-n', '--no-verify', is_flag=True, default=False,
              help='Disable verification prompt before the delete is '
                   'executed.')
@click.option('-i', '--interactive', is_flag=True, default=False,
              help='If set, presents list of users from which one can be '
                   'chosen.')
@click.pass_obj
def target_delete(context, targetid, **options):
    """
    Delete a target record from the targets table.

    The selection of the target may be by specific targetid, by entering
    "?" or use of the -i option which presents a select list of targets from
    which one may be selected for deletion

    The new target is permanently deleted from the target table in the
    database.
    """
    context.execute_cmd(lambda: cmd_target_delete(context, targetid, options))


##############################################################
#  targets processing commands
##############################################################


def prompt_for_fields(context, targetid, hints=None):
    """
    Prompt the user for all fields in the table and return a dictionary of
    all of the fields.
    """
    # TODO how do we separate out required and optional.
    # TODO provide for a template input where we get the field from another
    # record
    companies_tbl = CompaniesTable.factory(context.db_info, context.db_type,
                                           context.verbose)
    target_record = context.targets_tbl[targetid]
    changes = {}
    context.spinner.stop()
    click.echo('Enter new value for each field or hit enter to bypass a '
               'field.  CTRL-C aborts the subcommand. Enter "?" to '
               'enable select list for CompanyID')
    for field in context.targets_tbl.fields:
        if field == context.targets_tbl.key_field:
            continue
        try:
            if field == 'CompanyID':
                prompt_field = "%s or ? for select list" % \
                    target_record[field]
            else:
                prompt_field = target_record[field]

            hint = hints[field] if hints else ""
            value = prompt_toolkit.prompt(u'%s"(%s): %s: ' %
                                          (field, hint, prompt_field))
            if field == "CompanyID" and value == "?":
                value = pick_companyid(context, companies_tbl)
        except KeyboardInterrupt:
            raise click.ClickException("Subcommand aborted.")
        if value != "":
            changes[field] = value
    return changes


def cmd_target_new(context, options):
    """
    Create a new target record in the database.  This subcommand asks for
    the value of each field in the record based on the data provided by a
    template record.
    """
    targetid = get_target_id(context, options['template'], options)
    if targetid is None:
        return

    click.echo("Input fields. The value in the prompt is example data from "
               "the template.")
    fields = prompt_for_fields(context, targetid, context.targets_tbl.hints)

    for field in context.targets_tbl.required_fields:
        if field not in fields:
            raise click.ClickException("%s field must be in new target." %
                                       field)

    context.spinner.stop()

    for field, value in fields.items():
        click.echo("  %s: %s" % (field, value))

    if not validate_prompt('Validate insert this record?'):
        click.echo('Aborted Operation')
        return
    try:
        context.targets_tbl.insert(fields)
    except Exception as er:
        raise click.ClickException('Insert failed with Exception %s' % er)


def cmd_target_delete(context, targetid, options):
    """
   Delete the target defined by target id if it exists.
    """

    targetid = get_target_id(context, targetid, options)
    if targetid is None:
        return

    if targetid not in context.targets_tbl:
        raise click.ClickException('The TargetID %s is not in the table' %
                                   targetid)

    if not options['no_verify']:
        context.spinner.stop()
        target_record = context.targets_tbl[targetid]
        click.echo('TargetID: %s company: %s, product: %s:' %
                   (targetid, target_record['CompanyName'],
                    target_record['Product'],))
        if not validate_prompt('Validate delete this targetid?'):
            click.echo('Aborted Operation')
            return

    context.spinner.stop()
    try:
        context.targets_tbl.delete(targetid)
    except Exception as er:
        raise click.ClickException('Delete Failed with Exception %s' % er)


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
    title = 'Target Providers Overview: %s:' % \
            datetime_display_str(datetime.datetime.now())
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


def _verify_and_update(context, targetid, target_record, changes, no_verify):
    """
    Common code to verify the proposed changes and pass them to the
    db update method if user verifies that they are correct.
    """
    if no_verify:
        context.targets_tbl.update(targetid, changes)
    else:
        click.echo('TargetID: %s company: %s, product: %s:' %
                   (targetid, target_record['CompanyName'],
                    target_record['Product'],))
        for key, value in changes.items():
            click.echo('  %s: "%s" to "%s"' % (key, target_record[key],
                                               value))
        if validate_prompt('Modify target id %s' % targetid):
            context.targets_tbl.update_fields(targetid, changes)
        else:
            click.echo('Operation aborted by user.')
            return


def cmd_target_modify(context, targetid, options):
    """
    Modify the fields of a target.  Any of the field defined by options can
    be modified.
    """
    test_db_updates_allowed()
    # get targetid if options are for interactive request and validate that
    # it is valid. Returns None if interactive request is aborted
    targetid = get_target_id(context, targetid, options)
    if targetid is None:
        return

    # If option all, prompts for all fields in the table and takes input
    # for each entry optionally.  The update is created from the the entries
    # where the  user returns data.
    if options['all']:
        changes = prompt_for_fields(context, targetid)

    else:
        companies_tbl = CompaniesTable.factory(context.db_info,
                                               context.db_type,
                                               context.verbose)
        if 'companyid' in options and options['companyid'] == "?":
            companyid = pick_companyid(context, companies_tbl)
            options['CompanyID'] = companyid
        else:
            if companyid not in companies_tbl:
                raise click.ClickException("CompanyID %s invalid" % companyid)

        # Create dictionary of changes requested from input parameters
        changes = {}
        changes['IPAddress'] = options.get('ipaddress', None)
        changes['Port'] = options.get('port', None)
        changes['Principal'] = options.get('principal', None)
        changes['Credentials'] = options.get('credentials', None)
        changes['Product'] = options.get('product', None)
        changes['InteropNamespace'] = options.get('interopnamespace', None)
        changes['Namespace'] = options.get('namespace', None)
        changes['Protocol'] = options.get('protocol', None)
        changes['ScanEnabled'] = options.get('scanenabled', None)
        changes['SmiVersion'] = options.get('smiversion', None)
        changes['CompanyID'] = options.get('companyid', None)

        # delete all values with the default value.
        for key, value in changes.items():
            if value is None:
                del changes[key]
        target_record = context.targets_tbl[targetid]

    context.spinner.stop()

    if not changes:
        click.echo('No changes requested.')
        return

    if 'Port' in changes:
        if changes['Port'] <= 0:
            raise click.ClickException("Port must be positive integer not %s" %
                                       changes['Port'])

    # Abort if any  proposed changes do not change the record.
    for change, change_value in changes.items():
        # Exception if change does not change data
        if target_record[change] == change_value:
            raise click.ClickException("Change %s already set to %s" %
                                       (change, change_value))
    try:
        _verify_and_update(context, targetid, target_record, changes,
                           options['no_verify'])
    except Exception as ex:
        raise click.ClickException("%s: %s" % (ex.__class__.__name__, ex))


def cmd_targets_disable(context, targetid, enable, options):
    """
        Set the disable flag in a defined targetid
    """
    test_db_updates_allowed()
    targetid = get_target_id(context, targetid, options)
    if targetid is None:
        return

    target_record = context.targets_tbl[targetid]

    next_state = 'Enabled' if enable else 'Disabled'
    context.spinner.stop()
    click.echo('Current ScanEnabled Status=%s proposed change=%s'
               % (target_record['ScanEnabled'], next_state))
    if target_record['ScanEnabled'] == next_state:
        click.echo('State already same as proposed change')
        return

    changes = {}
    changes['ScanEnabled'] = next_state
    try:
        _verify_and_update(context, targetid, target_record, changes,
                           options['no_verify'])
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
    # TODO. For now this is hidden capability.  Need to make public
    # Entering all as first field name causes all fields to be used.
    if fields and fields[0] == 'all':
        fields = context.targets_tbl.all_fields

    field_selects = context.targets_tbl.fields
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
