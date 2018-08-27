
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
                                      mysql.
      -l, --log COMP=LEVEL,...        Set a component to a log level (COMP: [all|c
                                      li|pywbem|pywbemapi|pywbemhttp|api|groups],
                                      LEVEL: [critical|error|warning|info|debug],
                                      Default: all=error).
      --log-dest [file|stderr|none]   Log destination for this command (Default:
                                      file).
      -o, --output-format [table|plain|simple|grid|psql|rst|mediawiki|html]
                                      Output format (Default: simple). smicli may
                                      override the format choice depending on the
                                      operation since not all formats apply to all
                                      output data types.
      -v, --verbose                   Display extra information about the
                                      processing.
      --version                       Show the version of this command and exit.
      -h, --help                      Show this message and exit.

    Commands:
      cimping        Command group to do cimping.
      companies      Command group for Companies table.
      explorer       Command group to explore providers.
      help           Show help message for interactive mode.
      history        Command group manages history(pings) table.
      notifications  Command group for notifications table.
      programs       Command group to handle programs table.
      provider       Command group for provider operations.
      repl           Enter interactive (REPL) mode (default).
      sweep          Command group to sweep for servers.
      targets        Command group for managing targets data.
      users          Command group to handle users table.


.. _`smicli cimping --help`:

smicli cimping --help
---------------------



The following defines the help output for the `smicli cimping --help` subcommand


::

    Usage: smicli cimping [COMMAND-OPTIONS] COMMAND [ARGS]...

      Command group to do cimping.

      A cimping executes a system level ping (optional) and then tries to create
      a connection to the target WBEM serve and execute a simple WBEM operation.

      This generally tests both the existence of the WBEM server with the ping
      and the a ability to make a WBEM connection and get valid results from the
      WBEM server. The operation executed is EnumerateClasses on one of the
      known namespaces

      This allows target WBEM servers to be defined in a number of ways
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

      Creates a table of results and optionally logs status of each target in
      the Pings table (--saveresult option).

      This subcommand also compares the results with previous results in the
      pings table and marks any targets that have changed with an asterik ("*")
      as a flag.

      ex. smicli cimping all

    Options:
      -t, --timeout INTEGER  Timeout in sec for the operation. (Default: 10).
      --no-ping              Disable network ping of the wbem server before
                             executing the cim request. (Default: True).
      -s, --saveresult       Save the result of each cimping test of a wbem server
                             to the database Pings table for future analysis.
                             Saving the results creates an audit log record.
                             (Default: False).
      -d, --disabled         If set include disabled targets in the cimping scan.
                             (Default: False).
      -d, --debug            Set the debug parameter for the pywbem call. Displays
                             detailed information on the call and response.
                             (Default: False).
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
      -n, --namespace TEXT     Namespace for the operation. (Default: root/cimv2).
      -u, --user TEXT          Optional user name for the operation. (Default:
                               smilab).
      -p, --password TEXT      Optional password for the operation. (Default;
                               F00sb4ll).
      -t, --timeout INTEGER    Namespace for the operation. (Default: 10).
      --no-ping BOOLEAN        Disable network ping ofthe wbem server before
                               executing the cim request. (Default: True).
      -d--debug BOOLEAN        Set the debug parameter for the pywbem call.
                               Displays detailed information on the call and
                               response. (Default: False).
      -c--verify_cert BOOLEAN  Request that the client verify the server cert.
                               (Default: False).
      --certfile TEXT          Client certificate file for authenticating with the
                               WBEM server. If option specified the client
                               attempts to execute mutual authentication. Default:
                               Simple authentication).
      --keyfile TEXT           Client private key file for authenticating with the
                               WBEM server. Not required if private key is part of
                               the certfile option. Not allowed if no certfile
                               option. Default: No client key file. Client private
                               key should then be part  of the certfile).
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

      This test sets a cmd line exit code corresponding to the status of a given
      target WBEM Server.

      This subcommand will interactively let user select the TargetID if the
      --interactive mode is selected or "?" is entered for the TargetID.

      ex. smicli cimping 5

    Options:
      -t, --timeout INTEGER  Timeout in sec for the operation. (Default: 10).
      -i, --interactive      If set, presents list of targets to chose.
      --no-ping              Disable network ping of the wbem server before
                             executing the cim request. (Default: True).
      -d, --debug            Set the debug parameter for the pywbem call. Displays
                             detailed information on the call and response.
                             (Default: False).
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
      -t, --timeout INTEGER  Timeout in sec for the operation. (Default: 10).
      --no-ping              Disable network ping of the wbem server before
                             executing the cim request. (Default: True).
      -i, --interactive      If set, presents list of targets to chose.
      -d, --debug            Set the debug parameter for the pywbem call. Displays
                             detailed information on the call and response.
                             (Default: False).
      -h, --help             Show this message and exit.


