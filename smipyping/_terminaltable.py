"""
Internal module with utility stuff fthe terminaltable table formatter.
"""

from __future__ import print_function, absolute_import

from textwrap import wrap
import six
from terminaltables import SingleTable


def print_terminal_table(title, table_data, inner_border=False,
                         outer_border=False):
    """ Print table data as an ascii table. The input is a dictionary
        of table data in the format used by terminaltable package.

        title: list of strings defining the row titles

        table data:
           List of lists of strings. Each list of strings represents the
           data for a single row in the table

        inner_border

        outer_border

        NOTE: Currently this outputs in the terminatable SingleTable format
        It may be extended in the future to allow other formats such as the
        asciitable format, etc.  However these only differ in the table
        boundary character representation
    """

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
