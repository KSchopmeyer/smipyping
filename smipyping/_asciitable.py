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
Internal module with utilities to write to ascii outputs.

"""

from __future__ import print_function, absolute_import

from textwrap import wrap
import six
from terminaltables import SingleTable


def print_ascii_table(table_header, table_data, title=None, inner_border=False,
                      outer_border=False):
    """ Print table data as an ascii table. The input is a dictionary
        of table data in the format used by terminaltable package.


        table_header:
            list of strings defining the column names

        table data:
           List of lists of strings. Each list of strings represents the
           data for a single row in the table
        title:
            Title that is applied above table output if it is not None

        inner_border:
            optional flag that tells table builder to create inner borders

        outer_border:
            Optional flag that tells table builder to create border around
            complete table

        NOTE: Currently this outputs in the terminatable SingleTable format
        It may be extended in the future to allow other formats such as the
        asciitable format, etc.  However these only differ in the table
        boundary character representation
    """

    if not outer_border and title:  # terminaltable does not print title if no 
        print(title)
    table_data = [table_header] + table_data
    table_instance = SingleTable(table_data, title)
    table_instance.inner_column_border = inner_border
    table_instance.outer_border = outer_border

    print(table_instance.table)
    print()


def fold_cell(cell_string, max_cell_width):
    """ Fold a string within a maximum width to fit within a table entry

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
