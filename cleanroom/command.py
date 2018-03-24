# -*- coding: utf-8 -*-
"""Base class for commands usable in the system definition files.

The Command class will be used to derive all system definition file commands
from.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.exceptions as ex


class Command:
    """A command that can be used in to set up machines."""

    def __init__(self, name, *, syntax='', help):
        """Constructor."""
        assert(name)
        self._name = name
        self._syntax_string = syntax
        self._help_string = help

    def name(self):
        """Return the command name."""
        return self._name

    def validate_arguments(self, location, *args, **kwargs):
        """Validate all arguments.

        Validate all arguments and optionally return a dependency for
        the system.
        """
        print('Command "{}"" called validate_arguments illegally!'
              .format(self.name()))
        assert(False)
        return None

    def _validate_no_arguments(self, location, *args, **kwargs):
        if len(args) != 0:
            ex.ParseError('{} does not take arguments.'.format(self.name()),
                          location=location)
        if len(kwargs) != 0:
            ex.ParseError('{} does not take keyword arguments.'
                          .format(self.name()), location=location)
        return None

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        assert(False)
        return True

    def syntax(self):
        """Return syntax description."""
        if self._syntax_string:
            return '{} {}'.format(self._name, self._syntax_string)
        return self._name

    def help(self):
        """Print help string."""
        return self._help_string
