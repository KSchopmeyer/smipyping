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
import os
import unittest
import logging
# from testfixtures import log_capture

from smipyping._logging import get_logger, SmiPypingLoggers

VERBOSE = False

# Location of any test scripts for testing wbemcli.py
SCRIPT_DIR = os.path.dirname(__file__)

LOG_FILE_NAME = 'test_logging.log'
TEST_OUTPUT_LOG = '%s/%s' % (SCRIPT_DIR, LOG_FILE_NAME)

# TODO add test of actual logging.


class BaseLoggingTests(unittest.TestCase):
    """Base class for logging unit tests"""
    def setUp(self):
        SmiPypingLoggers.reset()
        if os.path.isfile(TEST_OUTPUT_LOG):
            os.remove(TEST_OUTPUT_LOG)

    def tearDown(self):

        # Close any open logging files
        # Windows log files be closed to be removed.
        if os.path.isfile(TEST_OUTPUT_LOG):
            logger = logging.getLogger('testlogger')
            if logger.handlers:
                handlers = logger.handlers[:]
                for handler in handlers:
                    handler.close()
                    logger.removeHandler(handler)

            os.remove(TEST_OUTPUT_LOG)

    def loadLogfile(self):
        if os.path.isfile(TEST_OUTPUT_LOG):
            with open(TEST_OUTPUT_LOG) as f:
                lines = f.read().splitlines()
                return lines
        return None


class TestGetLogger(unittest.TestCase):
    """All test cases for get_logger()."""

    def test_root_logger(self):
        """Test that get_logger('') returns the Python root logger and has at
        least one handler."""
        py_logger = logging.getLogger()

        my_logger = get_logger('')

        self.assertTrue(isinstance(my_logger, logging.Logger))
        self.assertEqual(my_logger, py_logger)
        self.assertTrue(len(my_logger.handlers) >= 1,
                        "Unexpected list of logging handlers: %r" %
                        my_logger.handlers)

    def test_foo_logger(self):
        """Test that get_logger('foo') returns the Python logger 'foo'
        and has at least one handler."""
        py_logger = logging.getLogger('foo')

        my_logger = get_logger('foo')

        self.assertTrue(isinstance(my_logger, logging.Logger))
        self.assertEqual(my_logger, py_logger)
        self.assertTrue(len(my_logger.handlers) >= 1,
                        "Unexpected list of logging handlers: %r" %
                        my_logger.handlers)


class TestLoggerCreate(BaseLoggingTests):
    """ Test the SmipypingLoggers.create_logger method."""
    def test_create_single_logger1(self):
        """
        Create a simple logger
        """
        SmiPypingLoggers.prog = 'test_logging'
        SmiPypingLoggers.create_logger('testlogger', log_dest='file',
                                       log_filename=TEST_OUTPUT_LOG,
                                       log_level='debug')

        if VERBOSE:
            print('smipyping_loggers dict %s' % SmiPypingLoggers.loggers)
        expected_result = \
            {'test_logging.testlogger': ('debug', 'file',
                                         TEST_OUTPUT_LOG)}

        self.assertEqual(SmiPypingLoggers.loggers, expected_result)


if __name__ == '__main__':
    unittest.main()
