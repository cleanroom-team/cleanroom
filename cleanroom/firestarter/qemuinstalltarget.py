#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Firestarter binary.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.firestarter.installtarget import InstallTarget
import cleanroom.firestarter.qemutools as qemu_tool
import cleanroom.firestarter.tools as tool
import cleanroom.helper.disk as disk
import cleanroom.helper.mount as mount
from cleanroom.helper.run import run
from cleanroom.printer import debug, verbose, trace

import os
from tempfile import TemporaryDirectory
import typing


def _create_hdd_image(device):
    verbose('hdd.img created.')
    partitioner = disk.Partitioner(device)

    partitioner.repartition([
        disk.Partitioner.efi_partition(size='512M'),
        disk.Partitioner.swap_partition(size='1G', name='swap'),
        disk.Partitioner.data_partition(name='data')])

    verbose('hdd.img repartitioned.')

    debug('Format EFI partitition.')
    run('/usr/bin/mkfs.vfat', device.device(1))
    debug('Set up swap partitition.')
    run('/usr/bin/mkswap', device.device(2))
    debug('Format data partitition.')
    run('/usr/bin/mkfs.btrfs', '-L', 'fs_btrfs', device.device(3))


def _setup_btrfs(mount_point: str):
    trace('Creating subvolumes.')
    run('btrfs', 'subvol', 'create', '@btrfs',
        work_directory=mount_point)
    run('btrfs', 'subvol', 'create', '@home',
        work_directory=mount_point)
    run('btrfs', 'subvol', 'create', '@var',
        work_directory=mount_point)
    run('btrfs', 'subvol', 'create', '.images',
        work_directory=mount_point)


def create_qemu_image(image_path: str, *,
                      image_size: str, image_format: str = 'qcow2',
                      system_name: str, system_version: str = '',
                      repository: str,
                      tempdir: str) -> str:
    trace('Creating image file {}.'.format(image_path))
    with disk.NbdDevice.new_image_file(image_path, image_size,
            disk_format=image_format) as device:
        _create_hdd_image(device)

        debug('mounting data partition for further setup.')
        with mount.Mount(device.device(3), os.path.join(tempdir, 'data'),
                         fs_type='btrfs',
                         options='subvolid=0',
                         fallback_cwd=os.getcwd()) as data_dir:
            _setup_btrfs(data_dir)

            extract_location = os.path.join(data_dir, '.images')
            verbose('Extracting system image to {}.'
                    .format(extract_location))
            extracted_version \
                = tool.write_image(system_name, extract_location,
                                   repository=repository,
                                   version=system_version)

            extracted_image \
                = os.path.join(data_dir, '.images',
                               'clrm_{}'.format(extracted_version))
            assert os.path.isfile(extracted_image)

            tool.copy_efi_partition(image_file=extracted_image,
                                    efi_device=device.device(1),
                                    tempdir=tempdir,
                                    kernel_only=False)

    return image_path


class QemuInstallTarget(InstallTarget):
    def __init__(self) -> None:
        super().__init__('qemu',
                         'Set up hdd image and start it in qemu')

    def __call__(self, parse_result: typing.Any) -> None:
        with TemporaryDirectory(prefix='clrm_qemu_') as tempdir:
            image_path \
                = create_qemu_image(os.path.join(tempdir, 'hdd.img'),
                                    image_size=parse_result.hdd_size,
                                    image_format=parse_result.hdd_format,
                                    system_name=parse_result.system_name,
                                    system_version=parse_result.system_version,
                                    repository=parse_result.repository,
                                    tempdir=tempdir)

            qemu_tool.run_qemu(parse_result,
                               drives=['{}:{}'
                                       .format(image_path,
                                               parse_result.hdd_format)],
                               work_directory=tempdir)

    def setup_subparser(self, parser: typing.Any) -> None:
        qemu_tool.setup_parser_for_qemu(parser)

        parser.add_argument('--hdd-size', dest='hdd_size', action='store',
                            nargs='?', default='10G',
                            help='Size of HDD to generate.')

        parser.add_argument('--hdd-format', dest='hdd_format', action='store',
                            nargs='?', default='qcow2',
                            help='Format of HDD to generate.')
