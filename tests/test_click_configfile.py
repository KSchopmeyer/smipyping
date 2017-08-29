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
from smipyping._click_configfile import get_config_dict, ConfigFileProcessor

SCRIPT_DIR = os.path.dirname(__file__)

VERBOSE = False

# test for config file with good data
good_config_data = [
    '#Test config file created by test_click_configfile.py',
    '[general]',
    'dbtype = mysql',

    '[mysql]',
    'host = localhost',
    'database = SMIStatus',
    'user = kschopmeyer',
    'password = test8play',

    '[csv]',
    'targetsfilename = targetdata_example.csv',

    '[logging]',
    'log_level = debug']


class ValidConfigFileTests(unittest.TestCase):
    """
    Tests for valid components in config file.
    Setup a config file and test validate
    """

    def setUp(self):
        """Setup for standard config file in tests  dir"""
        self.configfile = None

    def create_file(self, file_name, file_data):
        """
        Create a config file from the defined file data in the tests
        directory
        """
        test_config_file = os.path.join(SCRIPT_DIR, file_name)
        with open(test_config_file, 'w') as file_handle:
            for line in file_data:
                file_handle.write(line)
                file_handle.write('\n')
        self.configfile = test_config_file
        ConfigFileProcessor.set_search_path([SCRIPT_DIR])
        # print('test_config_file %s' % test_config_file)
        ConfigFileProcessor.set_config_files([file_name])

    def tearDown(self):
        """Remove config file if it exists"""
        if self.configfile and os.path.exists(self.configfile):
            # print('remove %s' % self.configfile)
            os.remove(self.configfile)


class ConfigFileTest(ValidConfigFileTests):
    """Class for simple tests of CSVUserData class."""

    def test_valid_data(self):
        """Test a single data file"""
        self.create_file('smicliblah.ini', good_config_data)

        config_dict = get_config_dict()

        default_map = config_dict['default_map']

        if VERBOSE:
            for data_key in default_map:
                print(' %s=%s' % (data_key, default_map[data_key]))

        self.assertEqual(default_map['dbtype'], 'mysql')

        mysql = default_map['mysql']

        self.assertEqual(mysql['host'], 'localhost')
        csv = default_map['csv']
        self.assertEqual(csv['targetsfilename'], 'targetdata_example.csv')

    def test_no_config_file(self):
        """Test where no file exists."""
        ConfigFileProcessor.set_config_files('blah.blah')
        config_dict = get_config_dict()
        expected = {'default_map': {}, 'help_option_names': ['-h', '--help']}
        self.assertEqual(config_dict, expected, 'Error: Expected:\n%s, '
                         '\nActual:\n%s' % (expected, config_dict))

    # TODO add more tests.


if __name__ == '__main__':
    unittest.main()
