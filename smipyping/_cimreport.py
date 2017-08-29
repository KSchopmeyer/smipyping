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

from ._companiestable import CompaniesTable
from ._pingstable import PingsTable
from ._targetdata import TargetsData


def build_cimreport(db_dict, dbtype, year, month, day_of_month, verbose):

    # get companies
    companies = CompaniesTable(db_dict, dbtype, verbose)

    # get scans for one day

    pings_table = PingsTable(db_dict, dbtype, verbose)
    pings = pings_table.get_data_for_day(year, month, day_of_month)

    # get enabled targets

    targets = TargetsData(db_dict, dbtype, verbose)
    enabled_targets = []
    for target in targets:
        if not target.disabled_target():
            enabled_targets.append(target)
    target_stats = []
    for target in enabled_targets:
        # count number of times target scanned
        pings = 0
        pings_ok = 0
        for ping in pings:
            if ping[target]:
                pings += 1
            if ping[target]['Status'] == 'OK':
                pings_ok += 1
        target_stats[target] = (pings, pings_ok)
    print('target_stats %s' % target_stats)
