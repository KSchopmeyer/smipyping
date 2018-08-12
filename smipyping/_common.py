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
import datetime
from textwrap import wrap
import six

__all__ = ['get_list_index', 'build_table_struct', 'filter_stringlist',
           'compute_startend_dates', 'fold_cell', 'get_url_str',
           'datetime_display_str']


def datetime_display_str(date_time):
    """Common function to create string for datetime for display. This creates
       a single point where date time is formatted for display
    """
    return date_time.strftime("%Y-%m-%d %H:%M:%S")


def get_url_str(scheme, name, port):
    """
    Create displayable output for url based on scheme, name, an ports based
    on knowledge that this is WBEM.  If the ports are the standard ports
    the port component is ignored
    """
    if isinstance(port, six.string_types):
        port = int(port)
    if (scheme == 'https' and port == 5989) or \
       (scheme == 'http' and port == 5988):
        url = '%s://%s' % (scheme, name)
    else:
        url = '%s://%s:%s' % (scheme, name, port)
    return url


def fold_cell(cell_string, max_cell_width):
    """ Fold a string within a maximum width to fit within a  the
        max_cell_width defined as an input parameter.

        Parameters:

          cell_string:
            The string of data to go into the cell
          max_cell_width:
            Maximum width of cell.  Data is folded into multiple lines to
            fit into this width.

        Return:
            String representing the folded string
    """
    new_cell = cell_string
    if isinstance(cell_string, six.string_types):
        if max_cell_width < len(cell_string):
            new_cell = '\n'.join(wrap(cell_string, max_cell_width))

    return new_cell


def compute_startend_dates(start_date, end_date=None, number_of_days=None,
                           oldest_date=None):
    """
    Compute the start and end dates from the arguments and return a tuple
    of start date and end date. This uses the three date inputs to create
    a start and end date that is returned

    Parameters:
      start_date(:class:`py:datetime.datetime` or `None`):
        Datetime for start of activity or if None, oldes timestamp in
        the pings table

      end_date(:class:`py:datetime.datetime` or `None`):
        Datetune for end of activity or None.  If None and `number_of_days`
        not set, the current date is used as the end_date

      number_of_days(:term:`integer` or None):
        If this integer set, end_date MUST BE `None`. Represents the
        number of days for this activity since the `start_date`.

      oldest_date(:class:`py:datetime.datetime` or `None`):
        Date to use for start_date if start_date is None
    """
    if start_date is None:
        start_date = oldest_date

    if number_of_days and end_date:
        raise ValueError('Simultaneous enddate %s and number of days %s '
                         'parameters not allowed' %
                         (end_date, number_of_days))

    if number_of_days:
        if number_of_days < 0:
            raise ValueError("NumberOfDays must be positive integer not %s"
                             % number_of_days)
        end_date = start_date + datetime.timedelta(days=number_of_days)

    if end_date is None:
        end_date = datetime.datetime.now()

    if end_date < start_date:
        raise ValueError('EndDate %s before StartDate %s' % (start_date,
                                                             end_date))
    return (start_date, end_date)


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

    Parameters:

      inputs (:term:`string` or list of :term:`string`)
        String or list of strings to manage.  Converted to list of strings
        containing only the chars in the parameter chars. Any other chars
        returns ValueError exception

      chars (:term:`string`):
        Set of characters that are allowed in each string in the resulting list

      fold (:term:`integer` or None)
        If integer, the string output is folded using the parameter as the
        max length before folding.

    """
    def __init__(self, inputs, match=None):
        """
        Create an internal variable that is a list of the value of each
        version definition in the list
        Used to manage lists of SMI versions because the string form of this
        list can have multiple forms (1.2/2.3, 1.2, 2.3, 1.2 1.3)

        Parameters:


        TODO test if only chars in chars are in string.
        """
        self._items = None
        if isinstance(inputs, six.string_types):
            if '/' in inputs:
                self._items = set(inputs.split("/"))
            elif ',' in inputs:
                self._items = set(inputs.split(","))
            elif " " in inputs:
                self._items = set(inputs.split(" "))
            else:
                self._items = set([inputs])
        elif isinstance(inputs, list):
            self._items = set(inputs)
        elif isinstance(inputs, tuple):
            self._items = set(list(input))
        else:
            raise ValueError("Versions Strlist %s not valid type" % input)

        self._items = [item.strip() for item in self._items]
        for item in self._items:
            if match and re.match(match, item) is None:
                raise ValueError('String "%s" does not match regex %s' %
                                 (item, match))
        self._items = sorted(self._items)

    def __str__(self):
        """
            Return string of versions separated by ",
        """
        return ", ".join(self._items)

    def __repr__(self):
        """
            Return string of versions separated by ",
        """
        return ", ".join(self._items)

    def str_by_sep(self, separator="/"):
        """
        Create single string output with defined separator
        """
        return separator.join(self._items)

    @property
    def items(self):
        """
            Return the list form of the input
        """
        return self._items

    def equal(self, strlist,):
        """
        Compare one StrList to another strlist for equality of items.
        This compares the objects string by string after sorting and defining
        a set for each to eliminate non-unique items
        """
        return self.items == strlist.items

    def folded_str(self, length):
        """
        Return a folded string based on len argument of the string
        """
        return fold_cell(str(self), length)
