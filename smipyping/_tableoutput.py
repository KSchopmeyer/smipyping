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
Internal module with utilities to write to table formatted outputs in
multiple formats.  The table outputs all depend on a common table definition
format (iterable of iterables).

"""

from __future__ import print_function, absolute_import

import os
from textwrap import wrap
import csv
import tabulate
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from terminaltables import AsciiTable
import six
from ._common import TABLE_FORMATS

__all__ = ['TableFormatter']


class TableFormatter(object):
    """
        Class that sets up the properties for creating tables.
        It includes the methods for building and printing the tables
    """

    def __init__(self, rows, headers, table_format='simple',
                 title=None, csv_dialect=None):
        """
          Parameters:

            rows(:term:'list' of lists):
                A list of lists where each inner list contains the items
                in a row of the table.
            headers(:term: 'list'):
                If not none, a list of strings where each string is a table
                column header (title for the column), If not Null it is
                output before the table as a header row.  The exact format
                depends on the table-output format
            table_format(:term: 'string'):
                An optional string defining the output format for the table.
                If None, the output format simple is assumed.

            title (:term: 'string'):
                An optional string containing a title that is output on the
                line before the table output.

            csv_dialect() (:term: 'string'): Future
        """
        self.rows = rows
        self.headers = [headers] if isinstance(headers, six.string_types) \
            else headers
        self.title = title
        if table_format not in TABLE_FORMATS:
            raise ValueError('Invalid table format %s passed to '
                             'TableFormatter' % table_format)
        self.table_format = table_format
        self.csv_dialect = csv_dialect

    def build_csv_table(self):
        """
        Output a list of lists and optional header as csv formatted data
        to a file.
        """
        # TODO: should I be writing this with 'wb' ???
        output = StringIO()
        writer = csv.writer(output, dialect=self.csv_dialect,
                            lineterminator=os.linesep,
                            delimiter=',', quotechar='"',
                            quoting=csv.QUOTE_NONNUMERIC)
        if self.headers:
            writer.writerow(self.headers)
        writer.writerows(self.rows)
        return output.getvalue()

    def print_table(self, output_file=None):
        """
        Output a table to either stdout or a file. Defaults to simple ascii
        format.
        """
        result = self.build_table()

        # TODO handling utf on output for both python 2 and 3
        if output_file:
            with open(output_file, 'w') as f:
                print(result, file=f)
                print("", file=f)
        else:
            print(result)
            print()

    def build_table(self):
        """
            General print table function. This is temporary while the world
            gets the tabulate python package capable of supporting multiline
            cells.

            Parameters:
              headers (iterable of strings) where each string is a
               table column name or None if no header is to be attached

              table_data - interable of iterables where:
                 each the top level iterables represents the list of rows
                 and each row is an iterable of strings for the data in that
                 row.

              title (:term: `string`)
                 Optional title to be places io the output above the table.
                 No title is output if this parameter is None

              table_format (:term: 'string')
                Output format defined by the string and limited to one of the
                choice of table formats defined in TABLE_FORMATS list

              output_file (:term: 'string')
                If not None, a file name to which the output formatted data
                is sent.

        """
        # test if there is a EOL in any cell and mark for folded processing
        folded = False
        for row in self.rows:
            for cell in row:
                if isinstance(cell, six.string_types) and'\n' in cell:
                    folded = True
        # If a cell is folded, use the terminal_table print
        result = ""
        if self.table_format == 'csv':
            result = self.build_csv_table()
        elif self.table_format == 'html':
            result = self.build_html_table()
        else:
            if folded:
                result = self.build_terminal_table()
            # Else use tabulate package as the base for the table
            else:
                # Prints dictionaries if header='keys'
                result = tabulate.tabulate(self.rows, self.headers,
                                           tablefmt=self.table_format)

        if self.title:
            result = '\n%s\n%s' % (self.title, result)
        else:
            result = '\n%s' % result
        return result

    def build_html_table(self):
        """
        Print a table and header in html format.
        """
        # Very inefficent but recreates the table with NL replaced by
        # html break.
        new_rows = []
        for row in self.rows:
            new_row = []
            for cell in row:
                if isinstance(cell, six.string_types):
                    cell = cell.replace('\n', '<br />')
                new_row.append(cell)
            new_rows.append(new_row)
        use_tabulate = False
        if self.title:
            print('<p>%s<\\p>' % self.title)
        if use_tabulate:
            result = tabulate.tabulate(new_rows, self.headers, tablefmt='html')
        else:
            result = HtmlTable(rows=new_rows, header_row=self.headers)

        return result

    def build_terminal_table(self):
        """ Build table with data as an ascii table using the terminal table
            package.  This is used only for multiline tables because it has
            fewer table format options than the tabulate package.

            Parameters:
              table data:
                 List of lists of strings. Each list of strings represents the
                 data for a single row in the table

              headers:
                  list of strings defining the column names

              title:
                  Title that is applied above table output if it is not None

              table_format: (:term: String) keyword defining table format

            NOTE: Currently this outputs in the terminatable AsciiTable format
            It may be extended in the future to allow other formats such as the
            asciitable format, etc.  However these only differ in the table
            boundary character representation
        """
        if self.headers:
            self.rows.insert(0, self.headers)

        table = AsciiTable(self.rows)
        if self.table_format is None or self.table_format == 'plain':
            table.inner_column_border = False
            table.inner_heading_row_border = False
            table.inner_row_border = False
            table.outer_border = False
        elif self.table_format == 'simple':
            table.inner_heading_row_border = True
            table.inner_column_border = False
            table.outer_border = False
        elif self.table_format == 'grid':
            table.inner_column_border = True
            table.outer_border = True
            table.inner_row_border = True
            table.inner_heading_row_border = True
        else:
            raise ValueError('Invalid table type %s. Folded tables have '
                             ' limited formatting.' % self.table_format)

        return(table.table)

    @staticmethod
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


# Table style to get thin black lines in Mozilla/Firefox instead of 3D borders
TABLE_STYLE_THINBORDER = "border: 1px solid #000000; border-collapse: collapse;"
# TABLE_STYLE_THINBORDER = "border: 1px solid #000000;"


class TableCell(object):  # pylint: disable=too-few-public-methods
    """
    a TableCell object is used to create a cell in a HTML table. (TD or TH)

    Attributes:
    - text: text in the cell (may contain HTML tags). May be any object which
            can be converted to a string using str().
    - header: bool, false for a normal data cell (TD), true for a header
        cell (TH)
    - bgcolor: str, background color
    - width: str, width
    - align: str, horizontal alignement (left, center, right, justify or char)
    - char: str, alignment character, decimal point if not specified
    - charoff: str, see HTML specs
    - valign: str, vertical alignment (top|middle|bottom|baseline)
    - style: str, CSS style
    - attribs: dict, additional attributes for the TD/TH tag

    Reference: http://www.w3.org/TR/html4/struct/tables.html#h-11.2.6

    Example:

    """

    def __init__(self, text="", bgcolor=None, header=False, width=None,
                 align=None, char=None, charoff=None, valign=None, style=None,
                 attribs=None):
        """TableCell constructor"""
        self.text = text
        self.bgcolor = bgcolor
        self.header = header
        self.width = width
        self.align = align
        self.char = char
        self.charoff = charoff
        self.valign = valign
        self.style = style
        self.attribs = attribs
        if attribs is None:
            self.attribs = {}

    def __str__(self):
        """return the HTML code for the table cell as a string"""
        attribs_str = ""
        if self.bgcolor:
            self.attribs['bgcolor'] = self.bgcolor
        if self.width:
            self.attribs['width'] = self.width
        if self.align:
            self.attribs['align'] = self.align
        if self.char:
            self.attribs['char'] = self.char
        if self.charoff:
            self.attribs['charoff'] = self.charoff
        if self.valign:
            self.attribs['valign'] = self.valign
        if self.style:
            self.attribs['style'] = self.style
        for attr in self.attribs:
            attribs_str += ' %s="%s"' % (attr, self.attribs[attr])
        if self.text:
            text = str(self.text)
        else:
            # An empty cell should at least contain a non-breaking space
            text = '&nbsp;'
        if self.header:
            return '  <TH%s>%s</TH>\n' % (attribs_str, text)

        return '  <TD%s>%s</TD>\n' % (attribs_str, text)


class TableRow(object):  # pylint: disable=too-few-public-methods
    """
    a TableRow object is used to create a row in a HTML table. (TR tag)

    Attributes:
    - cells: list, tuple or any iterable, containing one string or TableCell
             object for each cell
    - header: bool, true for a header row (TH), false for a normal data row (TD)
    - bgcolor: str, background color
    - col_align, col_valign, col_char, col_charoff, col_styles: see Table class
    - attribs: dict, additional attributes for the TR tag

    Reference: http://www.w3.org/TR/html4/struct/tables.html#h-11.2.5
    """

    def __init__(self, cells=None, bgcolor=None, header=False, attribs=None,
                 col_align=None, col_valign=None, col_char=None,
                 col_charoff=None, col_styles=None):
        """TableCell constructor"""
        self.bgcolor = bgcolor
        self.cells = cells
        self.header = header
        self.col_align = col_align
        self.col_valign = col_valign
        self.col_char = col_char
        self.col_charoff = col_charoff
        self.col_styles = col_styles
        self.attribs = attribs
        if attribs is None:
            self.attribs = {}

    def __str__(self):
        """return the HTML code for the table row as a string"""
        attribs_str = ""
        if self.bgcolor:
            self.attribs['bgcolor'] = self.bgcolor
        for attr in self.attribs:
            attribs_str += ' %s="%s"' % (attr, self.attribs[attr])
        result = ' <TR%s>\n' % attribs_str
        for cell in self.cells:
            col = self.cells.index(cell)    # cell column index
            if not isinstance(cell, TableCell):
                cell = TableCell(cell, header=self.header)
            # apply column alignment if specified:
            if self.col_align and cell.align is None:
                cell.align = self.col_align[col]
            if self.col_char and cell.char is None:
                cell.char = self.col_char[col]
            if self.col_charoff and cell.charoff is None:
                cell.charoff = self.col_charoff[col]
            if self.col_valign and cell.valign is None:
                cell.valign = self.col_valign[col]
            # apply column style if specified:
            if self.col_styles and cell.style is None:
                cell.style = self.col_styles[col]
            result += str(cell)
        result += ' </TR>\n'
        return result


class HtmlTable(object):  # pylint: disable=too-few-public-methods
    """
    a Table object is used to create a HTML table. (TABLE tag)

    Attributes:
    - rows: list, tuple or any iterable, containing one iterable or TableRow
            object for each row
    - header_row: list, tuple or any iterable, containing the header row
        (optional)
    - border: str or int, border width
    - style: str, table style in CSS syntax (thin black borders by default)
    - width: str, width of the table on the page
    - attribs: dict, additional attributes for the TABLE tag
    - col_width: list or tuple defining width for each column
    - col_align: list or tuple defining horizontal alignment for each column
    - col_char: list or tuple defining alignment character for each column
    - col_charoff: list or tuple defining charoff attribute for each column
    - col_valign: list or tuple defining vertical alignment for each column
    - col_styles: list or tuple of HTML styles for each column

    Reference: http://www.w3.org/TR/html4/struct/tables.html#h-11.2.1

    Example:

    table_data = [
            ['Last name',   'First name',   'Age'],
            ['Smith',       'John',         30],
            ['Carpenter',   'Jack',         47],
            ['Johnson',     'Paul',         62],
        ]
    htmlcode = HtmlTable(table_data,
        header_row = ['Last name',   'First name',   'Age', 'Score'],
        col_width=['', '20%', '10%', '10%'],
        col_align=['left', 'center', 'right', 'char'],
        col_styles=['font-size: large', '', 'font-size: small',
          'background-color:yellow'])

    htmlcode = HTML.table(table_data)

    """

    def __init__(self, rows=None, border='1', style=None, width=None,
                 cellspacing=None, cellpadding=4, attribs=None, header_row=None,
                 col_width=None, col_align=None, col_valign=None,
                 col_char=None, col_charoff=None, col_styles=None):
        """TableCell constructor"""
        self.border = border
        self.style = style
        # style for thin borders by default
        if style is None:
            self.style = TABLE_STYLE_THINBORDER
        self.width = width
        self.cellspacing = cellspacing
        self.cellpadding = cellpadding
        self.header_row = header_row
        self.rows = rows
        if not rows:
            self.rows = []
        self.attribs = attribs
        if not attribs:
            self.attribs = {}
        self.col_width = col_width
        self.col_align = col_align
        self.col_char = col_char
        self.col_charoff = col_charoff
        self.col_valign = col_valign
        self.col_styles = col_styles

    def __str__(self):
        """return the HTML code for the table as a string"""
        attribs_str = ""
        if self.border:
            self.attribs['border'] = self.border
        if self.style:
            self.attribs['style'] = self.style
        if self.width:
            self.attribs['width'] = self.width
        if self.cellspacing:
            self.attribs['cellspacing'] = self.cellspacing
        if self.cellpadding:
            self.attribs['cellpadding'] = self.cellpadding
        for attr in self.attribs:
            attribs_str += ' %s="%s"' % (attr, self.attribs[attr])
        result = '<TABLE%s>\n' % attribs_str
        # insert column tags and attributes if specified:
        if self.col_width:
            for width in self.col_width:
                result += '  <COL width="%s">\n' % width

        if self.header_row:
            if not isinstance(self.header_row, TableRow):
                result += str(TableRow(self.header_row, header=True))
            else:
                result += str(self.header_row)
        # Then all data rows:
        for row in self.rows:
            if not isinstance(row, TableRow):
                row = TableRow(row)
            # apply column alignments  and styles to each row if specified:
            # (Mozilla bug workaround)
            if self.col_align and not row.col_align:
                row.col_align = self.col_align
            if self.col_char and not row.col_char:
                row.col_char = self.col_char
            if self.col_charoff and not row.col_charoff:
                row.col_charoff = self.col_charoff
            if self.col_valign and not row.col_valign:
                row.col_valign = self.col_valign
            if self.col_styles and not row.col_styles:
                row.col_styles = self.col_styles
            result += str(row)
        result += '</TABLE>'
        return result
