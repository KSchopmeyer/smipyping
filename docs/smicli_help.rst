
.. _`smicli Help Command Details`:

smicli Help Command Details
===========================


This section defines the help output for each smicli command group and subcommand.



The following defines the help output for the `smicli  --help` subcommand


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
      -l, --log_level TEXT            Optional option to enable logging for the
                                      level  defined, by the parameter. Choices
                                      are:  ['error', 'warning', 'info', 'debug']
      -v, --verbose                   Display extra information about the
                                      processing.
      --version                       Show the version of this command and exit.
      --help                          Show this message and exit.
    
    Commands:
      cimping   Command group to do simpleping.
      explorer  Command group for general provider explore.
      help      Show help message for interactive mode.
      provider  Command group for simple provider operations.
      repl      Enter interactive (REPL) mode (default).
      targets   Command group for managing targets data.



.. _`smicli cimping --help`:

smicli cimping --help
---------------------



The following defines the help output for the `smicli cimping --help` subcommand


::

    Usage: smicli cimping [COMMAND-OPTIONS] COMMAND [ARGS]...
    
      Command group to do simpleping.
    
      This command group executes a simple ping on the target defined by the
      subcommand.  This allows targets to be defined in a number of ways
      including:
    
        - Complete target identification (url, etc.)
    
        - Target Id in the database.
    
        - All targets in the database.
    
      Simple ping is defined as opening a connection to a wbem server and
      executing a single command on that server, normally a getClass with a well
      known CIMClass.
    
    Options:
      --help  Show this message and exit.
    
    Commands:
      host  Execute a cimping on the wbem server defined...
      id    Execute a simple cim ping against the target...



.. _`smicli cimping host --help`:

smicli cimping host --help
^^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli cimping host --help` subcommand


::

    Usage: smicli cimping host [COMMAND-OPTIONS] HOST NAME
    
      Execute a cimping on the wbem server defined by hostname.
    
         Host name or url of the WBEM server in this format:
    
               [{scheme}://]{host}[:{port}]
    
            - scheme: Defines the protocol to use;
    
               - "https" for HTTPs protocol
    
                - "http" for HTTP protocol.
    
              Default: "https".
    
            - host: Defines host name as follows:
    
                 - short or fully qualified DNS hostname,
    
                 - literal IPV4 address(dotted)
    
                 - literal IPV6 address (RFC 3986) with zone
    
                   identifier extensions(RFC 6874)
    
                   supporting "-" or %%25 for the delimiter.
    
            - port: Defines the WBEM server port to be used
    
              Defaults:
    
                 - HTTP  - 5988
    
                 - HTTPS - 5989
    
    Options:
      -n, --namespace TEXT     Namespace for the operation. (Default: root/cimv2.
      -u, --user TEXT          Optional user name for the operation. (Default:
                               smilab.
      -p, --password TEXT      Optional password for the operation. (Default;
                               F00sb4ll.
      -t, --timeout INTEGER    Namespace for the operation. (Default: 10.
      --no-ping BOOLEAN        Disable network ping ofthe wbem server before
                               executing the cim request. (Default: True.
      -d--debug BOOLEAN        Set the debug parameter for the pywbem call.
                               Displays detailed information on the call and
                               response. (Default: False.
      -c--verify_cert BOOLEAN  Request that the client verify the server cert.
                               (Default: False.
      --certfile TEXT          Client certificate file for authenticating with the
                               WBEM server. If option specified the client
                               attempts to execute mutual authentication. Default:
                               Simple authentication.
      --keyfile TEXT           Client private key file for authenticating with the
                               WBEM server. Not required if private key is part of
                               the certfile option. Not allowed if no certfile
                               option. Default: No client key file. Client private
                               key should then be part  of the certfile
      --help                   Show this message and exit.



.. _`smicli cimping id --help`:

smicli cimping id --help
^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli cimping id --help` subcommand


