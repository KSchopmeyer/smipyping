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

import sys
import datetime
import click
from pywbem import CIMError

from smipyping import PingsTable
from smipyping import SimplePing, SimplePingList, fold_cell, \
    datetime_display_str
from smipyping.config import DEFAULT_NAMESPACE, DEFAULT_OPERATION_TIMEOUT, \
    DEFAULT_USERNAME, DEFAULT_PASSWORD
from smipyping._logging import AUDIT_LOGGER_NAME, get_logger

from .smicli import cli, CMD_OPTS_TXT
from ._common_options import add_options
from ._click_common import print_table, get_target_id, get_multiple_target_ids

#
#   Common options for the Ping group
#
timeout_option = [            # pylint: disable=invalid-name
    click.option('-t', '--timeout', type=int,
                 default=DEFAULT_OPERATION_TIMEOUT,
                 help='Timeout in sec for the pywbem operations to test the '
                      'server.'
                      ' ' + '(Default: %s).' % DEFAULT_OPERATION_TIMEOUT)]

no_ping_option = [            # pylint: disable=invalid-name
    click.option('--no-ping', default=False, is_flag=True, required=False,
                 help='If set this option disables network level ping of the '
                      'wbem server before executing the cim request. Since '
                      'executing the ping does not cause significant time '
                      'delay and helps define servers that are not responding'
                      'at all, normally it should not be set. The ping uses '
                      'available ping program to execute the ping.')]

debug_option = [            # pylint: disable=invalid-name
    click.option('-d', '--debug', default=False, is_flag=True, required=False,
                 help='If set this options sets the debug parameter for the '
                      'pywbem call. Displays detailed information on the call '
                      'and response.')]

thread_option = [            # pylint: disable=invalid-name
    click.option('--no-thread', default=False, is_flag=True, required=False,
                 help='If set run test single-threaded if no-thread set. '
                      'This option exists to aid debugging if issues occur '
                      'with multithreading or the servers responses in '
                      'general. If not set, the requests to each server are '
                      'issued in parallel using multi-threading.')]


@cli.group('cimping', options_metavar=CMD_OPTS_TXT)
def cimping_group():
    """
    Command group to do cimping.

    A cimping executes a system level ping (optional) and then tries to create
    a connection to the target WBEM serve and execute a simple WBEM operation.

    This generally tests both the existence of the WBEM server with the ping
    and the a ability to make a WBEM connection and get valid results from
    the WBEM server. The operation executed is EnumerateClasses on one
    of the known namespaces

    This allows target WBEM servers to be defined in a number of
    ways including:

      - Complete target identification (url, etc.) (host)

      - Target Id in the database.

      - All targets in the database.

    Simple ping is defined as opening a connection to a wbem server
    and executing a single command on that server, normally a getClass with
    a well known CIMClass.

    """
    pass


@cimping_group.command('host', options_metavar=CMD_OPTS_TXT)
@click.argument('host', type=str, metavar='HOST NAME', required=True)
@click.option('-n', '--namespace', type=str, default=DEFAULT_NAMESPACE,
              help='Namespace for the operation.'
                   ' ' + '(Default: %s).' % DEFAULT_NAMESPACE)
@click.option('-u', '--user', type=str, default=DEFAULT_USERNAME,
              help='Optional user name for the operation.'
                   ' ' + '(Default: %s).' % DEFAULT_USERNAME)
@click.option('-p', '--password', type=str, default=DEFAULT_PASSWORD,
              help='Optional password for the operation.'
                   ' ' + '(Default; %s).' % DEFAULT_PASSWORD)
@click.option('-t', '--timeout', type=int, default=DEFAULT_OPERATION_TIMEOUT,
              help='Namespace for the operation.'
                   ' ' + '(Default: %s).' % DEFAULT_OPERATION_TIMEOUT)
@click.option('--no-ping', default=False, type=bool, required=False,
              help='Disable network ping ofthe wbem server before executing '
                   'the cim request.'
                   ' ' + '(Default: %s).' % True)
