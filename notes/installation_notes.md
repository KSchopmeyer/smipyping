# Installing smipyping for gathering regular server data #


The following is an overview of the steps to install smipyping in the
smi environment for gathering regular server status data into the history
file and for generating a regular report to users on the status of
the smi servers.

This differs from a typical user installation in that it also sets up the
cron jobs for regularly gathering data on the status of servers defined in
the database and automatically generating a report of results (the weekly
report).

Requirements today:
-------------------

Linux system, Both redhat and ubuntu have been tested.

## Installation steps ##


1. Be sure the following are installed:
   * python 2.7
   * a python virtual environment (This guide is written around virtualenv and
     virtualenvwrapper). You do not have to have a virtual environment but
     it makes working with python much simpler. We have generally worked with
     `virtualenv` and   `virtualenvwrapper` but there are a number of different
     virtual environment tools available today.
   * pip. Be sure pip is up-to-date with pip install -U pip. Note that pip
     is part of the standard python install on some environments but not on
     others
   * make, specifically GNU make.  This should be part of the core install on
     all Linux systems.
   * MySQL (version 5.7.x) - This is an extra install and the installation
   depends on the particular environment used. Most of the debian based
   environments include mysql (version 5.7.x) as part of the supported packages
   that can be installed simply by selecting the package manager and searching
   for the MySQL package.  However, the Redhat bases systems place this into a
   set of separately installable packages


2. Create a directory for the installation and clone smipyping from github

   $ mkdir smipypingtest

   $ git clone https://github.com/KSchopmeyer/smipyping.git

   We are downloading from github now but will eventually move to installing
   from PyPi. The clone downloads all of the components in the git repo, not
   just the pip installables so that it includes extra development tools and
   the test directories

3.  Create a virtual environment for the installation. With `virtualenv` and
    `virtualenvwrapper` the step are:

    a. Go to the directory containing the root of smipyping

       $ cd smipypingtest/smipyping

    b. Create the virtual environment (the following line uses
       `virtualenvwrapper`). The -a . options sets the current directory as
       the workspace for this virtual environment so that simply executing
       `workon smipypingtest` activated the virtual environment and also changes
       to the directory containing that version of the project.

       $ mkvirtualenv -a . smipypingtest

       This creates a virtual environment named smipypingtest and also sets the
       directory for that virtual environment to the current directory. This
       makes it easy with one statement (workon ...) to activate that virtual
       envrionment and also go to the project directory for that environment.

    c. Activate the new virtual environment

        $ workon smipypingtest

4.  Install and build smipyping. This step is required because we cloned the
    code into place.  When we change to pip install, it will no longer be
    necessary.

    a. Be sure you are in the directory defined in step 3.  The easiest way
       is with the cmd:

       $ workon smipypingtest

    b. Build the python environment:

       i.  Install development requirements for smipyping. This is important
           because pywbem requires at least one system level install.

           $ make develop

       ii. build and install the whole environment

           $ make clobber install build check build_doc

           or the all options which also runs the testsuite

           $ make clobber all

5. Install the database of targets, etc.  For the moment, that is msql and
   it is easiest to take it from an existing database.

   Given that you have access to a current dump of either the complete
   database for this project or the schema, the `mysql` command line utility
   can be used to install that database data to the running verion of mysql.

   $mysql -p -u [user] [database] < sqldump.sql


6. Set up  configuration file (default smicli.ini) to define the database set
   up in 4 above. with mysql this requires knowing the database location,
   database name (our default is SMIStatus, mysql user, and mysql password).
   For example, the following lines define a local MySQL database for smicli:

		[mysql]
		#   Name of the database in the mysql database host.  This db must be
		#   compatible with the field requirements of smipyping
		#
		database = SMIStatus
		#
		# Logon credentials for the mysql database.
		#
		user = <user name for mysql>
		password = ********

	The following defines a remote MySQL database:

        [mysql]
        host = 10.1.134.124
        database = SMIStatus
        user = root
        password = *********

7. Test to be sure smicli runs. The following are samples that will test both
   the access to the database and to the target servers:

       $ smicli -h
       $ smicli targets list
       $ smicli cimping all

8. Test to see if the the reports are generated correctly:

   a. Request cimping report. This accesses all the servers and determines
      general status

        $ smicli cimping all

   b. Request weekly report This generates the weekly report:

        $ smicli weekly
        $ smicli -o html weekly

9. Create the scripts and crontab to run these reports regularly

  The following examples are linux based and assume that crontab is used
  to kick off the data capture and report generation.

  The following scripts are required.

    a. Script to run cimping on a regular basis (ex. 30 min) and save the
       results to the history file

       The command is:

         $ smicli cimping all -s

    b. Script to run the weekly report, save it, and send it to the group

       The command to generate the report is `cimping history weekly`

       The script generates the report, sends the mail and saves the
       script with date tag for the future.

## Scripts and crontab ##

Crontab is used to execute two tasks with smicli on a regular basis.

