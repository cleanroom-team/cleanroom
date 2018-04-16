#!/usr/bin/python
"""Test for the location class.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import pytest

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import cleanroom.location as loc


@pytest.mark.parametrize(('file_name', 'line_number', 'line_offset',
                          'extra_information', 'result_string'), [
    pytest.param(None, None, None, None, '<UNKNOWN>', id='nothing'),
    pytest.param('/tmp/foo', None, None, '!extra!',
                 '/tmp/foo "!extra!"', id='file_name, extra'),
    pytest.param('/tmp/foo', None, None, None, '/tmp/foo',
                 id='file_name'),
    pytest.param('/tmp/foo', 1, None, None, '/tmp/foo:1',
                 id='file_name, line_number=1'),
    pytest.param('/tmp/foo', 42, None, None, '/tmp/foo:42',
                 id='file_name, line_number=42'),
    pytest.param('/tmp/foo', 1, None, '!extra!', '/tmp/foo:1 "!extra!"',
                 id='file_name, line_number=1, extra'),
    pytest.param('/tmp/foo', 42, None, '!extra!', '/tmp/foo:42 "!extra!"',
                 id='file_name, line_number=42, extra'),
    pytest.param('/tmp/foo', 42, 23, None, '/tmp/foo:42+23',
                 id='file_name, line_number=42, line_offset'),
    pytest.param('/tmp/foo', 42, 23, '!extra!', '/tmp/foo:42+23 "!extra!"',
                 id='file_name, line_number=42, line_offset, extra'),
    pytest.param(None, None, None, '!extra!', '"!extra!"', id='extra_info'),
])
def test_location(file_name, line_number, line_offset, extra_information,
                  result_string):
    location = loc.Location(file_name=file_name, line_number=line_number,
                            line_offset=line_offset,
                            extra_information=extra_information)
    assert str(location) == result_string


@pytest.mark.parametrize(('file_name', 'line_number', 'line_offset',
                          'extra_information'), [
    pytest.param(None, 42, None, None, id='line_number'),
    pytest.param(None, None, 23, None, id='line_offset'),
    pytest.param('/tmp/foo', 0, None, None,
                 id='file_name, invalid line_number'),
    pytest.param('/tmp/foo', -1, None, None,
                 id='file_name, invalid line_number 2'),
    pytest.param('/tmp/foo', None, 23,  None,
                 id='file_name, line_offset'),
    pytest.param('/tmp/foo', 23, 0, None,
                 id='file_name, line_number, invalid line_offset'),
    pytest.param('/tmp/foo', 23, -1, None,
                 id='file_name, line_number, invalid line_offset 2'),
    pytest.param(None, 42, 23, '!extra!',
                 id='line_number, line_offset, extra'),
])
def test_location_errors(file_name, line_number,
                         line_offset, extra_information):
    with pytest.raises(AssertionError):
        loc.Location(file_name=file_name, line_number=line_number,
                     line_offset=line_offset,
                     extra_information=extra_information)