.. _`smicli companies --help`:

smicli companies --help
-----------------------



The following defines the help output for the `smicli companies --help` subcommand


::

    Usage: smicli companies [COMMAND-OPTIONS] COMMAND [ARGS]...

      Command group for Companies table.

      Includes commands to view and modify the Companies table in the database.

    Options:
      -h, --help  Show this message and exit.

    Commands:
      add     Add a new company to the the company table.
      delete  Delete a company from the database.
      list    List companies in the database.
      modify  Modify company data in database.


.. _`smicli companies add --help`:

smicli companies add --help
^^^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli companies add --help` subcommand


::

    Usage: smicli companies add [COMMAND-OPTIONS]

      Add a new company to the the company table.

      Creates a new company with the defined company name.

    Options:
      -c, --companyname TEXT  Company name for company to add to table.
      -h, --help              Show this message and exit.


.. _`smicli companies delete --help`:

smicli companies delete --help
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli companies delete --help` subcommand


::

    Usage: smicli companies delete [COMMAND-OPTIONS] CompanyID

      Delete a company from the database.

      Delete the company defined by the subcommand argument from the database.

      smicli companies delete ?      # does select list to select company
      to delete from companies table

    Options:
      -i, --interactive  If set, presents list of users from which one can be
                         chosen.
      -n, --no-verify    Verify the deletion before deleting the user.
      -h, --help         Show this message and exit.


.. _`smicli companies list --help`:

smicli companies list --help
^^^^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli companies list --help` subcommand


::

    Usage: smicli companies list [COMMAND-OPTIONS]

      List companies in the database.

      List the parameters of companies in the company table of the database.

    Options:
      -h, --help  Show this message and exit.


.. _`smicli companies modify --help`:

smicli companies modify --help
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli companies modify --help` subcommand


::

    Usage: smicli companies modify [COMMAND-OPTIONS] CompanyID

      Modify company data in database.

      Modifies the company name in the company table of the database.

      ex. smicli companies modify 13 -c "NewCompany Name"

    Options:
      -c, --companyname TEXT  New company name(required).  [required]
      -i, --interactive       If set, presents list of users from which one can be
                              chosen.
      -n, --no-verify         Disable verification prompt before the modify is
                              executed.
      -h, --help              Show this message and exit.


.. _`smicli explorer --help`:

smicli explorer --help
----------------------



The following defines the help output for the `smicli explorer --help` subcommand


::

    Usage: smicli explorer [COMMAND-OPTIONS] COMMAND [ARGS]...

      Command group to explore providers.

      This group of commands provides the tools for general explore of all
      providers defined in the database.

      The explore queries the providers and generates information on their state
      and status including if active, namespaces, profiles, etc. It also
      normally generates a log of all activity.

      This information is generated by accessing the provider itself.

      These subcommands automatically validates selected data from the server
      against the database and creates an audit log entry for any changes. The
      fields currently tested are:

        * SMIVersion

    Options:
      -h, --help  Show this message and exit.

    Commands:
      all  Explore all targets in database.
      ids  Explore a list of target IDs.


.. _`smicli explorer all --help`:

smicli explorer all --help
^^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli explorer all --help` subcommand


::

    Usage: smicli explorer all [COMMAND-OPTIONS]

      Explore all targets in database.

      Execute the general explore operation on  some or all the providers in the
      database and generate a report on the results.

      This command explores the general characteristics of the server including:

        * Company - From the targets database

        * Product = From the targets database

        * SMI Profiles   - As defined by the server itself

        * Interop Namespace - Ad defined by the server

        * Status - General status (i.e. CIMPing status)

        * Time - Time to execute the tests

      General Server information

      It executes the server requests in parallel mode (multi-threaded) or by
      setting a command line options single thread (if for some reason there is
      an issue with the multithreading)

      It generates a report to the the defined output as a table with the
      formatting defined by the global format option. Default is thread the
      requests speeding up the explore significantly.

      There is an option to ping the server before executing the explore simply
      to speed up the process for servers that are completely not available. The
      default is to ping as the first step.

      ex: smicli explore all

    Options:
      --ping / --no-ping             Ping the the provider as initial step in
                                     test. Default: ping
      --thread / --no-thread         Run test multithreaded.  Much faster.
                                     Default: thread
      -i, --include-disabled         Include hosts marked disabled in the targets
                                     table.
      -d, --detail [full|brief|all]  Generate full or brief (fewer columns)
                                     report. Full report includes namespaces,
                                     SMI_profiles, etc. (Default: full
      -h, --help                     Show this message and exit.


.. _`smicli explorer ids --help`:

smicli explorer ids --help
^^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli explorer ids --help` subcommand


