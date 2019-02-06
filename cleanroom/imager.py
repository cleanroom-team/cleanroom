#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Main CleanRoom functionality.

FIXME: Allow for different distro ids

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from __future__ import annotations

from .helper import disk
from .helper.run import run as helper_run
from .printer import info, debug, fail, success, trace, verbose

import collections
import os
import shutil
import tempfile
import typing


mib = 1024 * 1024


class DataProvider:
    def write_root_partition(self, target_device: str):
        assert False

    def write_verity_partition(self, target_device: str):
        assert False

    def has_linux_kernel(self):
        assert False
        
    def write_linux_kernel(self, target_directory: str):
        assert False


class FileDataProvider(DataProvider):
    def __init__(self, root_partition, verity_partition, kernel_file):
        self._root_partition = root_partition
        self._verity_partition = verity_partition
        self._kernel_file = kernel_file 

    def write_root_partition(self, target_device: str):
        shutil.copyfile(self._root_partition, target_device)

    def write_verity_partition(self, target_device: str):
        shutil.copyfile(self._verity_partition, target_device)

    def has_linux_kernel(self):
        return self._kernel_file

    def write_linux_kernel(self, target_directory: str):
        shutil.copyfile(self._kernel_file,
                        os.path.join(target_directory,
                                     os.path.basename(self._kernel_file)))


ExtraPartition \
    = collections.namedtuple('ExtraPartition',
                             ['size', 'filesystem', 'label', 'contents'])
ImageConfig \
    = collections.namedtuple('ImageConfig',
                             ['path', 'disk_format', 'force', 'repartition',
                              'efi_size', 'swap_size', 'extra_partitions'])
RawImageConfig \
    = collections.namedtuple('RawImageConfig',
                             ['path', 'disk_format', 'force', 'repartition',
                              'min_device_size', 'efi_size', 'root_size',
                              'verity_size', 'swap_size', 'root_hash',
                              'efi_label', 'root_label', 'verity_label',
                              'swap_label', 'extra_partitions', 'writer'])


def _minimum_efi_size(kernel_size: int) -> int:
    bootloader_size = 1 * mib  # size of systemd-boot (+ some spare)
    return disk.mib_ify(int((kernel_size * 1.05) + (2 * bootloader_size))) * mib


def _calculate_efi_size(kernel_size: int, efi_size: int) -> int:
    if efi_size > 0:
        assert kernel_size < efi_size
        return disk.mib_ify(efi_size) * mib  # rounded to full MiB
    return _minimum_efi_size(kernel_size)


def _calculate_minimum_size(kernel_size: int, root_size: int, verity_size: int,
                            efi_size: int, swap_size: int,
                            extra_partitions: typing.List[ExtraPartition]) \
        -> int:
    if efi_size < _minimum_efi_size(kernel_size):
        fail('EFI partition is too small to hold the kernel.')

    total_extra_size = 0
    for ep in extra_partitions:
        total_extra_size += ep.size

    return (2 * mib +      # Blank space in front
            efi_size +     # EFI partition
            swap_size +    # Swap partition
            root_size +    # Squashfs root partition
            verity_size +  # Verity root partition
            total_extra_size +
            2 * mib)       # Blank space in back


def _parse_extra_partition_value(value: str) -> typing.Optional[ExtraPartition]:
    parts = value.split(':')
    while len(parts) < 4:
        parts.append('')

    size = disk.mib_ify(disk.byte_size(parts[0]))
    assert size

    return ExtraPartition(size=size, filesystem=parts[1], label=parts[2],
                          contents=parts[3])


def parse_extra_partitions(extra_partition_data: typing.List[str]) \
        -> typing.List[ExtraPartition]:
    result = []  # type: typing.List[ExtraPartition]
    for ep in extra_partition_data:
        parsed_ep = _parse_extra_partition_value(ep) if ep else None
        if parsed_ep:
            result.append(parsed_ep) 
    return result


def _file_size(file_name: str) -> int:
    if file_name:
        statinfo = os.stat(file_name)
        return statinfo.st_size
    return 0


