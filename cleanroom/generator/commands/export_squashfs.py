# -*- coding: utf-8 -*-
"""export_squashfs command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

from cleanroom.generator.context import (Binaries, Context,)
from cleanroom.generator.exportcommand import ExportCommand
from cleanroom.generator.helper.generic.file import exists

from cleanroom.exceptions import (GenerateError, ParseError)
from cleanroom.helper.btrfs import (create_subvolume, delete_subvolume)
from cleanroom.printer import debug

import os.path
import shutil


class ExportSquashfsCommand(ExportCommand):
    """The export_squashfs Command."""

    def __init__(self):
        """Constructor."""
        self._key = None
        self._cert = None
        self._volume_group = None

        super().__init__('export_squashfs',
                         syntax='[key=<KEY>] [cert=<CERT>] [compression=lz4]',
                         help='Export the root filesystem as squashfs.',
                         file=__file__)

    def __call__(self, location, *args, **kwargs):
        """Execute command."""
        self._key = kwargs.get('key')
        self._cert = kwargs.get('cert')
        self._compression = kwargs.get('compression', 'lz4')

        location

        super().__call__(location, *args, **kwargs)

    def _create_root_tarball(self, location, system_context):
        tar_directory = '/usr/lib/boot'
        system_context.execute(location, 'mkdir', tar_directory)

        ## tarball = os.path.join(tar_directory, 'root-fs.tar')
        tarball = os.path.join(tar_directory, 'root-fs.tar')
        if exists(system_context, tarball):
            raise GenerateError('"{}": Root tarball "{}" already exists.'
                                .format(self.name(), tarball), location=location)
        system_context.run('/usr/bin/tar', '-cf', tarball,
                           '--sort=name', 'etc', 'root', work_directory='/')

    def _kernel_name(self, system_context):
        boot_data = system_context.boot_data_directory()
        return os.path.join(boot_data,
                            'linux-{}.efi'.format(system_context.timestamp))

    def _create_initramfs(self, location, system_context):
        location.set_description('Create initrd')
        initrd_parts = os.path.join(system_context
                                    .boot_data_directory(),
                                    'initrd-parts')
        os.makedirs(initrd_parts, exist_ok=True)
        system_context.execute(location.next_line(), 'create_initrd',
                               os.path.join(initrd_parts, '50-mkinitcpio'))

    def prepare_for_export(self, location, system_context):
        self._create_root_tarball(location, system_context)
        self._create_initramfs(location, system_context)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate arguments."""
        self._validate_no_args(location, *args)
        self._validate_kwargs(location, ('key', 'cert', 'compression'), **kwargs)

        if 'key' in kwargs:
            if not 'cert' in kwargs:
                raise ParseError('"{}": cert keyword is required when key keyword is given.',
                                 location=location)
        else:
            if 'cert' in kwargs:
                raise ParseError('"{}": key keyword is required when cert keyword is given.',
                                 location=location)

    def _create_efi_kernel(self, location, system_context, kernel_name, cmdline):
        location.set_description('Create EFI kernel')
        boot_data = system_context.boot_data_directory()
        system_context.execute(location.next_line(), 'create_efi_kernel', kernel_name,
                               kernel=os.path.join(system_context.boot_data_directory(), 'vmlinuz'),
                               initrd=os.path.join(boot_data, 'initrd-parts'),
                               commandline=cmdline)

    def _sign_efi_kernel(self, location, system_context, kernel, key, cert):
        location.set_description('Sign EFI kernel')
        system_context.execute(location.next_line(), 'sign_efi_binary', kernel,
                               key=key, cert=cert, outside=True)

    def _size_extend(self, file):
        size = os.path.getsize(file)
        block_size = 4 * 1024 * 1024  # 4MiB
        to_add = block_size - (size % block_size)
        if to_add == 0:
            return

        with open(file, 'ab') as f:
            f.write(b'\0' * to_add)

    def _create_squashfs(self, system_context, export_directory):
        squash_file = os.path.join(export_directory, 'root_{}'
                                   .format(system_context.timestamp))
        mksquashfs = system_context.binary(Binaries.MKSQUASHFS)
        system_context.run(mksquashfs, 'usr', squash_file, '-comp',
                           self._compression, '-noappend', '-no-exports',
                           '-keep-as-directory',
                           '-noI', '-noD', '-noF', '-noX',
                           outside=True,
                           work_directory=system_context.fs_directory())
        self._size_extend(squash_file)
        return squash_file

    def _create_dmverity(self, system_context, export_directory, squashfs_file):
        verity_file = os.path.join(export_directory, 'vrty_{}'
                                   .format(system_context.timestamp))
        veritysetup = system_context.binary(Binaries.VERITYSETUP)
        result = system_context.run(veritysetup, 'format',
                                    squashfs_file, verity_file, outside=True)

        self._size_extend(verity_file)

        root_hash = None
        uuid = None
        for line in result.stdout.split('\n'):
            if line.startswith('Root hash:'):
                root_hash = line[10:].strip()
            if line.startswith('UUID:'):
                uuid = line[10:].strip()

        assert root_hash is not None
        assert uuid is not None
        return (verity_file, uuid, root_hash)

    def _setup_kernel_commandline(self, base_cmdline,
                                  squashfs_device, verity_device,
                                  root_hash):
        cmdline = ' '.join((base_cmdline,
                            'systemd.verity=yes',
                            'systemd.verity_root_data={}'.format(squashfs_device),
                            'systemd.verity_root_hash={}'.format(verity_device),
                            'roothash={}'.format(root_hash),
                            'FOO'))
        return cmdline

    def _create_complete_kernel(self, location, system_context, base_cmdline,
                                squashfs_device, verity_device, root_hash,
                                export_volume):
        full_cmdline = self._setup_kernel_commandline(base_cmdline, squashfs_device, verity_device, root_hash)
        kernel_name = self._kernel_name(system_context)

        self._create_efi_kernel(location, system_context, kernel_name, full_cmdline)

        if self._key is not None and self._cert is not None:
            debug('Signing EFI kernel.')
            self._sign_efi_kernel(location, system_context, kernel_name,
                                  self._key, self._cert)

        shutil.copyfile(kernel_name,
                        os.path.join(export_volume, os.path.basename(kernel_name)))

    def create_export_directory(self, location, system_context):
        """Return the root directory."""
        cmdline = system_context.substitution('KERNEL_CMDLINE', '')
        cmdline = ' '.join((cmdline, 'systemd.volatile=true',
                            'rootfstype=squashfs'))

        export_volume \
            = Context.current_export_directory_from_work_directory(
               system_context.ctx.work_directory())
        create_subvolume(export_volume, command=system_context.binary(Binaries.BTRFS))

        squashfs_file = self._create_squashfs(system_context, export_volume)
        (verity_file, verity_uuid, root_hash) \
            = self._create_dmverity(system_context, export_volume,
                                    squashfs_file)

        verity_device = 'UUID={}'.format(verity_uuid)
        partlabel=system_context.substitution('ROOTFS_PARTLABEL', '')
        if not partlabel:
            partlabel = '{}_{}'.format(system_context.substitution('DISTRO_ID', 'clrm'),
                                       system_context.substitution('DISTRO_VERSION_ID', system_context.timestamp))
        squashfs_device = 'PARTLABEL={}'.format(partlabel)
        self._create_complete_kernel(location, system_context,  cmdline,
                                     squashfs_device, verity_device, root_hash,
                                     export_volume)

        return export_volume

    def delete_export_directory(self, system_context, export_directory):
        """Nothing to see, move on."""
        delete_subvolume(export_directory, command=system_context.binary(Binaries.BTRFS))
