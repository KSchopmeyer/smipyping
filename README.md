smipyping SMI Laboratory test tools
--------------------------------

About this project
------------------

smipyping is a set of WBEM server test tools based on the pywbem WBEM
client implementation. The goal is to provide a variety of tools to be
able to test the current status of WBEM servers both superically and by
analyzing the details of the server code using the SNIA smi profiles to
define the details of the server.

Installation
------------

See INSTALL.md

Usage
-----

smipyping consists of a number of scripts that provide tests of WBEM Servers

This includes:

- simpleping - This script emulates the operation of the original cim server
ping program in that it executes a test against a single server using the
input parameters to define the server parameters.  The command line input
is available with the --help option to simpleping.

This script does not depend on the userdata. You must supply all the required
fields.

Example:

    simpleping httpd://10.1.132.75 -u blah -p blah -n somenamespace -v

This will test the server at 10.1.132.75 with user name blah and password blah

- simplepingall - Script that executes simpleping against every entry
in the userbase.

- serversweep - does a sweep against the ipaddresses/ports defined on
input to find open ports and if the flag is set to use the userbase determines
if any servers that do have the defined ports open are in the data base.

- explore - Deep explore against servers defined in the user base.

Today the user base is a simple csv file that is in the root directory
of the smipyping installation.  We do have a problem in that I assume
it is in the same directory that you are using to execute.



Status
------

This code is under development and is provided today in as-is status.


License
-------

smipyping is provided under the  MIT license.
