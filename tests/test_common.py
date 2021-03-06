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
import sys
from datetime import datetime
from mock import patch
# from testfixtures import OutputCapture
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import pytest

from smicli._click_common import pick_from_list, pick_multiple_from_list, \
    print_table, validate_prompt
from smicli._click_context import ClickContext

from smipyping._common import get_list_index, filter_stringlist, StrList, \
    compute_startend_dates

VERBOSE = True


class Test_ComputeStartendDates(object):
    """
    Test the compute_startend_dates function
    """
    # parameters are:
    # start the start date as text in format %d/%m/%Y
    # end date as text in same format
    # num - number_of days or None
    # old - Oldest date in same text format or None
    # exp - Tuple of expected start and end dates in same text format
    # exc - None or expected exception
    @pytest.mark.parametrize(
        "start, end, num, old, exp, exc", [
            # test for valid response to start and end date
            ["01/01/18", "09/09/18", None, None, ("01/01/18", "09/09/18"),
             None],
            # test for valid response to date and number_of_days
            ["01/01/18", None, 9, None, ("01/01/18", "10/01/18"), None],
            # test for valid response with oldest set
            [None, None, 9, "01/01/18", ("01/01/18", "10/01/18"), None],
            # Test for Value error if both start and end date
            ["01/01/18", "01/01/18", 9, None, (), ValueError],
            # end date before start date
            ["01/01/18", "01/01/17", None, None, None, ValueError],
            # test for error if number of days negative
            ["01/01/18", None, -9, None, ("01/01/18", "10/01/18"), ValueError],
        ]
    )
    # TODO add more tests here.
    def test_compute_startend_dates(self, start, end, num, old, exp, exc):
        """Test the function"""
        fmt = "%d/%m/%y"
        if start:
            start = datetime.strptime(start, fmt)
        if old:
            old = datetime.strptime(old, fmt)
        if end:
            end = datetime.strptime(end, fmt)
        if exp:
            exp_rslt = (datetime.strptime(exp[0], fmt),
                        datetime.strptime(exp[1], fmt))

        if not exc:
            assert compute_startend_dates(start, end_date=end,
                                          number_of_days=num,
                                          oldest_date=old) == exp_rslt
        else:
            with pytest.raises(ValueError):
                assert compute_startend_dates(start, end_date=end,
                                              number_of_days=num,
                                              oldest_date=old) == exp_rslt


class TestGetListIndex(object):
    """
    Test the get_list_index function
    """
    # parameters are lst(list of strings), sel(selection)
    @pytest.mark.parametrize(
        "lst, sel, exp, exc", [
            [['abc', 'def'], 'def', 1, None],
            [['abc', 'def'], 'abc', 0, None],
            [['ABC', 'DEF'], 'abc', 0, None],
            [['ABC', 'DEF'], 'def', 1, None],
            [['AB\nC', 'DE\nF'], 'def', 1, None],
            [['\nAB\nC\n', '\nDE\nF\n'], 'def', 1, None],
            [['AB\nC', 'DE\nF'], 'def', 1, None],
            [['abc', 'def'], 'ABC', 0, None],
            [['abc', 'def'], 'xyz', 0, True],
        ]
    )
    def test_get_list_index(self, lst, sel, exp, exc):
        """Test case get_list_index"""
        if not exc:
            assert get_list_index(lst, sel) == exp
        else:
            with pytest.raises(ValueError):
                assert get_list_index(lst, sel) == exp


class TestFilterStringlist(object):
    """Test the common filter_namelist function."""

    @pytest.mark.parametrize(
        "tst, exp", [
            ['TST_', ['TST_abc']],
            ['TSt_', ['TST_abc']],
            ['XST_', []],
            ['CIM_', ['CIM_abc', 'CIM_def', 'CIM_123']]
        ]
    )
    def test_case_no_optional(self, tst, exp):
        """Test case insensitive match"""
        name_list = ['CIM_abc', 'CIM_def', 'CIM_123', 'TST_abc']

        assert filter_stringlist(tst, name_list) == exp

    @pytest.mark.parametrize(
        "tst, exp, ignore_case", [
            ['TST_', ['TST_abc'], False],
            ['TST_', ['TST_abc'], True],
            ['TSt_', [], False],
            ['TSt_', ['TST_abc'], True],
            ['XST_', [], False],
            ['XST_', [], True],
            ['CIM_', ['CIM_abc', 'CIM_def', 'CIM_123'], False],
            ['CIM_', ['CIM_abc', 'CIM_def', 'CIM_123'], True],
        ]
    )
    def test_case_general(self, tst, exp, ignore_case):
        """Test case sensitive matches"""
        name_list = ['CIM_abc', 'CIM_def', 'CIM_123', 'TST_abc']

        assert filter_stringlist(tst, name_list,
                                 ignore_case=ignore_case) == exp

    @pytest.mark.parametrize(
        "tst, exp, ignore_case", [
            [r'.*abc$', ['CIM_abc', 'TST_abc'], False],
            [r'.*def', ['CIM_def'], False],
        ]
    )
    def test_wildcard_filters(self, tst, exp, ignore_case):
        """Test more complex regex"""
        name_list = ['CIM_abc', 'CIM_def', 'CIM_123', 'TST_abc']

        assert filter_stringlist(tst, name_list, ignore_case=ignore_case) == exp


