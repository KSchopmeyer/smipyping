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
from pprint import pprint as pp  # noqa: F401

from pywbem import WBEMServer, WBEMConnection, Error, ValueMapping

from .smicli import cli, CMD_OPTS_TXT
from ._ping import ping_host
from .config import PING_TIMEOUT


@cli.group('provider', options_metavar=CMD_OPTS_TXT)
def provider_group():
    """
    Command group for operations on provider data maintained in a database.


    This group of commands provides commands to query the providers defined
    by entries in the targets database.  this includes commands like ping,
    get basic info, get namespace info, get profile information.

    It differs from the explore group in that it provides tools to process
    individual providers in the database rather than try to explore the
    entire set of providers.
    """
    pass


@provider_group.command('ping', options_metavar=CMD_OPTS_TXT)
@click.option('-t', '--targetid', type=int, required=False,
              help='Define a specific target ID from the database to '
                   ' use. Multiples are allowed.')
@click.option('--timeout', type=int, required=False, default=PING_TIMEOUT,
              help='Timeout for the ping in seconds.'
                   ' ' + '(Default %s.' % PING_TIMEOUT)
@click.pass_obj
def provider_ping(context, **options):
    """
    Ping the provider defined by targetid.

    The options include providerid which defines one or more provider id's
    to be displayed.

    The company options allows searching by company name in the provider
    base.
    """
    context.execute_cmd(lambda: cmd_provider_ping(context, options))


@provider_group.command('info', options_metavar=CMD_OPTS_TXT)
@click.option('-t', '--targetid', type=int, required=False,
              help='Define a specific target ID from the database to '
                   ' use. Multiples are allowed.')
@click.pass_obj
def provider_info(context, **options):
    """
    Display the brand information for the providers defined by the options.

    The options include providerid which defines one or more provider id's
    to be displayed.

    The company options allows searching by company name in the provider
    base.
    """
    context.execute_cmd(lambda: cmd_provider_info(context, options))


@provider_group.command('interop', options_metavar=CMD_OPTS_TXT)
@click.option('-t', '--targetid', type=int, required=False,
              help='Define a specific target ID from the database to '
                   ' use. Multiples are allowed.')
@click.pass_obj
def provider_interop(context, **options):
    """
    Display the brand information for the providers defined by the options.

    The options include providerid which defines one or more provider id's
    to be displayed.

    The company options allows searching by company name in the provider
    base.
    """
    context.execute_cmd(lambda: cmd_provider_interop(context, options))


@provider_group.command('namespaces', options_metavar=CMD_OPTS_TXT)
@click.option('-t', '--targetid', type=int, required=False,
              help='Define a specific target ID from the database to '
                   ' use. Multiples are allowed.')
@click.pass_obj
def provider_namespaces(context, **options):
    """
    Display the brand information for the providers defined by the options.

    The options include providerid which defines one or more provider id's
    to be displayed.

    The company options allows searching by company name in the provider
    base.
    """
    context.execute_cmd(lambda: cmd_provider_namespaces(context, options))


@provider_group.command('profiles', options_metavar=CMD_OPTS_TXT)
@click.option('-t', '--targetid', type=int, required=False,
              help='Define a specific target ID from the database to '
                   ' use. Multiple options are allowed.')
@click.option('-o', '--organization', type=int, required=False,
              help='Optionally specify organization for the profiles')
@click.option('-n', '--name', type=int, required=False,
              help='Optionally specify name for the profiles')
@click.option('-v', '--version', type=int, required=False,
              help='Optionally specify versionfor the profiles')
@click.pass_obj
def provider_profiles(context, **options):
    """
    profile information

    The options include providerid which defines one or more provider id's
    to be displayed.

    The company options allows searching by company name in the provider
    base.
    """
    context.execute_cmd(lambda: cmd_provider_profiles(context, options))

#########################################################################
##
#########################################################################


def cmd_provider_ping(context, options):
    """Ping the defined target"""
    targets = context.target_data
    target_id = options['targetid']

    try:
        target = targets[target_id]
    except Exception as ex:
        raise click.ClickException("%s: %s" % (ex.__class__.__name__, ex))

    ip_address = target['IPAddress']

    result = ping_host(ip_address, options['timeout'])

    status = 'Passed' if result else 'Failed'

    click.echo('ping %s %s' % (ip_address, status))


def print_profile_info(org_vm, inst):
    """Print the registered org, name, version for the profile defined by
       inst
    """
    org = org_vm.tovalues(inst['RegisteredOrganization'])
    name = inst['RegisteredName']
    vers = inst['RegisteredVersion']
    click.echo("  %s %s Profile %s" % (org, name, vers))


def cmd_provider_profiles(context, options):
    """Display list of autonomous profiles for this server"""
    targets = context.target_data
    target_id = options['targetid']
    server = connect_target(targets, target_id)

    click.echo("Advertised management profiles:")
    org_vm = ValueMapping.for_property(server, server.interop_ns,
                                       'CIM_RegisteredProfile',
                                       'RegisteredOrganization')
    for inst in server.profiles:
        print_profile_info(org_vm, inst)


def connect_target(targets, target_id):
    """
    Connect to the target defined by target_id.  This function does
    not actually contact the server so there is no try block
    """

    try:
        target = targets[target_id]
    except Exception as ex:
        raise click.ClickException("%s: %s" % (ex.__class__.__name__, ex))

    uri = '%s://%s' % (target['Protocol'], target['IPAddress'])
    creds = None
    if target['Principal'] or target['Credential']:
        creds = (target['Principal'], target['Credential'])

    conn = WBEMConnection(uri,
                          creds,
                          no_verification=True,
                          timeout=20)
    server = WBEMServer(conn)
    return server


def cmd_provider_namespaces(context, options):
    """Display interop namespace name"""
    targets = context.target_data
    target_id = options['targetid']
    server = connect_target(targets, target_id)
    try:
        # execute the namespaces just to get the data
        server.namespaces
        context.spinner.stop()

        click.echo("Interop namespace:\n  %s" % server.interop_ns)
    except Error as er:
        raise click.ClickException("%s: %s" % (er.__class__.__name__, er))


def cmd_provider_interop(context, options):
    """Display interop namespace name"""
    targets = context.target_data
    target_id = options['targetid']
    server = connect_target(targets, target_id)
    try:
        # execute the namespace cmd just to force the server connect
        namespaces = server.namespaces
        context.spinner.stop()

        click.echo("All namespaces:")
        for ns in namespaces:
            click.echo("  %s" % ns)
    except Error as er:
        raise click.ClickException("%s: %s" % (er.__class__.__name__, er))


def cmd_provider_info(context, options):
    """Search get brand info for a set of providers"""
    targets = context.target_data
    target_id = options['targetid']
    server = connect_target(targets, target_id)

    try:
        # execute the namespaces to force contact with server before
        # turning off the spinner.
        server.namespaces
        context.spinner.stop()

        click.echo("Brand:\n  %s" % server.brand)
        click.echo("Version:\n  %s" % server.version)
        click.echo("Interop namespace:\n  %s" % server.interop_ns)

        click.echo("All namespaces:")
        for ns in server.namespaces:
            click.echo("  %s" % ns)
    except Error as er:
        raise click.ClickException("%s: %s" % (er.__class__.__name__, er))
