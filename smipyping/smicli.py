from click_repl import repl
import click
# import click_spinner

# Display of options in usage line
GENERAL_OPTIONS_METAVAR = '[GENERAL-OPTIONS]'
CMD_OPTS_TXT = '[COMMAND-OPTIONS]'
def targets_cli(object):

    def __init__(self, prog):
    @click.group(invoke_without_command=True,
                 options_metavar=GENERAL_OPTIONS_METAVAR)
    @click.option('-c', '--config_file', type=str, envvar='SMI_CONFIG_FILE',
              help="Configuration file to use for config information.")
    @click.option('-v', '--verbose', type=str, is_flag=True,
                  help='Display extra information about the processing.')  
            
    @click.version_option(help="Show the version of this command and exit.")
    @click.pass_context

def targets(ctx, config_file, verbose):
    """
    Command line interface for the targets.

    The options shown above that can also be specified on any of the
    (sub-)commands.
    """
    # TODO add for noverify, etc.
    if ctx.obj is None:
        # We are in command mode or are processing the command line options in
        # interactive mode.
        # We apply the documented option defaults.
        if output_format is None:
            output_format = DEFAULT_CONFIG_FILE
        # TODO force noverify for now.
        noverify = True
    else:
        # We are processing an interactive command.
        # We apply the option defaults from the command line options.
        if server is None:
            server = ctx.obj.config_file
  
    # Create a command context for each command: An interactive command has
    # its own command context different from the command context for the
    # command line.
    ctx.obj = Context(ctx, config_file, verbose)

    # Invoke default command
    if ctx.invoked_subcommand is None:
        repl(ctx)

class Context(object):
    """
        Manage the click context object
    """

    def __init__(self, ctx, config_file, verbose):
        self._config_file = config_file
        self._verbose = verbose
        # self._spinner = click_spinner.Spinner()

    @property
    def config_file(self):
        """
        :term:`string`: Hostname or IP address of the HMC.
        """
        return self._config_file

    @property
    def verbose(self):
        """
        :term:`string`: Userid on the HMC.
        """
        return self._verbose



    # @property
    # def spinner(self):
    #    """
    #    :class:`~click_spinner.Spinner` object.
    #    """
    #    return self._spinner

    def execute_cmd(self, cmd):
        """
        Call the cmd executor defined by cmd with the spinner
        """
        if self._conn is None:
            if self._server is None:
                raise click.ClickException("No WBEM Server defined")
            # TODO expand this
            self._conn = _remote_connection(self.server, self.namespace,
                                            user=None,
                                            password=None)
        # self.spinner.start()
        try:
            cmd()
        finally:
            # self.spinner.stop()
            pass

    @property
    def verbose(self):
        """
        :class:`~click_spinner.Spinner` object.
        """
        return self._verbose

