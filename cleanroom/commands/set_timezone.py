# -*- coding: utf-8 -*-
"""set_timezone command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.exceptions import GenerateError
from cleanroom.location import Location
from cleanroom.generator.command import Command
from cleanroom.generator.helper.generic.file import exists
from cleanroom.generator.systemcontext import SystemContext

import typing


class SetTimezoneCommand(Command):
    """The set_timezone command."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__('set_timezone', syntax='<TIMEZONE>',
                         help_string='Set up the timezone for a system.',
                         file=__file__)

    def validate_arguments(self, location: Location, *args: typing.Any, **kwargs: typing.Any) \
            -> typing.Optional[str]:
        """Validate the arguments."""
        self._validate_arguments_exact(location, 1,
                                       '"{}" needs a timezone to set up.',
                                       *args, **kwargs)

        return None

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        etc = '/etc'
        localtime = 'localtime'
        etc_localtime = etc + '/' + localtime

        timezone = args[0]
        full_timezone = '../usr/share/zoneinfo/' + timezone
        if not exists(system_context, full_timezone, work_directory=etc):
            raise GenerateError('Timezone "{}" not found when trying to set timezone.'
                                .format(timezone), location=location)

        system_context.execute(location, 'remove', etc_localtime)
        system_context.execute(location.next_line(), 'symlink', full_timezone, localtime,
                               work_directory='/etc')
