#!/usr/bin/python
"""Test for the Parser class in cleanroom.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import cleanroom.testutils as tu
import cleanroom.command as cmd
import cleanroom.exceptions as ex
import cleanroom.parser as parser
import cleanroom.printer as printer

import unittest


class DummyCommand(cmd.Command):
    """Dummy command implementation."""

    def __init__(self, name):
        """Constructor."""
        super().__init__(name, help='test')

    def validate_arguments(self, location, *args, **kwargs):
        """Accept all arguments."""
        return None


class ParserTest(tu.BaseParserTest, unittest.TestCase):
    """Test for Parser class of cleanroom."""

    def setUp(self):
        """Set up method."""
        printer.Printer._instance = None  # Force printer to None

        self._create_and_setup_parser(5)

        self._cmd1 = 'test1'
        self._cmd2 = 'test2'

        parser.Parser._commands[self._cmd1] \
            = (DummyCommand(self._cmd1), '<builtin>/1')
        parser.Parser._commands[self._cmd2] \
            = (DummyCommand(self._cmd2), '<builtin>/2')

    # No command (WS or comment only):
    def test_comment(self):
        """Test a simple comment."""
        self._verify('# test comment\n', [])

    def test_comment_with_leading_ws(self):
        """Test a simple comment with leading whitespace."""
        self._verify(' \t  # test comment\n', [])

    def test_comment_without_nl(self):
        """Test a simple comment without new line character."""
        self._verify(' # test comment', [])

    def test_ws_only(self):
        """Test a whitespace only line."""
        self._verify(' \t \t \n', [])

    def test_nl_only(self):
        """Test a new line only line."""
        self._verify('\n', [])

    def test_empty_line(self):
        """Test an empty line."""
        self._verify('', [])

    # Command only:
    def test_command(self):
        """Test a command."""
        self._verify('test1\n', [(self._cmd1, (), {}, 1)])

    def test_command_no_nl(self):
        """Test a command without new line."""
        self._verify('test1', [(self._cmd1, (), {}, 1)])

    def test_command_leading_ws(self):
        """Test a command with leading whitespace."""
        self._verify(' \t test1\n', [(self._cmd1, (), {}, 1)])

    def test_command_leading_ws_no_nl(self):
        """Test a command with leading whitespace and no new line."""
        self._verify(' \ttest1', [(self._cmd1, (), {}, 1)])

    def test_command_comment(self):
        """Test a command directly followed by a comment."""
        self._verify('test1# comment\n', [(self._cmd1, (), {}, 1)])

    def test_command_ws_comment(self):
        """Test a command followed by a comment."""
        self._verify('test1   # comment\n', [(self._cmd1, (), {}, 1)])

    # command with arguments:
    def test_command_one_arg(self):
        """Test a command with one argument."""
        self._verify(' test1  arg1 \n', [(self._cmd1, ('arg1',), {}, 1)])

    def test_command_one_int(self):
        """Test a command with one argument 42."""
        self._verify(' test1  42 \n', [(self._cmd1, (42,), {}, 1)])

    def test_command_one_octal(self):
        """Test a command with one argument 0o42."""
        self._verify(' test1  0o42 \n', [(self._cmd1, (34,), {}, 1)])

    def test_command_one_octal2(self):
        """Test a command with one argument 042."""
        self._verify(' test1  042 \n', [(self._cmd1, (34,), {}, 1)])

    def test_command_one_hex(self):
        """Test a command with one argument 0xf8."""
        self._verify(' test1  0xf8 \n', [(self._cmd1, (248,), {}, 1)])

    def test_command_one_true(self):
        """Test a command with one argument True."""
        self._verify(' test1  True \n', [(self._cmd1, (True,), {}, 1)])

    def test_command_one_false(self):
        """Test a command with one argument False."""
        self._verify(' test1  False \n', [(self._cmd1, (False,), {}, 1)])

    def test_command_one_none(self):
        """Test a command with one argument None."""
        self._verify(' test1  None \n', [(self._cmd1, (None,), {}, 1)])

    def test_command_one_int_string(self):
        """Test a command with one argument 42."""
        self._verify(' test1  "42" \n', [(self._cmd1, ("42",), {}, 1)])

    def test_command_one_octal_string(self):
        """Test a command with one argument 0o42."""
        self._verify(' test1  "0o42" \n', [(self._cmd1, ("0o42",), {}, 1)])

    def test_command_one_octal2_string(self):
        """Test a command with one argument 042 string."""
        self._verify(' test1  "042" \n', [(self._cmd1, ("042",), {}, 1)])

    def test_command_one_hex_string(self):
        """Test a command with one argument 0xf8 string."""
        self._verify(' test1  "0xf8" \n', [(self._cmd1, ("0xf8",), {}, 1)])

    def test_command_one_true_string(self):
        """Test a command with one argument True string."""
        self._verify(' test1  "True" \n', [(self._cmd1, ("True",), {}, 1)])

    def test_command_one_false_string(self):
        """Test a command with one argument False string."""
        self._verify(' test1  \'False\' \n', [(self._cmd1, ("False",), {}, 1)])

    def test_command_one_none_string(self):
        """Test a command with one argument None string."""
        self._verify(' test1  "None" \n', [(self._cmd1, ("None",), {}, 1)])

    def test_command_two_args(self):
        """Test a command with two arguments."""
        self._verify('test1  arg1  arg2\n',
                     [(self._cmd1, ('arg1', 'arg2'), {}, 1)])

    def test_command_two_args_no_nl(self):
        """Test a command two arguments and no new line."""
        self._verify('test1   arg1  arg2',
                     [(self._cmd1, ('arg1', 'arg2'), {}, 1)])

    def test_command_one_arg_no_nl(self):
        """Test a command with one argument and no new line."""
        self._verify('test1  arg1', [(self._cmd1, ('arg1',), {}, 1)])

    # Command with string arguments:
    def test_command_sq_empty_arg(self):
        """Test a command with one argument and no new line."""
        self._verify('test1 \'\' arg', [(self._cmd1, ('', 'arg'), {}, 1)])

    def test_command_dq_empty_arg(self):
        """Test a command with one argument and no new line."""
        self._verify('test1 "" arg', [(self._cmd1, ('', 'arg'), {}, 1)])

    def test_command_sq_arg(self):
        """Test a command with one argument in single quotes."""
        self._verify('test1 \' arg 42\'', [(self._cmd1, (' arg 42',), {}, 1)])

    def test_command_dq_arg(self):
        """Test a command with one argument in double quotes."""
        self._verify('test1 " arg 42"', [(self._cmd1, (' arg 42',), {}, 1)])

    def test_command_sq_arg_with_comment(self):
        """Test a command with one argument in single quotes."""
        self._verify('test1 \' arg # 42\'',
                     [(self._cmd1, (' arg # 42',), {}, 1)])

    def test_command_dq_arg_with_comment(self):
        """Test a command with one argument in double quotes."""
        self._verify('test1 " arg # 42"',
                     [(self._cmd1, (' arg # 42',), {}, 1)])

    def test_command_sq_arg_with_dq(self):
        """Test a command with one argument in single quotes (dq)."""
        self._verify('test1 \' arg "42"\'',
                     [(self._cmd1, (' arg "42"',), {}, 1)])

    def test_command_dq_arg_with_sq(self):
        """Test a command with one argument in double quotes (sq)."""
        self._verify('test1 " arg \'42\'"',
                     [(self._cmd1, (' arg \'42\'',), {}, 1)])

    def test_command_sq_arg_with_one_dq(self):
        """Test a command with argument in single quotes (one dq)."""
        self._verify('test1 \' arg "42\'',
                     [(self._cmd1, (' arg "42',), {}, 1)])

    def test_command_dq_arg_with_one_sq(self):
        """Test a command with argument in double quotes (one sq)."""
        self._verify('test1 " arg \'42"',
                     [(self._cmd1, (' arg \'42',), {}, 1)])

    def test_command_arg_with_escapes(self):
        """Test a command with argument with escaped chars."""
        self._verify('test1 arg\ \ 42\ "',
                     [(self._cmd1, ('arg  42 "',), {}, 1)])

    def test_command_escaped_ws(self):
        """Test a command two arguments and no new line."""
        self._verify('test1  \ ',
                     [(self._cmd1, (' ',), {}, 1)])

    def test_command_escaped_sq_argument(self):
        """Test a command with argument surrounded by sq."""
        self._verify('test1  \\\'arg1\\\' ',
                     [(self._cmd1, ('\'arg1\'',), {}, 1)])

    def test_command_escaped_dq_argument(self):
        """Test a command with argument surrounded by dq."""
        self._verify('test1  \\"arg1\\" ',
                     [(self._cmd1, ('"arg1"',), {}, 1)])

    def test_command_escaped_sq_kw_argument(self):
        """Test a command with kwargument value surrounded by sq."""
        self._verify('test1  value=\\\'arg1\\\' ',
                     [(self._cmd1, (), {'value': '\'arg1\''}, 1)])

    def test_command_escaped_dq_kw_argument(self):
        """Test a command with kwargument value surrounded by dq."""
        self._verify('test1  value=\\"arg1\\" ',
                     [(self._cmd1, (), {'value': '"arg1"'}, 1)])

    def test_command_escaped_equal_in_kw_argument(self):
        """Test a command with kwargument value containing '='."""
        self._verify('test1  value=test=key ',
                     [(self._cmd1, (), {'value': 'test=key'}, 1)])

    # Special keywords:
    def test_command_with_kw_true(self):
        """Test a command with kwargument value of True."""
        self._verify('test1  value=True ',
                     [(self._cmd1, (), {'value': True}, 1)])

    def test_command_with_kw_false(self):
        """Test a command with kwargument value of False."""
        self._verify('test1  value=False ',
                     [(self._cmd1, (), {'value': False}, 1)])

    def test_command_with_kw_none(self):
        """Test a command with kwargument value of None."""
        self._verify('test1  value=None ',
                     [(self._cmd1, (), {'value': None}, 1)])

    def test_command_with_kw_int(self):
        """Test a command with kwargument value of 42."""
        self._verify('test1  value=42 ',
                     [(self._cmd1, (), {'value': 42}, 1)])

    def test_command_with_kw_octal(self):
        """Test a command with kwargument value of 0o42."""
        self._verify('test1  value=0o42 ',
                     [(self._cmd1, (), {'value': 34}, 1)])

    def test_command_with_kw_octal2(self):
        """Test a command with kwargument value of 042."""
        self._verify('test1  value=042 ',
                     [(self._cmd1, (), {'value': 34}, 1)])

    def test_command_with_kw_hex(self):
        """Test a command with kwargument value of 0xf8."""
        self._verify('test1  value=0xf8 ',
                     [(self._cmd1, (), {'value': 248}, 1)])

    def test_command_with_kw_true_sq_string(self):
        """Test a command with kwargument value of 'True'."""
        self._verify('test1  value=\'True\' ',
                     [(self._cmd1, (), {'value': 'True'}, 1)])

    def test_command_with_kw_false_sq_string(self):
        """Test a command with kwargument value of 'False'."""
        self._verify('test1  value=\'False\' ',
                     [(self._cmd1, (), {'value': 'False'}, 1)])

    def test_command_with_kw_none_sq_string(self):
        """Test a command with kwargument value of None."""
        self._verify('test1  value=\'None\' ',
                     [(self._cmd1, (), {'value': 'None'}, 1)])

    def test_command_with_kw_int_sq_string(self):
        """Test a command with kwargument value of '42'."""
        self._verify('test1  value=\'42\' ',
                     [(self._cmd1, (), {'value': '42'}, 1)])

    def test_command_with_kw_true_dq_string(self):
        """Test a command with kwargument value of "True"."""
        self._verify('test1  value="True" ',
                     [(self._cmd1, (), {'value': 'True'}, 1)])

    def test_command_with_kw_false_dq_string(self):
        """Test a command with kwargument value of "False"."""
        self._verify('test1  value="False" ',
                     [(self._cmd1, (), {'value': 'False'}, 1)])

    def test_command_with_kw_none_dq_string(self):
        """Test a command with kwargument value of "None"."""
        self._verify('test1  value="None" ',
                     [(self._cmd1, (), {'value': 'None'}, 1)])

    def test_command_with_kw_int_dq_string(self):
        """Test a command with kwargument value of "42"."""
        self._verify('test1  value="42" ',
                     [(self._cmd1, (), {'value': '42'}, 1)])

    def test_command_with_kw_true_ml_string(self):
        """Test a command with kwargument value of <<<<True>>>>."""
        self._verify('test1  value=<<<<True>>>> ',
                     [(self._cmd1, (), {'value': 'True'}, 1)])

    def test_command_with_kw_false_ml_string(self):
        """Test a command with kwargument value of <<<<False>>>>."""
        self._verify('test1  value=<<<<False>>>> ',
                     [(self._cmd1, (), {'value': 'False'}, 1)])

    def test_command_with_kw_none_ml_string(self):
        """Test a command with kwargument value of <<<<None>>>>."""
        self._verify('test1  value=<<<<None>>>> ',
                     [(self._cmd1, (), {'value': 'None'}, 1)])

    def test_command_with_kw_int_ml_string(self):
        """Test a command with kwargument value of <<<<42>>>>."""
        self._verify('test1  value=<<<<42>>>> ',
                     [(self._cmd1, (), {'value': '42'}, 1)])

    # Multiline:
    def test_command_empty_ml(self):
        """Test a command with empty ml argument."""
        self._verify('test1 <<<<>>>>', [(self._cmd1, ('',), {}, 1)])

    def test_command_arg_ml_arg(self):
        """Test a command with an arg, a ml arg and another arg."""
        self._verify('test1 arg1 <<<<foo>>>> arg2',
                     [(self._cmd1, ('arg1', 'foo', 'arg2'), {}, 1)])

    def test_command_two_line_ml(self):
        """Test a command with a two line ml argument."""
        self._verify(('test1 arg1 <<<<foo\n', 'bar>>>> arg2\n'),
                     [(self._cmd1, ('arg1', 'foo\nbar', 'arg2'), {}, 1)])

    def test_command_three_line_ml(self):
        """Test a command with a three line ml argument."""
        self._verify(('test1 arg1 <<<<foo\n', 'bar\n', 'baz>>>> arg2\n'),
                     [(self._cmd1, ('arg1', 'foo\nbar\nbaz', 'arg2'), {}, 1)])

    def test_command_two_fused_ml(self):
        """Test a command with two fused ml arguments."""
        self._verify(('test1 \'arg1\'<<<<foo>>>><<<<\n',
                      'bar\n', 'baz>>>>"arg2" # foobar\n'),
                     [(self._cmd1,
                       ('arg1', 'foo', '\nbar\nbaz', 'arg2'), {}, 1)])

    def test_comment_command(self):
        """Test a comment followed by a command."""
        self._verify(('# Foo bar\n',
                      '\n',
                      '    # ignore this comment\n',
                      '   test2 foo'),
                     [(self._cmd2, ('foo',), {}, 4)])

    def test_multiline_command(self):
        """Test a multiline command."""
        self._verify(('test1 \'arg1\'\n',
                      '    test2\n',
                      '\n',
                      '    # ignore this comment\n',
                      '      baz "arg2" # foobar\n',
                      '   test2 foo'),
                     [(self._cmd1, ('arg1', 'test2', 'baz', 'arg2'), {}, 1),
                      (self._cmd2, ('foo',), {}, 6)])

    def test_multiline_arg_command_command(self):
        """Test a multiline argument command followed by command."""
        self._verify(('test1 <<<<line1\n',
                      '  line2\n',
                      '\n',
                      ' line3>>>>\n',
                      '   test2 foo'),
                     [(self._cmd1, ('line1\n  line2\n\n line3',), {}, 1),
                      (self._cmd2, ('foo',), {}, 5)])

    def test_empty_lines_command(self):
        """Test some empty lines followed by command."""
        self._verify(('\n',
                      '  \n',
                      '\n',
                      ' \n',
                      '   test1 foo'),
                     [(self._cmd1, ('foo',), {}, 5)])

    def test_comments_command(self):
        """Test some comments followed by command."""
        self._verify(('# comment 1\n',
                      '# comment 2\n',
                      '\n',
                      ' \n',
                      '   test1 foo'),
                     [(self._cmd1, ('foo',), {}, 5)])

    def test_comments2_command(self):
        """Test some more comments followed by command."""
        self._verify(('# comment 1\n',
                      '    # comment 2\n',
                      '# comment 3\n',
                      '        # comment 4\n',
                      '   test1 foo'),
                     [(self._cmd1, ('foo',), {}, 5)])

    def test_multiline_command_with_extra_indent(self):
        """Test a indented multiline command."""
        self._verify(('  test1 \'arg1\'\n',
                      '      test2\n',
                      '\n',
                      '      # ignore this comment\n',
                      '        baz "arg2" # foobar\n',
                      '     test2 foo'),
                     [(self._cmd1, ('arg1', 'test2', 'baz', 'arg2'), {}, 1),
                      (self._cmd2, ('foo',), {}, 6)])

    def test_keyword_argument(self):
        """Test a command with a kw argument."""
        self._verify(('test1 key=value\n'),
                     [(self._cmd1, (), {'key': 'value'}, 1)])

    def test_keyword_argument_no_nl(self):
        """Test a command with a kw argument and no nl."""
        self._verify(('test1 key=value'),
                     [(self._cmd1, (), {'key': 'value'}, 1)])

    def test_keyword_argument_as_string(self):
        """Test a command with a string resembling a kw argument."""
        self._verify(('test1 "key=value"\n'),
                     [(self._cmd1, ('key=value',), {}, 1)])

    def test_keyword_argument_as_string_no_nl(self):
        """Test a command with a string containing a kw argument (no NL)."""
        self._verify(('test1 "key=value"'),
                     [(self._cmd1, ('key=value',), {}, 1)])

    def test_keyword_argument_with_ws(self):
        """Test a command with a kw argument containing ws."""
        self._verify(('test1 key="v a l u e"\n'),
                     [(self._cmd1, (), {'key': 'v a l u e'}, 1)])

    def test_keyword_argument_with_ws_no_nl(self):
        """Test a command with a kw argument containing ws (no NL)."""
        self._verify(('test1 key="v a l u e"'),
                     [(self._cmd1, (), {'key': 'v a l u e'}, 1)])

    def test_keyword_argument_with_ws_sq(self):
        """Test a command with a kw argument containing ws (sq)."""
        self._verify(('test1 key=\'v a l u e\'\n'),
                     [(self._cmd1, (), {'key': 'v a l u e'}, 1)])

    def test_keyword_argument_with_ws_sq_no_nl(self):
        """Test a command with a kw argument containing ws (sq, no NL)."""
        self._verify(('test1 key=\'v a l u e\''),
                     [(self._cmd1, (), {'key': 'v a l u e'}, 1)])

    def test_keyword_argument_with_ml_argument(self):
        """Test a command with a ml kw argument."""
        self._verify(('test1 key=<<<<v a l u e>>>>\n'),
                     [(self._cmd1, (), {'key': 'v a l u e'}, 1)])

    def test_keyword_argument_with_ml_argument_no_nl(self):
        """Test a command with a ml kw argument containing ws (no NL)."""
        self._verify(('test1 key=<<<<v a l u e>>>>'),
                     [(self._cmd1, (), {'key': 'v a l u e'}, 1)])

    def test_keyword_argument_with_empty_ml_argument(self):
        """Test a command with an empty kw argument."""
        self._verify(('test1 key=<<<<>>>>\n'),
                     [(self._cmd1, (), {'key': ''}, 1)])

    def test_keyword_argument_with_empty_ml_argument_no_nl(self):
        """Test a command with an empty kw argument (no NL)."""
        self._verify(('test1 key=<<<<>>>>'),
                     [(self._cmd1, (), {'key': ''}, 1)])

    def test_keyword_argument_with_long_ml_argument(self):
        """Test a command with a long kw argument."""
        self._verify(('test1 key=<<<<foo\n',
                      'bar\n',
                      'baz>>>>\n'),
                     [(self._cmd1, (), {'key': 'foo\nbar\nbaz'}, 1)])

    def test_keyword_argument_with_long_ml_argument_no_nl(self):
        """Test a command with a long kw argument (no NL)."""
        self._verify(('test1 key=<<<<foo\n',
                      'bar\n',
                      'baz>>>>'),
                     [(self._cmd1, (), {'key': 'foo\nbar\nbaz'}, 1)])

    # Error cases:
    def test_keyword_argument_without_value(self):
        """Test a command with a kw argument without value."""
        with self.assertRaises(ex.ParseError):
            self._parse('test1 key=\n')

    def test_keyword_argument_without_value_no_nl(self):
        """Test a command with a kw argument without value (no NL)."""
        with self.assertRaises(ex.ParseError):
            self._parse('test1 key=')

    def test_assert_on_unknown_command(self):
        """Test an invalid command."""
        with self.assertRaises(ex.ParseError):
            self._parse('   foobar test\n')

    def test_assert_on_invalid_char_in_command(self):
        """Test an command containing an unexpected character."""
        with self.assertRaises(ex.ParseError):
            self._parse('  !test1\n')

    def test_assert_on_missing_sq(self):
        """Test an argument with missing '."""
        with self.assertRaises(ex.ParseError):
            self._parse('  test1 \'fooo  \n')

    def test_assert_on_missing_dq(self):
        """Test an argument with missing "."""
        with self.assertRaises(ex.ParseError):
            self._parse('  test1 "baaarrrr  \n')

    def test_assert_on_invalid_keyword_argument(self):
        """Test an argument with missing "."""
        with self.assertRaises(ex.ParseError):
            self._parse('  test1 ke!y=value  \n')

    def test_assert_on_invalid_keyword_argument2(self):
        """Test an argument with missing "."""
        with self.assertRaises(ex.ParseError):
            self._parse('  test1 2key=value  \n')


if __name__ == '__main__':
    unittest.main()
