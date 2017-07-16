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


def print_table(table_header, table_data, title=None, table_type=None):
    """
        General print table function
    """
    if table_type == 'html':
        print_html_table(table_header, table_data, title=None)
    else:
        print_ascii_table(table_header, table_data, title=title,
                          table_type=table_type)


def print_html_table(table_header, table_data, title=None):
    """
    Print a table and header in html format.
    """
    html = HtmlTable(table_data,
                     table_header)
    print(html)


def print_ascii_table(table_header, table_data, title=None, table_type='plain'):
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
    print('asciitable type %s' % table_type)
    # terminaltable does not print title if no  borders.
    if table_type is None or table_type == 'plain':
        print(title)
        inner_border = False
        outer_border = False
    elif table_type == 'simple':
        inner_border = False
        outer_border = True
    elif table_type == 'grid':
        inner_border = False
        outer_border = True
    else:
        raise ValueError('Invalid table type %s' % table_type)

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


# Table style to get thin black lines in Mozilla/Firefox instead of 3D borders
TABLE_STYLE_THINBORDER = "border: 1px solid #000000; border-collapse: collapse;"
# TABLE_STYLE_THINBORDER = "border: 1px solid #000000;"


class TableCell (object):
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
        else:
            return '  <TD%s>%s</TD>\n' % (attribs_str, text)


class TableRow (object):
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


class HtmlTable (object):
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
        # The following code would also generate column attributes for style
        # and alignement according to HTML4 specs,
        # BUT it is not supported completely (only width) on Mozilla Firefox:
        # see https://bugzilla.mozilla.org/show_bug.cgi?id=915
# #        n_cols = max(len(self.col_styles), len(self.col_width),
# #                     len(self.col_align), len(self.col_valign))
# #        for i in range(n_cols):
# #            col = ''
# #            try:
# #                if self.col_styles[i]:
# #                    col += ' style="%s"' % self.col_styles[i]
# #            except: pass
# #            try:
# #                if self.col_width[i]:
# #                    col += ' width="%s"' % self.col_width[i]
# #            except: pass
# #            try:
# #                if self.col_align[i]:
# #                    col += ' align="%s"' % self.col_align[i]
# #            except: pass
# #            try:
# #                if self.col_valign[i]:
# #                    col += ' valign="%s"' % self.col_valign[i]
# #            except: pass
# #            result += '<COL%s>\n' % col
        # First insert a header row if specified:
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
