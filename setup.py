#!/usr/bin/env python

"""
Setup for smipyping tool. Uses standard setuptool definitions.
"""

from __future__ import print_function, absolute_import
from os import path
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

def package_version(filename, varname):
    """Return package version string by reading `filename` and retrieving its
       module-global variable `varnam`."""
    _locals = {}
    with open(filename) as fp:
        exec(fp.read(), None, _locals)  # pylint: disable=exec-used
    return _locals[varname]

# Get the long description from the README file
with open(path.join(here, 'README.md')) as f:
    long_description = f.read()

pkg_version = package_version("smipyping/_version.py", "__version__")

setup(
    name='smipyping',
    version=pkg_version,
    description='smipyping - SMI Lab Test Tools',
    long_description=long_description,
    url='https://git@bitbucket.org:kschopmeyer/smipyping.git',
    author='Karl Schopmeyer',
    author_email='k.schopmeyer@swbell.net',
    packages=['smipyping'],
    platforms=['any'],
    license='MIT',
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    # Run-time dependencies. These will be installed by pip
    install_requires=[
        'pywbem',
        'six',
        'terminaltables',
        'scapy',
        'pytest'],
        
    # smipyping prereqs for 'develop' command.
    # TOD enable this. pywbem does in os_setup.py
    develop_requires=[
        "pytest>=2.4",
        "pytest-cov",
        "Sphinx>=1.3",
        "GitPython>=2.0.6",
        "sphinx-git",
        "httpretty"],
        #"lxml",

    # package data files
    package_data={
        'smipyping': [
            'NEWS.md',
            'LICENSE.txt',
        ]},

    scripts=[
        'simpleping',
        'userdata',
        'explore',
        'serversweep',
        'simplepingall']
    )

#def main()

    #import_setuptools()
    #from setuptools import setup
    #from setuptools.command.build_py import build_py as _build_py

    #class build_py(_build_py):
        ## pylint: disable=invalid-name,too-few-public-methods
        #"""Custom command that extends the setuptools `build_py` command,
        #which prepares the Python files before they are being installed.
        #This command is used by `setup.py install` and `pip install`.

        #We use this only to pick up the verbosity level.
        #"""
        #def run(self):
            #global _VERBOSE  # pylint: disable=global-statement
            #_VERBOSE = self.verbose
            #_build_py.run(self)

    #py_version_m_n = "%s.%s" % (sys.version_info[0], sys.version_info[1])
    #py_version_m = "%s" % sys.version_info[0]

    #pkg_version = package_version("smipyping/_version.py", "__version__")

    ## The following retry logic attempts to handle the frequent xmlrpc
    ## errors that recently (9/2016) have shown up with Pypi.
    #tries = 2
    #while True:
        #tries -= 1
        #try:
            #setup(**args)
        #except Fault as exc:
            #if tries > 0:
                #print("Warning: Retrying setup() because %s was raised: %s" %
                      #(exc.__class__.__name__, exc))
                #continue
            #else:
                #raise
        #else:
            #break

    #if 'install' in sys.argv or 'develop' in sys.argv:
        #build_moftab(_VERBOSE)

    #return 0

#if __name__ == '__main__':
    #sys.exit(main())

