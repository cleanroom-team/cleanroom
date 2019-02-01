# -*- coding: utf-8 -*-
"""Test infrastructure for cleanroom tests.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import pytest  # type: ignore
import types

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..')))

from cleanroom.command import Command
from cleanroom.commandmanager import CommandManager
from cleanroom.parser import Parser
from cleanroom.systemcontext import SystemContext


@pytest.fixture()
def system_context(tmpdir):
    """Generate a system context."""
    scratch_directory = tmpdir.mkdir('scratch')
    storage_directory = tmpdir.mkdir('storage')
    systems_definition_directory = tmpdir.mkdir('definitions')

    system_context = SystemContext(system_name='test_system',
                                   base_system_name='',
                                   scratch_directory=scratch_directory,
                                   systems_definition_directory=systems_definition_directory,
                                   storage_directory=storage_directory,
                                   timestamp='20190101-010101')
    return system_context


def _create_file(fs, file_name, contents=None):
    if contents is None:
        contents = file_name.encode('utf-8')
    with open(os.path.join(fs, file_name[1:]), 'wb') as f:
        f.write(contents)


@pytest.fixture()
def populated_system_context(system_context):
    """Generate a fs tree in a system_context fs_directory."""
    fs_directory = system_context.fs_directory
    systems_definition_directory = system_context.systems_definition_directory

    os.makedirs(os.path.join(fs_directory, 'usr/bin'))
    os.makedirs(os.path.join(fs_directory, 'usr/lib'))
    os.makedirs(os.path.join(fs_directory, 'etc'))
    os.makedirs(os.path.join(fs_directory, 'home/test'))

    _create_file(fs_directory, '/usr/bin/ls')
    _create_file(fs_directory, '/usr/bin/grep')
    _create_file(fs_directory, '/usr/lib/libz')
    _create_file(fs_directory, '/etc/passwd')
    _create_file(fs_directory, '/home/test/example.txt')

    os.makedirs(os.path.join(systems_definition_directory, 'data/subdata'))
    _create_file(systems_definition_directory, '/data/test.txt')
    _create_file(systems_definition_directory, '/data/subdata/subtest.txt')

    return system_context


class DummyCommand(Command):
    """Dummy command implementation."""

    pass


_Parser_Instance = None


@pytest.fixture
def command_manager():
    return CommandManager(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                          '../cleanroom/commands')))


# Injected into parser:
def _parse_and_verify_string(parser, data, expected_base_system, expected):
    """Verify one line of input to the Parser."""
    (base_system, exec_obj_list) = parser._parse_string(data, '<TEST_DATA>')
    result = list(map(lambda x: (x.command, x.args,
                                 x.kwargs, x.location.line_number), exec_obj_list))

    assert base_system == expected_base_system
    assert result == expected


def _create_and_setup_parser(command_manager: CommandManager):
    """Set up method."""
    result = Parser(command_manager, debug_parser=True)

    # inject for easier testing:
    result.parse_and_verify_string \
        = types.MethodType(_parse_and_verify_string, result)

    return result


@pytest.fixture()
def parser(command_manager):
    """Return a parser."""
    global _Parser_Instance
    if _Parser_Instance is None:
        _Parser_Instance = _create_and_setup_parser(command_manager)
    return _Parser_Instance


@pytest.fixture()
def user_setup(tmpdir):
    """Generate a simple passwd file."""
    os.mkdir(os.path.join(tmpdir, 'etc'))
    passwd_path = os.path.join(tmpdir, 'etc/passwd')
    with open(passwd_path, 'w') as passwd:
        passwd.write('''root:x:0:0:root user:/root:/bin/bash
bin:x:1:1::/:/sbin/nologin
test:x:10001:10001:Test user:/home/test:/bin/false
test1:x:10002:10001:Test user 1:/home/test:/bin/false
test2:x:10003:10001:Test user 2:/home/test:/bin/false
test3:x:10004:10001:Test user 3:/home/test:/bin/false
''')
    shadow_path = os.path.join(tmpdir, 'etc/shadow')
    with open(shadow_path, 'w') as shadow:
        shadow.write('''root:!::::::
bin:!::::::
test:!::::::
test1:!::::::
test2:!::::::
test3:!::::::
''')
    group_path = os.path.join(tmpdir, 'etc/group')
    with open(group_path, 'w') as group:
        group.write('''root:x:0:root
sys:x:3:bin
mem:x:8:
log:x:19:
proc:x:26:polkitd
lock:x:54:
adm:x:999:daemon
kmem:x:997:
tty:x:5:
utmp:x:996:
audio:x:995:
disk:x:994:
input:x:993:
kvm:x:992:
lp:x:991:cups
optical:x:990:
render:x:989:
storage:x:988:
uucp:x:987:
video:x:986:
users:x:985:
systemd-journal:x:984:
rfkill:x:983:
bin:x:1:daemon
daemon:x:2:bin
http:x:33:
nobody:x:65534:
dbus:x:81:
test:x:10001:test,test1,test2
test1:x:10002
test2:x:10003
test3:x:10004
''')
    return str(tmpdir)
