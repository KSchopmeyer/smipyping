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

import six


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
