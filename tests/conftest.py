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

import cleanroom.command
import cleanroom.context
import cleanroom.parser
import cleanroom.printer
import cleanroom.systemcontext


@pytest.fixture()
def global_context():
    """Generate a global context object."""
    return cleanroom.context.Context()


@pytest.fixture()
def system_context(tmpdir, global_context):
    """Generate a system context."""
    system_dir = tmpdir.mkdir('system')
    work_dir = tmpdir.mkdir('work')

    global_context.set_directories(str(system_dir), str(work_dir))
    sys_ctx \
        = cleanroom.systemcontext.SystemContext(global_context,
                                                system='test-system',
                                                timestamp='now')
    assert(os.path.join(str(work_dir), 'current/fs')
           == sys_ctx.fs_directory())

    return sys_ctx


class DummyCommand(cleanroom.command.Command):
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
    cleanroom.parser.Parser.find_commands(global_ctx.commands_directory())
    result = cleanroom.parser.Parser()
    cleanroom.parser.Parser._commands['_setup'] \
        = (DummyCommand('_setup', help='placeholder'), '<placeholder>')
    cleanroom.parser.Parser._commands['_teardown'] \
        = (DummyCommand('_teardown', help='placeholder'), '<placeholder>')

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
