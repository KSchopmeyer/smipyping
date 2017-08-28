
.. _`smipyping utility commands`:

smipyping utility commands
==========================

.. _`smicli script`:

smicli script
-------------

The ``smicli`` command is the common interface that will be used for a
single command line utility  All of the
other individual scripts are being obsoleted as their functionality is
integrated into `smicli'.

``smicli`` replace all of the separate utilities and uses a single integrated
configuration file  It includes a number of subcommand
groups each of which includes one or more subcommands (ie. in the manner of many
newer cmd line tools).

``smicli`` is more completely defined in subsequent sections of this documentation.

Thus, the subcommand groups include:

* cimping   Command group to do simpleping.
* explorer  Command group for general provider explore.
* help      Show help message for interactive mode.
* provider  Command group for simple provider operations.
* repl      Enter interactive (REPL) mode (default).
* sweep     Command group to sweep for servers.
* targets   Command group for managing targets data.

NOTE: There may be more subcommand groups an any specific release.

Details on the use of ``smicli`` are in the following sections

In addition, smipyping includes utilities to aid in defining and working
with the databases as follows:

TODO



