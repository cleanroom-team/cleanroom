# -*- coding: utf-8 -*-
"""sed command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.location import Location
from cleanroom.generator.command import Command
from cleanroom.generator.systemcontext import SystemContext

import typing


class SedCommand(Command):
    """The sed command."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__('sed', syntax='<PATTERN> <FILE>',
                         help_string='Run sed on a file.', file=__file__)

    def validate_arguments(self, location: Location, *args: typing.Any, **kwargs: typing.Any) \
            -> typing.Optional[str]:
        """Validate the arguments."""
        self._validate_arguments_exact(location, 2,
                                       '"{}" needs a pattern and a file.',
                                       *args, **kwargs)

        return None

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        system_context.run('/usr/bin/sed', '-i', '-e', args[0],
                           system_context.file_name(args[1]), outside=True)
