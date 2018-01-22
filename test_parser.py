#!/usr/bin/python
"""Test for the Parser class in cleanroom.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

import cleanroom.context as context
import cleanroom.exceptions as exceptions
import cleanroom.parser as parser

import unittest


class ParserTest(unittest.TestCase):
    """Test for Parser class of cleanroom."""

    def setUp(self):
        """Set up method."""
        self.ctx = context.Context.Create(0)
        self.parser = parser.Parser(self.ctx)

        self._cmd1 = 'test1'
        self._cmd2 = 'test2'

        parser.Parser._commands[self._cmd1] = (self._cmd1, '<built-in>/1')
        parser.Parser._commands[self._cmd2] = (self._cmd2, '<built-in>/2')

    def _parse(self, data):
        """Call Parser._parse_lines and map the result."""
        result = None
        for exec_object in self.parser._parse_lines(data):
            if result:
                self.assertTrue(False)
            if exec_object:
                result = exec_object

        return (result._command, result._args) if result else ()

    def _verify(self, data, expected):
        """Verify one line of input to the Parser."""
        result = self._parse((data,))
        self.assertEqual(result, expected)

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

    def test_command(self):
        """Test a command."""
        self._verify('test1\n', (self._cmd1, None))

    def test_command_no_nl(self):
        """Test a command without new line."""
        self._verify('test1', (self._cmd1, None))

    def test_command_leading_ws(self):
        """Test a simple command with leading whitespace."""
        self._verify(' \t test1\n', (self._cmd1, None))

    def test_command_leading_ws_no_nl(self):
        """Test a simple command with leading whitespace and no new line."""
        self._verify(' \ttest1', (self._cmd1, None))

    def test_command_comment(self):
        """Test a simple command directly followed by a comment."""
        self._verify('test1# comment\n', (self._cmd1, None))

    def test_command_ws_comment(self):
        """Test a simple command followed by a comment."""
        self._verify('test1   # comment\n', (self._cmd1, None))

    def test_command_one_arg(self):
        """Test a simple command with one argument."""
        self._verify(' test1  arg1 \n', (self._cmd1, ('arg1 ')))  # FIXME

    def test_command_two_args(self):
        """Test a simple command with two arguments."""
        self._verify('test1  arg1  arg2\n',
                     (self._cmd1, ('arg1  arg2')))  # FIXME

    def test_command_one_arg_no_nl(self):
        """Test a simple command with one argument and no new line."""
        self._verify('test1  arg1', (self._cmd1, ('arg1')))

    def test_command_two_args_no_nl(self):
        """Test a simple command two arguments and no new line."""
        self._verify('test1   arg1  arg2',
                     (self._cmd1, ('arg1  arg2')))  # FIXME

    # FIXME Add string and multiline string tests

    # Error cases:

    def test_assert_on_unknown_command(self):
        """Test an invalid command."""
        with self.assertRaises(exceptions.ParseError):
            self._parse('   foobar test\n')

    def test_assert_on_invalid_char_in_command(self):
        """Test an command containing an unexpected character."""
        with self.assertRaises(exceptions.ParseError):
            self._parse('  !test1\n')


if __name__ == '__main__':
    unittest.main()