::

    Usage: smicli explorer ids [COMMAND-OPTIONS] TargetIDs

      Explore a list of target IDs.

      Execute the explorer on the providers defined by id.  Multiple ids may be
      supplied (ex. id 5 6 7)

      ex: smicli explorer ids 6 7 8

    Options:
      --ping / --no-ping             Ping the the provider as initial step in
                                     test. Default: ping
      --thread / --no-thread         Run test multithreaded.  Much faster.
                                     Default: thread
      -i, --interactive              If set, presents list of targets to chose.
                                     Entering "?"for id is equivalent
      -d, --detail [full|brief|all]  Generate full or brief (fewer columns) report
      -h, --help                     Show this message and exit.


.. _`smicli help --help`:

smicli help --help
------------------



The following defines the help output for the `smicli help --help` subcommand


::

    Usage: smicli help [OPTIONS]

      Show help message for interactive mode.

    Options:
      -h, --help  Show this message and exit.


.. _`smicli history --help`:

smicli history --help
---------------------



The following defines the help output for the `smicli history --help` subcommand


::

    Usage: smicli history [COMMAND-OPTIONS] COMMAND [ARGS]...

      Command group manages history(pings) table.

      The history command group processes the database pings table.

      The pings table maintains entries with the results of the ``cimping all
      -s`` subcommand.  Each history entry contains the target id, the timestamp
      for the test, and the results of the test.

      It includes commands to clean the pings table and also to create various
      reports and tables of the history of tests on the WBEM servers in the
      targets table that are stored in the Pings table.

      Because the pings table can be very large, there are subcommands to clean
      entries out of the table based on program id, dates, etc.

      Rather than a simple list subcommand this subcommand includes a number of
      reports to view the table for:

        - changes to status for particular targets.   - Consolidated history
        over time periods   - Snapshots of the full set of entries over periods
        of time.

    Options:
      -h, --help  Show this message and exit.

    Commands:
      delete    Delete records from history file.
      list      List history of pings in database.
      overview  Get overview of pings in database.
      timeline  Show history of status changes for IDs.
      weekly    Generate weekly report from ping history.


.. _`smicli history delete --help`:

smicli history delete --help
^^^^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli history delete --help` subcommand


::

    Usage: smicli history delete [COMMAND-OPTIONS]

      Delete records from history file.

      Delete records from the history file based on start date and end date
      options and the optional list of target ids provided.

      ex. smicli history delete --startdate 09/09/17 --endate 09/10/17

      Because this could accidently delete all history records, this command
      specifically requires that the user provide both the start date and either
      the enddate or number of days. It makes no assumptions about dates.

      It also requires verification before deleting any records.

    Options:
      -s, --startdate DATE        Start date for pings to be deleted. Format is
                                  dd/mm/yy  [required]
      -e, --enddate DATE          End date for pings to be deleted. Format is
                                  dd/mm/yy  [required]
      -n, --numberofdays INTEGER  Alternative to enddate. Number of days to report
                                  from startdate. "enddate" ignored if
                                  "numberofdays" set
      -t, --TargetID INTEGER      Optional targetID. If included, delete ping
                                  records only for the defined targetID. Otherwise
                                  all ping records in the defined time period are
                                  deleted.
      -h, --help                  Show this message and exit.


.. _`smicli history list --help`:

smicli history list --help
^^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli history list --help` subcommand


