#!/usr/bin/env python

from distutils.core import setup
from __future__ import print_function, absolute_import
"""
TODO add description here
"""

setup(name='pyping',
    version='1.0',
    description='pyping - SMI Lab Test Tools',
    author='Karl Schopmeyer',
    author_email='k.schopmeyer@swbell.net',
    url='https://www.python.org/sigs/distutils-sig/',
    packages=['pyping', 'distutils.command'],
    long_description = __doc__,
    platforms = ['any'],
    url = 'http://pywbem.github.io/pywbem/',
    ##    'version': pkg_version,
    #TODO define license
    license = 'TODO',
     )


if __name__ == '__main__':
    sys.exit(main())
