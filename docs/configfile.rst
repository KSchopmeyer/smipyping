.. _`smicli configuration file`:

smicli Configuration File
=========================

Because the smi utilities, and in particular `smicli` operate off of number
of parameters, much of the configuration uses a configuration file to
define core parameters.

The default name for the configuration file is `smicli.cfg` and it is
normally executed from the directory where smicli (or the other utilities)
are executed.  Each utility contains an in put parameter to define an alternate
location for the configuration file

This file generally includes information about:

* The database

* output report formats

* Logging parameters

* other specialcharacteristics of each of the utilities.

The configuration file is in the standard `ini` format with sections and
name/value defintions within each section

Configuration File Sections
---------------------------

The configuration file includes the following sections:

* General - Those parameters that are considered general to the startup of
the utilities

* mysql - Parameters used for the startup of a mysql database

* csv - Parameters for the startup of a csv database

* log - Parameters that define logging.

Note that some the parameters in the configuration file may be overwritten
by corresponding command line inputs.

Configuration file example
--------------------------

The following is an example of an smicli configuration file

::

    # -- FILE: smicli.cfg
    # general parameters
    [general]
    dbtype = mysql

    # connection parameters for a mysql database
    [mysql]
    host = localhost
    database = SMIStatus
    user = *******
    password = ******

    # parameters for a csv database
    [csv]
    filename = targetdata_example.csv

    # parameters for an sqllite database
    [sqllite]
    TODO

    [log]
    # define the level of logging
    loglevel = debug

