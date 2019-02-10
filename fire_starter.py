#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Main CleanRoom binary.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from argparse import ArgumentParser

import os
from shutil import chown, copyfile
import subprocess
import sys
from tempfile import TemporaryDirectory
import typing


class InstallTarget(object):
    def __init__(self, name: str, help_string: str) -> None:
        self._name = name
        self._help_string = help_string

    def __call__(self, parse_result: typing.Any) -> None:
        assert False

    def setup_subparser(self, subparser: typing.Any) -> None:
        assert False

    @property
    def help_string(self) -> str:
        return self._help_string

    @property
    def name(self) -> str:
        return self._name


borg = '/usr/bin/borg'

borg_env = os.environ
borg_env['LC_ALL'] = 'en_US.UTF-8'


# Helper code:


def _parse_commandline(*args: str,
                       install_targets: typing.List[InstallTarget]) \
        -> typing.Any:
    """Parse the command line options."""
    parser = ArgumentParser(description='Cleanroom OS image fire starter',
                            prog=args[0])

    parser.add_argument('--repository', dest='repository', type=str,
                        action='store', required=True,
                        help='The repository of systems to work with.')

    parser.add_argument(dest='system_name', metavar='<system>', type=str,
                        help='system to install')
    parser.add_argument('--system-version', dest='system_version',
                        default='', type=str,
                        help='version of system to install.')

    subparsers = parser.add_subparsers(help='Installation target specifics',
                                       dest='target_type')
    for it in install_targets:
        it.setup_subparser(subparsers.add_parser(it.name,
                                                 help=it.help_string))

    return parser.parse_args(args[1:])


# Library:

def _run_borg(*args, work_directory: str = '') -> subprocess.CompletedProcess:
    cwd = work_directory or None
    return subprocess.run([borg, *args],
                          env=borg_env, capture_output=True, check=True,
                          cwd=cwd)


def _find_archive(system_name: str, *, repository: str, version: str = '') \
        -> typing.Tuple[str, str]:
    borg_list = _run_borg('list', repository)

    archive_to_use = ''
    for line in borg_list.stdout.decode('utf-8').split('\n'):
        if not line.startswith(system_name):
            continue
        versioned_system_name = line.split(' ')[0]
        assert versioned_system_name[len(system_name)] == '-'
        current_version = versioned_system_name[len(system_name) + 1:]
        if version:
            if current_version == version:
                archive_to_use = versioned_system_name
                break
        else:
            if not archive_to_use or versioned_system_name > archive_to_use:
                archive_to_use = versioned_system_name

    return archive_to_use, archive_to_use[len(system_name) + 1:]


def _extract_archive(archive: str, target_directory: str, *,
                     repository: str) -> None:
    _run_borg('extract', '{}::{}'.format(repository, archive),
              work_directory=target_directory)


def write_image(system_name: str, target_directory: str, *,
                repository: str, version: str = '') -> str:
    (archive_to_extract, extracted_version) \
        = _find_archive(system_name, repository=repository, version=version)
    if not archive_to_extract:
        if version:
            print('Could not find version "{}" of system "{}" to extract.'
                  .format(version, system_name))
        else:
            print('Could not find system "{}" to extract'.format(system_name))
        sys.exit(2)

    _extract_archive(archive_to_extract, target_directory,
                     repository=repository)

    return extracted_version


def setup_loop_device(file_name: str) -> str:
    subprocess.run(['/usr/bin/losetup', '-f', '-P', file_name],
                   env=borg_env, capture_output=True, check=True)

    verify_result = subprocess.run(['/usr/bin/losetup', '-l'],
                                   env=borg_env, capture_output=True,
                                   check=True)
    for l in verify_result.stdout.decode('utf-8').split('\n'):
        if ' {} '.format(file_name) in l:
            dev = l[:l.find(' ')]
            return dev

    return ''


