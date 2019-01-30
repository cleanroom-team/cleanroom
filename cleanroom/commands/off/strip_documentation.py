# -*- coding: utf-8 -*-
"""strip_documentation command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.location import Location
from cleanroom.generator.command import Command
from cleanroom.generator.systemcontext import SystemContext

import typing


class StripDocumentationCommand(Command):
    """The strip_documentation Command."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__('strip_documentation',
                         help_string='Strip away documentation files.', file=__file__)

    def validate_arguments(self, location: Location, *args: typing.Any, **kwargs: typing.Any) \
            -> typing.Optional[str]:
        """Validate arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

        return None

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        system_context.add_hook(location, 'export', '_strip_documentation_hook')
