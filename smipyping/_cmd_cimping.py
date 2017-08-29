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

from smipyping import PingsTable
from smipyping import SimplePing, SimplePingList
from .smicli import cli, CMD_OPTS_TXT
from ._common_options import add_options
from ._tableoutput import TableFormatter
from .config import DEFAULT_NAMESPACE, DEFAULT_OPERATION_TIMEOUT, \
    DEFAULT_USERNAME, DEFAULT_PASSWORD

#
#   Common options for the Ping group
#
timeout_option = [            # pylint: disable=invalid-name
    click.option('-t', '--timeout', type=int,
                 default=DEFAULT_OPERATION_TIMEOUT,
                 help='Timeout in sec for the operation.'
                      ' ' + '(Default: %s.)' % DEFAULT_OPERATION_TIMEOUT)]

no_ping_option = [            # pylint: disable=invalid-name
    click.option('--no-ping', default=False, is_flag=True, required=False,
                 help='Disable network ping of the wbem server before '
                      'executing the cim request.'
                      ' ' + '(Default: %s.)' % True)]

debug_option = [            # pylint: disable=invalid-name
    click.option('-d', '--debug', default=False, is_flag=True, required=False,
                 help='Set the debug parameter for the pywbem call. Displays '
                      'detailed information on the call and response.'
                      ' ' + '(Default: %s.)' % False)]


