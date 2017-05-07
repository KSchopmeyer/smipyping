#!/usr/bin/env python
"""
    Test the components of the simpleping.py module
"""

from __future__ import absolute_import, print_function

import shlex
import unittest

from smipyping import SimplePing


class CommandLineTestCase(unittest.TestCase):
    """
    Base TestCase class, sets up a CLI parser
    """
    def setUp(self):
        """Setup the SimplePing instance and parser"""
        # create an instance of SimplePing named test
        self.simpleping = SimplePing("test")
        self.simpleping.create_parser()

    def parse(self, args):
        """Call the simpleping parser with input list of arguments"""
        print('test parse %s' % args)
        arg_list = shlex.split(args)
        opts = self.simpleping.parse_cmdline(input_params=arg_list)
        return opts

    def parse_with_exception(self, args):
        """Call the simpleping parser with input list of arguments.
        Expects an exception
        """
        try:
            arg_list = shlex.split(args)
            print('Split args %s' % arg_list)
            self.simpleping.parse_cmdline(input_params=arg_list)
        except Exception as ex:
            print('exception %s' % ex)
        except SystemExit as se:
            print('argparse error %s' % se)
        else:
            self.fail('Exception expected')


class PingTestCase(CommandLineTestCase):
    def test_with_empty_args(self):
        """
        User passes no args, should fail with SystemExit
        """
        self.parse_with_exception("")

    def test_simple(self):
        args = self.parse('http://localhost -n root')
        self.assertEqual(args.server, 'http://localhost')
        self.assertEqual(args.namespace, 'root')

    def test_cmdline_no_ns(self):
        args = self.parse_with_exception('http://localhost')


    def test_cmdline2(self):
        args = self.parse('http://localhost -n root --user fred')
        print('args %s' % args)
        self.assertEqual(args.server, 'http://localhost')
# ./simpleping https://10.1.132.185 -u pureuser -p pureuser -d

    def test_cmdline3(self):
        """Test parse of legal with user and connect"""
        args = self.parse('http://localhost -n root -u blah')
        self.assertEqual(args.server, 'http://localhost')
        conn = self.simpleping.connect_server(args.server)
        print('conn %s' % conn)


if __name__ == '__main__':
    unittest.main()
