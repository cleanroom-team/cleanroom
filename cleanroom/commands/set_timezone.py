"""set_timezone command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.exceptions as ex
import cleanroom.helper.generic.file as file


class SetTimezoneCommand(cmd.Command):
    """The set_timezone command."""

    def __init__(self):
        """Constructor."""
        super().__init__('set_timezone <TIMEZONE>',
                         'Set up the timezone for a system.')

    def validate_arguments(self, file_name, line_number, *args, **kwargs):
        """Validate the arguments."""
        if len(args) != 1:
            raise ex.ParseError('set_timezone needs a timezone to set up.',
                                file_name=file_name, line_number=line_number)

        return None

    def __call__(self, file_name, line_number, run_context, *args, **kwargs):
        """Execute command."""
        etc = '/etc'
        localtime = 'localtime'
        etc_localtime = etc + '/' + localtime

        timezone = args[0]
        full_timezone = '../usr/share/zoneinfo/' + timezone
        if not file.exists(run_context, full_timezone, base_directory=etc):
            raise ex.GenerateError('Timezone "{}" not found when trying to '
                                   'set timezone.'.format(timezone),
                                   file_name=file_name,
                                   line_number=line_number)

        file.remove(run_context, etc_localtime)
        file.symlink(run_context, full_timezone, localtime, base_directory=etc)
