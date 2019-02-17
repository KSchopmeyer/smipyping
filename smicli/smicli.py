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
import sys
import logging
from logging import StreamHandler, NullHandler
from logging.handlers import SysLogHandler
from logging.handlers import RotatingFileHandler
import platform
import click_repl
import click

from prompt_toolkit.history import FileHistory

import smipyping

from smipyping._logging import AUDIT_LOGGER_NAME, ERROR_LOGGER_NAME

from ._click_context import ClickContext
from ._click_common import SMICLI_PROMPT, SMICLI_HISTORY_FILE
from ._click_configfile import CONTEXT_SETTINGS
from ._click_common import DEFAULT_OUTPUT_FORMAT, set_input_variable
from ._tableoutput import TABLE_FORMATS

DEFAULT_LOG = 'all=error'
DEFAULT_LOG_DESTINATION = 'file'
LOG_LEVELS = ['critical', 'error', 'warning', 'info', 'debug']
LOG_DESTINATIONS = ['file', 'stderr', 'none']

GROUPS_LOGGER_NAME = 'smipyping.groups'
CLI_LOGGER_NAME = 'smicli.cli'
DEFAULT_SYSLOG_FACILITY = 'user'

# List of values to try for the 'address' parameter when creating
# a SysLogHandler object.
# Key: Operating system type, as returned by platform.system(). For CygWin,
# the returned value is 'CYGWIN_NT-6.1', which is special-cased to 'CYGWIN_NT'.
# Value: List of values for the 'address' parameter; to be tried in the
# specified order.
SYSLOG_ADDRESSES = {
    'Linux': ['/dev/log', ('localhost', 514)],
    'Darwin': ['/var/run/syslog', ('localhost', 514)],  # OS-X
    'Windows': [('localhost', 514)],
    'CYGWIN_NT': ['/dev/log', ('localhost', 514)],  # Requires syslog-ng pkg
}

PYWBEM_LOGGER_NAME = 'pywbem'
PYWBEM_HTTP_LOGGER_NAME = 'pywbem.http'
PYWBEM_API_LOGGER_NAME = 'pywbem.api'
SMIPYPING_API_LOGGER_NAME = 'smipyping.api'

# Logger names by log component
LOGGER_NAMES = {
    'all': '',  # root logger
    'api': SMIPYPING_API_LOGGER_NAME,
    'groups': GROUPS_LOGGER_NAME,
    'cli': CLI_LOGGER_NAME,
    # 'console': CONSOLE_LOGGER_NAME,
    'pywbem': PYWBEM_LOGGER_NAME,
    'pywbemhttp': PYWBEM_HTTP_LOGGER_NAME,
    'pywbemapi': PYWBEM_API_LOGGER_NAME,
}
LOG_COMPONENTS = LOGGER_NAMES.keys()

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


def reset_logger(log_comp):
    """
    Reset the logger for the specified log component to have exactly one
    NullHandler.
    """

    name = LOGGER_NAMES[log_comp]
    logger = logging.getLogger(name)

    has_nh = False
    for h in logger.handlers:
        if not has_nh and isinstance(h, NullHandler):
            has_nh = True
            continue
        logger.removeHandler(h)

    if not has_nh:
        nh = NullHandler()
        logger.addHandler(nh)


def setup_logger(log_comp, handler, level):
    """
    Setup the logger for the specified log component to add the specified
    handler and to set it to the specified log level.
    """

    name = LOGGER_NAMES[log_comp]
    logger = logging.getLogger(name)

    logger.addHandler(handler)
    logger.setLevel(level)


@click.group(invoke_without_command=True,
             context_settings=CONTEXT_SETTINGS,
             options_metavar=GENERAL_OPTIONS_METAVAR)
@click.option('-c', '--config_file', type=str, envvar='SMI_CONFIG_FILE',
              help="Configuration file to use for config information.")
# TODO set up default support
@click.option('-d', '--db_type', type=click.Choice(DB_POSSIBLE_TYPES),
              envvar='SMI_DB_TYPE',
              help="Database type. May be defined on cmd line, config file, "
                   " or through default. "
                   "Default is %s." % smipyping.DEFAULT_DBTYPE)
@click.option('-l', '--log', type=str, metavar='COMP=LEVEL,...',
              help="Set a component to a log level (COMP: [{comps}], "
              "LEVEL: [{levels}], Default: {def_log}).".
              format(comps='|'.join(LOG_COMPONENTS),
                     levels='|'.join(LOG_LEVELS),
                     def_log=DEFAULT_LOG))
@click.option('--log-dest', type=click.Choice(LOG_DESTINATIONS),
              help="Log destination for this command (Default: {def_dest}).".
              format(def_dest=DEFAULT_LOG_DESTINATION))
@click.option('-o', '--output-format', envvar='SMI_OUTPUT_FORMAT',
              type=click.Choice(TABLE_FORMATS),
              help="Output format (Default: {of}). smicli may override "
                   "the format choice depending on the operation since not "
                   "all formats apply to all output data types."
              .format(of=DEFAULT_OUTPUT_FORMAT))
@click.option('-v', '--verbose', is_flag=True, default=False,
              help='Display extra information about the processing.')
