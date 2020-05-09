# #!/usr/bin/python
# """Test for the file helper module.
#
# @author: Tobias Hunger <tobias.hunger@gmail.com>
# """


import pytest  # type: ignore
import typing

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import cleanroom.exceptions
import cleanroom.helper.file as filehelper
from cleanroom.systemcontext import SystemContext


@pytest.mark.parametrize(
    ("input_file", "result_file"),
    [
        pytest.param("/root/test.txt", "/root/test.txt", id="absolute path"),
        pytest.param("/root/../test.txt", "/test.txt", id="absolute path with .."),
    ],
)
def test_file_mapping(
    system_context: SystemContext, input_file: str, result_file: str
) -> None:
    result = filehelper.file_name(system_context, input_file)
    assert result == system_context.fs_directory + result_file


@pytest.mark.parametrize(
    ("input_file", "result_file"),
    [
        pytest.param("/root/test.txt", "/root/test.txt", id="absolute path"),
        pytest.param("/root/../test.txt", "/test.txt", id="absolute path with .."),
    ],
)
def test_file_mapping_outside(
    system_context: SystemContext, input_file: str, result_file: str
) -> None:
    result = filehelper.file_name(None, input_file)
    assert result == result_file


# Error cases:
@pytest.mark.parametrize(
    "input_file",
    [
        pytest.param("./test.txt", id="relative path"),
        pytest.param("/root/../../test.txt", id="outside root directory"),
    ],
)
def test_file_mapping_errors(system_context: SystemContext, input_file: str) -> None:
    with pytest.raises(cleanroom.exceptions.GenerateError):
        filehelper.file_name(system_context, input_file)


def _read_file(file_name: str) -> str:
    with open(file_name, "r") as f:
        return f.read()


def test_file_to_file_copy(populated_system_context: SystemContext) -> None:
    fs = populated_system_context.fs_directory
    filehelper.copy(populated_system_context, "/usr/bin/ls", "/etc/foo")
    assert _read_file(os.path.join(fs, "usr/bin/ls")) == "/usr/bin/ls"
    assert _read_file(os.path.join(fs, "etc/foo")) == "/usr/bin/ls"


def test_same_file_copy(populated_system_context: SystemContext) -> None:
    with pytest.raises(OSError):
        filehelper.copy(populated_system_context, "/usr/bin/ls", "/usr/bin/ls")


def test_same_file_different_path_copy(populated_system_context: SystemContext) -> None:
    with pytest.raises(OSError):
        filehelper.copy(populated_system_context, "/usr/bin/ls", "/usr/../usr/bin/ls")


def test_same_file_in_parent_copy(populated_system_context: SystemContext) -> None:
    with pytest.raises(AssertionError):
        filehelper.copy(populated_system_context, "/usr/bin/ls", "/usr/bin")


def test_file_to_existing_file_copy(populated_system_context: SystemContext) -> None:
    with pytest.raises(OSError):
        filehelper.copy(populated_system_context, "/usr/bin/ls", "/etc/passwd")


def test_file_to_overwrite_file_copy(populated_system_context: SystemContext) -> None:
    fs = populated_system_context.fs_directory
    filehelper.copy(populated_system_context, "/usr/bin/ls", "/etc/passwd", force=True)
    assert _read_file(os.path.join(fs, "usr/bin/ls")) == "/usr/bin/ls"
    assert _read_file(os.path.join(fs, "etc/passwd")) == "/usr/bin/ls"


def test_file_to_dir_copy(populated_system_context: SystemContext) -> None:
    fs = populated_system_context.fs_directory
    filehelper.copy(populated_system_context, "/usr/bin/ls", "/etc")
    assert _read_file(os.path.join(fs, "usr/bin/ls")) == "/usr/bin/ls"
    assert _read_file(os.path.join(fs, "etc/ls")) == "/usr/bin/ls"


def test_file_with_extension_to_dir_copy(
    populated_system_context: SystemContext,
) -> None:
    fs = populated_system_context.fs_directory
    filehelper.copy(populated_system_context, "/home/test/example.txt", "/etc")
    assert (
        _read_file(os.path.join(fs, "home/test/example.txt"))
        == "/home/test/example.txt"
    )
    assert _read_file(os.path.join(fs, "etc/example.txt")) == "/home/test/example.txt"


def test_dir_to_file_copy(populated_system_context: SystemContext) -> None:
    with pytest.raises(IsADirectoryError):
        filehelper.copy(populated_system_context, "/usr/bin", "/etc/foo")


def test_dir_to_dir_copy(populated_system_context: SystemContext) -> None:
    with pytest.raises(IsADirectoryError):
        filehelper.copy(populated_system_context, "/usr/bin", "/home")


def test_dir_to_dir_recursive_copy(populated_system_context: SystemContext) -> None:
    fs = populated_system_context.fs_directory
    filehelper.copy(populated_system_context, "/usr/bin", "/home", recursive=True)
    assert _read_file(os.path.join(fs, "usr/bin/ls")) == "/usr/bin/ls"
    assert _read_file(os.path.join(fs, "home/bin/ls")) == "/usr/bin/ls"


def test_file_to_file_move(populated_system_context: SystemContext) -> None:
    fs = populated_system_context.fs_directory
    filehelper.move(populated_system_context, "/usr/bin/ls", "/etc/foo")
    assert not os.path.exists(os.path.join(fs, "usr/bin/ls"))
    assert _read_file(os.path.join(fs, "etc/foo")) == "/usr/bin/ls"


def test_same_file_different_path_move(populated_system_context: SystemContext) -> None:
    with pytest.raises(OSError):
        filehelper.move(populated_system_context, "/usr/bin/ls", "/usr/../usr/bin/ls")


def test_same_file_in_parent_move(populated_system_context: SystemContext) -> None:
    with pytest.raises(AssertionError):
        filehelper.move(populated_system_context, "/usr/bin/ls", "/usr/bin")


def test_file_to_existing_file_move(populated_system_context: SystemContext) -> None:
    with pytest.raises(OSError):
        filehelper.move(populated_system_context, "/usr/bin/ls", "/etc/passwd")


def test_file_to_overwrite_file_move(populated_system_context: SystemContext) -> None:
    fs = populated_system_context.fs_directory
    filehelper.move(populated_system_context, "/usr/bin/ls", "/etc/passwd", force=True)
    assert not os.path.isfile(os.path.join(fs, "usr/bin/ls"))
    assert _read_file(os.path.join(fs, "etc/passwd")) == "/usr/bin/ls"


def test_file_to_dir_move(populated_system_context: SystemContext) -> None:
    fs = populated_system_context.fs_directory
    filehelper.move(populated_system_context, "/usr/bin/ls", "/etc")
    assert not os.path.isfile(os.path.join(fs, "usr/bin/ls"))
    assert _read_file(os.path.join(fs, "etc/ls")) == "/usr/bin/ls"


def test_dir_to_file_move(populated_system_context: SystemContext) -> None:
    with pytest.raises(OSError):
        filehelper.move(populated_system_context, "/usr/bin", "/etc/passwd")


def test_dir_to_dir_move(populated_system_context: SystemContext) -> None:
    fs = populated_system_context.fs_directory
    filehelper.move(populated_system_context, "/usr/bin", "/home")
    assert not os.path.isfile(os.path.join(fs, "usr/bin/ls"))
    assert _read_file(os.path.join(fs, "home/bin/ls")) == "/usr/bin/ls"
