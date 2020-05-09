# -*- coding: utf-8 -*-
"""Parse system definition files.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from .exceptions import ParseError
from .location import Location
from .printer import debug
from .commandmanager import CommandManager
from .execobject import ExecObject

import re
import pyparsing as pp  # type: ignore
import typing


__octal_pattern = re.compile("^0o?([0-7]+)$")
__hex_pattern = re.compile("^0x([0-9a-fA-F]+)$")


def _generate_grammar(*, debug_parser: bool = False):
    pp.ParserElement.setDefaultWhitespaceChars(" \t")

    EOL = pp.Optional(pp.pythonStyleComment()) + pp.LineEnd()
    LC = pp.Suppress(pp.OneOrMore(EOL) + pp.White(ws=" \t", min=4))

    Identifier = pp.Word(initChars=pp.alphas, bodyChars=pp.alphanums + "_-")

    MultilineArgument = pp.QuotedString(
        quoteChar="<<<<", endQuoteChar=">>>>", multiline=True
    )
    SingleQuotedArgument = pp.QuotedString(quoteChar="'", escChar="\\")
    DoubleQuotedArgument = pp.QuotedString(quoteChar='"', escChar="\\")
    QuotedArgument = (SingleQuotedArgument | DoubleQuotedArgument | MultilineArgument)(
        "quoted"
    )
    SimpleArgument = pp.Word(pp.alphanums + "_-+*!$%&/()[]{}.,;:")("simple")
    Argument = (QuotedArgument | SimpleArgument) + pp.Optional(LC)

    KwArgument = pp.Combine(Identifier("key") + "=" + Argument)

    ArgumentList = pp.Group(pp.ZeroOrMore(pp.Group(KwArgument | Argument)))

    Command = (
        pp.locatedExpr(Identifier)("command") + pp.Optional(LC) + ArgumentList("args")
    )

    Grammar = pp.ZeroOrMore(pp.Group(pp.Optional(Command) + pp.Suppress(EOL)))

    if debug_parser:
        for expr_name in (
            "Grammar Command ArgumentList KwArgument Argument "
            "SimpleArgument QuotedArgument DoubleQuotedArgument "
            "SingleQuotedArgument MultilineArgument "
            "Identifier LC EOL".split()
        ):
            expr = locals()[expr_name]
            expr.setName(expr_name)
            expr.setDebug()

    Grammar.parseWithTabs()  # Keep tabs unexpanded!
    return Grammar


def __map_value(value: typing.Dict[str, str]) -> typing.Any:
    if "simple" in value:
        v = value["simple"]
        assert v is not None

        if v == "None":
            return None
        if v == "True":
            return True
        if v == "False":
            return False
        octal_match = __octal_pattern.match(v)
        if octal_match:
            return int(octal_match.group(1), 8)
        hex_match = __hex_pattern.match(v)
        if hex_match:
            return int(hex_match.group(1), 16)
        if v.isdigit():
            return int(v)
        return v
    else:
        return value["quoted"]


def _process_arguments(
    arguments: typing.List[typing.Dict[str, str]]
) -> typing.Tuple[typing.Tuple[typing.Any, ...], typing.Dict[str, typing.Any]]:
    args: typing.Tuple[typing.Any, ...] = ()
    kwargs: typing.Dict[str, typing.Any] = {}

    for a in arguments:
        key = a.get("key", "")
        if key:
            kwargs[key] = __map_value(a)
        else:
            args = (*args, __map_value(a))

    return args, kwargs


class Parser:
    """Parse a system definition file."""

    def __init__(
        self, command_manager: CommandManager, *, debug_parser: bool = False
    ) -> None:
        """Constructor."""
        self._command_manager = command_manager
        self._grammar = _generate_grammar(debug_parser=debug_parser)

    def parse(self, input_file: str) -> typing.Tuple[str, typing.List[ExecObject]]:
        """Parse a file."""
        with open(input_file, "r") as f:
            debug("Parsing file {}...".format(input_file))
            return self._parse_string(f.read(), input_file)

    def _parse_string(
        self, data, input_file_name
    ) -> typing.Tuple[str, typing.List[ExecObject]]:
        base_system_name = ""
        exec_obj_list: typing.List[ExecObject] = []

        current_location = Location(file_name=input_file_name)

        try:
            parse_result = self._grammar.parseString(data, parseAll=True)

            for c in parse_result:
                if not c:
                    continue

                child_dict = c.asDict()
                arguments = child_dict.get("args", [])
                if isinstance(arguments, dict):
                    arguments = [arguments]
                assert isinstance(arguments, list)

                command = child_dict.get("command", {})
                assert len(command) == 3

                command_pos = command.get("locn_start", -1)
                command_name = command.get("value", "")

                current_location = Location(
                    file_name=input_file_name,
                    line_number=pp.lineno(command_pos, data),
                    description=command_name,
                )
                command_info = self._command_manager.command(command_name)

                if not command_info:
                    raise ParseError(
                        "Unknown command {}.".format(c), location=current_location
                    )

                (args, kwargs) = _process_arguments(arguments)

                command_info.validate_func(current_location, *args, **kwargs)
                command_dependency = command_info.dependency_func(*args, **kwargs)
                if command_dependency:
                    if base_system_name:
                        raise ParseError(
                            "More than one base system was "
                            'provided in "{}".'.format(input_file_name)
                        )
                    base_system_name = command_dependency

                exec_obj_list.append(
                    ExecObject(
                        location=current_location,
                        command=command_name,
                        args=args,
                        kwargs=kwargs,
                    )
                )

        except pp.ParseException as pe:
            raise ParseError(str(pe), location=current_location)

        return base_system_name, exec_obj_list
