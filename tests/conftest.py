# -*- coding: utf-8 -*-
"""Test infrastructure for cleanroom tests.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import pytest
import types

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..')))

from cleanroom.command import Command
from cleanroom.commandmanager import CommandManager
from cleanroom.parser import Parser
from cleanroom.systemcontext import SystemContext

import cleanroom.printer


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
    fs = system_context.fs_directory
    sys = system_context._systems_definition_directory

    os.makedirs(os.path.join(fs, 'usr/bin'))
    os.makedirs(os.path.join(fs, 'usr/lib'))
    os.makedirs(os.path.join(fs, 'etc'))
    os.makedirs(os.path.join(fs, 'home/test'))

    _create_file(fs, '/usr/bin/ls')
    _create_file(fs, '/usr/bin/grep')
    _create_file(fs, '/usr/lib/libz')
    _create_file(fs, '/etc/passwd')
    _create_file(fs, '/home/test/example.txt')

    os.makedirs(os.path.join(sys, 'data/subdata'))
    _create_file(sys, '/data/test.txt')
    _create_file(sys, '/data/subdata/subtest.txt')

    return system_context


class DummyCommand(Command):
    """Dummy command implementation."""

    pass


_Parser_Instance = None


# Injected into parser:
def _parse_and_verify_lines(parser, data, expected):
    """Verify one line of input to the Parser."""
    result = list(map(lambda x: (x.command(), x.arguments(),
                                  x.kwargs(), x.location().line_number),
                       parser._parse_string(''.join(data), '<TEST_DATA>')))

    assert len(result) >= 2
    assert result[0] == ('_setup', (), {}, 1)
    assert result[-1] == ('_teardown', (), {}, 1)
    assert result[1:-1] == expected


def _create_and_setup_parser(system_context: SystemContext):
    """Set up method."""
    cleanroom.printer.Printer.instance()
    command_manager = CommandManager(system_context.systems_definition_directory)
    command_manager._add_command('_setup', DummyCommand('_setup', help='placeholder', file=__file__), '<placeholder>')
    command_manager._add_command('_teardown', DummyCommand('_teardown', help='placeholder', file=__file__), '<placeholder>')
    result = Parser(command_manager, debug=True)

    # inject for easier testing:
    result.parse_and_verify_lines \
        = types.MethodType(_parse_and_verify_lines, result)

    return result


@pytest.fixture()
def parser(global_context):
    """Return a parser."""
    global _Parser_Instance
    if _Parser_Instance is None:
        _Parser_Instance = _create_and_setup_parser(global_context)
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
