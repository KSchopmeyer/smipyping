#!/usr/bin/env python

"""
    Test the CSVUserData class.
"""

from __future__ import absolute_import, print_function
import unittest
#import pytest
#import pyping

from smipyping import CsvUserData

#unimplemented = pytest.mark.skipif(True, reason="test not implemented")

class CsvUserDataTest(unittest.TestCase):

    def test_get_data(self):
        user_data = CsvUserData('userdata_example.csv')
        self.assertTrue(len(user_data) != 0)

    def test_display_data(self):
        user_data = CsvUserData('userdata_example.csv')
        user_data.display_all()

    def test_contains(self):
        user_data = CsvUserData('userdata_example.csv')
        #if '42' in user_data:
            #print('test_ contains: OK')
        #else:
            #print('test_ contains: Not OK')

        self.assertIn("42", user_data)

    def test_not_contains(self):
        user_data = CsvUserData('userdata_example.csv')
        #if '942' in user_data:
            #print('test_not_contains: OK')
        #else:
            #print('test__not_contains: Not OK')

        self.assertNotIn("942", user_data)

    def test_get_user_data_host(self):
        user_data = CsvUserData('userdata_example.csv')
        host_id = ['10.1.132.110', 5989]
        result_list = user_data.get_user_data_host(host_id)
        if not result_list:
            print('test_get_user_data_host: OK')
        else:
            print('test_get_user_data_host: Not OK')

if __name__ == '__main__':
    unittest.main()