::

    Usage: smicli history list [COMMAND-OPTIONS]

      List history of pings in database.

      The listing may be filtered a date range with the --startdate, --enddate,
      and --numberofdays options.  It may also be filtered to only show a single
      target WBEM server from the targets table with the `--targetid` option

      The output of this subcommand is determined by the `--result` option which
      provides for:

        * `full` - all records defined by the input parameters

        * `status` - listing records by status (i.e. OK, etc.) and     count of
        records for that status

        * `%ok` - listing the percentage of records that have 'OK' status and
        the total number of ping records

        * `count` - count of records within the defined date/time range

    Options:
      -s, --startdate DATE            Start date for ping records included. Format
                                      is dd/mm/yy where dd and mm are zero padded
                                      (ex. 01) and year is without century (ex.
                                      17). Default is oldest record
      -e, --enddate DATE              End date for ping records included. Format
                                      is dd/mm/yy where dd and dm are zero padded
                                      (ex. 01) and year is without century (ex.
                                      17). Default is current datetime
      -n, --numberofdays INTEGER      Alternative to enddate. Number of days to
                                      report from startdate. "enddate" ignored if
                                      "numberofdays" set
      -t, --targetId TEXT             Get results only for the defined targetID.
                                      If the value is "?" a select list is
                                      provided to the console to select the target
                                      WBEM server from the targets table.
      -r [full|changes|status|%ok|count]
                                      Display history records or status info on
                                      records. "full" displays all records,
                                      "changes" displays records that change
                                      status, "status"(default) displays status
                                      summary by target. "%ok" reports percentage
                                      pings OK by Id and total count.
      -h, --help                      Show this message and exit.


.. _`smicli history overview --help`:

smicli history overview --help
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli history overview --help` subcommand


::

    Usage: smicli history overview [COMMAND-OPTIONS]

      Get overview of pings in database.

      This subcommand only shows the count of records and the oldest and newest
      record in the pings database, and the number of pings by program.

    Options:
      -h, --help  Show this message and exit.


.. _`smicli history timeline --help`:

smicli history timeline --help
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli history timeline --help` subcommand


::

    Usage: smicli history timeline [COMMAND-OPTIONS] TargetIDs

      Show history of status changes for IDs.

      Generates a report for the defined target IDs and the time period defined
      by the options of the historical status of the defined target ID. The
      --result option defines the report generated with options for 1) "full"
      full list of history records 2) summary status by target ID, or 3) "%OK"
      percentage of records that report OK and total records for the period by
      target ID.

    Options:
      -s, --startdate DATE            Start date for ping records included. Format
                                      is dd/mm/yy where dd and mm are zero padded
                                      (ex. 01) and year is without century (ex.
                                      17). Default is oldest record
      -e, --enddate DATE              End date for ping records included. Format
                                      is dd/mm/yy where dd and dm are zero padded
                                      (ex. 01) and year is without century (ex.
                                      17). Default  if neither `enddate` or
                                      `numberofdays` are defined is current
                                      datetime
      -n, --numberofdays INTEGER      Alternative to enddate. Number of days to
                                      report from startdate. "enddate" ignored if
                                      "numberofdays" set
      -r, --result [full|status|%ok]  "full" displays all records, "status"
                                      displays status summary by id. "%ok" reports
                                      percentage pings OK by Id and total count.
                                      Default="status".
      -h, --help                      Show this message and exit.


.. _`smicli history weekly --help`:

smicli history weekly --help
^^^^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli history weekly --help` subcommand


::

    Usage: smicli history weekly [COMMAND-OPTIONS]

      Generate weekly report from ping history.

      This subcommand generates a report on the status of each target id in the
      targets table filtered by the --date parameter. It generates a summary of
      the status for the current day, for the previous week and for the total
      program.

      The --date is optional. Normally the report is generated for the week
      ending at the time the report is generated but the --date pararameter
      allows the report to be generated for previous dates.

      This report includes percentage OK for each target for today, this week,
      and the program and overall information on the target (company, product,
      SMIversion, contacts.)

    Options:
      -d, --date DATE   Optional date to be used as basis for report in form
                        dd/mm/yy. Default is today. This option allows reports to
                        be generated for previous periods.
      -o, --order TEXT  Sort order of the columns for the report output.  This can
                        be any of the column headers (case independent). Default:
                        Company
      -h, --help        Show this message and exit.


.. _`smicli notifications --help`:

smicli notifications --help
---------------------------



The following defines the help output for the `smicli notifications --help` subcommand


::

    Usage: smicli notifications [COMMAND-OPTIONS] COMMAND [ARGS]...

      Command group for notifications table.

      Includes commands to list and modify the Companies table in the database.

      This is largely an inernal table that keeps track of notifications make
      There is nothing to be done except to list notifications made and to clean
      up the table.

    Options:
      -h, --help  Show this message and exit.

    Commands:
      delete  Delete records from notifications file.
      list    List Notifications in the database.
      stats   Get stats on pings in database.


.. _`smicli notifications delete --help`:

smicli notifications delete --help
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli notifications delete --help` subcommand