@cli.group('cimping', options_metavar=CMD_OPTS_TXT)
def cimping_group():
    """
    Command group to do simpleping.

    This command group executes a simple ping on the target defined by
    the subcommand.  This allows targets to be defined in a number of
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
                   ' ' + '(Default: %s.' % DEFAULT_NAMESPACE)
@click.option('-u', '--user', type=str, default=DEFAULT_USERNAME,
              help='Optional user name for the operation.'
                   ' ' + '(Default: %s.' % DEFAULT_USERNAME)
@click.option('-p', '--password', type=str, default=DEFAULT_PASSWORD,
              help='Optional password for the operation.'
                   ' ' + '(Default; %s.' % DEFAULT_PASSWORD)
@click.option('-t', '--timeout', type=int, default=DEFAULT_OPERATION_TIMEOUT,
              help='Namespace for the operation.'
                   ' ' + '(Default: %s.' % DEFAULT_OPERATION_TIMEOUT)
@click.option('--no-ping', default=False, type=bool, required=False,
              help='Disable network ping ofthe wbem server before executing '
                   'the cim request.'
                   ' ' + '(Default: %s.' % True)
@click.option('-d' '--debug', default=False, type=bool, required=False,
              help='Set the debug parameter for the pywbem call. Displays '
                   'detailed information on the call and response.'
                   ' ' + '(Default: %s.' % False)
@click.option('-c' '--verify_cert', type=bool, required=False, default=False,
              help='Request that the client verify the server cert.'
                   ' ' + '(Default: %s.' % False)
@click.option('--certfile', default=None, type=str, required=False,
              help='Client certificate file for authenticating with the '
                   'WBEM server. If option specified the client attempts '
                   'to execute mutual authentication. '
                   'Default: Simple authentication.')
@click.option('--keyfile', default=None, type=str, required=False,
              help='Client private key file for authenticating with the '
                   'WBEM server. Not required if private key is part of the '
                   'certfile option. Not allowed if no certfile option. '
                   'Default: No client key file. Client private key should '
                   'then be part  of the certfile')
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
@click.argument('IDs', type=int, metavar='TargetIDs', required=True, nargs=-1)
@add_options(timeout_option)
@add_options(no_ping_option)
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
@click.argument('ID', type=int, metavar='TargetID', required=True)
@add_options(timeout_option)
@add_options(no_ping_option)
@add_options(debug_option)
@click.pass_obj
def cimping_id(context, id, **options):  # pylint: disable=redefined-builtin
    """
    Cimping  one target from database.

    Executes a simple ping against one target wbem servers in the target
    database and returns exit code in accord with response. Exits interactive
    mode and returns exit code corresponding to test result.

    This test can specifically be used to get a cmd line exit code corresponding
    to the status of a given target WBEM Server.

    ex. smicli cimping 5
    """
    context.execute_cmd(lambda: cmd_cimping_id(context, id, options))


@cimping_group.command('all', options_metavar=CMD_OPTS_TXT)
@add_options(timeout_option)
@add_options(no_ping_option)
@click.option('-s', '--saveresult', default=False, is_flag=True,
              required=False,
              help='Save the result of each cimping test of a wbem server'
              ' to the database Pings table for future analysis.'
              ' ' + '(Default: %s.' % False)
@add_options(debug_option)
@click.pass_obj
def cimping_all(context, **options):  # pylint: disable=redefined-builtin
    """
    CIMPing all enabled targets in database.

    Executes the ping on all enabledtargets in the targets table of the
    database.

    Creates a table of results and optionally logs status of each in the
    Pings table (saveresult option)

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
    Execute a simple ping of a target wbem server based on the target_ids
    from the database provided with the input parameters.
    """

    if True:
        simple_ping_list = SimplePingList(context.target_data, None,
                                          logfile=context.log_file,
                                          log_level=context.log_level,
                                          verbose=context.verbose)
        results = simple_ping_list.ping_servers()

        headers = ['id', 'addr', 'result', 'exception', 'time', 'company']
        # print('Results %s' % results)
        rows = []
        for result in results:
            target_id = result[0]
            target = context.target_data[target_id]
            test_result = result[1]

            addr = '%s://%s' % (target['Protocol'], target['IPAddress'])
            exception = '%s' % test_result.exception

            rows.append([target_id,
                         addr,
                         ('%s:%s' % (test_result.type, test_result.code)),
                         TableFormatter.fold_cell(exception, 12),
                         test_result.execution_time,
                         TableFormatter.fold_cell(target['Product'], 12)])

        tbl_inst = PingsTable.factory(context.db_info, context.db_type,
                                      context.verbose)
        print('pingstable %s %r' % (tbl_inst, tbl_inst))
        # if option set, append status to pings table
        # TODO figure out why click prepends the s__ for this
        if options['saveresult']:
            timestamp = datetime.datetime.now()
            for result in results:
                print('ping data %s %s %s' % (result[0], result[1], timestamp))
                tbl_inst.append(result[0], result[1], timestamp)

        context.spinner.stop()

        table = TableFormatter(rows, headers,
                               title='CIMPing Results:',
                               table_format=context.output_format)
        click.echo(table.build_table())

    else:  # TODO Why this code TODO Old code before we did the all class.
        ids = context.target_data.keys()

        rows = []
        for id_ in ids:
            simpleping = SimplePing(target_id=id_, timeout=options['timeout'],
                                    target_data=context.target_data,
                                    ping=not options['no_ping'],
                                    logfile=context.log_file,
                                    log_level=context.log_level)

            # simpleping.set_param_from_targetdata(id_, context.target_data)
            test_result = simpleping.test_server(verify_cert=False)

            target = context.target_data.get_target(id_)
            addr = '%s://%s' % (target['Protocol'], target['IPAddress'])
            exception = '%s' % test_result.exception

            rows.append([id_,
                         ('%s:%s' % (test_result.type, test_result.code)),
                         TableFormatter.fold_cell(exception, 12),
                         test_result.execution_time,
                         addr,
                         TableFormatter.fold_cell(target['Product'], 8)])

        context.spinner.stop()
        headers = ['id', 'result', 'exception', 'time', 'addr', 'company']

        table = TableFormatter(rows, headers,
                               title='cimping all targets:',
                               table_format=context.output_format)
        click.echo(table.build_table())


def cmd_cimping_ids(context, ids, options):  # pylint: disable=redefined-builtin
    """
    Execute a simple ping of a target wbem server based on the target_ids
    from the database provided with the input parameters.
    """
    for id_ in ids:
        try:
            context.target_data.get_target(id_)  # noqa: F841
        except KeyError:
            raise click.ClickException('Invalid Target: ID=%s not in database'
                                       ' %s.' % (id_, context.target_data))

    for id_ in ids:
        simpleping = SimplePing(target_id=id_, timeout=options['timeout'],
                                target_data=context.target_data,
                                ping=not options['no_ping'],
                                logfile=context.log_file,
                                log_level=context.log_level)

        # TODO: Move the requirement for all target data up and
        # set from record get the target_record
        test_result = simpleping.test_server(verify_cert=False)

        # TODO pass on output_format
        context.spinner.stop()
        print_ping_result(simpleping, test_result, context.verbose)


def cmd_cimping_id(context, id, options):  # pylint: disable=redefined-builtin
    """
    Execute one simple ping of a target wbem server based on the target_ids
    from the database provided with the input parameters. Closes
    interactive mode
    """
    try:
        context.target_data.get_target(id)  # noqa: F841
    except KeyError:
        raise click.ClickException('Invalid Target: ID=%s not in database'
                                   ' %s.' % (id, context.target_data))

    simpleping = SimplePing(target_id=id, timeout=options['timeout'],
                            target_data=context.target_data,
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
