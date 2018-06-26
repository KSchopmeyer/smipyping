
.. _`WBEM Server database`:

smipyping database
==================

Because smipyping operates on a number of WBEM Servers at the same time
and also maintains status of these servers over time. It depends on a database
to contain information about the WBEM Servers, the WBEM Server owners, and
the results of testing these servers.

smipyping uses a database in one of serveral forms (either csv files for
very simple installations or a sql database for more complex installations).


The database contains the following tables:

1. Companies - A table of the companies responsibile for the servers. This
   relates each company to one or more Targets
2. Targets - A table of the WBEM Servers to be tested with smipyping.  This includes key information
   about each server that cannot be derived from knowing only the host name
   of the server including passwords. Any information that can be derived
   from the servers themselves is normally not maintained in this table.
3. Users - A table of users primarily as a means of contacting the personnel
   responsible for each server and as a desination for reports. This table
   relates each user to an entry in the companies table.
4. Pings - A table that is augmented when status checks are run on
   the servers. It provides historical information on the status of
   those checks for each server (up/down, etc.). This table is updated when
   the command ``smicli cimping all --saveresult`` is run adding the status
   of each server test to the pings table.  Each status entry identifies
   the target, time, and status returned from the ping.
5. Notifications - A table showing what notifications of server status
   changes have been sent.


We intend to make this database as general but as simple as possible however,
for the moment is can be either a simple csv file database or a more general
sql database using mysql.

Normally the database is maintained outside of smipyping using tools for that
database. Thus for csv files, an editor suffices if the csv database form
is used.

However, for the mysql database a tool such as the mysql workbench is useful
to be able to add entries, delete entries, make modifications, etc.

We have included the capability to update, add, delete, and clean the tables for
a number of these tables directly from smicli.

Database structure
------------------

The following diagram shows the interaction between the different tables
in the database.

::

    +----------+
    | Programs |
    | Table    |    +--------------+
    +----------+    |   Targets    |
                    |   Table      <------+ targetID
                    +----+---------+      |
                         | CompanyID      |
    +----------+   +-----v-------+   +----+------+
    |          |   |             |   |           |
    |   Users  +--^+  Companies  |   |  Pings    |
    |   Table  |   |  Table      |   |  Table    |
    |          |   |             |   |           |
    +----------+   +-------------+   +-----------+


Alternative Databases
---------------------

Today we do not test with any alternative databases.  We are looking at
sqllite for the next release partly because it is integrated into python.

We can run with a simple csv database for the targets table.  However, this has
many limitations including the fact that it cannot create entries in a
pings table today so it is good for current status reports but does not
save history.

Database schema
---------------

MySQL Database
^^^^^^^^^^^^^^

Although the schema may change with new versions of smipyping, the following
is the schema for smipyping version 0.7.0::

    --
    -- Table structure for table `Companies`
    --
    CREATE TABLE IF NOT EXISTS `Companies` (
      `CompanyID` int(11) unsigned NOT NULL AUTO_INCREMENT,
      `CompanyName` varchar(30) NOT NULL,
      PRIMARY KEY (`CompanyID`)
    ) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=34 ;

    --
    -- Table structure for table `LastScan`
    --

    CREATE TABLE IF NOT EXISTS `LastScan` (
      `ScanID` int(11) unsigned NOT NULL AUTO_INCREMENT,
      `LastScan` datetime NOT NULL,
      PRIMARY KEY (`ScanID`)
    ) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=2 ;

    --
    -- Table structure for table `Notifications`
    --

    CREATE TABLE IF NOT EXISTS `Notifications` (
      `NotifyID` int(11) unsigned NOT NULL AUTO_INCREMENT,
      `NotifyTime` datetime NOT NULL,
      `UserID` varchar(20) NOT NULL,
      `TargetID` int(11) NOT NULL,
      `Message` varchar(100) NOT NULL,
      PRIMARY KEY (`NotifyID`)
    ) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=55522 ;

    --
    -- Table structure for table `Pings`
    --

    CREATE TABLE IF NOT EXISTS `Pings` (
      `PingID` int(11) unsigned NOT NULL AUTO_INCREMENT,
      `TargetID` int(11) unsigned NOT NULL,
      `Timestamp` datetime NOT NULL,
      `Status` varchar(255) NOT NULL,
      PRIMARY KEY (`PingID`)

    --
    -- Table structure for table `PreviousScans`
    --

    CREATE TABLE IF NOT EXISTS `PreviousScans` (
      `ScanID` int(11) unsigned NOT NULL AUTO_INCREMENT,
      `TimeStamp` datetime NOT NULL,
      PRIMARY KEY (`ScanID`)
    ) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

    --
    -- Table structure for table `Program`
    --

    CREATE TABLE IF NOT EXISTS `Program` (
      `ProgramID` int(11) unsigned NOT NULL AUTO_INCREMENT,
      `ProgramName` varchar(15) NOT NULL,
      `StartDate` date NOT NULL,
      `EndDate` date NOT NULL,
      PRIMARY KEY (`ProgramID`)
    ) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=13 ;


    --
    -- Table structure for table `Targets`
    --

    CREATE TABLE IF NOT EXISTS `Targets` (
      `TargetID` int(11) unsigned NOT NULL AUTO_INCREMENT,
      `IPAddress` varchar(15) NOT NULL,
      `CompanyID` int(11) unsigned NOT NULL,
      `Namespace` varchar(30) NOT NULL,
      `SMIVersion` varchar(15) DEFAULT NULL,
      `Product` varchar(30) NOT NULL,
      `Principal` varchar(30) NOT NULL,
      `Credential` varchar(30) NOT NULL,
      `CimomVersion` varchar(30) DEFAULT NULL,
      `InteropNamespace` varchar(30) DEFAULT NULL,
      `Notify` enum('Enabled','Disabled') NOT NULL DEFAULT 'Disabled',
      `NotifyUsers` varchar(12) DEFAULT NULL,
      `ScanEnabled` enum('Enabled','Disabled') NOT NULL DEFAULT 'Enabled',
      `Protocol` varchar(10) NOT NULL DEFAULT 'http',
      `Port` varchar(10) NOT NULL,
      PRIMARY KEY (`TargetID`)
    ) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=123 ;


    --
    -- Table structure for table `Users`
    --

    CREATE TABLE IF NOT EXISTS `Users` (
      `UserID` int(11) unsigned NOT NULL AUTO_INCREMENT,
      `Firstname` varchar(30) NOT NULL,
      `Lastname` varchar(30) NOT NULL,
      `Email` varchar(50) NOT NULL,
      `CompanyID` int(11) NOT NULL,
      `Active` enum('Active','Inactive') NOT NULL,
      `Notify` enum('Enabled','Disabled') NOT NULL,
      PRIMARY KEY (`UserID`)
    ) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=81 ;

CSV database

The schema for a csv database is simply the column names as shown below.

    TargetID,CompanyName,Namespace,SMIVersion,Product,Principal,Credential,CimomVersion,IPAddress,InteropNamespace,Protocol,Port,ScanEnabled

This database uses the CompanyName directly rather than an ID to point to
a companies table.

The following is an example of a row in a csv table:

    01,Inova,root/cimv2,,OpenPegasus,,,OpenPegasus,mypw,interop,http,5988,Enabled
