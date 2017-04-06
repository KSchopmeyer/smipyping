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
from smipyping import DEFAULT_CONFIG_FILE
from ._click_context import ClickContext

from .config import PYWBEMCLI_PROMPT, PYWBEMCLI_HISTORY_FILE

# Display of options in usage line
GENERAL_OPTIONS_METAVAR = '[GENERAL-OPTIONS]'
CMD_OPTS_TXT = '[COMMAND-OPTIONS]'

DBTYPE = 'csv'

__all__ = ['cli']


@click.group(invoke_without_command=True,
             options_metavar=GENERAL_OPTIONS_METAVAR)
@click.option('-c', '--config_file', type=str, envvar='SMI_CONFIG_FILE',
              help="Configuration file to use for config information.")
@click.option('-v', '--verbose', type=str, is_flag=True,
              help='Display extra information about the processing.')
@click.version_option(help="Show the version of this command and exit.")
@click.pass_context
def cli(ctx, config_file, verbose):
    """
    General command line script for smipyping.  This script executes a number
    of subcommands to:

    \b
        * Explore one or more smi servers for basic WBEM information and
          additional information specific to SMI.

     \b
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
    ctx.obj = ClickContext(ctx, config_file, provider_data, verbose)
    print('set contextdone ')

    # Invoke default command
    if ctx.invoked_subcommand is None:
        print('invoke cmd')
        ctx.invoke(ctx)


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
  --help                      Show smicli general help message, including a
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
    Enter interactive (REPL) mode (default) and load any existing
    history file.
    """
    print('repl start')
    history_file = SMICLI_HISTORY_FILE
    if history_file.startswith('~'):
        history_file = os.path.expanduser(history_file)

    print("Enter 'help' for help, <CTRL-D> or ':q' to exit smicli.")

    prompt_kwargs = {
        'message': SMICLI_PROMPT,
        'history': FileHistory(history_file),
    }
    click_repl.repl(ctx, prompt_kwargs=prompt_kwargs)
