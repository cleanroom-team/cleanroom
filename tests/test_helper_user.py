# -*- coding: utf-8 -*-
"""Test for the cleanroom.helper.generic.user

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import pytest

import os
import os.path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..')))

import cleanroom.helper.generic.user as user


@pytest.fixture()
def passwd_file(tmpdir):
    """Generate a simple passwd file."""
    path = os.path.join(tmpdir, 'passwd')
    with open(path, 'w') as passwd:
        passwd.write('root:x:0:0::/root:/bin/bash\n'
                     'bin:x:1:1::/:/sbin/nologin\n'
                     'test:x:10001:10001:Test user:/home/test:/bin/false\n')
    return path


@pytest.mark.parametrize(('user_name', 'expected_data'), [
    pytest.param('root', {'name': 'root', 'password': 'x', 'uid': 0, 'gid': 0,
                          'comment': '', 'home': '/root', 'shell': '/bin/bash'},
                 id='root'),
    pytest.param('bin', {'name': 'bin', 'password': 'x', 'uid': 1, 'gid': 1,
                         'comment': '', 'home': '/', 'shell': '/sbin/nologin'},
                 id='bin'),
    pytest.param('test', {'name': 'test', 'password': 'x',
                          'uid': 10001, 'gid': 10001, 'comment': 'Test user',
                          'home': '/home/test', 'shell': '/bin/false'},
                 id='test'),
])
def test_user_data(passwd_file, user_name, expected_data):
    """Test reading of valid data from /etc/passwd-like file."""
    result = user._user_data(passwd_file, user_name)
    assert result._asdict() == expected_data


def test_missing_user_data(passwd_file):
    """Test reading a unknown user name from /etc/passwd-like file."""
    result = user._user_data(passwd_file, 'unknownUser')
    assert result is None