def create_image(image_filename: str, image_format: str,
                 extra_partitions: typing.List[ExtraPartition],
                 efi_size: int, swap_size: int, *,
                 kernel_file: typing.Optional[str],
                 root_partition: str, verity_partition: str,
                 root_hash: str) -> None:
    debug('Creating image "{}".'.format(image_filename))

    kernel_size = _file_size(kernel_file) if kernel_file else 0
    root_size = _file_size(root_partition)
    verity_size = _file_size(verity_partition)

    trace('Got sizes from repository: kernel: {}b, root: {}b, verity: {}b'
          .format(kernel_size, root_size, verity_size))

    extra_total = 0
    for ep in extra_partitions:
        extra_total += ep.size
    trace('Calculated total extra partition size: {}b'.format(extra_total))

    efi_size = _calculate_efi_size(kernel_size, efi_size)
    trace('EFI size: {}b, Swap size: {}b, extra partitions: {}'
          .format(efi_size, swap_size, extra_total))

    min_device_size =\
        _calculate_minimum_size(kernel_size, root_size, verity_size, efi_size,
                                swap_size, extra_partitions)

    verbose('Sizes: kernel: {}b, root: {}b, verity: {}b '
            '=> min device size: {}b'
            .format(kernel_size, root_size, verity_size, min_device_size))

    writer = FileDataProvider(root_partition, verity_partition, kernel_file)
    _work_on_device_node(
        RawImageConfig(path=image_filename,
                       disk_format=image_format,
                       force=True, repartition=True,
                       min_device_size=min_device_size,
                       efi_size=efi_size, root_size=root_size,
                       verity_size=verity_size,
                       swap_size=swap_size,
                       efi_label=None,
                       root_label=os.path.basename(root_partition),
                       verity_label=os.path.basename(verity_partition),
                       root_hash=root_hash,
                       swap_label=None,
                       extra_partitions=extra_partitions,
                       writer=writer))


def _work_on_device_node(ic: RawImageConfig):
    with _find_or_create_device_node(ic.path, ic.disk_format,
                                     ic.min_device_size) as device:

        info('Working on device {}.'.format(ic.path))

        partition_devices = _repartition(device, ic.repartition,
                                         ic.root_label, ic.verity_label,
                                         efi_size=ic.efi_size,
                                         root_size=ic.root_size,
                                         verity_size=ic.verity_size,
                                         root_hash=ic.root_hash,
                                         swap_size=ic.swap_size,
                                         extra_partitions=ic.extra_partitions)
        for name, dev in partition_devices.items():
            trace('Created partition "{}": {}.'.format(name, dev))

        success('Partitions created.', verbosity=2)

        if 'swap' in partition_devices:
            helper_run('/usr/bin/mkswap', '-L', 'main',
                       partition_devices['swap'])
        assert 'root' in partition_devices
        ic.writer.write_root_partition(partition_devices['root'])
        success('Root partition installed.', verbosity=2)

        assert 'verity' in partition_devices
        ic.writer.write_verity_partition(partition_devices['verity'])
        success('Verity partition installed.', verbosity=2)

        if ic.writer.has_linux_kernel():
            assert 'efi' in partition_devices
            _prepare_efi_partition(partition_devices['efi'],
                                   partition_devices['root'],
                                   ic.writer.write_linux_kernel)
            success('EFI partition installed.', verbosity=2)
        else:
            success('EFI partition SKIPPED (no kernel)', verbosity=2)

        for i in range(len(ic.extra_partitions)):
            ep = ic.extra_partitions[i]
            _prepare_extra_partition(partition_devices['extra{}'.format(i+1)],
                                     filesystem=ep.filesystem, label=ep.label,
                                     contents=ep.contents)
        success('Extra partitions installed.', verbosity=2)


def _find_or_create_device_node(path: str, disk_format: str,
                                min_device_size: int) -> typing.ContextManager:
    if disk.is_block_device(path):
        _validate_size_of_block_device(path, min_device_size)
        return disk.Device(path)
    return _create_nbd_device(path, disk_format, min_device_size)


def _validate_size_of_block_device(path: str, min_device_size: int) -> None:
    result = helper_run('/usr/bin/blockdev', '--getsize64', path,
                        trace_output=trace)
    if int(result.stdout) < min_device_size:
        fail('"{}" is too small for image data. Minimum size is {}b.'
             .format(path, min_device_size))


def _create_nbd_device(path: str, disk_format: str, min_device_size: int) \
        -> disk.Device:
    return disk.NbdDevice.new_image_file(path, min_device_size,
                                         disk_format=disk_format)


def _uuidify(data: str) -> str:
    assert len(data) == 32
    return '{}-{}-{}-{}-{}'.format(data[0:8],
                                   data[8:12], data[12:16], data[16:20],
                                   data[20:])


