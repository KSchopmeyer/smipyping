
.. _`Development`:

Development
===========

This section only needs to be read by developers of the smipyping package.
People that want to make a fix or develop some extension, and people that
want to test the project are also considered developers for the purpose of
this section.


.. _`Repository`:

Repository
----------

The repository for smipyping is on GitHub:

https://github.com/smipyping/smipyping


.. _`Setting up the development environment`:

Setting up the development environment
--------------------------------------

The development environment is pretty easy to set up.

Besides having a supported operating system with a supported Python version
(see :ref:`Supported environments`), it is recommended that you set up a
`virtual Python environment`_.

.. _virtual Python environment: http://docs.python-guide.org/en/latest/dev/virtualenvs/

Then, with a virtual Python environment active, clone the Git repo of this
project and prepare the development environment with ``make develop``:

::

    $ git clone git@github.com:smipyping/smipyping.git
    $ cd smipyping
    $ make develop

This will install all prerequisites the package needs to run, as well as all
prerequisites that you need for development.

Generally, this project uses Make to do things in the currently active
Python environment. The command ``make help`` (or just ``make``) displays a
list of valid Make targets and a short description of what each target does.


.. _`Building the documentation`:

Building the documentation
--------------------------

The ReadTheDocs (RTD) site is used to publish the documentation for the
smipyping package at http://smipyping.readthedocs.io/

This page automatically gets updated whenever the ``master`` branch of the
Git repo for this package changes.

In order to build the documentation locally from the Git work directory, issue:

::

    $ make builddoc

The top-level document to open with a web browser will be
``build_doc/html/docs/index.html``.


.. _`Testing`:

Testing
-------

To run unit tests in the currently active Python environment, issue one of
these example variants of ``make test``:

::

    $ make test                                              # Run all unit tests
    $ PYTHONPATH=. py.test testsuite/test_cim_obj.py -s      # Run only this test source file
    $ PYTHONPATH=. py.test InitCIMInstanceName -s            # Run only this test class
    $ PYTHONPATH=. py.test -k InitCIMInstanceName or Bla -s  # py.test -k expressions are possible

Invoke ``py.test --help`` for details on the expression syntax of its ``-k``
option.

To run the unit tests and some more commands that verify the project is in good
shape in all supported Python environments, use Tox:

::

    $ tox                              # Run all tests on all supported Python versions
    $ tox -e py27                      # Run all tests on Python 2.7


.. _`Developing Ipython Notebooks`:

Developing PyWBEM Ipython Documentation Notebooks
----------------------------

The smipyping developers are using ipython notebooks to demonstrate the use of
smipyping.  Today we generally have one notebook per operation or group of
operations including definition of the operation, references back to the
smipyping documentation, and one or more examples  (hopefully examples that
will actually execute against a wbem server)

These can easily be extended or supplemented using a local ipython or
jupyter server by:

1. Install ipython or Jupyter software using pip or pip3. The notebook server
 may be installed as root or within a python virtual environment. For
 example:

::

   $ sudo pip install ipython
   or
   $ sudo pip3 install ipython
   or   
   $ sudo pip install jupyter

The notebook server may be installed as root or within a python virtual
environment.
  
2. Start the local ipython notebook server in the notebook directory:

   a. Go to the smipyping directory `smipyping/docs/notebooks`.
   
   b. Start the ipython server:

::

  $ ipython notebook
  or      
  $ jupyter notebook

This will start the local ipython/juypter notebook server and on the first page
displayed in your web browser all existing smipyping ipython notebooks will be
available for editing. New ones can be created using the commands on that
ipython server web page.

New and changed notebooks must go through the same contribution process as other
components of smipyping to be integrated into the github repository.

.. _`Contributing`:

Contributing
------------

Third party contributions to this project are welcome!

In order to contribute, create a `Git pull request`_, considering this:

.. _Git pull request: https://help.github.com/articles/using-pull-requests/

* Test is required.
* Each commit should only contain one "logical" change.
* A "logical" change should be put into one commit, and not split over multiple
  commits.
* Large new features should be split into stages.
* The commit message should not only summarize what you have done, but explain
  why the change is useful.
* The commit message must follow the format explained below.

What comprises a "logical" change is subject to sound judgement. Sometimes, it
makes sense to produce a set of commits for a feature (even if not large).
For example, a first commit may introduce a (presumably) compatible API change
without exploitation of that feature. With only this commit applied, it should
be demonstrable that everything is still working as before. The next commit may
be the exploitation of the feature in other components.

For further discussion of good and bad practices regarding commits, see:

* `OpenStack Git Commit Good Practice`_
* `How to Get Your Change Into the Linux Kernel`_

.. _OpenStack Git Commit Good Practice: https://wiki.openstack.org/wiki/GitCommitMessages
.. _How to Get Your Change Into the Linux Kernel: https://www.kernel.org/doc/Documentation/SubmittingPatches
