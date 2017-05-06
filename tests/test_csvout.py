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
smicli commands based on python click for operations on the smipyping
data file.
"""

from __future__ import print_function, absolute_import

import os
import csv
import unittest

from smipyping import TargetsData
from smipyping._csvtable import write_csv_table

# unimplemented = pytest.mark.skipif(True, reason="test not implemented")

TEST_CONFIG_FILE_NAME = 'testconfig.ini'
SCRIPT_DIR = os.path.dirname(__file__)

DB_TYPE = 'csv'

class CSVOutputTestsSetup(unittest.TestCase):
    """ Setup class for cvs file tests"""
    def setUp(self):
        test_config_file = os.path.join(SCRIPT_DIR, TEST_CONFIG_FILE_NAME)
        print('test_config_file %s' % test_config_file)
        db_config = read_config(test_config_file, DB_TYPE)
        db_config['directory'] = os.path.dirname(test_config_file)
        self.target_table = TargetsData.factory(test_config_file, DB_TYPE,
                                                False)

    def read_csv_file(self, file_name):
        with open(file_name, 'rb') as csvfile:
            reader = csv.reader(csvfile)
            rows = []
            for row in reader:
                rows.append(row)
                print(', '.join(row))
        return rows


class CSVOutputTests(CSVOutputTestsSetup):

    def write_lists(self):
        """Test to write a simple fixed file"""
        data = [['row1', 'row2', 'row3'],
                ['data1', 2, 'data3']]
        rows = write_csv_table(data, csv_file='test_cvsout.csv')

        rows = self.read_csv_file('test_cvsout.csv')
        print('rows\n' % rows)


if __name__ == '__main__':
    unittest.main()
