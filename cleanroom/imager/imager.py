#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Main CleanRoom functionality.

FIXME: Allow for different distro ids

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

from ..helper import disc
from ..helper.run import run as helper_run
from ..printer import debug, fail, success, trace, verbose
from ..export import Exporter, ExportContents

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


class BorgDataProvider(DataProvider):
    def __init__(self, contents):
        self._contents = contents 

    def write_root_partition(self, target_device: str):
        self._contents.extract(self._contents.root_name(), '--stdout', stdout=target_device)

    def write_verity_partition(self, target_device: str):
        self._contents.extract(self._contents.verity_name(), '--stdout', stdout=target_device)

    def has_linux_kernel(self):
        return True

    def write_linux_kernel(self, target_directory: str):
        self._contents.extract(self._contents.kernel_name(), work_directory=target_directory)


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
        shutil.copyfile(self._kernel_file, target_directory)


ExtraPartition = collections.namedtuple('ExtraPartition',
                                        ['size', 'filesystem', 'label', 'contents'])
ImageConfig = collections.namedtuple('ImageConfig',
                                     ['path', 'disk_format', 'force', 'repartition',
                                      'efi_size', 'swap_size', 'extra_partitions'])
RawImageConfig = collections.namedtuple('RawImageConfig',
                                        ['path', 'disk_format', 'force', 'repartition',
                                         'min_device_size', 'efi_size', 'root_size',
                                         'verity_size', 'swap_size',
                                         'efi_label', 'root_label', 'verity_label', 'swap_label',
                                         'extra_partitions', 'writer'])


def _parse_extra_partition_value(value: str) -> typing.Optional[ExtraPartition]:
    parts = value.split(':')
    while len(parts) < 4:
        parts.append('')

    size = disc.mib_ify(disc.normalize_size(parts[0]))
    assert size

    return ExtraPartition(size=size, filesystem=parts[1], label=parts[2],
                          contents=parts[3])


def parse_extra_partitions(extra_partition_data: typing.List[str]) -> typing.List[ExtraPartition]:
    result = []  # type: typing.List[ExtraPartition]
    for ep in extra_partition_data:
        parsed_ep = _parse_extra_partition_value(ep) if ep else None
        if parsed_ep:
            result.append(parsed_ep) 
    return result


def _file_size(file_name):
    if file_name:
        statinfo = os.stat(file_name)
        return statinfo.st_size
    return 0


def create_image(image_filename, image_format, extra_partitions,
                 efi_size, swap_size, *,
                 kernel_file, root_partition, verity_partition):
    if os.geteuid() != 0:
        fail('Not running as root.')

    trace('Running as root.')

    debug('Creating image "{}".'.format(image_filename))
    
    kernel_size = _file_size(kernel_file) if kernel_file else 1024*1204
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
    _work_on_device_node(RawImageConfig(path=image_filename,
                                        disk_format=image_format,
                                        force=True, repartition=True,
                                        min_device_size=min_device_size,
                                        efi_size=efi_size, root_size=root_size,
                                        verity_size=verity_size,
                                        swap_size=swap_size,
                                        efi_label=None,
                                        root_label=root_partition,
                                        verity_label=verity_partition,
                                        swap_label=None,
                                        extra_partitions=extra_partitions,
                                        writer=writer))


def _work_on_device_node(ic: RawImageConfig):
    with _find_or_create_device_node(ic.path, ic.disk_format,
                                     ic.min_device_size) as device:

        partition_devices = _repartition(device, ic.repartition,
                                         ic.root_label, ic.verity_label,
                                         efi_size=ic.efi_size,
                                         root_size=ic.root_size,
                                         verity_size=ic.verity_size, swap_size=ic.swap_size,
                                         extra_partitions=ic.extra_partitions)
        for name, dev in partition_devices.items():
            trace('Created partition "{}": {}.'.format(name, dev))

        success('Partitions created.', verbosity=2)

        if 'swap' in partition_devices:
            helper_run('/usr/bin/mkswap', '-L', 'main', partition_devices['swap'])
        assert 'root' in partition_devices
        ic.writer.write_root_partition(partition_devices['root'])
        success('Root partition installed.', verbosity=2)

        assert 'verity' in partition_devices
        ic.writer.write_verity_partition(partition_devices['root'])
        success('Verity partition installed.', verbosity=2)

        if ic.writer.has_linux_kernel():
            assert 'efi' in partition_devices
            _prepare_efi_partition(partition_devices['efi'], partition_devices['root'],
                                   ic.writer.write_kernel_file)
            success('EFI partition installed.', verbosity=2)
        else:
            success('EFI partition SKIPPED (no kernel)', verbosity=2)

        for i in range(len(ic.extra_partitions)):
            ep = ic.extra_partitions[i]
            _prepare_extra_partition(partition_devices['extra{}'.format(i+1)],
                                     filesystem=ep.filesystem, label=ep.label,
                                     contents=ep.contents)
        success('Extra partitions installed.', verbosity=2)


