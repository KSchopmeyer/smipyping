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
Tests for functions and classes in _pingstable.py
"""
from __future__ import print_function, absolute_import

import os
import unittest
import datetime

from smipyping._pingstable import PingsTable
from smipyping._configfile import read_config

VERBOSE = False

SCRIPT_DIR = os.path.dirname(__file__)


class TableTests(unittest.TestCase):
    def setUp(self):
        self.test_config_file = os.path.join(SCRIPT_DIR, 'testconfig.ini')

    def get_config(self, dbtype):
        test_config_file = os.path.join(SCRIPT_DIR, 'testconfig.ini')
        db_config = read_config(test_config_file, dbtype)
        db_config['directory'] = os.path.dirname(test_config_file)
        return db_config

    def methods_test(self, tbl_inst):
        """Generate test for methods of the pings_table class"""
        if VERBOSE:
            print('dict %s' % tbl_inst.data_dict)
        test_keys = []
        for key in tbl_inst:
            test_keys.append(key)
            self.assertTrue(key in tbl_inst)
            value = tbl_inst[key]
            id_ = value[tbl_inst.key_field]
            self.assertTrue(isinstance(id_, int))
            for name in tbl_inst:
                self.assertTrue(name in tbl_inst)

        self.assertEqual(len(test_keys), len(tbl_inst))

        for key in test_keys:
            self.assertTrue(key in tbl_inst)

        for key in test_keys:
            self.assertTrue(key in tbl_inst)

        for key, value in tbl_inst .iteritems():
            self.assertTrue(key in test_keys)


class MySQLTests(TableTests):
    """Tests for a mysql database"""

    def setUp(self):
        """Open database and get pings table"""
        dbtype = 'mysql'
        db_config = self.get_config(dbtype)

        self.tbl_inst = PingsTable.factory(db_config, dbtype, False)

    def tearDown(self):
        """Close the database"""
        self.tbl_inst.close_connection()

    def test_create(self):
        """Test create the pings table and get some instances"""

        print('pings %s' % self.tbl_inst.data_dict)
        self.assertEqual(len(self.tbl_inst), 0)
        # self.methods_test(tbl_inst)
        rows = self.tbl_inst.get_data_for_day(2016, 8, 5)
        print('len rows %s' % len(rows))

    def test_compute_number_of_days(self):
        """Test the function that computes start and end dates"""

        # test parameters
        # Start date, end date, number of days, rtn start date, rtn end date
        tests = [
            ['01/01/16', '01/02/16', None, '01/01/16', '01/02/16'],
            ['01/01/16', '02/01/16', None, '01/01/16', '02/01/16'],
            [None, '02/01/16', None, '01/01/16', '02/01/16'],
            ['01/01/16', None, 1, '01/01/16', '02/01/16'], ]

        format = '%d/%m/%y'

        for test in tests:
            start = None
            end = None
            if test[0]:
                start = datetime.datetime.strptime(test[0], format)
            if test[1]:
                end = datetime.datetime.strptime(test[1], format)
            start_date, end_date = self.tbl_inst.compute_dates(start,
                                                               end,
                                                               test[2])
            print('test %s start %s, end %s' % (test, start_date, end_date))
            if start:
                start_date = start_date.strftime(format)
                self.assertEqual(start_date, test[3])

            end_date = end_date.strftime(format)
            self.assertEqual(end_date, test[4])

        try:
            end = datetime.datetime.strptime('01/01/16', format)
            start_date, end_date = self.tbl_inst.compute_dates(None,
                                                               end,
                                                               2)
            self.fail("Exception expected")
        except ValueError as ve:
            print(ve)


if __name__ == '__main__':
    unittest.main()
