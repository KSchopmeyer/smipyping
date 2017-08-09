smipyping: Python SMI Laboratory Test Tools
===========================================

About this project
------------------

smipyping is a set of WBEM server test tools based on the pywbem WBEM
client implementation. The goal is to provide a variety of tools to be
able to test the current status of WBEM servers both superically and by
analyzing the details of the server code using the SNIA smi profiles to
define the details of the server.

Installation Requirements
-------------------------

1. Python 2.7. At this point, this package will only run with Python2.7 because
   one of the core packages (scapy) is Python 2 only.

2. smipyping - Installed as part of the smipyping installation

3. Linux - Including linux tools like make, etc.

We do NOT support python 3 right now primarily because one required package
(scapy) does not support python 3. Plans are to remove this requirement and
then smipyping will support python 3.

Installation
------------

See INSTALL.md

Usage
-----

smipyping consists of a number of scripts that provide tests of WBEM Servers.

These are documented in the smipyping documentation.

This includes:

smicli
^^^^^^ 

This is a multilevel cli program that will include all the functionality
in the following commands: This tool incorporates a number of subcommands
including the following subcommands:

::

      cimping   Command group to do simpleping.
      explorer  Command group for general provider explore.
      help      Show help message for interactive mode.
      provider  Command group for simple provider operations.
      repl      Enter interactive (REPL) mode (default).
      targets   Command group for managing targets data.

This command is described in detail in the documentation.  It includes built-in
help at every level of the command to define the arguments and options for
that level.  Thus, for example, you can request help as follows:

.. code-block:: bash

    smicli --help                   - Top level help
    smicli cimping --help           - Tells you what options/cmds exist under
                                      cimping
    smicli cimping providers --help - Parameters for this subcommand that
                                      executes a simple ping against a host.

smicli will replace all other commands in the near future or so as we complete
the tests to be sure it is equivalent to each of these commands.

simpleping
^^^^^^^^^^
simpleping  (superceeded by smicli and to be removed for next release) is a
simple WBEM Server test tool.

This script emulates the operation of the original cim server
ping program in that it executes a test against a single server using the
input parameters to define the server parameters.  The command line input
is available with the --help option to simpleping.

This script does not depend on the userdata. You must supply all the required
fields.

Example:

.. code-block:: bash

    simpleping httpd://10.1.132.75 -u blah -p blah -n somenamespace -v

This will test the server at 10.1.132.75 with user name blah and password blah


serversweep
^^^^^^^^^^^

serversweep executes a sweep against the ipaddresses/ports defined on
input to find open ports and if the flag is set to use the userbase determines
if any servers that do have the defined ports open are in the data base.

Since this command requires running in admin mode, the easiest way to use it
with the current database of smilab servers is to run the bash script:

.. code-block:: bash

  runserversweep

which is in the smipyping directory.  That script includes the definition of
the config file (csv) and the functionality to run) the code in admin mode.
Normally it will request your password when it calls the serversweep
executable.

explore
^^^^^^^

explore (superceeded by smicli and to be removed for next release) executes
a deep exlore of servers defined in the database.

The deep explore includes:

* finding namespaces
* finding interop namespace
* finding profiles


Targets databases
-----------------

smipyping allows for multiple types of databases:

* sql (mysql and sqlite)
* csv (comma-separated-values) file as a database for at least the the
  definitions of the target WBEM servers to be tested.

mysql database
^^^^^^^^^^^^^^

TODO

csv database
^^^^^^^^^^^^
A simple csv file that is in the root directory serves as the current definition
of serevers

    targetdata_example.csv

This file is up-to-date with the definitions of wbem server targets in the
cimping sql database.


Status
------

This code is under development and is provided today in as-is status.


License
-------

smipyping is provided under the Apache-2 license.

Examples:
---------

Running a serversweep

.. code-block:: bash

    ./runserversweep