1. Add status data to the database, this adds the status of each documented
   target to the database in the `pings` table.

   The command that executes this is:

     $ smicli cimping all -s

   This command executes a simping on all the servers in the targets table and
   enabled and (because the -s option is included) appends the results to the
   pings table.

   Typically this is executed every 30 minutes

2. Automatically generate the regular status report (ex. the weekly report)

   This subcommand generates a report on the overall recent and historical
   status of each server. Generally this is executed once a week at a defined
   time and distributed to a the plugfest members.

   The smicli command to generate this report is:

       $smicli -o html history weekly

    Which generates the report as an html output.

    Today, sending the email is a separate piece of code (pysendmail that is
    in the tools directory.)
### General information on example scripts ###

Crontab does not help much in establishing an environment to execute a script
so that, for example, the default shell may be sh, not bash, there is no user
setup, etc.  Unless smipyping is installed for root, these components should be
setup to allow activation of the python virtual environment containing
the smipyping being used

The scripts below are based on smipyping being in a python virtual environment
defined by virtualenv and virtualenvwrapper.  This works for python 2.7 and
allows both easy access from the command line (workon <env name>) and
activation of the environment via crontab.  Other virtual envrionments will
require a di

The combination of the crontab entrys and the scripts sets the correct user,
executes the bash profile and bashrc for that user and then executes the
script which first activates the virtual environment and then executes the
smicli command itself.

HOWEVER, to activate the virtual environment through crontab with virtualenv
and virtuaenvwrapper you must make one change	 in the environment, set the file
activate in the environment to executable.

    $ cd /.virtualenvs/$WORKON_NAME/bin/activate
    $ chmod +x activate

TODO: There may be other ways to activate this particular virtual environment
mechanism but this works for now.


### Script to generate cimping information and insert into history ###

The process of regularly adding history data to the db is controlled by a
scheduler such as the cron scheduler in linux.

The following scripts  set up the virtual environment, change to the directory
for that environment, and executes the smicli command.That can be removed when
the environment is stable

NOTE: The -s option is critical as that activates insertion of the results of
the cimping command into the history table.

    #!/bin/bash
    CRONOUT=$HOME/smiclipingcrounout.txt

    # setup virtual environment. This varies by virtual env tool used.
    # To set up when tool set is virtualenv and  virtualenvwrapper you need to
    # set the activate script to executable. Then you call that script to
    # activate the particular environment
    WORKON_NAME=smicliprod
    VIRTUALENV=~/smipypingprod/smipyping
    source ~/.virtualenvs/$WORKON_NAME/bin/activate
    cd $VIRTUALENV
    # smipypingprod/smipyping
    which smicli >$CRONOUT
    # test that smicli is installed
    smicli -h >>$CRONOUT
    RESULT=$?
    if [ $RESULT -eq 0 ]; then
      echo smicli -h success >>$CRONOUT
    else
      exit smicli -h Bad: $RESULT >>$CRONOUT
    fi

    # execute the smicli command to ping the servers
    smicli cimping all -s >>$CRONOUT

### Script to generate weekly report ###

    #!/bin/bash
    CRONOUT=$HOME/smicliweeklycrounout.txt

    # setup virtual environment. This varies by virtual env tool used.
    # To set up when tool set is virtualenv and  virtualenvwrapper you need to
    # set the activate script to executable. Then you call that script to
    # activate the particular environment
    echo "start smicliweekly script" >$CRONOUT
    REPORT_NAME=$HOME/weekly.html
    REPORT_ARCHIVE=$HOME/weekly
    WORKON_NAME=smicliprod
    VIRTUALENV=~/smipypingprod/smipyping
    source ~/.virtualenvs/$WORKON_NAME/bin/activate
    cd $VIRTUALENV

    smicli -o html history weekly >$REPORT_NAME
    NOW=$(date +"%m_%d_%Y")
    SUBJECT="SMLAB Weekly Provider Report for $NOW by smipyping"
    pysendmail -t smi_lab@snia.org -f k.schopmeyer@swbell.net -s "$SUBJECT" -F $REPORT_NAME -vvvv

    pysendmail -t karl.schopmeyer@gmail.com -f k.schopmeyer@swbell.net -s "$SUBJECT" -F $REPORT_NAME -v

    cp $REPORT_NAME $REPORT_ARCHIVE/week_$NOW.html
    # NOTE: This does not delete old reports

### Sample crontab to execute these scripts

    SHELL=/bin/bash
    0,30 * * * * sudo -u kschopmeyer -i bash -c '. $HOME/.bash_profile; . $HOME/.bashrc; $HOME/bin/smicliping.sh; > $HOME/smicliping.log'

    # Weekly Report Generate once a week, Sunday Night at 23:35 after last ping:w
    35 23 * * SUN sudo -u kschopmeyer -i bash -c '. $HOME/.bash_profile; . $HOME/.bashrc; $HOME/bin/smicliweekly.sh; > $HOME/smiweekly.log'