::

    Usage: smicli cimping id [COMMAND-OPTIONS] TargetID
    
      Execute a simple cim ping against the target id defined in the request
    
    Options:
      -t, --timeout INTEGER  Namespace for the operation. (Default: 10.
      --no-ping BOOLEAN      Disable network ping ofthe wbem server before
                             executing the cim request. (Default: True.
      -d--debug BOOLEAN      Set the debug parameter for the pywbem call. Displays
                             detailed information on the call and response.
                             (Default: False.
      --help                 Show this message and exit.



.. _`smicli explorer --help`:

smicli explorer --help
----------------------



The following defines the help output for the `smicli explorer --help` subcommand


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
      id   Execute the general explorer on the enabled...



.. _`smicli explorer all --help`:

smicli explorer all --help
^^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli explorer all --help` subcommand


::

    Usage: smicli explorer all [COMMAND-OPTIONS]
    
      Execute the general explorer on the enabled providers in the database
    
    Options:
      --ping / --no-ping      Ping the the provider as initial step in test.
                              Default: ping
      --thread / --no-thread  Run test multithreaded.  Much faster. Default:
                              thread
      --help                  Show this message and exit.



.. _`smicli explorer id --help`:

smicli explorer id --help
^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli explorer id --help` subcommand


::

    Usage: smicli explorer id [COMMAND-OPTIONS] TargetID
    
      Execute the general explorer on the enabled providers in the database
    
    Options:
      --ping / --no-ping      Ping the the provider as initial step in test.
                              Default: ping
      --thread / --no-thread  Run test multithreaded.  Much faster. Default:
                              thread
      --help                  Show this message and exit.



.. _`smicli help --help`:

smicli help --help
------------------



The following defines the help output for the `smicli help --help` subcommand


::

    Usage: smicli help [OPTIONS]
    
      Show help message for interactive mode.
    
    Options:
      --help  Show this message and exit.



.. _`smicli provider --help`:

smicli provider --help
----------------------



The following defines the help output for the `smicli provider --help` subcommand


::

    Usage: smicli provider [COMMAND-OPTIONS] COMMAND [ARGS]...
    
      Command group for simple provider operations.
    
      This group of commands provides commands to query the providers defined by
      entries in the targets database.  This includes commands like ping, get
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



.. _`smicli provider info --help`:

smicli provider info --help
^^^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli provider info --help` subcommand


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



.. _`smicli provider interop --help`:

smicli provider interop --help
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli provider interop --help` subcommand


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



.. _`smicli provider namespaces --help`:

smicli provider namespaces --help
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli provider namespaces --help` subcommand


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



.. _`smicli provider ping --help`:

smicli provider ping --help
^^^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli provider ping --help` subcommand


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



.. _`smicli provider profiles --help`:

smicli provider profiles --help
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli provider profiles --help` subcommand


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



.. _`smicli repl --help`:

smicli repl --help
------------------



The following defines the help output for the `smicli repl --help` subcommand


::

    Usage: smicli repl [OPTIONS]
    
      Enter interactive (REPL) mode (default).
    
      This subcommand enters the interactive mode where subcommands can be
      executed without exiting the progarm and loads any existing command
      history file.
    
    Options:
      --help  Show this message and exit.



.. _`smicli targets --help`:

smicli targets --help
---------------------



The following defines the help output for the `smicli targets --help` subcommand


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



.. _`smicli targets disable --help`:

smicli targets disable --help
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli targets disable --help` subcommand


::

    Usage: smicli targets disable [COMMAND-OPTIONS] TargetID
    
      Disable a provider from scanning.
    
    Options:
      -e, --enable  Enable the Target if it is disabled.
      --help        Show this message and exit.



.. _`smicli targets fields --help`:

smicli targets fields --help
^^^^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli targets fields --help` subcommand


::

    Usage: smicli targets fields [COMMAND-OPTIONS]
    
      Display the names of fields in the providers base.
    
    Options:
      --help  Show this message and exit.



.. _`smicli targets get --help`:

smicli targets get --help
^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli targets get --help` subcommand


::

    Usage: smicli targets get [COMMAND-OPTIONS] TargetID
    
      Get the details of a single record from the database and display.
    
    Options:
      --help  Show this message and exit.



.. _`smicli targets info --help`:

smicli targets info --help
^^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli targets info --help` subcommand


::

    Usage: smicli targets info [COMMAND-OPTIONS]
    
      get and display a list of classnames.
    
    Options:
      --help  Show this message and exit.



.. _`smicli targets list --help`:

smicli targets list --help
^^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli targets list --help` subcommand


::

    Usage: smicli targets list [COMMAND-OPTIONS]
    
      Display the entries in the provider database.
    
    Options:
      -f, --fields TEXT  Define specific fields for output. It always includes
                         TargetID. Ex. -f TargetID -f CompanyName Default: a
                         Standard list of fields
      -o, --order TEXT   sort by the defined field name. NOT IMPLEMENTED
      --help             Show this message and exit.


