#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parse system definition files.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from . import exceptions

import importlib.util
import inspect
import os


class ExecObject:
    """Describe command in system definition file.

    Describe the command to execute later during generation phase.
    """

    def __init__(self, name, command, args):
        """Constructor."""
        self._name = name
        self._command = command
        self._args = args

    def execute(self):
        """Execute the command."""
        self._command.execute(*self._args)


class _ParserState:
    """Hold the state of the Parser."""

    def __init__(self):
        self._line_number = -1

        self._command = ''
        self._args = []
        self._multiline_start = ''


class Parser:
    """Parse a system definition file."""

    _commands = {}
    """A list of known commands."""

    @staticmethod
    def find_commands(ctx):
        """Find possible commands in the file system."""
        ctx.printer.trace('Checking for commands.')
        checked_dirs = []
        for path in (ctx.systemsCommandsDirectory(), ctx.commandsDirectory()):
            if path in checked_dirs:
                continue
            checked_dirs.append(path)
            ctx.printer.trace('Checking "{}" for command files.'.format(path))
            if not os.path.isdir(path):
                continue  # skip non-existing directories

            for f in os.listdir(path):
                if not f.endswith('.py'):
                    continue

                f_path = os.path.join(path, f)
                ctx.printer.trace('Found file: {}'.format(f_path))

                cmd = f[:-3]
                name = 'cr_cmd_' + cmd + '.py'

                spec = importlib.util.spec_from_file_location(name, f_path)
                cmd_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(cmd_module)

                def is_command(x):
                    return inspect.isclass(x) and \
                        x.__name__.endswith('Command') and \
                        x.__module__ == name
                klass = inspect.getmembers(cmd_module, is_command)
                instance = klass[0][1](ctx)
                Parser._commands[cmd] = (instance, f_path)

        ctx.printer.debug('Commands found:')
        for (name, value) in Parser._commands.items():
            path = value[1]
            location = '<GLOBAL>' if path.startswith(ctx.commandsDirectory()
                                                     + '/') else '<LOCAL>'
            ctx.printer.debug('  {}: {}'.format(name, location))

    def __init__(self, ctx):
        """Constructor."""
        self._ctx = ctx

    def parse(self, input_file):
        """Parse a file."""
        self._reset_parsing_state(self)

        with open(input_file, 'r') as f:
            yield self._parse_lines(f)

    def _parse_lines(self, iterable):
        """Parse an iterable of lines."""
        state = _ParserState()

        for line in iterable:
            print('>>>>', line)
            (state, obj) = self._parse_single_line(state, line)
            if obj:
                yield obj

        if state._multiline_start:
            raise exceptions.ParseError(state._line_number,
                                        'In multiline string at EOF.')

    def _parse_single_line(self, state, line):
        """Parse a single line."""
        state._line_number += 1

        if state._multiline_start:
            self._ctx.printer.trace('parsing "{}" (multiline continuation)'
                                    .format(line[:-1]))
            pass  # handle multi-line strings
        else:
            self._ctx.printer.trace('parsing "{}"'.format(line))
            (next_state, command, args) = self._extract_command(state, line)
            if command and next_state._multiline_start == '':
                obj = ExecObject(command, Parser._commands[command][0], args)
                return (next_state, obj)
            else:
                return (next_state, None)

    def _extract_command(self, state, line):
        """Extract the command from a line."""
        assert(state._multiline_start == '')
        assert(state._command == '')
        assert(len(state._args) == 0)

        token = ''
        pos = -1

        in_leading_space = True

        for c in line:
            pos += 1

            if c.isspace():
                if in_leading_space:
                    continue

                assert(token)
                (state, args) = self._extract_arguments(state, line[pos:])
                command = self._validate_command(state, token)

                if state._multiline_start:
                    state._command = command
                    state._args = args

                    return (state, None, None)
                return (state, command, args)

            in_leading_space = False

            if c == '#':
                self._ctx.printer.trace('    Comment')
                return (state, self._validate_command(state, token), None)

            if c.isalnum():
                token += c
                continue

            raise exceptions.ParseError(self._line_number,
                                        'Unexpected character \'{}\'.'
                                        .format(c))

        return (state, self._validate_command(state, token), None)

    def _validate_command(self, state, command):
        if not command:
            return None

        if command not in Parser._commands:
            self._ctx.printer.trace('Command "{}" not found.'.format(command))
            raise exceptions.ParseError(state._line_number,
                                        'Invalid command "{}"'.format(command))

        return command

    def _extract_arguments(self, state, line):
        return (state, line)
