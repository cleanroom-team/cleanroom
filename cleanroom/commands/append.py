# -*- coding: utf-8 -*-
"""append command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.location import Location
from cleanroom.generator.command import Command
from cleanroom.generator.helper.generic.file import append_file
from cleanroom.generator.systemcontext import SystemContext

import typing


class AppendCommand(Command):
    """The append command."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__('append', syntax='<FILENAME> <CONTENTS>',
                         help_string='Append contents to file.', file=__file__)

    def validate_arguments(self, location: Location,
                           *args: typing.Any, **kwargs: typing.Any) -> typing.Optional[str]:
        """Validate the arguments."""
        self._validate_arguments_exact(location, 2,
                                       '"{}" needs a file and contents '
                                       'to append to it.', *args)
        self._validate_kwargs(location, ('force',), **kwargs)

        return None

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        to_write = system_context.substitute(args[1]).encode('utf-8')
        append_file(system_context, args[0], to_write, **kwargs)
