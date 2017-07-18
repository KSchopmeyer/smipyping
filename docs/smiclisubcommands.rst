.. _`smicli subcommands`:

smicli subcommand options
=========================

There are a number of ``smicli``  groups and subcommands defined.  Each subcommand
may have arguments  and options (defined with - or -- as part of the
name). While many arguments and options are specific to each subcommand, there
are several options that are more general and apply to multiple subcommands
including the following:

* verbose - defines the verbosity of output. Normally only used for debugging
* log - Defines the level of logging

See the ``smicli`` help for the definition of all current general options


smicli subcommands
=====================

Generally the structure of pywbemcli is:

pywbemcli <general options> <cmd-group> <subcommand> <subcommand arguments> <subcommand options>

Generally each command group is a noun, referencing some entity (ex. targets
refers to operation on the targets (definitions of wbem servers to be tested).
The subcommands are generally actions on
those entities defined by the group name. Thus ``targets`` is a group and
``list`` is a subcommand so:

    $ smicli targets list

Defines a command to list the items in the targets list on stdout.


