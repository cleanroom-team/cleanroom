# -*- coding: utf-8 -*-
"""Manage the list of available commands.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from .command import Command
from .execobject import ExecObject

from ..location import Location
from ..printer import debug, h2

import importlib.util
import inspect
import os
import typing


class CommandManager:
    """Manage the list of available commands."""

    def __init__(self):
        self._commands: typing.Dict[str, typing.Tuple[Command, str]] = {}

    def _add_command(self, name: str, command: Command, file_name: str) -> None:
        self._commands[name] = (command, file_name)

    def find_commands(self, *directories: str) -> None:
        """Find possible commands in the file system."""
        h2('Searching for available commands', verbosity=2)
        checked_dirs: typing.List[str] = []
        for path in directories:
            if path in checked_dirs:
                continue
            checked_dirs.append(path)
            if not os.path.isdir(path):
                continue  # skip non-existing directories

            for f in os.listdir(path):
                if not f.endswith('.py'):
                    continue

                f_path = os.path.join(path, f)

                cmd = f[:-3]
                name = 'cleanroom.generator.commands.' + cmd

                spec = importlib.util.spec_from_file_location(name, f_path)
                cmd_module = importlib.util.module_from_spec(spec)
                assert spec and spec.loader
                spec.loader.exec_module(cmd_module)

                def is_command(x):
                    return inspect.isclass(x) and \
                        x.__name__.endswith('Command') and \
                        x.__module__ == name
                klass = inspect.getmembers(cmd_module, is_command)
                instance = klass[0][1]()
                self._add_command(cmd, instance, f_path)

        debug('Commands found:')
        for (name, value) in self._commands.items():
            path = value[1]
            debug('  {}: "{}"'.format(name, path))

    def list_commands(self) -> None:
        """Print a list of all known commands."""
        h2('Command List:')

        for key in sorted(self._commands):
            cmd, path = self._commands[key]

            long_help_lines = cmd.help().split('\n')
            print('{}\n          {}\n\n          Definition in: {}\n\n'
                  .format(cmd.syntax(), '\n          '.join(long_help_lines),
                          path))

    def command(self, name: str) -> typing.Optional[Command]:
        """Retrieve a command."""
        return self._commands.get(name, (None, None))[0]

    def command_file(self, name: str) -> typing.Optional[str]:
        """Retrieve the file containing a command."""
        return self._commands.get(name, (None, None))[1]

