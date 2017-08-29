#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
    test wbemcli script.  This test generates a cmdline that calls
    wbemcli with a specific set of options and tests the returns.

    It dynamically generates the set of tests from the TEST_MAP table.
"""

from __future__ import print_function, absolute_import
import os
import unittest
from re import search
from subprocess import Popen, PIPE
import six

# Location of any test scripts for testing wbemcli.py
SCRIPT_DIR = os.path.dirname(__file__)


# Output fragments to test against for each test defined
# Each item is a list of fragmants that are tested against the cmd execution
# result
HELP_OUTPUT = ['subnet,',
               '--port', ]
SIMPLE_OUTPUT = ['5921',
                 'count=254',
                 '\'10.1.134\'', ]
CMPLEX1_OUTPUT = ['5921',
                  'count=4',
                  '\'10.1.134.10\', 5921']
CMPLEX2_OUTPUT = ['5921',
                  'count=20',
                  '\'10.1.134.10\', 5921']


# TODO change this to use named tuple for clarity
TESTS_MAP = {  # pylint: disable=invalid-name
    'help': ["--help", HELP_OUTPUT, None],
    'simple': ["10.1.134 -p 5921 --dryrun", SIMPLE_OUTPUT, None],
    'complex1': ["10.1.134.1,10 -p 5921 5922 --dryrun", CMPLEX1_OUTPUT, None],
    'complex2': ["10.1.134.1:10 -p 5921 5922 --dryrun", CMPLEX2_OUTPUT, None], }


class ContainerMeta(type):
    """Class to define the function to generate unittest methods."""

    def __new__(mcs, name, bases, dict):  # pylint: disable=redefined-builtin
        def gen_test(test_name, cmd_str, expected_stdout, expected_stderr):
            """
            Defines the test method that we generate for each test
            and returns the method.

            The cmd_str defines ONLY the arguments and options part of the
            command.  This function prepends wbemcli to the cmd_str.

            Since wbemcli is interactive, it also includes a quit script

            Each test builds the pywbemcli command executes it and tests the
            results
            """
            def test(self):  # pylint: disable=missing-docstring
                """ The test method that is generated.
                """
                command = 'serversweep %s' % cmd_str
                # Disable python warnings for wbemcli call.
                # This is because some imports generate deprecated warnings.
                command = 'export PYTHONWARNINGS="" && %s' % command
                proc = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
                std_out, std_err = proc.communicate()
                exitcode = proc.returncode
                if six.PY3:
                    std_out = std_out.decode()
                    std_err = std_err.decode()

                if exitcode != 0:
                    print('exitcode %s, err %s' % (exitcode, std_err))
                self.assertEqual(exitcode, 0, ('%s: ExitCode Err, cmd="%s" '
                                               'exitcode %s' %
                                               (test_name, command, exitcode)))

                if not expected_stderr:
                    self.assertEqual(std_err, "",
                                     '%s stderr not empty. returned %s'
                                     % (test_name, std_err))
                else:
                    for item in expected_stderr:
                        match_result = search(item, std_err)
                        self.assertIsNotNone(match_result,
                                             "Expecting smatch for "
                                             "stderr match item %s in %s" %
                                             (item, std_err))

                for item in expected_stdout:
                    match_result = search(item, std_out)
                    self.assertIsNotNone(match_result,
                                         "Expecting match for "
                                         "stdout match item %s in %s" %
                                         (item, std_out))
            return test

        for test_name, params in six.iteritems(TESTS_MAP):
            test_name = "test_%s" % test_name
            dict[test_name] = gen_test(test_name, params[0], params[1],
                                       params[2])
        return type.__new__(mcs, name, bases, dict)


@six.add_metaclass(ContainerMeta)
class TestsContainer(unittest.TestCase):
    """Container class for all tests"""
    __metaclass__ = ContainerMeta


if __name__ == '__main__':
    unittest.main()
