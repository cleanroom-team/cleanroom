# -*- coding: utf-8 -*-
"""firejail_apps command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.exceptions import GenerateError, ParseError
from cleanroom.location import Location
from cleanroom.generator.command import Command
from cleanroom.generator.systemcontext import SystemContext

import os.path
import typing


class FirejailAppsConfigureCommand(Command):
    """The firejail_apps command."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__('firejail_apps', syntax='<APP>+',
                         help_string='Firejail applications.', file=__file__)

    def validate_arguments(self, location: Location, *args: typing.Any, **kwargs: typing.Any) \
            -> typing.Optional[str]:
        """Validate the arguments."""
        if not args:
            raise ParseError('"{}" does need at least one application.'
                             .format(self.name()), location=location)
        self._validate_arguments_at_least(location, 1,
                                          '"{}" needs at least one application.', *args)

        return None

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        for a in args:
            location.set_description('Processing application {}.'
                                     .format(a))
            desktop_file = '/usr/share/applications/{}.desktop'.format(a)
            if not os.path.exists(desktop_file):
                raise GenerateError('Desktop file "{}" not found.'
                                    .format(desktop_file), location=location)
            system_context.execute(location.next_line(), 'sed', '/^Exec=.*$$/ '
                                   's!^Exec=!Exec=/usr/bin/firejail !', desktop_file)
