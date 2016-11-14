#!/usr/bin/env python

"""
Test the CSVUserData class.
"""

from __future__ import absolute_import, print_function
import unittest
import six

from smipyping import CsvUserData

# unimplemented = pytest.mark.skipif(True, reason="test not implemented")


class CsvUserDataTest(unittest.TestCase):
    """Class for simple tests of CSVUserData class."""

    def test_get_data(self):
        """Test getting the CsvUserData object."""
        user_data = CsvUserData('userdata_example.csv')
        self.assertTrue(len(user_data) != 0)

    def test_display_data(self):
        """Test display."""
        user_data = CsvUserData('userdata_example.csv')
        user_data.display_all()

    def test_contains(self):
        """Test contains functionality."""
        user_data = CsvUserData('userdata_example.csv')
        if 42 in user_data:
            print('test_ contains: OK')
        else:
            print('test_ contains: Not OK')

        self.assertIn(42, user_data)
        self.assertIn(1, user_data)

    def test_get_data_record(self):
        """Test get one record"""
        user_data = CsvUserData('userdata_example.csv')
        self.assertIn(42, user_data)
        user_record = user_data.get_dict_record(42)
        self.assertIn('Product', user_record)

    def test_iter_items(self):
        """Test iteritems functionality"""
        user_data = CsvUserData('userdata_example.csv')
        counter = 0
        for user_id, user_record in six.iteritems(user_data):
            counter += 1
            self.assertIn('Product', user_record)
            self.assertIn('SMIVersion', user_record)
        self.assertEqual(counter, 51)

    def test_not_contains(self):
        user_data = CsvUserData('userdata_example.csv')
        if 942 in user_data:
            print('test_not_contains: Not OK')
        else:
            print('test__not_contains: OK')

        self.assertNotIn(942, user_data)

    def test_get_user_data_host(self):
        user_data = CsvUserData('userdata_example.csv')
        host_id = ['10.1.132.110', 5989]
        result_list = user_data.get_user_data_host(host_id)
        print('result_list %s' % result_list)
        if not result_list:
            print('test_get_user_data_host: Not OK')
        else:
            print('test_get_user_data_host: OK')
        self.assertTrue(result_list is not None)


if __name__ == '__main__':
    unittest.main()
