"""pacman command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.exceptions as ex
import cleanroom.helper.archlinux.pacman as pacman


class PacmanCommand(cmd.Command):
    """The pacman command."""

    def __init__(self):
        """Constructor."""
        super().__init__('pacman <PACKAGES>',
                         'Run pacman to install <PACKAGES>.')

    def validate_arguments(self, file_name, line_number, *args, **kwargs):
        """Validate the arguments."""
        if len(args) < 1:
            raise ex.ParseError('pacman needs at least '
                                'one package or group to install.',
                                file_name=file_name, line_number=line_number)

        return None

    def __call__(self, file_name, line_number, run_context, *args, **kwargs):
        """Execute command."""
        pac_object = pacman.Pacman(run_context)
        pac_object.pacman(*args)
