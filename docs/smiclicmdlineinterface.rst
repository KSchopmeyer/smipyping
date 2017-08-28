.. _`Smicli Command line interface`:

``smicli`` Command line interface
=================================

This package provides a command line interface (``smicli``) tool
that supports communication with a WBEM server through the pywbem client
api and shell scripting.

.. _`Modes of operation`:

Modes of operation
------------------

smicli supports two modes of operation:

* `Interactive mode`_: Invoking an interactive smicli shell for typing
  smicli sub-commands.
* `Command mode`_: Using it as a standalone non-interactive command.

.. _`Interactive mode`:

Interactive mode
----------------

In interactive mode, an interactive shell environment is brought up that allows
typing smicli commands, internal commands (for operating the smicli shell), and
external commands (that are executed in the standard shell for the user).

This smicli shell is started when the ``smicli`` command is invoked without
specifying any (sub-)commands::

    $ smicli [GENERAL-OPTIONS]
    > _

Alternatively, the pywbemcl shell can also be started by specifying the ``repl``
(sub-)command::

    $ smicli [GENERAL-OPTIONS] repl
    > _

The smicli shell uses the ``>`` prompt, and the cursor is shown in the examples
above as an underscore ``_``.

General options may be specified on the ``smicli`` command, and they serve as
defaults for the smicli commands that can be typed in the smicli shell and
as the definition of the connection to a WBEM Server.

The ``smicli`` commands that can be typed in the ``smicli`` shell are simply the command
line arguments that would follow the ``smicli`` command when used in
`command mode`_::

    $ smicli

    > targets id 4
    . . . display of the definition of target with id = 4
    > targets id 5
    . . . display of the definition of target with id = 5
    > :q

For example, the smicli shell command ``targets id 4`` in the example
above has the same effect as the standalone command::

    $ smicli targets id 4

    . . . display of the definition of target with id = 4

See also `Environment variables`_.

The internal commands ``:?``, ``:h``, or ``:help`` display general help
information for external and internal commands::

    > :help
    REPL help:

      External Commands:
        prefix external commands with "!"

      Internal Commands:
        prefix internal commands with ":"
        :?, :h, :help     displays general help information
        :exit, :q, :quit  exits the repl

In this help text, "REPL" stands for "Read-Execute-Print-Loop" which is a
term that denotes the approach used in the smicli shell.

In addition to using one of the internal shell commands shown in the help text
above, you can also exit the smicli shell by typing `Ctrl-D`.

Typing ``--help`` in the smicli shell displays general help information for the
smicli commands, which includes global options and a list of the supported
commands::

    > --help
      General command line script for smicli.  This script executes a number of
      subcommands to:

          * Explore one or more smi servers for basic WBEM information and
            additional information specific to SMI.

           * Manage a database that defines smi servers. It supports two forms
             of the data base, sql database and csv file.

    Options:
      -c, --config_file TEXT  Configuration file to use for config information.
      -v, --verbose           Display extra information about the processing.
      --version               Show the version of this command and exit.
      --help                  Show this message and exit.


        Commands:
          database  Command group for operations on provider data...
          explorer  Command group for general provider explore.
          help      Show help message for interactive mode.
          provider  Command group for simple operations on...
          repl      Enter interactive (REPL) mode (default) and...


Note that ``-h`` can be uses as a shortcut for ``--help`` throughout ``smicli``.

The usage line in this help text show the standalone command use. Within the
smicli shell, the ``smicli`` word is ommitted and the remainder is typed in.

Typing ``COMMAND --help`` in the smicli shell displays help information for the
specified smicli command, for example::

    > provider --help
    Usage: smicli  provider [COMMAND-OPTIONS] COMMAND [ARGS]...

      Command group to inspect providers.

    Options:
      --help  Show this message and exit.

    Commands:
        ...

The smicli shell supports popup help text while typing, where the valid choices
are shown based upon what was typed so far, and where an item from the popup
list can be picked with <TAB> or with the cursor keys. In the following
examples, an underscore ``_`` is shown as the cursor::

    > --_
  database  Command group for operations on provider data...
  explorer  Command group for general provider explore.
  help      Show help message for interactive mode.
  provider  Command group for simple operations on...
  repl      Enter interactive (REPL) mode (default) and...


The smicli shell supports history (within one invocation of the shell, not
persisted across smicli shell invocations).

.. _`Command mode`:

Command mode
------------

In command mode, the ``smicli`` command performs its task and terminates,
like any other standalone non-interactive command.

This mode is used when the ``smicli`` command is invoked with a (sub-)command::

    $ smicli [GENERAL-OPTIONS] COMMAND [ARGS...] [COMMAND-OPTIONS]

Examples::

    $ smicli cimping http://localhost -n root/cimv2 -u username
    . . . <TODO>

In command mode, bash tab completion is also supported, but must be enabled
first as follows (in a bash shell)::

    $ eval "$(_SMICLI_COMPLETE=source smicli)"

Bash tab completion for ``smicli`` is used like any other bash tab completion::

    $ smicli --<TAB><TAB>
    ... <shows the global options to select from>

    $ smicli <TAB><TAB>
    ... <shows the commands to select from>

    $ smicli database <TAB><TAB>
    ... <shows the database sub-commands to select from>

.. _`Environment variables`:

Environment variables
---------------------

The smicli CLI has  environment variable options corresponding to the
command line options for specifying the general options to be used including:

1. SMI_CONFIG_FILE - The absolute path to the configuration file

2. SMI_DB_TYPE - The typd of database

3. SMI_LOG_LEVEL - The log level

4. SMI_OUTPUT_FORMAT - The output format for reports, etc.

If these environment variables are set, the corresponding general option on the
command line is not required and the value of the environment variable is
used.

Thus, in the following example, the second line accesses the configuration
file blah.ini ::

      $ export SMICLI_CONFIG_FILE=blah.ini
      $ smicli ...

Passwords
---------
The current `` smicli`` implementation does not support encrypted, hidden, etc. passwords.
Passwords (credentials) are defined in:

1. The options for some of the subcommands (ex. ``smicli cimping host``)

2. The targets database. There is are specific columns
in the database for users(prinicpals) and passwords(credentials)

3. A standard default credential and user name that will be used if none are
provided. This allows simplification of the database if the targets can all
be defined to use a standard user name and password.


FUTURE; We may elect to protect credentials in the future but that is an
open question today.