::

    Usage: smicli notifications delete [COMMAND-OPTIONS]

      Delete records from notifications file.

      Delete records from the notifications file based on start date and end
      date options and the optional list of target ids provided.

      ex. smicli notifications delete --startdate 09/09/17 --endate 09/10/17

      Because this could accidently delete all history records, this command
      specifically requires that the user provide both the start date and either
      the enddate or number of days. It makes no assumptions about dates.

      It also requires verification before deleting any records.

    Options:
      -s, --startdate DATE        Start date for pings to be deleted. Format is
                                  dd/mm/yy  [required]
      -e, --enddate DATE          End date for pings to be deleted. Format is
                                  dd/mm/yy  [required]
      -n, --numberofdays INTEGER  Alternative to enddate. Number of days to report
                                  from startdate. "enddate" ignored if
                                  "numberofdays" set
      -t, --TargetID INTEGER      Optional targetID. If included, delete ping
                                  records only for the defined targetID. Otherwise
                                  all ping records in the defined time period are
                                  deleted.
      -h, --help                  Show this message and exit.


.. _`smicli notifications list --help`:

smicli notifications list --help
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli notifications list --help` subcommand


::

    Usage: smicli notifications list [COMMAND-OPTIONS]

      List Notifications in the database.

      List notifications for a date range and optionally a company or user.

    Options:
      -i, --targetIDs INTEGER     Optional list of ids. If not supplied, all ids
                                  are used.
      -s, --startdate DATE        Start date for ping records included. Format is
                                  dd/mm/yy where dd and mm are zero padded (ex.
                                  01) and year is without century (ex. 17).
                                  Default is oldest record
      -e, --enddate DATE          End date for ping records included. Format is
                                  dd/mm/yy where dd and dm are zero padded (ex.
                                  01) and year is without century (ex. 17).
                                  Default is current datetime
      -n, --numberofdays INTEGER  Alternative to enddate. Number of days to report
                                  from startdate. "enddate" ignored if
                                  "numberofdays" set
      -u, --UserId INTEGER        Get results only for the defined userID
      -S--summary                 If set only a summary is generated.
      -h, --help                  Show this message and exit.


.. _`smicli notifications stats --help`:

smicli notifications stats --help
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli notifications stats --help` subcommand


::

    Usage: smicli notifications stats [COMMAND-OPTIONS]

      Get stats on pings in database.

      This subcommand only shows the count of records and the oldest and newest
      record in the pings database

      TODO we need to grow this output to more statistical information

    Options:
      -h, --help  Show this message and exit.


.. _`smicli programs --help`:

smicli programs --help
----------------------



The following defines the help output for the `smicli programs --help` subcommand


::

    Usage: smicli programs [COMMAND-OPTIONS] COMMAND [ARGS]...

      Command group to handle programs table.

      The programs table defines programs in terms of start and end dates so
      that other commands can use specific programs to manage their tables.
      Normally a program is one year long and includes it start date, end date,
      and a program name.

      There are subcommands to create,modify, delete program entries and a list
      command that shows all entries in the table.

    Options:
      -h, --help  Show this message and exit.

    Commands:
      add      Add new program to the database.
      current  Get info on current program.
      delete   Delete a program from the database.
      list     List programs in the database.


.. _`smicli programs add --help`:

smicli programs add --help
^^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli programs add --help` subcommand


::

    Usage: smicli programs add [COMMAND-OPTIONS]

      Add new program to the database.

    Options:
      -s, --startdate DATE    Start date for program. Format is dd/mm/yy where dd
                              and mm are zero padded (ex. 01) and year is without
                              century (ex. 17). This option is optional and if not
                              supplied the day after the end of the latest program
                              will be selected.
      -e, --enddate DATE      End date for program. Format is dd/mm/yy where dd
                              and mm are zero padded (ex. 01) and year is without
                              century (ex. 17). This field is optional and if not
                              defined on the command line 12 montsh - 1 day after
                              the start date will be used as the end date.
      -p, --programname TEXT  Descriptive name for program  [required]
      -h, --help              Show this message and exit.


.. _`smicli programs current --help`:

smicli programs current --help
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli programs current --help` subcommand


::

    Usage: smicli programs current [COMMAND-OPTIONS]

      Get info on current program.

      Search database for current program and display info on this program

    Options:
      -h, --help  Show this message and exit.


.. _`smicli programs delete --help`:

