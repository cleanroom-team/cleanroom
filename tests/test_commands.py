# #!/usr/bin/python
# """Test for the built-in print_commands of cleanroom.
#
# @author: Tobias Hunger <tobias.hunger@gmail.com>
# """


import pytest

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..')))

import cleanroom.exceptions as ex


def test_based_on_command(parser):
    """Test based with a name."""
    parser.parse_and_verify_string('   based_on foo\n', 'foo',
                                  [('based_on', ('foo',), {}, 1)])


# Error cases:
@pytest.mark.parametrize('test_input', [
    pytest.param('  based_on\n', id='no system'),
    pytest.param('  based_on f!00\n', id='invalid system name'),
])
def test_based_on_errors(parser, test_input):
    """Test an image without name."""
    with pytest.raises(ex.ParseError):
        parser.parse_and_verify_string(test_input, '<invalid>', [])
