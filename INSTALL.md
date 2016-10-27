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
