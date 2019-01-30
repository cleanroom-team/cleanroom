# -*- coding: utf-8 -*-
"""based_on command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.exceptions import ParseError
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext
from cleanroom.printer import trace, verbose

import re
import typing


class BasedOnCommand(Command):
    """The based_on command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__('based_on', syntax='<SYSTEM_NAME>)',
                         help_string='Use <SYSTEM_NAME> as a base for this '
                         'system. Use "scratch" to start from a '
                         'blank slate.\n\n'
                         'Note: This command needs to be the first in the '
                         'system definition file!', file=__file__,
                         **services)

    def validate(self, location: Location,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Validate the arguments."""
        self._validate_arguments_exact(location, 1,
                                       '"{}" needs a system name.', *args, **kwargs)
        base = args[0]

        system_pattern = re.compile('^[A-Za-z][A-Za-z0-9_-]*$')
        if not system_pattern.match(base):
            raise ParseError('"{}" got invalid base system name "{}".'
                             .format(self.name(), base), location=location)

    def dependency(self, *args: typing.Any, **kwargs: typing.Any) -> str:
        return args[0]

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""

        base_system = args[0]
        if base_system == 'scratch':
            verbose('Building from scratch!')
            system_context.add_hook(location, 'testing', '_test')
            self._execute(location, system_context, '_setup')
        else:
            verbose('Building on top of {}.'.format(base_system))
            self._execute(location, system_context, '_restore', base_system)

        # FIXME:
        ## run_hooks("_setup")
