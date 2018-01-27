#!/usr/bin/python
"""Test for the Parser class in cleanroom.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

import cleanroom.command as cmd
import cleanroom.context as context
import cleanroom.exceptions as exceptions
import cleanroom.parser as parser

import unittest


class TestCommand(cmd.Command):
    """Dummy command implementation."""

    pass


class ParserTest(unittest.TestCase):
    """Test for Parser class of cleanroom."""

    def setUp(self):
        """Set up method."""
        self.ctx = context.Context.Create(5)
        self.parser = parser.Parser(self.ctx)

        self._cmd1name = 'test1'
        self._cmd1 = TestCommand()

        self._cmd2name = 'test2'
        self._cmd2 = TestCommand()

        parser.Parser._commands[self._cmd1name] = (self._cmd1, '<builtin>/1')
        parser.Parser._commands[self._cmd2name] = (self._cmd2, '<builtin>/2')

    def _parse(self, data):
        """Call Parser._parse_lines and map the result."""
        result = None
        input = (data,) if type(data) is str else data
        for exec_object in self.parser._parse_lines(input):
            if result:
                self.assertTrue(False)
            if exec_object:
                result = exec_object

        return (result._command, result._args) if result else ()

    def _verify(self, data, expected):
        """Verify one line of input to the Parser."""
        result = self._parse(data)
        self.assertEqual(result, expected)

    # No command (WS or comment only):
    def test_comment(self):
        """Test a simple comment."""
        self._verify('# test comment\n', ())

    def test_comment_with_leading_ws(self):
        """Test a simple comment with leading whitespace."""
        self._verify(' \t  # test comment\n', ())

    def test_comment_without_nl(self):
        """Test a simple comment without new line character."""
        self._verify(' # test comment', ())

    def test_ws_only(self):
        """Test a whitespace only line."""
        self._verify(' \t \t \n', ())

    def test_nl_only(self):
        """Test a new line only line."""
        self._verify('\n', ())

    def test_empty_line(self):
        """Test an empty line."""
        self._verify('', ())

    # Command only:
    def test_command(self):
        """Test a command."""
        self._verify('test1\n', (self._cmd1, ()))

    def test_command_no_nl(self):
        """Test a command without new line."""
        self._verify('test1', (self._cmd1, ()))

    def test_command_leading_ws(self):
        """Test a simple command with leading whitespace."""
        self._verify(' \t test1\n', (self._cmd1, ()))

    def test_command_leading_ws_no_nl(self):
        """Test a simple command with leading whitespace and no new line."""
        self._verify(' \ttest1', (self._cmd1, ()))

    def test_command_comment(self):
        """Test a simple command directly followed by a comment."""
        self._verify('test1# comment\n', (self._cmd1, ()))

    def test_command_ws_comment(self):
        """Test a simple command followed by a comment."""
        self._verify('test1   # comment\n', (self._cmd1, ()))

    # command with arguments:
    def test_command_one_arg(self):
        """Test a simple command with one argument."""
        self._verify(' test1  arg1 \n', (self._cmd1, ('arg1',)))

    def test_command_two_args(self):
        """Test a simple command with two arguments."""
        self._verify('test1  arg1  arg2\n',
                     (self._cmd1, ('arg1', 'arg2')))

    def test_command_two_args_no_nl(self):
        """Test a simple command two arguments and no new line."""
        self._verify('test1   arg1  arg2',
                     (self._cmd1, ('arg1', 'arg2')))

    def test_command_one_arg_no_nl(self):
        """Test a simple command with one argument and no new line."""
        self._verify('test1  arg1', (self._cmd1, ('arg1',)))

    # Command with string arguments:
    def test_command_sq_empty_arg(self):
        """Test a simple command with one argument and no new line."""
        self._verify('test1 \'\' arg', (self._cmd1, ('', 'arg')))

    def test_command_dq_empty_arg(self):
        """Test a simple command with one argument and no new line."""
        self._verify('test1 "" arg', (self._cmd1, ('', 'arg')))

    def test_command_sq_arg(self):
        """Test a simple command with one argument in single quotes."""
        self._verify('test1 \' arg 42\'', (self._cmd1, (' arg 42',)))

    def test_command_dq_arg(self):
        """Test a simple command with one argument in double quotes."""
        self._verify('test1 " arg 42"', (self._cmd1, (' arg 42',)))

    def test_command_sq_arg_with_comment(self):
        """Test a simple command with one argument in single quotes."""
        self._verify('test1 \' arg # 42\'', (self._cmd1, (' arg # 42',)))

    def test_command_dq_arg_with_comment(self):
        """Test a simple command with one argument in double quotes."""
        self._verify('test1 " arg # 42"', (self._cmd1, (' arg # 42',)))

    def test_command_sq_arg_with_dq(self):
        """Test a simple command with one argument in single quotes (dq)."""
        self._verify('test1 \' arg "42"\'', (self._cmd1, (' arg "42"',)))

    def test_command_dq_arg_with_sq(self):
        """Test a simple command with one argument in double quotes (sq)."""
        self._verify('test1 " arg \'42\'"', (self._cmd1, (' arg \'42\'',)))

    def test_command_sq_arg_with_one_dq(self):
        """Test a simple command with argument in single quotes (one dq)."""
        self._verify('test1 \' arg "42\'', (self._cmd1, (' arg "42',)))

    def test_command_dq_arg_with_one_sq(self):
        """Test a simple command with argument in double quotes (one sq)."""
        self._verify('test1 " arg \'42"', (self._cmd1, (' arg \'42',)))

    def test_command_arg_with_escapes(self):
        """Test a simple command with argument with escaped chars."""
        self._verify('test1 arg\ \ 42\ "', (self._cmd1, ('arg  42 "',)))

    def test_command_escaped_ws(self):
        """Test a simple command two arguments and no new line."""
        self._verify('test1  \ ',
                     (self._cmd1, (' ',)))

    # Multiline:
    def test_command_empty_ml(self):
        """Test a simple command with empty ml argument."""
        self._verify('test1 <<<<>>>>',
                     (self._cmd1, ('',)))

    def test_command_arg_ml_arg(self):
        """Test a simple command with an arg, a ml arg and another arg."""
        self._verify('test1 arg1 <<<<foo>>>> arg2',
                     (self._cmd1, ('arg1', 'foo', 'arg2')))

    def test_command_two_line_ml(self):
        """Test a simple command with a two line ml argument."""
        self._verify(('test1 arg1 <<<<foo\n', 'bar>>>> arg2\n'),
                     (self._cmd1, ('arg1', 'foo\nbar', 'arg2')))

    def test_command_three_line_ml(self):
        """Test a simple command with a three line ml argument."""
        self._verify(('test1 arg1 <<<<foo\n', 'bar\n', 'baz>>>> arg2\n'),
                     (self._cmd1, ('arg1', 'foo\nbar\nbaz', 'arg2')))

    def test_command_two_fused_ml(self):
        """Test a simple command with two fused ml arguments."""
        self._verify(('test1 \'arg1\'<<<<foo>>>><<<<\n',
                      'bar\n', 'baz>>>>"arg2" # foobar\n'),
                     (self._cmd1, ('arg1', 'foo', '\nbar\nbaz', 'arg2')))

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


if __name__ == '__main__':
    unittest.main()
