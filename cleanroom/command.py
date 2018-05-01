# -*- coding: utf-8 -*-
"""Base class for commands usable in the system definition files.

The Command class will be used to derive all system definition file commands
from.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.exceptions as ex

import os
import os.path


class Command:
    """A command that can be used in to set up machines."""

    def __init__(self, name, *, syntax='', help, file):
        """Constructor."""
        assert(name)
        self._name = name
        self._syntax_string = syntax
        self._help_string = help
        self._base_directory = os.path.dirname(os.path.realpath(file))

    def name(self):
        """Return the command name."""
        return self._name

    def helper_directory(self):
        """Return the helper directory."""
        full_path = os.path.join(self._base_directory, 'helper', self.name())
        if os.path.isdir(full_path):
            return full_path

    def validate_arguments(self, location, *args, **kwargs):
        """Validate all arguments.

        Validate all arguments and optionally return a dependency for
        the system.
        """
        print('Command "{}"" called validate_arguments illegally!'
              .format(self.name()))
        assert(False)

    def _validate_no_arguments(self, location, *args, **kwargs):
        self._validate_no_args(location, *args)
        self._validate_kwargs(location, (), **kwargs)

    def _validate_arguments_exact(self, location, arg_count, message,
                                  *args, **kwargs):
        self._validate_args_exact(location, arg_count, message, *args)
        self._validate_kwargs(location, (), **kwargs)

    def _validate_arguments_at_least(self, location, arg_count, message,
                                     *args, **kwargs):
        self._validate_args_at_least(location, arg_count, message, *args)
        self._validate_kwargs(location, (), **kwargs)

    def _validate_no_args(self, location, *args):
        self._validate_args_exact(location, 0,
                                  '"{}"" does not take arguments.', *args)

    def _validate_args_exact(self, location, arg_count, message, *args):
        if len(args) != arg_count:
            raise ex.ParseError(message.format(self.name()), location=location)

    def _validate_args_at_least(self, location, arg_count, message, *args):
        if len(args) < arg_count:
            raise ex.ParseError(message.format(self.name()), location=location)

    def _validate_kwargs(self, location, known_kwargs, **kwargs):
        if not known_kwargs:
            if kwargs:
                raise ex.ParseError('"{}" does not accept keyword arguments.'
                                    .format(self.name()), location=location)
        else:
            for key, value in kwargs.items():
                if key not in known_kwargs:
                    raise ex.ParseError('"{}" does not accept the keyword '
                                        'arguments "{}".'
                                        .format(self.name(), key),
                                        location=location)

    def _require_kwargs(self, location, required_kwargs, **kwargs):
        for key in required_kwargs:
            if key not in kwargs:
                raise ex.ParseError('"{}" requires the keyword '
                                    'arguments "{}" to be passed.'
                                    .format(self.name(), key),
                                    location=location)

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
