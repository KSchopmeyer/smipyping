
.. _`smicli Help Command Details`:

smicli Help Command Details
===========================


This section defines the help output for each smicli command group and subcommand.



The following defines the help output for the `smicli  --help` subcommand


::

    Usage: smicli [GENERAL-OPTIONS] COMMAND [ARGS]...
    
      Command line script for smicli.  This script executes a number of
      subcommands to:
    
          * Explore one or more smi servers for basic WBEM information and
            additional information specific to SMI.
    
          * Manage a database that defines smi servers, users, company names
            and history. It supports two forms of the data base, sql database
            and csv file.
    
          * Sweep ranges of ip addresses and ports to find wbem servers.
    
    Options:
      -c, --config_file TEXT          Configuration file to use for config
                                      information.
      -d, --db_type [csv|mysql|sqlite]
                                      Database type. May be defined on cmd line,
                                      config file,  or through default. Default is
                                      csv.
      -l, --log_level TEXT            Optional option to enable logging for the
                                      level  defined, by the parameter. Choices
                                      are:  ['error', 'warning', 'info', 'debug']
      -o, --output-format [plain|simple|grid|html]
                                      Output format (Default: simple). pywbemcli
                                      may override the format choice depending on
                                      the operation since not all formats apply to
                                      all output data types.
      -v, --verbose                   Display extra information about the
                                      processing.
      --version                       Show the version of this command and exit.
      -h, --help                      Show this message and exit.
    
    Commands:
      cimping   Command group to do simpleping.
      explorer  Command group for general provider explore.
      help      Show help message for interactive mode.
      provider  Command group for simple provider operations.
      repl      Enter interactive (REPL) mode (default).
      sweep     Command group to sweep for servers.
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
    
        - Complete target identification (url, etc.) (host)
    
        - Target Id in the database.
    
        - All targets in the database.
    
      Simple ping is defined as opening a connection to a wbem server and
      executing a single command on that server, normally a getClass with a well
      known CIMClass.
    
    Options:
      -h, --help  Show this message and exit.
    
    Commands:
      all   CIMPing all enabled targets in database.
      host  cimping wbem server defined by hostname.
      id    Cimping one target from database.
      ids   Cimping a list of targets from database.



.. _`smicli cimping all --help`:

smicli cimping all --help
^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli cimping all --help` subcommand


::

    Usage: smicli cimping all [COMMAND-OPTIONS]
    
      CIMPing all enabled targets in database.
    
      Executes the ping on all enabledtargets in the targets table of the
      database.
    
      Creates a table of results and optionally logs status of each in the Pings
      table (saveresult option)
    
      ex. smicli cimping all
    
    Options:
      -t, --timeout INTEGER  Timeout in sec for the operation. (Default: 10.)
      --no-ping              Disable network ping of the wbem server before
                             executing the cim request. (Default: True.)
      -s, --saveresult       Save the result of each cimping test of a wbem server
                             to the database Pings table for future analysis.
                             (Default: False.
      -d, --debug            Set the debug parameter for the pywbem call. Displays
                             detailed information on the call and response.
                             (Default: False.)
      -h, --help             Show this message and exit.



.. _`smicli cimping host --help`:

smicli cimping host --help
^^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli cimping host --help` subcommand


::

    Usage: smicli cimping host [COMMAND-OPTIONS] HOST NAME
    
      cimping wbem server defined by hostname.
    
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
      -h, --help               Show this message and exit.



.. _`smicli cimping id --help`:

smicli cimping id --help
^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli cimping id --help` subcommand


::

    Usage: smicli cimping id [COMMAND-OPTIONS] TargetID
    
      Cimping  one target from database.
    
      Executes a simple ping against one target wbem servers in the target
      database and returns exit code in accord with response. Exits interactive
      mode and returns exit code corresponding to test result.
    
      This test can specifically be used to get a cmd line exit code
      corresponding to the status of a given target WBEM Server.
    
      ex. smicli cimping 5
    
    Options:
      -t, --timeout INTEGER  Timeout in sec for the operation. (Default: 10.)
      --no-ping              Disable network ping of the wbem server before
                             executing the cim request. (Default: True.)
      -d, --debug            Set the debug parameter for the pywbem call. Displays
                             detailed information on the call and response.
                             (Default: False.)
      -h, --help             Show this message and exit.



.. _`smicli cimping ids --help`:

smicli cimping ids --help
^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli cimping ids --help` subcommand


