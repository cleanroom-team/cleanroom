# -*- coding: utf-8 -*-
"""Parse system definition files.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from .command import Command
from .commandmanager import CommandManager
from .context import Context
from .execobject import ExecObject

from ..exceptions import ParseError
from ..location import Location
from ..printer import debug, h2

import importlib.util
import inspect
import os
import re
import typing


class _ParserState:
    """Hold the state of the Parser."""

    def __init__(self, file_name: str, command_manager: CommandManager) -> None:
        self._command_manager = command_manager
        self._current_file_name = file_name
        self._current_line = 1
        self._start_line = 1
        self._to_process = ''
        self._key_for_value = ''

        self._indent_depth = 0

        self.reset()

    def is_token_complete(self) -> bool:
        return self._incomplete_token == ''

    def is_command_continuation(self) -> bool:
        if self._to_process == '' or self._to_process == '\n':
            return True

        return self._indent_depth > 0 \
            and self._to_process.startswith(' ' * self._indent_depth)

    def record_command_start(self) -> None:
        self._start_line = self._current_line

    def next_line(self) -> None:
        self._current_line += 1

    def current_location(self) -> Location:
        return Location(file_name=self._current_file_name, line_number=self._current_line)

    def start_location(self) -> typing.Optional[Location]:
        if self._start_line < 1:
            return None
        return Location(file_name=self._current_file_name, line_number=self._start_line)

    def reset(self) -> None:
        self._args: typing.List[typing.Any] = []
        self._kwargs: typing.Dict[str, typing.Any] = {}

        self._key_for_value = ''
        self._incomplete_token = ''

        self._indent_depth = 0

        assert(self.is_token_complete())

    def create_execute_object(self) -> typing.Optional[ExecObject]:
        if not self._args or self._start_line == 0:
            return None

        args = self._args
        kwargs = self._kwargs
        if self._key_for_value:
            kwargs[self._key_for_value] = ''

        self.reset()

        location = self.start_location()
        assert location
        command = self._command_manager.command(args[0])
        assert command
        return command.exec_object(location, *args[1:], **kwargs)

    def _args_to_string(self) -> str:
        args = ','.join([str(a) for a in self._args]) + ':' \
            + ','.join([k + '=' + str(v) for (k, v) in self._kwargs.items()])
        return args.replace('\n', '\\n').replace('\t', '\\t')

    def _to_process_to_string(self) -> str:
        return self._to_process.replace('\n', '\\n').replace('\t', '\\t')

    def _incomplete_token_to_string(self) -> str:
        return self._incomplete_token.replace('\n', '\\n').replace('\t', '\\t')

    def __str__(self) -> str:
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
    def __init__(self, command_manager: CommandManager) -> None:
        """Constructor."""
        self._command_manager = command_manager

        self._command_pattern = re.compile('^[A-Za-z][A-Za-z0-9_-]*$')
        self._octal_pattern = re.compile('^0o?([0-7]+)$')
        self._hex_pattern = re.compile('^0x([0-9a-fA-F]+)$')

    def parse(self, input_file: str) -> typing.Generator[ExecObject, None, None]:
        """Parse a file."""
        with open(input_file, 'r') as f:
            for result in self._parse_lines(f, input_file):
                yield result

    def _parse_lines(self, iterable: typing.Iterator[str],
                     file_name: str) -> typing.Generator[ExecObject, None, None]:
        """Parse an iterable of lines."""
        state = _ParserState(file_name, self._command_manager)
        built_in = Location(file_name='<BUILT_IN>', line_number=1)

        yield ExecObject(built_in, None, '_setup')

        for line in iterable:
            state._to_process += line

            (state, obj) = self._parse_single_line(state)
            if obj:
                yield obj

            if state._to_process != '':
                raise ParseError('Unexpected tokens "{}" found.'
                                 .format(state._to_process),
                                 location=state.current_location())

            state.next_line()

        if not state.is_token_complete():
            raise ParseError('Unexpected EOF.',
                             location=state.current_location())

        # Flush last exec object:
        flush_obj = state.create_execute_object()
        if flush_obj:
            yield flush_obj

        yield ExecObject(built_in, None, '_teardown')

    def _parse_single_line(self, state: _ParserState) \
            -> typing.Tuple[_ParserState, typing.Optional[ExecObject]]:
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

    def _strip_comment_and_ws(self, line: str) -> str:
        """Extract a comment up to the end of the line."""
        input = line
        line = input.lstrip()
        if line == '\n' or line == '' or line.startswith('#'):
            line = ''

        return line

    def _extract_command(self, state: _ParserState) -> _ParserState:
        """Extract the command from a line."""
        assert(state._indent_depth == 0)
        assert(state._args == [])
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

        state._args = [self._validate_command(state, command),]
        state._to_process = line[pos:]

        return state

    def _extract_arguments(self, state: _ParserState) -> _ParserState:
        # extract arguments:
        while state._to_process != '':
            location = state.start_location()
            assert(location)
            (key, has_value, value, to_process, token) \
                = self._parse_next_argument(location, state._to_process, state._incomplete_token)

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
                    state._args.append(value)

        return state

    def _validate_command(self, state: _ParserState, command: str) -> str:
        if not command:
            raise ParseError('Empty command found.', location=state.start_location())

        if not self._command_pattern.match(command):
            raise ParseError('Invalid command "{}".'.format(command),
                             location=state.start_location())

        if not self._command_manager.command(command):
            raise ParseError('Command "{}" not found.'.format(command),
                             location=state.start_location())

        return command

    def _parse_next_argument(self, location: Location, to_process: str,
                             token: str) -> typing.Tuple[typing.Optional[str], bool,
                                                         typing.Optional[str], str, str]:
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
            assert key
            if not self._command_pattern.match(key):
                raise ParseError('Keyword "{}" is not valid.'.format(key),
                                 location=location)

            (has_part, section, is_keyword, to_process, token) \
                = self._parse_argument_part(location, to_process, token,
                                            is_keyword_possible=False)

            value = section
            has_value = has_part

            if not has_value and not token:
                raise ParseError('Keyword without a value found.',
                                 location=location)
            assert(not is_keyword)
        else:
            value = section
            has_value = True

        return (key, has_value, value, to_process, token)

    def _parse_argument_part(self, location: Location, to_process: str, token: str, *,
                             is_keyword_possible: bool=False) \
            -> typing.Tuple[bool, typing.Optional[str], bool, str, str]:
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

    def _process_value(self, value: str) -> typing.Any:
        if value is None:
            return None

        octal_match = self._octal_pattern.match(value)
        hex_match = self._hex_pattern.match(value)
        if value == 'None':
            return None
        if value == 'True':
            return True
        if value == 'False':
            return False
        if octal_match:
            return int(octal_match.group(1), 8)
        if hex_match:
            return int(hex_match.group(1), 16)
        if value.isdigit():
            return int(value)
        return value

    def _extract_multiline_argument(self, state: _ParserState) -> _ParserState:
        location = state.start_location()
        assert location
        (value, to_process, token) \
            = self._parse_multiline_argument(location, state._to_process, state._incomplete_token)
        state._to_process = to_process
        state._incomplete_token = token
        if token == '':
            if state._key_for_value:
                state._kwargs[state._key_for_value] = value
                state._key_for_value = ''
            else:
                state._args.append(value)

        return state

    def _parse_multiline_argument(self, location: Location,
                                  to_process: str, token: str) \
            -> typing.Tuple[typing.Optional[str], str, str]:
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

    def _parse_string_argument(self, location: Location,
                               line: str, quote: str) -> typing.Tuple[str, str]:
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

                raise ParseError('Invalid escape sequence "\{}" in string.'
                                 .format(c), location=location)

            if c == '\\':
                must_escape = True
                continue

            if c == quote:
                return (value, line[pos + 1:])

            value += c

        raise ParseError('Missing closing "{}" quote.'.format(quote),
                         location=location)

    def _parse_normal_argument(self, location: Location, line: str,
                               is_keyword_possible: bool=True) -> typing.Tuple[str, str, bool]:
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

                raise ParseError('Invalid escape sequence "\{}" in argument.'
                                 .format(c), location=location)

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
