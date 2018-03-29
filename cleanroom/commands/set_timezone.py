# -*- coding: utf-8 -*-
"""set_timezone command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.helper.generic.file as file


class SetTimezoneCommand(cmd.Command):
    """The set_timezone command."""

    def __init__(self):
        """Constructor."""
        super().__init__('set_timezone', syntax='<TIMEZONE>',
                         help='Set up the timezone for a system.')

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        return self._validate_arguments_exact(location, 1,
                                              '"{}" needs a timezone to '
                                              'set up.', *args, **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        etc = '/etc'
        localtime = 'localtime'
        etc_localtime = etc + '/' + localtime

        timezone = args[0]
        full_timezone = '../usr/share/zoneinfo/' + timezone
        if not file.exists(system_context, full_timezone, base_directory=etc):
            raise ex.GenerateError('Timezone "{}" not found when trying to '
                                   'set timezone.'.format(timezone),
                                   location=location)

        system_context.execute(location, 'remove', etc_localtime)
        system_context.execute(location, 'symlink', full_timezone, localtime,
                               base_directory='/etc')
