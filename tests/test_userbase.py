#!/usr/bin/env python

from __future__ import absolute_import, print_function
import unittest
#import pytest
#import pyping

from smipyping import CsvUserData

#unimplemented = pytest.mark.skipif(True, reason="test not implemented")

class CsvUserBaseTest(unittest.TestCase):

    def test_get_data(self):
        user_data = CsvUserData('userdata_example.csv')
        self.assertTrue(len(user_data) != 0)

    def test_display_data(self):
        user_data = CsvUserData('userdata_example.csv')
        user_data.display_all()

    def test_contains(self):
        user_data = CsvUserData('userdata_example.csv')
        if 1 in user_data:
            print('test_ contains: OK')
        else:
            print('test_ contains: Not OK')
            #self.fail('1 not in user_data')
        #self.assertIn(1, user_data)

if __name__ == '__main__':
    unittest.main()
