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
    Test the components of the simpleping.py module
"""

from __future__ import absolute_import, print_function

import unittest
import re

from smipyping import SimplePing


class CommandLineTestCase(unittest.TestCase):
    """
    Base TestCase class, sets up a CLI parser
    """
    # TODO extend these tests. In particular test setting from target data.

    
class SimplePingTestCase(CommandLineTestCase):

    def test_server0(self):
        """Test with valid server param"""
        sp = SimplePing('http://localhost')
        self.assertEqual(sp.url, 'http://localhost')
        conn = sp.connect_server(sp.url, verify_cert=False)
        print(sp.get_connection_info(conn))

    def test_server1(self):
        """Test with valid server param"""
        sp = SimplePing('https://localhost')
        self.assertEqual(sp.url, 'https://localhost')

    def test_server2(self):
        """Test with valid server param"""
        sp = SimplePing(server='http://localhost', user='fred', password='xx',
                        timeout=10, ping=False)
        self.assertEqual(sp.url, 'http://localhost')
        self.assertEqual(sp.timeout, 10)
        self.assertEqual(sp.ping, False)
        self.assertEqual(sp.user, 'fred')
        self.assertEqual(sp.password, 'xx')
        conn = sp.connect_server(sp.url, verify_cert=False)
        self.assertEqual(conn.url, 'http://localhost')
        banner = sp.get_connection_info(conn)
        match_result = re.match(r'Connection: http://localhost', banner)
        self.assertIsNotNone(match_result)

    def test_target_id(self):
        sp = SimplePing(target_id=4)
        self.assertEqual(sp.target_id, 4)

    def test_invalid_server(self):
        try:
            SimplePing(server='httpx://localhost')
            self.fail('Exception expected')
        except ValueError:
            pass

    def test_dup_id(self):
        try:
            SimplePing(server='http://localhost', target_id=4)
            self.fail('Expected exception')
        except ValueError:
            pass


if __name__ == '__main__':
    unittest.main()