def close_loop_device(device: str) -> None:
    if device:
        print('Disconnected {}.'.format(device))
        subprocess.run(['/usr/bin/losetup', '-d', device],
                       env=borg_env, capture_output=True, check=True)


def mount(device: str, location: str = '', *,
          fs_type: str = '', options: str = '') -> None:
    args = ['/usr/bin/mount']
    args += ['-t', fs_type] if fs_type else []
    args += ['-o', options] if options else []
    args += [device]
    args += [location] if location else []

    if location:
        print('Mounting {} on {}.'.format(device, location))
    else:
        print('Mounting {} based on fstab entry.'.format(device))

    subprocess.run(args, env=borg_env, capture_output=True, check=True)


def unmount(location: str = '') -> None:
    args = ['/usr/bin/umount', location]
    print('Unmounting {}.'.format(location))

    subprocess.run(args, env=borg_env, capture_output=True, check=True)


def has_mount(location: str) -> bool:
    mounts = subprocess.run(['/usr/bin/mount'], env=borg_env,
                            capture_output=True, check=True)

    for l in mounts.stdout.decode('utf-8').split('\n'):
        if ' on {} type '.format(location) in l:
            return True

    return False


def export_into_directory(system_name: str, target_directory: str, *,
                          repository: str, version: str = '',
                          create_directory: bool = False,
                          owner: str = '', group: str = '',
                          mode: int = 0) -> str:
    if not os.path.isdir(target_directory):
        if create_directory:
            os.makedirs(target_directory)

    assert os.path.isdir(target_directory)

    with TemporaryDirectory(prefix='clrm_dir_',
                            dir=target_directory) as tempdir:
        extracted_version \
            = write_image(system_name, tempdir,
                          repository=repository,
                          version=version)

        exported_file_name = 'clrm_{}'.format(extracted_version)
        exported_file = os.path.join(tempdir, exported_file_name)
        assert os.path.isfile(exported_file)

        if group or owner:
            chown(exported_file, user=owner or 'root', group=group or 'root')
        if mode:
            os.chmod(exported_file, mode)

        target_file = os.path.join(target_directory, exported_file_name)
        os.rename(exported_file, target_file)

        # Create symlink:
        link_location = os.path.join(target_directory, 'latest.img')
        if os.path.islink(link_location):
            os.unlink(link_location)
        os.symlink('./{}'.format(exported_file_name), link_location)
        if group or owner:
            chown(link_location, user=owner or 'root', group=group or 'root')

        return target_file


# Install types:

class ImagePartition(InstallTarget):
    def __init__(self) -> None:
        super().__init__('image_partition',
                         'export image into image_partition and update EFI.')

    def setup_subparser(self, parser: typing.Any) -> None:
        parser.add_argument(dest='target_directory', action='store',
                            help='The directory to export into.')

        parser.add_argument('--create-target-directory',
                            dest='create_directory', action='store_true')

    def __call__(self, parse_result: typing.Any) -> None:
        loop_dev = ''
        tmp_boot_mnt = ''
        unmount_target = False
        unmount_boot = False

        with TemporaryDirectory() as tempdir:
            try:
                if not has_mount(parse_result.target_directory):
                    mount(parse_result.target_directory)
                    unmount_target = True

                exported_file \
                    = export_into_directory(parse_result.system_name,
                                            parse_result.target_directory,
                                            version=parse_result.system_version,
                                            repository=parse_result.repository,
                                            create_directory=parse_result
                                            .create_directory)

                loop_dev = setup_loop_device(exported_file)
                assert loop_dev

                tmp_boot_mnt = os.path.join(tempdir, 'boot')
                os.makedirs(tmp_boot_mnt)
                mount('{}p1'.format(loop_dev), tmp_boot_mnt, fs_type='vfat')

                if not has_mount('/boot'):
                    mount('/dev/sda1', '/boot')
                    unmount_boot = True

                if not os.path.isdir('/boot/EFI/Linux'):
                    os.makedirs('/boot/EFI/Linux')

                kernels_dir = os.path.join(tmp_boot_mnt, 'EFI/Linux')
                for f in [f for f in os.listdir(kernels_dir)
                          if os.path.isfile(os.path.join(kernels_dir, f))]:
                    copyfile(os.path.join(kernels_dir, f),
                             os.path.join('/boot/EFI/Linux', f))

            finally:
                if tmp_boot_mnt:
                    unmount(tmp_boot_mnt)
                if loop_dev:
                    close_loop_device(loop_dev)

                if unmount_target:
                    unmount(parse_result.target_directory)
                if unmount_boot:
                    unmount('/boot')


