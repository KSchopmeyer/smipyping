
.. _`smipyping utility commands`:

smipyping utility commands
==========================

.. _`smicli`:

smicli
------

``smicli`` is the common command line tool for smipyping It  is a
single command line utility with command groups and commands.

``smicli`` uses a single integrated configuration file  It includes a number of
command groups each of which includes one or more commands (ie. in the
manner of many newer cmd line tools).

``smicli`` is more completely defined in subsequent sections of this documentation.

The subcommand groups include:

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
with the databases documented in section :ref:`Database tools`:
