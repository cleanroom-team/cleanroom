# -*- coding: utf-8 -*-
"""Base class for print_commands usable in the system definition files.

The Command class will be used to derive all system definition file print_commands
from.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from __future__ import annotations

from .exceptions import GenerateError, ParseError
from .location import Location
from .printer import trace, fail, success
from .systemcontext import SystemContext

import os
import os.path
import typing


ServicesType = typing.Mapping[str, typing.Any]


def _stringify(command: str, *args, **kwargs):
    args_str = ' "' + '" "'.join(args) + '"' if args else ''
    kwargs_str = ' '.join(map(lambda kv: kv[0] + '="' + str(kv[1]) + '"',
                              kwargs.items())) if kwargs else ''
    return '"{}"'.format(command) + args_str + kwargs_str


class Command:
    """A command that can be used in to set up a machines."""

    def __init__(self, name: str, *, file: str,
                 syntax: str = '', help_string: str,
                 services: ServicesType) \
            -> None:
        """Constructor."""
        self._name = name
        self._syntax_string = syntax
        self._help_string = help_string
        helper_directory = os.path.join(os.path.dirname(os.path.realpath(file)),
                                        'helper', self._name)
        self.__helper_directory = helper_directory if os.path.isdir(helper_directory) else None
        self._services = services

    @property
    def syntax_string(self) -> str:
        """Return syntax description."""
        if self._syntax_string:
            return '{} {}'.format(self._name, self._syntax_string)
        return self._name

    @property
    def name(self) -> str:
        return self._name

    @property
    def help_string(self) -> str:
        """Print help string."""
        return self._help_string

    def validate(self, location: Location,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Implement this!

        Validate all arguments.
        """
        fail('Command "{}"" called validate_arguments illegally!'
             .format(self.name))
        return None

    def dependency(self, *args: typing.Any, **kwargs: typing.Any) \
            -> typing.Optional[str]:
        """Maybe implement this, but this default implementation should be ok."""
        return None

    def execute(self, location: Location, system_context: SystemContext,
                *args: typing.Any, **kwargs: typing.Any) -> None:
        command_str = _stringify(self.name, *args, **kwargs)
        trace('{}: Execute {}.'.format(location, self.name, command_str))
        self(location, system_context, *args, **kwargs)
        success('{}: Executed {}{}'.format(location, self.name, command_str))

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Implement this!"""

    def _execute(self, location: Location, system_context: SystemContext,
                 command: str, *args: typing.Any, **kwargs: typing.Any) -> None:
        command_str = _stringify(command, *args, **kwargs)
        trace('{}: Execute {}.'.format(location, self.name, command_str))

        command_info = self.service('command_manager').command(command)
        if not command_info:
            raise GenerateError('Command "{}" not found.'.format(command))
        command_info.validate_func(location, *args, **kwargs)
        command_info.execute_func(location, system_context, *args, **kwargs)
        success('{}: Executed {}{}'.format(location, self.name, command_str))

    def service(self, service_name: str) -> typing.Any:
        return self._services.get(service_name, None)

    @property
    def _helper_directory(self) -> typing.Optional[str]:
        """Return the helper directory."""
        return self.__helper_directory

    def _validate_no_arguments(self, location: Location,
                               *args: typing.Any, **kwargs: typing.Any) -> None:
        self._validate_no_args(location, *args)
        self._validate_kwargs(location, (), **kwargs)

    def _validate_arguments_exact(self, location: Location, arg_count: int, message: str,
                                  *args: typing.Any, **kwargs: typing.Any) -> None:
        self._validate_args_exact(location, arg_count, message, *args)
        self._validate_kwargs(location, (), **kwargs)

    def _validate_arguments_at_least(self, location: Location, arg_count: int, message: str,
                                     *args: typing.Any, **kwargs: typing.Any) -> None:
        self._validate_args_at_least(location, arg_count, message, *args)
        self._validate_kwargs(location, (), **kwargs)

    def _validate_no_args(self, location: Location, *args: typing.Any) -> None:
        if args is list:
            trace('Validating arguments: "{}".'.format('", "'.join(str(args))))
        else:
            trace('Validating argument: "{}".'.format(args))
        self._validate_args_exact(location, 0,
                                  '"{}" does not take arguments.', *args)

    def _validate_args_exact(self, location: Location, arg_count: int,
                             message: str, *args: typing.Any) -> None:
        if args is list:
            trace('Validating arguments: "{}".'.format('", "'.join(str(args))))
        else:
            trace('Validating argument: "{}".'.format(args))
        if len(args) != arg_count:
            raise ParseError(message.format(self.name), location=location)

    def _validate_args_at_least(self, location: Location, arg_count: int,
                                message: str, *args: typing.Any) -> None:
        if args is list:
            trace('Validating arguments: "{}".'.format('", "'.join(str(args))))
        else:
            trace('Validating argument: "{}".'.format(args))
        if len(args) < arg_count:
            raise ParseError(message.format(self.name), location=location)

    def _validate_kwargs(self, location: Location, known_kwargs: typing.Tuple[str, ...],
                         **kwargs: typing.Any) -> None:
        trace('Validating keyword arguments: "{}"'
              .format('", "'.join(['{}={}'.format(k, str(kwargs[k]))
                                   for k in kwargs.keys()])))
        if not known_kwargs:
            if kwargs:
                raise ParseError('"{}" does not accept keyword arguments.'
                                 .format(self.name), location=location)
        else:
            for key, value in kwargs.items():
                if key not in known_kwargs:
                    raise ParseError('"{}" does not accept the keyword '
                                     'arguments "{}".'
                                     .format(self.name, key),
                                     location=location)

    def _require_kwargs(self, location: Location, required_kwargs: typing.Tuple[str, ...],
                        **kwargs: typing.Any) -> None:
        for key in required_kwargs:
            if key not in kwargs:
                raise ParseError('"{}" requires the keyword '
                                 'arguments "{}" to be passed.'
                                 .format(self.name, key),
                                 location=location)
