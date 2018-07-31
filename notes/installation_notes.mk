# Installing smipyping for gathering regular server data #


The following is an overview of the steps to install smipyping in the
smi environment for gathering regular server status data into the history
file and for generating a regular report to users on the status of
the smi servers.

Requirements today:
-------------------

 Linux system, Both redhat and ubuntu have been tested.

## Installation steps ##


1. Be sure the following are installed:
   * python 2.7
   * a python virtual environment (This guide is written around virtualenv and
     virtualenvwrapper). You do not have to have the virtual environment but
     it makes working with python much simpler.
   * pip. Be sure pip is up-to-date with pip install -u pip
   * make
   * mysql

   TODO detailed install instructions for the above

2. Create a directory for the installation and download smipyping from github

   $ mkdir smipypingtest

   $ git clone https://github.com/KSchopmeyer/smipyping.git

   We are downloading from github now but will eventually move to installing
   from PyPi

3.  Create a virtual environment for the installation. With virtualenv and
    virtualenvwrapper the step are:

    $ cd smipypingtest/smipyping

    $ mkvirtualenv -a . smipypingtest

    $ workon smipypingtest

4.  Install smipyping

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
   TODO Finish this.

6. Set up  configuration file (default smicli.ini) to define the database set
   up in 4 above. with mysql this requires knowing the database location,
   database name (our default is SMIStatus, mysql user, and mysql password).
   For example, the following lines define a local mysql database  for smicli:

		[mysql]
		#   Name of the database in the mysql database host.  This db must be
		#   compatible with the field requirements of smipyping
		#
		database = SMIStatus
		#
		# Logon credentials for the mysql database.
		#
		user = root
		password = ********

	The following define a remote database:

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

8. Test to see if the the reports are generate correctly:

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

       The command to generate the report is cimping history weekly

       The script generates the report, sends the mail and saves the
       script with date tag for the future.

## Example Scripts and crontab ##

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
and virtuaenvwrapper you must make one change in the environment, set the file
activate in the environment to executable.

    $ cd /.virtualenvs/$WORKON_NAME/bin/activate
    $ chmod +x activate

TODO: There may be other ways to activate this particular virtual environment
mechanism but this works for now.


### Script to generate cimping information and insert into history ###

The following script sets up the virtual environment, changes to the
directory for that environment, and executes the smicli command. It generates
output to a file $CRONOUT as a diagnostic. That can be removed when the
environment is stable

NOTE: The -s option is critical as that activates insertation of the results
into the history table.

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
	smicli -h >>$CRONOUT
	RESULT=$?
	if [ $RESULT -eq 0 ]; then
	  echo smicli -h success >>$CRONOUT
	else
	  exit smicli -h Bad: $RESULT >>$CRONOUT
	fi
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
	# echo "Generate weekly report" >> $CRONOUT

	smicli -o html history weekly >$REPORT_NAME
	NOW=$(date +"%m_%d_%Y")
	# echo "move weekly report for " $NOW
	cp $REPORT_NAME $REPORT_ARCHIVE/week_$NOW.html
	# echo "weekly report in dir"
	# ls -ltr $HOME/weekly
	# TODO Delete old reports

### Sample crontab to execute these scripts

	SHELL=/bin/bash
	0,30 * * * * sudo -u kschopmeyer -i bash -c '. $HOME/.bash_profile; . $HOME/.bashrc; $HOME/bin/smicliping.sh; > $HOME/smicliping.log'
	#Test. generate daily at noon
	23 55 * * FRI sudo -u kschopmeyer -i bash -c '. $HOME/.bash_profile; . $HOME/.bashrc; $HOME/bin/smicliweekly.sh; > $HOME/smicliweekly.log'
