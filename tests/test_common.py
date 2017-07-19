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
from mock import patch

from smipyping._common import pick_from_list, pick_multiple_from_list
from smipyping._click_context import ClickContext


class TestPickFromList(unittest.TestCase):
    """Tests for pick_from_list. Mocked response"""
    def test_valid_pick(self):
        """Execute valid pick from a list"""
        list_ = ["aaa", "bbb", "ccc"]
        prompt_txt = 'Select an entry by index or enter Ctrl-C to exit >'
        with patch('smipyping._common.prompt', return_value='1') as prompt:
            ctx = ClickContext(None, None, None, None, None, None, None, None)
            self.assertEqual(pick_from_list(ctx, list_, prompt_txt), 1)
            prompt.assert_called_once_with(prompt_txt)


class TestPickFromMultiplesList(unittest.TestCase):
    """Tests for pick_from_list. Mocked response"""
    def test_valid_pick(self):
        """Execute valid pick from a multipleslist"""
        list_ = ["aaa", "bbb", "ccc"]
        prompt_txt = 'Select multiple entries by index or Ctrl-C to exit >'
        with patch('smipyping._common.prompt', return_value='1') as prompt:
            ctx = ClickContext(None, None, None, None, None, None, None, None)
            self.assertEqual(pick_multiple_from_list(ctx, list_, prompt_txt),
                             [1])
            prompt.assert_called_once_with(prompt_txt)

    def test_valid_pick2(self):
        """Execute valid pick from a multipleslist"""
        list_ = ["aaa", "bbb", "ccc"]
        prompt_txt = 'Select multiple entries by index or Ctrl-C to exit >'
        with patch('smipyping._common.prompt', return_value='1 2') as prompt:
            ctx = ClickContext(None, None, None, None, None, None, None, None)
            self.assertEqual(pick_multiple_from_list(ctx, list_, prompt_txt),
                             [1, 2])
            prompt.assert_called_once_with(prompt_txt)


if __name__ == '__main__':
    unittest.main()