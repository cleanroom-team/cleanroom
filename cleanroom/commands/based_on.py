# -*- coding: utf-8 -*-
"""based_on command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.exceptions as ex
import cleanroom.printer as printer

import re


class BasedOnCommand(cmd.Command):
    """The based_on command."""

    def __init__(self):
        """Constructor."""
        super().__init__('based_on', syntax='<SYSTEM_NAME>)',
                         help='Use <SYSTEM_NAME> as a base for this '
                         'system. Use "scratch" to start from a '
                         'blank slate.\n\n'
                         'Note: This command needs to be the first in the '
                         'system definition file!')

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        base = None

        self._validate_arguments_exact(location, 1,
                                       '"{}" needs a system name.', *args)
        base = args[0]
        assert(base)

        system_pattern = re.compile('^[A-Za-z][A-Za-z0-9_-]*$')
        if not system_pattern.match(base):
            raise ex.ParseError('"{}" got invalid base system name "{}".'
                                .format(self.name(), base), location=location)
        return None if self._is_scratch(base) else base

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        base_system = args[0]
        if self._is_scratch(base_system):
            printer.verbose('Building from scratch!')
            location.next_line_offset('testing')
            system_context.add_hook(location, '_test', '_test')
        else:
            printer.verbose('Building on top of {}.'.format(base_system))
            system_context.execute(location, '_restore', base_system)

    def _is_scratch(self, base):
        return base == 'scratch'
