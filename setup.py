#!/usr/bin/env python
"""
Setup for smipyping tool. Uses standard setuptool definitions.

TODO expand this
"""

from __future__ import print_function, absolute_import
from os import path
from setuptools import setup

here = path.abspath(path.dirname(__file__))


def package_version(filename, varname):
    """
    Return package version string.

    Reads `filename` and retrieves its module-global variable `varnam`.
    """
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
        'pytest',
        'mysql-connector',
        'configparser',
        'click',
        'click-repl',
        'click-spinner'],

    # smipyping prereqs for 'develop' command.
    # TOD enable this. pywbem does in os_setup.py
    develop_requires=[
        "pytest>=2.4",
        "pytest-cov",
        "Sphinx>=1.3",
        # Pinning GitPython to 2.0.8 max, due to its use of unittest.case
        # which is not available on Python 2.6.
        # TODO: Track resolution of GitPython issue #540:
        #       https://github.com/gitpython-developers/GitPython/issues/540
        "GitPython==2.0.8",
        "sphinx-git"],

    # package data files
    package_data={
        'smipyping': [
            'NEWS.md',
            'LICENSE.txt',
        ]},

    scripts=[
        'simpleping',
        'explore',
        'serversweep',
        'simplepingall',
        'smicli']
    )
