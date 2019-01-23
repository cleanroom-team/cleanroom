# -*- coding: utf-8 -*-
"""chmod command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.location import Location
from cleanroom.generator.command import Command
from cleanroom.generator.systemcontext import SystemContext
from cleanroom.generator.helper.generic.file import chmod

import typing


class ChmodCommand(Command):
    """The chmod command."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__('chmod', syntax='<MODE> <FILE>+',
                         help_string='Chmod a file or files.', file=__file__)

    def validate_arguments(self, location: Location,
                           *args: typing.Any, **kwargs: typing.Any) -> typing.Optional[str]:
        """Validate the arguments."""
        self._validate_arguments_at_least(location, 2,
                                          '"{}" takes a mode and one '
                                          'or more files.', *args, **kwargs)

        return None

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        chmod(system_context, *args, **kwargs)