class Directory(InstallTarget):
    def __init__(self) -> None:
        super().__init__('directory', 'export image into directory')

    def setup_subparser(self, parser: typing.Any) -> None:
        parser.add_argument(dest='target_directory', action='store',
                            help='The directory to export into.')
        parser.add_argument('--mode', action='store', default=0, type=int,
                            help='mode of exported file.')
        parser.add_argument('--owner', action='store',
                            help='owner of exported file')
        parser.add_argument('--group', action='store',
                            help='group of exported file')

        parser.add_argument('--create-target-directory',
                            dest='create_directory',
                            action='store_true')

    def __call__(self, parse_result: typing.Any) -> None:
        export_into_directory(parse_result.system_name,
                              parse_result.target_directory,
                              version=parse_result.system_version,
                              repository=parse_result.repository,
                              create_directory=parse_result.create_directory,
                              owner=parse_result.owner,
                              group=parse_result.group,
                              mode=parse_result.mode)


def _append_network(hostname, *, hostfwd=[], mac='', net='', host=''):
    hostfwd_args = ['hostfwd={}'.format(p) for p in hostfwd]

    hostfwd_str = ',' + ','.join(hostfwd_args) if hostfwd_args else ''
    mac_str = ',mac={}'.format(mac) if mac else ''
    host_str = ',host={}'.format(host) if host else ''
    net_str = ',net={}'.format(net) if net else ''

    # -netdev bridge,id=bridge1,br=qemubr0
    # -device virtio-net,netdev=bridge1,mac=52:54:00:12:01:c1

    return ['-netdev', 'user,id=nic0,hostname={}{}{}{}'
            .format(hostname, hostfwd_str, net_str, host_str),
            '-device', 'virtio-net,netdev=nic0{}'.format(mac_str)]


def _append_hdd(bootindex, disk):
    disk_parts = disk.split(':')
    if len(disk_parts) < 2:
        disk_parts.append('qcow2')
    assert len(disk_parts) == 2

    c = _append_hdd.counter;
    _append_hdd.counter += 1

    return ['-drive', 'file={},format={},if=none,id=disk{}'
                      .format(disk_parts[0], disk_parts[1], c),
            '-device', 'virtio-blk-pci,drive=disk{},bootindex={}'
                       .format(c, bootindex)]


_append_hdd.counter = 0


def _append_fs(fs, *, read_only=False):
    fs_parts = fs.split(':')
    assert len(fs_parts) == 2

    ro = ',read-only' if read_only else ''

    return ['-virtfs',
            'local,id={0},path={1},mount_tag={0},security_mode=passthrough{2}'
            .format(fs_parts[0], fs_parts[1], ro)]


def _append_efi(efivars):
    if not os.path.exists(efivars):
        copyfile('/usr/share/ovmf/x64/OVMF_VARS.fd', efivars)
    return ['-drive', 'if=pflash,format=raw,readonly,'
            'file=/usr/share/ovmf/x64/OVMF_CODE.fd', '-drive',
            'if=pflash,format=raw,file={}'.format(efivars)]


