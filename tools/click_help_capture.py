#!/usr/bin/env python

"""
This tool can capture the help outputs from a click application and output
the result either as text or in restructured text format.

It executes the click script --help and recursively scrapes all of the
subcommands from the output, generating an output that is the help text for
every groupt/subcommand in the script.

All output is to stdout.

It will generate either restructured text or pure text output depending on
the variable USE_RST.

the rst output set a section name for each help subject.

This should be usable with different click generated apps by simply changing
the variable  SCRIPT_NAME to the name of the target scripere t.

There are no executeion inputs since the primary use is to generate information
for review and documentation and the two variables:

SCIRPT_NAME
USE_RST

Are probably normally fixed

"""


from __future__ import print_function, absolute_import

from subprocess import Popen, PIPE
try:
    import textwrap
    textwrap.indent  # pylint: disable=pointless-statement
except AttributeError:  # undefined function (wasn't added until Python 3.3)
    def indent(text, amount, ch=' '):  # pylint: disable=invalid-name
        """Indent locally define"""
        padding = amount * ch
        return ''.join(padding + line for line in text.splitlines(True))
else:
    def indent(text, amount, ch=' '):  # pylint: disable=invalid-name
        """Wrap textwrap function"""
        return textwrap.indent(text, amount * ch)

import six

# Flag that allows displaying the data as pure text rather than markdown
# format
USE_RST = True

ERRORS = 0

VERBOSE = False


def rst_headline(title, level):
    """
    Format a markdown header line based on the level argument. The rst format
    for headings is generally of the form
    ====================
    title for this thing
    ====================
    """
    level_char_list = ['#', '*', '=', '-', '^', '"']
    try:
        level_char = level_char_list[level]
    except IndexError:
        level_char = '='

    # output anchor in form .. _`smicli subcommands`:
    anchor = '.. _`%s`:' % title
    title_marker = level_char * len(title)
    if level == 0:
        return '\n%s\n\n%s\n%s\n%s\n' % (anchor, title_marker, title,
                                         title_marker)

    return '\n%s\n\n%s\n%s\n' % (anchor, title, title_marker)


def print_rst_verbatum_text(text_str):
    """
    Print the text on input surrounded by the back quotes defining
    veratum text
    """
    print('::\n')
    # indent text for rst. rst requires that block monospace test be
    # indented and preceeded by line with just '::' and followed by
    # empty line. This indents by two char the complete test_str except
    # the first line
    print('%s\n' % indent(text_str, 4))


HELP_DICT = {}


def get_subcmd_group_names(cmd, script_name):
    """
    Execute the script with defined subcommand and help and get the
    groups defined for that help.

    returns list of subcommands/groups
    """
    command = '%s %s --help' % (script_name, cmd)
    # Disable python warnings for script call.
    command = 'export PYTHONWARNINGS="" && %s' % command
    if VERBOSE:
        print('command %s' % command)
    proc = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
    std_out, std_err = proc.communicate()
    exitcode = proc.returncode

    HELP_DICT[cmd] = std_out

    if six.PY3:
        std_out = std_out.decode()
        std_err = std_err.decode()

    if exitcode:
        raise RuntimeError('Error, unexpected non-zero exit code %s'
                           ' from %s call' % (script_name, exitcode))
    if len(std_err):
        raise RuntimeError('Error. expected stderr (%s)returned from '
                           '%s call.' % (script_name, std_err))

    # Split stdout into list of lines
    lines = std_out.split('\n')

    # get first word of all lines after line containing 'Commands:'
    group_list = []
    group_state = False
    for line in lines:
        if group_state and len(line):
            # split line into list of words and get first word as subcommand
            words = line.split()
            group_list.append(words[0])

        # test for line that matchs the word Commands
        if line == 'Commands:':
            group_state = True
    return group_list


def get_subgroup_names(group_name, script_name):
    """
    Get all the subcommands for the help_group_name defined on input.
    Executes script and extracts groups after line with 'Commands'
    """
    subcmds_list = get_subcmd_group_names(group_name, script_name)
    space = ' ' if group_name else ''
    
    return ['%s%s%s' % (group_name, space, name) for name in subcmds_list]


def create_help_cmd_list(script_name):
    """
    Create the command list.
    """
    # Result list of assembled help subcmds
    help_groups_result = []
    # start with empty group, the top level (i.e. pywbemcli --help).
    # This is list of names to process and is extended as we process
    # each group.
    group_names = [""]

    help_groups_result.extend(group_names)
    for name in group_names:
        return_cmds = get_subgroup_names(name, script_name)
        help_groups_result.extend(return_cmds)
        # extend input list with returned assembled groups
        group_names.extend(return_cmds)
    # sort to match order of click
    help_groups_result.sort()
    if USE_RST:
        print(rst_headline("%s Help Command Details" % script_name, 2))
        print('\nThis section defines the help output for each %s '
              'command group and subcommand.\n' % script_name)

    for name in help_groups_result:
        command = '%s %s --help' % (script_name, name)
        out = HELP_DICT[name]
        if USE_RST:
            level = len(command.split())
            # Don't put the top level in a separate section
            if level > 2:
                print(rst_headline(command, level))
            print('\n%s\n' % '\nThe following defines the help output for the '
                  '`%s` subcommand\n' % command)
            print_rst_verbatum_text(out)
        else:
            print('%s\n%s COMMAND: %s' % (('=' * 50), script_name, command))
            print(out)

    return help_groups_result


if __name__ == '__main__':
    create_help_cmd_list('smicli')
