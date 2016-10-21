Installation of smipyping
=============================

The smipyping Client can be installed quite easily by running its standard Python
setup script (`setup.py`) with the `install` command, or by using `pip install`
(which also invokes the setup script).

The setup script has support for installing its
prerequisites. This includes installing Python packages and OS-level packages,
and it includes the usual install mode and development mode.


Examples
--------

* Install latest version from PyPI into the current virtual Python:

      pip install smipyping

  If the OS-level prerequisites are not yet satisfied, then this command
  will fail. You can then perform this sequence of commands to get the
  the OS-level prerequisites installed in addition:

      pip download smipyping
      tar -xf smipyping-*.tar.gz
      cd smipyping-*
      python setup.py install_os install

  Note that you do not need to use 'sudo' in the command line, because you
  want to install the Python packages into the current virtual Python. The
  OS-level packages are installed by invoking 'sudo' under the covers.

  The OS-level prerequisites will be installed to the system, and the Python
  prerequisites along with PyWBEM itself will be installed into the current
  virtual Python environment.

* (FUTURE))Install latest version from PyPI into the system Python:

      sudo pip install smipyping

  If the OS-level prerequisites are not yet satisfied, then this command
  will fail. You can then perform this sequence of commands to get the
  the OS-level prerequisites installed in addition:

      pip download smipyping
      tar -xf smipyping-*.tar.gz
      cd smipyping-*
      sudo python setup.py install


* Install the latest development version from GitHub into the current
  virtual Python, installing OS-level prerequisites as needed:

      git clone git@github.com:pywbem/pywbem.git pywbem
      cd smipyping
      python setup.py install_os install

* Install from a particular distribution archive on GitHub into the current
  virtual Python, installing OS-level prerequisites as needed:

      wget https://github.com/pywbem/pywbem/blob/master/dist/pywbem-0.8/pywbem-0.8.3.tar.gz
      tar -xf smipyping-0.8.3.tar.gz
      cd smipyping-0.8.3
      python setup.py install_os install

* The installation of smipyping in development mode is supported as
  well:

      git clone git@github.com:pywbem/pywbem.git smipyping
      cd smipyping
      make develop

  This will install additional OS-level and Python packages that are needed
  for development and test of PyWBEM.

The command syntax above is shown for Linux, but this works the same way on
Windows and on other operating systems supported by Python.

Test of the installation
------------------------
TODO: This is all wrong
To test that PyWBEM is sucessfully installed, start up a Python interpreter and
try to import the pywbem module:

    python -c "import smipyping"

If you do not see any error messages after the import command, PyWBEM has been
sucessfully installed and its Python dependencies are available.

If you have installed in development mode, you can run the test suite:

    make test
