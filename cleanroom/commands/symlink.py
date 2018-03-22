"""symlink command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.exceptions as ex
import cleanroom.helper.generic.file as file


class SymlinkCommand(cmd.Command):
    """The symlink command."""

    def __init__(self):
        """Constructor."""
        super().__init__('symlink <SOURCE> <TARGET> [base_directory=BASE]',
                         'Create a symlink.')

    def validate_arguments(self, run_context, *args, **kwargs):
        """Validate the arguments."""
        if len(args) != 2:
            raise ex.ParseError('symlink needs a source and a target.',
                                run_context=run_context)
        return None

    def __call__(self, run_context, *args, **kwargs):
        """Execute command."""
        source = args[0]
        target = args[1]
        base = kwargs.get('base_directory', None)

        file.symlink(run_context, source, target, base_directory=base)
