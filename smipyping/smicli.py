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
    Command line definition for smicli command.  This cmd line uses
    the click tool to define the command line
"""

from __future__ import print_function, absolute_import

import os
import click_repl
import click

from prompt_toolkit.history import FileHistory

from smipyping import TargetsData
from smipyping import DEFAULT_DBTYPE
from ._click_context import ClickContext

from .config import SMICLI_PROMPT, SMICLI_HISTORY_FILE
from ._click_configfile import CONTEXT_SETTINGS
from ._logging import LOG_LEVELS
from ._common import TABLE_FORMATS, DEFAULT_OUTPUT_FORMAT, set_input_variable


# Display of options in usage line
GENERAL_OPTIONS_METAVAR = '[GENERAL-OPTIONS]'
CMD_OPTS_TXT = '[COMMAND-OPTIONS]'


__all__ = ['cli', 'DB_POSSIBLE_TYPES', 'DEFAULT_DB_CONFIG']

#: Possible db types list.  This ks all of the db types allowed in smipyping
DB_POSSIBLE_TYPES = ['csv', 'mysql', 'sqlite']

#: Dictionary that defines a default database configuration
#: if no database is defined in config file or cmd line input
#: This is a csv file and corresponses to the DEFAULT_DBTYPE above
DEFAULT_DB_CONFIG = {'targetfilename': 'targetdata_example.csv'}


@click.group(invoke_without_command=True,
             context_settings=CONTEXT_SETTINGS,
             options_metavar=GENERAL_OPTIONS_METAVAR)
@click.option('-c', '--config_file', type=str, envvar='SMI_CONFIG_FILE',
              help="Configuration file to use for config information.")
# TODO set up default support
@click.option('-d', '--db_type', type=click.Choice(DB_POSSIBLE_TYPES),
              envvar='SMI_DB_TYPE',
              help="Database type. May be defined on cmd line, config file, "
                   " or through default. Default is %s." % DEFAULT_DBTYPE)
@click.option('-l', '--log_level', type=str, envvar='SMI_LOG_LEVEL',
              required=False, default=None,
              help="Optional option to enable logging for the level "
                   " defined, by the parameter. Choices are: "
                   " " + "%s" % LOG_LEVELS)
@click.option('-o', '--output-format', envvar='SMI_OUTPUT_FORMAT',
              type=click.Choice(TABLE_FORMATS),
              help="Output format (Default: {of}). pywbemcli may override "
                   "the format choice depending on the operation since not "
                   "all formats apply to all output data types."
              .format(of=DEFAULT_OUTPUT_FORMAT))
@click.option('-v', '--verbose', is_flag=True,
              help='Display extra information about the processing.')
@click.version_option(help="Show the version of this command and exit.")
@click.pass_context
def cli(ctx, config_file, db_type, log_level, output_format, verbose,
        provider_data=None, db_info=None, log_file=None):
    """
    Command line script for smicli.  This script executes a number
    of subcommands to:

    \b
        * Explore one or more smi servers for basic WBEM information and
          additional information specific to SMI.

    \b
        * Manage a database that defines smi servers, users, company names
          and history. It supports two forms of the data base, sql database
          and csv file.

    \b
        * Sweep ranges of ip addresses and ports to find wbem servers.
    """

    # TODO add for noverify, etc.

    if verbose:
        if ctx and ctx.default_map:
            for data_key in ctx.default_map.keys():
                print('ctx default map data key %s' % data_key)

    if ctx.obj is None:
        # We are in command mode or are processing the command line options in
        # interactive mode.
        # Apply the documented option defaults.

        # get the db_type. Order is cmd line, config file, default

        output_format = set_input_variable(ctx, output_format, 'output_format',
                                           DEFAULT_OUTPUT_FORMAT)

        db_type = set_input_variable(ctx, db_type, 'dbtype', DEFAULT_DBTYPE)

        log_level = set_input_variable(ctx, log_level, 'log_level', None)

        if log_level:
            if ctx.default_map and 'log_file' in ctx.default_map:
                log_file = ctx.default_map['log_file']
            else:
                log_file = 'smicli.log'
        else:
            log_file = None

        if ctx.default_map:
            db_info = ctx.default_map[db_type]
        else:
            # NEED DEFAULT for dbinfo
            db_info = {}
            print('WARNING: No Database info provided for database type %s'
                  % db_type)
        config_file_dir = os.path.dirname(os.getcwd())
        db_info['directory'] = config_file_dir
        if verbose:
            print('db_info %s' % db_info)

        # TODO: Why not glue db_type into db_info itself in context.

        # use db info to get target info.
        try:
            target_data = TargetsData.factory(db_info, db_type, verbose,
                                              output_format=output_format)
        except ValueError as ve:
            raise click.ClickException("%s: %s" % (ve.__class__.__name__, ve))

    else:
        # We are processing an interactive command.
        # We apply the option defaults from the command line options.
        # Move info from the inherited context to the current context.
        if config_file is None:
            config_file = ctx.obj.config_file
        if db_type is None:
            db_type = ctx.obj.db_type
        if db_info is None:
            db_info = ctx.obj.db_info
        if log_file is None:
            log_file = ctx.obj.log_file
        if log_level is None:
            log_level = ctx.obj.log_level
        if provider_data is None:
            target_data = ctx.obj.target_data
        if output_format is None:
            output_format = ctx.obj.output_format
        if verbose is None:
            verbose = ctx.obj.verbose

    # Create a command context for each command: An interactive command has
    # its own command context different from the command context for the
    # command line.
    ctx.obj = ClickContext(ctx, config_file, db_type, db_info, log_level,
                           log_file, target_data, output_format, verbose)

    # Invoke default command
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


@cli.command('help')
@click.pass_context
def repl_help(ctx):  # pylint: disable=unused-argument
    """
    Show help message for interactive mode.
    """
    print("""
The following can be entered in interactive mode:

  <smicli-cmd>                Execute smicli command <smicli-cmd>.
  !<shell-cmd>                Execute shell command <shell-cmd>.

  <CTRL-D>, :q, :quit, :exit  Exit interactive mode.

  <TAB>                       Tab completion (can be used anywhere).
  --help or -h                Show smicli general help message, including a
                              list of smicli commands.
  <smicli-cmd> --help      Show help message for smicli command
                              <smicli-cmd>.
  help                        Show this help message.
  :?, :h, :help               Show help message about interactive mode.
""")


@cli.command('repl')
@click.pass_context
def repl(ctx):
    """
    Enter interactive (REPL) mode (default).

    This subcommand enters the interactive mode where subcommands can be
    executed without exiting the progarm and loads any existing command
    history file.
    """
    history_file = SMICLI_HISTORY_FILE
    if history_file.startswith('~'):
        history_file = os.path.expanduser(history_file)

    print("Enter 'help' for help, <CTRL-D> or ':q' to exit smicli.")

    prompt_kwargs = {
        'message': SMICLI_PROMPT,
        'history': FileHistory(history_file),
    }
    click_repl.repl(ctx, prompt_kwargs=prompt_kwargs)
