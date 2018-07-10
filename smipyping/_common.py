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
    Common functions for the smipyping. Note that click common functions
    are in a separate package.
"""


from __future__ import absolute_import, unicode_literals

import re
import six

__all__ = ['get_list_index', 'build_table_struct', 'filter_stringlist']


def filter_stringlist(regex, string_list, ignore_case=True):
    """
    Filter out names in string_list that do not match regex input parameter.

    Note that the regex may define a subset of the name string.  Thus,  regex:
        - CIM matches any name that starts with CIM
        - CIM_abc matches any name that starts with CIM_abc
        - CIM_ABC$ matches only the name CIM_ABC.

    Parameters:
      regex (:term: `String`) Python regular expression to match

      name_list: List of strings to be matched.

      ignore_case: bool. If True, do case-insensitive match. Default = True

    Returns the list of strings that match.

    """
    flags = re.IGNORECASE if ignore_case else None
    compiled_regex = re.compile(regex, flags) if flags else re.compile(regex)
    new_list = [n for n in string_list for m in[compiled_regex.match(n)] if m]
    return new_list


def get_list_index(str_list, selection):
    """
    Gets the index of the string in a list of strings. This is case
    case insensitive and returns the index of the default string.
    It removes any EOL in the strings.

      Parameters:
        str_list(list of (:term:`String`))

        selection (:term:`String`):

        default(:term:`String`):
      Returns:
        index of selected entry
      Exception:
        ValueError if the selection cannot be found in the list

    """
    l1 = [li.replace('\n', '').lower() for li in str_list]
    # l2 = [hi.lower() for hi in l1]
    # ValueError if match fails
    col_index = l1.index(selection.lower())
    return col_index


def build_table_struct(fields, db_table, max_width=None, sort=False):
    """
    Build a formatted table from the list of fields in the db_table.
    This builds a table with each table entry in the table

    Parameters:
      fields(list of :term:`string`):
        list containing the names of the fields from the the db_table
        to be included in the table formatted output

      db_table TODO

      max_width(:term:`integer`):
        Optional maximum width of any field

      sort(:class:`py:bool`):
        If True, the resulting rows are sorted by ID

    Returns:
        list of lists where each inner list is a row. This is suitable for
        printing with the table formatter.

    """
    tbl_rows = []
    # pylint: disable=unused-variable
    for id_, data in six.iteritems(db_table):
        row = [data[field] for field in fields]
        tbl_rows.append(row)

    if sort:
        tbl_rows.sort(key=lambda x: x[0])

    return tbl_rows


class StrList(object):
    """
    Manage the list of strings. Since this list has multiple forms (
    list of strings, formatted string, etc.), this class maps between the
    different versions.

    TODO
    """
    def __init__(self, input, chars=None):
        """
        Create an internal variable that is a list of the value of each
        version definition in the list
        Used to manage lists of SMI versions because the string form of this
        list can have multiple forms (1.2/2.3, 1.2, 2.3, 1.2 1.3)

        TODO test if only chars in chars are in string.
        """
        if isinstance(input, six.string_types):
            if '/' in input:
                self._list_form = input.split("/")
            elif ',' in input:
                self.self._list_form = input.split("/")
            elif " " in input:
                self._list_form = input.split("/")
        elif isinstance(input, list):
            self._list_form = input
        elif isinstance(input, tuple):
            self._list_form = list(input)

        else:
            raise ValueError("Versions Strlist %s not valid type" % input)

        for v in self._list_form:
            v.strip()

    def __repr__(self):
        """
            Return string of versions separated by ",
        """
        return ", ".join(self.list_form)

    @property
    def list_form(self):
        return self._list_form
