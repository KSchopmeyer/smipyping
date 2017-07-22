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
Tests for functions in smipyping/_common.py
"""
from __future__ import print_function, absolute_import

import os
import unittest
import sys
import re

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from smipyping._tableoutput import print_table, build_table, fold_cell

VERBOSE = True


class TableTests(unittest.TestCase):
    """Base class for testing table output"""
    def create_simple_table(self):
        """Create a standard table"""
        headers = ['col1', 'col2', 'col3']
        rows = [['row1col1', 'row1col2', 'row1col3'],
                ['row2col1', 'row2col2', 'row2col3'],
                ['row3 col1', 'row3  col2', 'row3   col3'],
                [0, 999, 9999999],
                [1.1432, 1.2, 0]]
        title = 'test_table'
        return (rows, headers, title)

    def create_folded_table(self):
        """Create a table with folded cells"""
        headers = ['col1', 'col2', 'col3']
        folded = fold_cell('this is a folded cell', 10)
        rows = [['row1col1', 'row2col2', folded],
                [folded, 'row2col2', 'row2col3']]
        title = 'test_folded_table'
        return (rows, headers, title)

    def compare_results(self, actual, expected):
        """Compare two multiline strings to find differences. Helpful to
           find minor errors in the actual/expected outputs
        """
        if actual == expected:
            return
        actual_lines = actual.split(os.linesep)
        expected_lines = expected.split(os.linesep)
        if len(actual_lines) != len(expected_lines):
            print('Different number of lines actual %s, expected %s' %
                  (len(actual_lines), len(expected_lines)))
        line = 0
        for line_a, line_e in zip(actual_lines, expected_lines):
            if line_a != line_e:
                print('Line %s: Difference\n%s\n%s' % (line, line_a, line_e))
                if len(line_a) != len(line_e):
                    print('Different lengths act %s exp %s' % (len(line_a),
                                                               len(line_e)))
            line += 1


class AsciiTableTests(TableTests):
    """Tests on the asciitable module"""
    def test_table_simple(self):
        """Test a simple table with header"""

        captured_output = StringIO()          # Create StringIO object
        sys.stdout = captured_output                   # and redirect stdout.
        rows, headers, title = self.create_simple_table()
        print_table(rows, headers, title=title, table_format='simple')
        sys.stdout = sys.__stdout__  # pylint: disable=redefined-variable-type
        actual = captured_output.getvalue()
        if VERBOSE:
            print(actual)

        expected = ('col1       col2        col3\n'
                    '---------  ----------  -----------\n'
                    'row1col1   row1col2    row1col3\n'
                    'row2col1   row2col2    row2col3\n'
                    'row3 col1  row3  col2  row3   col3\n'
                    '0          999         9999999\n'
                    '1.1432     1.2         0\n\n')

        self.compare_results(actual, expected)

        self.assertEqual(actual, expected,
                         'Actual:\n%s\nExpected:\n%s\n' % (actual, expected))

    def test_table_simple_build(self):
        """Test a simple table with header build function"""

        rows, headers, title = self.create_simple_table()
        actual = build_table(rows, headers, title=title, table_format='simple')
        if VERBOSE:
            print(actual)

        expected = ('col1       col2        col3\n'
                    '---------  ----------  -----------\n'
                    'row1col1   row1col2    row1col3\n'
                    'row2col1   row2col2    row2col3\n'
                    'row3 col1  row3  col2  row3   col3\n'
                    '0          999         9999999\n'
                    '1.1432     1.2         0')
                    

        self.compare_results(actual, expected)
        self.assertEqual(actual, expected,
                         'Actual:\n%s\nExpected:\n%s\n' % (actual, expected))

    def test_table_plain(self):
        """Test a none table borders with header"""

        captured_output = StringIO()          # Create StringIO object
        sys.stdout = captured_output                   # and redirect stdout.

        rows, headers, title = self.create_simple_table()

        print_table(rows, headers, title=title, table_format='plain')

        sys.stdout = sys.__stdout__  # pylint: disable=redefined-variable-type
        actual = captured_output.getvalue()
        if VERBOSE:
            print(actual)

        expected = ('col1       col2        col3\n'
                    'row1col1   row1col2    row1col3\n'
                    'row2col1   row2col2    row2col3\n'
                    'row3 col1  row3  col2  row3   col3\n'
                    '0          999         9999999\n'
                    '1.1432     1.2         0\n\n')

        self.compare_results(actual, expected)
        self.assertEqual(actual, expected,
                         'Actual:\n%s\nExpected:\n%s\n' % (actual, expected))

    def test_table_grid(self):
        """Test a plain table with borders and header"""
        captured_output = StringIO()          # Create StringIO object
        sys.stdout = captured_output                   # and redirect stdout.

        rows, headers, title = self.create_simple_table()

        print_table(rows, headers, title=title, table_format='grid')
        sys.stdout = sys.__stdout__  # pylint: disable=redefined-variable-type
        actual = captured_output.getvalue()
        if VERBOSE:
            print(actual)

        expected = ('+-----------+------------+-------------+\n'
                    '| col1      | col2       | col3        |\n'
                    '+===========+============+=============+\n'
                    '| row1col1  | row1col2   | row1col3    |\n'
                    '+-----------+------------+-------------+\n'
                    '| row2col1  | row2col2   | row2col3    |\n'
                    '+-----------+------------+-------------+\n'
                    '| row3 col1 | row3  col2 | row3   col3 |\n'
                    '+-----------+------------+-------------+\n'
                    '| 0         | 999        | 9999999     |\n'
                    '+-----------+------------+-------------+\n'
                    '| 1.1432    | 1.2        | 0           |\n'
                    '+-----------+------------+-------------+\n\n')




        self.compare_results(actual, expected)
        self.assertEqual(actual, expected,
                         'Actual:\n%s\nExpected:\n%s\n' % (actual, expected))

    def test_table_default(self):
        """Test a table with default format"""
        captured_output = StringIO()          # Create StringIO object
        sys.stdout = captured_output                   # and redirect stdout.

        rows, headers, title = self.create_simple_table()

        print_table(rows, headers, title=title)
        sys.stdout = sys.__stdout__  # pylint: disable=redefined-variable-type
        actual = captured_output.getvalue()
        if VERBOSE:
            print(actual)

        expected = ('col1       col2        col3\n'
                    '---------  ----------  -----------\n'
                    'row1col1   row1col2    row1col3\n'
                    'row2col1   row2col2    row2col3\n'
                    'row3 col1  row3  col2  row3   col3\n'
                    '0          999         9999999\n'
                    '1.1432     1.2         0\n\n')

        self.compare_results(actual, expected)
        self.assertEqual(actual, expected,
                         'Actual:\n%s\nExpected:\n%s\n' % (actual, expected))

    def test_folded_cell_plain(self):
        """Test a folded cell table plain with header"""

        rows, headers, title = self.create_folded_table()

        actual = build_table(rows, headers, title=title, table_format='plain')
        if VERBOSE:
            print(actual)

        expected = (
            ' col1       col2      col3      \n'
            ' row1col1   row2col2  this is a \n'
            '                      folded    \n'
            '                      cell      \n'
            ' this is a  row2col2  row2col3  \n'
            ' folded                         \n'
            ' cell                           ')

        self.compare_results(actual, expected)
        self.assertEqual(actual, expected,
                         'Actual:\n%s\nExpected:\n%s\n' % (actual, expected))

    def test_folded_cell_simple(self):
        """Test a folded cell table simplewith header"""
        captured_output = StringIO()          # Create StringIO object
        sys.stdout = captured_output                   # and redirect stdout.

        rows, headers, title = self.create_folded_table()

        print_table(rows, headers, title=title, table_format='simple')
        sys.stdout = sys.__stdout__  # pylint: disable=redefined-variable-type
        actual = captured_output.getvalue()
        if VERBOSE:
            print(actual)

        expected = (
            ' col1       col2      col3      \n'
            '--------------------------------\n'
            ' row1col1   row2col2  this is a \n'
            '                      folded    \n'
            '                      cell      \n'
            ' this is a  row2col2  row2col3  \n'
            ' folded                         \n'
            ' cell                           \n\n')

        self.compare_results(actual, expected)
        self.assertEqual(actual, expected,
                         'Actual:\n%s\nExpected:\n%s\n' % (actual, expected))

    def test_folded_cell_grid(self):
        """Test a folded cell table with header"""

        rows, headers, title = self.create_folded_table()

        actual = build_table(rows, headers, title=None, table_format='grid')

        if VERBOSE:
            print(actual)

        expected = ('+-----------+----------+-----------+\n'
                    '| col1      | col2     | col3      |\n'
                    '+-----------+----------+-----------+\n'
                    '| row1col1  | row2col2 | this is a |\n'
                    '|           |          | folded    |\n'
                    '|           |          | cell      |\n'
                    '+-----------+----------+-----------+\n'
                    '| this is a | row2col2 | row2col3  |\n'
                    '| folded    |          |           |\n'
                    '| cell      |          |           |\n'
                    '+-----------+----------+-----------+')

        self.compare_results(actual, expected)
        self.assertEqual(actual, expected,
                         'Actual:\n%s\nExpected:\n%s\n' % (actual, expected))


class HtmlTableTests(TableTests):
    """Tests on the asciitable module"""
    def test_simple_table(self):
        """Test a simple table with header"""

        captured_output = StringIO()          # Create StringIO object
        sys.stdout = captured_output                   # and redirect stdout.
        rows, headers, title = self.create_simple_table()

        print_table(rows, headers, title=title, table_format='html')
        sys.stdout = sys.__stdout__  # pylint: disable=redefined-variable-type
        print('Captured\n%s' % captured_output.getvalue())

    def test_complex_table(self):
        """Test a simple table with header"""

        captured_output = StringIO()          # Create StringIO object
        sys.stdout = captured_output                   # and redirect stdout.
        headers = ['col1', 'col2', 'col3']
        rows = [['row1col1', 'row1col2', 'row1col3'],
                ['row2col1', 'row2col2', 'row2col3'],
                ['row3col1', 'row3col2'],
                ['row4col1LongCol', 'row4col2', 'row4col3'],
                ['row5col1', 'row5col2', 'row5col3\nSecondRow']]
        title = 'test_HTML_table'
        print_table(rows, headers, title=title, table_format='html')
        sys.stdout = sys.__stdout__  # pylint: disable=redefined-variable-type
        print('Captured\n%s' % captured_output.getvalue())

        match_result = re.search(r'<TH>col1</TH>',
                                 captured_output.getvalue())
        self.assertIsNotNone(match_result, 'Expected match %s to %s' %
                             ('<TH>col3</TH>',
                              captured_output.getvalue()))

        search_result = re.search(r'<TD>row1col1</TD>',
                                  captured_output.getvalue())
        self.assertIsNotNone(search_result, 'Expected match')


class CsvTableTests(TableTests):
    """Test generating csv format output tables"""

    def test_table_simple_build(self):
        """Test a simple table csv with header"""
        rows, headers, title = self.create_simple_table()
        actual = build_table(rows, headers, title=title, table_format='csv')
        if VERBOSE:
            print(actual)

        expected = ('"col1","col2","col3"\n'
                    '"row1col1","row1col2","row1col3"\n'
                    '"row2col1","row2col2","row2col3"\n'
                    '"row3 col1","row3  col2","row3   col3"\n'
                    '0,999,9999999\n'
                    '1.1432,1.2,0\n')

        self.compare_results(actual, expected)
        self.assertEqual(actual, expected,
                         'Actual:\n%s\nExpected:\n%s\n' % (actual, expected))


if __name__ == '__main__':
    unittest.main()
