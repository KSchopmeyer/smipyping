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

from smipyping._asciitable import print_table, fold_cell


class AsciiTableTests(unittest.TestCase):
    """Tests on the asciitable module"""
    def test_simple_table(self):
        """Test a simple table with header"""

        capturedOutput = StringIO.StringIO()          # Create StringIO object
        sys.stdout = capturedOutput                   # and redirect stdout.
        header = ['col1', 'col2', 'col3']
        row1 = ['row1col1', 'row2col2', 'row3col3']
        row2 = ['row2col1', 'row2col2', 'row2col3']
        table_data = [row1, row2]
        title = 'test_simple_table'
        print_table(header, table_data, title)
        sys.stdout = sys.__stdout__                   # Reset redirect.
        print('Captured\n%s' % capturedOutput.getvalue())  # Now works as before

        match_result = re.search(r' col1      col2      col3',
                                 capturedOutput.getvalue())
        self.assertIsNotNone(match_result, 'Expected match %s to %s' %
                             (' col1      col2      col3',
                              capturedOutput.getvalue()))

        search_result = re.search(r' row1col1  row2col2  row3col3',
                                  capturedOutput.getvalue())
        self.assertIsNotNone(search_result, 'Expected match')

    # TODO we do not know how to test tables with borders.
    def test_none_table_borders(self):
        """Test a none table borders with header"""

        capturedOutput = StringIO.StringIO()          # Create StringIO object
        sys.stdout = capturedOutput                   # and redirect stdout.

        header = ['col1', 'col2', 'col3']
        row1 = ['row1col1', 'row2col2', 'row3col3']
        row2 = ['row2col1', 'row2col2', 'row2col3']
        table_data = [row1, row2]
        title = 'test_none_table'
        print("")
        print_table(header, table_data, title)
        sys.stdout = sys.__stdout__                   # Reset redirect.
        match_result = re.search(r' col1      col2      col3',
                                 capturedOutput.getvalue())
        self.assertIsNotNone(match_result, 'Expected match %s to %s' %
                             (' col1      col2      col3',
                              capturedOutput.getvalue()))

    def test_plain_table_borders(self):
        """Test a plain table with borders and header"""
        capturedOutput = StringIO.StringIO()          # Create StringIO object
        sys.stdout = capturedOutput                   # and redirect stdout.

        header = ['col1', 'col2', 'col3']
        row1 = ['row1col1', 'row2col2', 'row2col3']
        row2 = ['row2col1', 'row2col2', 'row2col3']
        table_data = [row1, row2]
        title = 'test_bordered_table'
        print("")
        print_table(header, table_data, title, table_type='plain')
        sys.stdout = sys.__stdout__                   # Reset redirect.
        match_result = re.search(r' col1      col2      col3',
                                 capturedOutput.getvalue())
        self.assertIsNotNone(match_result, 'Expected match %s to %s' %
                             (' col1      col2      col3',
                              capturedOutput.getvalue()))

    def test_grid_table_borders(self):
        """Test a grid table with borders andheader"""
        capturedOutput = StringIO.StringIO()          # Create StringIO object
        sys.stdout = capturedOutput                   # and redirect stdout.
        header = ['col1', 'col2', 'col3']
        row1 = ['row1col1', 'row2col2', 'row3col3']
        row2 = ['row2col1', 'row2col2', 'row2col3']
        table_data = [row1, row2]
        title = 'test_grid_table'
        print("")
        print_table(header, table_data, title, table_type='grid')

        match_result = re.search(r' col1      col2      col3',
                                 capturedOutput.getvalue())
                                 
        self.assertIsNotNone(match_result, 'Expected match %s to %s' %
                             (' col1      col2      col3',
                              capturedOutput.getvalue()))

    def test_folded_cell(self):
        """Test a folded cell table with header"""
        capturedOutput = StringIO.StringIO()          # Create StringIO object
        sys.stdout = capturedOutput                   # and redirect stdout.

        header = ['col1', 'col2', 'col3']
        folded = fold_cell('this is a folded cell', 10)
        row1 = ['row1col1', 'row2col2', folded]
        row2 = [folded, 'row2col2', 'row2col3']
        table_data = [row1, row2]
        title = 'test_folded_table'
        print("")
        print_table(header, table_data, title)

        match_result = re.search(r' col1       col2      col3',
                                 capturedOutput.getvalue())
        self.assertIsNotNone(match_result, 'Expected match %s to %s' %
                             (' col1       col2      col3',
                              capturedOutput.getvalue()))

        match_result = re.search(r' this is a  row2col2  row2col3',
                                 capturedOutput.getvalue())
        self.assertIsNotNone(match_result, 'Expected match %s to %s' %
                             (' this is a  row2col2  row2col3',
                              capturedOutput.getvalue()))


class HtmlTableTests(unittest.TestCase):
    """Tests on the asciitable module"""
    def test_simple_table(self):
        """Test a simple table with header"""

        capturedOutput = StringIO.StringIO()          # Create StringIO object
        sys.stdout = capturedOutput                   # and redirect stdout.
        header = ['col1', 'col2', 'col3']
        row1 = ['row1col1', 'row1col2', 'row1col3']
        row2 = ['row2col1', 'row2col2', 'row2col3']
        table_data = [row1, row2]
        title = 'test_HTML_table'
        print_table(header, table_data, title, table_type='html')
        sys.stdout = sys.__stdout__                   # Reset redirect.
        # print('Captured\n%s' % capturedOutput.getvalue())

        match_result = re.search(r'<TH>col1</TH>',
                                 capturedOutput.getvalue())
        self.assertIsNotNone(match_result, 'Expected match %s to %s' %
                             ('<TH>col3</TH>',
                              capturedOutput.getvalue()))

        search_result = re.search(r'<TD>row1col1</TD>',
                                  capturedOutput.getvalue())
        self.assertIsNotNone(search_result, 'Expected match')

    def test_complex_table(self):
        """Test a simple table with header"""

        capturedOutput = StringIO.StringIO()          # Create StringIO object
        sys.stdout = capturedOutput                   # and redirect stdout.
        header = ['col1', 'col2', 'col3']
        row1 = ['row1col1', 'row1col2', 'row1col3']
        row2 = ['row2col1', 'row2col2', 'row2col3']
        row3 = ['row3col1', 'row3col2']
        row4 = ['row4col1LongCol', 'row4col2', 'row4col3']
        row5 = ['row5col1', 'row5col2', 'row5col3\nSecondRow']
        # print('row5 %s' % row5)
        table_data = [row1, row2, row3, row4, row5]
        title = 'test_HTML_table'
        print_table(header, table_data, title, table_type='html')
        sys.stdout = sys.__stdout__                   # Reset redirect.
        # print('Captured\n%s' % capturedOutput.getvalue())

        match_result = re.search(r'<TH>col1</TH>',
                                 capturedOutput.getvalue())
        self.assertIsNotNone(match_result, 'Expected match %s to %s' %
                             ('<TH>col3</TH>',
                              capturedOutput.getvalue()))

        search_result = re.search(r'<TD>row1col1</TD>',
                                  capturedOutput.getvalue())
        self.assertIsNotNone(search_result, 'Expected match')


if __name__ == '__main__':
    unittest.main()
