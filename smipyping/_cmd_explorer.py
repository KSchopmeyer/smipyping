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

from pprint import pprint as pp  # noqa: F401
import click

from .smicli import cli, CMD_OPTS_TXT
from ._explore import Explorer


@cli.group('explorer', options_metavar=CMD_OPTS_TXT)
def explorer_group():
    """
    Command group for general provider explore.


    This group of commands provides the tools for general explore of all
    providers defined in the database.

    The explore queries the providers and generates information on their
    state and status including if active, namespaces, profiles, etc.
    It also normally generates a log of all activity.

    """
    pass


@explorer_group.command('all', options_metavar=CMD_OPTS_TXT)
@click.option('--ping/--no-ping', default=True,
              help='Ping the the provider as initial step in test. '
                   'Default: ping')
@click.option('--thread/--no-thread', default=True,
              help='Run test multithreaded.  Much faster. '
                   'Default: thread')
@click.pass_obj
def explore_all(context, **options):
    """
    Execute the general explorer on the enabled providers in the database

    """
    context.execute_cmd(lambda: cmd_explore_all(context, **options))


######################################################################
#
#  Action functions
#
######################################################################

def cmd_explore_all(context, **options):
    """Explore all of the providers defined in the current database and
    report results.
    """
    print('cmd_explorer options %s' % options)
    # print('context %s' % context)

    # TODO configure logging
    explorer = Explorer('smicli', context.target_data, logfile=None,
                        verbose=context.verbose,
                        ping=options['ping'], threaded=options['thread'])

    hosts = context.target_data.get_hostid_list()
    targets = []
    for host in hosts:
        if context.verbose:
            print('targest extend host %s, rtns %s' %
                  (host, context.target_data.get_target_for_host(host)))

        targets.extend(context.target_data.get_target_for_host(host))

    targets = set(targets)

    servers = explorer.explore_servers(targets)

    # print results
    # TODO make this part of normal print services
    explorer.report_server_info(servers, context.target_data)
