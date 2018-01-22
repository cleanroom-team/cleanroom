#!/usr/bin/python

import cleanroom.context as context
import cleanroom.exceptions as exceptions
import cleanroom.parser as parser

import unittest

class ParserTest(unittest.TestCase):
    def setUp(self):
        self.ctx = context.Context.Create(0)
        self.parser = parser.Parser(self.ctx)

        self._cmd1 = 'test1'
        self._cmd2 = 'test2'

        parser.Parser._commands[self._cmd1] = (self._cmd1, '<built-in>/1')
        parser.Parser._commands[self._cmd2] = (self._cmd2, '<built-in>/2')


    def _parse(self, data):
        return tuple(map(lambda e : (e._name, e._args), self.parser._parse_lines(data)))

    def _verify(self, data, expected):
        if data is str:
            data = tuple(data)
        result = self._parse(data)
        self.assertEqual(result, expected)


    def test_comment(self):
        self._verify('# test comment\n', ())

    def test_comment_with_leading_ws(self):
        self._verify(' \t  # test comment\n', ())

    def test_comment_without_nl(self):
        self._verify(' # test comment', ())

    def test_ws_only(self):
        self._verify(' \t \t \n', ())

    def test_nl_only(self):
        self._verify('\n', ())

    def test_empty_line(self):
        self._verify('', ())

    def test_command(self):
        self._verify('test1\n', (self._cmd1, None))

    def test_command_no_nl(self):
        self._verify('test1', (self._cmd1, None))

    def test_command_leading_ws(self):
        self._verify(' \t test1\n', (self._cmd1, None))

    def test_command_leading_ws_no_nl(self):
        self._verify(' \ttest1', (self._cmd1, None))

    def test_command_comment(self):
        self._verify('test1# comment\n', (self._cmd1, None))

    def test_command_ws_comment(self):
        self._verify('test1   # comment\n', (self._cmd1, None))

    def test_command_one_arg(self):
        self._verify(' test1  arg1 \n', (self._cmd1, ('arg1  \n'))) # FIXME

    def test_command_two_args(self):
        self._verify('test1  arg1  arg2\n', (self._cmd1, ('arg1   arg3\n'))) # FIXME

    def test_command_one_arg_no_nl(self):
        self._verify('test1  arg1', (self._cmd1, ('arg1')))

    def test_command_two_args_no_nl(self):
        self._verify('test1   arg1  arg2', (self._cmd1, ('arg1  arg2'))) # FIXME

    # FIXME Add string and multiline string tests

    # Error cases:

    def test_assert_on_unknown_command(self):
       with self.assertRaises(exceptions.ParseError):
           data = ('   foobar test\n', '')
           self.parse(data)


if __name__ == '__main__':
    unittest.main()
