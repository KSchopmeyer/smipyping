"""
    Command line definition for smipyping command.  This cmd line uses
    the click tool to define the command line
"""

from __future__ import print_function, absolute_import
from click_repl import repl
import click
import click_spinner

from smipyping import TargetsData
from smipyping import DEFAULT_CONFIG_FILE

# Display of options in usage line
GENERAL_OPTIONS_METAVAR = '[GENERAL-OPTIONS]'
CMD_OPTS_TXT = '[COMMAND-OPTIONS]'

DBTYPE = 'csv'


@click.group(invoke_without_command=True,
             options_metavar=GENERAL_OPTIONS_METAVAR)
@click.option('-c', '--config_file', type=str, envvar='SMI_CONFIG_FILE',
              help="Configuration file to use for config information.")
@click.option('-v', '--verbose', type=str, is_flag=True,
              help='Display extra information about the processing.')
@click.version_option(help="Show the version of this command and exit.")
@click.pass_context
def smicli(ctx, config_file, verbose):
    """
    General command line script for smipyping.  This script executes a number
    of subcommands to:

        * explore one or more smi servers for basic WBEM information and
          additional information specific to SMI.
          
        
        * Manage a database that defines smi servers. It supports two forms
          of the data base, sql database and csv file.

    """
    # TODO add for noverify, etc.
    if ctx.obj is None:
        # We are in command mode or are processing the command line options in
        # interactive mode.
        # We apply the documented option defaults.
        if config_file is None:
            config_file = DEFAULT_CONFIG_FILE
            print('Using default config file %s' % config_file)
        provider_data = TargetsData.factory(config_file, DBTYPE, verbose)

    else:
        # We are processing an interactive command.
        # We apply the option defaults from the command line options.
        if config_file is None:
            config_file = ctx.obj.config_file
        if provider_data is None:
            provider_data = ctx.obj.provider_data
        if verbose is None:
            verbose = ctx.obj.verbose
    # Create a command context for each command: An interactive command has
    # its own command context different from the command context for the
    # command line.
    ctx.obj = Context(ctx, config_file, provider_data, verbose)

    # Invoke default command
    if ctx.invoked_subcommand is None:
        repl(ctx)


class Context(object):
    """
        Manage the click context object
    """

    def __init__(self, ctx, config_file, provider_data, verbose):
        self._config_file = config_file
        self._verbose = verbose
        self._provider_data = provider_data
        self._spinner = click_spinner.Spinner()

    @property
    def config_file(self):
        """
        :term:`string`: Name of the config file used.
        """
        return self._config_file

    @property
    def verbose(self):
        """
        :term:`bool`: verbose display flag
        """
        return self._verbose

    @property
    def provider_data(self):
        """
        :term:`provider_data`: Dictionary of provider data
        """
        return self._provider_data

    @property
    def spinner(self):
        """
        :class:`~click_spinner.Spinner` object.
        """
        return self._spinner

    def execute_cmd(self, cmd):
        """
        Call the cmd executor defined by cmd with the spinner
        """
        if self._provider_data is None:
            raise click.ClickException("No providers database defined")
        self.spinner.start()
        try:
            cmd()
        finally:
            self.spinner.stop()
