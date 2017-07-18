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
smicli commands based on python click for executin a simple ping against
wbem servers.  Subcommands allow executing request by specific server
information or through a database that defines characteristics of a group
of wbem servers.
"""
from __future__ import print_function, absolute_import

# from pprint import pprint as pp  # noqa: F401
import click

from smipyping import SimplePing

from .smicli import cli, CMD_OPTS_TXT

from .config import DEFAULT_NAMESPACE, DEFAULT_OPERATION_TIMEOUT, \
    DEFAULT_USERNAME, DEFAULT_PASSWORD


@cli.group('cimping', options_metavar=CMD_OPTS_TXT)
def cimping_group():
    """
    Command group to do simpleping.

    This command group executes a simple ping on the target defined by
    the subcommand.  This allows targets to be defined in a number of
    ways including:

      - Complete target identification (url, etc.)

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
    Execute a cimping on the wbem server defined by hostname.

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
    context.execute_cmd(lambda: cmd_cimping_hostname(context, host, options))


# TODO. Should we consider cert verify, etc. as part of this


@cimping_group.command('id', options_metavar=CMD_OPTS_TXT)
@click.argument('ID', type=int, metavar='TargetID', required=True)
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
@click.pass_obj
def cimping_id(context, id, **options):
    """
    Execute a simple cim ping against the target id defined in the request
    """
    context.execute_cmd(lambda: cmd_cimping_id(context, id, options))


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


def cmd_cimping_id(context, id, options):
    """
    Execute a simple ping of a target wbem server based on the target_id
    from the database provided with the input parameters.
    """
    try:
        target_record = context.target_data.get_dict_record(id)
    except Exception as ex:
        raise click.ClickException('Invalid TargetID=%s. Not in database. '
                                   '%s: %s' % (id, ex.__class__.__name__, ex))

    # TODO add other setup parameters, ping, timeout
    simpleping = SimplePing(target_id=id, timeout=options['timeout'],
                            ping=not options['no_ping'],
                            logfile=context.log_file,
                            log_level=context.log_level)

    # TODO: Move the requirement for all target data up and
    # set from record get the target_record
    simpleping.set_param_from_targetdata(id, context.target_data)

    test_result = simpleping.test_server(verify_cert=False)

    print_ping_result(simpleping, test_result, context.verbose)
