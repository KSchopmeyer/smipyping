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

from .smicli import cli, CMD_OPTS_TXT


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
              help='Define specific fields for output. It always includes '
                   ' TargetID. Ex. -f TargetID -f CompanyName')
@click.option('-c', '--company', type=str, default=None,
              help='regex filter to filter selected companies.')
# TODO sort by a particular field
@click.pass_obj
def targets_list(context, fields, company, **options):
    """
    Display the entries in the provider database.
    """
    context.execute_cmd(lambda: cmd_targets_list(context, fields, company,
                                                 options))


@targets_group.command('info', options_metavar=CMD_OPTS_TXT)
@click.pass_obj
def targets_info(context):
    """
    get and display a list of classnames.
    """
    context.execute_cmd(lambda: cmd_targets_info(context))


@targets_group.command('fields', options_metavar=CMD_OPTS_TXT)
@click.pass_obj
def targets_fields(context):
    """
    Display the names of fields in the providers base.
    """
    context.execute_cmd(lambda: cmd_targets_fields(context))


@targets_group.command('get', options_metavar=CMD_OPTS_TXT)
@click.argument('ProviderID', type=int, metavar='ProviderID', required=True)
@click.pass_obj
def targets_get(context, providerid, **options):
    """
    Get the details of a single record from the database and display.
    """
    context.execute_cmd(lambda: cmd_targets_get(context, providerid, options))


@targets_group.command('disable', options_metavar=CMD_OPTS_TXT)
@click.argument('ProviderID', type=int, metavar='ProviderID', required=True)
@click.option('-e', '--enable', is_flag=True,
              help='Enable the Provider if it is disabled.')
@click.pass_obj
def targets_disable(context, providerid, enable, **options):
    """
    Disable a provider from scanning.
    """
    context.execute_cmd(lambda: cmd_targets_disable(context, providerid,
                                                    enable, options))


##############################################################
#  targets processing commands
##############################################################


def cmd_targets_disable(context, providerid, enable, options):
    """Display the information fields for the providers dictionary."""

    try:
        host_record = context.provider_data.get_dict_record(providerid)

        # TODO add test to see if already in correct state

        if host_record is not None:
            host_record['EnableScan'] = False if enable is True else True
            context.provider_data.write_updated()
        else:
            print('Id %s invalid or not in table' % providerid)

    except Exception as ex:
        raise click.ClickException("%s: %s" % (ex.__class__.__name__, ex))


def cmd_targets_info(context):
    """Display information on the targets config and data file."""

    print('DB Info: type=%s config file %s' % (context.target_data.db_type,
                                               context.config_file))

    if context.db_info:
        for key in context.db_info:
            print('  %s=%s' % (key, context.db_info[key]))

    else:
        print('context %r' % context)


def cmd_targets_fields(context):
    """Display the information fields for the providers dictionary."""

    print('\n'.join(context.target_data.get_field_list()))


def cmd_targets_get(context, recordid, options):
    """Display the fields of a single provider record."""

    try:
        provider_record = context.target_data.get_dict_record(recordid)

        # TODO need to order output.
        for key in provider_record:
            print('%s: %s' % (key, provider_record[key]))

    except KeyError as ke:
        print('record id %s invalid for this database.' % recordid)
        raise click.ClickException("%s: %s" % (ke.__class__.__name__, ke))

    except Exception as ex:
        raise click.ClickException("%s: %s" % (ex.__class__.__name__, ex))


def cmd_targets_list(context, fields, company, options):
    """ List the smi providers in the database."""

    show = list(fields)
    show.append('TargetID')
    try:
        context.target_data.display_all(list(fields), company)

    except Exception as ex:
        raise click.ClickException("%s: %s" % (ex.__class__.__name__, ex))
