
.. _`Change log`:

Change log
==========

.. ifconfig:: version.endswith('dev0')

.. # Reenable the following lines when working on a development version:

This version of the documentation is development version |version| and
contains the `master` branch up to this commit:

.. git_changelog::
   :revisions: 1


smipyping v0.6.0
----------------

Released: 2017-03-16

This is the first public version of this code.  As such, the following
categories do not apply.

Deprecations
^^^^^^^^^^^^


Known Issues
^^^^^^^^^^^^

* sqllite is not really tested at this point.  There are issues between the
  mysql database and sqllite in converting the database.

* Documentation concerning setup and use of the databases is incomplete.

* The csv database was removed from this repository and will be supplied
  separately because of security issues concerning information about the
  equipment in the center.

Enhancements
^^^^^^^^^^^^

Bug fixes
^^^^^^^^^