class RunQemu(InstallTarget):
    def __init__(self) -> None:
        super().__init__('qemu', 'Start image in qemu')

    def __call__(self, parse_result: typing.Any) -> None:
        with TemporaryDirectory(prefix='clrm_qemu_') as tempdir:
            extracted_version \
                    = write_image(parse_result.system_name, tempdir,
                                  repository=parse_result.repository,
                                  version=parse_result.system_version)

            extracted_image = os.path.join(tempdir,
                                           'clrm_{}'.format(extracted_version))
            assert os.path.isfile(extracted_image)

            qemu_args = ['/usr/bin/qemu-system-x86_64',
                         '--enable-kvm',
                         '-cpu', 'host',
                         '-smp', 'cores={}'.format(parse_result.cores),
                         '-machine', 'pc-q35-2.12',
                         '-accel', 'kvm',
                         '-m', 'size={}'.format(parse_result.memory),  # memory
                         '-object', 'rng-random,filename=/dev/urandom,id=rng0',
                         '-device',
                         'virtio-rng-pci,rng=rng0,max-bytes=512,period=1000',
                         # Random number generator
                         ]

            qemu_args += _append_network(parse_result.hostname,
                                         hostfwd=parse_result.hostfwd,
                                         mac=parse_result.mac,
                                         net=parse_result.net,
                                         host=parse_result.host)

            bootindex = 0
            qemu_args += _append_hdd(bootindex,
                                     '{}:raw'.format(extracted_image))
            bootindex += 1
            for disk in parse_result.disks:
                qemu_args += _append_hdd(bootindex, disk)
                bootindex += 1

            for fs in parse_result.ro_fses:
                qemu_args += _append_fs(fs, read_only=True)
            for fs in parse_result.fses:
                qemu_args += _append_fs(fs, read_only=False)

            if parse_result.no_graphic:
                qemu_args.append('-nographic')

            qemu_args += _append_efi(os.path.join(tempdir, 'vars.fd'))
            if parse_result.verbatim:
                qemu_args += parse_result.verbatim

            subprocess.run(qemu_args, cwd=tempdir, check=True)

    def setup_subparser(self, parser: typing.Any) -> None:
        parser.add_argument('--no-graphic', dest='no_graphic',
                            action='store_true', help='Use no-graphics mode')

        parser.add_argument('--cores', action='store', nargs='?', default=2,
                            help='Number of cores to use.')
        parser.add_argument('--memory', action='store', nargs='?',
                            default='4G', help='Memory')
        parser.add_argument('--mac', dest='mac', action='store',
                            nargs='?', default='',
                            help='MAC address of main network card')
        parser.add_argument('--net', dest='net', action='store',
                            nargs='?', default='',
                            help='Network address of main network card')
        parser.add_argument('--host', dest='host', action='store',
                            nargs='?', default='',
                            help='Host address of main network card')

        parser.add_argument('--hostname', dest='hostname', action='store',
                            nargs='?', default='unknown',
                            help='Hostname to use for NIC')
        parser.add_argument('--hostfwd', dest='hostfwd',
                            default=[], action='append',
                            help='Port spec to forward from host to guest')

        parser.add_argument('--disk', dest='disks',
                            default=[], action='append',
                            help='Extra disks to add (file[:format])')

        parser.add_argument('--ro-fs', dest='ro_fses',
                            default=[], action='append',
                            help='Host folders to make available to guest -- read-only (id:path)')
        parser.add_argument('--fs', dest='fses',
                            default=[], action='append',
                            help='Host folder to make available to guest (id:path)')

        parser.add_argument('--verbatim', dest='verbatim', action='append',
                            help='Argument to copy verbatim to qemu.')


# Main section:

def main(*command_args: str):
    known_install_targets = [Directory(), ImagePartition(), RunQemu()]

    parse_result = _parse_commandline(*command_args,
                                      install_targets=known_install_targets)

    install_target = next(x for x in known_install_targets
                          if x.name == parse_result.target_type)
    install_target(parse_result)


def run():
    current_directory = os.getcwd()

    try:
        main(*sys.argv)
    finally:
        os.chdir(current_directory)


if __name__ == '__main__':
    run()
