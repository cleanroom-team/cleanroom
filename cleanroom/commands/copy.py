"""copy command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.exceptions as ex
import cleanroom.helper.generic.file as file


class CopyFileCommand(cmd.Command):
    """The copy command."""

    def __init__(self):
        """Constructor."""
        super().__init__('copy <SOURCE> <DESTINATION> [force=True] '
                         '[from_outside=True] [to_outside=True]',
                         'Copy a file within the system.')

    def validate_arguments(self, run_context, *args, **kwargs):
        """Validate the arguments."""
        if len(args) != 2:
            raise ex.ParseError('copy needs source and a destination.',
                                run_context=run_context)

        if kwargs.get('from_outside', False) \
           and kwargs.get('to_outside', False):
            raise ex.ParseError('You can not copy a file from_outside '
                                'to_outside.', run_context=run_context)

        return None

    def __call__(self, run_context, *args, **kwargs):
        """Execute command."""
        file.copy(run_context, args[0], args[1], **kwargs)
