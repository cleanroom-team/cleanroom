# -*- coding: utf-8 -*-
"""Test for the cleanroom.generator.helper.generic.group

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import pytest

import os
import os.path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..')))

import cleanroom.generator.helper.generic.group as group


@pytest.fixture()
def group_file(tmpdir):
    """Generate a simple passwd file."""
    path = os.path.join(tmpdir, 'group')
    with open(path, 'w') as passwd:
        passwd.write('root:x:0:root\n'
                     'sys:x:3:bin\n'
                     'mem:x:8:\n'
                     'test:x:10001:test,test1,test2\n')
    return path


@pytest.mark.parametrize(('group_name', 'expected_data'), [
    pytest.param('root', {'name': 'root', 'password': 'x', 'gid': 0,
                          'members': ['root']}, id='root'),
    pytest.param('sys', {'name': 'sys', 'password': 'x', 'gid': 3,
                         'members': ['bin']}, id='sys'),
    pytest.param('mem', {'name': 'mem', 'password': 'x', 'gid': 8,
                         'members': []}, id='sys'),
    pytest.param('test', {'name': 'test', 'password': 'x', 'gid': 10001,
                          'members': ['test', 'test1', 'test2']}, id='test'),
])
def test_group_data(group_file, group_name, expected_data):
    """Test reading of valid data from /etc/passwd-like file."""
    result = group._group_data(group_file, group_name)
    assert result._asdict() == expected_data


def test_missing_group_data_file(group_file):
    """Test reading from an unknown /etc/passwd-like file."""
    result = group._group_data(group_file + 'FOO', 'root')
    assert result is None


def test_missing_group_data(group_file):
    """Test reading a unknown user name from /etc/passwd-like file."""
    result = group._group_data(group_file, 'unknownGroup')
    assert result._asdict() == {'name': 'nobody', 'password': 'x',
                                'gid': 65534, 'members': []}
