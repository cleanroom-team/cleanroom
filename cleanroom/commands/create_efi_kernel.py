# -*- coding: utf-8 -*-
"""create_efi_kernel command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.context as ctx
import cleanroom.exceptions as ex

import os.path
import tempfile


class CreateEfiBinaryCommand(cmd.Command):
    """The create_efi_kernel command."""

    def __init__(self):
        """Constructor."""
        super().__init__('create_efi_kernel',
                         syntax='kernel=<KERNEL> initrd=<INITRD>(,<INITRD>)* '
                         'commandline=<KERNEL_COMMANDLINE>',
                         help='Create a efi kernel with built-in initrd.')

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_no_args(location, 1, *args)
        self._validate_kwargs(location, ('kernel', 'initrd', 'commandline'),
                              **kwargs)
        return self._require_kwargs(location,
                                    ('kernel', 'initrd', 'commandline'),
                                    **kwargs)

    def _validate_files(self, location, *files):
        for f in files:
            if f and not os.path.isfile(f):
                raise ex.GenerateError(location, '"{}": referrenced file '
                                       '"{}" does not exist.'
                                       .format(self.name(), f))

    def _create_initrd(dir, *files):
        target = os.path.join(dir, 'initrd')
        with open(target, "wb") as target_file:
            for f in files:
                target_file.write(f.read())
        return target

    def _create_cmdline_file(dir, cmdline):
        target = os.path.join(dir, 'cmdline')
        with open(target, "wb") as cmdline_file:
            cmdline_file.write(cmdline.encode('utf-8'))
        return cmdline_file

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        kernel = kwargs.get('kernel', '')
        initrd_files = kwargs.get('initrd', '').split(',')
        cmdline_input = kwargs.get('commandline')
        osrelease_file = system_context.file_name('/usr/lib/os-release')
        efistub = system_context.file_name('/usr/lib/systemd/boot/efi/linuxx64.efi.stub')

        self._validate_files(kernel, *initrd, osrelease_file, efistub)
        with tempfile.TemporaryDirectory() as tmp:
            initrd = self._create_initrd(tmp, *initrd)
            cmdline = self._create_cmdline_file(tmp, cmdline_input)

            system_context.run(location,
                               system_context.ctx.binary(ctx.Binaries.OBJCOPY))

        ### FIXME: Implement this!

#* RAW objcopy --add-section .osrel="\${ROOT}/usr/lib/os-release" --change-section-vma .osrel=0x20000 --add-section .cmdline="\${_CMDFILE}" --change-section-vma .cmdline=0x30000 --add-section .linux="\${BOOT_DATA_DIR}/vmlinuz" --change-section-vma .linux=0x40000 --add-section .initrd="\${_INITRD}" --change-section-vma .initrd=0x3000000 "\${ROOT}/usr/lib/systemd/boot/efi/linuxx64.efi.stub" "\${BOOT_DATA_DIR}/linux.efi"
#*
#* RAW mv "\${_CMDFILE}" "\${KERNEL_CMDLINE}"
#*
#* RAW rm -rf "\${_TMP_DIR}"
