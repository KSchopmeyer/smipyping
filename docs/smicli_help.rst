
.. _`Help Command Details`:lt
Help Command Details
====================


This section defines the help output for each smicli group and subcommand.


.. _`smicli  --help`:lt
smicli  --help
**************

::

    Usage: smicli [GENERAL-OPTIONS] COMMAND [ARGS]...
    
      General command line script for smicli.  This script executes a number of
      subcommands to:
    
          * Explore one or more smi servers for basic WBEM information and
            additional information specific to SMI.
    
           * Manage a database that defines smi servers. It supports two forms
             of the data base, sql database and csv file.
    
    Options:
      -c, --config_file TEXT          Configuration file to use for config
                                      information.
      -d, --db_type [csv|mysql|sqlite]
                                      Database type. May be defined on cmd line,
                                      config file,  or through default. Default is
                                      mysql.
      -v, --verbose                   Display extra information about the
                                      processing.
      --version                       Show the version of this command and exit.
      --help                          Show this message and exit.
    
    Commands:
      explorer  Command group for general provider explore.
      help      Show help message for interactive mode.
      provider  Command group for simple operations on...
      repl      Enter interactive (REPL) mode (default) and...
      targets   Command group for managing targets data.



.. _`Help Command Details`:lt
Help Command Details
====================


This section defines the help output for each smicli group and subcommand.


.. _`smicli explorer --help`:lt
smicli explorer --help
======================

::

    Usage: smicli explorer [COMMAND-OPTIONS] COMMAND [ARGS]...
    
      Command group for general provider explore.
    
      This group of commands provides the tools for general explore of all
      providers defined in the database.
    
      The explore queries the providers and generates information on their state
      and status including if active, namespaces, profiles, etc. It also
      normally generates a log of all activity.
    
    Options:
      --help  Show this message and exit.
    
    Commands:
      all  Execute the general explorer on the enabled...



.. _`Help Command Details`:lt
Help Command Details
====================


This section defines the help output for each smicli group and subcommand.


.. _`smicli explorer all --help`:lt
smicli explorer all --help
--------------------------

::

    Usage: smicli explorer all [COMMAND-OPTIONS]
    
      Execute the general explorer on the enabled providers in the database
    
    Options:
      --ping / --no-ping      Ping the the provider as initial step in test.
                              Default: ping
      --thread / --no-thread  Run test multithreaded.  Much faster. Default:
                              thread
      --help                  Show this message and exit.



.. _`Help Command Details`:lt
Help Command Details
====================


This section defines the help output for each smicli group and subcommand.


.. _`smicli help --help`:lt
smicli help --help
==================

::

    Usage: smicli help [OPTIONS]
    
      Show help message for interactive mode.
    
    Options:
      --help  Show this message and exit.



.. _`Help Command Details`:lt
Help Command Details
====================


This section defines the help output for each smicli group and subcommand.


.. _`smicli provider --help`:lt
smicli provider --help
======================

::

    Usage: smicli provider [COMMAND-OPTIONS] COMMAND [ARGS]...
    
      Command group for simple operations on providers.
    
      This group of commands provides commands to query the providers defined by
      entries in the targets database.  this includes commands like ping, get
      basic info, get namespace info, get profile information. for individual
      providers.
    
      It differs from the explore group in that it provides tools to process
      individual providers in the database rather than try to explore the entire
      set of providers.
    
    Options:
      --help  Show this message and exit.
    
    Commands:
      info        Display the brand information for the...
      interop     Display the brand information for the...
      namespaces  Display the brand information for the...
      ping        Ping the provider defined by targetid.
      profiles    profile information The options include...



.. _`Help Command Details`:lt
Help Command Details
====================


This section defines the help output for each smicli group and subcommand.


.. _`smicli provider info --help`:lt
smicli provider info --help
---------------------------

::

    Usage: smicli provider info [COMMAND-OPTIONS]
    
      Display the brand information for the providers defined by the options.
    
      The options include providerid which defines one or more provider id's to
      be displayed.
    
      The company options allows searching by company name in the provider base.
    
    Options:
      -t, --targetid INTEGER  Define a specific target ID from the database to
                              use. Multiples are allowed.
      --help                  Show this message and exit.



.. _`Help Command Details`:lt
Help Command Details
====================


This section defines the help output for each smicli group and subcommand.


.. _`smicli provider interop --help`:lt
smicli provider interop --help
------------------------------

::

    Usage: smicli provider interop [COMMAND-OPTIONS]
    
      Display the brand information for the providers defined by the options.
    
      The options include providerid which defines one or more provider id's to
      be displayed.
    
      The company options allows searching by company name in the provider base.
    
    Options:
      -t, --targetid INTEGER  Define a specific target ID from the database to
                              use. Multiples are allowed.
      --help                  Show this message and exit.



.. _`Help Command Details`:lt
Help Command Details
====================


This section defines the help output for each smicli group and subcommand.


.. _`smicli provider namespaces --help`:lt
smicli provider namespaces --help
---------------------------------