def _repartition(device: disk.Device, repartition: bool, root_label: str,
                 verity_label: str, *,
                 root_hash: str,
                 efi_size: int, root_size: int,
                 verity_size: int, swap_size: int = 0,
                 extra_partitions: typing.Tuple[ExtraPartition, ...] = ()) \
        -> typing.Mapping[str, str]:
    partitioner = disk.Partitioner(device)

    if partitioner.is_partitioned() and not repartition:
        fail('"{}" is already partitioned, use --repartition to force '
             'repartitioning.'.format(device.device()))

    root_uuid = _uuidify(root_hash[:32]) if root_hash else ''
    vrty_uuid = _uuidify(root_hash[32:]) if root_hash else ''

    if root_hash:
        debug('Root hash: {}.'.format(root_hash))
        debug('Root partition UUID: {}.'.format(root_uuid))
        debug('Vrty partition UUID: {}.'.format(vrty_uuid))

    trace('Setting basic partitions')
    partitions = [partitioner.efi_partition(start='2m', size=efi_size),
                  partitioner.data_partition(size=root_size,
                                             name=root_label,
                                             partition_type='4f68bce3-e8cd-'
                                                            '4db1-96e7-'
                                                            'fbcaf984b709',
                                             partition_uuid=root_uuid),
                  partitioner.data_partition(size=verity_size,
                                             name=verity_label,
                                             partition_type='2c7357ed-ebd2-'
                                                            '46d9-aec1-'
                                                            '23d437ec2bf5',
                                             partition_uuid=vrty_uuid)]
    devices = {'efi': device.device(1), 'root': device.device(2),
               'verity': device.device(3)}

    trace('Adding swap (if necessary)')
    if swap_size > 0:
        partitions.append(partitioner.swap_partition(size=swap_size))
        devices['swap'] = device.device(4)

    extra_counter = 0
    debug('Adding extra partitions: {}.'.format(extra_partitions))
    for ep in extra_partitions:
        extra_counter += 1

        name = 'extra{}'.format(extra_counter)

        label = name if ep.label is None else ep.label
        partitions.append(partitioner.data_partition(size=ep.size, name=label))
        devices[name] = device.device(4 + extra_counter)

    trace('*** REPARTITION NOW ***')
    partitioner.repartition(partitions)

    return devices


def _copy_efi_file(source: str, destination: str) -> None:
    shutil.copyfile(source, destination)
    os.chmod(destination, 0o755)


def _prepare_efi_partition(efi_dev: str, root_dev: str, kernel_file_writer) \
        -> None:
    trace('Preparing EFI partition.')
    _prepare_extra_partition(efi_dev, filesystem='vfat', label='EFI')

    trace('... Partition created.')
    cwd = os.getcwd()
    with tempfile.TemporaryDirectory() as mnt_point:
        boot_mnt = os.path.join(mnt_point, 'boot')
        root_mnt = os.path.join(mnt_point, 'root')
        try:
            os.makedirs(boot_mnt)
            helper_run('/usr/bin/mount', '-t', 'vfat', efi_dev, boot_mnt,
                       trace_output=trace)
            os.makedirs(root_mnt)
            helper_run('/usr/bin/mount', '-t', 'squashfs', root_dev, root_mnt,
                       trace_output=trace)

            trace('... boot and root are mounted.')

            loader = os.path.join(root_mnt,
                                  'usr/lib/systemd/boot/efi/'
                                  'systemd-bootx64.efi')
            os.makedirs(os.path.join(boot_mnt, 'EFI/Boot'))
            trace('... "EFI/boot" directory created.')
            _copy_efi_file(loader, os.path.join(boot_mnt,
                                                'EFI/Boot/BOOTX64.EFI'))
            trace('... default boot loader installed')
            os.makedirs(os.path.join(boot_mnt, 'EFI/systemd'))
            trace('... "EFI/systemd" directory created.')
            _copy_efi_file(loader, os.path.join(boot_mnt,
                                                'EFI/systemd/'
                                                'systemd-bootx64.efi'))
            trace('... systemd boot loader installed.')
            os.makedirs(os.path.join(boot_mnt, 'loader/entries'))
            with open(os.path.join(boot_mnt, 'loader/loader.conf'), 'w') as lc:
                lc.write('#timeout 3\n')
                lc.write('default linux-*\n')

            trace('... loader.conf written.')

            linux_dir = os.path.join(boot_mnt, 'EFI/Linux')
            os.makedirs(linux_dir)
            trace('... "EFI/Linux" created.')
            kernel_file_writer(linux_dir)
            trace('... kernel installed')

        finally:
            trace('... cleaning up.')
            os.chdir(cwd)
            helper_run('/usr/bin/umount', boot_mnt,
                       trace_output=trace, returncode=None)
            helper_run('/usr/bin/umount', root_mnt,
                       trace_output=trace, returncode=None)


def _file_to_partition(device: str, file_name: str) -> None:
    shutil.copyfile(file_name, device)


def _format_partition(device: str, filesystem: str, *label_args: str) -> None:
    helper_run('/usr/bin/mkfs.{}'.format(filesystem), *label_args, device)


def _prepare_extra_partition(device: str, *,
                             filesystem: typing.Optional[str] = None,
                             label: typing.Optional[str] = None,
                             contents: typing.Optional[str] = None) -> None:
    if filesystem is None:
        assert contents is None
        return

    verbose('Preparing extra partition on {} using {}.'.format(device,
                                                               filesystem))

    label_args = ()  # type: typing.Tuple[str, ...]
    if label is not None:
        debug('... setting label to "{}".'.format(label))
        if filesystem == 'fat' or filesystem == 'vfat':
            label_args = ('-n', label,)
        if filesystem.startswith('ext') or filesystem == 'btrfs' \
                or filesystem == 'xfs':
            label_args = ('-L', label,)

    _format_partition(device, filesystem, *label_args)

    if contents is not None:
        # FIXME: Implement this!
        assert contents is None
        return
