#!/usr/bin/python
"""Test for the exceptions of cleanroom.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..')))

import cleanroom.exceptions as ex
import cleanroom.location as location


def test_base_exceptions():
    """Test the base exception class."""
    e = ex.CleanRoomError('message')
    assert str(e) == 'Error: message'


def test_base_exceptions_multi_args():
    """Test the base exception class."""
    e = ex.CleanRoomError('message', 'something')
    assert str(e) == 'Error: message something'


def test_base_exceptions_with_location():
    """Test the base exception class with file."""
    loc = location.Location(file_name='/foo/bar')
    e = ex.CleanRoomError('message', location=loc)
    assert str(e) == 'Error in /foo/bar: message'


def test_base_exceptions_with_file_and_line():
    """Test the base exception class with file and line."""
    loc = location.Location(file_name='/foo/bar', line_number=42)
    e = ex.CleanRoomError('message', location=loc)
    assert str(e) == 'Error in /foo/bar:42: message'


def test_preflight():
    """Test preflight exception."""
    e = ex.PreflightError('Something went wrong')
    assert str(e) == 'Error: Something went wrong'


def test_context():
    """Test context exception."""
    e = ex.ContextError('Something went wrong')
    assert str(e) == 'Error: Something went wrong'


def test_prepare():
    """Test prepare exception."""
    e = ex.PrepareError('Something went wrong')
    assert str(e) == 'Error: Something went wrong'


def test_generate():
    """Test prepare exception."""
    e = ex.GenerateError('Something went wrong')
    assert str(e) == 'Error: Something went wrong'


def test_system_not_found():
    """Test system not found exception."""
    e = ex.SystemNotFoundError('Something went wrong')
    assert str(e) == 'Error: Something went wrong'


def test_parse():
    """Test parse exception."""
    e = ex.ParseError('Something went wrong')
    assert str(e) == 'Error: Something went wrong'
