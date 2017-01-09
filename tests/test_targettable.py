#!/usr/bin/env python

"""
Test the CSVUserData class.
"""

from __future__ import absolute_import, print_function
import unittest
import six

from smipyping import CsvUserData

# unimplemented = pytest.mark.skipif(True, reason="test not implemented")

class ValidCSVTargetTableTests(unittest.TestCase):
    def setUp(self):
        self.target_table = CsvUserData('userdata_example.csv')

class CsvTargetTableTest(ValidCSVTargetTableTests):
    """Class for simple tests of CSVUserData class."""

    def test_get_table(self):
        """Test getting the CsvUserData object."""
        self.assertTrue(len(self.target_table) != 0)

    def test_display_table(self):
        """Test display."""
        self.target_table.display_all()

    def test_table_contains(self):
        """Test contains functionality."""
        self.assertIn(42, self.target_table)
        self.assertIn(1, self.target_table)

    def test_get_data_record(self):
        """Test get one record"""
        self.assertIn(42, self.target_table)
        user_record = self.target_table.get_dict_record(42)
        self.assertIn('Product', user_record)

    def test_iter_items(self):
        """Test iteritems functionality"""
        counter = 0
        for user_id, user_record in six.iteritems(self.target_table):
            counter += 1
            self.assertIn('Product', user_record)
            self.assertIn('SMIVersion', user_record)
            self.assertIn('ScanEnabled', user_record)

        self.assertEqual(counter, 51)
        self.assertEqual(len(self.target_table), 51)

    def test_not_contains(self):
        self.assertNotIn(942, self.target_table)

    def test_get_target_table_host(self):
        host_id = ['10.1.132.110', 5989]
        result_list = self.target_table.get_user_data_host(host_id)

        self.assertTrue(result_list is not None)

    def test_disabled_target(self):
        self.assertTrue(self.target_table.disabled_record(
            self.target_table[42]))

    def test_enabled_target(self):
        self.assertFalse(self.target_table.disabled_record(
            self.target_table[4]))

if __name__ == '__main__':
    unittest.main()
