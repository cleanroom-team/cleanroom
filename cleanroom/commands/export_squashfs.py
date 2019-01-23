# -*- coding: utf-8 -*-
"""export_squashfs command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.exceptions import GenerateError, ParseError
from cleanroom.location import Location
from cleanroom.generator.context import Binaries
from cleanroom.generator.exportcommand import ExportCommand
from cleanroom.generator.helper.generic.file import exists
from cleanroom.generator.systemcontext import SystemContext
from cleanroom.helper import disk
from cleanroom.helper.btrfs import create_subvolume, delete_subvolume, \
                                   delete_subvolume_recursive, has_subvolume
from cleanroom.imager.imager import ExtraPartition, create_image, \
                                    parse_extra_partitions
from cleanroom.printer import debug

import os.path
import shutil
import typing


def _kernel_name(system_context: SystemContext) -> str:
    boot_data = system_context.boot_data_directory()
    assert boot_data
    return os.path.join(boot_data,
                        'linux-{}.efi'.format(system_context.timestamp))


def _create_initramfs(location: Location, system_context: SystemContext) -> bool:
    location.set_description('Create initrd')
    initrd_parts = os.path.join(system_context
                                .boot_data_directory(),
                                'initrd-parts')
    os.makedirs(initrd_parts, exist_ok=True)
    system_context.execute(location.next_line(), 'create_initrd',
                           os.path.join(initrd_parts, '50-mkinitcpio'))

    return os.path.exists(os.path.join(system_context.boot_data_directory(),
                          'initrd-parts/50-mkinitcpio'))


def _create_efi_kernel(location: Location, system_context: SystemContext,
                       kernel_name: str, cmdline: str) -> None:
    location.set_description('Create EFI kernel')
    boot_data = system_context.boot_data_directory()
    system_context.execute(location.next_line(), 'create_efi_kernel', kernel_name,
                           kernel=os.path.join(system_context.boot_data_directory(),
                                               'vmlinuz'),
                           initrd=os.path.join(boot_data, 'initrd-parts'),
                           commandline=cmdline)


def _sign_efi_kernel(location: Location, system_context: SystemContext,
                     kernel: str, key: str, cert: str) -> None:
    location.set_description('Sign EFI kernel')
    system_context.execute(location.next_line(), 'sign_efi_binary', kernel,
                           key=key, cert=cert, outside=True)


def _size_extend(file: str) -> None:
    size = os.path.getsize(file)
    block_size = 4 * 1024 * 1024  # 4MiB
    to_add = block_size - (size % block_size)
    if to_add == 0:
        return

    with open(file, 'ab') as f:
        f.write(b'\0' * to_add)


def _create_squashfs(system_context: SystemContext, target_directory: str) -> str:
    squash_file = os.path.join(target_directory, 'root_{}'
                               .format(system_context.timestamp))
    mksquashfs = system_context.binary(Binaries.MKSQUASHFS)
    system_context.run(mksquashfs, 'usr', squash_file, '-comp', 'zstd',
                       '-noappend', '-no-exports', '-keep-as-directory',
                       '-noI', '-noD', '-noF', '-noX', '-processors', '1',
                       outside=True,
                       work_directory=system_context.fs_directory())
    _size_extend(squash_file)
    return squash_file


def _create_dmverity(system_context: SystemContext, target_directory: str,
                     squashfs_file: str) -> typing.Tuple[str, str, str]:
    verity_file = os.path.join(target_directory, 'vrty_{}'
                               .format(system_context.timestamp))
    veritysetup = system_context.binary(Binaries.VERITYSETUP)
    result = system_context.run(veritysetup, 'format',
                                squashfs_file, verity_file, outside=True)

    _size_extend(verity_file)

    root_hash = None
    uuid = None
    for line in result.stdout.split('\n'):
        if line.startswith('Root hash:'):
            root_hash = line[10:].strip()
        if line.startswith('UUID:'):
            uuid = line[10:].strip()

    assert root_hash is not None
    assert uuid is not None
    return verity_file, uuid, root_hash


def _setup_kernel_commandline(base_cmdline: str,
                              squashfs_device: str, verity_device: str,
                              root_hash: str) -> str:
    cmdline = ' '.join((base_cmdline,
                        'systemd.verity=yes',
                        'systemd.verity_root_data={}'.format(squashfs_device),
                        'systemd.verity_root_hash={}'.format(verity_device),
                        'roothash={}'.format(root_hash),
                        'FOO'))
    return cmdline


class ExportSquashfsCommand(ExportCommand):
    """The export_squashfs Command."""

    def __init__(self) -> None:
        """Constructor."""
        self._key = None  # type: typing.Optional[str]
        self._cert = None  # type: typing.Optional[str]
        self._volume_group = None  # type: typing.Optional[str]

        self._image_format = 'raw'
        self._image_compression = 'zstd'
        self._extra_partitions = []  # type: typing.List[ExtraPartition]
        self._efi_size = 0
        self._swap_size = 0

        self._kernel_file = None  # type: typing.Optional[str]
        self._root_partition = None  # type: typing.Optional[str]
        self._verity_partition = None  # type: typing.Optional[str]

        super().__init__('export_squashfs',
                         syntax='[efi_key=<KEY>] [efi_cert=<CERT>] '
                         '[efi_size=0M] [swap_size=0M] '
                         '[extra_partitions=p1,p2,...] '
                         '[image_format=(raw|qcow2)]',
                         help='Export a filesystem image.',
                         file=__file__)

    def validate_arguments(self, location: Location, *args: typing.Any, **kwargs: typing.Any) \
            -> typing.Optional[str]:
        """Validate arguments."""
        self._validate_no_args(location, *args)
        self._validate_no_args(location, *args)
        self._validate_kwargs(location, ('efi_key', 'efi_cert',
                                         'efi_size', 'swap_size',
                                         'extra_partitions',
                                         'image_format',),
                              **kwargs)

        if 'key' in kwargs:
            if 'cert' not in kwargs:
                raise ParseError('"{}": cert keyword is required when key keyword is given.',
                                 location=location)
        else:
            if 'cert' in kwargs:
                raise ParseError('"{}": key keyword is required when cert keyword is given.',
                                 location=location)

        return None

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        self._key = kwargs.get('efi_key')
        self._cert = kwargs.get('efi_cert')
        self._image_format = kwargs.get('image_format', 'raw')
        self._extra_partitions = \
            parse_extra_partitions(kwargs.get('extra_partitions', '').split(','))

        self._efi_size = disk.mib_ify(kwargs.get('efi_size', 0))
        self._swap_size = disk.mib_ify(kwargs.get('swap_size', 0))
        assert self._image_format in ('raw', 'qcow2',)

        return super().__call__(location, *args, **kwargs)

    def _create_root_tarball(self, location: Location, system_context: SystemContext) -> None:
        tarball = 'usr/lib/boot/root-fs.tar'
        system_context.execute(location, 'mkdir', '/usr/lib/boot')

        if exists(system_context, tarball):
            raise GenerateError('"{}": Root tarball "{}" already exists.'
                                .format(self.name(), tarball), location=location)
        system_context.run(system_context.binary(Binaries.TAR), '-cf', tarball,
                           '--sort=name', 'etc', 'root',
                           work_directory=system_context.fs_directory(), outside=True)

    def prepare_for_export(self, location: Location, system_context: SystemContext) -> None:
        self._create_root_tarball(location, system_context)
        has_kernel = _create_initramfs(location, system_context)

        (self._kernel_file, self._root_partition, self._verity_partition,) = \
            self._create_cache_data(location, system_context, has_kernel=has_kernel)

    def _create_complete_kernel(self, location: Location, system_context: SystemContext,
                                base_cmdline: str, squashfs_device: str, verity_device: str,
                                root_hash: str, target_directory: str) -> str:
        full_cmdline = _setup_kernel_commandline(base_cmdline, squashfs_device, verity_device, root_hash)
        kernel_name = _kernel_name(system_context)

        _create_efi_kernel(location, system_context, kernel_name, full_cmdline)

        if self._key is not None and self._cert is not None:
            debug('Signing EFI kernel.')
            _sign_efi_kernel(location, system_context, kernel_name,
                             self._key, self._cert)

        kernel_filename = os.path.join(target_directory, os.path.basename(kernel_name))
        shutil.copyfile(kernel_name, kernel_filename)

        return kernel_filename

    def _create_cache_data(self, location: Location,
                           system_context: SystemContext, *,
                           has_kernel: bool) \
            -> typing.Tuple[typing.Optional[str], str, str]:
        squashfs_file = _create_squashfs(system_context,
                                         system_context.cache_directory())
        (verity_file, verity_uuid, root_hash) \
            = _create_dmverity(system_context,
                               system_context.cache_directory(),
                               squashfs_file)

        verity_device = 'UUID={}'.format(verity_uuid)
        partlabel = system_context.substitution('ROOTFS_PARTLABEL', '')
        if not partlabel:
            partlabel = '{}_{}'.format(system_context.substitution('DISTRO_ID', 'clrm'),
                                       system_context.substitution('DISTRO_VERSION_ID',
                                       system_context.timestamp))
        squashfs_device = 'PARTLABEL={}'.format(partlabel)

        cmdline = system_context.substitution('KERNEL_CMDLINE', '')
        cmdline = ' '.join((cmdline, 'systemd.volatile=true', 'rootfstype=squashfs')).strip()

        kernel_file = None
        if has_kernel:
            kernel_file = \
                self._create_complete_kernel(location, system_context,  cmdline,
                                             squashfs_device, verity_device, root_hash,
                                             system_context.cache_directory())

        return kernel_file, squashfs_file, verity_file

    def create_export_directory(self, location: Location,
                                system_context: SystemContext) -> str:
        """Return the root directory."""
        assert system_context.ctx
        work_directory = system_context.ctx.work_directory()
        assert work_directory
        export_volume = os.path.join(work_directory, 'export')
        if has_subvolume(export_volume, command=system_context.binary(Binaries.BTRFS)):
            delete_subvolume_recursive(export_volume, command=system_context.binary(Binaries.BTRFS))
        create_subvolume(export_volume, command=system_context.binary(Binaries.BTRFS))

        os_name = system_context.substitution('DISTRO_ID', 'clrm')
        timestamp = system_context.substitution('TIMESTAMP', 'unknown')

        image_filename = os.path.join(export_volume,
                                      '{}-{}.{}'.format(os_name, timestamp, self._image_format))
        create_image(image_filename, self._image_format,
                     self._extra_partitions,
                     self._efi_size, self._swap_size,
                     kernel_file=self._kernel_file,
                     root_partition=self._root_partition,
                     verity_partition=self._verity_partition)

        return export_volume

    def delete_export_directory(self, system_context: SystemContext, export_directory: str) -> None:
        """Nothing to see, move on."""
        delete_subvolume(export_directory, command=system_context.binary(Binaries.BTRFS))
