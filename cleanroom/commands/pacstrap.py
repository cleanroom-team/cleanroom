"""pacstrap command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.helper.archlinux.pacman as pacman
import cleanroom.helper.generic.file as file
import cleanroom.command as cmd
import cleanroom.exceptions as ex


class PacstrapCommand(cmd.Command):
    """The pacstrap command."""

    def __init__(self):
        """Constructor."""
        pass

    def validate_arguments(self, line_number, args):
        """Validate the arguments."""
        if len(args) == 0:
            raise ex.ParseError(line_number, 'pacstrap needs at least one '
                                'package or group to install.')
        return None

    def execute(self, run_context, args):
        """Execute command."""
        pac_object = pacman.Pacman(run_context)

        run_context.ctx.printer.h2('Pacstrap-ing system')
        all_packages = []
        for a in args:
            all_packages += a.split()

        self._prepare_for_pacstrap(run_context, pac_object)

    def _prepare_for_pacstrap(self, run_context, pac_object):
        # Make sure important pacman directories exist:
        file.makedirs(run_context, pac_object.cache_directory())
        file.makedirs(run_context, pac_object.db_directory())
        file.makedirs(run_context, pac_object.gpg_directory())
