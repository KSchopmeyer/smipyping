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
Implementation of the exlorer cmd group.
"""
from __future__ import print_function, absolute_import

import click
from smipyping._explore import Explorer

from smipyping._common import StrList, fold_cell
from smipyping._logging import AUDIT_LOGGER_NAME, get_logger
from .smicli import cli, CMD_OPTS_TXT
from ._click_common import print_table, get_multiple_target_ids, \
    validate_target_ids


@cli.group('explorer', options_metavar=CMD_OPTS_TXT)
def explorer_group():
    """
    Command group to explore providers.

    This group of commands provides the tools for general explore of all
    providers defined in the database.

    The explore queries the providers and generates information on their
    state and status including if active, namespaces, profiles, etc.
    It also normally generates a log of all activity.

    This information is generated by accessing the provider itself.

    These subcommands automatically validates selected data from the server
    against the database and creates an audit log entry for any changes. The
    fields currently tested are:

      * SMIVersion
    """
    pass  # pylint: disable=unnecessary-pass


@explorer_group.command('all', options_metavar=CMD_OPTS_TXT)
@click.option('--ping/--no-ping', default=True,
              help='Ping the the provider as initial step in test. '
                   'Default: ping')
@click.option('--thread/--no-thread', default=True,
              help='Run test multithreaded.  Much faster. This option is only'
                   'here to aid debugging if issues occur with multithread.'
                   'Default: thread')
@click.option('-i', '--include-disabled', is_flag=True, default=False,
              help='Include hosts marked disabled in the targets table.')
@click.option('-d', '--detail', type=click.Choice(['full', 'brief', 'all']),
              default='full',
              help='Generate full or brief (fewer columns) report. Full '
                   'report includes namespaces, SMI_profiles, etc. '
                   '(Default: full).')
@click.pass_obj
def explore_all(context, **options):
    """
    Explore all targets in database.

    Execute the general explore operation on  some or all the providers in the
    database and generate a report on the results.

    This command explores the general characteristics of the server including:

      * Company - From the targets database

      * Product = From the targets database

      * SMI Profiles   - As defined by the server itself

      * Interop Namespace - Ad defined by the server

      * Status - General status (i.e. CIMPing status)

      * Time - Time to execute the tests

    General Server information

    It executes the server requests in parallel mode (multi-threaded) or by
    setting a command line options single thread (if for some reason there is
    an issue with the multithreading)

    It generates a report to the the defined output as a table with the
    formatting defined by the global format option. Default is thread the
    requests speeding up the explore significantly.

    There is an option to ping the server before executing the
    explore simply to speed up the process for servers that are completely
    not available. The default is to ping as the first step.

    ex: smicli explore all

    """
    context.execute_cmd(lambda: cmd_explore_all(context, **options))


@explorer_group.command('ids', options_metavar=CMD_OPTS_TXT)
@click.argument('target-ids', type=str, metavar='TargetIDs', required=True,
                nargs=-1)
@click.option('--ping/--no-ping', default=True,
              help='Ping the the provider as initial step in test. '
                   'Default: ping')
@click.option('--thread/--no-thread', default=True,
              help='Run test multithreaded.  Much faster. '
                   'Default: thread')
@click.option('-d', '--detail', type=click.Choice(['full', 'brief', 'all']),
              default='full',
              help='Generate all or brief (fewer columns) report'
                   '(Default: full).')
@click.pass_obj
def explore_ids(context, target_ids, **options):
    """
    Explore a list of target IDs.

    Execute the explorer on the providers defined by id.  Multiple
    ids may be supplied (ex. id 5 6 7)

    ex: smicli explorer ids 6 7 8
        smicli explorer ids ?

    """
    context.execute_cmd(lambda: cmd_explore_ids(context, target_ids, **options))

######################################################################
#
# Common functions for this group
#
######################################################################


######################################################################
#
#  Action functions
#
######################################################################

def cmd_explore_all(context, **options):
    """Explore all of the providers defined in the current database and
    report results.
    """
    # TODO fix the log_level processing.
    explorer = Explorer('smicli', context.targets_tbl,
                        logfile=context.log_file,
                        log_level=None,
                        verbose=context.verbose,
                        ping=options['ping'],
                        threaded=options['thread'],
                        output_format=context.output_format)

    if options['include_disabled']:
        targets = context.targets_tbl.keys()
    else:
        targets = context.targets_tbl.get_enabled_targetids()

    servers = explorer.explore_servers(targets)

    validate_servers(servers, context.targets_tbl)

    # print results
    # TODO make this part of normal print services
    context.spinner.stop()
    report_server_info(servers, context.targets_tbl, context.output_format,
                       report=options['detail'])


def cmd_explore_ids(context, target_ids, **options):
    """
    Explore the wbem server defined by the Id provided
    """
    target_ids = get_multiple_target_ids(context, target_ids, options)
    if target_ids is None:
        return

    validate_target_ids(context, target_ids)

    explorer = Explorer('smicli', context.targets_tbl,
                        verbose=context.verbose,
                        ping=options['ping'],
                        threaded=options['thread'],
                        logfile=context.log_file,
                        log_level=context.log_level,
                        output_format=context.output_format)

    servers = explorer.explore_servers(target_ids)

    validate_servers(servers, context.targets_tbl)

    context.spinner.stop()
    report_server_info(servers, context.targets_tbl,
                       context.output_format,
                       report=options['detail'])


def validate_servers(servers, targets_tbl):
    """
    Validate the fields in the targetid against the data received from the
    server.  This allows updating the following fields from data received
    from the server:

      * SMIVERSION
      * interop namespace
    """
    # TODO this should be in explorer, not in the cmd_processor.
    for server_tuple in servers:
        server = server_tuple.server
        status = server_tuple.status
        target_id = server_tuple.target_id
        target = targets_tbl.get_target(target_id)
        if server is not None and status == 'OK':
            try:
                svr_profile_list = smi_versions(server_tuple)
            except TypeError:
                # ignore this server.
                continue
            sorted(svr_profile_list)
            target_smi_profiles = target['SMIVersion']
            regex = r'^[0-9.]*$'
            server_smi_profiles = StrList(svr_profile_list, match=regex)
            target_smi_profiles = StrList(target_smi_profiles, match=regex)
            if not server_smi_profiles.equal(target_smi_profiles):
                changes = {"SMIVersion": server_smi_profiles.str_by_sep("/")}
                try:
                    targets_tbl.update_fields(target_id, changes)
                    change_str = ""
                    for key, value in changes.items():
                        change_str += "%s:%s " % (key, value)
                    audit_logger = get_logger(AUDIT_LOGGER_NAME)
                    audit_logger.info('Targets Table TargetID %s, updated '
                                      'fields %s', target_id, change_str)
                    click.echo('Updated targetid=%s updated fields %s' %
                               (target_id, change_str))

                except Exception as ex:
                    raise click.ClickException('Targets DB update failed '
                                               'targetid=%s changes=%r. '
                                               'Exception=%s' %
                                               (target_id, changes, ex))


##############################################################
#
#   Table generation functions
#
############################################################


def report_server_info(servers, targets_tbl, output_format,
                       table_format='table',
                       columns=None, report='full'):
    """ Display a table of info from the server scan
    """

    rows = []
    if report == 'full':
        headers = ['Id', 'Url', 'Company', 'Product', 'Vers',
                   'SMI Profiles', 'Interop_ns', 'Status', 'time']
    elif report == 'all':
        headers = targets_tbl.fields
    else:
        headers = ['Id', 'Url', 'Company', 'Product',
                   'Status', 'time']
    servers.sort(key=lambda tup: int(tup.target_id))
    for server_tuple in servers:
        url = server_tuple.url
        server = server_tuple.server
        status = server_tuple.status
        target_id = server_tuple.target_id
        target = targets_tbl.get_target(target_id)
        version = ''
        interop_ns = ''
        smi_profiles = ''
        if server is not None and status == 'OK':
            version = server.version
            interop_ns = server.interop_ns
            try:
                smi_profile_list = smi_versions(server_tuple)
            except TypeError:
                smi_profile_list = []
            if smi_profile_list is not None:
                sorted(smi_profile_list)
                cell_str = ", ". join(sorted(smi_profile_list))
                smi_profiles = fold_cell(cell_str, 14)

        disp_time = None
        if server_tuple.time <= 60:
            disp_time = "%.2fs" % (round(server_tuple.time, 1))
        else:
            disp_time = "%.2fm" % (server_tuple.time / 60)
        row = []
        if 'Id' in headers:
            row.append(target_id)
        if 'Url' in headers:
            row.append(url)
        if 'Company' in headers:
            row.append(fold_cell(target['CompanyName'], 11),)
        if 'Product' in headers:
            row.append(fold_cell(target['Product'], 8),)
        if 'Vers' in headers:
            row.append(version)
        if 'SMI Profiles' in headers:
            row.append(smi_profiles)
        if 'Interop_ns' in headers:
            row.append(interop_ns)
        if 'Status' in headers:
            row.append(server_tuple.status)
        if 'time' in headers:
            row.append(disp_time)

        rows.append(row)

    print_table(rows, headers=headers,
                title='Server Explorer Report:',
                table_format=output_format)


def smi_versions(server_tuple):
    """
    Get the smi version used by this server from the SNIA profile
    information on the server. Uses pywbem server.get_selected_profiles to get
    the complete list of profiles.

    This code accounts for the issue that some profile instances may be
    incorrectly defined and may generate an error in the process.

    If the SMI-S profile cannot be found in the registered profiles an
    exception is generated (TypeError)

    Parameters:
      server_tuple (named tuple ServerInfoTuple):
        Named tuple that defines the target id and server object. The
        server object is used to get the profiles from the server

    Returns:
      List of the property RegisteredVersion for all profiles that are
      registered org 'SNIA' and registered name 'SMI-S.

      If there is an exception, it returns an empty string.

    Raises:
      TypeError: if get_selected_profiles returns TypeError exception


    """
    server = server_tuple.server
    try:
        snia_server_profiles = server.get_selected_profiles(
            registered_org='SNIA', registered_name='SMI-S')
    except TypeError as te:
        audit_logger = get_logger(AUDIT_LOGGER_NAME)
        audit_logger.error('Invalid profile definition caused exception '
                           'for targetid=%s, url=%s. exception %s: %s',
                           server_tuple.target_id,
                           server.conn.url, te.__class__.__name__, te)
        click.echo('ERROR: Invalid profile definition caused exception for '
                   'targetid=%s url=%s. '
                   'exception: %s: %s' % (server_tuple.target_id,
                                          server.conn.url,
                                          te.__class__.__name__, te))
        raise te

    versions = [inst['RegisteredVersion'] for inst in snia_server_profiles]

    return versions


def print_smi_profile_info(servers, user_data, table_format):
    """
    Generates a table of smi profile information listing the smi profiles

    Parameters:

      servers: list of ServerInfoTuple entries
    """

    table_data = []
    table_hdr = [' Id', 'Url', 'Company', 'Product', 'SMI Profiles']
    table_data.append(table_hdr)
    for server_tuple in servers:
        if server_tuple.status == 'OK':
            target_id = server_tuple.target_id
            target = user_data.get_target(target_id)
            try:
                versions = smi_versions(server_tuple.server)
            # Uses very broad exception because smi_versions can generate
            # some strange errors because of bad definitions in the server.
            except Exception as ex:  # pylint: disable=broad-except
                audit_logger = get_logger(AUDIT_LOGGER_NAME)
                audit_logger.error('Exception %s in smi_version %s. Ignored',
                                   ex, server_tuple)
                versions = []

            line = [target['TargetID'],
                    server_tuple.url,
                    target['CompanyName'],
                    target['Product']]
            if versions is not None:
                cell_str = ", ". join(sorted(versions))
                line.append(fold_cell(cell_str, 14))
            table_data.append(line)

    print_table(table_data, headers=table_hdr,
                title='Display SMI Profile Information',
                table_format=table_format)
