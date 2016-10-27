Installation of smipyping
=============================

smpipping is not in PyPi today so it must be installed from the
git repository at:

git clone https://kschopmeyer@bitbucket.org/kschopmeyer/smipyping.git

There are two ways to do this:

Clone install
-------------

In this installation you first clone the repository and then install
from that clone.

1. clone the repository. Note that you only have to clone once. From
then on you can merge in new changes.

git clone https://kschopmeyer@bitbucket.org/kschopmeyer/smipyping.git

you will now have a directory smipyping that is the complete development
environmemt including all prerequisits, etc.

  cd smipyping
  make install
  
actually I think it should be sudo make install.

This should install the package.

To update the installation when I add more code:

1. go to smipyping
2. update with
      git fetch
      git pull origin
3. reinstall
   make install

pip install
-----------

Python packages can also be directly installed from git.  That can
be done with the command:

sudo pip install -e git+https://kschopmeyer@bitbucket.org/kschopmeyer/smipyping.git#egg=smipyping

This should be the equivalent of the clone, make install



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
