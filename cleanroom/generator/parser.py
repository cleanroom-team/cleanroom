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
import pyparsing as pp
import typing


def _generate_grammar(*, debug: bool=False):
    pp.ParserElement.setDefaultWhitespaceChars(' \t')

    EOL = pp.Optional(pp.pythonStyleComment()) + pp.LineEnd()
    LC = pp.Suppress(pp.OneOrMore(EOL) + pp.White(ws=' \t', min=4))

    Identifier = pp.Word(initChars=pp.alphas, bodyChars=pp.alphanums + '_-')
    
    MultilineArgument = pp.QuotedString(quoteChar = '<<<<', endQuoteChar = '>>>>', multiline=True)
    SingleQuotedArgument = pp.QuotedString(quoteChar = '\'', escChar = '\\')
    DoubleQuotedArgument = pp.QuotedString(quoteChar = '"', escChar = '\\')
    QuotedArgument = (SingleQuotedArgument | DoubleQuotedArgument | MultilineArgument)('quoted')
    SimpleArgument = pp.Word(pp.alphanums + '_-+*!$%&/()[]{}.,;:')('simple')
    Argument = (QuotedArgument | SimpleArgument) + pp.Optional(LC)

    KwArgument = pp.Combine(Identifier('key') + '=' + Argument)

    ArgumentList = pp.Group(pp.ZeroOrMore(pp.Group(KwArgument | Argument)))

    Command = pp.locatedExpr(Identifier)('command') + pp.Optional(LC) + ArgumentList('args')

    Grammar = pp.ZeroOrMore(pp.Group(pp.Optional(Command) + pp.Suppress(EOL)))

    if debug:
        for ename in "Grammar Command ArgumentList KwArgument Argument SimpleArgument QuotedArgument DoubleQuotedArgument SingleQuotedArgument MultilineArgument Identifier LC EOL".split():
            expr = locals()[ename]
            expr.setName(ename)
            expr.setDebug()

    Grammar.parseWithTabs()  # Keep tabs unexpanded!
    return Grammar


class Parser:
    """Parse a system definition file."""
    def __init__(self, command_manager: CommandManager, *, debug: bool=False) -> None:
        """Constructor."""
        self._command_manager = command_manager
        self._grammar = _generate_grammar(debug=debug)

    def parse(self, input_file: str) -> typing.List[ExecObject]:
        """Parse a file."""
        with open(input_file, 'r') as f:
            debug('Parsing file {}...'.format(input_file))
            return self._parse_string(f.read(), input_file)

    def _parse_string(self, data, input_file):
        result: typing.List[ExecObject] = []
        built_in = Location(file_name='<BUILT_IN>', line_number=1)
        result.append(ExecObject(built_in, None, '_setup'))
        
        current_location = Location(file_name=input_file)

        try:
            parse_result = self._grammar.parseString(data, parseAll=True)

            for c in parse_result:
                if len(c) == 0:  # empty line
                    continue

                child_dict = c.asDict()
                    
                arguments = child_dict.get('args', [])
                if isinstance(arguments, dict):
                    arguments = [arguments,]
                assert isinstance(arguments, list)

                command = child_dict.get('command', {})
                assert len(command) == 3

                command_pos = command.get('locn_start', -1)
                command_name = command.get('value', '')

                current_location = Location(file_name=input_file,
                                            line_number=pp.lineno(command_pos, data),
                                            description=command_name)
                cmd = self._command_manager.command(command_name)

                if not cmd:
                    raise ParseError('Unknown command {}.'.format(c),
                                     location=current_location)

                (args, kwargs) = _process_arguments(arguments)
                result.append(cmd.exec_object(current_location, *args, **kwargs));
        except pp.ParseException as pe:
            raise ParseError(str(pe), location=current_location)
        except ParseError as pe:
            pe.set_location(current_location)
            raise

        built_in.set_description('_teardown')
        result.append(ExecObject(built_in, None, '_teardown'))
        return result


def _process_arguments(arguments: typing.List[typing.Dict[str, str]]) \
        -> typing.Tuple[typing.List[typing.Any], typing.Dict[str, typing.Any]]:
    args: typing.List[typing.Any] = []
    kwargs: typing.Dict[str, typing.Any] = {}
    
    for a in arguments:
        key = a.get('key', None)
        value = a
        if key:
            kwargs[key] = _map_value(value)
        else:
            args.append(_map_value(value))
        
    return (args, kwargs)

def _map_value(value: typing.Dict[str, str]) -> typing.Any:
    if 'simple' in value:
        v = value['simple']
        assert v is not None

        if v == 'None':
            return None
        if v == 'True':
            return True
        if v == 'False':
            return False
        octal_match = _map_value._octal_pattern.match(v) 
        if octal_match:
            return int(octal_match.group(1), 8)
        hex_match = _map_value._hex_pattern.match(v)
        if hex_match:
            return int(hex_match.group(1), 16)
        if v.isdigit():
            return int(v)
        return v
    else:
        return value['quoted']    

_map_value._octal_pattern = re.compile('^0o?([0-7]+)$')
_map_value._hex_pattern = re.compile('^0x([0-9a-fA-F]+)$')