::

    Usage: smicli cimping ids [COMMAND-OPTIONS] TargetIDs
    
      Cimping a list of targets from database.
    
      Execute simple cim ping against the list of ids provided for target
      servers in the database defined by each id in the list of ids creates a
      table showing result.
    
      ex. smicli cimping ids 5 8 9
    
    Options:
      -t, --timeout INTEGER  Timeout in sec for the operation. (Default: 10.)
      --no-ping              Disable network ping of the wbem server before
                             executing the cim request. (Default: True.)
      -d, --debug            Set the debug parameter for the pywbem call. Displays
                             detailed information on the call and response.
                             (Default: False.)
      -h, --help             Show this message and exit.



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
      -h, --help  Show this message and exit.
    
    Commands:
      all  Execute the general explorer on the enabled...
      ids  Execute the general explorer on the providers...



.. _`smicli explorer all --help`:

smicli explorer all --help
^^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli explorer all --help` subcommand


::

    Usage: smicli explorer all [COMMAND-OPTIONS]
    
      Execute the general explorer on the enabled providers in the database
    
    Options:
      --ping / --no-ping         Ping the the provider as initial step in test.
                                 Default: ping
      --thread / --no-thread     Run test multithreaded.  Much faster. Default:
                                 thread
      -r, --report [full|brief]  Generate full or brief (fewer columns) report
      -h, --help                 Show this message and exit.



.. _`smicli explorer ids --help`:

smicli explorer ids --help
^^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli explorer ids --help` subcommand


::

    Usage: smicli explorer ids [COMMAND-OPTIONS] TargetIDs
    
      Execute the general explorer on the providers defined by id.  Multiple ids
      may be supplied (ex. id 5 6 7)
    
    Options:
      --ping / --no-ping         Ping the the provider as initial step in test.
                                 Default: ping
      --thread / --no-thread     Run test multithreaded.  Much faster. Default:
                                 thread
      -r, --report [full|brief]  Generate full or brief (fewer columns) report
      -h, --help                 Show this message and exit.



.. _`smicli help --help`:

smicli help --help
------------------



The following defines the help output for the `smicli help --help` subcommand


::

    Usage: smicli help [OPTIONS]
    
      Show help message for interactive mode.
    
    Options:
      -h, --help  Show this message and exit.



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
      -h, --help  Show this message and exit.
    
    Commands:
      classes     Find all classes that match CLASSNAME.
      info        Display the brand information for the...
      interop     Display the brand information for the...
      namespaces  Display the brand information for the...
      ping        Ping the provider defined by targetid.
      profiles    profile information The options include...



.. _`smicli provider classes --help`:

smicli provider classes --help
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli provider classes --help` subcommand


::

    Usage: smicli provider classes [COMMAND-OPTIONS]
    
      Find all classes that match CLASSNAME.
    
      Find all  class names in the namespace(s) of the defined WBEMServer that
      match the CLASSNAME regular expression argument. The CLASSNAME argument
      may be either a complete classname or a regular expression that can be
      matched to one or more classnames. To limit the filter to a single
      classname, terminate the classname with $.
    
      The regular expression is anchored to the beginning of CLASSNAME and is
      case insensitive. Thus pywbem_ returns all classes that begin with
      PyWBEM_, pywbem_, etc.
    
      The namespace option limits the search to the defined namespace.
    
    Options:
      -t, --targetid INTEGER          Define a specific target ID from the
                                      database to  use. Multiple options are
                                      allowed.
      -c, --classname CLASSNAME regex
                                      Regex that filters the classnames to return
                                      only those that match the regex. This is a
                                      case insensitive, anchored regex. Thus,
                                      "CIM_" returns all classnames that start
                                      with "CIM_". To return an exact classname
                                      append "$" to the classname
      -s, --summary                   Return only the count of classes in the
                                      namespace(s)
      -n, --namespace <name>          Namespace to use for this operation. If not
                                      defined all namespaces are used
      -h, --help                      Show this message and exit.



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
      -h, --help              Show this message and exit.



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
      -h, --help              Show this message and exit.



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
      -h, --help              Show this message and exit.



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
      -h, --help              Show this message and exit.



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
      -h, --help                  Show this message and exit.



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
      -h, --help  Show this message and exit.



.. _`smicli sweep --help`:

smicli sweep --help
-------------------



The following defines the help output for the `smicli sweep --help` subcommand


::

    Usage: smicli sweep [COMMAND-OPTIONS] COMMAND [ARGS]...
    
      Command group to sweep for servers.
    
      Sweeping for servers involves pinging in one form or another possible
      ip/port combinations to find open ports.
    
      This group sweeps servers in a defined range looking for open WBEMServers.
    
    Options:
      -h, --help  Show this message and exit.
    
    Commands:
      nets  Execute sweep on the ip/port combinations...
      todo  Execute sweep on the ip/port combinations...



.. _`smicli sweep nets --help`:

smicli sweep nets --help
^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli sweep nets --help` subcommand


