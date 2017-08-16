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
Tests for functions and classes in smipyping/_tableoutput.py
"""
from __future__ import print_function, absolute_import

import os
import unittest

from smipyping._userstable import UsersTable
from smipyping._configfile import read_config

VERBOSE = False

SCRIPT_DIR = os.path.dirname(__file__)


class TableTests(unittest.TestCase):
    def setUp(self):
        self.test_config_file = os.path.join(SCRIPT_DIR, 'testconfig.ini')

    def get_config(self, dbtype):
        test_config_file = os.path.join(SCRIPT_DIR, 'testconfig.ini')
        db_config = read_config('testconfig.ini', dbtype)
        db_config['directory'] = os.path.dirname(test_config_file)
        return db_config

    def methods_test(self, tbl_inst):
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
    def test_create(self):
        dbtype = 'mysql'
        db_config = self.get_config(dbtype)

        tbl_inst = UsersTable.factory(db_config, dbtype, True)
        self.assertTrue(len(tbl_inst) > 10)
        self.methods_test(tbl_inst)


class CsvTests(TableTests):
    @unittest.skip("Code not complete")
    def test_create(self):
        dbtype = 'csv'
        db_config = self.get_config(dbtype)
        print('csv Config File db info  dbtype %s, details %s' % (dbtype,
                                                                  db_config))

        tbl_inst = UsersTable.factory(db_config, dbtype, True)
        self.assertTrue(len(tbl_inst) > 10)
        self.methods_test(tbl_inst)


if __name__ == '__main__':
    unittest.main()
