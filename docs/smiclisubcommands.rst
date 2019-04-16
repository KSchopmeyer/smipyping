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

smicli <general options> <cmd-group> <subcommand> <subcommand arguments> <subcommand options>

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

1. **cimping:** - Command group to do simpleping on providers to determine general
   status of the provider.  This command group executes an optional ping using
   the OS level ping and if that is successful a single request for a known
   entity (ex. CIMClass) on the WBEM Server to determine status. Generally it
   establishes that the smicli can connect to the server and that the expected
   namespace and class exist.

   This command returns a number of possible errors for exception  responses
   indicating the type of error received. See WBEM server
   :ref:`WBEM server error codes` for details of the error codes.

2. **explorer:** - Command group to explore providers. This group provides commands
   to explore status and state of providers including profiles, namespaces,
   general size of tables, etc.

3. **provider:** - Command group for detailed provider operations. This allows
   users to explore providers (targets) in detail.

4. **sweep:** - Command group to sweep for servers. Allows testing all
   addresses in a range of ip address for possible WBEM Servers and determining
   if these are already in the targets table. Typically a search would be
   executed for all IP addresses in a known subnet and for selected ports.
   This command first finds ipaddress/port combinations that respond to the
   ping and the scan option.  If the results of these tests indicate that
   there may be a WBEM server, it first confirms if the server is already
   known in the targets table. If the server is known, information on the
   server (company, etc.) is added to the report.  If it is not known, the
   sweep tool executes further tests including 1) all logical Principal and
   Credentials (taken from the target table) and possible namespaces to
   determine if a WBEM Server exists and reports what it finds.

5. **history:** - Command group to manage the history (pings) table. This includes
   a number of reports to summarize history of individual and all provider
   status over time periods. It also include a subcommand specifically to
   execute the smilab weekly report `smicli history weekly`.

6. **programs:** - Command group to view and manage the
   programs table. This table is the definition of a single SMI program and
   defines the program name, start date and end date.
   Provides the capability to list and modify entries.

6. **targets:** - Command group for managing targets data.  This is the table of
   providers currently defined and includes information on the address, security,
   etc on each entry.  Normally it includes information that cannot be
   retrievied from the providers themselves.  This subcommand allows listing
   and managing the entries of the targets table.

7. **companies:** - Command group to manage the companies table.  The companies
   table defines the company names of the each company involved and has
   references in the targets table, and the users table so that the entries
   in these tables can be linked to a company
   This group provides viewing and managing entries in the table.

8. **users:** - Command group to process the users table. The users table
   defines users associated with a company including email addresses so that
   notifications, reports, etc. can be forwarded to users concerning status
   and status changes of the targets. This group provides
   viewing and managing entries in the table.

9. **notifications** - Command group to manage the notifications table. The
   notifications table is a history of notifications sent concerning changes
   to target status.

10. **help:**  -  Show help message for interactive mode.

11. **repl:**       Enter interactive (REPL) mode (default).
