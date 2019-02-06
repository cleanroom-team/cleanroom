#!/usr/bin/python
"""Test for the systemd_cleanup of cleanroom.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import pytest  # type: ignore

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..')))

from cleanroom.command import process_args, process_kwargs


@pytest.mark.parametrize(('test_input', 'expected'), [
    pytest.param(('test', '1, 2, 3'),
                 ('test', '1, 2, 3'),
                 id='basic'),
    pytest.param(('test', 1, True, False, None),
                 ('test', '1', 'True', 'False', 'None'),
                 id='special inputs'),
    pytest.param(('${ROOT_DIR}/etc/testfile',),
                 ('/some/place/etc/testfile',),
                 id='substitution'),
])
def test_cmd_run_map_args(system_context, test_input, expected):
    """Test map_base."""
    system_context.set_substitution('TEST', '<replaced>')
    system_context.set_substitution('ROOT_DIR', '/some/place')

    result = process_args(system_context, *test_input)
    assert result == expected


@pytest.mark.parametrize(('test_input', 'expected'), [
    pytest.param({'test': 'fortytwo', 'foo': 'bar'},
                 {'test': 'fortytwo', 'foo': 'bar'},
                 id='basic'),
    pytest.param({'test': True, 'foo': False, 'nothing': None, 'int': 42},
                 {'test': True, 'foo': False, 'nothing': None, 'int': 42},
                 id='special inputs'),
    pytest.param({'path': '${ROOT_DIR}/some/file', 'int': 42},
                 {'path': '/some/place/some/file', 'int': 42},
                 id='substitution'),
])
def test_cmd_run_map_kwargs(system_context, test_input, expected):
    """Test map_base."""
    system_context.set_substitution('TEST', '<replaced>')
    system_context.set_substitution('ROOT_DIR', '/some/place')

    result = process_kwargs(system_context, **test_input)
    assert result == expected
