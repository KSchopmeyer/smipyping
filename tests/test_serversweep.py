#!/usr/bin/env python

"""
Unit Test the server sweep functions
"""
from __future__ import absolute_import, print_function

import unittest

from smipyping._serversweep import expand_subnet_definition, \
    build_test_list


class ExpandSubnetDefTests(unittest.TestCase):

    def test1(self):
        actual = [x for x in expand_subnet_definition('10.1.1.1')]
        self.assertEqual(actual, ['10.1.1.1'])

        actual = [x for x in expand_subnet_definition('10.1.1.1,2')]
        self.assertEqual(actual, ['10.1.1.1', '10.1.1.2'])

        actual = [x for x in expand_subnet_definition('10.1.1.1:3')]
        self.assertEqual(actual, ['10.1.1.1', '10.1.1.2', '10.1.1.3'])

        actual = [x for x in expand_subnet_definition('10.1.1:2.1')]
        self.assertEqual(actual, ['10.1.1.1', '10.1.2.1'])

        actual = [x for x in expand_subnet_definition('10.1.1',
                                                      min_val=1, max_val=2)]
        self.assertEqual(actual, ['10.1.1.1', '10.1.1.2'])

    def test_build_test_list(self):
        actual = [x for x in build_test_list('10.1.1.1,2', 1, 254,
                                             [5988, 5989])]
        self.assertEqual(
            actual,
            [('10.1.1.1', 5988), ('10.1.1.1', 5989), ('10.1.1.2', 5988),
             ('10.1.1.2', 5989)])


if __name__ == '__main__':
    unittest.main()
