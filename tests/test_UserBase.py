#!/usr/bin/env python

from __future__ import absolute_import, print_function
#import unittest

#import pyping

import userbase

class CsvUserBaseTest():

    def test_get_base(self):
        userbase = CsvUserBase('userbase_example.csv')

    def test_display_base(self):
        userbase = CsvUserBase('userbase_example.csv')
        userbase.display()

if __name__ == '__main__':
    unittest.main()