def _size_from_contents(contents, filename):
    file = contents.file(filename)
    return file.size if file else 0


def root_only_part(ic: ImageConfig, system: str, timestamp: str, repository: str) -> None:
    if os.geteuid() != 0:
        fail('Not running as root.')

    trace('Running as root.')

    exporter = Exporter(repository)
    if timestamp is None:
        system_timestamps = exporter.timestamps(system)
        if len(system_timestamps) == 0:
            fail('Could not find system "{}" in repository "{}".'
                 .format(system, repository))
        else:
            timestamp = system_timestamps[-1].timestamp
    else:
        if not exporter.has_system_with_timestamp(system, timestamp):
            fail('Could not find system "{}" with timestamp "{}" in repository "{}".'
                 .format(system, timestamp, repository))

    debug('Using timestamp "{}".'.format(timestamp))

    path = ic.path.replace('XXXXXX', timestamp)

    full_system_name = '{}-{}'.format(system, timestamp)

    debug('Creating image "{}" from "{}".'.format(path, full_system_name))

    contents = exporter.export(system, timestamp)
    _validate_contents(contents)

    kernel_size = _size_from_contents(contents, contents.kernel_name())
    assert kernel_size
    root_size = _size_from_contents(contents, contents.root_name())
    assert root_size
    verity_size = _size_from_contents(contents, contents.verity_name())
    assert verity_size

    trace('Got sizes from repository: kernel: {}b, root: {}b, verity: {}b'
          .format(kernel_size, root_size, verity_size))

    extra_total = 0
    for ep in ic.extra_partitions:
        extra_total += ep.size
    trace('Calculated total extra partition size: {}b'.format(extra_total))

    efi_size = _calculate_efi_size(kernel_size, ic.efi_size)
    trace('EFI size: {}b, Swap size: {}b, extra partitions: {}'
          .format(efi_size, ic.swap_size, extra_total))

    min_device_size = _calculate_minimum_size(kernel_size, root_size, verity_size,
                                              efi_size, ic.swap_size, ic.extra_partitions)
    verbose('Sizes: efi: {}b, root: {}b, verity: {}b => min device size: {}b'
            .format(efi_size, root_size, verity_size, min_device_size))

    raw_ic = RawImageConfig(path=ic.path, disk_format=ic.disk_format, force=ic.force,
                            repartition=ic.repartition,
                            min_device_size=min_device_size, efi_size=efi_size, root_size=root_size,
                            verity_size=verity_size, swap_size=ic.swap_size,
                            efi_label='', root_label='', verity_label='', swap_label='',
                            extra_partitions=ic.extra_partitions,
                            writer=BorgDataProvider(contents))
    _work_on_device_node(raw_ic)


def _backup_name(repository: str, full_system_name: str) -> str:
    return '{}::{}'.format(repository, full_system_name)


def _kernel_name(timestamp: str) -> str:
    return 'linux-{}.efi'.format(timestamp)


def _root_name(timestamp: str) -> str:
    return 'root_{}'.format(timestamp)


def _verity_name(timestamp: str) -> str:
    return 'vrty_{}'.format(timestamp)


def _minimum_efi_size(kernel_size: int) -> int:
    bootloader_size = 1 * mib  # size of systemd-boot (+ some spare)
    return int((kernel_size + 2 * bootloader_size) * 1.05)


def _calculate_efi_size(kernel_size: int, efi_size: int) -> int:
    if efi_size > 0:
        return efi_size
    return _minimum_efi_size(kernel_size)


def _calculate_minimum_size(kernel_size: int, root_size: int, verity_size: int,
                            efi_size: int, swap_size: int,
                            extra_partitions: typing.List[ExtraPartition]) -> int:
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


def _validate_contents(contents: ExportContents) -> None:
    export_type = contents.extract('export_type', '--stdout')
    if export_type != 'export_squashfs':
        fail('Failed with invalid export_type in archive (was "{}")'.format(type))
    trace('export_type contents was export_squashfs, as expected.')


