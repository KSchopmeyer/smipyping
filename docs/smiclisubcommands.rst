.. _`smicli subcommands`:

smicli subcommand options
============================

There are a number of ``smicli``  groups and subcommands defined.  Each subcommand
may have arguments  and options (defined with - or -- as part of the
name). While many arguments and options are specific to each subcommand, there
are several that are more general and apply to multiple subcommands including
the following:

TODO - right now there are none

smicli subcommands
=====================

Generally the structure of pywbemcli is:

pywbemcli <general options> <cmd-group> <subcommand> <subcommand arguments> <subcommand options>

Generally each command group is a noun, referencing some entity (ex. class
referes to operation on CIMClasses). The subcommands are generally actions on
those entities defined by the group name. Thus ``database`` is a group and
``display`` is a subcommand so:

    $ pywbemcli database display

Defines a command to get display the database entries.

TODO: Incomplete in that it says it does the whole database

