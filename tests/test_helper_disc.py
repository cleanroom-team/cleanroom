#!/usr/bin/python
"""Test for the disc helper module.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import pytest

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..')))

import cleanroom.generator.helper.generic.disc as disc


@pytest.mark.parametrize(('input', 'output'), [
    pytest.param(1, 1, id='int 1'),
    pytest.param(1024, 1024, id='int 1024'),
    pytest.param('9', 9, id='9 as string'),
    pytest.param('1024', 1024, id='1024 as string'),
    pytest.param('9b', 9, id='9b'),
    pytest.param('9K', 9216, id='9K'),
    pytest.param('9k', 9216, id='9k'),
    pytest.param('9m', 9437184, id='9m'),
    pytest.param('9M', 9437184, id='9M'),
    pytest.param('9g', 9663676416, id='9g'),
    pytest.param('9G', 9663676416, id='9G'),
    pytest.param('9t', 9895604649984, id='9t'),
    pytest.param('9T', 9895604649984, id='9T'),
])
def test_disc_normalize_size(input, output):
    """Test absolute input file name."""
    result = disc.normalize_size(input)

    assert result == output


# Error cases:
@pytest.mark.parametrize('input', [
    pytest.param('12,3', id='float'),
    pytest.param('0', id='0'),
    pytest.param('-12', id='negative int'),
    pytest.param('12.3b', id='float b'),
    pytest.param('test', id='test'),
    pytest.param('12z', id='wrong unit')
])
def test_disc_normalize_size_errors(input):
    """Test absolute input file name."""
    with pytest.raises(ValueError):
        disc.normalize_size(input)


@pytest.mark.parametrize('size', [
    pytest.param(1),
    pytest.param(512),
    pytest.param(1024),
    pytest.param(9 * 1024),
    pytest.param(1 * 1024 * 1024)
])
def test_create_image_file(tmpdir, size):
    file = os.path.join(tmpdir, 'testfile')
    disc.create_image_file(file, size)

    assert size == os.path.getsize(file)
