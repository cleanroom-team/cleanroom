#!/usr/bin/python

import cleanroom.context as context
import cleanroom.parser as parser

import unittest

class ParserTest(unittest.TestCase):
    def setUp(self):
        self.ctx = context.Context.Create(0)

    def test_comments_and_empty_lines(self):
        p = parser.Parser(self.ctx)
        self.assertIsNotNone(p)

        data =  '# test comment 1\n'
        data += '   \t    # test comment 2     \n'
        data += '####### test comment 3 ######\n'
        data += ' \t \t    \n'
        data += '\n'
        data += '\t   '

        result = p._parse_lines(data.split('\n'))
        self.assertEqual(result, [])

if __name__ == '__main__':
    unittest.main()
