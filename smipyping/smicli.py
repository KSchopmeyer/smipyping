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
from smipyping import DEFAULT_CONFIG_FILE, DEFAULT_DBTYPE, DB_POSSIBLE_TYPES
from ._click_context import ClickContext

from .config import SMICLI_PROMPT, SMICLI_HISTORY_FILE
from ._click_configfile import CONTEXT_SETTINGS


# Display of options in usage line
GENERAL_OPTIONS_METAVAR = '[GENERAL-OPTIONS]'
CMD_OPTS_TXT = '[COMMAND-OPTIONS]'

__all__ = ['cli']

@click.group(invoke_without_command=True,
             context_settings=CONTEXT_SETTINGS,
             options_metavar=GENERAL_OPTIONS_METAVAR)
@click.option('-c', '--config_file', type=str, envvar='SMI_CONFIG_FILE',
              help="Configuration file to use for config information.")
# TODO set up default support
@click.option('-D', '--db_type', type=click.Choice(DB_POSSIBLE_TYPES),
              envvar='SMI_DB_TYPE',
              help="Database type. May be defined on cmd line, config file, "
                   " or through default. Default is %s." % DEFAULT_DBTYPE)
@click.option('-v', '--verbose', is_flag=True,
              help='Display extra information about the processing.')
@click.version_option(help="Show the version of this command and exit.")
@click.pass_context
def cli(ctx, config_file, db_type, verbose, provider_data=None, db_info=None):
    """
    General command line script for smicli.  This script executes a number
    of subcommands to:

    \b
        * Explore one or more smi servers for basic WBEM information and
          additional information specific to SMI.

     \b
        * Manage a database that defines smi servers. It supports two forms
          of the data base, sql database and csv file.

    """

    # TODO add for noverify, etc.
    print('CONTEXT_SETTINGS %s ' % CONTEXT_SETTINGS)
    print('ctx type %s' % type(ctx))
    if ctx and ctx.default_map:
        for data_key in ctx.default_map.keys():
            print('ctx default map data key %s' % data_key)

    if ctx.obj is None:
        # We are in command mode or are processing the command line options in
        # interactive mode.
        # Apply the documented option defaults.

        # get the db_type. Order is cmd line, config file, default
        if db_type:
            db_type = db_type
        elif  ctx.default_map and 'dbtype' in ctx.default_map:
            db_type = ctx.default_map['dbtype']
        else:
            db_type = DEFAULT_DBTYPE
        print('dbtype %s' % db_type)

        if ctx.default_map:
            db_info = ctx.default_map[db_type]
        else:
            # NEED DEFAULT for dbinfo
            db_info = {}
        config_file_dir = os.path.dirname(os.getcwd())
        db_info['directory'] = config_file_dir
        print('db_info %s' % db_info)
        # TODO: Why not glue db_type into db_info itself in context.

        # use db info to get target info.
        try:
            # print('csv config config_file %s' % config_file)
            # csv_config = read_config(config_file, 'csv')
            # filename = csv_config['filename']
            # if not os.path.dirname(filename):
            #    filename = os.path.join(config_file_dir, filename)
            target_data = TargetsData.factory(db_info, db_type, verbose)
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
        if provider_data is None:
            target_data = ctx.obj.target_data
        if verbose is None:
            verbose = ctx.obj.verbose

    # Create a command context for each command: An interactive command has
    # its own command context different from the command context for the
    # command line.
    ctx.obj = ClickContext(ctx, config_file, db_type, db_info, target_data,
                           verbose)

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
