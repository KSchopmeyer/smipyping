from __future__ import print_function, absolute_import

from click_repl import repl
import click
# import click_spinner

from .smicli import wcli, CMD_OPTS_TXT, display_result, fix_propertylist

    def display(self, target_data):
        """
        Functiovn to display table data.

        gets the arguments for the display and display the  Table data.
        """
        disp_parser = _argparse.ArgumentParser(
            description='Display target data repository')

        disp_parser.add_argument('-s', '--sort',
                                 default='IP',
                                 help='Sort by field')

        # now that we're inside a subcommand, ignore the first
        # TWO argvs, ie the command and the subcommand
        args = disp_parser.parse_args(_sys.argv[2:])

        print('keys %s'  % list(target_data.table_format_dict))

        print('\n')
        target_data.display_all()

from .wclicmd import wcli, CMD_OPTS_TXT, display_result, fix_propertylist


@wcli.group('target', options_metavar=CMD_OPTS_TXT)
def target_group():
    """
    Command group for class operations.
    """
    pass


@class_group.command('get', options_metavar=CMD_OPTS_TXT)
@click.argument('CLASSNAME', type=str, metavar='CLASSNAME', required=True,)
@click.pass_obj
def targets_display(context, classname, **options):
    """
    get and display a list of classnames.
    """
    context.execute_cmd(lambda: cmd_targets_display(context, classname, options))

def cmd_class_list(context, classname, options):
    """ Execute the EnumerateClassNames operation."""
    try:
        if context.verbose:
            print('enumerateclassnames %s deepinheritance %s' %
                  (classname, options['deepinheritance']))
        result = context.conn.EnumerateClassNames(
            ClassName=classname,
            DeepInheritance=options['deepinheritance'])
        display_result(result)
    except Error as er:
        raise click.ClickException("%s: %s" % (er.__class__.__name__, er))
