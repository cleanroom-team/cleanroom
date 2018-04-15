#!/usr/bin/python
"""Test for the location class.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import cleanroom.location as loc

import pytest


def test_nothing():
    """Test location with no data."""
    location = loc.Location()
    assert str(location) == '<UNKNOWN>'


def test_file_name():
    """Test location with file name only."""
    location = loc.Location(file_name='/tmp/foo')
    assert str(location) == '/tmp/foo'


def test_line_number():
    """Test location with line number only."""
    with pytest.raises(AssertionError):
        loc.Location(line_number=42)


def test_line_offset():
    """Test location with line offset only."""
    with pytest.raises(AssertionError):
        loc.Location(line_offset=23)


def test_extra_information():
    """Test location with extra information only."""
    location = loc.Location(extra_information='!extra!')
    assert str(location) == '"!extra!"'


def test_fn_invalid_line_number():
    """Test location with file name and invalid line number."""
    with pytest.raises(AssertionError):
        loc.Location(file_name='/tmp/foo', line_number=0)


def test_file_name_line_number1():
    """Test location with file name and line number 1."""
    location = loc.Location(file_name='/tmp/foo', line_number=1)
    assert str(location) == '/tmp/foo:1'


def test_file_name_line_number42():
    """Test location with file name and line number 1."""
    location = loc.Location(file_name='/tmp/foo', line_number=42)
    assert str(location) == '/tmp/foo:42'


def test_file_name_line_number_extra_information():
    """Test location with file name, line number and extra information."""
    location = loc.Location(file_name='/tmp/foo',
                            line_number=42,
                            extra_information='!extra!')
    assert str(location) == '/tmp/foo:42 "!extra!"'


def test_file_name_line_offset():
    """Test location with file name and line offset 23."""
    with pytest.raises(AssertionError):
        loc.Location(file_name='/tmp/foo', line_offset=23)


def test_file_name_extra_information():
    """Test location with file name and extra information."""
    location = loc.Location(file_name='/tmp/foo',
                            extra_information='!extra!')
    assert str(location) == '/tmp/foo "!extra!"'


def test_file_name_line_number_line_offset():
    """Test location with file name, line number and line offset."""
    location = loc.Location(file_name='/tmp/foo',
                            line_number=42, line_offset=23)
    assert str(location), '/tmp/foo:42+23'


def test_file_name_line_number_invalid_line_offset():
    """Test location with file name, line number and line offset."""
    with pytest.raises(AssertionError):
        loc.Location(file_name='/tmp/foo', line_number=42, line_offset=0)


def test_file_name_line_number_line_offset_extra_information():
    """Test location with file name, line number, line offset and extra."""
    location = loc.Location(file_name='/tmp/foo',
                            line_number=42, line_offset=23,
                            extra_information='!extra!')
    assert str(location) == '/tmp/foo:42+23 "!extra!"'


def test_line_number_line_offset_extra_information():
    """Test location with line number and line offset and extra info."""
    with pytest.raises(AssertionError):
        loc.Location(line_number=42, line_offset=23,
                     extra_information='!extra!')
