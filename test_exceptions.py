#!/usr/bin/python
"""Test for the exceptions of cleanroom.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

import cleanroom.exceptions as ex
import cleanroom.location as location

import unittest


class ExceptionsTest(unittest.TestCase):
    """Test for exceptions of cleanroom."""

    def test_base_exceptions(self):
        """Test the base exception class."""
        e = ex.CleanRoomError('message')
        self.assertEqual(str(e), 'Error: message')

    def test_base_exceptions_multi_args(self):
        """Test the base exception class."""
        e = ex.CleanRoomError('message', 'something')
        self.assertEqual(str(e), 'Error: message something')

    def test_base_exceptions_with_location(self):
        """Test the base exception class with file."""
        loc = location.Location(file_name='/foo/bar')
        e = ex.CleanRoomError('message', location=loc)
        self.assertEqual(str(e), 'Error in /foo/bar: message')

    def test_base_exceptions_with_file_and_line(self):
        """Test the base exception class with file and line."""
        loc = location.Location(file_name='/foo/bar', line_number=42)
        e = ex.CleanRoomError('message', location=loc)
        self.assertEqual(str(e), 'Error in /foo/bar:42: message')

    def test_preflight(self):
        """Test preflight exception."""
        e = ex.PreflightError('Something went wrong')
        self.assertEqual(str(e), 'Error: Something went wrong')

    def test_context(self):
        """Test context exception."""
        e = ex.ContextError('Something went wrong')
        self.assertEqual(str(e), 'Error: Something went wrong')

    def test_prepare(self):
        """Test prepare exception."""
        e = ex.PrepareError('Something went wrong')
        self.assertEqual(str(e), 'Error: Something went wrong')

    def test_generate(self):
        """Test prepare exception."""
        e = ex.GenerateError('Something went wrong')
        self.assertEqual(str(e), 'Error: Something went wrong')

    def test_system_not_found(self):
        """Test system not found exception."""
        e = ex.SystemNotFoundError('Something went wrong')
        self.assertEqual(str(e), 'Error: Something went wrong')

    def test_parse(self):
        """Test parse exception."""
        e = ex.ParseError('Something went wrong')
        self.assertEqual(str(e), 'Error: Something went wrong')


if __name__ == '__main__':
    unittest.main()
