#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Base class for commands usable in the system definition files.

The Command class will be used to derive all system definition file commands
from.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


class Command:
    """A command that can be used in to set up machines."""

    def __init__(self):
        """Constructor."""
        pass

    def validate_arguments(self, line, args):
        """Validate all arguments.

        Validate all arguments and optionally return a dependency for
        the system.
        """
        return None

    def execute(self, args):
        """Execute command."""
        return True
