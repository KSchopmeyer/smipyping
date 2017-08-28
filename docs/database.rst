
.. _`WBEM Server database`:

smipyping database
==================

Because smipyping operates on a number of WBEM Servers at the same time
and also maintains status of these servers over time. It depends on a database
to contain information about the WBEM Servers, the WBEM Server owners, and
the the results of testing these servers.

For this is uses a database in one of serveral forms (either csv files for
very simple installations or a sql database for more complex installations).

The data base generally contains:

1. Companies - A table of the companies responsibile for the servers
2. Targets - A table of the WBEM Servers to be tested.  This includes key information
   about each server that cannot be derived from knowing only the host name
   of the server including passwords. Any information that can be derived
   from the servers themselves is normally not maintained in this table
3. Users - A table of users primarily as a means of contacting the personnel
   responsible for each server and as a desination for reports
4. Pings - A status table that is augmented when status checks are run on
   the servers and that provides historical information on the status of
   those checks for each server (up/down, etc.)
5. Notifications - TODO


We intend to make this database as general but as simple as possible however,
for the moment is can be either a simple csv file database or a more general
sql database using mysql.

Normally the database is maintained outside of smipyping using tools for that
database. Thus for csv files, an editor suffices.

However, for the mysql database a tool such as the mysql workbench is useful
to be able to add entries, delete entries, make modifications, etc.

Database structure
------------------

TODO

Alternative Databases
---------------------

TODO

Database parameter definitions
------------------------------

TODO
