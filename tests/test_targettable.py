#!/usr/bin/env python

# (C) Copyright 2017 Inova Development Inc.
# All Rights Reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test the TargetsData class class.
"""
from __future__ import absolute_import, print_function

import os
import unittest
import six

from smipyping import TargetsData
from smipyping._configfile import read_config

# unimplemented = pytest.mark.skipif(True, reason="test not implemented")

TEST_CONFIG_FILE_NAME = 'testconfig.ini'
SCRIPT_DIR = os.path.dirname(__file__)


class TargetTableTests(unittest.TestCase):
    pass


class CsvTableTests(TargetTableTests):
    def setUp(self):
        """Load the csv test table"""
        dbtype = 'csv'
        test_config_file = os.path.join(SCRIPT_DIR, TEST_CONFIG_FILE_NAME)
        db_config = read_config(test_config_file, dbtype)
        db_config['directory'] = os.path.dirname(test_config_file)
        self.target_table = TargetsData.factory(db_config, dbtype, False)


class TargetTableTest(CsvTableTests):
    """Class for simple tests of CSVUserData class."""

    def test_get_table(self):
        """Test getting the object."""
        self.assertTrue(len(self.target_table) != 0)

    def test_display_table(self):
        """Test display."""
        self.target_table.display_all()

    def test_table_contains(self):
        """Test contains functionality."""
        self.assertIn(6, self.target_table)
        self.assertIn(1, self.target_table)

    def test_keys(self):
        self.assertIn(6, self.target_table.keys())
        for key in self.target_table.keys():
            self.assertIn(key, self.target_table)

    def test_get_data_record(self):
        """Test get one record"""
        self.assertIn(6, self.target_table)
        user_record = self.target_table.get_target(6)
        user_record2 = self.target_table[6]
        self.assertIn('Product', user_record)
        self.assertEqual(user_record, user_record2)

    def test_iter_items(self):
        """Test iteritems functionality"""
        counter = 0
        for user_id, user_record in six.iteritems(self.target_table):
            counter += 1
            self.assertIn('Product', user_record)
            self.assertIn('SMIVersion', user_record)
            self.assertIn('ScanEnabled', user_record)

        self.assertEqual(counter, 6)
        self.assertEqual(len(self.target_table), 6)

    def test_not_contains(self):
        self.assertNotIn(96, self.target_table)

    def test_get_target_table_host(self):
        host_id = ['10.1.132.110', 5989]
        result_list = self.target_table.get_targets_host(host_id)

        self.assertTrue(result_list is not None)

    def test_disabled_target(self):
        self.assertTrue(self.target_table.disabled_target(
            self.target_table[6]))

    def test_get_enabled_list(self):
        ids = self.target_table.get_enabled_targetids()
        self.assertTrue(len(ids) == 5)
        self.assertTrue(4 in ids)
        self.assertTrue(6 not in ids)

    def test_get_disabled_list(self):
        ids = self.target_table.get_disabled_targetids()
        self.assertTrue(len(ids) == 1)
        self.assertTrue(4 not in ids)
        self.assertTrue(6 in ids)

    def test_display_disabled(self):
        # target_data = self.get_target_data()
        self.target_table.display_disabled('simple')

    def test_enabled_target(self):
        # target_data = self.get_target_data()
        self.target_table.display_disabled('simple')
        self.assertFalse(
            self.target_table.disabled_target(self.target_table[4]))


if __name__ == '__main__':
    unittest.main()
