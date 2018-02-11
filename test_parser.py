#!/usr/bin/python
"""Test for the Parser class in cleanroom.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

import cleanroom.testutils as tu
import cleanroom.command as cmd
import cleanroom.exceptions as exceptions
import cleanroom.parser as parser

import unittest


class TestCommand(cmd.Command):
    """Dummy command implementation."""

    def __init__(self):
        """Constructor."""
        super().__init__('test', 'test')

    def validate_arguments(self, file_name, line_number, *args, **kwargs):
        """Accept all arguments."""
        return None


class ParserTest(tu.BaseParserTest, unittest.TestCase):
    """Test for Parser class of cleanroom."""

    def setUp(self):
        """Set up method."""
        self._create_and_setup_parser(5)

        self._cmd1 = 'test1'
        self._cmd2 = 'test2'

        parser.Parser._commands[self._cmd1] = (TestCommand(), '<builtin>/1')
        parser.Parser._commands[self._cmd2] = (TestCommand(), '<builtin>/2')

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
        self._verify('test1\n', [(self._cmd1, (), {})])

    def test_command_no_nl(self):
        """Test a command without new line."""
        self._verify('test1', [(self._cmd1, (), {})])

    def test_command_leading_ws(self):
        """Test a command with leading whitespace."""
        self._verify(' \t test1\n', [(self._cmd1, (), {})])

    def test_command_leading_ws_no_nl(self):
        """Test a command with leading whitespace and no new line."""
        self._verify(' \ttest1', [(self._cmd1, (), {})])

    def test_command_comment(self):
        """Test a command directly followed by a comment."""
        self._verify('test1# comment\n', [(self._cmd1, (), {})])

    def test_command_ws_comment(self):
        """Test a command followed by a comment."""
        self._verify('test1   # comment\n', [(self._cmd1, (), {})])

    # command with arguments:
    def test_command_one_arg(self):
        """Test a command with one argument."""
        self._verify(' test1  arg1 \n', [(self._cmd1, ('arg1',), {})])

    def test_command_two_args(self):
        """Test a command with two arguments."""
        self._verify('test1  arg1  arg2\n',
                     [(self._cmd1, ('arg1', 'arg2'), {})])

    def test_command_two_args_no_nl(self):
        """Test a command two arguments and no new line."""
        self._verify('test1   arg1  arg2',
                     [(self._cmd1, ('arg1', 'arg2'), {})])

    def test_command_one_arg_no_nl(self):
        """Test a command with one argument and no new line."""
        self._verify('test1  arg1', [(self._cmd1, ('arg1',), {})])

    # Command with string arguments:
    def test_command_sq_empty_arg(self):
        """Test a command with one argument and no new line."""
        self._verify('test1 \'\' arg', [(self._cmd1, ('', 'arg'), {})])

    def test_command_dq_empty_arg(self):
        """Test a command with one argument and no new line."""
        self._verify('test1 "" arg', [(self._cmd1, ('', 'arg'), {})])

    def test_command_sq_arg(self):
        """Test a command with one argument in single quotes."""
        self._verify('test1 \' arg 42\'', [(self._cmd1, (' arg 42',), {})])

    def test_command_dq_arg(self):
        """Test a command with one argument in double quotes."""
        self._verify('test1 " arg 42"', [(self._cmd1, (' arg 42',), {})])

    def test_command_sq_arg_with_comment(self):
        """Test a command with one argument in single quotes."""
        self._verify('test1 \' arg # 42\'', [(self._cmd1, (' arg # 42',), {})])

    def test_command_dq_arg_with_comment(self):
        """Test a command with one argument in double quotes."""
        self._verify('test1 " arg # 42"', [(self._cmd1, (' arg # 42',), {})])

    def test_command_sq_arg_with_dq(self):
        """Test a command with one argument in single quotes (dq)."""
        self._verify('test1 \' arg "42"\'', [(self._cmd1, (' arg "42"',), {})])

    def test_command_dq_arg_with_sq(self):
        """Test a command with one argument in double quotes (sq)."""
        self._verify('test1 " arg \'42\'"',
                     [(self._cmd1, (' arg \'42\'',), {})])

    def test_command_sq_arg_with_one_dq(self):
        """Test a command with argument in single quotes (one dq)."""
        self._verify('test1 \' arg "42\'', [(self._cmd1, (' arg "42',), {})])

    def test_command_dq_arg_with_one_sq(self):
        """Test a command with argument in double quotes (one sq)."""
        self._verify('test1 " arg \'42"', [(self._cmd1, (' arg \'42',), {})])

    def test_command_arg_with_escapes(self):
        """Test a command with argument with escaped chars."""
        self._verify('test1 arg\ \ 42\ "', [(self._cmd1, ('arg  42 "',), {})])

    def test_command_escaped_ws(self):
        """Test a command two arguments and no new line."""
        self._verify('test1  \ ',
                     [(self._cmd1, (' ',), {})])

    # Multiline:
    def test_command_empty_ml(self):
        """Test a command with empty ml argument."""
        self._verify('test1 <<<<>>>>', [(self._cmd1, ('',), {})])

    def test_command_arg_ml_arg(self):
        """Test a command with an arg, a ml arg and another arg."""
        self._verify('test1 arg1 <<<<foo>>>> arg2',
                     [(self._cmd1, ('arg1', 'foo', 'arg2'), {})])

    def test_command_two_line_ml(self):
        """Test a command with a two line ml argument."""
        self._verify(('test1 arg1 <<<<foo\n', 'bar>>>> arg2\n'),
                     [(self._cmd1, ('arg1', 'foo\nbar', 'arg2'), {})])

    def test_command_three_line_ml(self):
        """Test a command with a three line ml argument."""
        self._verify(('test1 arg1 <<<<foo\n', 'bar\n', 'baz>>>> arg2\n'),
                     [(self._cmd1, ('arg1', 'foo\nbar\nbaz', 'arg2'), {})])

    def test_command_two_fused_ml(self):
        """Test a command with two fused ml arguments."""
        self._verify(('test1 \'arg1\'<<<<foo>>>><<<<\n',
                      'bar\n', 'baz>>>>"arg2" # foobar\n'),
                     [(self._cmd1, ('arg1', 'foo', '\nbar\nbaz', 'arg2'), {})])

    def test_multiline_command(self):
        """Test a multiline command."""
        self._verify(('test1 \'arg1\'\n',
                      '    test2\n',
                      '\n',
                      '    # ignore this comment\n',
                      '      baz "arg2" # foobar\n',
                      '   test2 foo'),
                     [(self._cmd1, ('arg1', 'test2', 'baz', 'arg2'), {}),
                      (self._cmd2, ('foo',), {})])

    def test_multiline_command_with_extra_indent(self):
        """Test a indented multiline command."""
        self._verify(('  test1 \'arg1\'\n',
                      '      test2\n',
                      '\n',
                      '      # ignore this comment\n',
                      '        baz "arg2" # foobar\n',
                      '     test2 foo'),
                     [(self._cmd1, ('arg1', 'test2', 'baz', 'arg2'), {}),
                      (self._cmd2, ('foo',), {})])

    def test_keyword_argument(self):
        """Test a command with a kw argument."""
        self._verify(('test1 key=value\n'),
                     [(self._cmd1, (), {'key': 'value'})])

    def test_keyword_argument_no_nl(self):
        """Test a command with a kw argument and no nl."""
        self._verify(('test1 key=value'),
                     [(self._cmd1, (), {'key': 'value'})])

    def test_keyword_argument_as_string(self):
        """Test a command with a string resembling a kw argument."""
        self._verify(('test1 "key=value"\n'),
                     [(self._cmd1, ('key=value',), {})])

    def test_keyword_argument_as_string_no_nl(self):
        """Test a command with a string containing a kw argument (no NL)."""
        self._verify(('test1 "key=value"'),
                     [(self._cmd1, ('key=value',), {})])

    def test_keyword_argument_with_ws(self):
        """Test a command with a kw argument containing ws."""
        self._verify(('test1 key="v a l u e"\n'),
                     [(self._cmd1, (), {'key': 'v a l u e'})])

    def test_keyword_argument_with_ws_no_nl(self):
        """Test a command with a kw argument containing ws (no NL)."""
        self._verify(('test1 key="v a l u e"'),
                     [(self._cmd1, (), {'key': 'v a l u e'})])

    def test_keyword_argument_with_ws_sq(self):
        """Test a command with a kw argument containing ws (sq)."""
        self._verify(('test1 key=\'v a l u e\'\n'),
                     [(self._cmd1, (), {'key': 'v a l u e'})])

    def test_keyword_argument_with_ws_sq_no_nl(self):
        """Test a command with a kw argument containing ws (sq, no NL)."""
        self._verify(('test1 key=\'v a l u e\''),
                     [(self._cmd1, (), {'key': 'v a l u e'})])

    def test_keyword_argument_with_ml_argument(self):
        """Test a command with a ml kw argument."""
        self._verify(('test1 key=<<<<v a l u e>>>>\n'),
                     [(self._cmd1, (), {'key': 'v a l u e'})])

    def test_keyword_argument_with_ml_argument_no_nl(self):
        """Test a command with a ml kw argument containing ws (no NL)."""
        self._verify(('test1 key=<<<<v a l u e>>>>'),
                     [(self._cmd1, (), {'key': 'v a l u e'})])

    def test_keyword_argument_with_empty_ml_argument(self):
        """Test a command with an empty kw argument."""
        self._verify(('test1 key=<<<<>>>>\n'),
                     [(self._cmd1, (), {'key': ''})])

    def test_keyword_argument_with_empty_ml_argument_no_nl(self):
        """Test a command with an empty kw argument (no NL)."""
        self._verify(('test1 key=<<<<>>>>'),
                     [(self._cmd1, (), {'key': ''})])

    def test_keyword_argument_with_long_ml_argument(self):
        """Test a command with a long kw argument."""
        self._verify(('test1 key=<<<<foo\n',
                      'bar\n',
                      'baz>>>>\n'),
                     [(self._cmd1, (), {'key': 'foo\nbar\nbaz'})])

    def test_keyword_argument_with_long_ml_argument_no_nl(self):
        """Test a command with a long kw argument (no NL)."""
        self._verify(('test1 key=<<<<foo\n',
                      'bar\n',
                      'baz>>>>'),
                     [(self._cmd1, (), {'key': 'foo\nbar\nbaz'})])

    def test_keyword_argument_without_value(self):
        """Test a command with a kw argument without value."""
        self._verify(('test1 key=\n'),
                     [(self._cmd1, (), {'key': ''})])

    def test_keyword_argument_without_value_no_nl(self):
        """Test a command with a kw argument without value (no NL)."""
        self._verify(('test1 key='),
                     [(self._cmd1, (), {'key': ''})])

    # Error cases:
    def test_assert_on_unknown_command(self):
        """Test an invalid command."""
        with self.assertRaises(exceptions.ParseError):
            self._parse('   foobar test\n')

    def test_assert_on_invalid_char_in_command(self):
        """Test an command containing an unexpected character."""
        with self.assertRaises(exceptions.ParseError):
            self._parse('  !test1\n')

    def test_assert_on_missing_sq(self):
        """Test an argument with missing '."""
        with self.assertRaises(exceptions.ParseError):
            self._parse('  test1 \'fooo  \n')

    def test_assert_on_missing_dq(self):
        """Test an argument with missing "."""
        with self.assertRaises(exceptions.ParseError):
            self._parse('  test1 "baaarrrr  \n')

    def test_assert_on_invalid_keyword_argument(self):
        """Test an argument with missing "."""
        with self.assertRaises(exceptions.ParseError):
            self._parse('  test1 ke!y=value  \n')

    def test_assert_on_invalid_keyword_argument2(self):
        """Test an argument with missing "."""
        with self.assertRaises(exceptions.ParseError):
            self._parse('  test1 2key=value  \n')


if __name__ == '__main__':
    unittest.main()
