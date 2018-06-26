.. _`smicli subcommands`:

smicli subcommand options
=========================

``smicli`` contains a number of command groups and subcommands.  Each subcommand
may have arguments  and options (defined with -h or --help as part of the
name). While many arguments and options are specific to each subcommand, there
are several options that are general and and are defined as part of the smicli
command.

* verbose - defines the verbosity of output. Normally only used for debugging
* log - Defines the level of logging
* output_format - Defines the output format for tables.

Thus to use verbose with a subcommand:

   smicli -v cimping all

See the ``smicli`` help for the definition of all current general options


smicli subcommands
=====================

Generally the structure of smicli is:

pywbemcli <general options> <cmd-group> <subcommand> <subcommand arguments> <subcommand options>

Generally each command group is a noun, referencing some entity (ex. targets
refers to operation on the targets (definitions of wbem servers to be tested).
The subcommands are generally actions on
those entities defined by the group name. Thus ``targets`` is a group and
``list`` is a subcommand so:


Defines a command to list the items in the targets list on stdout.

Subcommand groups
=====================

The subcommand groups fall into the following catagories:

1. Actions - This includes cimping, sweep, and explorer.  These define actions
upon the targets.

2. Table management - There is a group for each database table (ex. companies,
targets, programs, etc.). These subcommands for managing each of the tables
including viewing the table, and maintaining entries in the table. Note that
the history group is really the manager for the pings table

3. General - The help and repl subcommands are provide access to the help
information and execute the repl mode.

The command groups available for smicli are:

1. **cimping:**  -  Command group to do simpleping on providers to determine general
   status of the provider.

2. **explorer:** -  Command group to explore providers. This group provides commands
   to explore status and state of providers including profiles, namespaces,
   general size of tables, etc.

3. **provider:** -  Command group for provider operations. This allows users to
   explore providers (targets) in detail.

4. **sweep:** -     Command group to sweep for servers. Allows testing all addresses
   in a range of ip address for possible WBEM Servers and determining if these
   are already in the targets table.

5. **history:** -   Command group to manage the history (pings) table. This includes
   a number of reports to summarize history of individual and all provider
   status over time periods.6. **programs:**   Command group to process the
   programs table. Provides the capability to list and modify entries.

6. **targets:** -   Command group for managing targets data.  This is the table of
   providers currently defined and includes information on the address, security,
   etc on each entry.  Normally it includes information that cannot be
   retrievied from the providers themselves.

7. **companies:** - Command group to manage the companies table.  This group provides
   viewing and modifying entries in the table.

8. **users:**  -    Command group to process the users table. This group provides
   viewing and   modifying entries in the table.

9. **notifications** - Command group to manage the notifications table

10. **help:**  -  Show help message for interactive mode.

11. **repl:**       Enter interactive (REPL) mode (default).
