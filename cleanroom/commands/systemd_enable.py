"""systemd_enable command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.exceptions as ex
import cleanroom.helper.generic.systemd as sd


class SystemdEnableCommand(cmd.Command):
    """The systemd_enable command."""

    def __init__(self):
        """Constructor."""
        super().__init__('systemd_enable <UNIT> [<MORE_UNITS>]',
                         'Enable systemd units.')

    def validate_arguments(self, run_context, *args, **kwargs):
        """Validate the arguments."""
        if len(args) == 0:
            raise ex.ParseError('systemd_enable needs at least one unit '
                                'to enable.', run_context=run_context)
        return None

    def __call__(self, run_context, *args, **kwargs):
        """Execute command."""
        sd.systemd_enable(*args)
