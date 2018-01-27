#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parse system definition files.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from . import exceptions as ex

import importlib.util
import inspect
import os
import re


class ExecObject:
    """Describe command in system definition file.

    Describe the command to execute later during generation phase.
    """

    def __init__(self, name, dependency, command, args):
        """Constructor."""
        self._name = name
        self._command = command
        self._args = args
        self._dependency = dependency

    def dependency(self):
        """Return dependency of the system (or None)."""
        return self._dependency

    def execute(self):
        """Execute the command."""
        self._command.execute(*self._args)


class _ParserState:
    """Hold the state of the Parser."""

    def __init__(self):
        self._line_number = 0
        self._to_process = ''

        self.reset()

    def is_command_complete(self):
        return self._incomplete_token == ''

    def is_line_done(self):
        return self._to_process == ''

    def reset(self):
        assert(self._line_number >= 0)
        assert(self._to_process == '')

        self._command = ''
        self._args = []

        self._incomplete_token = ''
        self._to_process = ''

        assert(self.is_command_complete())
        assert(self.is_line_done())

    def __str__(self):
        dump = self._to_process.replace('\n', '\\n').replace('\t', '\\t')

        return '{}-\"{}\" ({})-cc:{}-ld:{}-"{}".'.\
               format(self._line_number, self._command,
                      ','.join(self._args), self.is_command_complete(),
                      self.is_line_done(), dump)


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

    def _object_from_state(self, state):
        if state.is_line_done() \
           and state.is_command_complete() \
           and state._command:
            self._ctx.printer.debug('Creating Exec Object ({}).'.format(state))
            command = state._command
            args = state._args
            state.reset()

            command_object = Parser._commands[command][0]
            dependency = command_object.validate_arguments(state._line_number,
                                                           args)

            return (state, ExecObject(command, dependency,
                                      command_object, tuple(args)))

        return (state, None)

    def parse(self, input_file):
        """Parse a file."""
        self._reset_parsing_state(self)

        with open(input_file, 'r') as f:
            yield self._parse_lines(f)

    def _parse_lines(self, iterable):
        """Parse an iterable of lines."""
        state = _ParserState()

        for line in iterable:
            state._to_process += line
            state._line_number += 1

            next_state = self._parse_single_line(state)
            (state, obj) = self._object_from_state(next_state)

            if obj:
                yield obj

            if not state.is_line_done():
                raise ex.ParseError(state._line_number,
                                    'Unexpected tokens "{}" found.'
                                    .format(state._to_process))

        if not state.is_line_done() \
           or not state.is_command_complete():
            raise ex.ParseError(state._line_number, 'Unexpected EOF.')

        return None

    def _parse_single_line(self, state):
        """Parse a single line."""
        self._ctx.printer.trace('Parsing single line ({}).'.format(state))

        if state.is_command_complete():
            self._ctx.printer.trace('Part of a new command ({}).'
                                    .format(state))
            state = self._extract_command(state)
        else:
            self._ctx.printer.trace('Continuation of earlier command ({}).'
                                    .format(state))
            state = self._extract_multiline_argument(state)

        return self._extract_arguments(state)

    def _strip_comment_and_ws(self, state):
        """Extract a comment up to the end of the line."""
        line = state._to_process.lstrip()
        if line == '' or line.startswith('#'):
            state._to_process = ''
        else:
            state._to_process = line
        self._ctx.printer.trace('Stripped WS and comments ({}).'.format(state))
        return state

    def _extract_command(self, state):
        """Extract the command from a line."""
        assert(state._command == '')
        assert(state._args == [])

        state = self._strip_comment_and_ws(state)
        if state.is_line_done():
            return state

        line = state._to_process.lstrip()
        pos = 0
        command = ''

        self._ctx.printer.trace('Extracting command ({}).'.format(state))

        for c in line:
            if c.isspace() or c == '#':
                break

            pos += 1
            command += c

        state._command = self._validate_command(state, command)
        state._to_process = line[pos:]

        self._ctx.printer.debug('Command found ({}).'.format(state))

        return state

    def _extract_arguments(self, state):
        # extract arguments:
        while not state.is_line_done():
            state = self._extract_next_argument(state)

        self._ctx.printer.debug('<EOL> ({}).'.format(state))

        return state

    def _validate_command(self, state, command):
        self._ctx.printer.trace('Validating command "{}".'.format(command))
        if not command:
            self._ctx.printer.trace('Empty command found.')
            raise ex.ParseError(state._line_number, 'Empty command found.')

        command_pattern = re.compile("^[A-Za-z][A-Za-z0-9]*$")
        if not command_pattern.match(command):
            self._ctx.printer.trace('Invalid command "{}".'.format(command))
            raise ex.ParseError(state._line_number,
                                'Invalid command "{}".'.format(command))

        if command not in Parser._commands:
            self._ctx.printer.trace('Command "{}" not found.'.format(command))
            raise ex.ParseError(state._line_number,
                                'Command "{}" not found.'.format(command))

        return command

    def _extract_next_argument(self, state):
        state = self._strip_comment_and_ws(state)
        if state.is_line_done():
            return state

        self._ctx.printer.trace('Extracting argument ({}).'.format(state))

        line = state._to_process

        if line.startswith('<<<<'):
            state._to_process = line[4:]
            return self._extract_multiline_argument(state)

        if line[0] == '"' or line[0] == '\'':
            state._to_process = line[1:]
            return self._extract_string_argument(state, line[0])

        state._to_process = line
        return self._extract_normal_argument(state)

    def _extract_multiline_argument(self, state):
        line = state._to_process

        self._ctx.printer.trace('Extracting multiline ({}).'.format(state))

        end_pos = line.find('>>>>')
        if end_pos >= 0:
            arg = state._incomplete_token + line[:end_pos]

            state._incomplete_token = ''
            state._args.append(arg)
            state._to_process = line[end_pos + 4:]

            self._ctx.printer.debug('  ML Arg ({}).'.format(state))
        else:
            state._incomplete_token += line
            state._to_process = ''

        return state

    def _extract_string_argument(self, state, quote):
        must_escape = False
        line = state._to_process
        pos = -1
        arg = ''

        for c in line:
            pos += 1

            if must_escape:
                must_escape = False
                if c == '\'' or c == quote:
                    arg += c
                    continue

                raise ex.ParseError(state._line_number,
                                    'Invalid escape sequence "\{}" in string.'
                                    .format(c))

            if c == '\\':
                must_escape = True
                continue

            if c == quote:
                state._to_process = line[pos + 1:]
                state._args.append(arg)
                return state

            arg += c

        raise ex.ParseError(state._line_number,
                            'Missing closing "{}" quote.'.format(quote))

    def _extract_normal_argument(self, state):
        must_escape = False
        line = state._to_process
        pos = -1
        arg = ''

        for c in line:
            pos += 1

            if must_escape:
                must_escape = False
                if c == ' ' or c == '\\':
                    arg += c
                    continue

                raise ex.ParseError(state._line_number,
                                    'Invalid escape sequence "\{}" '
                                    'in argument.'.format(c))

            if c == '\\':
                must_escape = True
                continue

            if c.isspace() or c == '#':
                # end of argument...
                break

            arg += c

        state._to_process = line[pos + 1:]
        assert(arg != '')
        self._ctx.printer.debug('  Arg ({}).'.format(state))
        state._args.append(arg)
        return state
