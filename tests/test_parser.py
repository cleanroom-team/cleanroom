#!/usr/bin/python
"""Test for the Parser class in cleanroom.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

import pytest  # type: ignore
import typing

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cleanroom.command import Command
from cleanroom.exceptions import ParseError
from cleanroom.location import Location


class DummyCommand(Command):
    """Dummy command implementation."""

    def __init__(self, name: str) -> None:
        """Constructor."""
        super().__init__(name, help_string="test", file=__file__)

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Accept all arguments."""
        pass


CMD1 = "test1"
CMD2 = "test2"
INVALID_CMD1 = "test!1"
INVALID_CMD2 = "1test"


def _setup_commands(parser):
    cm = parser._command_manager
    if not cm.command(CMD1):
        cm._add_command(CMD1, "<builtin>/1", DummyCommand(CMD1))
    if not cm.command(CMD2):
        cm._add_command(CMD2, "<builtin>/2", DummyCommand(CMD2))
    if not cm.command(INVALID_CMD1):
        cm._add_command(INVALID_CMD1, "<builtin>/3", DummyCommand(INVALID_CMD1))
    if not cm.command(INVALID_CMD1):
        cm._add_command(INVALID_CMD2, "<builtin>/4", DummyCommand(INVALID_CMD2))


@pytest.mark.parametrize(
    ("test_input", "expected"),
    [
        pytest.param("", [], id="empty"),
        pytest.param("\n", [], id="empty line"),
        pytest.param("", [], id="empty line no_nl"),
        pytest.param(" \t \t \n", [], id="ws"),
        pytest.param(" \t \t ", [], id="ws no_nl"),
        pytest.param("# test comment\n", [], id="comment"),
        pytest.param("# test comment", [], id="comment no_nl"),
        pytest.param(" \t  # test comment\n", [], id="ws comment"),
        pytest.param(" \t  # test comment", [], id="ws comment no_nl"),
        pytest.param("test1\n", [(CMD1, (), {}, 1)], id="command"),
        pytest.param("\ntest1\n", [(CMD1, (), {}, 2)], id="command in line 2"),
        pytest.param("test1", [(CMD1, (), {}, 1)], id="command no_nl"),
        pytest.param(" \t test1\n", [(CMD1, (), {}, 1)], id="ws command"),
        pytest.param(" \t test1", [(CMD1, (), {}, 1)], id="ws command no_nl"),
        pytest.param("test1# comment\n", [(CMD1, (), {}, 1)], id="command comment"),
        pytest.param("test1# comment", [(CMD1, (), {}, 1)], id="command comment no_nl"),
        pytest.param(
            "test1  \t# comment\n", [(CMD1, (), {}, 1)], id="command ws comment"
        ),
        pytest.param(
            "test1  \t# comment", [(CMD1, (), {}, 1)], id="command ws comment no_nl"
        ),
        pytest.param(" test1  arg1\n", [(CMD1, ("arg1",), {}, 1)], id="command arg"),
        pytest.param(
            " test1  arg1", [(CMD1, ("arg1",), {}, 1)], id="command arg no_nl"
        ),
        pytest.param(
            " test1  arg1 \n", [(CMD1, ("arg1",), {}, 1)], id="command arg ws"
        ),
        pytest.param(
            " test1  arg1 ", [(CMD1, ("arg1",), {}, 1)], id="command arg ws no_nl"
        ),
        pytest.param(" test1  42\n", [(CMD1, (42,), {}, 1)], id="command int_arg"),
        pytest.param(" test1  42", [(CMD1, (42,), {}, 1)], id="command int_arg no_nl"),
        pytest.param(" test1  42\t\n", [(CMD1, (42,), {}, 1)], id="command int_arg ws"),
        pytest.param(
            " test1  42 ", [(CMD1, (42,), {}, 1)], id="command int_arg ws no_nl"
        ),
        pytest.param(" test1  0o42\n", [(CMD1, (34,), {}, 1)], id="command octal_arg"),
        pytest.param(
            " test1  0o42", [(CMD1, (34,), {}, 1)], id="command octal_arg no_nl"
        ),
        pytest.param(
            " test1  0o42 \n", [(CMD1, (34,), {}, 1)], id="command octal_arg ws"
        ),
        pytest.param(
            " test1  0o42 ", [(CMD1, (34,), {}, 1)], id="command octal_arg ws no_nl"
        ),
        pytest.param(" test1  042\n", [(CMD1, (34,), {}, 1)], id="command octal2_arg"),
        pytest.param(
            " test1  042", [(CMD1, (34,), {}, 1)], id="command octal2_arg no_nl"
        ),
        pytest.param(
            " test1  042 \n", [(CMD1, (34,), {}, 1)], id="command octal2_arg ws"
        ),
        pytest.param(
            " test1  042 ", [(CMD1, (34,), {}, 1)], id="command octal2_arg ws no_nl"
        ),
        pytest.param(" test1  0x42\n", [(CMD1, (66,), {}, 1)], id="command hex_arg"),
        pytest.param(
            " test1  0x42", [(CMD1, (66,), {}, 1)], id="command hex_arg no_nl"
        ),
        pytest.param(
            " test1  0x42 \n", [(CMD1, (66,), {}, 1)], id="command hex_arg ws"
        ),
        pytest.param(
            " test1  0x42 ", [(CMD1, (66,), {}, 1)], id="command hex_arg ws no_nl"
        ),
        pytest.param(" test1  True\n", [(CMD1, (True,), {}, 1)], id="command True"),
        pytest.param(" test1  True", [(CMD1, (True,), {}, 1)], id="command True no_nl"),
        pytest.param(
            " test1  True\t\n", [(CMD1, (True,), {}, 1)], id="command True ws"
        ),
        pytest.param(
            " test1  True\t", [(CMD1, (True,), {}, 1)], id="command True ws no_nl"
        ),
        pytest.param(" test1  False\n", [(CMD1, (False,), {}, 1)], id="command False"),
        pytest.param(
            " test1  False", [(CMD1, (False,), {}, 1)], id="command False no_nl"
        ),
        pytest.param(
            " test1  False\t\n", [(CMD1, (False,), {}, 1)], id="command False ws"
        ),
        pytest.param(
            " test1  False\t", [(CMD1, (False,), {}, 1)], id="command False ws no_nl"
        ),
        pytest.param(" test1  None\n", [(CMD1, (None,), {}, 1)], id="command None"),
        pytest.param(" test1  None", [(CMD1, (None,), {}, 1)], id="command None no_nl"),
        pytest.param(
            " test1  None\t\n", [(CMD1, (None,), {}, 1)], id="command None ws"
        ),
        pytest.param(
            " test1  None\t", [(CMD1, (None,), {}, 1)], id="command None ws no_nl"
        ),
        pytest.param(' test1  "42"\n', [(CMD1, ("42",), {}, 1)], id="command int_dq"),
        pytest.param(
            ' test1  "42"', [(CMD1, ("42",), {}, 1)], id="command int_dq no_nl"
        ),
        pytest.param(
            ' test1  "42" \n', [(CMD1, ("42",), {}, 1)], id="command int_dq ws"
        ),
        pytest.param(
            ' test1  "42" ', [(CMD1, ("42",), {}, 1)], id="command int_dq ws no_nl"
        ),
        pytest.param(
            ' test1  "0o42"\n', [(CMD1, ("0o42",), {}, 1)], id="command octal_dq"
        ),
        pytest.param(
            ' test1  "042"\n', [(CMD1, ("042",), {}, 1)], id="command octal2_dq"
        ),
        pytest.param(
            ' test1  "0xf8"\n', [(CMD1, ("0xf8",), {}, 1)], id="command hex_dq"
        ),
        pytest.param(
            ' test1  "True"\n', [(CMD1, ("True",), {}, 1)], id="command True_dq"
        ),
        pytest.param(
            ' test1  "False"\n', [(CMD1, ("False",), {}, 1)], id="command False_dq"
        ),
        pytest.param(
            ' test1  "None"\n', [(CMD1, ("None",), {}, 1)], id="command None_dq"
        ),
        pytest.param(" test1  '42'\n", [(CMD1, ("42",), {}, 1)], id="command int_sq"),
        pytest.param(
            " test1  '0o42'\n", [(CMD1, ("0o42",), {}, 1)], id="command octal_sq"
        ),
        pytest.param(
            " test1  '042'\n", [(CMD1, ("042",), {}, 1)], id="command octal2_sq"
        ),
        pytest.param(
            " test1  '0xf8'\n", [(CMD1, ("0xf8",), {}, 1)], id="command hex_sq"
        ),
        pytest.param(
            " test1  'True'\n", [(CMD1, ("True",), {}, 1)], id="command True_sq"
        ),
        pytest.param(
            " test1  'False'\n", [(CMD1, ("False",), {}, 1)], id="command False_sq"
        ),
        pytest.param(
            " test1  'None'\n", [(CMD1, ("None",), {}, 1)], id="command None_sq"
        ),
        pytest.param(
            "test1  arg1  arg2\n",
            [(CMD1, ("arg1", "arg2"), {}, 1)],
            id="command arg arg",
        ),
        pytest.param(
            "test1  arg1  arg2",
            [(CMD1, ("arg1", "arg2"), {}, 1)],
            id="command arg arg no_nl",
        ),
        pytest.param(
            "test1  arg1  arg2\t  \n",
            [(CMD1, ("arg1", "arg2"), {}, 1)],
            id="command arg arg ws",
        ),
        pytest.param(
            "test1  arg1  arg2\t  ",
            [(CMD1, ("arg1", "arg2"), {}, 1)],
            id="command arg arg ws no_nl",
        ),
        pytest.param(
            "test1  ''  arg", [(CMD1, ("", "arg"), {}, 1)], id="command empty_sq arg"
        ),
        pytest.param(
            'test1  ""  arg', [(CMD1, ("", "arg"), {}, 1)], id="command empty_dq arg"
        ),
        pytest.param(
            "test1 ' arg 42'\n", [(CMD1, (" arg 42",), {}, 1)], id="command sq"
        ),
        pytest.param(
            "test1 ' arg 42'", [(CMD1, (" arg 42",), {}, 1)], id="command sq no_nl"
        ),
        pytest.param(
            'test1 " arg 42"\n', [(CMD1, (" arg 42",), {}, 1)], id="command dq"
        ),
        pytest.param(
            'test1 " arg 42"', [(CMD1, (" arg 42",), {}, 1)], id="command dq no_nl"
        ),
        pytest.param(
            "test1 ' arg 42 # comment'\n",
            [(CMD1, (" arg 42 # comment",), {}, 1)],
            id="command sq_comment",
        ),
        pytest.param(
            "test1 ' arg 42 # comment'",
            [(CMD1, (" arg 42 # comment",), {}, 1)],
            id="command sq_comment no_nl",
        ),
        pytest.param(
            'test1 " arg 42 # comment"\n',
            [(CMD1, (" arg 42 # comment",), {}, 1)],
            id="command dq_comment",
        ),
        pytest.param(
            'test1 " arg 42 # comment"',
            [(CMD1, (" arg 42 # comment",), {}, 1)],
            id="command dq_comment no_nl",
        ),
        pytest.param(
            "test1 ' arg \"42\"'\n",
            [(CMD1, (' arg "42"',), {}, 1)],
            id="command sq_with_dq",
        ),
        pytest.param(
            "test1 ' arg \"42\"'",
            [(CMD1, (' arg "42"',), {}, 1)],
            id="command sq_with_dq no_nl",
        ),
        pytest.param(
            "test1 ' arg \\'42\\''\n",
            [(CMD1, (" arg '42'",), {}, 1)],
            id="command sq_with_sq",
        ),
        pytest.param(
            "test1 ' arg \\'42\\''",
            [(CMD1, (" arg '42'",), {}, 1)],
            id="command sq_with_sq no_nl",
        ),
        pytest.param(
            'test1 " arg \\"42\\""\n',
            [(CMD1, (' arg "42"',), {}, 1)],
            id="command dq_with_dq",
        ),
        pytest.param(
            'test1 " arg \\"42\\""',
            [(CMD1, (' arg "42"',), {}, 1)],
            id="command dq_with_dq no_nl",
        ),
        pytest.param(
            "test1 \" arg '42'\"\n",
            [(CMD1, (" arg '42'",), {}, 1)],
            id="command dq_with_sq",
        ),
        pytest.param(
            "test1 \" arg '42'\"",
            [(CMD1, (" arg '42'",), {}, 1)],
            id="command dq_with_sq no_nl",
        ),
        pytest.param(
            "test1 ' arg \\'42'\n",
            [(CMD1, (" arg '42",), {}, 1)],
            id="command sq_with_one_sq",
        ),
        pytest.param(
            "test1 ' arg \\'42'",
            [(CMD1, (" arg '42",), {}, 1)],
            id="command sq_with_one_sq no_nl",
        ),
        pytest.param(
            'test1 " arg \'42"\n',
            [(CMD1, (" arg '42",), {}, 1)],
            id="command dq_with_one_sq",
        ),
        pytest.param(
            'test1 " arg \'42"',
            [(CMD1, (" arg '42",), {}, 1)],
            id="command dq_with_one_sq no_nl",
        ),
        pytest.param(
            "test1 'key=value'\n",
            [(CMD1, ("key=value",), {}, 1)],
            id="command arg_key_value_sq",
        ),
        pytest.param(
            "test1 'key=value'",
            [(CMD1, ("key=value",), {}, 1)],
            id="command arg_key_value_sq no_nl",
        ),
        pytest.param(
            "test1 'key=value' \n",
            [(CMD1, ("key=value",), {}, 1)],
            id="command arg_key_value_sq ws",
        ),
        pytest.param(
            "test1 'key=value' ",
            [(CMD1, ("key=value",), {}, 1)],
            id="command arg_key_value_sq ws no_nl",
        ),
        pytest.param(
            'test1  "key=value"\n',
            [(CMD1, ("key=value",), {}, 1)],
            id="command arg_key_value_dq",
        ),
        pytest.param(
            'test1  "key=value"',
            [(CMD1, ("key=value",), {}, 1)],
            id="command arg_key_value_dq no_nl",
        ),
        pytest.param(
            'test1  "key=value" \n',
            [(CMD1, ("key=value",), {}, 1)],
            id="command arg_key_value_dq ws",
        ),
        pytest.param(
            'test1  "key=value" ',
            [(CMD1, ("key=value",), {}, 1)],
            id="command arg_key_value_dq ws no_nl",
        ),
        pytest.param(
            "test1  value=arg\n", [(CMD1, (), {"value": "arg"}, 1)], id="command kwarg"
        ),
        pytest.param(
            "test1  value=arg",
            [(CMD1, (), {"value": "arg"}, 1)],
            id="command kwarg no_nl",
        ),
        pytest.param(
            "test1  value=arg \t\n",
            [(CMD1, (), {"value": "arg"}, 1)],
            id="command kwarg ws",
        ),
        pytest.param(
            "test1  value=arg \t",
            [(CMD1, (), {"value": "arg"}, 1)],
            id="command kwarg ws no_nl",
        ),
        pytest.param(
            "test1  value='arg 1'\n",
            [(CMD1, (), {"value": "arg 1"}, 1)],
            id="command kwarg_with_sq",
        ),
        pytest.param(
            "test1  value='arg 1'",
            [(CMD1, (), {"value": "arg 1"}, 1)],
            id="command kwarg_with_sq no_nl",
        ),
        pytest.param(
            'test1  value="arg 1"\n',
            [(CMD1, (), {"value": "arg 1"}, 1)],
            id="command kwarg_with_dq",
        ),
        pytest.param(
            'test1  value="arg 1"',
            [(CMD1, (), {"value": "arg 1"}, 1)],
            id="command kwarg_with_dq no_nl",
        ),
        pytest.param(
            "test1  value=True\n",
            [(CMD1, (), {"value": True}, 1)],
            id="command kwarg_True",
        ),
        pytest.param(
            "test1  value=True",
            [(CMD1, (), {"value": True}, 1)],
            id="command kwarg_True no_nl",
        ),
        pytest.param(
            "test1  value='True'\n",
            [(CMD1, (), {"value": "True"}, 1)],
            id="command kwarg_True_sq",
        ),
        pytest.param(
            "test1  value='True'",
            [(CMD1, (), {"value": "True"}, 1)],
            id="command kwarg_True_sq no_nl",
        ),
        pytest.param(
            'test1  value="True"\n',
            [(CMD1, (), {"value": "True"}, 1)],
            id="command kwarg_True_dq",
        ),
        pytest.param(
            'test1  value="True"',
            [(CMD1, (), {"value": "True"}, 1)],
            id="command kwarg_True_dq no_nl",
        ),
        pytest.param(
            "test1  value=False\n",
            [(CMD1, (), {"value": False}, 1)],
            id="command kwarg_False",
        ),
        pytest.param(
            "test1  value=False",
            [(CMD1, (), {"value": False}, 1)],
            id="command kwarg_False no_nl",
        ),
        pytest.param(
            "test1  value='False'\n",
            [(CMD1, (), {"value": "False"}, 1)],
            id="command kwarg_False_sq",
        ),
        pytest.param(
            "test1  value='False'",
            [(CMD1, (), {"value": "False"}, 1)],
            id="command kwarg_False_sq no_nl",
        ),
        pytest.param(
            'test1  value="False"\n',
            [(CMD1, (), {"value": "False"}, 1)],
            id="command kwarg_False_dq",
        ),
        pytest.param(
            'test1  value="False"',
            [(CMD1, (), {"value": "False"}, 1)],
            id="command kwarg_False_dq no_nl",
        ),
        pytest.param(
            "test1  value=None\n",
            [(CMD1, (), {"value": None}, 1)],
            id="command kwarg_None",
        ),
        pytest.param(
            "test1  value=None",
            [(CMD1, (), {"value": None}, 1)],
            id="command kwarg_None no_nl",
        ),
        pytest.param(
            "test1  value='None'\n",
            [(CMD1, (), {"value": "None"}, 1)],
            id="command kwarg_None_sq",
        ),
        pytest.param(
            "test1  value='None'",
            [(CMD1, (), {"value": "None"}, 1)],
            id="command kwarg_None_sq no_nl",
        ),
        pytest.param(
            'test1  value="None"\n',
            [(CMD1, (), {"value": "None"}, 1)],
            id="command kwarg_None_dq",
        ),
        pytest.param(
            'test1  value="None"',
            [(CMD1, (), {"value": "None"}, 1)],
            id="command kwarg_None_dq no_nl",
        ),
        pytest.param(
            "test1  value=42\n", [(CMD1, (), {"value": 42}, 1)], id="command kwarg_42"
        ),
        pytest.param(
            "test1  value=42",
            [(CMD1, (), {"value": 42}, 1)],
            id="command kwarg_42 no_nl",
        ),
        pytest.param(
            "test1  value='42'\n",
            [(CMD1, (), {"value": "42"}, 1)],
            id="command kwarg_42_sq",
        ),
        pytest.param(
            "test1  value='42'",
            [(CMD1, (), {"value": "42"}, 1)],
            id="command kwarg_42_sq no_nl",
        ),
        pytest.param(
            'test1  value="42"\n',
            [(CMD1, (), {"value": "42"}, 1)],
            id="command kwarg_42_dq",
        ),
        pytest.param(
            'test1  value="42"',
            [(CMD1, (), {"value": "42"}, 1)],
            id="command kwarg_42_dq no_nl",
        ),
        pytest.param(
            "test1  value=0o42\n",
            [(CMD1, (), {"value": 34}, 1)],
            id="command kwarg_0o42",
        ),
        pytest.param(
            "test1  value=0o42",
            [(CMD1, (), {"value": 34}, 1)],
            id="command kwarg_0o42 no_nl",
        ),
        pytest.param(
            "test1  value='0o42'\n",
            [(CMD1, (), {"value": "0o42"}, 1)],
            id="command kwarg_0o42_sq",
        ),
        pytest.param(
            "test1  value='0o42'",
            [(CMD1, (), {"value": "0o42"}, 1)],
            id="command kwarg_0o42_sq no_nl",
        ),
        pytest.param(
            'test1  value="0o42"\n',
            [(CMD1, (), {"value": "0o42"}, 1)],
            id="command kwarg_0o42_dq",
        ),
        pytest.param(
            'test1  value="0o42"',
            [(CMD1, (), {"value": "0o42"}, 1)],
            id="command kwarg_0o42_dq no_nl",
        ),
        pytest.param(
            "test1  value=042\n", [(CMD1, (), {"value": 34}, 1)], id="command kwarg_042"
        ),
        pytest.param(
            "test1  value=042",
            [(CMD1, (), {"value": 34}, 1)],
            id="command kwarg_042 no_nl",
        ),
        pytest.param(
            "test1  value='042'\n",
            [(CMD1, (), {"value": "042"}, 1)],
            id="command kwarg_042_sq",
        ),
        pytest.param(
            "test1  value='042'",
            [(CMD1, (), {"value": "042"}, 1)],
            id="command kwarg_042_sq no_nl",
        ),
        pytest.param(
            'test1  value="042"\n',
            [(CMD1, (), {"value": "042"}, 1)],
            id="command kwarg_042_dq",
        ),
        pytest.param(
            'test1  value="042"',
            [(CMD1, (), {"value": "042"}, 1)],
            id="command kwarg_042_dq no_nl",
        ),
        pytest.param(
            "test1  value=0x42\n",
            [(CMD1, (), {"value": 66}, 1)],
            id="command kwarg_0x42",
        ),
        pytest.param(
            "test1  value=0x42",
            [(CMD1, (), {"value": 66}, 1)],
            id="command kwarg_0x42 no_nl",
        ),
        pytest.param(
            "test1  value='0x42'\n",
            [(CMD1, (), {"value": "0x42"}, 1)],
            id="command kwarg_0x42_sq",
        ),
        pytest.param(
            "test1  value='0x42'",
            [(CMD1, (), {"value": "0x42"}, 1)],
            id="command kwarg_0x42_sq no_nl",
        ),
        pytest.param(
            'test1  value="0x42"\n',
            [(CMD1, (), {"value": "0x42"}, 1)],
            id="command kwarg_0x42_dq",
        ),
        pytest.param(
            'test1  value="0x42"',
            [(CMD1, (), {"value": "0x42"}, 1)],
            id="command kwarg_0x42_dq no_nl",
        ),
        pytest.param(
            "test1  value=<<<<>>>>\n",
            [(CMD1, (), {"value": ""}, 1)],
            id="command kwarg_ml",
        ),
        pytest.param(
            "test1  value=<<<<>>>>",
            [(CMD1, (), {"value": ""}, 1)],
            id="command kwarg_ml no_nl",
        ),
        pytest.param(
            "test1  value=<<<<>>>> \t \n",
            [(CMD1, (), {"value": ""}, 1)],
            id="command kwarg_ml ws",
        ),
        pytest.param(
            "test1  value=<<<<>>>> \t ",
            [(CMD1, (), {"value": ""}, 1)],
            id="command kwarg_ml ws no_nl",
        ),
        pytest.param(
            "test1  value=<<<<arg 1>>>>\n",
            [(CMD1, (), {"value": "arg 1"}, 1)],
            id="command kwarg_ml_with_ws",
        ),
        pytest.param(
            "test1  value=<<<<arg 1>>>>",
            [(CMD1, (), {"value": "arg 1"}, 1)],
            id="command kwarg_ml_with_ws no_nl",
        ),
        pytest.param(
            "test1  value=<<<<arg 1>>>> \t \n",
            [(CMD1, (), {"value": "arg 1"}, 1)],
            id="command kwarg_ml_with_ws ws",
        ),
        pytest.param(
            "test1  value=<<<<arg 1>>>> \t ",
            [(CMD1, (), {"value": "arg 1"}, 1)],
            id="command kwarg_ml_with_ws ws no_nl",
        ),
        pytest.param(
            "test1  value=<<<<True>>>>\n",
            [(CMD1, (), {"value": "True"}, 1)],
            id="command kwarg_ml_True",
        ),
        pytest.param(
            "test1  value=<<<<False>>>>\n",
            [(CMD1, (), {"value": "False"}, 1)],
            id="command kwarg_ml_False",
        ),
        pytest.param(
            "test1  value=<<<<None>>>>\n",
            [(CMD1, (), {"value": "None"}, 1)],
            id="command kwarg_ml_None",
        ),
        pytest.param(
            "test1  value=<<<<42>>>>\n",
            [(CMD1, (), {"value": "42"}, 1)],
            id="command kwarg_ml_42",
        ),
        pytest.param(
            "test1  value=<<<<0o42>>>>\n",
            [(CMD1, (), {"value": "0o42"}, 1)],
            id="command kwarg_ml_0o42",
        ),
        pytest.param(
            "test1  value=<<<<042>>>>\n",
            [(CMD1, (), {"value": "042"}, 1)],
            id="command kwarg_ml_042",
        ),
        pytest.param(
            "test1  value=<<<<0x42>>>>\n",
            [(CMD1, (), {"value": "0x42"}, 1)],
            id="command kwarg_ml_0x42",
        ),
        pytest.param(
            "test1 arg1 <<<<foo>>>> arg2\n",
            [(CMD1, ("arg1", "foo", "arg2"), {}, 1)],
            id="command arg ml_arg arg",
        ),
        pytest.param(
            "test1 arg1 <<<<foo>>>> arg2",
            [(CMD1, ("arg1", "foo", "arg2"), {}, 1)],
            id="command arg ml_arg arg no_nl",
        ),
        pytest.param(
            "test1 arg1 <<<<foo>>>> arg2\t \n",
            [(CMD1, ("arg1", "foo", "arg2"), {}, 1)],
            id="command arg ml_arg arg ws",
        ),
        pytest.param(
            "test1 arg1 <<<<foo>>>> arg2\t ",
            [(CMD1, ("arg1", "foo", "arg2"), {}, 1)],
            id="command arg ml_arg arg ws no_nl",
        ),
        pytest.param(
            "test1 arg1 <<<<foo\nbar>>>> arg2\n",
            [(CMD1, ("arg1", "foo\nbar", "arg2"), {}, 1)],
            id="command arg two_line_ml_arg arg",
        ),
        pytest.param(
            "test1 arg1 <<<<foo\nbar>>>> arg2",
            [(CMD1, ("arg1", "foo\nbar", "arg2"), {}, 1)],
            id="command arg two_line_ml_arg arg no_nl",
        ),
        pytest.param(
            "test1 arg1 <<<<foo\nbar>>>> arg2\t\n",
            [(CMD1, ("arg1", "foo\nbar", "arg2"), {}, 1)],
            id="command arg two_line_ml_arg arg ws",
        ),
        pytest.param(
            "test1 arg1 <<<<foo\nbar>>>> arg2\t",
            [(CMD1, ("arg1", "foo\nbar", "arg2"), {}, 1)],
            id="command arg two_line_ml_arg arg ws no_nl",
        ),
        pytest.param(
            "test1 arg1 <<<<foo\nbar\nbaz>>>> arg2\n",
            [(CMD1, ("arg1", "foo\nbar\nbaz", "arg2"), {}, 1)],
            id="command arg three_line_ml_arg arg",
        ),
        pytest.param(
            "test1 arg1 <<<<foo\nbar\nbaz>>>> arg2",
            [(CMD1, ("arg1", "foo\nbar\nbaz", "arg2"), {}, 1)],
            id="command arg three_line_ml_arg arg no_nl",
        ),
        pytest.param(
            "test1 arg1 <<<<foo\nbar\nbaz>>>> arg2  \n",
            [(CMD1, ("arg1", "foo\nbar\nbaz", "arg2"), {}, 1)],
            id="command arg three_line_ml_arg arg ws",
        ),
        pytest.param(
            "test1 arg1 <<<<foo\nbar\nbaz>>>> arg2  ",
            [(CMD1, ("arg1", "foo\nbar\nbaz", "arg2"), {}, 1)],
            id="command arg three_line_ml_arg arg ws no_nl",
        ),
        pytest.param(
            "test1 'arg1'<<<<foo>>>><<<<\nbar\nbaz>>>>\"arg2\" # foobar\n",
            [(CMD1, ("arg1", "foo", "\nbar\nbaz", "arg2"), {}, 1)],
            id="command arg ml_arg ml_arg arg ws comment",
        ),
        pytest.param(
            "test1 'arg1'<<<<foo>>>><<<<\nbar\nbaz>>>>\"arg2\" # foobar",
            [(CMD1, ("arg1", "foo", "\nbar\nbaz", "arg2"), {}, 1)],
            id="command arg ml_arg ml_arg arg ws comment no_nl",
        ),
        pytest.param(
            "test1 'arg1'<<<<foo>>>><<<<\nbar\nbaz>>>>\"arg2\"# foobar\n",
            [(CMD1, ("arg1", "foo", "\nbar\nbaz", "arg2"), {}, 1)],
            id="command arg ml_arg ml_arg arg comment",
        ),
        pytest.param(
            "test1 'arg1'<<<<foo>>>><<<<\nbar\nbaz>>>>\"arg2\"# foobar",
            [(CMD1, ("arg1", "foo", "\nbar\nbaz", "arg2"), {}, 1)],
            id="command arg ml_arg ml_arg arg comment no_nl",
        ),
        pytest.param(
            "# Foo bar\n\n    # ignore this comment\n   test2 foo",
            [(CMD2, ("foo",), {}, 4)],
            id="comment comment command arg",
        ),
        pytest.param(
            "test1 'arg1'\n    test2\n\n  # ignore this comment\n        baz \"arg2\" # foobar\n   test2 foo",
            [(CMD1, ("arg1", "test2", "baz", "arg2"), {}, 1), (CMD2, ("foo",), {}, 6)],
            id="ml command",
        ),
        pytest.param(
            "test1\n         'arg1'\n    test2\n\n  # ignore this comment\n        baz \"arg2\" # foobar\n   test2 foo",
            [(CMD1, ("arg1", "test2", "baz", "arg2"), {}, 1), (CMD2, ("foo",), {}, 7)],
            id="ml command on own line",
        ),
        pytest.param(
            "test1 <<<<line1\n  line2\n\n line3>>>>\n   test2 foo",
            [(CMD1, ("line1\n  line2\n\n line3",), {}, 1), (CMD2, ("foo",), {}, 5)],
            id="ml_arg command command",
        ),
        pytest.param(
            "\n  \n\t\n \n   test1 foo",
            [(CMD1, ("foo",), {}, 5)],
            id="empty lines command",
        ),
        pytest.param(
            "# comment 1\n# comment 2\n\n \n   test1 foo",
            [(CMD1, ("foo",), {}, 5)],
            id="comments command",
        ),
        pytest.param(
            "# comment 1\n    # comment 2\n# comment 3\n        # comment 4\n   test1 foo",
            [(CMD1, ("foo",), {}, 5)],
            id="comments2 command",
        ),
        pytest.param(
            'test1 key="v a l u e"\n',
            [(CMD1, (), {"key": "v a l u e"}, 1)],
            id="kwarg_with_ws_and_dq",
        ),
        pytest.param(
            'test1 key="v a l u e"',
            [(CMD1, (), {"key": "v a l u e"}, 1)],
            id="kwarg_with_ws_and_dq no_nl",
        ),
        pytest.param(
            "test1 key='v a l u e'\n",
            [(CMD1, (), {"key": "v a l u e"}, 1)],
            id="kwarg_with_ws_and_sq",
        ),
        pytest.param(
            "test1 key='v a l u e'",
            [(CMD1, (), {"key": "v a l u e"}, 1)],
            id="kwarg_with_ws_and_sq no_nl",
        ),
        pytest.param(
            "test1 key=<<<<foo\nbar\nbaz>>>>\n",
            [(CMD1, (), {"key": "foo\nbar\nbaz"}, 1)],
            id="long multiline string",
        ),
        pytest.param(
            "test1 key=<<<<foo\nbar\nbaz>>>>",
            [(CMD1, (), {"key": "foo\nbar\nbaz"}, 1)],
            id="long multiline string no_nl",
        ),
    ],
)
def test_parser(parser, test_input, expected):
    """Test parsing of lines."""
    _setup_commands(parser)

    # parse_and_verify_string is injected into Parser by conftest.py!
    parser.parse_and_verify_string(test_input, "", expected)


# Error cases:
@pytest.mark.parametrize(
    "test_input",
    [
        pytest.param("test1 key=\n", id="kwarg without value"),
        pytest.param("test1 key=", id="kwarg without value no_nl"),
        pytest.param("foobarXXXXYYYYY test", id="unknown command"),
        pytest.param("test!1\n", id="invalid char in command"),
        pytest.param("1test\n", id="command starts with number"),
        pytest.param("test1 'baaarrrr  \n", id="missing sq"),
        pytest.param('test1 "baaarrrr  \n', id="missing dq"),
        pytest.param("test1 ke!y=value\n", id="invalid kwarg key"),
        pytest.param("test1 2key=value\n", id="kwarg key starts with number"),
        pytest.param("test1 key=<<<<value\n", id="unterminated ml kwvalue"),
        pytest.param("test1 <<<<value\n", id="unterminated ml arg"),
        pytest.param("test1 key=<<<<value", id="unterminated ml kwvalue no_nl"),
        pytest.param("test1 <<<<value", id="unterminated ml arg no_nl"),
    ],
)
def test_parse_errors(parser, test_input):
    """Test parse errors."""
    _setup_commands(parser)
    with pytest.raises(ParseError):
        parser.parse_and_verify_string(test_input, "", [])
