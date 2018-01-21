#!/usr/bin/python

import cleanroom.context as context
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

    def test_comments_and_empty_lines(self):
        data = ['# test comment 1\n',
                '   \t    # test comment 2     \n',
                '####### test comment 3 ######\n',
                ' \t \t    \n',
                '\n',
                '\t   ']

        result = list(map(lambda e : (e._name, e._args), self.parser._parse_lines(data)))
        self.assertEqual(result, [])

    def test_commands(self):
        data = ['    test1 foo bar\n',
                ' \t test2 bar\n',
                '  test2#comment\n',
                '     test1\n',
                'test1# comment 2\n',
                '   test1   \t # comment 3\n',
                'test1 baz 12345\n',
                'test2']

        result = list(map(lambda e : (e._name, e._args), self.parser._parse_lines(data)))
        self.assertEqual(result,
                         [(self._cmd1, ' foo bar\n'),
                          (self._cmd2, ' bar\n'),
                          (self._cmd2, None),
                          (self._cmd1, '\n'),
                          (self._cmd1, None),
                          (self._cmd1, '   \t # comment 3\n'),
                          (self._cmd1, ' baz 12345\n'),
                          (self._cmd2, None)])


if __name__ == '__main__':
    unittest.main()
