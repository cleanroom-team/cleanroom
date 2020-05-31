#!/usr/bin/python
"""Test for the set command of cleanroom.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import pytest  # type: ignore

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cleanroom.commandmanager import call_command
from cleanroom.commands.set import SetCommand


@pytest.mark.parametrize(
    ("key", "value", "expected"),
    [
        pytest.param("FOO", "bar", "bar", id="basic"),
        pytest.param("KNOWN", "bar", "bar", id="override KNOWN"),
        pytest.param("KNOWN", "${KNOWN} bar", "some value bar", id="Append KNOWN"),
        pytest.param("KNOWN", "bar  ${KNOWN}", "bar  some value", id="Prepend KNOWN"),
        pytest.param(
            "KNOWN",
            "bar ${KNOWN}  foo",
            "bar some value  foo",
            id="Prepend & Append KNOWN",
        ),
    ],
)
def test_cmd_set(system_context, location, key, value, expected):
    """Test map_base."""
    system_context.set_substitution("TEST", "<replaced>")
    system_context.set_substitution("ROOT_DIR", "/some/place")

    system_context.set_substitution("KNOWN", "some value")

    set_cmd = SetCommand()

    call_command(location, system_context, set_cmd, key, value)

    result = system_context.substitution(key, "")

    assert result == expected