::

    sweep_group
    Usage: smicli sweep nets [COMMAND-OPTIONS]
    
      Execute sweep on the ip/port combinations defined by the --subnet and
      --port options
    
    Options:
      -s, --subnet TEXT             IP subnets to scan (ex. 10.1.132). One subnet
                                    per option Each subnet string is itself a
                                    definition that consists of period separated
                                    octets that are used to create the individual
                                    ip addresses to be tested:   * Integers: Each
                                    integer is in the range 0-255       ex.
                                    10.1.2.9   * Octet range definition: A range
                                    expansion is in the      form: int-int which
                                    defines the mininum and maximum       values
                                    for that octet (ex 10.1.132-134) or   *
                                    Integer lists: A range list is in the form:
                                    int,int,int
                                         and defines the set of values
                                    for that octet. Missing octet definitions are
                                    expanded to the value range defined by the min
                                    and max octet value parameters All octets of
                                    the ip address can use any of the 3
                                    definitions.
                                    Examples: 10.1.132,134 expands to
                                    addresses in 10.1.132 and 10.1.134. where the
                                    last octet is the range 1 to 254  [required]
      -p, --port INTEGER RANGE      Port(s) to test. This argument may be define
                                    multiple  ports. Ex. -p 5988 -p 5989.
                                    Default=5989
      -t, --scantype [tcp|syn|all]  Set scan type: %s. Some scan types require
                                    privilege mode. (Default: tcp.)
      -m INTEGER RANGE              Minimum expanded value for any octet that is
                                    not specifically included in a net definition.
                                    Default = 1
      -M INTEGER RANGE              Maximum expanded value for any octet that is
                                    not specifically included in a net definition.
                                    Default = 254
      -D, --dryrun                  Display list of systems/ports to be scanned
                                    but do not  scan. This is a diagnostic tool
                                    (Default: False.)
      --no_threads                  Disable multithread scan.  This should only be
                                    used if there are issues with the multithread
                                    scan. It is MUCH  slower. (Default: False.)
      -h, --help                    Show this message and exit.



.. _`smicli sweep todo --help`:

smicli sweep todo --help
^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli sweep todo --help` subcommand


::

    sweep_group
    Usage: smicli sweep todo [COMMAND-OPTIONS]
    
      Execute sweep on the ip/port combinations defined by the --subnet and
      --port options
    
    Options:
      -s, --subnet TEXT     blah blah  [required]
      -D, --dryrun BOOLEAN  Set the debug parameter for the pywbem call. Displays
                            detailed information on the call and response.
                            (Default: False.
      -h, --help            Show this message and exit.



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
      -h, --help  Show this message and exit.
    
    Commands:
      disable  Disable a provider from scanning.
      fields   Display field names in targets database.
      get      display details of a single record from...
      info     Show target database config information
      list     Display the entries in the targets database.



.. _`smicli targets disable --help`:

smicli targets disable --help
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli targets disable --help` subcommand


::

    Usage: smicli targets disable [COMMAND-OPTIONS] TargetID
    
      Disable a provider from scanning. This changes the database.
    
    Options:
      -e, --enable  Enable the Target if it is disabled.
      -h, --help    Show this message and exit.



.. _`smicli targets fields --help`:

smicli targets fields --help
^^^^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli targets fields --help` subcommand


::

    Usage: smicli targets fields [COMMAND-OPTIONS]
    
      Display field names in targets database.
    
    Options:
      -h, --help  Show this message and exit.



.. _`smicli targets get --help`:

smicli targets get --help
^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli targets get --help` subcommand


::

    Usage: smicli targets get [COMMAND-OPTIONS] TargetID
    
      display details of a single record from Targets database.
    
    Options:
      -h, --help  Show this message and exit.



.. _`smicli targets info --help`:

smicli targets info --help
^^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli targets info --help` subcommand


::

    Usage: smicli targets info [COMMAND-OPTIONS]
    
      Show target database config information
    
    Options:
      -h, --help  Show this message and exit.



.. _`smicli targets list --help`:

smicli targets list --help
^^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli targets list --help` subcommand


::

    Usage: smicli targets list [COMMAND-OPTIONS]
    
      Display the entries in the targets database.
    
    Options:
      -f, --fields TEXT  Define specific fields for output. It always includes
                         TargetID. Ex. -f TargetID -f CompanyName Default: a
                         Standard list of fields
      -d, --disabled     Show disabled targets. Otherwise only targets that are
                         set enabled in the database are shown. (Default: False.
      -o, --order TEXT   sort by the defined field name. NOT IMPLEMENTED
      -h, --help         Show this message and exit.


