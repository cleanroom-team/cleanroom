#!/usr/bin/python

import cleanroom.context as context
import cleanroom.parser as parser

import unittest

class ParserTest(unittest.TestCase):
    def setUp(self):
        self.ctx = context.Context.Create()

    def test_simple(self):
        p = parser.Parser(self.ctx)

        self.assertIsNotNone(p)

if __name__ == '__main__':
    unittest.main()
