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
    """Unit test for SimplePing Class"""
    def test_server0(self):
        """Test with valid server param"""
        sim_ping = SimplePing('http://localhost')
        self.assertEqual(sim_ping.url, 'http://localhost')
        conn = sim_ping.connect_server(sim_ping.url, verify_cert=False)
        print(sim_ping.get_connection_info(conn))

    def test_server1(self):
        """Test with valid server param"""
        sim_ping = SimplePing('https://localhost')
        self.assertEqual(sim_ping.url, 'https://localhost')

    def test_server2(self):
        """Test with valid server param"""
        sim_ping = SimplePing(server='http://localhost', user='fred',
                              password='xx', timeout=10, ping=False)
        self.assertEqual(sim_ping.url, 'http://localhost')
        self.assertEqual(sim_ping.timeout, 10)
        self.assertEqual(sim_ping.ping, False)
        self.assertEqual(sim_ping.user, 'fred')
        self.assertEqual(sim_ping.password, 'xx')
        conn = sim_ping.connect_server(sim_ping.url, verify_cert=False)
        self.assertEqual(conn.url, 'http://localhost')
        banner = sim_ping.get_connection_info(conn)
        match_result = re.match(r'Connection: http://localhost', banner)
        self.assertIsNotNone(match_result)

    def test_target_id(self):
        """Test with valid target id"""
        sim_ping = SimplePing(target_id=4)
        self.assertEqual(sim_ping.target_id, 4)

    def test_invalid_server(self):
        """Test for invalid server schema"""
        try:
            SimplePing(server='httpx://localhost')
            self.fail('Exception expected')
        except ValueError:
            pass

    def test_dup_id(self):
        """Test duplicate ID"""
        try:
            SimplePing(server='http://localhost', target_id=4)
            self.fail('Expected exception')
        except ValueError:
            pass


if __name__ == '__main__':
    unittest.main()
