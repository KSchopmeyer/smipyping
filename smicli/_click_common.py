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
"""
from textwrap import wrap
import re
import six
import prompt_toolkit


__all__ = ['DEFAULT_CONFIG_FILE', 'SMICLI_PROMPT', 'SMICLI_HISTORY_FILE',
           'DEFAULT_SMICLI_CONFIG_FILES']

#: Default configuration file for smipyping cli
DEFAULT_CONFIG_FILE = 'smicli.ini'

#: Default smi cli configuration file for smipyping cli
#: These are the default names for the smicli config files

DEFAULT_SMICLI_CONFIG_FILES = ['smicli.ini', 'smicli.cfg']


#: Characters for cmdline prompt when the smicli repl is executing.
#: The prompt is presented at the beginning of a line awaiting a command
#: input.
#: The prompt MUST BE Unicode (prompt-toolkit requirement)

SMICLI_PROMPT = u'smicli> '

#: File path of history file for interactive mode.
#: If the file name starts with tilde (which is handled by the shell, not by
#: the file system), it is properly expanded.

SMICLI_HISTORY_FILE = '~/.smicli_history'

TABLE_FORMATS = ['plain', 'simple', 'grid', 'html']

# TODO: Want to expand to this when we get updated tabulate.
# TABLE_FORMATS = ['table', 'plain', 'simple', 'psql', 'rst', 'mediawiki',
#                 'html']

DEFAULT_OUTPUT_FORMAT = 'simple'


def prompt(txt):
    """ single function for prompt. Aids mock tests"""
    return prompt_toolkit.prompt(txt)


def validate_prompt(text=""):
    """
    Issue prompt and get y/n response. Input parameter text is prepended to
    the prompt output.
    """
    text = prompt('%s valid (y/n): ' % text)
    return True if text == 'y' else False


def filter_namelist(regex, name_list, ignore_case=True):
    """
    Filter out names in name_list that do not match compiled_regex.

    Note that the regex may define a subset of the name string.  Thus,  regex:
        - CIM matches any name that starts with CIM
        - CIM_abc matches any name that starts with CIM_abc
        - CIM_ABC$ matches only the name CIM_ABC.

    Parameters:
      regex (:term: `String`) Python regular expression to match

      name_list: List of strings to be matched.

      ignore_case: bool. If True, do case-insensitive match. Default = True

    Returns the list of names that match.

    """
    flags = re.IGNORECASE if ignore_case else None
    compiled_regex = re.compile(regex, flags) if flags else re.compile(regex)
    new_list = [n for n in name_list for m in[compiled_regex.match(n)] if m]
    return new_list


def pick_from_list(context, options, title):
    """
    Interactive component that displays a set of options (strings) and asks
    the user to select one.  Returns the item and index of the selected string.

    Parameters:
      options:
        List of strings to select

      title:
        Title to display before selection

    Retries until either integer within range of options list is input
    or user enter no value. Ctrl_C ends even the REPL.

    Returns: Index of selected item

    Exception: Returns ValueError if Ctrl-c input from console.

    TODO: This could be replaced by the python pick library that would use
    curses for the selection process.
    """
    context.spinner.stop()
    print(title)
    index = -1
    for str_ in options:
        index += 1
        print('%s: %s' % (index, str_))
    selection_txt = None
    while True:
        try:
            selection_txt = prompt(
                'Select an entry by index or enter Ctrl-C to exit >')
            if selection_txt.isdigit():
                selection = int(selection_txt)
                if selection >= 0 and selection <= index:
                    return selection
        except ValueError:
            pass
        except KeyboardInterrupt:
            raise ValueError
        print('%s Invalid. Input integer between 0 and %s or Ctrl-C to '
              'exit.' % (selection_txt, index))
    context.spinner.start()


def pick_multiple_from_list(context, options, title):
    """
    Interactive component that displays a set of options (strings) and asks
    the user to select one.  Returns the item and index of the selected string.

    Parameters:
      options:
        List of strings to select

      title:
        Title to display before selection

    Retries until either integer within range of options list is input
    or user enter no value. Ctrl_C ends even the REPL.

    Returns: List of indexes of selected items

    Exception: Returns ValueError if Ctrl-c input from console.

    TODO: This could be replaced by the python pick library that would use
    curses for the selection process.
    """
    context.spinner.stop()
    print(title)
    selection_list = []
    index = -1
    for str_ in options:
        index += 1
        print('%s: %s' % (index, str_))
    while True:
        selection_txt = None
        try:
            response = prompt(
                'Select multiple entries by index or Ctrl-C to exit >')
            selections = response.split()
            for selection_txt in selections:
                if selection_txt.isdigit():
                    selection = int(selection_txt)
                    if selection >= 0 and selection <= index:
                        print('selection %s' % selection)
                        selection_list.append(selection)
                    else:
                        raise ValueError('Invalid input %s' % selection_txt)
                else:
                    raise ValueError('Invalid input %s' % selection_txt)
            return selection_list
        except ValueError:
            selection_list = None
        except KeyboardInterrupt:
            raise ValueError
        print('%s Invalid. Input list of integers between 0 and %s or Ctrl-C '
              'to exit.' % (selection_txt, index))
    context.spinner.start()


def set_input_variable(ctx, var_, config_file_name, default_value):
    """
    Set the variable defined by var_ to one of the following:
        - Itself if it has a value
        - The value from the config file if that exists
        - The default define default_value

    This sets the order for inputs to:
        1. definition on the command line or env
        2. Definition in the config file
        3. Default value
    """
    if var_:
        rtn_value = var_
    elif ctx.default_map and config_file_name in ctx.default_map:
        rtn_value = ctx.default_map[config_file_name]
    else:
        rtn_value = default_value
    return rtn_value


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