::

    Open WBEMServers:subnet(s)=['10.1.132,134,136', '10.2.100:117.1:50']
    port(s)=[5988, 5989] range 1:254, time 3.11 min
        total pings=3324 pings answered=66
     IPAddress          CompanyName      Product              SMIVersion  
    ──────────────────────────────────────────────────────────────────────
     10.1.132.135:5989  Unknown                                           
     10.1.132.176:5988  Unknown                                           
     10.1.132.177:5988  Unknown                                           
     10.1.132.178:5988  Unknown                                           
     10.1.132.179:5988  Unknown                                           
     10.1.132.22:5989   Unknown                                           
     10.1.132.24:5989   EMC              VNXe (Unified)       1.4/1.5/1.6 
     10.1.132.53:5988   Unknown                                           
     10.1.132.53:5989   Unknown                                           
     10.1.132.70:5989   Unknown                                           
     10.1.132.86:5988   Unknown                                           
     10.1.132.86:5989   Tintri           VMStore              0           
     10.1.132.87:5988   Unknown                                           
     10.1.132.87:5989   Unknown                                           
     10.1.134.116:5989  Dot Hill         Assured SAN 5720     1.5         
     10.1.134.117:5989  Dot Hill         Assured SAN 5720     1.5         
     10.1.134.136:5988  Fujitsu          DX200S3              1.6         
     10.1.134.136:5989  Unknown                                           
     10.1.134.137:5989  Hewlett Packard  HP P9500 (Embedded)  1.3.0/1.5.0 
     10.1.134.143:5988  Unknown                                           
     10.1.134.143:5989  Unknown                                           
     10.1.134.144:5988  Unknown                                           
     10.1.134.144:5989  Unknown                                           
     10.1.134.146:5989  Hewlett Packard  P2000 G3 MSA         1.5         
     10.1.134.147:5989  Hewlett Packard  P2000 G3 MSA         1.5         
     10.1.134.148:5989  Hewlett Packard  P2000 G3 MSA         1.5         
     10.1.134.163:5989  Brocade          BRCD1 Fabric                     
     10.1.134.167:5988  Unknown                                           
     10.1.134.167:5989  Unknown                                           
     10.1.134.182:5989  Unknown                                           
     10.1.134.185:5988  Unknown                                           
     10.1.134.186:5988  Unknown                                           
     10.1.134.186:5989  EMC              FC HBA               1.4         
     10.1.134.187:5988  Unknown                                           
     10.1.134.187:5989  Unknown                                           
     10.1.134.188:5988  Unknown                                           
     10.1.134.188:5989  Unknown                                           
     10.1.134.190:5989  Unknown                                           
     10.1.134.219:5989  Unknown                                           
     10.1.134.38:5989   Unknown                                           
     10.1.134.75:5988   Unknown                                           
     10.1.134.75:5989   EMC              VNX Storage Array    1.6         
     10.1.134.91:5988   Unknown                                           
     10.1.134.91:5989   Fujitsu          DX200S3              1.6         
     10.1.134.96:5988   Unknown                                           
     10.1.134.96:5989   Dell/Compellent  Storage Center       1.5         
     10.1.134.98:5988   Unknown                                           
     10.1.134.98:5989   Fujitsu          DX80S2               1.4

     . . .

Running smicli cimping
----------------------

.. code-block:: bash

    smicli cimping id 4

::

    SimplePing server None, target_id 4
    cimping url=https://10.1.134.96, ns=root/compellent, principal=******, cred=********
    Running

A running server reports 'Running'

A failed server reports errors as follows:

.. code-block:: bash

    smicli cimping id 3

::

    SimplePing server None, target_id 3
    cimping url=https://10.1.137.211, ns=cimv2, principal=smilab6, cred=F00sb4ll
    https://10.1.137.211 Error Response, Exit code 4 TimeoutError The client timed out and closed the socket after 11s.


Running smicli explorer
-----------------------

.. code-block:: bash

    smicli explorer id 4

::

     Server Basic Information
     Id  Url                  Brand  Company          Product         Vers  SMI Profiles  Interop_ns  Status   time   
    ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────
     04  https://10.1.134.96         Dell/Compellent  Storage Center                                  PyWBMEr  0.40 s

     
.. code-block:: bash

    smicli explorer id 3

::
    
    Server Basic Information
     Id  Url                   Brand  Company  Product  Vers  SMI Profiles  Interop_ns  Status   time   
    ────────────────────────────────────────────────────────────────────────────────────────────────────
     03  https://10.1.137.211         Cisco    DCNM                                     PyWBMEr  7.60 s
