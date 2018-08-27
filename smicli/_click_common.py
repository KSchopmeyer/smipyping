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
Table printer.  This is being replaced by the python tabulate package as
that package develops more capabilities.  Currently the only functions in
this module used are the csv format and the htmo format
"""
import copy
import six
import prompt_toolkit
import pywbem
import click
from tabulate import tabulate
from ._tableoutput import HtmlTable


__all__ = ['DEFAULT_CONFIG_FILE', 'SMICLI_PROMPT', 'SMICLI_HISTORY_FILE',
           'DEFAULT_SMICLI_CONFIG_FILES', 'pick_from_list',
           'pick_multiple_from_list', 'print_table',
           'get_target_id', 'get_multiple_target_ids',
           'test_db_updates_allowed']

#: Flag to determine if smicli can update the database.  This either allows
#: or disallows any of the add, modify, delete subcommands that execute on
#: the database as well as the cimping -s option and the explorer option
#: that update the smi version.
DB_UPDATES_ALLOWED = True

USE_TABULATE = False
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

DEFAULT_OUTPUT_FORMAT = 'simple'


def local_prompt(txt):
    """ Single function for prompt. This only exists to allow testing the
    validate prompt code since this is mocked as part of the tests.
    Issues promplt_toolkit prompt and returns with reponse.
    """
    assert isinstance(txt, six.text_type)

    return prompt_toolkit.prompt(txt)


def validate_prompt(text=""):
    """
    Issue prompt and get y/n response. Input parameter text is prepended to
    the prompt output.
    """
    rslt = local_prompt(unicode('%s valid (y/n): ' % text))
    return True if rslt == 'y' else False


def test_db_updates_allowed():
    """
    Test if db updates allowed and return True if allowed. If not allowed
    generate click exception.
    """
    if DB_UPDATES_ALLOWED:
        return True
    click.clickException('Subcommands that update the database are not '
                         'allowed.')


def pick_from_list(context, options, title):
    """
    Interactive component that displays a set of options (strings) and asks
    the user to select one.  Returns the item and index of the selected string.

    Parameters:
      options:
        List of strings, one per line of the selection

      title:
        Title to display before selection

    Retries until either integer within range of options list is input
    or user enters no value. Ctrl_C ends even the REPL.

    Returns: Index of selected item or None if user choses to not input

    Exception: Returns ValueError if Ctrl-C input from console.

    TODO: This could be replaced by the python pick library that would use
    curses for the selection process.
    """
    context.spinner.stop()

    click.echo(title)
    index = -1
    for str_ in options:
        index += 1
        click.echo('%s: %s' % (index, str_))
    selection = None
    msg = 'Input integer between 0 and %s or Enter to abort selection: ' % index
    while True:
        try:
            selection = local_prompt(unicode(msg))
            if not selection:
                return None
            selection = int(selection)
            if selection >= 0 and selection <= index:
                return selection
        except ValueError:
            pass
        click.echo('%s Invalid. %s' % (selection, msg))
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

    TODO: FUTURE This could be replaced by the python pick library that would
    use curses for the selection process.
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
            response = local_prompt(
                u'Select multiple entries by index (index< index> or Enter to '
                u'abort >')
            if not response:
                return None
            selections = response.split()
            for selection_txt in selections:
                if selection_txt.isdigit():
                    selection = int(selection_txt)
                    if selection >= 0 and selection <= index:
                        selection_list.append(selection)
                    else:
                        raise ValueError('Invalid input %s' % selection_txt)
                else:
                    raise ValueError('Invalid input %s' % selection_txt)
            return selection_list
        except ValueError:
            selection_list = None
        print('%s Invalid. Input list of integers between 0 and %s or Enter '
              'to abort selection.' % (selection_txt, index))
    context.spinner.start()


def pick_target_id(context):
    """
    Interactive selection of target id from list presented on the console.

      Parameters ()
         The click_context which contains target data information.

      Returns:
        target_id selected or None if user enter ctrl-C
    """
    targets_list = context.targets_tbl.keys()
    display_options = []

    for t in targets_list:
        display_options.append(u'    id=%s %s company=%s, product=%s' %
                               (t, context.targets_tbl.get_url_str(t),
                                context.targets_tbl[t]['CompanyName'],
                                context.targets_tbl[t]['Product']))
    try:
        index = pick_from_list(context, display_options, "Pick TargetID:")
    except ValueError:
        pass
    if index is None:
        click.echo('Abort command')
        return None
    return targets_list[index]


def get_target_id(context, targetid, options=None, allow_none=False):
    """
        Get the target based on the value of targetid or the value of the
        interactive option.  If targetid is an
        integer, get targetid directly and generate exception if this fails.
        If it is ? use the interactive pick_target_id.
        If options exist test for 'interactive' option and if set, call
        pick_target_id
        This function executes the pick function if the targetid is "?" or
        if options is not None and the interactive flag is set

        This is a support function for any subcommand requiring the target id

        This support function always tests the target_id to against the
        targets table.

        Parameters:

          context(): Current click context

          targetid(:term:`string` or :term:`integer` or None):
            The targets database target id as a string or integer or the
            string "?" or the value None

          options: The click options.  Used to determine if --interactive mode
            is defined

          allow_none(:class:`py:bool`):
            If True, None is allowed as a value and returned. Otherwise
            None is considered invalid. This is used to separate the cases
            where the target id is an option that may have a None value vs.
            those cases where it is a required parameter.

        Returns:
            Returns integer target_id of a valid targetstbl TargetID

        raises:
          KeyError if target_id not in table and allow_none is False
    """
    if allow_none and targetid is None:
        return targetid
    context.spinner.stop()

    if options and 'interactive' in options and options['interactive']:
        context.spinner.stop()
        targetid = pick_target_id(context)
    elif isinstance(targetid, six.integer_types):
        pass
    elif isinstance(targetid, six.string_types):
        if targetid == "?":
            context.spinner.stop()
            targetid = pick_target_id(context)
        else:
            try:
                targetid = int(targetid)
            except ValueError:
                raise click.ClickException('TargetID must be integer or "?" '
                                           'not %s' % targetid)
    else:
        raise click.ClickException("TargetID %s could not process" % targetid)

    if targetid is None:
        click.echo("Operation aborted by user.")

    try:
        context.targets_tbl.get_target(targetid)
    except KeyError as ke:
        raise click.ClickException('Target ID %s  not in targets '
                                   'table. Exception %s: %s.' %
                                   (targetid, ke.__class__.__name__,
                                    ke))
    context.spinner.start()
    return targetid


def pick_multiple_target_ids(context):
    """
    Interactive selection of target ids from list presented on the console.

      Parameters ()
         The click_context which contains target data information.

      Returns:
        target_id selected or None if user enter ctrl-C
    """
    targets_list = context.targets_tbl.keys()
    display_options = []

    for t in targets_list:
        display_options.append(u'    id=%s %s company=%s, product=%s' %
                               (t, context.targets_tbl.get_url_str(t),
                                context.targets_tbl[t]['CompanyName'],
                                context.targets_tbl[t]['Product']))
    try:
        indexes = pick_multiple_from_list(context, display_options,
                                          "Pick TargetIDs:")
    except ValueError:
        pass
    if indexes is None:
        click.echo('Abort command')
        return None
    return [targets_list[index] for index in indexes]


def get_multiple_target_ids(context, targetids, options=None, allow_none=False):
    """
        Get the target based on the value of targetid or the value of the
        interactive option.  If targetid is an
        integer, get targetid directly and generate exception if this fails.
        If it is ? use the interactive pick_target_id.
        If options exist test for 'interactive' option and if set, call
        pick_target_id
        This function executes the pick function if the targetid is "?" or
        if options is not None and the interactive flag is set

        This is a support function for any subcommand requiring the target id

        This support function always tests the target_id to against the
        targets table.

        Parameters:

          context(): Current click context

          targetid(list of :term:`string` or list of:term:`integer` or None):
            The targets database target id as a string or integer or the
            string "?" or the value None

          options: The click options.  Used to determine if --interactive mode
            is defined

          allow_none(:class:`py:bool`):
            If True, None is allowed as a value and returned. Otherwise
            None is considered invalid. This is used to separate the cases
            where the target id is an option that may have a None value vs.
            those cases where it is a required parameter.

        Returns:
            Returns integer target_id of a valid targetstbl TargetID

        raises:
          KeyError if target_id not in table and allow_none is False
    """
    if allow_none and targetids is None or targetids == []:
        return targetids
    context.spinner.stop()

    if options and 'interactive' in options and options['interactive']:
        context.spinner.stop()
        int_target_ids = pick_multiple_target_ids(context)
    elif isinstance(targetids, (list, tuple)):
        int_target_ids = []
        if len(targetids) == 1 and \
                targetids[0] == "?":
            context.spinner.stop()
            int_target_ids = pick_multiple_target_ids(context)
        else:
            for targetid in targetids:
                if isinstance(targetid, six.integer_types):
                    pass
                elif isinstance(targetid, six.string_types):
                    try:
                        targetid = int(targetid)
                    except ValueError:
                        raise click.ClickException('TargetID must be integer. '
                                                   '"%s" cannot be mapped to '
                                                   'integer' % targetid)
                else:
                    raise click.ClickException('List of target Ids invalid')
                try:
                    context.targets_tbl.get_target(targetid)
                    int_target_ids.append(targetid)
                except KeyError as ke:
                    raise click.ClickException('Target ID %s not in database. '
                                               'Exception: %s: %s' %
                                               (targetid,
                                                ke.__class__.__name__, ke))
                int_target_ids.append(targetid)

            context.spinner.start()
            return int_target_ids

    if int_target_ids == []:
        click.echo("Operation aborted by user.")
    context.spinner.start()
    return int_target_ids


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


def print_table(rows, headers=None, title=None, table_format='simple'):
    """
    Create table output for the title, headers, and rows provided and
    return the resulting string.

    Parameters:
        rows(list of lists or other iterable of iterables):
            Each itterable within the outter iterable is a row in the table
            Each item in the inner iterable is the data in a cell.  It may
            be string, numeric, or None.

            TODO: Define inner table
            TODO: define formattting

        headers(list of :term:`string`):
            Each string in the list is a column header. Optional and if not
            included, no header is placed on the table

        title(:term:`string` or None):
            If string that string is printed as a title before the table
            normally left justified.

        table_format(:term:`string`):
            one of the strings defined in TABLE_FORMATS list that defines
            the output format of the table


    """
    if table_format == 'table':
        table_format = 'psql'

    if headers and isinstance(headers, six.string_types):
        headers = [headers]

    # all formats except html go to tabulate directly
    if table_format == 'html':
        result = build_html_table(rows, headers, title)
        click.echo('%s\n' % result)

        # Currently tabulate does not allow setting borders, etc. on
        # html tables. The following would be the tabulate code.
        # if title:
        #    title = '<p>%s<\\p>' % title
        # click.echo(tabulate(rows, headers=headers,
        #                    tablefmt=table_format))
    else:
        if title:
            click.echo('\n\n%s\n' % title)
        click.echo(tabulate(rows, headers=headers, tablefmt=table_format))


def build_html_table(rows, headers, title):
    """
    Print a table and header in html format.
    """
    # Create copy to avoid modifying original
    n_rows = copy.deepcopy(rows)
    n_headers = copy.copy(headers)
    # Convert EOL to html break for html output.
    for row in n_rows:
        for i, cell in enumerate(row):
            if isinstance(cell, six.string_types):
                row[i] = cell.replace('\n', '<br />')
    for i, header in enumerate(n_headers):
        if isinstance(header, six.string_types):
            n_headers[i] = header.replace('\n', '<br />')
    if title:
        print('\n<p>%s</p>\n' % title)
    return HtmlTable(rows=n_rows, header_row=n_headers)


def raise_click_exception(exc, error_format='sg'):
    """
    Raise a ClickException with the desired error message format.
    Parameters:
      exc (exception or string):
        The exception or the message.
      error_format (string):
        The error format (see ``--error-format`` general option).
    """
    if error_format == 'def':
        if isinstance(exc, pywbem.Error):
            error_str = exc.str_def()
        else:
            assert isinstance(exc, six.string_types)
            error_str = "classname: None, message: {}".format(exc)
    else:
        assert error_format == 'msg'
        if isinstance(exc, pywbem.Error):
            error_str = "{}: {}".format(exc.__class__.__name__, exc)
        else:
            assert isinstance(exc, six.string_types)
            error_str = exc
    raise click.ClickException(error_str)
