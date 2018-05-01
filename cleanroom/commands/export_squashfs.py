# -*- coding: utf-8 -*-
"""export_squashfs command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

import cleanroom.context as context
import cleanroom.exportcommand as cmd
import cleanroom.exceptions as ex
import cleanroom.printer as printer

import cleanroom.helper.generic.btrfs as btrfs
import cleanroom.helper.generic.file as file

import os.path


class ExportSquashfsCommand(cmd.ExportCommand):
    """The export_squashfs Command."""

    def __init__(self):
        """Constructor."""
        self._key = None
        self._cert = None
        self._volume_group = None

        super().__init__('export_squashfs',
                         syntax='[key=<KEY>] [cert=<CERT>] [vg=<VG>]',
                         help='Export the root filesystem as squashfs.',
                         file=__file__)

    def __call__(self, location, *args, **kwargs):
        """Execute command."""
        self._key = kwargs.get('key')
        self._cert = kwargs.get('cert')
        self._volume_group = kwargs.get('vg')

        super().__call__(location, *args, **kwargs)

    def _create_root_tarball(self, location, system_context):
        tar_directory = '/usr/lib/boot'
        system_context.execute(location, 'mkdir', tar_directory)

        tarball = os.path.join(tar_directory, 'root-fs.tar')
        if file.exists(system_context, tarball):
            raise ex.GenerateError('"{}": Root tarball "{}" already exists.'
                                   .format(self.name(), tarball),
                                   location=location)
        system_context.run('/usr/bin/tar', '-cf', tarball,
                           '--sort=name', 'etc', 'root', work_directory='/')

    def _kernel_name(self, system_context):
        boot_data = system_context.boot_data_directory()
        return os.path.join(boot_data,
                            'linux-{}.efi'.format(system_context.timestamp))

    def _create_initramfs(self, location, system_context):
        location.next_line_offset('Create initrd')
        initrd_parts = os.path.join(system_context
                                    .boot_data_directory(),
                                    'initrd-parts')
        os.makedirs(initrd_parts)
        system_context.execute(location, 'create_initrd',
                               os.path.join(initrd_parts, '50-mkinitcpio'))

    def prepare_for_export(self, location, system_context):
        self._create_root_tarball(location, system_context)
        self._create_initramfs(location, system_context)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate arguments."""
        self._validate_no_args(location, *args)
        self._validate_kwargs(location, ('key', 'cert', 'vg'), **kwargs)

    def _create_efi_kernel(self, location, system_context):
        location.next_line_offset('Create EFI kernel')
        boot_data = system_context.boot_data_directory()
        system_context.execute(location, 'create_efi_kernel',
                               self._kernel_name(system_context),
                               kernel=os.path.join(system_context.boot_data_directory(), 'vmlinuz'),
                               initrd=os.path.join(boot_data, 'initrd-parts'),
                               commandline=system_context
                               .substitution('KERNEL_CMDLINE', ''))

    def _sign_efi_kernel(self, location, system_context, key, cert):
        location.next_line_offset('Sign EFI kernel')
        system_context.execute(location, 'sign_efi_binary',
                               self._kernel_name(system_context),
                               key=key, cert=cert)

    def _size_extend(self, file):
        size = os.path.getsize(file)
        block_size = 4 * 1024 * 1024  # 4MiB
        to_add = block_size - (size % block_size)
        if to_add == 0:
            return

        with open(file, 'wb') as f:
            f.write(b'\0' * to_add)

    def _create_squashfs(self, location, system_context, export_directory):
        squash_file = os.path.join(export_directory, 'root_{}'
                                   .format(system_context.timestamp))
        mksquashfs = system_context.ctx.binary(context.Binaries.MKSQUASHFS)
        system_context.run(mksquashfs, 'usr', squash_file, '-comp',
                           'lz4', '-noappend', '-no-exports',
                           '-keep-as-directory', outside=True)
        self._size_extend(squash_file)
        return squash_file

    def _create_dmverity(self, location, system_context, export_directory,
                         squashfs_file):
        verity_file = os.path.join(export_directory, 'root_{}_verity'
                                   .format(system_context.timestamp))
        veritysetup = system_context.ctx.binary(context.Binaries.VERITYSETUP)
        result = system_context.run(veritysetup, 'format',
                                    squashfs_file, verity_file, outside=True)

        self._size_extend(verity_file)

        root_hash = None
        for line in result.stdout.split('\n'):
            if not line.startswith('Root hash:'):
                continue

            root_hash = line[10:].strip()

        assert root_hash is not None
        return (verity_file, root_hash)

    def _file_to_lv(self, file_name):
        result = '/dev/mapper/' + self._volume_group + '-' + file_name
        result.replace('-', '--')
        return result

    def _setup_kernel_commandline(self, system_context, root_hash,
                                  squashfs_file, verity_file):
        cmdline = system_context.substitution('KERNEL_CMDLINE', '')
        cmdline = ' '.join((cmdline, 'rd.systemd.verity=yes',
                            'roothash={}'.format(root_hash),
                            'systemd.verity_root_data={}'
                            .format(self._file_to_lv(squashfs_file)),
                            'systemd.verify_root_hash={}'
                            .format(self._file_to_lv(verity_file)),
                            'FOO'))
        system_context.set_substitution('KERNEL_CMDLINE', cmdline)

    def create_export_directory(self, location, system_context):
        """Return the root directory."""
        cmdline = system_context.substitution('KERNEL_CMDLINE', '')
        cmdline = ' '.join((cmdline, 'systemd.volatile=true',
                            'rootfstype=squashfs'))

        export_volume \
            = context.Context.current_export_directory_from_work_directory(
               system_context.ctx.work_directory())
        btrfs.create_subvolume(system_context, export_volume)

        squashfs_file = self._create_squashfs(location, system_context,
                                              export_volume)
        (verity_file, root_hash) \
            = self._create_dmverity(location, system_context,
                                    export_volume, squashfs_file)
        self._setup_kernel_commandline(system_context, root_hash,
                                       squashfs_file, verity_file)

        self._create_efi_kernel(location, system_context)

        if self._key is not None and self._cert is not None:
            printer.verbose('Signing EFI kernel.')
            self._sign_efi_kernel(location, system_context,
                                  self._key, self._cert)

        return export_volume

    def delete_export_directory(self, system_context, export_directory):
        """Nothing to see, move on."""
        btrfs.delete_subvolume(system_context, export_directory)
