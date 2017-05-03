
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
  It outputs a file defining any found servers.

* :ref:`simpleping`

  Runs a simple test against a defined WBEMServer to determine if it is
  operational


* :ref:`targets`

  TODO

* :ref:`explore`

  TODO

.. _`mof_compiler`:

smicli
------------

The ``smicli`` command is the common interface that will be used for a
single utility to replace the multiple tools in the early release

TODO - Document

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

Usage
^^^^^

Here is the help text of the command:

.. include:: serversweep.help.txt
   :literal:

Global functions
^^^^^^^^^^^^^^^^

.. automodule:: serversweep
   :members:

simpleping
-------

The ``simpleping`` command is a WBEM client command line interface (CLI). It is
implemented as an interactive shell.

TODO

Usage
^^^^^

Here is the help text of the command:

.. include:: simpleping.help.txt
   :literal:

Global functions
^^^^^^^^^^^^^^^^

.. automodule:: simpleping
   :members:

simplepingall
-------

The ``simplepingall`` command is a WBEM client command line interface (CLI). It is
implemented as an interactive shell.

TODO

Usage
^^^^^

Here is the help text of the command:

.. include:: simplepingall.help.txt
   :literal:

Global functions
^^^^^^^^^^^^^^^^

.. automodule:: simplepingall
   :members:

targets
-------

The ``targets`` command is a WBEM client command line interface (CLI). It is
implemented as an interactive shell.

TODO

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
explores the capabilities of a set of servers defined by its config file
TODO

Usage
^^^^^

Here is the help text of the command:

.. include:: explore.help.txt
   :literal:

Global functions
^^^^^^^^^^^^^^^^

.. automodule:: explore
   :members:

