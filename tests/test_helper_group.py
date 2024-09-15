#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test for the cleanroom.generator.helper.generic.group

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

import pytest  # type: ignore
import typing

import os
import os.path
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cleanroom.binarymanager import BinaryManager, Binaries
from cleanroom.helper.group import GroupHelper


@pytest.mark.parametrize(
    ("group_name", "expected_data"),
    [
        pytest.param(
            "root",
            {"name": "root", "password": "x", "gid": 0, "members": ["root"]},
            id="root",
        ),
        pytest.param(
            "sys",
            {"name": "sys", "password": "x", "gid": 3, "members": ["bin"]},
            id="sys",
        ),
        pytest.param(
            "mem", {"name": "mem", "password": "x", "gid": 8, "members": []}, id="sys"
        ),
        pytest.param(
            "test",
            {
                "name": "test",
                "password": "x",
                "gid": 10001,
                "members": ["test", "test1", "test2"],
            },
            id="test",
        ),
    ],
)
def test_group_data(
    user_setup, group_name: str, expected_data: typing.Dict[str, typing.Any]
) -> None:
    """Test reading of valid data from /etc/passwd-like file."""
    result = GroupHelper.group_data(group_name, root_directory=user_setup)
    assert result
    assert result._asdict() == expected_data


def test_missing_group_data_file(user_setup) -> None:
    """Test reading from an unknown /etc/group-like file."""
    result = GroupHelper.group_data(
        "root", root_directory=os.path.join(user_setup, "etc")
    )
    assert result is None


def test_missing_group_data(user_setup) -> None:
    """Test reading a unknown user name from /etc/passwd-like file."""
    result = GroupHelper.group_data("unknownGroup", root_directory=user_setup)
    assert result
    assert result._asdict() == {
        "name": "nobody",
        "password": "x",
        "gid": 65534,
        "members": [],
    }


def test_add_group(user_setup) -> None:
    binary_manager = BinaryManager()
    group_helper = GroupHelper(
        binary_manager.binary(Binaries.GROUPADD),
        binary_manager.binary(Binaries.GROUPMOD),
    )
    group_helper.groupadd("addedgroup", gid=1200, root_directory=user_setup)

    result = GroupHelper.group_data("addedgroup", root_directory=user_setup)
    assert result
    assert result._asdict() == {
        "name": "addedgroup",
        "password": "x",
        "gid": 1200,
        "members": [],
    }


def test_mod_group(user_setup) -> None:
    binary_manager = BinaryManager()
    group_helper = GroupHelper(
        binary_manager.binary(Binaries.GROUPADD),
        binary_manager.binary(Binaries.GROUPMOD),
    )
    group_helper.groupmod("test", rename="tester", root_directory=user_setup)

    result = GroupHelper.group_data("tester", root_directory=user_setup)
    assert result
    assert result._asdict() == {
        "name": "tester",
        "password": "x",
        "gid": 10001,
        "members": ["test", "test1", "test2"],
    }
