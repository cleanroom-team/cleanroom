#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Base class for commands usable in the system definition files.

The Command class will be used to derive all system definition file commands
from.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from . import exceptions as ex


class Command:
    """A command that can be used in to set up machines."""

    def __init__(self, syntax_string, help_string):
        """Constructor."""
        self._syntax_string = syntax_string
        self._help_string = help_string

    def name(self):
        """Return the command name."""
        return self.__module__[19:]  # minus cleanroom.commands.

    def validate_arguments(self, file_name, line_number, *args, **kwargs):
        """Validate all arguments.

        Validate all arguments and optionally return a dependency for
        the system.
        """
        if len(args) != 0:
            raise ex.ParseError('Command does not take arguments.',
                                file_name=file_name, line_number=line_number)
        return None

    def __call__(self, run_context, *args, **kwargs):
        """Execute command."""
        return True

    def syntax(self):
        """Return syntax description."""
        return self._syntax_string

    def help(self):
        """Print help string."""
        return self._help_string
