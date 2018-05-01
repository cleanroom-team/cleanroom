# -*- coding: utf-8 -*-
"""Parse system definition files.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.exceptions as ex
import cleanroom.execobject as execobject
import cleanroom.location as loc
import cleanroom.printer as printer

import importlib.util
import inspect
import os
import re


class _ParserState:
    """Hold the state of the Parser."""

    def __init__(self, file_name):
        self._current_file_name = file_name
        self._current_line = 1
        self._start_line = 0
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

    def record_command_start(self):
        self._start_line = self._current_line

    def next_line(self):
        self._current_line += 1

    def current_location(self):
        return loc.Location(file_name=self._current_file_name,
                            line_number=self._current_line)

    def start_location(self):
        if self._start_line < 1:
            return None
        return loc.Location(file_name=self._current_file_name,
                            line_number=self._start_line)

    def reset(self):
        self._args = ()
        self._kwargs = {}

        self._key_for_value = ''
        self._incomplete_token = ''

        self._indent_depth = 0

        assert(self.is_token_complete())

    def create_execute_object(self):
        if not self._args or self._start_line == 0:
            return None

        args = self._args
        kwargs = self._kwargs
        if self._key_for_value:
            kwargs[self._key_for_value] = ''

        self.reset()

        return Parser.create_execute_object(self.start_location(),
                                            *args, **kwargs)

    def _args_to_string(self):
        args = ','.join([str(a) for a in self._args]) + ':' \
            + ','.join([k + '=' + str(v) for (k, v) in self._kwargs.items()])
        return args.replace('\n', '\\n').replace('\t', '\\t')

    def _to_process_to_string(self):
        return self._to_process.replace('\n', '\\n').replace('\t', '\\t')

    def _incomplete_token_to_string(self):
        return self._incomplete_token.replace('\n', '\\n').replace('\t', '\\t')

    def __str__(self):
        return '{}(start at:{}) "{}" ({})-token:"{}", complete?"{}"-key:"{}"'.\
               format(self.current_location(),
                      self._start_line,
                      self._args_to_string(),
                      self._to_process_to_string(),
                      self._incomplete_token_to_string(),
                      self.is_token_complete(),
                      self._key_for_value)


class Parser:
    """Parse a system definition file."""

    _commands = {}
    """A list of known commands."""

    @staticmethod
    def find_commands(*directories):
        """Find possible commands in the file system."""
        printer.h2('Searching for available commands', verbosity=2)
        checked_dirs = []
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

        printer.debug('Commands found:')
        for (name, value) in Parser._commands.items():
            path = value[1]
            printer.debug('  {}: "{}"'.format(name, path))

    @staticmethod
    def list_commands(ctx):
        """Print a list of all known commands."""
        printer.h2('Command List:')

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
    def create_execute_object(location, *args, **kwargs):
        """Create an execute object based on command and arguments."""
        if not args:
            return None

        if not location.extra_information:
            location.extra_information = args[0]

        obj = execobject.ExecObject(location, None, *args, **kwargs)
        obj.set_dependency(_validate_exec_object(location, obj))

        return obj

    def __init__(self):
        """Constructor."""
        self._command_pattern = re.compile('^[A-Za-z][A-Za-z0-9_-]*$')
        self._octal_pattern = re.compile('^0o?([0-7]+)$')
        self._hex_pattern = re.compile('^0x([0-9a-fA-F]+)$')

    def parse(self, input_file):
        """Parse a file."""
        with open(input_file, 'r') as f:
            for result in self._parse_lines(f, input_file):
                yield result

    def _parse_lines(self, iterable, file_name):
        """Parse an iterable of lines."""
        state = _ParserState(file_name)
        built_in = loc.Location(file_name='<BUILT_IN>', line_number=1)

        yield execobject.ExecObject(built_in, None, '_setup')

        for line in iterable:
            state._to_process += line

            (state, obj) = self._parse_single_line(state)
            if obj:
                yield obj

            if state._to_process != '':
                raise ex.ParseError('Unexpected tokens "{}" found.'
                                    .format(state._to_process),
                                    location=state.current_location())

            state.next_line()

        if not state.is_token_complete():
            raise ex.ParseError('Unexpected EOF.',
                                location=state.current_location())

        # Flush last exec object:
        obj = state.create_execute_object()
        if obj:
            yield obj

        yield execobject.ExecObject(built_in, None, '_teardown')

    def _parse_single_line(self, state):
        """Parse a single line."""
        exec_object = None

        if state.is_token_complete() and not state.is_command_continuation():
            exec_object = state.create_execute_object()
            state.record_command_start()
            state = self._extract_command(state)
        else:
            if state.is_token_complete():
                state._to_process = state._to_process[state._indent_depth:]
            else:
                state = self._extract_multiline_argument(state)

        return (self._extract_arguments(state), exec_object)

    def _strip_comment_and_ws(self, line):
        """Extract a comment up to the end of the line."""
        input = line
        line = input.lstrip()
        if line == '\n' or line == '' or line.startswith('#'):
            line = ''

        return line

    def _extract_command(self, state):
        """Extract the command from a line."""
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

        state._args = (self._validate_command(state, command),)
        state._to_process = line[pos:]

        return state

    def _extract_arguments(self, state):
        # extract arguments:
        while state._to_process != '':
            (key, has_value, value, to_process, token) \
                = self._parse_next_argument(state.start_location(),
                                            state._to_process,
                                            state._incomplete_token)

            state._to_process = to_process
            state._incomplete_token = token

            if key is not None:
                if has_value:
                    state._kwargs[key] = value
                    state._key_for_value = ''
                else:
                    state._key_for_value = key
            else:
                if has_value:
                    state._args = (*state._args, value)

        return state

    def _validate_command(self, state, command):
        if not command:
            raise ex.ParseError('Empty command found.',
                                location=state.start_location())

        if not self._command_pattern.match(command):
            raise ex.ParseError('Invalid command "{}".'.format(command),
                                location=state.start_location())

        if command not in Parser._commands:
            raise ex.ParseError('Command "{}" not found.'.format(command),
                                location=state.start_location())

        return command

    def _parse_next_argument(self, location, to_process, token):
        key = None
        has_value = False
        value = None
        to_process = self._strip_comment_and_ws(to_process)
        # token

        (has_part, section, is_keyword, to_process, token) \
            = self._parse_argument_part(location, to_process, token,
                                        is_keyword_possible=True)
        if not has_part:
            return (key, has_value, value, to_process, token)

        if is_keyword:
            key = section
            if not self._command_pattern.match(key):
                raise ex.ParseError('Keyword "{}" is not valid.'.format(key),
                                    location=location)

            (has_part, section, is_keyword, to_process, token) \
                = self._parse_argument_part(location, to_process, token,
                                            is_keyword_possible=False)

            value = section
            has_value = has_part

            if not has_value and not token:
                raise ex.ParseError('Keyword without a value found.',
                                    location=location)
            assert(not is_keyword)
        else:
            value = section
            has_value = True

        return (key, has_value, value, to_process, token)

    def _parse_argument_part(self, location, to_process, token, *,
                             is_keyword_possible=False):
        has_part = False
        section = None
        is_keyword = False
        to_process = self._strip_comment_and_ws(to_process)
        # token
        if to_process != '':
            if to_process.startswith('<<<<'):
                (section, to_process, token) \
                    = self._parse_multiline_argument(location, to_process[4:],
                                                     token)
                has_part = not token
            elif to_process[0] == '"' or to_process[0] == '\'':
                has_part = True
                assert(not token)
                (section, to_process) \
                    = self._parse_string_argument(location, to_process[1:],
                                                  to_process[0])
            else:
                has_part = True
                assert(not token)
                # Either a key-value pair or a simple value.
                (section, to_process, is_keyword) \
                    = self._parse_normal_argument(location, to_process,
                                                  is_keyword_possible)
                if not is_keyword:
                    section = self._process_value(section)

        return (has_part, section, is_keyword, to_process, token)

    def _process_value(self, value):
        if value is None:
            return None

        octal_match = self._octal_pattern.match(value)
        hex_match = self._hex_pattern.match(value)
        if value == 'None':
            value = None
        elif value == 'True':
            value = True
        elif value == 'False':
            value = False
        elif octal_match:
            value = int(octal_match.group(1), 8)
        elif hex_match:
            value = int(hex_match.group(1), 16)
        elif value.isdigit():
            value = int(value)
        return value

    def _extract_multiline_argument(self, state):
        (value, to_process, token) \
            = self._parse_multiline_argument(state.start_location(),
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

        return state

    def _parse_multiline_argument(self, location, to_process, token):
        value = None

        end_pos = to_process.find('>>>>')

        if end_pos >= 0:
            value = token + to_process[:end_pos]
            token = ''
            to_process = to_process[end_pos + 4:]
        else:
            token += to_process
            to_process = ''
        return (value, to_process, token)

    def _parse_string_argument(self, location, line, quote):
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
                                    .format(c), location=location)

            if c == '\\':
                must_escape = True
                continue

            if c == quote:
                return (value, line[pos + 1:])

            value += c

        raise ex.ParseError('Missing closing "{}" quote.'.format(quote),
                            location=location)

    def _parse_normal_argument(self, location, line,
                               is_keyword_possible=True):
        must_escape = False
        pos = -1
        value = ''
        is_keyword = False

        for c in line:
            pos += 1

            if must_escape:
                must_escape = False
                if c == ' ' or c == '\\' or c == '\'' or c == '\"':
                    value += c
                    continue

                raise ex.ParseError('Invalid escape sequence "\{}" '
                                    'in argument.'.format(c),
                                    location=location)

            if c == '\\':
                must_escape = True
                continue

            if c == '=' and is_keyword_possible:
                # end of argument, start of value...
                is_keyword = True
                break

            if c.isspace() or c == '#':
                # end of argument...
                break

            value += c

        return (value, line[pos + 1:], is_keyword)


def _validate_exec_object(location, obj):
    command_name = obj.command()
    args = obj.arguments()
    kwargs = obj._kwargs

    command = Parser.command(command_name)
    return command.validate_arguments(location, *args, **kwargs)