@click.option('-d' '--debug', default=False, type=bool, required=False,
              help='Set the debug parameter for the pywbem call. Displays '
                   'detailed information on the call and response.'
                   ' ' + '(Default: %s).' % False)
@click.option('-c' '--verify_cert', type=bool, required=False, default=False,
              help='Request that the client verify the server cert.'
                   ' ' + '(Default: %s).' % False)
@click.option('--certfile', default=None, type=str, required=False,
              help='Client certificate file for authenticating with the '
                   'WBEM server. If option specified the client attempts '
                   'to execute mutual authentication. '
                   'Default: Simple authentication).')
@click.option('--keyfile', default=None, type=str, required=False,
              help='Client private key file for authenticating with the '
                   'WBEM server. Not required if private key is part of the '
                   'certfile option. Not allowed if no certfile option. '
                   'Default: No client key file. Client private key should '
                   'then be part  of the certfile).')
@click.pass_obj
def cimping_host(context, host, **options):
    """
    cimping wbem server defined by hostname.

       Host name or url of the WBEM server in this format:\n
             [{scheme}://]{host}[:{port}]\n
          - scheme: Defines the protocol to use;\n
             - "https" for HTTPs protocol\n
              - "http" for HTTP protocol.\n
            Default: "https".\n
          - host: Defines host name as follows:\n
               - short or fully qualified DNS hostname,\n
               - literal IPV4 address(dotted)\n
               - literal IPV6 address (RFC 3986) with zone\n
                 identifier extensions(RFC 6874)\n
                 supporting "-" or %%25 for the delimiter.\n
          - port: Defines the WBEM server port to be used\n
            Defaults:\n
               - HTTP  - 5988\n
               - HTTPS - 5989\n
    """
    context.execute_cmd(lambda: cmd_cimping_host(context, host, options))


# TODO. Should we consider cert verify, etc. as part of this
# TODO: This differs from pattern. targetid is an argument, not options

@cimping_group.command('ids', options_metavar=CMD_OPTS_TXT)
@click.argument('ids', type=str, metavar='TargetIDs', required=False, nargs=-1)
@add_options(timeout_option)
@add_options(no_ping_option)
@click.option('-i', '--interactive', is_flag=True, default=False,
              help='If set, presents list of targets to chose.')
@add_options(debug_option)
@click.pass_obj
def cimping_ids(context, ids, **options):  # pylint: disable=redefined-builtin
    """
    Cimping a list of targets from database.

    Execute simple cim ping against the list of ids provided for target servers
    in the database defined by each id in the list of ids creates a table
    showing result.

    ex. smicli cimping ids 5 8 9

    """
    context.execute_cmd(lambda: cmd_cimping_ids(context, ids, options))


@cimping_group.command('id', options_metavar=CMD_OPTS_TXT)
@click.argument('id', type=str, metavar='TargetID', required=False)
@add_options(timeout_option)
@click.option('-i', '--interactive', is_flag=True, default=False,
              help='If set, presents list of targets to chose.')
@add_options(no_ping_option)
@add_options(debug_option)
@add_options(thread_option)
@add_options(timeout_option)
@click.pass_obj
def cimping_id(context, id, **options):
    # pylint: disable=redefined-builtin
    """
    Cimping  one target from database.

    Executes a simple ping against one target wbem servers in the target
    database and returns exit code in accord with response. Exits interactive
    mode and returns exit code corresponding to test result.

    This test sets a cmd line exit code corresponding to the status of a given
    target WBEM Server.

    This subcommand will interactively let user select the TargetID if the
    --interactive mode is selected or "?" is entered for the TargetID.

    ex. smicli cimping 5
    """
    context.execute_cmd(lambda: cmd_cimping_id(context, id, options))


@cimping_group.command('all', options_metavar=CMD_OPTS_TXT)

@click.option('-s', '--saveresult', default=False, is_flag=True,
              required=False,
              help='Save the result of each cimping test of a wbem server'
              ' to the database Pings table for future analysis. Saving the '
              'results creates an audit log record.'
              ' ' + '(Default: %s).' % False)
