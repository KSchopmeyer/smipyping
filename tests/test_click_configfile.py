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
from smipyping._click_configfile import get_config_dict

TEST_CONFIG_FILE_NAME = 'smicli.ini'

SCRIPT_DIR = os.path.dirname(__file__)

# test for config file with good data
good_config_data = [
    '[general]',
    'dbtype = mysql',

    '[mysql]',
    'host = localhost',
    'database = SMIStatus',
    'user = kschopmeyer',
    'password = test8play',

    '[csv]',
    'filename = targetdata_example.csv',

    '[logging]',
    'log_level = debug']


class ValidConfigFileTests(unittest.TestCase):

    def setUp(self):
        test_config_file = os.path.join(SCRIPT_DIR, TEST_CONFIG_FILE_NAME)
        self.configfile = None

    def create_file(self, file_name, file_data):
        """
        Create a config file from the defined file data
        """
        test_config_file = os.path.join(SCRIPT_DIR, file_name)
        with open(test_config_file, 'w') as file_handle:
            for line in file_data:
                file_handle.write(line)
                file_handle.write('\n')
        self.configfile = file_name

    def tearDown(self):
        if self.configfile:
            os.remove(self.configfile)


class ConfigFileTest(ValidConfigFileTests):
    """Class for simple tests of CSVUserData class."""

    def test_valid_data(self):
        """Test a single data file"""
        self.create_file('smicli.cfg', good_config_data)

        config_dict = get_config_dict()

        print(config_dict)

        for data_key in config_dict:
            print(' %s=%s' % (data_key, config_dict[data_key]))

        self.assertEqual(config_dict['dbtype'], 'mysql')

        mysql = config_dict['mysql']

        self.assertEqual(mysql['host'], 'localhost')
        csv = config_dict['csv']
        self.assertEqual(csv['filename'], 'targetdata_example.csv')

    def test_no_config_file(self):
        """Test where no file exists."""

        config_dict = get_config_dict()
        self.assertEqual(config_dict, {})

    # TODO add more tests.


if __name__ == '__main__':
    unittest.main()
