#!/usr/bin/python
"""Test for the built-in commands of cleanroom.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import cleanroom.exceptions as exceptions
import cleanroom.parser as parser
import cleanroom.printer as printer
import cleanroom.testutils as tu

import tempfile
import unittest


class CommandTest(unittest.TestCase, tu.BaseParserTest):
    """Test for Parser class of cleanroom."""

    def setUp(self):
        """Set up method."""
        printer.Printer._instance = None  # Force-reset printer
        self._create_and_setup_parser(5)
        self._tempDir = tempfile.TemporaryDirectory(prefix='clrm-cmd-test',
                                                    dir='/tmp')

        work_directory = os.path.join(self._tempDir.name, 'work')
        systems_directory = os.path.join(self._tempDir.name, 'systems')

        self.ctx.set_directories(systems_directory, work_directory)

        parser.Parser.find_commands(self.ctx.commands_directory())

    def tearDown(self):
        """Tear down method."""
        self._tempDir.cleanup()

    def test_based_on(self):
        """Test based with a name."""
        self._verify('   based_on foo\n', [('based_on', ('foo',), {}, 1)])

    # Error cases:
    def test_based_on_nothing(self):
        """Test an image without name."""
        with self.assertRaises(exceptions.ParseError):
            self._parse('  based_on\n')

    def test_based_on_with_invalid_base(self):
        """Test based with invalid name."""
        with self.assertRaises(exceptions.ParseError):
            self._parse('   based_on f!oo\n')


if __name__ == '__main__':
    unittest.main()
