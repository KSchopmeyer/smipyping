
"""
Internal module with utility stuff for command line programs.
"""

from __future__ import print_function, absolute_import

import argparse

def check_negative_int(value):
    """ Test the input value for type int and ge 0 generate exception if
        it fails these tests.

    Parameters
        input string
    Returns
        integer value
    ivalue = int(value)
    if ivalue < 0:
        raise argparse.ArgumentTypeError('%s expected positive integer' % value)
    return ivalue
    """
    ivalue = int(value)
    if ivalue < 0:
        raise argparse.ArgumentTypeError('%s: invalid positive int value' % \
                                         value)
    return ivalue

class SmartFormatter(argparse.HelpFormatter):
    """Formatter class for `argparse`, that respects newlines in help strings.

    Idea and code from: http://stackoverflow.com/a/22157136

    Usage:
        If an argparse argument help text starts with 'R|', it will be treated
        as a *raw* string that does line formatting on its own by specifying
        newlines appropriately. The string should not exceed 55 characters per
        line. Indentation handling is still applied automatically and does not
        need to be specified within the string.

        Otherwise, the strings are formatted as normal and newlines are
        treated like blanks.

    Limitations:
        It seems this only works for the `help` argument of
        `ArgumentParser.add_argument()`, and not for group descriptions,
        and usage, description, and epilog of ArgumentParser.
    """

    def _split_lines(self, text, width):
        if text.startswith('R|'):
            return text[2:].splitlines()
        return argparse.HelpFormatter._split_lines(self, text, width)

