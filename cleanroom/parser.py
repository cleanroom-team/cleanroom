#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parse system definition files.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from . import exceptions as ex
from . import execobject

import importlib.util
import inspect
import os
import re


class _ParserState:
    """Hold the state of the Parser."""

    def __init__(self, file_name):
        self._file_name = file_name
        self._line_number = 0
        self._to_process = ''

        self._indent_depth = 0

        self.reset()

    def is_token_complete(self):
        return self._incomplete_token == ''

    def is_command_continuation(self):
        if self._to_process == '' or self._to_process == '\n':
            return True

        return self._indent_depth > 0 \
            and self._to_process.startswith(' ' * self._indent_depth)

    def is_line_done(self):
        return self._to_process == ''

    def reset(self):
        assert(self._line_number >= 0)

        self._command = ''
        self._args = ()
        self._kwargs = {}

        self._incomplete_token = ''

        self._indent_depth = 0

        assert(self.is_token_complete())

    def create_execute_object(self):
        if self._command == '':
            return None

        command = self._command
        args = self._args
        kwargs = self._kwargs
        file_name = self._file_name
        line_number = self._line_number

        self.reset()

        command_object = Parser._commands[command][0]
        dependency = command_object.validate_arguments(file_name,
                                                       line_number,
                                                       *args, *kwargs)

        return execobject.ExecObject((file_name, line_number), command,
                                     dependency, command_object, *args,
                                     *kwargs)

    def __str__(self):
        dump1 = self._to_process.replace('\n', '\\n').replace('\t', '\\t')
        dump2 = self._incomplete_token.replace('\n', '\\n')\
            .replace('\t', '\\t')

        return '{}-\"{}\" ({})-tc:{}-ld:{}-"{}"-token:"{}".'.\
               format(self._line_number, self._command,
                      ','.join(self._args), self.is_token_complete(),
                      self.is_line_done(), dump1, dump2)


