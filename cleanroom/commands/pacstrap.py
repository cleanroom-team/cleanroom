"""pacstrap command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.context as context
import cleanroom.execobject as eo
import cleanroom.exceptions as ex
import cleanroom.helper.archlinux.pacman as pacman
import cleanroom.helper.generic.file as file
import cleanroom.run as run

import os


class PacstrapCommand(cmd.Command):
    """The pacstrap command."""

    def __init__(self):
        """Constructor."""
        pass

    def validate_arguments(self, file_name, line_number, *args, **kwargs):
        """Validate the arguments."""
        if len(args) < 1:
            raise ex.ParseError(file_name, line_number,
                                'pacstrap needs at least '
                                'one package or group to install.')

        if 'config' not in kwargs:
            raise ex.ParseError(file_name, line_number,
                                'pacstrap needs a "config" keyword argument.')
        return None

    def __call__(self, run_context, *args, **kwargs):
        """Execute command."""
        pac_object = pacman.Pacman(run_context)

        pacstrap_config = kwargs['config']
        self._prepare_keyring(run_context, pac_object, pacstrap_config)

        pac_object.pacstrap(pacstrap_config, args)

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

        gpgdir = pac_object.target_gpg_directory()

        run_context.add_hook('_teardown',
                             eo.ExecObject(
                                ('<pacstrap command>', 1),
                                'clean pacman key directory', None,
                                file.Deleter(),
                                os.path.join(gpgdir, 'S.scdaemon'),
                                os.path.join(gpgdir, 'S.gpg-agent'),
                                os.path.join(gpgdir, 'S.gpg-agent.browser'),
                                os.path.join(gpgdir, 'S.gpg-agent.extra'),
                                os.path.join(gpgdir, 'S.gpg-agent.ssh'),
                                os.path.join(gpgdir, 'pubring.gpg~'),
                                force=True))
