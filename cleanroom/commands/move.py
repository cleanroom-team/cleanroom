"""move command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.exceptions as ex
import cleanroom.helper.generic.file as file


class MoveCommand(cmd.Command):
    """The move command."""

    def __init__(self):
        """Constructor."""
        super().__init__('move <SOURCE> [<SOURCE>] <DEST> ',
                         'Move file or directory.')

    def validate_arguments(self, run_context, *args, **kwargs):
        """Validate the arguments."""
        if len(args) < 2:
            raise ex.ParseError('move needs source and a destination.',
                                run_context=run_context)
        return None

    def __call__(self, run_context, *args, **kwargs):
        """Execute command."""
        file.move(file.expand_files(run_context, *args[:-1]), args[-1],
                  **kwargs)
