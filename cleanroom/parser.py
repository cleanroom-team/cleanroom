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
        self._key_for_value = ''

        self._indent_depth = 0

        self.reset()

    def is_token_complete(self):
        return self._incomplete_token == ''

    def is_command_continuation(self):
        if self._to_process == '' or self._to_process == '\n':
            return True

        return self._indent_depth > 0 \
            and self._to_process.startswith(' ' * self._indent_depth)

    def reset(self):
        assert(self._line_number >= 0)

        self._command = ''
        self._args = ()
        self._kwargs = {}

        self._key_for_value = ''
        self._incomplete_token = ''

        self._indent_depth = 0

        assert(self.is_token_complete())

    def create_execute_object(self):
        if self._command == '':
            return None

        command = self._command
        args = self._args
        kwargs = self._kwargs
        if self._key_for_value:
            kwargs[self._key_for_value] = ''

        file_name = self._file_name
        line_number = self._line_number

        self.reset()

        return Parser.create_execute_object(file_name, line_number,
                                            command, *args, **kwargs)

    def __str__(self):
        dump1 = ','.join(self._args) + ':'
        dump1 += ','.join([k + '=' + v for (k, v) in self._kwargs.items()])
        dump1 = dump1.replace('\n', '\\n').replace('\t', '\\t')
        dump2 = self._to_process.replace('\n', '\\n').replace('\t', '\\t')
        dump3 = self._incomplete_token.replace('\n', '\\n')\
            .replace('\t', '\\t')

        return '{}-\"{}\" ({})-tc:{}-"{}"-token:"{}".'.\
               format(self._line_number, self._command, dump1,
                      self.is_token_complete(), dump2, dump3)