smicli programs delete --help
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli programs delete --help` subcommand


::

    Usage: smicli programs delete [COMMAND-OPTIONS] ProgramID

      Delete a program from the database.

      Delete the program defined by the subcommand argument from the database.
      The program to delete can be input directly, or selected from a list of
      programs by entering the character "?" as program ID or including the
      --interactive option.

    Options:
      -n, --no-verify    Do not verify the deletion before deleting the program.
      -i, --interactive  If set, presents list of programs from which one can be
                         chosen.
      -h, --help         Show this message and exit.


.. _`smicli programs list --help`:

smicli programs list --help
^^^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli programs list --help` subcommand


::

    Usage: smicli programs list [COMMAND-OPTIONS]

      List programs in the database.

    Options:
      -h, --help  Show this message and exit.


.. _`smicli provider --help`:

smicli provider --help
----------------------



The following defines the help output for the `smicli provider --help` subcommand


::

    Usage: smicli provider [COMMAND-OPTIONS] COMMAND [ARGS]...

      Command group for provider operations.

      This group of commands provides commands to query the providers defined by
      entries in the targets database.  This includes subcommands like ping, get
      basic info, get namespace info, get profile information. for individual
      providers.

      It differs from the explore group in that it provides tools to process
      individual providers in the database rather than try to explore the entire
      set of providers.  It also allows many more operations against the
      individual provider.

    Options:
      -h, --help  Show this message and exit.

    Commands:
      classes     Find all classes that match CLASSNAME.
      info        Display general info for the provider.
      interop     Display interop namespace for the provider.
      namespaces  Display public namespaces for the provider.
      ping        Ping the provider defined by targetid.
      profiles    Display registered profiles for provider.


.. _`smicli provider classes --help`:

smicli provider classes --help
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli provider classes --help` subcommand


::

    Usage: smicli provider classes [COMMAND-OPTIONS] TargetID

      Find all classes that match CLASSNAME.

      Find all class names in the namespace(s) of the defined
      proovider(WBEMServer) that match the CLASSNAME regular expression
      argument. The CLASSNAME argument may be either a complete classname or a
      regular expression that can be matched to one or more classnames. To limit
      the filter to a single classname, terminate the classname with $.

      The regular expression is anchored to the beginning of CLASSNAME and is
      case insensitive. Thus pywbem_ returns all classes that begin with
      PyWBEM_, pywbem_, etc.

      TODO: Add option to limit to single namespace

    Options:
      -i, --interactive               If set, presents list of targets to chose
                                      from.
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

    Usage: smicli provider info [COMMAND-OPTIONS] TargetID

      Display general info for the provider.

      The TargetID defines a single provider (See targets table). It may be
      picked from a list by entering ? or the --interactive option.

      The company options allows searching by company name in the provider base.

    Options:
      -i, --interactive  If set, presents list of targets to chose.
      -h, --help         Show this message and exit.


.. _`smicli provider interop --help`:

smicli provider interop --help
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli provider interop --help` subcommand


::

    Usage: smicli provider interop [COMMAND-OPTIONS] TargetID

      Display interop namespace for the provider.

      The TargetID defines a single provider (See targets table). It may be
      picked from a list by entering ? or the --interactive option.

      The company options allows searching by company name in the provider base.

    Options:
      -i, --interactive  If set, presents list of targets to chose.
      -h, --help         Show this message and exit.


.. _`smicli provider namespaces --help`:

smicli provider namespaces --help
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli provider namespaces --help` subcommand


::

    Usage: smicli provider namespaces [COMMAND-OPTIONS] TargetID

      Display public namespaces for the provider.

      The targetID for the provider can be entered directly or by using the
      interactive feature (entering "?" for the targetid or the --interactive
      option) to pick the provider from a list.

      ex. smicli provider namespaces ?

    Options:
      -i, --interactive  If set, presents list of targets to chose.
      -h, --help         Show this message and exit.


.. _`smicli provider ping --help`:

smicli provider ping --help
^^^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli provider ping --help` subcommand


::

    Usage: smicli provider ping [COMMAND-OPTIONS] TargetID

      Ping the provider defined by targetid.

      The TargetID defines a single provider (See targets table). It may be
      picked from a list by entering ? or the --interactive option.

      The company options allows searching by company name in the provider base.

    Options:
      -i, --interactive  If set, presents list of targets to chose.
      --timeout INTEGER  Timeout for the ping in seconds. (Default 2).
      -h, --help         Show this message and exit.


.. _`smicli provider profiles --help`:

