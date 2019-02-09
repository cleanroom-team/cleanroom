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


# Install types:

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
        target_directory = parse_result.target_directory
        if not os.path.isdir(target_directory):
            if parse_result.create_directory:
                os.makedirs(target_directory)

        assert os.path.isdir(target_directory)

        with TemporaryDirectory(prefix='clrm_dir_',
                                dir=target_directory) as tempdir:
            extracted_version \
                = write_image(parse_result.system_name, tempdir,
                              repository=parse_result.repository,
                              version=parse_result.system_version)

            exported_file_name = 'clrm_{}'.format(extracted_version)
            exported_file = os.path.join(tempdir, exported_file_name)
            assert os.path.isfile(exported_file)

            if parse_result.group or parse_result.owner:
                chown(exported_file,
                      user=parse_result.owner or 'root',
                      group=parse_result.group or 'root')
            if parse_result.mode:
                os.chmod(exported_file, parse_result.mode)

            os.rename(exported_file, os.path.join(target_directory,
                                                  exported_file_name))

            # Create symlink:
            link_location = os.path.join(target_directory, 'latest.img')
            if os.path.islink(link_location):
                os.unlink(link_location)
            os.symlink('./{}'.format(exported_file_name), link_location)
            if parse_result.group or parse_result.owner:
                chown(link_location,
                      user=parse_result.owner or 'root',
                      group=parse_result.group or 'root')


class RunQemu(InstallTarget):
    def __init__(self) -> None:
        super().__init__('qemu', 'Start image in qemu')

    def __call__(self, parse_result: typing.Any) -> None:
        with TemporaryDirectory(prefix='clrm_qemu_') as tempdir:
            extracted_version \
                    = write_image(parse_result.system_name, tempdir,
                                  repository=parse_result.repository,
                                  version=parse_result.system_version)

            assert os.path.isfile(os.path.join(tempdir,
                                               'clrm_{}'.format(extracted_version)))

            copyfile('/usr/share/ovmf/x64/OVMF_VARS.fd',
                     os.path.join(tempdir, 'vars.fd'))
            subprocess.run(['/usr/bin/qemu-system-x86_64', '--enable-kvm',
                            '-cpu', 'host', '-smp', 'cores=2', '-machine',
                            'pc-q35-2.12', '-accel', 'kvm', '-m', 'size=8G',
                            '-object', 'rng-random,filename=/dev/urandom,id=rng0',
                            '-device', 'virtio-rng-pci,rng=rng0,'
                                       'max-bytes=512,period=1000',
                            '-netdev', 'user,id=nic0,hostname=unknown',
                            '-device', 'virtio-net,netdev=nic0',
                            '-drive', 'file={}/clrm_{},format=raw,if=none,id=disk0'
                           .format(tempdir, extracted_version),
                            '-device', 'virtio-blk-pci,drive=disk0,bootindex=0',
                            '-drive', 'if=pflash,format=raw,readonly,'
                                      'file=/usr/share/ovmf/x64/OVMF_CODE.fd',
                            '-drive', 'if=pflash,format=raw,file={}/vars.fd'
                           .format(tempdir)],
                            cwd=tempdir, check=True)

    def setup_subparser(self, parser: typing.Any) -> None:
        parser.add_argument('--cores', dest='cores', action='store',
                            nargs='?', default=2,
                            help='Number of cores to use.')
        parser.add_argument('--memory', dest='memory', action='store',
                            nargs='?', default='4G',
                            help='Memory')
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

        parser.add_argument('--verbatim', dest='verbatim', action='append',
                            help='Argument to copy verbatim to qemu.')


# Main section:

def main(*command_args: str):
    known_install_targets = [Directory(), RunQemu()]

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
