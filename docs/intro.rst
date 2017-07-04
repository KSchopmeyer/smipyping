
.. _`Introduction`:

Introduction
============

.. _`Functionality`:

Functionality
-------------

This python package provides the functionality to maintain information on the
status of a number of servers in a WBEM Server environment and to explore
the details of the WBEM Servers in that environment.

It includes several command line tools and a database of the WBEM Servers
in the environment.


.. _`Installation`:

Installation
------------
The following examples show different ways to install smipyping. They all ensure
that prerequisite Python packages are installed as needed:

1. Install a particular branch from the Git repository::

       $ pip install git+https://github.com/smipyping/smipyping.git@<branch-name>

These examples install smipyping and its prerequisite Python packages into the
currently active Python environment. By default, the system Python environment
is active. This is probably the right choice if you just want to use the
scripts that come with smipyping. In that case, you need to prepend the
installation commands shown above (i.e. `pip` and `python setup.py`) with
`sudo`, and your Linux userid needs to be authorized accordingly.

In a test user enviroment  installation into
a `virtual Python environment`_ is recommended).

.. _virtual Python environment: http://docs.python-guide.org/en/latest/dev/virtualenvs/


The command syntax above is shown for Linux, but works in similar ways on
Windows and OS-X.

In case of trouble with the installation, see the :ref:`Troubleshooting`
section.

You can verify that smipyping and its dependent packages are installed correctly
by importing the package into Python::

    $ python -c "import smipyping; print('ok')"
    ok


.. _`Prerequisite operating system packages`:
