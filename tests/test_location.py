#!/usr/bin/python
"""Test for the location class.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import cleanroom.location as loc

import unittest


class LocationTest(unittest.TestCase):
    """Test for Location class of cleanroom."""

    def test_nothing(self):
        """Test location with no data."""
        location = loc.Location()
        self.assertEqual(str(location), '<UNKNOWN>')

    def test_fn(self):
        """Test location with file name only."""
        location = loc.Location(file_name='/tmp/foo')
        self.assertEqual(str(location), '/tmp/foo')

    def test_ln(self):
        """Test location with line number only."""
        with self.assertRaises(AssertionError):
            loc.Location(line_number=42)

    def test_lo(self):
        """Test location with line offset only."""
        with self.assertRaises(AssertionError):
            loc.Location(line_offset=23)

    def test_ei(self):
        """Test location with extra information only."""
        location = loc.Location(extra_information='!extra!')
        self.assertEqual(str(location), '"!extra!"')

    def test_fn_invalid_ln(self):
        """Test location with file name and invalid line number."""
        with self.assertRaises(AssertionError):
            loc.Location(file_name='/tmp/foo', line_number=0)

    def test_fn_ln1(self):
        """Test location with file name and line number 1."""
        location = loc.Location(file_name='/tmp/foo', line_number=1)
        self.assertEqual(str(location), '/tmp/foo:1')

    def test_fn_ln42(self):
        """Test location with file name and line number 1."""
        location = loc.Location(file_name='/tmp/foo', line_number=42)
        self.assertEqual(str(location), '/tmp/foo:42')

    def test_fn_ln_ei(self):
        """Test location with file name, line number and extra information."""
        location = loc.Location(file_name='/tmp/foo',
                                line_number=42,
                                extra_information='!extra!')
        self.assertEqual(str(location), '/tmp/foo:42 "!extra!"')

    def test_fn_lo(self):
        """Test location with file name and line offset 23."""
        with self.assertRaises(AssertionError):
            loc.Location(file_name='/tmp/foo', line_offset=23)

    def test_fn_ei(self):
        """Test location with file name and extra information."""
        location = loc.Location(file_name='/tmp/foo',
                                extra_information='!extra!')
        self.assertEqual(str(location), '/tmp/foo "!extra!"')

    def test_fn_ln_lo(self):
        """Test location with file name, line number and line offset."""
        location = loc.Location(file_name='/tmp/foo',
                                line_number=42, line_offset=23)
        self.assertEqual(str(location), '/tmp/foo:42+23')

    def test_fn_ln_invalid_lo(self):
        """Test location with file name, line number and line offset."""
        with self.assertRaises(AssertionError):
            loc.Location(file_name='/tmp/foo',
                         line_number=42, line_offset=0)

    def test_fn_ln_lo_ei(self):
        """Test location with file name, line number, line offset and extra."""
        location = loc.Location(file_name='/tmp/foo',
                                line_number=42, line_offset=23,
                                extra_information='!extra!')
        self.assertEqual(str(location), '/tmp/foo:42+23 "!extra!"')

    def test_ln_lo_ei(self):
        """Test location with line number and line offset and extra info."""
        with self.assertRaises(AssertionError):
            loc.Location(line_number=42, line_offset=23,
                         extra_information='!extra!')


if __name__ == '__main__':
    unittest.main()
