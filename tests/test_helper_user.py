# # -*- coding: utf-8 -*-
# """Test for the cleanroom.generator.helper.generic.user
#
# @author: Tobias Hunger <tobias.hunger@gmail.com>
# """


import pytest  # type: ignore
import typing

import os
import os.path
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cleanroom.binarymanager import BinaryManager, Binaries
from cleanroom.helper.user import UserHelper


@pytest.mark.parametrize(
    ("user_name", "expected_data"),
    [
        pytest.param(
            "root",
            {
                "name": "root",
                "password": "x",
                "uid": 0,
                "gid": 0,
                "comment": "root user",
                "home": "/root",
                "shell": "/bin/bash",
            },
            id="root",
        ),
        pytest.param(
            "bin",
            {
                "name": "bin",
                "password": "x",
                "uid": 1,
                "gid": 1,
                "comment": "",
                "home": "/",
                "shell": "/sbin/nologin",
            },
            id="bin",
        ),
        pytest.param(
            "test",
            {
                "name": "test",
                "password": "x",
                "uid": 10001,
                "gid": 10001,
                "comment": "Test user",
                "home": "/home/test",
                "shell": "/bin/false",
            },
            id="test",
        ),
    ],
)
def test_user_data(
    user_setup, user_name: str, expected_data: typing.Dict[str, typing.Any]
) -> None:
    """Test reading of valid data from /etc/passwd-like file."""
    result = UserHelper.user_data(user_name, root_directory=user_setup)
    assert result
    assert result._asdict() == expected_data


def test_missing_user_data_file(user_setup) -> None:
    """Test reading a unknown user name from /etc/passwd-like file."""
    result = UserHelper.user_data(
        "root", root_directory=os.path.join(user_setup, "etc")
    )
    assert result is None


def test_missing_user_data(user_setup) -> None:
    """Test reading a unknown user name from /etc/passwd-like file."""
    result = UserHelper.user_data("unknownUser", root_directory=user_setup)
    assert result
    assert result._asdict() == {
        "name": "nobody",
        "password": "x",
        "uid": 65534,
        "gid": 65534,
        "comment": "Nobody",
        "home": "/",
        "shell": "/sbin/nologin",
    }


def test_add_user(user_setup) -> None:
    binary_manager = BinaryManager()
    user_helper = UserHelper(
        binary_manager.binary(Binaries.USERADD), binary_manager.binary(Binaries.USERMOD)
    )
    user_helper.useradd(
        "addeduser",
        comment="freshly added user",
        uid=1200,
        gid=33,
        home="/var/lib/addeduser",
        shell="/usr/bin/nologin",
        root_directory=user_setup,
    )

    result = UserHelper.user_data("addeduser", root_directory=user_setup)
    assert result
    assert result._asdict() == {
        "name": "addeduser",
        "password": "x",
        "uid": 1200,
        "gid": 33,
        "comment": "freshly added user",
        "home": "/var/lib/addeduser",
        "shell": "/usr/bin/nologin",
    }


def test_mod_user(user_setup) -> None:
    binary_manager = BinaryManager()
    user_helper = UserHelper(
        binary_manager.binary(Binaries.USERADD), binary_manager.binary(Binaries.USERMOD)
    )
    user_helper.usermod(
        "test",
        comment="freshly added user",
        shell="/usr/bin/nologin",
        root_directory=user_setup,
    )

    result = UserHelper.user_data("test", root_directory=user_setup)
    assert result
    assert result._asdict() == {
        "name": "test",
        "password": "x",
        "uid": 10001,
        "gid": 10001,
        "comment": "freshly added user",
        "home": "/home/test",
        "shell": "/usr/bin/nologin",
    }
