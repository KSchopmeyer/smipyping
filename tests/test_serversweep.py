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
Unit Test the server sweep functions
"""
from __future__ import absolute_import, print_function

import unittest

from smipyping._serversweep import ServerSweep


class ExpandSubnetDefTests(unittest.TestCase):
    """
    Tests for the ability to expand ips and build lists of subnets
    """

    def test_expand_subnet(self):
        """
        Test the expand_subnet_definition function
        """
        # pylint: disable=invalid-name
        t1 = ServerSweep('10.1.1.1', '5988')
        actual = [x for x in t1.expand_subnet_definition('10.1.1.1')]
        self.assertEqual(actual, ['10.1.1.1'])

        actual = [x for x in t1.expand_subnet_definition('10.1.1.1,2')]
        self.assertEqual(actual, ['10.1.1.1', '10.1.1.2'])

        actual = [x for x in t1.expand_subnet_definition('10.1.1.1-3')]
        self.assertEqual(actual, ['10.1.1.1', '10.1.1.2', '10.1.1.3'])

        actual = [x for x in t1.expand_subnet_definition('10.1.1-2.1')]
        self.assertEqual(actual, ['10.1.1.1', '10.1.2.1'])

        t2 = ServerSweep('10.1.1', '5988',
                         min_octet_val=1, max_octet_val=2)

        actual = [x for x in t2.expand_subnet_definition('10.1.1')]
        self.assertEqual(actual, ['10.1.1.1', '10.1.1.2'])

    def test_build_test_list(self):
        """
        Test the build_test_list function
        """
        # pylint: disable=invalid-name
        t1 = ServerSweep('10.1.1.1,2', [5988, 5989],
                         min_octet_val=1, max_octet_val=254)
        actual = [x for x in t1.build_test_list()]
        self.assertEqual(
            actual,
            [('10.1.1.1', 5988), ('10.1.1.1', 5989), ('10.1.1.2', 5988),
             ('10.1.1.2', 5989)])

        t2 = ServerSweep('10.1.1.1,2', [5989],
                         min_octet_val=1, max_octet_val=254)
        actual = [x for x in t2.build_test_list()]

        self.assertEqual(
            actual, [('10.1.1.1', 5989), ('10.1.1.2', 5989)])

        t3 = ServerSweep('10.1.1.1,2', [5987, 5988, 5989],
                         min_octet_val=1, max_octet_val=254)
        actual = [x for x in t3.build_test_list()]

        self.assertEqual(
            actual,
            [('10.1.1.1', 5987), ('10.1.1.1', 5988), ('10.1.1.1', 5989),
             ('10.1.1.2', 5987), ('10.1.1.2', 5988),
             ('10.1.1.2', 5989)])

        t4 = ServerSweep('10.1.1.1,2', 5989,
                         min_octet_val=1, max_octet_val=2)
        actual = [x for x in t4.build_test_list()]

        self.assertEqual(
            actual,
            [('10.1.1.1', 5989), ('10.1.1.2', 5989)])

        t5 = ServerSweep('10.1.1.1-3', 5989,
                         min_octet_val=1, max_octet_val=2)
        actual = [x for x in t5.build_test_list()]

        self.assertEqual(
            actual,
            [('10.1.1.1', 5989), ('10.1.1.2', 5989), ('10.1.1.3', 5989)])

        t6 = ServerSweep('10.1.1', 5989,
                         min_octet_val=2, max_octet_val=3)
        actual = [x for x in t6.build_test_list()]

        self.assertEqual(
            actual,
            [('10.1.1.2', 5989), ('10.1.1.3', 5989)])


if __name__ == '__main__':
    unittest.main()