class Parser:
    """Parse a system definition file."""

    _commands = {}
    """A list of known commands."""

    @staticmethod
    def find_commands(ctx):
        """Find possible commands in the file system."""
        ctx.printer.h2('Searching for available commands', verbosity=2)
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
                name = 'cleanroom.commands.' + cmd

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
        ctx.printer.h2('Command List:')

        for key in sorted(Parser._commands):
            cmd, path = Parser._commands[key]

            long_help_lines = cmd.help().split('\n')
            print('{}\n          {}\n\n          Definition in: {}\n\n'
                  .format(cmd.syntax(), '\n          '.join(long_help_lines),
                          path))

    @staticmethod
    def command(name):
        """Retrieve a command."""
        return Parser._commands[name][0]

    @staticmethod
    def command_file(name):
        """Retrieve the file containing a command."""
        return Parser._commands[name][1]

    @staticmethod
    def create_execute_object(file_name, line_number,
                              command, *args, message=None, **kwargs):
        """Create an execute object based on command and arguments."""
        if message is None:
            message = command

        command_object = Parser.command(command)
        dependency = command_object.validate_arguments(file_name,
                                                       line_number,
                                                       *args, **kwargs)

        return execobject.ExecObject((file_name, line_number), message,
                                     dependency, command_object, *args,
                                     **kwargs)

    def __init__(self, ctx):
        """Constructor."""
        self._ctx = ctx
        self._command_pattern = re.compile("^[A-Za-z][A-Za-z0-9_-]*$")

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
                                    Parser.command('_setup'))

        for line in iterable:
            state._to_process += line
            state._line_number += 1

            (state, obj) = self._parse_single_line(state)
            if obj:
                yield obj

            if state._to_process != '':
                raise ex.ParseError('Unexpected tokens "{}" found.'
                                    .format(state._to_process),
                                    file_name=state._file_name,
                                    line_number=state._line_number)

            self._ctx.printer.info('  <EOL> ({}).'.format(state))

        if not state.is_token_complete():
            raise ex.ParseError('Unexpected EOF.',
                                file_name=state._file_name,
                                line_number=state._line_number)

        # Flush last exec object:
        obj = state.create_execute_object()
        if obj:
            yield obj

        yield execobject.ExecObject(built_in, '_teardown', None,
                                    Parser.command('_teardown'))

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
            else:
                self._ctx.printer.trace('  Continuation of argument ({}).'
                                        .format(state))
                state = self._extract_multiline_argument(state)

        return (self._extract_arguments(state), exec_object)

    def _strip_comment_and_ws(self, line):
        """Extract a comment up to the end of the line."""
        input = line
        line = input.lstrip()
        if line == '\n' or line == '' or line.startswith('#'):
            line = ''

        # Only report if there are changes:
        if input != line:
            self._ctx.printer.trace('      Stripped WS and comments ({}).'
                                    .format(line
                                            .replace('\n', '\\n')
                                            .replace('\t', '\\t')))

        return line

    def _extract_command(self, state):
        """Extract the command from a line."""
        assert(state._command == '')
        assert(state._indent_depth == 0)
        assert(state._args == ())
        assert(state._kwargs == {})

        indent_depth = \
            len(state._to_process) - len(state._to_process.lstrip(' ')) + 4

        state._to_process = self._strip_comment_and_ws(state._to_process)
        if state._to_process == '':
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
        while state._to_process != '':
            (key, value, token, to_process, need_arg_value) \
                = self._parse_next_argument(state._file_name,
                                            state._line_number,
                                            state._to_process,
                                            state._incomplete_token, True)

            state._incomplete_token = token
            state._to_process = to_process

            if key is not None:
                if need_arg_value:
                    if not self._command_pattern.match(key):
                        raise ex.ParseError('"{}" is not a valid keyword '
                                            'argument.'.format(key),
                                            file_name=state._file_name,
                                            line_number=state._line_number)
                    if value is not None:
                        state._kwargs[key] = value
                        state._key_for_value = ''
                    else:
                        state._key_for_value = key
                else:
                    state._args = (*state._args, key)

        return state

    def _validate_command(self, state, command):
        self._ctx.printer.trace('      Validating command "{}".'
                                .format(command))
        if not command:
            raise ex.ParseError('Empty command found.',
                                file_name=state._file_name,
                                line_number=state._line_number)

        if not self._command_pattern.match(command):
            raise ex.ParseError('Invalid command "{}".'.format(command),
                                file_name=state._file_name,
                                line_number=state._line_number)

        if command not in Parser._commands:
            raise ex.ParseError('Command "{}" not found.'.format(command),
                                file_name=state._file_name,
                                line_number=state._line_number)

        self._ctx.printer.info('    Command is "{}".'.format(command))

        return command

    def _parse_next_argument(self, file_name, line_number, line, token,
                             is_keyword_possible=True):
        to_process = self._strip_comment_and_ws(line)
        if to_process == '':
            return (None, None, '', '', False)  # return what

        if to_process.startswith('<<<<'):
            to_process = to_process[4:]
            (value, token, to_process) \
                = self._parse_multiline_argument(file_name, line_number,
                                                 to_process, token)
            return (value, None, token, to_process, False)
        if to_process[0] == '"' or to_process[0] == '\'':
            quote = to_process[0]
            to_process = to_process[1:]
            (value, to_process) \
                = self._parse_string_argument(file_name, line_number,
                                              to_process, quote)
            return (value, None, '', to_process, False)

        (key_or_value, to_process, need_arg_value) \
            = self._parse_normal_argument(file_name, line_number,
                                          to_process, is_keyword_possible)

        value = None
        if need_arg_value:
            (value, token, to_process) \
                = self._parse_next_argument_value(file_name, line_number,
                                                  to_process, token)

        return (key_or_value, value, token, to_process, need_arg_value)

    def _parse_next_argument_value(self, file_name, line_number, line, token):
        (value, unused, token, to_process, need_arg_value) \
            = self._parse_next_argument(file_name, line_number, line, token,
                                        is_keyword_possible=False)

        assert(unused is None)
        assert(not need_arg_value)

        return (value, token, to_process)

    def _extract_multiline_argument(self, state):
        (value, token, to_process) \
            = self._parse_multiline_argument(state._file_name,
                                             state._line_number,
                                             state._to_process,
                                             state._incomplete_token)
        state._to_process = to_process
        state._incomplete_token = token
        if token == '':
            if state._key_for_value:
                state._kwargs[state._key_for_value] = value
                state._key_for_value = ''
            else:
                state._args = (*state._args, value)

        self._ctx.printer.trace('      Extracting multiline ({}).'
                                .format(state))

        return state

    def _parse_multiline_argument(self, file_name, line_number, line, token):
        value = None
        to_process = ''

        end_pos = line.find('>>>>')

        if end_pos >= 0:
            value = token + line[:end_pos]
            token = ''
            to_process = line[end_pos + 4:]
        else:
            token += line
        return (value, token, to_process)

    def _parse_string_argument(self, file_name, line_number, line, quote):
        must_escape = False
        pos = -1
        value = ''

        for c in line:
            pos += 1

            if must_escape:
                must_escape = False
                if c == '\\' or c == quote:
                    value += c
                    continue

                raise ex.ParseError('Invalid escape sequence "\{}" in string.'
                                    .format(c), file_name=file_name,
                                    line_number=line_number)

            if c == '\\':
                must_escape = True
                continue

            if c == quote:
                return (value, line[pos + 1:])

            value += c

        raise ex.ParseError('Missing closing "{}" quote.'.format(quote),
                            file_name=file_name, line_number=line_number)

    def _parse_normal_argument(self, file_name, line_number, line,
                               is_keyword_possible=True):
        must_escape = False
        pos = -1
        value = ''
        need_arg_value = False

        for c in line:
            pos += 1

            if must_escape:
                must_escape = False
                if c == ' ' or c == '\\':
                    value += c
                    continue

                raise ex.ParseError('Invalid escape sequence "\{}" '
                                    'in argument.'.format(c),
                                    file_name=file_name,
                                    line_number=line_number)

            if c == '\\':
                must_escape = True
                continue

            if c == '=' and is_keyword_possible:
                # end of argument, start of value...
                need_arg_value = True
                break

            if c.isspace() or c == '#':
                # end of argument...
                break

            value += c

        return (value, line[pos + 1:], need_arg_value)