class Parser:
    """Parse a system definition file."""

    _commands = {}
    """A list of known commands."""

    @staticmethod
    def find_commands(ctx):
        """Find possible commands in the file system."""
        ctx.printer.trace('Checking for commands.')
        checked_dirs = []
        for path in (ctx.systems_commands_directory(),
                     ctx.commands_directory()):
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
                instance = klass[0][1]()
                Parser._commands[cmd] = (instance, f_path)

        ctx.printer.debug('Commands found:')
        for (name, value) in Parser._commands.items():
            path = value[1]
            location = '<GLOBAL>' if path.startswith(ctx.commands_directory()
                                                     + '/') else '<LOCAL>'
            ctx.printer.debug('  {}: {}'.format(name, location))

    @staticmethod
    def list_commands(ctx):
        """Print a list of all known commands."""
        ctx.printer.h1('Command List:')

        for key in sorted(Parser._commands):
            cmd, path = Parser._commands[key]

            long_help_lines = cmd.help().split('\n')
            ctx.printer.print('{}\n          {}\n\n          '
                              'Definition in: {}\n\n'
                              .format(cmd.syntax(),
                                      '\n          '.join(long_help_lines),
                                      path))

    def __init__(self, ctx):
        """Constructor."""
        self._ctx = ctx

    def parse(self, input_file):
        """Parse a file."""
        with open(input_file, 'r') as f:
            for result in self._parse_lines(f, input_file):
                yield result

    def _parse_lines(self, iterable, file_name):
        """Parse an iterable of lines."""
        state = _ParserState(file_name)

        built_in = ('<BUILT_IN>', 1)

        yield execobject.ExecObject(built_in, '_setup', None,
                                    Parser._commands['_setup'][0])

        for line in iterable:
            state._to_process += line
            state._line_number += 1

            (state, obj) = self._parse_single_line(state)
            if obj:
                yield obj

            if not state.is_line_done():
                raise ex.ParseError(state._file_name, state._line_number,
                                    'Unexpected tokens "{}" found.'
                                    .format(state._to_process))

            self._ctx.printer.info('  <EOL> ({}).'.format(state))

        if not state.is_token_complete():
            raise ex.ParseError(state._file_name, state._line_number,
                                'Unexpected EOF.')

        # Flush last exec object:
        obj = state.create_execute_object()
        if obj:
            yield obj

        yield execobject.ExecObject(built_in, '_teardown', None,
                                    Parser._commands['_teardown'][0])

    def _parse_single_line(self, state):
        """Parse a single line."""
        self._ctx.printer.info('Parsing line ({}).'.format(state))

        exec_object = None

        if state.is_token_complete() and not state.is_command_continuation():
            self._ctx.printer.trace('  Part of a new command ({}).'
                                    .format(state))
            exec_object = state.create_execute_object()
            state = self._extract_command(state)
        else:
            if state.is_token_complete():
                state._to_process = state._to_process[state._indent_depth:]
                self._ctx.printer.trace('  Continuation of command ({}).'
                                        .format(state))
                state = self._extract_arguments(state)
            else:
                self._ctx.printer.trace('  Continuation of argument ({}).'
                                        .format(state))
                state = self._extract_multiline_argument(state)

        return (self._extract_arguments(state), exec_object)

    def _strip_comment_and_ws(self, state):
        """Extract a comment up to the end of the line."""
        input = state._to_process
        line = input.lstrip()
        if line == '' or line.startswith('#'):
            state._to_process = ''
        else:
            state._to_process = line

        # Only report if there are changes:
        if input != state._to_process:
            self._ctx.printer.trace('      Stripped WS and comments ({}).'
                                    .format(state))

        return state

    def _extract_command(self, state):
        """Extract the command from a line."""
        assert(state._command == '')
        assert(state._indent_depth == 0)
        assert(state._args == ())
        assert(state._kwargs == {})

        indent_depth = \
            len(state._to_process) - len(state._to_process.lstrip(' ')) + 4

        state = self._strip_comment_and_ws(state)
        if state.is_line_done():
            return state

        state._indent_depth = indent_depth

        line = state._to_process.lstrip()
        pos = 0
        command = ''

        for c in line:
            if c.isspace() or c == '#':
                break

            pos += 1
            command += c

        state._command = self._validate_command(state, command)
        state._to_process = line[pos:]

        self._ctx.printer.trace('      Command found ({}).'.format(state))

        return state

    def _extract_arguments(self, state):
        # extract arguments:
        while not state.is_line_done():
            state = self._extract_next_argument(state)

        return state

    def _validate_command(self, state, command):
        self._ctx.printer.trace('      Validating command "{}".'
                                .format(command))
        if not command:
            raise ex.ParseError(state._file_name, state._line_number,
                                'Empty command found.')

        command_pattern = re.compile("^[A-Za-z][A-Za-z0-9_-]*$")
        if not command_pattern.match(command):
            raise ex.ParseError(state._file_name, state._line_number,
                                'Invalid command "{}".'.format(command))

        if command not in Parser._commands:
            raise ex.ParseError(state._file_name, state._line_number,
                                'Command "{}" not found.'.format(command))

        self._ctx.printer.info('    Command is "{}".'.format(command))

        return command

    def _extract_next_argument(self, state):
        state = self._strip_comment_and_ws(state)
        if state.is_line_done():
            return state

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

        self._ctx.printer.trace('      Extracting multiline ({}).'
                                .format(state))

        end_pos = line.find('>>>>')
        if end_pos >= 0:
            arg = state._incomplete_token + line[:end_pos]

            state._incomplete_token = ''
            state._args = (*state._args, arg)
            state._to_process = line[end_pos + 4:]

            self._ctx.printer.info('    multi-line Arg ({}).'
                                   .format(state))
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

                raise ex.ParseError(state._file_name, state._line_number,
                                    'Invalid escape sequence "\{}" in string.'
                                    .format(c))

            if c == '\\':
                must_escape = True
                continue

            if c == quote:
                state._to_process = line[pos + 1:]
                state._args = (*state._args, arg)
                self._ctx.printer.info('    string Arg ({}).'.format(state))
                return state

            arg += c

        raise ex.ParseError(state._file_name, state._line_number,
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

                raise ex.ParseError(state._file_name, state._line_number,
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
        state._args = (*state._args, arg)
        self._ctx.printer.info('    normal Arg ({}).'.format(state))
        return state
