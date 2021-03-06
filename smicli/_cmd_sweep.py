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
smicli commands based on python click for executing a sweep of defined targets
to find open ports and then attempting to determine if these are WBEM
servers.
"""
from __future__ import print_function, absolute_import

import time
import click

from smipyping import ServerSweep,\
    DEFAULT_SWEEP_PORT, SCAN_TYPES
from .smicli import cli, CMD_OPTS_TXT
from ._click_common import print_table
# from .config import DEFAULT_NAMESPACE, DEFAULT_OPERATION_TIMEOUT, \
#    DEFAULT_USERNAME, DEFAULT_PASSWORD


@cli.group('sweep', options_metavar=CMD_OPTS_TXT)
def sweep_group():
    """
    Command group to sweep for servers.

    Sweeping for servers involves pinging in one form or another possible
    ip/port combinations to find open ports.

    This group sweeps servers in a defined range looking for open WBEMServers.
    """
    print('sweep_group')


@sweep_group.command('nets', options_metavar=CMD_OPTS_TXT)
@click.option('-s', '--subnet', type=str, required=True, multiple=True,
              help='IP subnets to scan (ex. 10.1.132). One subnet per option '
                   'Each subnet string is itself a definition that '
                   'consists of period separated octets that are used to '
                   'create the individual ip addresses to be tested: '
                   '  * Integers: Each integer is in the range 0-255 '
                   '      ex. 10.1.2.9 '
                   '  * Octet range definition: A range expansion is in the '
                   '     form: int-int which defines the mininum and maximum '
                   '      values for that octet (ex 10.1.132-134) or '
                   '  * Integer lists: A range list is in the form: '
                   '     int,int,int\n'
                   '     and defines the set of values for that octet. '
                   'Missing octet definitions are expanded to the value '
                   'range defined by the min and max octet value parameters '
                   'All octets of the ip address can use any of the 3 '
                   'definitions.\n'
                   'Examples: 10.1.132,134 expands to addresses in 10.1.132 '
                   'and 10.1.134. where the last octet is the range 1 to 254')
@click.option('-p', '--port', type=click.IntRange(1, 65535, clamp=False),
              required=False, multiple=True,
              help='Port(s) to test. This argument may be define multiple '
                   ' ports.'
                   ' Ex. -p 5988 -p 5989. Default=%s' % DEFAULT_SWEEP_PORT)
# TODO make default external
@click.option('-t', '--scantype', type=click.Choice(SCAN_TYPES), default='tcp',
              help='Set scan type: %s. Some scan types require privilege mode.'
                   ' ' + '(Default: %s.)' % 'tcp')
@click.option('-m', 'MinOctetVal', type=click.IntRange(1, 254, clamp=False),
              required=False, default=1,
              help='Minimum expanded value for any octet that is not '
                   'specifically included in a net definition. Default = 1')
@click.option('-M', 'MaxOctetVal', type=click.IntRange(0, 254, clamp=False),
              required=False, default=254,
              help='Maximum expanded value for any octet that is not '
                   'specifically included in a net definition. Default = 254')
@click.option('-D', '--dryrun', default=False, is_flag=True, required=False,
              help='Display list of systems/ports to be scanned but do not '
                   ' scan. This is a diagnostic tool'
                   ' ' + '(Default: %s.)' % False)
@click.option('--no_threads', default=False, is_flag=True, required=False,
              help='Disable multithread scan.  This should only be used if '
                   'there are issues with the multithread scan. It is MUCH '
                   ' slower.'
                   ' ' + '(Default: %s.)' % False)
@click.pass_obj
def sweep_nets(context, **options):  # pylint: disable=redefined-builtin
    """
    Execute sweep on the ip/port combinations defined by the --subnet and
    --port options
    """
    context.execute_cmd(lambda: cmd_sweep_nets(context, options))


#####################################################################
#
#     Action functions for sweep
#
#####################################################################


def cmd_sweep_nets(context, options):
    """
    Build the list of subnets to sweep from the inputs and execute the
    server sweep over that subnet.  Upon the completion, create a report
    defining servers found in the sweep.
    """
    # Sweep the servers and display result
    if options['scantype'] != 'tcp':
        click.echo('WARNING: serversweep requires privilege mode for the %s '
                   'scantype' % options['scantype'])

    click.echo('Start sweep for subnets %s, port %s, range %s:%s' %
               (options['subnet'], options['port'], options['MinOctetVal'],
                options['MaxOctetVal']))

    start_time = time.time()   # Scan start time

    sweep = ServerSweep(list(options['subnet']),
                        options['port'],
                        targets_tbl=context.targets_tbl,
                        no_threads=options['no_threads'],
                        min_octet_val=options['MinOctetVal'],
                        max_octet_val=options['MaxOctetVal'],
                        verbose=context.verbose,
                        scan_type=options['scantype'])

    if options['dryrun']:
        sweep.list_subnets_to_scan()
    else:
        click.echo('The sweep may take several minutes')

        open_servers = sweep.sweep_servers()

        headers = ['IPAddress', 'CompanyName', 'Product', 'Status']

        rows, known, unknown = sweep.prep_open_hosts_report(open_servers)

        range_txt = '%s:%s' % (options['MinOctetVal'], options['MaxOctetVal'])
        title = 'Open WBEMServers:subnet(s)=%s\n' \
                'port(s)=%s range=%s, scan type=%s scan time=%s\n' \
                '    total pings=%s pings answered=%s' \
                % (sweep.net_defs, options['port'], range_txt,
                   options['scantype'],
                   sweep.sweep_time, sweep.total_pings, len(open_servers))

        execution_time = time.time() - start_time
        if execution_time <= 60:
            execution_time = "%.2f sec" % (round(execution_time, 1))
        else:
            execution_time = "%.2f min" % (execution_time / 60)

        context.spinner.stop()
        if rows:
            print_table(rows, headers=headers, title=title)
        else:
            range_txt = '%s:%s' % (options['MinOctetVal'],
                                   options['MaxOctetVal'])

            click.echo('No WBEM Servers found:subnet(s)=%s port(s)=%s '
                       'range %s, %s' % (sweep.net_defs, sweep.ports, range_txt,
                                         sweep.sweep_time))
        # TODO: Should the following  be in the report???
        click.echo('\nScan Results: Found=%s, Unknown=%s, Total=%s '
                   'Sweep time=%s Total time=%s' %
                   (known, unknown, (known + unknown), sweep.sweep_time,
                    execution_time))

# what about database as option???
