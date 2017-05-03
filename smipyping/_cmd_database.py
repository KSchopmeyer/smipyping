"""
smicli commands based on python click for operations on the smipyping
data file.
"""
from __future__ import print_function, absolute_import

# from pprint import pprint as pp  # noqa: F401
import click

from .smicli import cli, CMD_OPTS_TXT
from ._configfile import read_config


@cli.group('database', options_metavar=CMD_OPTS_TXT)
def database_group():
    """
    Command group for operations on provider data maintained in a database.

    This database defines the providers to be pinged, teste, etc. includin
    all information to access the provider and key information for contacts,
    mfgr, etc.
    """
    pass


@database_group.command('list', options_metavar=CMD_OPTS_TXT)
@click.option('-f', '--fields', multiple=True, type=str, default=None,
              help='Define specific fields for output. It always includes '
                   ' TargetID. Ex. -f TargetID -f CompanyName')
@click.option('-c', '--company', type=str, default=None,
              help='regex filter to filter selected companies.')
# TODO sort by a particular field
@click.pass_obj
def database_list(context, fields, company, **options):
    """
    Display the entries in the provider database.
    """
    context.execute_cmd(lambda: cmd_database_list(context, fields, company,
                                                  options))


@database_group.command('info', options_metavar=CMD_OPTS_TXT)
@click.pass_obj
def database_info(context, **options):
    """
    get and display a list of classnames.
    """
    context.execute_cmd(lambda: cmd_database_info(context))


@database_group.command('fields', options_metavar=CMD_OPTS_TXT)
@click.pass_obj
def database_fields(context):
    """
    Display the names of fields in the providers base.
    """
    context.execute_cmd(lambda: cmd_database_fields(context))


@database_group.command('get', options_metavar=CMD_OPTS_TXT)
@click.argument('ProviderID', type=int, metavar='ProviderID', required=True)
@click.pass_obj
def database_get(context, providerid, **options):
    """
    Get the details of a single record from the database and display.
    """
    context.execute_cmd(lambda: cmd_database_get(context, providerid,
                                                 options))


@database_group.command('disable', options_metavar=CMD_OPTS_TXT)
@click.argument('ProviderID', type=int, metavar='ProviderID', required=True)
@click.option('-e', '--enable', type=str, is_flag=True,
              help='Enable the Provider if it is disabled.')
@click.pass_obj
def database_disable(context, providerid, enable, **options):
    """
    Disable a provider from scanning.
    """
    context.execute_cmd(lambda: cmd_database_disable(context, providerid,
                                                     enable, options))


##############################################################
#  Database processing commands
##############################################################


def cmd_database_disable(context, providerid, enable, options):
    """Display the information fields for the providers dictionary."""

    try:
        host_record = context.provider_data.get_dict_record(providerid)

        # TODO add test to see if already in correct state

        if host_record is not None:
            current_state = host_record['EnableScan']
            host_record['EnableScan'] = False if enable is True else True
            context.provider_data.write_updated()
        else:
            print('Id %s invalid or not in table' % providerid)

    except Exception as ex:
        raise click.ClickException("%s: %s" % (ex.__class__.__name__, ex))


def cmd_database_info(context):
    """Display information on the providers config and data file."""
    
    print('DB Info:\nfilename:%s\ndatabase type: %s' %
          (context.target_data.filename, context.target_date.db_type))

    print('config file %s' % context.config_file)
    config_info_dict = read_config(context.config_file,
                                   context.target_data.db_type)
    for key in config_info_dict:
        print('  %s; %s' % (key, config_info_dict[key]))


def cmd_database_fields(context):
    """Display the information fields for the providers dictionary."""

    print('\n'.join(context.target_data.get_field_list()))


def cmd_database_get(context, recordid, options):
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


def cmd_database_list(context, fields, company, options):
    """ List the smi providers in the database."""

    show = list(fields)
    show.append('TargetID')
    try:
        context.target_data.display_all(list(fields), company)

    except Exception as ex:
        raise click.ClickException("%s: %s" % (ex.__class__.__name__, ex))
