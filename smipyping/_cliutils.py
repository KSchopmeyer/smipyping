"""Internal module with utility functions to support argparse."""

from __future__ import print_function, absolute_import

import argparse


def check__int_range(value, min_, max_):
    """
    Test the input value for type int within defined range.

    Parameters
        input string, min integer value, max integer value
    Returns
        integer value

    Exception: not integer or out of range
    """
    ivalue = int(value)
    if ivalue < min_ or ivalue > max_:
        raise argparse.ArgumentTypeError('%s: invalid range for integer.'
                                         ' min=%s, max=%s' %
                                         (value, min_, max_))
    return ivalue


def check_negative_int(value):
    """
    Test the input value for type int and ge 0.

    Generate exception if it fails this tests.

    Parameters
        input string representing an integer
    Returns
        integer value

    Exception: negative integer value or not an integer
    """
    ivalue = int(value)
    if ivalue < 0:
        raise argparse.ArgumentTypeError('%s: invalid. '
                                         ' Positive int value required' %
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


class SmiSmartFormatter(SmartFormatter,
                        argparse.RawDescriptionHelpFormatter):
    """
    Define a custom Formatter to allow formatting help and epilog.

    argparse formatter specifically allows multiple inheritance for the
    formatter customization and actually recommends this in a discussion
    in one of the issues:

        http://bugs.python.org/issue13023

    """
    pass
