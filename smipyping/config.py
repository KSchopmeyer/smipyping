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
The :mod:`smipyping.config` module sets configuration variables for smipyping.

These configuration variables are used bysmipyping only after its modules
have been loaded, so they can be modified by the user directly after
importing :mod:`smipyping`. For example:

::

    import smipyping
    pywbem.config.ENFORCE_INTEGER_RANGE = False

Note that the source file of the :mod:`pywbem.config` module should not be
changed by the user. Instead, use the technique described above to modify
the variables.
"""

# This module is meant to be safe for 'import *'.

__all__ = ['ENFORCE_INTEGER_RANGE', 'DEFAULT_SWEEP_PORT',
           'PING_TEST_CLASS', 'SIMPLEPING_OPERATION_DEFAULT_TIMEOUT',
           'DEFAULT_CONFIG_FILE', 'DEFAULT_NAMESPACE', 'DEFAULT_DBTYPE',
           'DEFAULT_SMICLI_CONFIG_FILES',
           'DEFAULT_OPERATION_TIMEOUT', 'DEFAULT_USERNAME', 'DEFAULT_PASSWORD']

#: Enforce the value range in CIM integer types (e.g. :class:`~pywbem.Uint8`).
#:
#: * True (default): Enforce the value range; Assigning values out of range
#:   causes :exc:`~py:exceptions.ValueError` to be raised.
#: * False: Do not enforce the value range; Assigning values out of range
#:   works.
ENFORCE_INTEGER_RANGE = True

#: The default port used by the serversweep function in case no parameter is
#: provided. This is the DMTF defined https port.
DEFAULT_SWEEP_PORT = 5989

#: The class that is used in ping tests.
PING_TEST_CLASS = 'CIM_ComputerSystem'

#: Timetout in seconds for the ping command
PING_TIMEOUT = 2

#: Timeout in seconds for the WBEM operation
SIMPLEPING_OPERATION_DEFAULT_TIMEOUT = 20

#: Default configuration file for smipyping cli
DEFAULT_CONFIG_FILE = 'smicli.ini'

#: Default smi cli configuration file for smipyping cli
#: These are the default names for the smicli config files

DEFAULT_SMICLI_CONFIG_FILES = ['smicli.ini', 'smicli.cfg']

#: Defualt namespace when none is specified
DEFAULT_NAMESPACE = 'root/cimv2'

#: type of database to use. Possible types are in DB_TYPES
DEFAULT_DBTYPE = 'csv'

#: Maximum number of parallel threads to use in multithreaded operations
MAX_THREADS = 100

#: Characters for cmdline prompt when the smicli repl is executing.
#: The prompt is presented at the beginning of a line awaiting a command
#: input.
#: The prompt MUST BE Unicode (prompt-toolkit requirement)

SMICLI_PROMPT = u'smicli> '

#: File path of history file for interactive mode.
#: If the file name starts with tilde (which is handled by the shell, not by
#: the file system), it is properly expanded.

SMICLI_HISTORY_FILE = '~/.smicli_history'

#: Default operation timeout in seconds if none is specified.
DEFAULT_OPERATION_TIMEOUT = 10

#: Default user name if not specified.
#: Used primarily to set user names the same across a number of servers.
DEFAULT_USERNAME = 'smilab'

DEFAULT_PASSWORD = 'F00sb4ll'
