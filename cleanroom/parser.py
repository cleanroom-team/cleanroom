#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from . import exceptions


from enum import Enum, auto, unique
import importlib.util
import inspect
import os


class ExecObject:
    def __init__(self, name, command, args):
        self._name = name
        self._command = command
        self._args = args

    def execute(self):
        self._command.execute(*self._args)


class _ParserState:
    def __init__(self):
        self._line_number = -1

        self._command = ''
        self._args = []
        self._multiline_start = ''

class Parser:
    ''' Parse a container.conf file '''

    _commands = {}
    ''' A list of known commands '''

    @staticmethod
    def find_commands(ctx):
        ctx.printer.trace('Checking for commands.')
        checked_dirs = []
        for path in ( ctx.systemsCommandsDirectory(), ctx.commandsDirectory()):
            if path in checked_dirs:
                continue
            checked_dirs.append(path)
            ctx.printer.trace('Checking "{}" for command files.'.format(path))
            if not os.path.isdir(path):
                continue # skip non-existing directories

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

                predicate = lambda x : inspect.isclass(x) and \
                                       x.__name__.endswith('Command') and \
                                       x.__module__ == name
                klass = inspect.getmembers(cmd_module, predicate)
                instance = klass[0][1](ctx)
                Parser._commands[cmd] = ( instance, f_path )

        ctx.printer.debug('Commands found:')
        for (name, value) in Parser._commands.items():
            path = value[1]
            location = '<GLOBAL>' if path.startswith(ctx.commandsDirectory() + '/') else '<LOCAL>'
            ctx.printer.debug('  {}: {}'.format(name, location))

    def __init__(self, ctx):
        self._ctx = ctx

    def parse(self, input_file):
        _reset_parsing_state(self)

        with open(input_file, 'r') as f:
            yield _parse_lines(f)

    def _parse_lines(self, iterable):
        result = []
        state = _ParserState()

        for line in iterable:
            (state, obj) = self._parse_single_line(state, line)
            if obj: yield obj

        if state._multiline_start:
            raise exceptions.ParseError(line, 'In multiline string at EOF.')

        return result

    def _parse_single_line(self, state, line):
        state._line_number += 1

        if state._multiline_start:
            self._ctx.printer.trace('parsing "{}" (multiline continuation)'.format(line[:-1]))
            pass # handle multi-line strings
        else:
            print('parsing "{}"'.format(line))
            (next_state, command, args) = self._extract_command(state, line)
            print('::: {}: {} --- State: {}: {} :::'.format(command, args, next_state._command, next_state._multiline_start))
            if command and next_state._multiline_start == '':
                obj = ExecObject(command, Parser._commands[command][0], args)
                return (next_state, obj)
            else:
                return (next_state, None)

    def _extract_command(self, state, line):
        assert(state._multiline_start == '')
        assert(state._command == '')
        assert(len(state._args) == 0)

        token = ''
        pos = -1

        in_leading_space = True

        has_arguments = False

        for c in line:
            pos += 1

            if c.isspace():
                if in_leading_space: continue

                assert(token)

                (state, args) = self._extract_arguments(state, str(line[pos:]))
                if state._multiline_start:
                    state._command = command
                    state._args = args

                    return (state, None, None)
                return (state, token, args)

            if c == '#':
                self._ctx.printer.trace('    Comment')
                command = token if token else None
                return (state, command, None) # No further processing necessary

            if c.isalnum():
                if in_leading_space:
                    in_leading_space = False
                token += c
                continue

            raise exceptions.ParseError(self._line_number, 'Unexpected character \'{}\'.'.format(c))

        if token: return (state, token, None) # Command only
        else: return (state, None, None) # Whitespace only

    def _extract_arguments(self, state, line):
        return (state, line)

