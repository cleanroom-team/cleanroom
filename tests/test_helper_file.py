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
import cleanroom.helper.generic.file as filehelper


@pytest.mark.parametrize(('input_file', 'result_file'), [
    pytest.param('/root/test.txt', '/root/test.txt', id='absolute path'),
    pytest.param('/root/../test.txt', '/test.txt', id='absolute path with ..'),
])
def test_file_mapping(system_context, input_file, result_file):
    """Test absolute input file name."""
    result = filehelper.file_name(system_context, input_file)

    assert result == system_context.fs_directory() + result_file

# Error cases:
@pytest.mark.parametrize('input_file', [
    pytest.param('./test.txt', id='relative path'),
    pytest.param('/root/../../test.txt', id='outside root directory'),
])
def test_file_mapping_errors(system_context, input_file):
    """Test absolute input file name."""
    with pytest.raises(cleanroom.exceptions.GenerateError):
        filehelper.file_name(system_context, input_file)
