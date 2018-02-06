"""pacstrap command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.context as context
import cleanroom.exceptions as ex
import cleanroom.helper.archlinux.pacman as pacman
import cleanroom.helper.generic.file as file
import cleanroom.run as run


class PacstrapCommand(cmd.Command):
    """The pacstrap command."""

    def __init__(self):
        """Constructor."""
        pass

    def validate_arguments(self, line_number, args):
        """Validate the arguments."""
        if len(args) < 2:
            raise ex.ParseError(line_number,
                                'pacstrap needs a config file and at least '
                                'one package or group to install.')
        return None

    def execute(self, run_context, args):
        """Execute command."""
        pac_object = pacman.Pacman(run_context)

        pacstrap_config = args[0]
        self._prepare_keyring(run_context, pac_object, pacstrap_config)

        pac_object.pacstrap(pacstrap_config, args[1:])

    def _prepare_keyring(self, run_context, pac_object, pacstrap_config):
        # Make sure important pacman directories exist:
        file.makedirs(run_context, pac_object.host_gpg_directory())
        pacman_key = run_context.ctx.binary(context.Binaries.PACMAN_KEY)
        run.run(pacman_key,
                '--config', pacstrap_config,
                '--gpgdir', pac_object.host_gpg_directory(),
                '--init',
                exit_code=0,
                work_directory=run_context.ctx.systems_directory(),
                trace_output=run_context.ctx.printer.trace)
        run.run(pacman_key,
                '--config', pacstrap_config,
                '--gpgdir', pac_object.host_gpg_directory(),
                '--populate', 'archlinux',
                exit_code=0,
                work_directory=run_context.ctx.systems_directory(),
                trace_output=run_context.ctx.printer.trace)
