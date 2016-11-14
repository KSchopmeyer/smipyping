#!/usr/bin/env python
"""
    Test the components of the simpleping.py module
"""

from __future__ import absolute_import, print_function
import unittest

from smipyping import SimplePing


class CommandLineTestCase(unittest.TestCase):
    """
    Base TestCase class, sets up a CLI parser
    """
    @classmethod
    def setUpClass(cls):
        simpleping = SimplePing("test")
        cls.simpleping = simpleping
        parser = simpleping.create_parser()
        cls.parser = parser


class PingTestCase(CommandLineTestCase):
    def test_with_empty_args(self):
        """
        User passes no args, should fail with SystemExit
        """
        with self.assertRaises(SystemExit):
            self.parser.parse_args([])

    def test_simple(self):
        args = self.parser.parse_args(['http://localhost'])
        self.assertEqual(args['server'] == 'http://localhost')

    def test_cmdline2(self):
        args = self.parser.parse_args(['http://localhost', 'user=blah'])
        print('args %s' % args)
        self.assertEqual(args['server'] == 'http://localhost')
# ./simpleping https://10.1.132.185 -u pureuser -p pureuser -d

    def test_cmdline3(self):
        args = self.parser.parse_args(['http://localhost', 'user=blah'])
        self.assertEqual(args['server'] == 'http://localhost')
        result = connect(args.server, args, arg_parser)