def validate_image_config_path(path: str, force: bool) -> bool:
    if disc.is_block_device(path):
        _validate_device(path, force)
    else:
        _validate_image_file(path, force)
    return True


def _validate_device(path: str, force: bool) -> None:
    if not force:
        fail('You need to --force to work with block device "{}".'
             .format(path))


def _validate_image_file(path: str, force: bool) -> None:
    if os.path.exists(path):
        if not force:
            fail('You need to --force override of existing image file "{}".'
                 .format(path))


def _find_or_create_device_node(path: str, disk_format: str,
                                min_device_size: int) -> typing.ContextManager:
    if disc.is_block_device(path):
        _validate_size_of_block_device(path, min_device_size)
        return disc.Device(path)
    return _create_nbd_device(path, disk_format, min_device_size)


def _validate_size_of_block_device(path: str, min_device_size: int) -> None:
    result = helper_run('/usr/bin/blockdev', '--getsize64', path, trace_output=trace)
    if int(result.stdout) < min_device_size:
        fail('"{}" is too small for image data. Minimum size is {}b.'
             .format(path, min_device_size))


def _create_nbd_device(path: str, disk_format: str, min_device_size: int) \
        -> disc.Device:
    return disc.NbdDevice.new_image_file(path, min_device_size,
                                         disk_format=disk_format)


def _repartition(device: disc.Device, repartition: bool, root_label: str,
                 verity_label: str, *, efi_size: int, root_size: int,
                 verity_size: int, swap_size: int = 0,
                 extra_partitions: typing.Tuple[ExtraPartition, ...] = ()) \
        -> typing.Mapping[str, str]:
    partitioner = disc.Partitioner(device)

    if partitioner.is_partitioned() and not repartition:
        fail('"{}" is already partitioned, use --repartition to force repartitioning.'
             .format(device.device()))

    trace('Setting basic partitions')
    partitions = [partitioner.efi_partition(start='2m', size=efi_size),
                  partitioner.data_partition(size=root_size,
                                             name=root_label),
                  partitioner.data_partition(size=verity_size,
                                             name=verity_label)]
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


def _prepare_efi_partition(device: str, root_dev: str, kernel_file_writer) -> None:
    trace('Preparing EFI partition.')
    _prepare_extra_partition(device, filesystem='vfat', label='EFI')

    trace('... Partition created.')
    cwd = os.getcwd()
    with tempfile.TemporaryDirectory() as mnt_point:
        boot_mnt = os.path.join(mnt_point, 'boot')
        root_mnt = os.path.join(mnt_point, 'root')
        try:
            os.makedirs(boot_mnt)
            helper_run('/usr/bin/mount', '-t', 'vfat', device, boot_mnt, trace_output=trace)
            os.makedirs(root_mnt)
            helper_run('/usr/bin/mount', '-t', 'squashfs', root_dev, root_mnt, trace_output=trace)

            trace('... boot and root are mounted.')

            loader = os.path.join(root_mnt, 'usr/lib/systemd/boot/efi/systemd-bootx64.efi')
            os.makedirs(os.path.join(boot_mnt, 'EFI/Boot'))
            trace('... "EFI/boot" directory created.')
            _copy_efi_file(loader, os.path.join(boot_mnt, 'EFI/Boot/BOOTX64.EFI'))
            trace('... default boot loader installed')
            os.makedirs(os.path.join(boot_mnt, 'EFI/systemd'))
            trace('... "EFI/systemd" directory created.')
            _copy_efi_file(loader, os.path.join(boot_mnt, 'EFI/systemd/systemd-bootx64.efi'))
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
            helper_run('/usr/bin/umount', boot_mnt, trace_output=trace, returncode=None)
            helper_run('/usr/bin/umount', root_mnt, trace_output=trace, returncode=None)


def _write_to_partition(device: str, file_name: str, contents: ExportContents) -> None:
    contents.extract(file_name, '--stdout', stdout=device)


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

    verbose('Preparing extra partition on {} using {}.'.format(device, filesystem))

    label_args = ()  # type: typing.Tuple[str, ...]
    if label is not None:
        debug('... setting label to "{}".'.format(label))
        if filesystem == 'fat' or filesystem == 'vfat':
            label_args = ('-n', label,)
        if filesystem.startswith('ext') or filesystem == 'btrfs' or filesystem == 'xfs':
            label_args = ('-L', label,)

    _format_partition(device, filesystem, *label_args)

    if contents is not None:
        # FIXME: Implement this!
        assert contents is None
        return