::

    Usage: smicli provider namespaces [COMMAND-OPTIONS]
    
      Display the brand information for the providers defined by the options.
    
      The options include providerid which defines one or more provider id's to
      be displayed.
    
      The company options allows searching by company name in the provider base.
    
    Options:
      -t, --targetid INTEGER  Define a specific target ID from the database to
                              use. Multiples are allowed.
      --help                  Show this message and exit.



.. _`Help Command Details`:lt
Help Command Details
====================


This section defines the help output for each smicli group and subcommand.


.. _`smicli provider ping --help`:lt
smicli provider ping --help
---------------------------

::

    Usage: smicli provider ping [COMMAND-OPTIONS]
    
      Ping the provider defined by targetid.
    
      The options include providerid which defines one or more provider id's to
      be displayed.
    
      The company options allows searching by company name in the provider base.
    
    Options:
      -t, --targetid INTEGER  Define a specific target ID from the database to
                              use. Multiples are allowed.
      --timeout INTEGER       Timeout for the ping in seconds. (Default 2.
      --help                  Show this message and exit.



.. _`Help Command Details`:lt
Help Command Details
====================


This section defines the help output for each smicli group and subcommand.


.. _`smicli provider profiles --help`:lt
smicli provider profiles --help
-------------------------------

::

    Usage: smicli provider profiles [COMMAND-OPTIONS]
    
      profile information
    
      The options include providerid which defines one or more provider id's to
      be displayed.
    
      The company options allows searching by company name in the provider base.
    
    Options:
      -t, --targetid INTEGER      Define a specific target ID from the database to
                                  use. Multiple options are allowed.
      -o, --organization INTEGER  Optionally specify organization for the profiles
      -n, --name INTEGER          Optionally specify name for the profiles
      -v, --version INTEGER       Optionally specify versionfor the profiles
      --help                      Show this message and exit.



.. _`Help Command Details`:lt
Help Command Details
====================


This section defines the help output for each smicli group and subcommand.


.. _`smicli repl --help`:lt
smicli repl --help
==================

::

    Usage: smicli repl [OPTIONS]
    
      Enter interactive (REPL) mode (default) and load any existing history
      file.
    
    Options:
      --help  Show this message and exit.



.. _`Help Command Details`:lt
Help Command Details
====================


This section defines the help output for each smicli group and subcommand.


.. _`smicli targets --help`:lt
smicli targets --help
=====================

::

    Usage: smicli targets [COMMAND-OPTIONS] COMMAND [ARGS]...
    
      Command group for managing targets data.
    
      This command group enables operations for viewing and management of data
      on the target providers as defined in a database.
    
      The targets database defines the providers to be pinged, tested, etc.
      including all information to access the provider and links to other data
      such as company, etc.
    
    Options:
      --help  Show this message and exit.
    
    Commands:
      disable  Disable a provider from scanning.
      fields   Display the names of fields in the providers...
      get      Get the details of a single record from the...
      info     get and display a list of classnames.
      list     Display the entries in the provider database.



.. _`Help Command Details`:lt
Help Command Details
====================


This section defines the help output for each smicli group and subcommand.


.. _`smicli targets disable --help`:lt
smicli targets disable --help
-----------------------------

::

    Usage: smicli targets disable [COMMAND-OPTIONS] TargetID
    
      Disable a provider from scanning.
    
    Options:
      -e, --enable  Enable the Target if it is disabled.
      --help        Show this message and exit.



.. _`Help Command Details`:lt
Help Command Details
====================


This section defines the help output for each smicli group and subcommand.


.. _`smicli targets fields --help`:lt
smicli targets fields --help
----------------------------

::

    Usage: smicli targets fields [COMMAND-OPTIONS]
    
      Display the names of fields in the providers base.
    
    Options:
      --help  Show this message and exit.



.. _`Help Command Details`:lt
Help Command Details
====================


This section defines the help output for each smicli group and subcommand.


.. _`smicli targets get --help`:lt
smicli targets get --help
-------------------------

::

    Usage: smicli targets get [COMMAND-OPTIONS] TargetID
    
      Get the details of a single record from the database and display.
    
    Options:
      --help  Show this message and exit.



.. _`Help Command Details`:lt
Help Command Details
====================


This section defines the help output for each smicli group and subcommand.


.. _`smicli targets info --help`:lt
smicli targets info --help
--------------------------

::

    Usage: smicli targets info [COMMAND-OPTIONS]
    
      get and display a list of classnames.
    
    Options:
      --help  Show this message and exit.



.. _`Help Command Details`:lt
Help Command Details
====================


This section defines the help output for each smicli group and subcommand.


.. _`smicli targets list --help`:lt
smicli targets list --help
--------------------------

::

    Usage: smicli targets list [COMMAND-OPTIONS]
    
      Display the entries in the provider database.
    
    Options:
      -f, --fields TEXT  Define specific fields for output. It always includes
                         TargetID. Ex. -f TargetID -f CompanyName Default: a
                         Standard list of fields
      -o, --order TEXT   sort by the defined field name. NOT IMPLEMENTED
      --help             Show this message and exit.


