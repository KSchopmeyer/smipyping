
.. _`smipyping utility commands`:

smipyping utility commands
=====================

The smipyping package provides a number of utility commands.
They are all implemented as pure-Python scripts.

These commands are installed into the Python script directory and should
therefore automatically be available in the command search path.

The following commands are provided:

* :ref:`serversweep`

  This utility sweeps a range of ip addresses looking for WBEM Servers.
  It outputs a file defining any found servers.  The input parameters
  for the sweep are defined on the command line.

* :ref:`simpleping`

  Runs a simple test against a defined WBEMServer to determine if it is
  operational.  The server to be tested is defined either by the targetId
  in the database or by the full set of connection information on that server
  (host name or ipaddress, namespace, password, user name). optionaly it
  provides input parameters to allow testing other ssl parameters such as
  certificates.


* :ref:`targets`

  This utility displays information on the WBEM Servers in the database and
  allows enabling and disabling particular servers.  Servers that are disabled
  do not participate in the sweeps such as the `explore`  

* :ref:`explore`

  This utility sweeps the entire database and generates a report on the all
  of the servers in the database showing status and relevant information about
  the servers.

.. _`smicli`:

smicli
------------

The ``smicli`` command is the common interface that will be used for a
single utility to replace the multiple tools in the early release

smicli is to replace all of the separate utilities above and to be able to
operation on a single configuration file.  It includes a number of subcommand
groups each of which includes one or more subcommands (ie. in the manner of many
newer cmd line tools).

smicli is more completely defined in subsequent sections of this documentation.

Thus, the groups include:

* database  Command group for operations on provider data in the database
* explorer  Command group for general provider explore.
* help      Show help message for interactive mode.
* provider  Command group for simple operations on the individual wbem servers
* repl      Enter interactive (REPL) mode (default) and...


Usage
^^^^^

Here is the help text of the command:

.. include:: mof_compiler.help.txt
   :literal:

.. _`serversweep`:

serversweep
-------

The ``serversweep`` command is a command line interface (CLI). It is
implemented as an interactive shell.

It sweeps the defined subnets looking for WBEM Server by executing a TCP
SYM command against all of the addresses defined by the input parameters.

The goals of a serversweep to to find all enties in the environment that
might be WBEM servers and then to futher determine if they are already in
the database.

It also creates a csv file output identifying any sweep results that may be
wbem server but are not in the database.

Note that this utility must be operated in privilege mode because it uses
ray TCP packets to determine if the defined ports are open and that can only
be done through https ports with a command such as SYN.

Usage
^^^^^

Here is the help text of the command:

.. include:: serversweep.help.txt
   :literal:

Example
^^^^^^^

The following is an example of executing this command:

::
    The configuration file localdbconfig.ini
    
    [general]
    dbtype = mysql

    [mysql]
    host = localhost
    database = SMIStatus
    user = xxxxxxx
    password = xxxxxxx

    [csv]
    filename = targetdata_example.csv

    [dbtype]    


  # execution script for 
  CONFIG_FILE=$PWD/localdbconfig.ini
  # sweeps 10.1  132, 134,136 all in octet 4(1 through 254)
  #        10.2  100 THROUGH 117      octet 4(1 through 50)
  sudo ./serversweep 10.1.132,134,136 10.2.100:117.1:50 -c $CONFIG_FILE -p 5988 -p 5989

simpleping
-------

The ``simpleping`` command is a WBEM client command line interface (CLI). It is
implemented as an interactive shell.  It executes a predefined request
against the command server defined on the command line or a particular
server from the SMIStatus datbase define by it id in that database


Usage
^^^^^

Here is the help text of the command:

.. include:: simpleping.help.txt
   :literal:


simplepingall
-------

The ``simplepingall`` command is a WBEM client command line interface (CLI). It is
implemented as an interactive shell.

This utility is an extension of the simpleping utility that executes
a predefined command against all of the WBEM servers defined in the
SMIStatus database

Usage
^^^^^

Here is the help text of the command:

.. include:: simplepingall.help.txt
   :literal:


targets
-------

The ``targets`` command is a WBEM client command line interface (CLI). It is
implemented as an interactive shell.

This utility display information about the target WBEM Servers in the database
and allows changing the status of targets

Usage
^^^^^

Here is the help text of the command:

.. include:: targets.help.txt
   :literal:

Global functions
^^^^^^^^^^^^^^^^

.. automodule:: targets
   :members:

explore
-------

The ``explore`` command is a WBEM client command line interface (CLI). That
explores the capabilities of a set of servers defined by the servers defined
in the SMIStatus database.

This command tests all of the servers in the database and generates a
report on the overall status of each server including:

* TargetId, The id of the server in the database
* Company name
* 



Usage
^^^^^

Here is the help text of the command:

.. include:: explore.help.txt
   :literal:



