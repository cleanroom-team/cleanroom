# -*- coding: utf-8 -*-
"""Manage the list of available commands.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from .command import Command, stringify
from .exceptions import PreflightError
from .location import Location
from .printer import debug, h2, success, trace
from .systemcontext import SystemContext

import importlib.util
import inspect
import os
import re
import typing


class CommandInfo(typing.NamedTuple):
    name: str
    syntax_string: str
    help_string: str
    file_name: str
    dependency_func: typing.Callable[
        [typing.Tuple[typing.Any, ...], typing.Dict[str, typing.Any]],
        typing.Optional[str],
    ]
    validate_func: typing.Callable[
        [Location, typing.Tuple[typing.Any, ...], typing.Dict[str, typing.Any],], None,
    ]
    execute_func: typing.Callable[
        [
            Location,
            SystemContext,
            typing.Tuple[typing.Any, ...],
            typing.Dict[str, typing.Any],
        ],
        None,
    ]
    register_substitutions: typing.Callable[
        [], typing.List[typing.Tuple[str, str, str]]
    ]


def _process_args(system_context: SystemContext, *args: typing.Any) -> typing.Any:
    return tuple(map(lambda a: system_context.expand(a), args))


def _process_kwargs(
    system_context: SystemContext, **kwargs: typing.Any
) -> typing.Dict[str, typing.Any]:
    return {k: system_context.expand(v) for k, v in kwargs.items()}


def call_command(
    location: Location,
    system_context: SystemContext,
    command: Command,
    *args: typing.Any,
    **kwargs: typing.Any
):
    _args = _process_args(system_context, *args)
    _kwargs = _process_kwargs(system_context, **kwargs)
    command(location, system_context, *_args, **_kwargs)


class CommandManager:
    """Manage the list of available commands."""

    def __init__(self, *command_directories: str, **services: typing.Any) -> None:
        self._commands: typing.Dict[str, CommandInfo] = {}
        self._search_directories = command_directories
        self._services_to_propagate = services
        self._services_to_propagate["command_manager"] = self
        self._find_commands(*command_directories)

    def print_commands(self) -> None:
        """Print a list of all known commands."""
        h2("Command List:")

        for key in sorted(self._commands.keys()):
            command_info = self.command(key)
            assert command_info
            long_help_lines = command_info.help_string.split("\n")
            print(
                "{}\n          {}\n\n          Definition in: {}\n\n".format(
                    command_info.syntax_string,
                    "\n          ".join(long_help_lines),
                    command_info.file_name,
                )
            )

    def _collect_substitutions(
        self,
    ) -> typing.List[typing.Tuple[str, str, str, typing.Tuple[str, ...]]]:
        result: typing.Dict[
            str, typing.Tuple[str, str, str, typing.Tuple[str, ...]]
        ] = {}

        for cmd in self._commands.keys():
            command_info = self.command(cmd)
            assert command_info

            name = command_info.name
            for (key, value, description) in command_info.register_substitutions():
                if not key in result:
                    result[key] = (key, value, description, (name,))
                else:
                    (old_key, old_value, old_description, old_names) = result[key]
                    assert (
                        old_key == key
                        and old_value == value
                        and old_description == description
                        and not name in old_names
                        and old_names
                    )
                    result[key] = (key, value, description, (*old_names, name))

        return [v for v in result.values()]

    def print_substitutions(self) -> None:
        h2("Predefined Substitutions:")
        print(
            "  BASE_SYSTEM_NAME, SYSTEM_NAME:\n    The names of the current system and its base system\n\n"
            "  BASE_SYSTEM_LIST:\n    Comma-separated list of all base systems\n\n"
            "  SCRATCH_DIR, ROOT_DIR, META_DIR, CACHE_DIR:\n    Directories used during system creation\n\n"
            "  SYSTEMS_DEFINITION_DIR:\n    The directory holding system definition files\n\n"
            "  SYSTEM_HELPER_DIR:\n    The directory containing files associated with the current system definition\n\n"
            "  TIMESTAMP:\n    The current timestamp\n\n"
        )

        h2("Command Substitutions:")
        self._known_substitutions: typing.List[typing.Tuple[str, str, str]] = []

        substitutions = self._collect_substitutions()
        substitutions.sort()
        for (key, value, description, name) in substitutions:
            print('  {} ("{}"): {}\n    {}\n'.format(key, value, name, description))

    def setup_substitutions(self, system_context: SystemContext):
        if system_context.base_context:
            debug(
                'System Context inherited, using substitutions from "{}".'.format(
                    system_context.base_context.system_name
                )
            )
            return

        pattern = re.compile("^[A-Za-z][A-Za-z0-9_]*$")

        substitutions = self._collect_substitutions()
        for (key, value, _, _) in substitutions:
            if not pattern.match(key):
                continue  # skip this key, but keep it in documentation!
            assert not system_context.has_substitution(key)
            debug(
                'Setting up system context: substitution "{}" = "{}".'.format(
                    key, value
                )
            )
            system_context.set_substitution(key, value)

    def preflight_check(self) -> None:
        if not self._search_directories:
            raise PreflightError("No directories to search for commands " "were given.")
        if not self._commands:
            raise PreflightError(
                'No commands were found in "{}".'.format(
                    '", "'.join(self._search_directories)
                )
            )

    def command(self, name: str) -> typing.Optional[CommandInfo]:
        return self._commands.get(name, None)

    def _add_command(self, name: str, file_name: str, command: typing.Any) -> None:
        def __validate_func(
            cmd: Command, location: Location, *args: typing.Any, **kwargs: typing.Any
        ) -> None:
            cmd_str = stringify(cmd.name, args, kwargs)
            trace("{} Validating {}.".format(location, cmd_str))
            command.validate(location, *args, **kwargs),
            success("{}: Validated {}.".format(location, cmd_str), verbosity=4)

        def __dependency_func(
            cmd: Command, *args: typing.Any, **kwargs: typing.Any
        ) -> typing.Optional[str]:
            cmd_str = stringify(cmd.name, args, kwargs)
            trace("Getting dependency of {}.".format(cmd_str))
            result = cmd.dependency(*args, **kwargs)
            success('Dependency of {} is "{}".'.format(cmd_str, result), verbosity=3)
            return result

        def __execute_func(
            cmd: Command,
            location: Location,
            system_context: SystemContext,
            *args: typing.Any,
            **kwargs: typing.Any
        ) -> None:
            cmd_str = stringify(cmd.name, args, kwargs)
            trace("{}: Executing {}.".format(location, cmd_str))
            call_command(location, system_context, cmd, *args, **kwargs)
            success("{}: Executed {}.".format(location, cmd_str), verbosity=2)

        self._commands[name] = CommandInfo(
            name=name,
            syntax_string=command.syntax_string,
            help_string=command.help_string,
            file_name=file_name,
            dependency_func=lambda *args, **kwargs: __dependency_func(
                command, *args, **kwargs
            ),
            validate_func=lambda loc, *args, **kwargs: __validate_func(
                command, loc, *args, **kwargs
            ),
            execute_func=lambda loc, sc, *args, **kwargs: __execute_func(
                command, loc, sc, *args, **kwargs
            ),
            register_substitutions=command.register_substitutions,
        )

    def _find_commands_in_directory(self, directory: str) -> None:
        for f in os.listdir(directory):
            if not f.endswith(".py"):
                continue

            command_file_name = os.path.join(directory, f)

            trace("Loading command from {}.".format(command_file_name))

            command_name = f[:-3]
            name = "cleanroom.commands." + command_name

            spec = importlib.util.spec_from_file_location(name, command_file_name)
            cmd_module = importlib.util.module_from_spec(spec)
            assert spec and spec.loader
            spec.loader.exec_module(cmd_module)

            def is_command(x: typing.Any) -> bool:
                return (
                    inspect.isclass(x)
                    and x.__name__.endswith("Command")
                    and x.__module__ == name
                )

            command_class = inspect.getmembers(cmd_module, is_command)
            instance = command_class[0][1](**self._services_to_propagate)
            self._add_command(command_name, command_file_name, instance)

    def _find_commands(self, *directories: str) -> None:
        """Find possible commands in the file system."""
        debug("Searching for available commands")
        visited_directories: typing.Set[str] = set()
        for directory in directories:
            if directory in visited_directories:
                continue
            visited_directories.add(directory)
            if not os.path.isdir(directory):
                continue  # skip non-existing directories

            self._find_commands_in_directory(directory)

        debug("Commands found:")
        for (command_name, command_info) in self._commands.items():
            path = command_info.file_name
            debug('  {}: "{}"'.format(command_name, path))
