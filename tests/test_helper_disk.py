#!/usr/bin/python
"""Test for the disk helper module.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import pytest  # type: ignore

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..')))

import cleanroom.helper.disk as disk


@pytest.mark.parametrize(('input_size', 'output_size'), [
    pytest.param(1, 1, id='int 1'),
    pytest.param(0, 0, id='0'),
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
def test_disk_normalize_size(input_size, output_size) -> None:
    """Test absolute input file name."""
    result = disk.normalize_size(input_size)

    assert result == output_size


# Error cases:
@pytest.mark.parametrize('input_size', [
    pytest.param('12,3', id='float'),
    pytest.param('-12', id='negative int'),
    pytest.param('12.3b', id='float b'),
    pytest.param('test', id='test'),
    pytest.param('12z', id='wrong unit')
])
def test_disk_normalize_size_errors(input_size) -> None:
    """Test absolute input file name."""
    with pytest.raises(ValueError):
        disk.normalize_size(input_size)


@pytest.mark.parametrize('input_size', [
    pytest.param(1),
    pytest.param(512),
    pytest.param(1024),
    pytest.param(9 * 1024),
    pytest.param(1 * 1024 * 1024)
])
def test_create_image_file(tmpdir, input_size: int) -> None:
    if os.geteuid() != 0:
        pytest.skip('This test needs root to run.')

    file = os.path.join(tmpdir, 'testfile')
    disk.create_image_file(file, input_size, disk_format='raw')

    # qemu-img does some rounding to sector sizes:
    assert input_size <= os.path.getsize(file)
    assert input_size + 1024 > os.path.getsize(file)


def test_partitioner(tmpdir) -> None:
    if os.geteuid() != 0:
        pytest.skip('This test needs root to run.')

    with disk.NbdDevice.new_image_file(os.path.join(tmpdir, 'testdisk'),
                                       disk.normalize_size('512m')) as device:
        partitioner = disk.Partitioner(device)
        assert not partitioner.is_partitioned()
        assert partitioner.label() is None

        print('LBA: {}-{}'.format(partitioner.first_lba(), partitioner.last_lba()))

        parts = [disk.Partitioner.efi_partition(size='64M'),
                 disk.Partitioner.swap_partition(size='128M'),
                 disk.Partitioner.data_partition(name='PV0 of vg_something')]
        partitioner.repartition(parts)

        assert partitioner.is_partitioned()
        assert partitioner.label() == 'gpt'