smicli provider profiles --help
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli provider profiles --help` subcommand


::

    Usage: smicli provider profiles [COMMAND-OPTIONS] TargetID

      Display registered profiles for provider.

      The TargetID defines a single provider (See targets table). It may be
      picked from a list by entering ? or the --interactive option.

      The other options allow the selection of a subset of the profiles from the
      server by organization name, profile name, or profile version.

      ex. smicli provider profiles 4 -o SNIA

    Options:
      -i, --interactive        If set, presents list of targets to chose.
      -o, --organization TEXT  Optionally specify organization for the profiles
      -n, --name TEXT          Optionally specify name for the profiles
      -v, --version TEXT       Optionally specify versionfor the profiles
      -h, --help               Show this message and exit.


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
      get      Display details of single database target.
      info     Show target database config information
      list     Display the entries in the targets database.
      modify   Modify fields target database record.


.. _`smicli targets disable --help`:

smicli targets disable --help
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli targets disable --help` subcommand


::

    Usage: smicli targets disable [COMMAND-OPTIONS] TargetID

      Disable a provider from scanning. This changes the database.

      Use the `interactive` option  or "?" for target id to select the target
      from a list presented.

    Options:
      -e, --enable       Enable the Target if it is disabled.
      -i, --interactive  If set, presents list of targets to chose.
      -h, --help         Show this message and exit.


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

      Display details of single database target.

      Use the `interactive` option or "?" for Target ID to select the target
      from a list presented.

    Options:
      -i, --interactive  If set, presents list of targets to chose.
      -h, --help         Show this message and exit.


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
      -f, --fields FIELDNAME  Define specific fields for output. TargetID always
                              included. Multiple fields can be specified by
                              repeating the option. (Default: predefined list of
                              fields).
                              Enter: "-f ?" to interactively select
                              fields for display.
                              Ex. "-f TargetID -f CompanyName"
      -d, --disabled          Show disabled targets. Otherwise only targets that
                              are set enabled in the database are
                              shown.(Default:Do not show disabled targets).
      -o, --order FIELDNAME   Sort by the defined field name. Names are viewed
                              with the targets fields subcommand or "-o ?" to
                              interactively select field for sort
      -h, --help              Show this message and exit.


.. _`smicli targets modify --help`:

smicli targets modify --help
^^^^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli targets modify --help` subcommand


::

    Usage: smicli targets modify [COMMAND-OPTIONS] TargetID

      Modify fields target database record.

      This subcommand changes the database permanently. It normally allows the
      user to verify all changes before they are committed to the database. All
      changes to the database are recorded in the audit log.

      Use the `interactive` option or "?" for Target ID to select the target
      from a list presented.

      Not all fields are defined for modification. Today the fields of
      CompanyName, SMIVersion, CimomVersion, ScanEnabled, NotifyUsers Notify,
      and enable cannot be modified with this subcommand.

      TODO: Expand for other fields in the targets table.

    Options:
      -e, --enable                 Enable the Target if it is disabled.
      -i, --ipaddress TEXT         Modify the IP address if this option is
                                   included.
      -p, --port TEXT              Modify the port field. If 5988 or 5989, also
                                   sets the protocol field to https if 5989 or
                                   http if 5988
      -P, --principal TEXT         Modify the Principal field.
      -c, --credential TEXT        Modify the Credential field.
      -R, --product TEXT           Modify the the Product field.
      -I, --interopnamespace TEXT  Modify the InteropNamespace field.
      -n, --namespace TEXT         Modify the namespace field.
      -N, --no_verify              Disable verification prompt before the change
                                   is executed.
      -h, --help                   Show this message and exit.


.. _`smicli users --help`:

smicli users --help
-------------------



The following defines the help output for the `smicli users --help` subcommand


::

    Usage: smicli users [COMMAND-OPTIONS] COMMAND [ARGS]...

      Command group to handle users table.

      Includes subcommands to list entries in the users table in the database
      and to create, modify, delete specific entries.

    Options:
      -h, --help  Show this message and exit.

    Commands:
      activate  Activate or deactivate multiple users.
      add       Add a new user in the user table.
      delete    Delete a user from the database.
      fields    Display field names in targets database.
      list      List users in the database.
      modify    Modify fields of a user in the user database.


.. _`smicli users activate --help`:

smicli users activate --help
^^^^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli users activate --help` subcommand


