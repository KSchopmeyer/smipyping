.. _`Smicli Command line interface`:

Smicli Command line interface
================================

This package provides a command line interface (CLI) in the smicli tool
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

The smicli commands that can be typed in the smicli shell are simply the command
line arguments that would follow the ``smicli`` command when used in
`command mode`_::

    $ smicli -c smli2.ini
    Enter password: <password>
    > class enumerate -o
    . . . <Enumeration of the names of classes in the defined namespace>
    > class get CIM_System
    . . . <MOF output of the class CIM_System from the WBEM Server>
    > :q

For example, the smicli shell command ``class get CIM_System`` in the example
above has the same effect as the standalone command::

    $ smicli -c smli2.ini
    Enter password: <password>
    . . . <MOF formated display of the CIM_System class>

TODO: This one is incorrect today
However, the smicli shell will prompt for a password only once during its
invocation, while the standalone command will prompt for a password every time
it is executed
.
See also `Environment variables and avoiding password prompts`_.

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


The usage line in this help text show the standalone command use. Within the
smicli shell, the ``smicli`` word is ommitted and the remainder is typed in.

Typing ``COMMAND --help`` in the smicli shell displays help information for the
specified smicli command, for example::

    > c --help
    Usage: smicli  database [COMMAND-OPTIONS] COMMAND [ARGS]...

      Command group to manage CIM Classes.

    Options:
      --help  Show this message and exit.

    Commands:

TODO

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

    $ smicli -s http://localhost -n root/cimv2 -u username class get
    Enter password: <password>
    . . . <TODO>

TODO: Need to sort this one out
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

.. _`Environment variables and avoiding password prompts`:

Environment variables and avoiding password prompts
---------------------------------------------------

The smicli CLI has  environment variable options corresponding to the
command line options for specifying the general options to be used including:

TODO add the SMICLI environment variables

If these environment variables are set, the corresponding general option on the
command line is not required and the value of the environment variable is
used.

Thus, in the following example, the second line accesses the server
http://localhost::

      $ export PYWBEMCLI_SERVER=http://localhost
      $ smicli class get CIM_Managed element

If the WBEM operations performed by a particular smicli command require a
password, the password is prompted for if the --user option is set (in both
modes of operation) and the --pasword option is not set::

      $ smicli -s http://localhost -n root/cimv2 -u user class get
      Enter password: <password>
      . . . <The display output from get class>

If both the --user and --password options are set, the command is executed
without a password prompt::

      $ smicli -s http://localhost -n root/cimv2 -u user -p blah class get
      . . . <The display output from get class>

If the operations performed by a particular smicli command do not
require a password or no user is supplied, no password is prompted for::

      $ smicli --help
      . . . <help output>

For script integration, it is important to have a way to avoid the interactive
password prompt. This can be done by storing the password string in an
environment variable or entering it on the command line.


The ``smicli`` command supports a ``connection export`` (sub-)command that
outputs the (bash) shell commands to set all needed environment variables::

      $ smicli -s http://localhost -n root/cimv2 -u fred
      Enter password: <password>
      export PYWBEMCLI_SERVER=http://localhost
      export PYWBEMCLI_NAMESPACE=root/cimv2


This ability can be used to set those environment variables and thus to persist
the connection name in the shell environment, from where it will be used in
any subsequent smicli commands::

      $ eval $(smicli -s http://localhost -u username -n namespace)
      Enter password: <password>

      $ env |grep SMICLI
      TODO - Correct the following
      export PYWBEMCLI_SERVER=http://localhost
      export PYWBEMCLI_NAMESPACE=root/cimv2

      $ smicli instance server namespaces
      . . . <list of namespaces for the defined server>

The password is only prompted for when creating the connection, and the
connection info stored in the shell environment is utilized in the
``smicli instance server namespaces`` command, avoiding
another password prompt.
