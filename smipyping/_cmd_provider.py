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

# from pprint import pprint as pp  # noqa: F401
import click
import six

from pywbem import WBEMServer, WBEMConnection, Error, ValueMapping

from .smicli import cli, CMD_OPTS_TXT
from ._ping import ping_host
from .config import PING_TIMEOUT
from ._tableoutput import TableFormatter
from ._common_options import add_options, namespace_option
from ._common import filter_namelist


@cli.group('provider', options_metavar=CMD_OPTS_TXT)
def provider_group():
    """
    Command group for simple provider operations.


    This group of commands provides commands to query the providers defined
    by entries in the targets database.  This includes commands like ping,
    get basic info, get namespace info, get profile information. for
    individual providers.

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


@provider_group.command('classes', options_metavar=CMD_OPTS_TXT)
@click.option('-t', '--targetid', type=int, required=False,
              help='Define a specific target ID from the database to '
                   ' use. Multiple options are allowed.')
@click.option('-c', '--classname', type=str, metavar='CLASSNAME regex',
              required=False,
              help='Regex that filters the classnames to return only those '
                   'that match the regex. This is a case insensitive, '
                   'anchored regex. Thus, "CIM_" returns all classnames that '
                   'start with "CIM_". To return an exact classname append '
                   '"$" to the classname')
@click.option('-s', '--summary', is_flag=True, default=False, required=False,
              help='Return only the count of classes in the namespace(s)')
@add_options(namespace_option)
@click.pass_obj
def provider_classes(context, **options):
    """
    Find all classes that match CLASSNAME.

    Find all  class names in the namespace(s) of the defined WBEMServer that
    match the CLASSNAME regular expression argument. The CLASSNAME argument may
    be either a complete classname or a regular expression that can be matched
    to one or more classnames. To limit the filter to a single classname,
    terminate the classname with $.

    The regular expression is anchored to the beginning of CLASSNAME and
    is case insensitive. Thus pywbem_ returns all classes that begin with
    PyWBEM_, pywbem_, etc.

    The namespace option limits the search to the defined namespace.
    """
    context.execute_cmd(lambda: cmd_provider_classes(context, options))

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


def get_profile_info(org_vm, inst):
    """
    Get the org, name, and version from the profile instance and
    return them as a tuple.
    """
    org = org_vm.tovalues(inst['RegisteredOrganization'])
    name = inst['RegisteredName']
    vers = inst['RegisteredVersion']
    return org, name, vers


def cmd_provider_profiles(context, options):
    """Return tuple of info of autonomous profiles for this server"""
    targets = context.target_data
    target_id = options['targetid']
    server = connect_target(targets, target_id)

    org_vm = ValueMapping.for_property(server, server.interop_ns,
                                       'CIM_RegisteredProfile',
                                       'RegisteredOrganization')
    rows = []
    for inst in server.profiles:
        row = get_profile_info(org_vm, inst)
        rows.append(row)
    headers = ['Organization', 'Registered Name', 'Version']

    table = TableFormatter(rows, headers,
                           title='Advertised management profiles:',
                           table_format=context.output_format)
    table.print_table()


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
        namespaces = server.namespaces
        context.spinner.stop()

        rows = []
        for ns in namespaces:
            rows.append([ns])
        table = TableFormatter(rows, 'Namespace Name',
                               title='Server Namespaces:',
                               table_format=context.output_format)
        table.print_table()

    except Error as er:
        raise click.ClickException("%s: %s" % (er.__class__.__name__, er))


def cmd_provider_interop(context, options):
    """Display interop namespace name"""
    targets = context.target_data
    target_id = options['targetid']
    server = connect_target(targets, target_id)
    try:
        # execute the interop request before stopping spinner
        interop_ns = server.interop_ns
        context.spinner.stop()

        rows = []
        rows.append([interop_ns])
        table = TableFormatter(rows, 'Namespace Name',
                               title='Server Interop Namespace:',
                               table_format=context.output_format)
        table.print_table()

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
        server.namespaces  # pylint: disable=pointless-statement
        context.spinner.stop()

        rows = []
        headers = ['Brand', 'version', 'Interop Namespace', 'Namespaces']
        if len(server.namespaces) > 50:
            namespaces = '\n'.join(server.namespaces)
        else:
            namespaces = ', '.join(server.namespaces)
        rows.append([server.brand, server.version, server.interop_ns,
                     namespaces])
        table = TableFormatter(rows, headers,
                               title='Server General Information',
                               table_format=context.output_format)
        table.print_table()

    except Error as er:
        raise click.ClickException("%s: %s" % (er.__class__.__name__, er))


def cmd_provider_classes(context, options):
    """
    Execute the command for get class and display the result. The result is
    a list of classes/namespaces
    """
    targets = context.target_data
    target_id = options['targetid']
    server = connect_target(targets, target_id)

    if options['namespace']:
        ns_names = options['namespace']
        if ns_names not in server.namespaces:
            raise click.ClickException('Namespace %s not in server namespaces '
                                       '%s' % (ns_names, server.namespaces))
        ns_names = [ns_names]
    else:
        ns_names = server.namespaces
        ns_names.sort()

    classname_regex = options['classname']

    try:
        names_dict = {}
        for ns_name in ns_names:
            classnames = server.conn.EnumerateClassNames(
                namespace=ns_name, DeepInheritance=True)
            if classname_regex:
                classnames = filter_namelist(classname_regex, classnames)
            classnames.sort()
            names_dict[ns_name] = classnames

        rows = []
        if options['summary']:
            headers = ['Namespace', 'Class count']
            title = 'Server Class count'
            for ns_name in sorted(names_dict):
                rows.append((ns_name, len(names_dict[ns_name])))

        else:
            headers = ['Namespace', 'Classname']
            title = 'Server Classes'
            for ns_name, classes in sorted(six.iteritems(names_dict)):
                ns_rows = []
                for classname in classes:
                    ns_rows.append([ns_name, classname])
                # sort the result by classname
                ns_rows.sort(key=lambda x: x[1])
                rows.extend(ns_rows)

        context.spinner.stop()
        title += ' (filter=%s):' % classname_regex if classname_regex else ':'

        table = TableFormatter(rows, headers,
                               title='Server Classes:',
                               table_format=context.output_format)
        table.print_table()

    except Error as er:
        raise click.ClickException("%s: %s" % (er.__class__.__name__, er))
