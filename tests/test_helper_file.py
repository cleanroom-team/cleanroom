#!/usr/bin/python
"""Test for the file helper module.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import pytest

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..')))

import cleanroom.exceptions
import cleanroom.generator.helper.generic.file as filehelper


@pytest.mark.parametrize(('input_file', 'result_file'), [
    pytest.param('/root/test.txt', '/root/test.txt', id='absolute path'),
    pytest.param('/root/../test.txt', '/test.txt', id='absolute path with ..'),
])
def test_file_mapping(system_context, input_file, result_file):
    """Test absolute input file name."""
    result = filehelper.file_name(system_context, input_file)

    assert result == system_context.fs_directory() + result_file


@pytest.mark.parametrize(('input_file', 'result_file'), [
    pytest.param('/root/test.txt', '/root/test.txt', id='absolute path'),
    pytest.param('/root/../test.txt', '/test.txt', id='absolute path with ..'),
])
def test_file_mapping_outside(system_context, input_file, result_file):
    """Test absolute input file name."""
    result = filehelper.file_name(None, input_file)

    assert result == result_file


# Error cases:
@pytest.mark.parametrize('input_file', [
    pytest.param('./test.txt', id='relative path'),
    pytest.param('/root/../../test.txt', id='outside root directory'),
])
def test_file_mapping_errors(system_context, input_file):
    """Test absolute input file name."""
    with pytest.raises(cleanroom.exceptions.GenerateError):
        filehelper.file_name(system_context, input_file)


def _read_file(file_name):
    with open(file_name, 'r') as f:
        return f.read()


def test_file_to_file_copy(populated_system_context):
    """Test copying file to file."""
    system_context = populated_system_context
    filehelper.copy(system_context, '/usr/bin/ls', '/etc/foo')
    assert _read_file(os.path.join(system_context.fs_directory(),
                                   'usr/bin/ls')) == '/usr/bin/ls'
    assert _read_file(os.path.join(system_context.fs_directory(),
                                   'etc/foo')) == '/usr/bin/ls'


def test_same_file_copy(populated_system_context):
    """Test copying file to file."""
    system_context = populated_system_context
    with pytest.raises(AssertionError):
        filehelper.copy(system_context, '/usr/bin/ls', '/usr/bin/ls')


def test_same_file_different_path_copy(populated_system_context):
    """Test copying file to file."""
    system_context = populated_system_context
    with pytest.raises(AssertionError):
        filehelper.copy(system_context, '/usr/bin/ls', '/usr/../usr/bin/ls')


def test_same_file_in_parent_copy(populated_system_context):
    """Test copying file to file."""
    system_context = populated_system_context
    with pytest.raises(AssertionError):
        filehelper.copy(system_context, '/usr/bin/ls', '/usr/bin')


def test_file_to_existing_file_copy(populated_system_context):
    """Test copying file to file."""
    system_context = populated_system_context
    with pytest.raises(AssertionError):
        filehelper.copy(system_context, '/usr/bin/ls', '/etc/passwd')


def test_file_to_overwrite_file_copy(populated_system_context):
    """Test copying file to file."""
    system_context = populated_system_context
    filehelper.copy(system_context, '/usr/bin/ls', '/etc/passwd', force=True)
    assert _read_file(os.path.join(system_context.fs_directory(),
                                   'usr/bin/ls')) == '/usr/bin/ls'
    assert _read_file(os.path.join(system_context.fs_directory(),
                                   'etc/passwd')) == '/usr/bin/ls'


def test_file_to_dir_copy(populated_system_context):
    """Test copying file to directory."""
    system_context = populated_system_context
    filehelper.copy(system_context, '/usr/bin/ls', '/etc')
    assert _read_file(os.path.join(system_context.fs_directory(),
                                   'usr/bin/ls')) == '/usr/bin/ls'
    assert _read_file(os.path.join(system_context.fs_directory(),
                                   'etc/ls')) == '/usr/bin/ls'


def test_file_with_extension_to_dir_copy(populated_system_context):
    """Test copying file to directory."""
    system_context = populated_system_context
    filehelper.copy(system_context, '/home/test/example.txt', '/etc')
    assert _read_file(os.path.join(system_context.fs_directory(),
                                   'home/test/example.txt')) \
        == '/home/test/example.txt'
    assert _read_file(os.path.join(system_context.fs_directory(),
                                   'etc/example.txt')) \
        == '/home/test/example.txt'


def test_dir_to_file_copy(populated_system_context):
    """Test copying a directory into a file."""
    system_context = populated_system_context
    with pytest.raises(IsADirectoryError):
        filehelper.copy(system_context, '/usr/bin', '/etc/foo')


def test_dir_to_dir_copy(populated_system_context):
    """Test copying a directory into another directory."""
    system_context = populated_system_context
    with pytest.raises(IsADirectoryError):
        filehelper.copy(system_context, '/usr/bin', '/home')


def test_dir_to_dir_recursive_copy(populated_system_context):
    """Test copying a directory into another directory."""
    system_context = populated_system_context
    filehelper.copy(system_context, '/usr/bin', '/home', recursive=True)
    assert _read_file(os.path.join(system_context.fs_directory(),
                                   'usr/bin/ls')) == '/usr/bin/ls'
    assert _read_file(os.path.join(system_context.fs_directory(),
                                   'home/bin/ls')) == '/usr/bin/ls'


def test_file_to_file_move(populated_system_context):
    """Test moving file to file."""
    system_context = populated_system_context
    filehelper.move(system_context, '/usr/bin/ls', '/etc/foo')
    assert not os.path.exists(os.path.join(system_context.fs_directory(),
                              'usr/bin/ls'))
    assert _read_file(os.path.join(system_context.fs_directory(),
                                   'etc/foo')) == '/usr/bin/ls'


def test_same_file_different_path_move(populated_system_context):
    """Test moving file to file."""
    system_context = populated_system_context
    with pytest.raises(AssertionError):
        filehelper.move(system_context, '/usr/bin/ls', '/usr/../usr/bin/ls')


def test_same_file_in_parent_move(populated_system_context):
    """Test moving file to file."""
    system_context = populated_system_context
    with pytest.raises(AssertionError):
        filehelper.move(system_context, '/usr/bin/ls', '/usr/bin')


def test_file_to_existing_file_move(populated_system_context):
    """Test moving file to file."""
    system_context = populated_system_context
    with pytest.raises(AssertionError):
        filehelper.move(system_context, '/usr/bin/ls', '/etc/passwd')


def test_file_to_overwrite_file_move(populated_system_context):
    """Test moving file to file."""
    system_context = populated_system_context
    filehelper.move(system_context, '/usr/bin/ls', '/etc/passwd', force=True)
    assert not os.path.isfile(os.path.join(system_context.fs_directory(),
                                           'usr/bin/ls'))
    assert _read_file(os.path.join(system_context.fs_directory(),
                                   'etc/passwd')) == '/usr/bin/ls'


def test_file_to_dir_move(populated_system_context):
    """Test moving file to directory."""
    system_context = populated_system_context
    filehelper.move(system_context, '/usr/bin/ls', '/etc')
    assert not os.path.isfile(os.path.join(system_context.fs_directory(),
                                           'usr/bin/ls'))
    assert _read_file(os.path.join(system_context.fs_directory(),
                                   'etc/ls')) == '/usr/bin/ls'


def test_dir_to_file_move(populated_system_context):
    """Test moving a directory into a file."""
    system_context = populated_system_context
    with pytest.raises(AssertionError):
        filehelper.move(system_context, '/usr/bin', '/etc/passwd')


def test_dir_to_dir_move(populated_system_context):
    """Test moving a directory into another directory."""
    system_context = populated_system_context
    filehelper.move(system_context, '/usr/bin', '/home')
    assert not os.path.isfile(os.path.join(system_context.fs_directory(),
                                           'usr/bin/ls'))
    assert _read_file(os.path.join(system_context.fs_directory(),
                                   'home/bin/ls')) == '/usr/bin/ls'