@click.option('-d', '--disabled', default=False, is_flag=True,
              required=False,
              help='If set include disabled targets in the cimping scan.'
              ' ' + '(Default: %s).' % False)
@add_options(timeout_option)
@add_options(no_ping_option)
@add_options(debug_option)
@add_options(thread_option)
@click.pass_obj
def cimping_all(context, **options):  # pylint: disable=redefined-builtin
    """
    CIMPing all enabled targets in database.

    Executes the ping on all enabledtargets in the targets table of the
    database.

    Creates a table of results and optionally logs status of each target in the
    Pings table (--saveresult option).

    This subcommand also compares the results with previous results in the
    pings table and marks any targets that have changed with an asterik ("*")
    as a flag.

    ex. smicli cimping all
    """
    context.execute_cmd(lambda: cmd_cimping_all(context, options))


######################################################################
#   Action functions for cim ping subcommand
######################################################################


def print_ping_result(simpleping, test_result, verbose):
    """
    Display the ping results for a single ping
    """
    if test_result.code != 0:
        print('%s Error Response, Exit code %s %s %s' % (simpleping.url,
                                                         test_result.code,
                                                         test_result.type,
                                                         test_result.exception))
    else:
        if verbose:
            print('%s Return code = %s:%s in %s sec' %
                  (simpleping.url,
                   test_result.type,
                   test_result.code,
                   test_result.execution_time))
        print('Running')     # print the word 'Running' to match javaping


def cmd_cimping_host(context, host, options):
    """
    Execute a simple ping for the host defined by the input parameters.
    """
    simpleping = SimplePing(server=host, namespace=options['namespace'],
                            user=options['user'],
                            password=options['password'],
                            timeout=options['timeout'],
                            ping=not options['no_ping'],
                            debug=options['d__debug'],
                            logfile=context.log_file,
                            log_level=context.log_level,
                            verbose=context.verbose)

    test_result = simpleping.test_server(verify_cert=options['c__verify_cert'])

    print_ping_result(simpleping, test_result, context.verbose)


def cmd_cimping_all(context, options):  # pylint: disable=redefined-builtin
    """
    Execute a simple ping of a target wbem server based using all of the targets
    from the database provided with the input parameters.
    """

    # cimping the complete set of targets
    include_disabled = options['disabled']

    print('Start ping options %s' % options)

    simple_ping_list = SimplePingList(context.targets_tbl,
                                      timeout=options['timeout'],
                                      logfile=context.log_file,
                                      log_level=context.log_level,
                                      verbose=context.verbose,
                                      threaded=not options['no_thread'],
                                      include_disabled=include_disabled)
    results = simple_ping_list.ping_servers()

    print('ping test ended')

    # get last pings information from history
    pings_tbl = PingsTable.factory(context.db_info, context.db_type,
                                   context.verbose)

    ping_rows = pings_tbl.get_last_timestamped()
    last_status = {ping[1]: ping[3] for ping in ping_rows}
    last_status_time = ping_rows[0][2]

    print("got results from history")

    # if saveresult set, update pings table with results.
    save_result = options['saveresult']
    # all records  have same timestamp
    timestamp = datetime.datetime.now()
    # if save_result set, add to pings table and make table change log entry
    if save_result:
        tbl_inst = PingsTable.factory(context.db_info, context.db_type,
                                      context.verbose)
        # if option set, append status to pings table
        for result in results:
            tbl_inst.append(result[0], result[1], timestamp)
        # TODO this may be duplicate logging since the audit log for this
        # is in the append method
        audit_logger = get_logger(AUDIT_LOGGER_NAME)
        audit_logger.info('cimping updated pings table timestamp %s add %s '
                          'records', timestamp, len(results))

    # print results of the scan.
    headers = ['Id', 'Addr', 'Result', 'Exception', 'Time', 'Company',
               'Product']
    rows = []
    if not results:
        raise click.ClickException("No response returned")
    for result in results:
        target_id = result[0]
        target = context.targets_tbl[target_id]
        test_result = result[1]

        url = context.targets_tbl.build_url(target_id)

        #print('test_result %r\n%r' % (test_result, test_result))
        #print('EXCEPTION %s %r' % (test_result.exception,
        #                           test_result.exception))
        if test_result.exception:
            test_status = "%s %s" % (test_result.type, test_result.exception)
        else:
            test_status = test_result.type
        #print('TEST_STATUS %s' % test_status)
        changed = "" if test_status == last_status[target_id] else "*"

        if changed:
            audit_logger = get_logger(AUDIT_LOGGER_NAME)
            audit_logger.info('cimping Status change target %s from %s to %s',
                              target_id, last_status[target_id], test_status)

            if context.verbose:
                print('Changed %r LAST_STATUS %r' % (last_status[target_id],
                                                     test_status))

        itemresult = '%s%s' % (test_result.type, changed)

        # format the exception column
        exception_row = None
        if test_result.exception:
            if isinstance(test_result.exception, CIMError):
                exception_row = test_result.exception.status_code_name
                if exception_row.startswith("CIM_ERR_"):
                    exception_row = exception_row[8:]
            else:
                exception_row = '%s' % test_result.exception

        rows.append([target_id,
                     url,
                     itemresult,
                     fold_cell(exception_row, 12),
                     test_result.execution_time,
                     fold_cell(target['CompanyName'], 12),
                     fold_cell(target['Product'], 12)])

    # fixed sort based on target id
    # TODO: future expand sort so that it can sort on any field.
    rows.sort(key=lambda x: x[0])

    context.spinner.stop()

    disabled_state = ': Includes Disabled' if include_disabled else ''
    save_result_state = ': SavedResult' if save_result else ''
    title = 'CIMPing all Results: %s%s %s (* status change since %s)' % \
            (disabled_state, save_result_state,
             datetime_display_str(timestamp),
             datetime_display_str(last_status_time))
    print_table(rows, headers, title=title,
                table_format=context.output_format)


