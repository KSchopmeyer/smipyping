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

from smipyping._configfile import read_config
from smipyping._cimreport import build_cimreport

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


class ReportTests(TableTests):
    def test_create_report(self):
        dbtype = 'mysql'
        db_config = self.get_config(dbtype)
        year = 2016
        month = 12
        day_of_month = 1
        report = build_cimreport(db_config, dbtype, year, month,
                                 day_of_month)
        # TODO test results of report
        print(report)


if __name__ == '__main__':
    unittest.main()