::

    Usage: smicli users activate [COMMAND-OPTIONS] UserID

      Activate or deactivate multiple users.

      This sets the users defined by the userids argument to either active or
      inactive.  When a user is inactive they are no longer shown in tables that
      involve user information such as the weekly report.

      The users to be activated or deactivated may be specified by a) specific
      user ids, b) the interactive mode option, or c) using '?' as the user id
      argument which also initiates the interactive mode options.

      Each user selected activated separately and users already in the target
      state are bypassed. If the --no-verify option is not set each user to be
      changed causes a verification request before the change.

      Example:     smicli users ? --activate

    Options:
      --active / --inactive  Set the active/inactive state in the database for
                             this user. Default is to attempt set user to
                             inactive.
      -i, --interactive      If set, presents list of users from which one can be
                             chosen.
      -n, --no-verify        Disable verification prompt before the operation is
                             executed.
      -h, --help             Show this message and exit.


.. _`smicli users add --help`:

smicli users add --help
^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli users add --help` subcommand


::

    Usage: smicli users add [COMMAND-OPTIONS]

      Add a new user in the user table.

      Creates a new user with the defined parameters for the company defined by
      the required parameter companyID.

      Verification that the operation is correct is requested before the change
      is executed unless the `--no-verify' parameter is set.

    Options:
      -f, --firstname TEXT  User first name.  [required]
      -l, --lastname TEXT   User last name  [required]
      -e, --email TEXT      User email address.  [required]
      -c, --companyID TEXT  CompanyID for the company attached to this user. Enter
                            ? to use selection list to get company id  [required]
      --inactive            Set the active/inactive state in the database for this
                            user. An inactive user is ignored. Default is active
      --disable             Disable notifications in the database for this user.
                            Default is enabled
      -N, --no_verify       Disable verification prompt before the change is
                            executed.
      -h, --help            Show this message and exit.


.. _`smicli users delete --help`:

smicli users delete --help
^^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli users delete --help` subcommand


::

    Usage: smicli users delete [COMMAND-OPTIONS] UserID

      Delete a user from the database.

      Delete the program user by the subcommand argument from the database.

      The user to be deleted may be specified by a) specific user id, b) the
      interactive mode option, or c) using '?' as the user id argument which
      also initiates the interactive mode options

    Options:
      -n, --no-verify    Disable verification prompt before the delete is
                         executed.
      -i, --interactive  If set, presents list of users from which one can be
                         chosen.
      -h, --help         Show this message and exit.


.. _`smicli users fields --help`:

smicli users fields --help
^^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli users fields --help` subcommand


::

    Usage: smicli users fields [COMMAND-OPTIONS]

      Display field names in targets database.

    Options:
      -h, --help  Show this message and exit.


.. _`smicli users list --help`:

smicli users list --help
^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli users list --help` subcommand


::

    Usage: smicli users list [COMMAND-OPTIONS]

      List users in the database.

    Options:
      -f, --fields FIELDNAME  Define specific fields for output. UserID always
                              included. Multiple fields can be specified by
                              repeating the option. (Default: predefined list of
                              fields).
                              Enter: "-f ?" to interactively select
                              fields for display.
                              Ex. "-f UserID -f CompanyName"
      -d, --disabled          Show disabled tusers. Otherwise only users that are
                              set enabled in the database are shown.(Default:Do
                              not show disabled users).
      -o, --order FIELDNAME   Sort by the defined field name. Names are viewed
                              with the targets fields subcommand or "-o ?" to
                              interactively select field for sort
      -h, --help              Show this message and exit.


.. _`smicli users modify --help`:

smicli users modify --help
^^^^^^^^^^^^^^^^^^^^^^^^^^



The following defines the help output for the `smicli users modify --help` subcommand


::

    Usage: smicli users modify [COMMAND-OPTIONS] UserID

      Modify fields of a user in the user database.

      This allows modifications of the fields for a particular specified by the
      user id on input.

      The user to be modified may be specified by a) specific user id, b) the
      interactive mode option, or c) using '?' as the user id argument which
      also initiates the interactive mode options

      ex. smicli users modify 9 -n fred # changes the first name of the user
      with user id 9.

    Options:
      -f, --firstname TEXT     User first name.
      -l, --lastname TEXT      User last name
      -e, --email TEXT         User email address.
      -c, --CompanyID INTEGER  CompanyID for the company attached to this user
      --no_notifications       Disable the notify state in the database for this
                               user if this flag set.
      -n, --no-verify          Disable verification prompt before the change is
                               executed.
      -i, --interactive        If set, presents list of users from which one can
                               be chosen.
      -h, --help               Show this message and exit.

