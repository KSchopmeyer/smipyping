Installation of smipyping
=============================

smpipping is not in PyPi today so it must be installed from the
git repository at:

git clone https://kschopmeyer@bitbucket.org/kschopmeyer/smipyping.git

There are two ways to do this:

1. Clone Install - clone the repository into your local system and then install
   from that clone.

2. pip install from the git repository. NOTE: For some reason this is not
   working right now.

Clone install
-------------

In this installation you first clone the git repository and then install
the actual running smipyping from that clone.

0. Go to directory where you want to clone smipyping.

1. Clone the repository. Note that you only have to clone once. From
then on you can merge in new changes.

    >git clone https://kschopmeyer@bitbucket.org/kschopmeyer/smipyping.git

you will now have a directory smipyping that is the complete development
environment including all prerequisits, etc.

  cd smipyping
  sudo make install

NOTE: to make this work I did su - and then went back to the smipyping dir.

This should install the smipyping package

Updating Clone install with new smipyping code
----------------------------------------------

To update the installation when the package is updated, you simple refresh
the local clone from the repository

1. go to smipyping directory that was installed with the clone command earlier

2. update with

      >git fetch
      >git pull origin
      
You should see tell you if there is anything new in master with the fetch
command.  The git pull will merge new code into the current base.
    
3. reinstall the package as before with make:
      sudo >make install 


pip install
-----------

NOTE: Having problems with this right now. Says it installs but the installion
is incomplete when finished.

Python packages can also be directly installed from git with pip.  That can
be done with the command:

sudo pip install -e git+https://kschopmeyer@bitbucket.org/kschopmeyer/smipyping.git#egg=smipyping

This should be the equivalent of the clone, make install when I figure out
the problem.


Test of the installation
------------------------
To test if it is working you can execute one of the scripts:

    >simpleping --help

Note that from within the repository directory you can also execute the
unit tests with:

    make test
