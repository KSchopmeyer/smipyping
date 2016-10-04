#!/usr/bin/env python

"""
TODO add description here
"""
from __future__ import print_function, absolute_import
from os import path
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))


here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md')) as f:
    long_description = f.read()

setup(
    name='smipyping',
    version='1.0',
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
    install_requires=['pywbem', 'six', 'tabulate', 'scapy'],

    # package data files
    package_data={
        'smipyping': [
            'NEWS.md',
            'LICENSE.txt',
        ]},
    )

