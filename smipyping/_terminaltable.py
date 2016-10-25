"""
Internal module with utility stuff fthe terminaltable table formatter.
"""

from __future__ import print_function, absolute_import

from textwrap import wrap
import six
from terminaltables import SingleTable

def print_terminal_table(title, table_data):
    """ Print table data as an ascii table. The input is a dictionary
        of table data in the format used by terminaltable package.

        The first line is the headers as a list.

        The remaining lines are the table lines each as a list of entries
    """

    table_instance = SingleTable(table_data, title)
    table_instance. inner_column_border = False
    table_instance.outer_border = False

    print(table_instance.table)
    print()

def fold_cell(cell_string, max_cell_width):
    """ Fold a line within a maximum width to fit within a table entry
    """
    new_cell = cell_string
    if isinstance(cell_string, six.string_types):
        if max_cell_width < len(cell_string):
            new_cell = '\n'.join(wrap(cell_string, max_cell_width))

    return new_cell

