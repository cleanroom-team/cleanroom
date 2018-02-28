"""systemd_enable command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.exceptions as ex


class SystemdEnableCommand(cmd.Command):
    """The systemd_enable command."""

    def __init__(self):
        """Constructor."""
        super().__init__('systemd_enable <UNIT> [<MORE_UNITS>]',
                         'Enable systemd units.')

    def validate_arguments(self, file_name, line_number, *args, **kwargs):
        """Validate the arguments."""
        if len(args) == 0:
            raise ex.ParseError('systemd_enable needs at least one unit '
                                'to enable.',
                                file_name=file_name, line_number=line_number)

        return None

    def __call__(self, file_name, line_number, run_context, *args, **kwargs):
        """Execute command."""
        run_context.run('/usr/bin/systemctl',
                        '--root={}'.format(run_context.fs_directory()),
                        'enable', *args, outside=True)
