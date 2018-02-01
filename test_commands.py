#!/usr/bin/python
"""Test for the built-in commands of cleanroom.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

import cleanroom.exceptions as exceptions
import cleanroom.parser as parser
import cleanroom.testutils as tu

import os
import tempfile
import unittest


class CommandTest(unittest.TestCase, tu.BaseParserTest):
    """Test for Parser class of cleanroom."""

    def setUp(self):
        """Set up method."""
        self._create_and_setup_parser(5)
        self._tempDir = tempfile.TemporaryDirectory(prefix='clrm-cmd-test',
                                                    dir='/tmp')

        work_directory = os.path.join(self._tempDir.name, 'work')
        systems_directory = os.path.join(self._tempDir.name, 'systems')

        self.ctx.set_directories(systems_directory, work_directory)

        parser.Parser.find_commands(self.ctx)

    def tearDown(self):
        """Tear down method."""
        self._tempDir.cleanup()

    def test_based(self):
        """Test based with a name."""
        self._verify('   based on foo\n', [('based', ('on', 'foo',))])

    # Error cases:
    def test_based_nothing(self):
        """Test an image without 'on' and name."""
        with self.assertRaises(exceptions.ParseError):
            self._parse('  based\n')

    def test_based_no_name(self):
        """Test based without name."""
        with self.assertRaises(exceptions.ParseError):
            self._parse('  based  on\n')

    def test_based_with_invalid_base(self):
        """Test based with invalid name."""
        with self.assertRaises(exceptions.ParseError):
            self._parse('   based on f!oo\n')


if __name__ == '__main__':
    unittest.main()
