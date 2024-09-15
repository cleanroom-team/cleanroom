#!/usr/bin/python
"""Test for the location class.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

import pytest  # type: ignore

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import cleanroom.location as loc


@pytest.mark.parametrize(
    ("file_name", "line_number", "description", "result_string"),
    [
        pytest.param(None, None, None, "<UNKNOWN>", id="nothing"),
        pytest.param(
            "/tmp/foo", None, "!extra!", '/tmp/foo "!extra!"', id="file_name, extra"
        ),
        pytest.param("/tmp/foo", None, None, "/tmp/foo", id="file_name"),
        pytest.param("/tmp/foo", 1, None, "/tmp/foo:1", id="file_name, line_number=1"),
        pytest.param(
            "/tmp/foo", 42, None, "/tmp/foo:42", id="file_name, line_number=42"
        ),
        pytest.param(
            "/tmp/foo",
            1,
            "!extra!",
            '/tmp/foo:1 "!extra!"',
            id="file_name, line_number=1, extra",
        ),
        pytest.param(
            "/tmp/foo",
            42,
            "!extra!",
            '/tmp/foo:42 "!extra!"',
            id="file_name, line_number=42, extra",
        ),
        pytest.param(None, None, "!extra!", '"!extra!"', id="extra_info"),
    ],
)
def test_location(file_name, line_number, description, result_string):
    location = loc.Location(
        file_name=file_name, line_number=line_number, description=description
    )
    assert str(location) == result_string


@pytest.mark.parametrize(
    ("file_name", "line_number", "description"),
    [
        pytest.param(None, 42, None, id="line_number"),
        pytest.param("/tmp/foo", 0, None, id="file_name, invalid line_number"),
        pytest.param("/tmp/foo", -1, None, id="file_name, invalid line_number 2"),
        pytest.param(None, 42, "!extra!", id="line_number, extra"),
    ],
)
def test_location_errors(file_name, line_number, description):
    with pytest.raises(AssertionError):
        loc.Location(
            file_name=file_name, line_number=line_number, description=description
        )