def cmd_cimping_ids(context, ids, options):  # pylint: disable=redefined-builtin
    """
    Execute a simple ping of a target wbem server based on the target_ids
    from the database provided with the input parameters.
    """
    # TODO redefine this to be a subset of the all function so that it does
    # them all and then prints the table.
    ids = get_multiple_target_ids(context, ids, options)
    if ids is None:
        return

    for id_ in ids:
        try:
            context.targets_tbl.get_target(id_)  # noqa: F841
        except Exception as ex:
            raise click.ClickException('Invalid TargetID=%s. Not in database. '
                                       '%s: %s' % (id,
                                                   ex.__class__.__name__, ex))
    for id_ in ids:
        simpleping = SimplePing(target_id=id_, timeout=options['timeout'],
                                targets_tbl=context.targets_tbl,
                                ping=not options['no_ping'],
                                logfile=context.log_file,
                                threaded= not options['no_thread'],
                                log_level=context.log_level)

        # TODO: Move the requirement for all target data up and
        # set from record get the target_record
        test_result = simpleping.test_server(verify_cert=False)

        # TODO pass on output_format
        context.spinner.stop()
        print_ping_result(simpleping, test_result, context.verbose)


def cmd_cimping_id(context, id, options):
    # pylint: disable=redefined-builtin
    """
    Execute one simple ping of a target wbem server based on the target_ids
    from the database provided with the input parameters. Closes
    interactive mode
    """
    id = get_target_id(context, id, options)
    if id is None:
        return
    try:
        context.targets_tbl.get_target(id)  # noqa: F841
    except KeyError:
        raise click.ClickException('Invalid Target: ID=%s not in database'
                                   ' %s.' % (id, context.targets_tbl))

    simpleping = SimplePing(target_id=id, timeout=options['timeout'],
                            targets_tbl=context.targets_tbl,
                            ping=not options['no_ping'],
                            logfile=context.log_file,
                            log_level=context.log_level)

    # TODO: Move the requirement for all target data up and
    # set from record get the target_record
    test_result = simpleping.test_server(verify_cert=False)

    # TODO pass on output_format
    context.spinner.stop()
    print_ping_result(simpleping, test_result, context.verbose)

    # Exit with code returned from test
    sys.exit(test_result.code)