@click.version_option(help="Show the version of this command and exit.")
@click.pass_context
def cli(ctx, config_file, db_type, log, log_dest, output_format, verbose,
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
    # TODO add log components to cmd line
    log_components = None
    syslog_facility = None

    if ctx.obj is None:
        # We are in command mode or are processing the command line options in
        # interactive mode.
        # Apply the documented option defaults.

        # get the db_type. Order is cmd line, config file, default

        output_format = set_input_variable(ctx, output_format, 'output_format',
                                           DEFAULT_OUTPUT_FORMAT)

        db_type = set_input_variable(ctx, db_type, 'dbtype',
                                     smipyping.DEFAULT_DBTYPE)

        log = set_input_variable(ctx, log, 'log', None)

        # TODO fix this log problem so we can get log config from
        # config file
        # if log:
        #    # if ctx.default_map and 'log_file' in ctx.default_map:
        #        # log_file = ctx.default_map['log_file']
        #    # else:
        #        # log_file = 'smicli.log'
        # else:
        #    # log_file = None
        log_file = 'smicli.log'

        if ctx.default_map:
            db_info = ctx.default_map[db_type]
        else:
            # NEED DEFAULT for dbinfo. For now raise exception
            db_info = {}
            # TODO correct this by moving to were first used.
            # raise click.ClickException('No Database info provided for '
            #                           'database type %s' % db_type)

        config_file_dir = os.path.dirname(os.getcwd())

        # Enable the hidden loggers.
        logger = logging.getLogger(AUDIT_LOGGER_NAME)
        logger.setLevel(logging.INFO)
        handler = RotatingFileHandler(log_file, maxBytes=80000, backupCount=4)
        formatter = logging.Formatter('%(asctime)s-%(name)s-%(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        logger = logging.getLogger(ERROR_LOGGER_NAME)
        logger.setLevel(logging.INFO)
        handler = RotatingFileHandler(log_file, maxBytes=80000, backupCount=4)
        formatter = logging.Formatter('%(asctime)s-%(name)s-%(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        db_info['directory'] = config_file_dir
        if verbose:
            print('db_info %s' % db_info)

        # TODO: Why not glue db_type into db_info itself in context.

        # use db info to get target info.
        try:
            targets_tbl = smipyping.TargetsTable.factory(
                db_info, db_type, verbose, output_format=output_format)
        except ValueError as ve:
            raise click.ClickException("Invalid database. Targets table "
                                       "load fails. Exception %s" % ve)

    else:
        # Processing an interactive command.
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
        # TODO we should be able to remove the log stuff from context
        # if we completely create the loggers here.
        if log is None:
            log_level = ctx.obj.log_level
        if log_components is None:
            log_components = ctx.obj.log_components
        if provider_data is None:
            targets_tbl = ctx.obj.targets_tbl
        if output_format is None:
            output_format = ctx.obj.output_format
        if verbose is None:
            verbose = ctx.obj.verbose

    # Now we have the effective values for the options as they should be used
    # by the current command, regardless of the mode.

    # Set up logging
    if log is None:
        log = DEFAULT_LOG
    if log_dest is None:
        log_dest = DEFAULT_LOG_DESTINATION
    if log_file is None:
        log_file = 'smicli.log'

    if log_dest == 'syslog':
        # The choices in SYSLOG_FACILITIES have been validated by click
        # so we don't need to further check them.
        facility = SysLogHandler.facility_names[syslog_facility]
        system = platform.system()
        if system.startswith('CYGWIN_NT'):
            # Value is 'CYGWIN_NT-6.1'; strip off trailing version:
            system = 'CYGWIN_NT'
        try:
            addresses = SYSLOG_ADDRESSES[system]
        except KeyError:
            raise NotImplementedError(
                "Logging to syslog is not supported on this platform: {}".
                format(system))
        assert isinstance(addresses, list)
        for address in addresses:
            try:
                handler = SysLogHandler(address=address, facility=facility)
            except Exception as exc:  # pylint: disable=broad-except
                click.echo("Exception in creating SysLogHandler, ignored. %s"
                           % exc)
                continue
            break
        else:
            exc = sys.exc_info()[1]
            exc_name = exc.__class__.__name__ if exc else None
            raise RuntimeError(
                "Creating SysLogHandler with addresses {!r} failed. "
                "Failure on last address {!r} was: {}: {}".
                format(addresses, address, exc_name, exc))
        fs = '%(levelname)s -%(name)s-%(message)s'
        handler.setFormatter(logging.Formatter(fs))
    elif log_dest == 'stderr':
        handler = StreamHandler(stream=sys.stderr)
        fs = '%(asctime)s-%(levelname)s -%(name)s-%(message)s'
        handler.setFormatter(logging.Formatter(fs))
    elif log_dest == 'file':
        if not log_file:
            raise ValueError('Filename required if log destination '
                             'is "file"')
        handler = logging.FileHandler(log_file)
        fs = '%(asctime)s-%(levelname)s -%(name)s-%(message)s'
        handler.setFormatter(logging.Formatter(fs))
    else:
        # The choices in LOG_DESTINATIONS have been validated by click
        # TODO assert log_dest == 'none'
        handler = None

    for lc in LOG_COMPONENTS:
        reset_logger(lc)

    log_specs = log.split(',')
    for log_spec in log_specs:

        # ignore extra ',' at begin, end or in between
        if log_spec == '':
            continue

        try:
            log_component, log_level = log_spec.split('=', 1)
        except ValueError:
            raise click.ClickException("Missing '=' in COMP=LEVEL "
                                       "specification in "
                                       "--log option: {ls}".
                                       format(ls=log_spec))

        level = getattr(logging, log_level.upper(), None)
        if level is None:
            raise click.ClickException("Invalid log level in COMP=LEVEL "
                                       "specification in --log option: "
                                       "{ls}".format(ls=log_spec))

        if log_component not in LOG_COMPONENTS:
            raise click.ClickException("Invalid log component in COMP=LEVEL "
                                       "specification in --log option: {ls}".
                                       format(ls=log_spec))

        if handler:
            setup_logger(log_component, handler, level)

    # Create a command context for each command: An interactive command has
    # its own command context different from the command context for the
    # command line.
    ctx.obj = ClickContext(ctx, config_file, db_type, db_info, log_level,
                           log_file, log_component, targets_tbl, output_format,
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
