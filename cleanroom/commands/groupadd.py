"""groupadd command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.exceptions as ex
import cleanroom.helper.generic.group as group


class GroupaddCommand(cmd.Command):
    """The groupadd command."""

    def __init__(self):
        """Constructor."""
        super().__init__('groupadd <NAME> [force=False] [system=False] '
                         '[gid=<GID>]',
                         'Add a group.')

    def validate_arguments(self, run_context, *args, **kwargs):
        """Validate the arguments."""
        if len(args) != 1:
            raise ex.ParseError('groupadd needs a groupname.',
                                run_context=run_context)

        return None

    def __call__(self, run_context, *args, **kwargs):
        """Execute command."""
        group.groupadd(run_context, args[0], **kwargs)