class TestPickFromList(object):
    """Tests for pick_from_list. Mocked response"""
    def test_valid_pick(self):
        """Execute valid pick from a list"""
        list_ = ["aaa", "bbb", "ccc"]
        prompt_txt = 'Input integer between 0 and 2 or Enter to abort ' \
                     'selection: '
        with patch('smicli._click_common.local_prompt', return_value='1') as \
                local_prompt:
            ctx = ClickContext(None, None, None, None, None, None, None,
                               None, None, None)
            assert pick_from_list(ctx, list_, prompt_txt) == 1
            local_prompt.assert_called_once_with(prompt_txt)


class TestPickFromMultiplesList(object):
    """Tests for pick_from_list. Mocked response"""
    def test_valid_pick(self):
        """Execute valid pick from a multipleslist"""
        list_ = ["aaa", "bbb", "ccc"]
        prompt_txt = 'Select multiple entries by index (index< index> or ' \
                     'Enter to abort >'
        with patch('smicli._click_common.local_prompt', return_value='1') as \
                local_prompt:
            ctx = ClickContext(None, None, None, None, None, None, None,
                               None, None, None)
            assert pick_multiple_from_list(ctx, list_, prompt_txt) == [1]
            local_prompt.assert_called_once_with(prompt_txt)

    def test_valid_pick2(self):
        """Execute valid pick from a multipleslist"""
        list_ = ["aaa", "bbb", "ccc"]
        prompt_txt = 'Select multiple entries by index (index< index> or ' \
                     'Enter to abort >'
        with patch('smicli._click_common.local_prompt', return_value='1 2') as \
                local_prompt:
            ctx = ClickContext(None, None, None, None, None, None, None,
                               None, None, None)
            assert pick_multiple_from_list(ctx, list_, prompt_txt) == [1, 2]
            local_prompt.assert_called_once_with(prompt_txt)


class TestValidatePrompt(object):
    """
    Test the click_common validate prompt
    """
    def test_valid_pick(self):
        """Execute validateprompt"""
        prompt_txt = 'blah blah'
        with patch('smicli._click_common.local_prompt', return_value='y') as \
                local_prompt:
            ClickContext(None, None, None, None, None, None, None,
                         None, None, None)
            assert validate_prompt(prompt_txt) is True
            local_prompt.assert_called_once_with(u'blah blah valid (y/n): ')


class TestPrintTable(object):

    @staticmethod
    def compare_results(actual, expected):
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

    @pytest.mark.parametrize(
        "out_fmt, exp_stdout_template", [
            ['simple',
             '\n\nsimple\n\n'
             'col1       col2        col3\n'
             '---------  ----------  -----------\n'
             'row1col1   row1col2    row1col3\n'
             'row2col1   row2col2    row2col3\n'
             'row3 col1  row3  col2  row3   col3\n'
             '0          999         9999999\n'
             '1.1432     1.2         0\n'],
        ]
    )
    def test_table_format(self, out_fmt, exp_stdout_template):
        """Test formatting of table output"""

        headers = ['col1', 'col2', 'col3']
        rows = [['row1col1', 'row1col2', 'row1col3'],
                ['row2col1', 'row2col2', 'row2col3'],
                ['row3 col1', 'row3  col2', 'row3   col3'],
                [0, 999, 9999999],
                [1.1432, 1.2, 0]]
        title = 'simple'
        captured_output = StringIO()          # Create StringIO object
        sys.stdout = captured_output          # and redirect stdout.

        print_table(rows, headers, title, table_format=out_fmt)
        sys.stdout = sys.__stdout__  # pylint: disable=redefined-variable-type
        actual = captured_output.getvalue()
        if VERBOSE:
            print('ACTUAL:\n%s\nEXPECTED:\n%s\n' % (actual,
                                                    exp_stdout_template))

        self.compare_results(actual, exp_stdout_template)

        assert actual == exp_stdout_template


# Regular expression used in TestVersionsClass
RE = r'^[0-9.]*$'


class TestVersionsClass(object):
    """
    Test the StrList function
    """
    @pytest.mark.parametrize(
        "ver_in, re, exp_str, exp_repr, exp_exc_type", [
            [['1.2.3', '2.3.4'], RE, '1.2.3, 2.3.4', ['1.2.3', '2.3.4'], None],
            ['1.2.3, 2.3.4', RE, '1.2.3, 2.3.4', ['1.2.3', '2.3.4'], None],
            ['1.2.3/2.3.4', RE, '1.2.3, 2.3.4', ['1.2.3', '2.3.4'], None],
            ['1.2.3 2.3.4', RE, '1.2.3, 2.3.4', ['1.2.3', '2.3.4'], None],
            [['1.2.3', '2.3.4'], RE, '1.2.3, 2.3.4', ['1.2.3', '2.3.4'], None],
            ['1.2.3', RE, '1.2.3', ['1.2.3'], None],
            # ['1.2.3, 1.2.3', RE, '1.2.3', ['1.2.3'], None],
            # TODO extend for errors, regex and input
        ]
    )
    def test_versions(self, ver_in, re, exp_str, exp_repr, exp_exc_type):
        """
            Test the variations of input and results.
        """

        if exp_exc_type:
            with pytest.raises(exp_exc_type):
                v = StrList(ver_in, match=re)
        else:
            v = StrList(ver_in, match=re)
            assert sorted(v.items) == sorted(exp_repr)
            assert str(v) == exp_str

    @pytest.mark.parametrize(
        "input1,input2, exp_rslt", [
            [['1.2.3', '2.3.4'], ['1.2.3', '2.3.4'], True],
            [['1.2.3', '2.3.5'], ['1.2.3', '2.3.4'], False],

        ]
    )
    def test_equal_versions(self, input1, input2, exp_rslt):
        """Test the equals method"""

        v1s = StrList(input1)
        v2s = StrList(input2)
        assert v1s.equal(v2s) == exp_rslt
