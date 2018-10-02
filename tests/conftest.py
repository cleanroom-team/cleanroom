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

from cleanroom.generator.command import Command
from cleanroom.generator.commandmanager import CommandManager
from cleanroom.generator.context import Context
from cleanroom.generator.parser import Parser
from cleanroom.generator.systemcontext import SystemContext

import cleanroom.printer


@pytest.fixture()
def global_context():
    """Generate a global context object."""
    return Context()


@pytest.fixture()
def system_context(tmpdir, global_context):
    """Generate a system context."""
    system_dir = tmpdir.mkdir('system')
    work_dir = tmpdir.mkdir('work')

    global_context.set_directories(str(system_dir), str(work_dir))
    sys_ctx = SystemContext(global_context, system='test-system', timestamp='now')
    assert(os.path.join(str(work_dir), 'current/fs')
           == sys_ctx.fs_directory())

    return sys_ctx


def _create_file(fs, file_name, contents=None):
    if contents is None:
        contents = file_name.encode('utf-8')
    with open(os.path.join(fs, file_name[1:]), 'wb') as f:
        f.write(contents)


@pytest.fixture()
def populated_system_context(system_context):
    """Generate a fs tree in a system_context fs_directory."""
    fs = system_context.fs_directory()
    sys = system_context.ctx.systems_directory()

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
                      parser._parse_lines(data, '<TEST_DATA>')))

    assert len(result) >= 2
    assert result[0] == ('_setup', (), {}, 1)
    assert result[-1] == ('_teardown', (), {}, 1)
    assert result[1:-1] == expected


def _create_and_setup_parser(global_ctx):
    """Set up method."""
    cleanroom.printer.Printer.Instance()
    command_manager = CommandManager()
    command_manager.find_commands(global_ctx.commands_directory())
    command_manager._add_command('_setup', DummyCommand('_setup', help='placeholder', file=__file__), '<placeholder>')
    command_manager._add_command('_teardown', DummyCommand('_teardown', help='placeholder', file=__file__), '<placeholder>')
    result = Parser(command_manager)

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
