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

import unittest
import StringIO
import sys
import re

from smipyping._tableoutput import print_table, build_table, fold_cell

class TableTests(unittest.TestCase):
    def create_simple_table(self):
        """Create a standard table"""
        headers = ['col1', 'col2', 'col3']
        row1 = ['row1col1', 'row2col2', 'row3col3']
        row2 = ['row2col1', 'row2col2', 'row2col3']
        rows = [row1, row2]
        title = 'test_table'
        return (rows, headers, title)

    def create_folded_table(self):
        """Create a table with folded cells"""
        headers = ['col1', 'col2', 'col3']
        folded = fold_cell('this is a folded cell', 10)
        row1 = ['row1col1', 'row2col2', folded]
        row2 = [folded, 'row2col2', 'row2col3']
        rows = [row1, row2]
        title = 'test_folded_table'
        return (rows, headers, title)

class AsciiTableTests(TableTests):
    """Tests on the asciitable module"""

    def create_simple_table(self):
        """Create a standard table"""
        headers = ['col1', 'col2', 'col3']
        row1 = ['row1col1', 'row2col2', 'row3col3']
        row2 = ['row2col1', 'row2col2', 'row2col3']
        rows = [row1, row2]
        title = 'test_table'
        return (rows, headers, title)

    def create_folded_table(self):
        """Create a table with folded cells"""
        headers = ['col1', 'col2', 'col3']
        folded = fold_cell('this is a folded cell', 10)
        row1 = ['row1col1', 'row2col2', folded]
        row2 = [folded, 'row2col2', 'row2col3']
        rows = [row1, row2]
        title = 'test_folded_table'
        return (rows, headers, title)

    def test_table_simple(self):
        """Test a simple table with header"""

        captured_output = StringIO.StringIO()          # Create StringIO object
        sys.stdout = captured_output                   # and redirect stdout.
        rows, headers, title = self.create_simple_table()
        print_table(rows, headers, title=title, table_format='simple')
        sys.stdout = sys.__stdout__  # pylint: disable=redefined-variable-type
        print('Captured\n%s' % captured_output.getvalue())  # Restored

        match_result = re.search(r'col1      col2      col3',
                                 captured_output.getvalue())
        self.assertIsNotNone(match_result, 'Expected match %s to %s' %
                             ('col1      col2      col3',
                              captured_output.getvalue()))

        search_result = re.search(r'row1col1  row2col2  row3col3',
                                  captured_output.getvalue())
        self.assertIsNotNone(search_result, 'Expected match')

    def test_table_plain(self):
        """Test a none table borders with header"""

        captured_output = StringIO.StringIO()          # Create StringIO object
        sys.stdout = captured_output                   # and redirect stdout.

        rows, headers, title = self.create_simple_table()

        print_table(rows, headers, title=title, table_format='plain')

        sys.stdout = sys.__stdout__  # pylint: disable=redefined-variable-type
        print('Captured\n%s' % captured_output.getvalue())  # Restored
        match_result = re.search(r'col1      col2      col3',
                                 captured_output.getvalue())
        self.assertIsNotNone(match_result, 'Expected match %s to %s' %
                             ('col1      col2      col3',
                              captured_output.getvalue()))

    def test_table_grid(self):
        """Test a plain table with borders and header"""
        captured_output = StringIO.StringIO()          # Create StringIO object
        sys.stdout = captured_output                   # and redirect stdout.

        rows, headers, title = self.create_simple_table()

        print_table(rows, headers, title=title, table_format='grid')
        sys.stdout = sys.__stdout__  # pylint: disable=redefined-variable-type
        print('Captured\n%s' % captured_output.getvalue())  # Restored

        match_result = re.search(r'| col1     | col2     | col3     |',
                                 captured_output.getvalue())
        self.assertIsNotNone(match_result, 'Expected match %s to %s' %
                             ('| col1     | col2     | col3     |',
                              captured_output.getvalue()))

    def test_table_default(self):
        """Test a table with default format"""
        captured_output = StringIO.StringIO()          # Create StringIO object
        sys.stdout = captured_output                   # and redirect stdout.

        rows, headers, title = self.create_simple_table()

        print_table(rows, headers, title=title)
        sys.stdout = sys.__stdout__  # pylint: disable=redefined-variable-type
        print('Captured\n%s' % captured_output.getvalue())  # Restored

        match_result = re.search(r'col1      col2      col3',
                                 captured_output.getvalue())

        self.assertIsNotNone(match_result, 'Expected match %s to %s' %
                             ('col1      col2      col3',
                              captured_output.getvalue()))

    def test_folded_cell_plain(self):
        """Test a folded cell table with header"""

        rows, headers, title = self.create_folded_table()

        actual = build_table(rows, headers, title=title, table_format='plain')

        expected = (
            ' col1       col2      col3      \n'
            ' row1col1   row2col2  this is a \n'
            '                      folded    \n'
            '                      cell      \n'
            ' this is a  row2col2  row2col3  \n'
            ' folded                         \n'
            ' cell                           ')
        self.assertEqual(actual, expected,
            'Actual:\n%s\nExpected:\n%s\n' % (actual, expected))

    def test_folded_cell_simple(self):
        """Test a folded cell table with header"""
        captured_output = StringIO.StringIO()          # Create StringIO object
        sys.stdout = captured_output                   # and redirect stdout.

        rows, headers, title = self.create_folded_table()

        print_table(rows, headers, title=title, table_format='simple')
        sys.stdout = sys.__stdout__  # pylint: disable=redefined-variable-type
        print('Captured\n%s' % captured_output.getvalue())  # Restored

        match_result = re.search(r' col1       col2      col3',
                                 captured_output.getvalue())
        self.assertIsNotNone(match_result, 'Expected match %s to %s' %
                             (' col1       col2      col3',
                              captured_output.getvalue()))

        match_result = re.search(r'--------------------------',
                                 captured_output.getvalue())
        self.assertIsNotNone(match_result, 'Expected match %s to %s' %
                             ('--------------------------',
                              captured_output.getvalue()))

        match_result = re.search(r' this is a  row2col2  row2col3',
                                 captured_output.getvalue())
        self.assertIsNotNone(match_result, 'Expected match %s to %s' %
                             (' this is a  row2col2  row2col3',
                              captured_output.getvalue()))

    def test_folded_cell_grid(self):
        """Test a folded cell table with header"""

        rows, headers, title = self.create_folded_table()

        actual = build_table(rows, headers, title=None, table_format='grid')

        expected = (
            '+-----------+----------+-----------+\n'
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
        self.assertEqual(actual, expected,
            'Actual:\n%s\nExpected:\n%s\n' % (actual, expected))

class HtmlTableTests(TableTests):
    """Tests on the asciitable module"""
    def test_simple_table(self):
        """Test a simple table with header"""

        captured_output = StringIO.StringIO()          # Create StringIO object
        sys.stdout = captured_output                   # and redirect stdout.
        rows, headers, title = self.create_simple_table()

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

    def test_complex_table(self):
        """Test a simple table with header"""

        captured_output = StringIO.StringIO()          # Create StringIO object
        sys.stdout = captured_output                   # and redirect stdout.
        headers = ['col1', 'col2', 'col3']
        row1 = ['row1col1', 'row1col2', 'row1col3']
        row2 = ['row2col1', 'row2col2', 'row2col3']
        row3 = ['row3col1', 'row3col2']
        row4 = ['row4col1LongCol', 'row4col2', 'row4col3']
        row5 = ['row5col1', 'row5col2', 'row5col3\nSecondRow']
        rows = [row1, row2, row3, row4, row5]
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


if __name__ == '__main__':
    unittest.main()
