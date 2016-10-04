smipyping SMI Laboratory test tools
--------------------------------

About this project
------------------

smipyping is a set of WBEM server test tools based on the pywbem WBEM
client implementation. The goal is to provide a variety of tools to be
able to test the current status of WBEM servers both superically and by
analyzing the details of the server code using the SNIA smi profiles to
define the details of the server.

Usage
-----

smipyping consists of a number of scripts that provide tests of WBEM Servers

This includes:

- simpleping - This script emulates the operation of the original cim server
ping program in that it executes a test against a single server using the
input parameters to define the server parameters.  The command line input
is available with the --help option to simpleping.

Status
------

This code is under development and is provided today in as-is status.


License
-------

smipyping is provided under the  MIT license.
