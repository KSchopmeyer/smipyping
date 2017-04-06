"""
smicli commands based on python click for operations on the smipyping
data file.
"""
from __future__ import print_function, absolute_import

import click
from pprint import pprint as pp  # noqa: F401

from .smicli import cli, CMD_OPTS_TXT


@cli.group('server', options_metavar=CMD_OPTS_TXT)
def explore_group():
    """
    Command group for operations on provider data maintained in a database.

    This database defines the providers to be pinged, teste, etc. includin
    all information to access the provider and key information for contacts,
    mfgr, etc.
    """
    pass


@explore_group.command('info', options_metavar=CMD_OPTS_TXT)
@click.argument('providerid', multiple=True, type=str, default=None,
                help='Define a specific Provider ID from the database to '
                     ' use.')
@click.pass_obj
def provider_info(context, providerid, **options):
    """
    Display the brand information for the providers defined by the options.

    The options include providerid which defines one or more provider id's
    to be displayed.

    The company options allows searching by company name in the provider
    base.
    """
    context.execute_cmd(lambda: cmd_provider_info(context, providerid,
                                                  options))


def cmd_provider_info(context, providerid, options):
    """Search get brand info for a set of providers"""

    # get server info for this provider

    # get the info for this set of providers
