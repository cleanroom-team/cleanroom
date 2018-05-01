# -*- coding: utf-8 -*-
"""create_efi_kernel command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.context as ctx
import cleanroom.exceptions as ex
import cleanroom.printer as printer

import glob
import os.path
import tempfile


class CreateEfiKernelCommand(cmd.Command):
    """The create_efi_kernel command."""

    def __init__(self):
        """Constructor."""
        super().__init__('create_efi_kernel',
                         syntax='<EFI_KERNEL> kernel=<KERNEL> '
                         'initrd=<INITRD_PARTS_DIRECTORY> '
                         'commandline=<KERNEL_COMMANDLINE>',
                         help='Create a efi kernel with built-in initrd.',
                         file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_args_exact(location, 1, '"{}" needs a efi kernel '
                                               'image to create.',
                                  *args)
        self._validate_kwargs(location, ('kernel', 'initrd', 'commandline'),
                              **kwargs)
        self._require_kwargs(location, ('kernel', 'initrd', 'commandline'),
                             **kwargs)

    def _validate_files(self, location, *files):
        for f in files:
            if f and not os.path.isfile(f):
                raise ex.GenerateError('"{}": referrenced file '
                                       '"{}" does not exist.'
                                       .format(self.name(), f),
                                       location=location)

    def _create_initrd(self, dir, *files):
        target = os.path.join(dir, 'initrd')
        with open(target, "wb") as target_file:
            for f in files:
                with open(f, 'rb') as source_file:
                    target_file.write(source_file.read())
        return target

    def _create_cmdline_file(self, dir, cmdline):
        target = os.path.join(dir, 'cmdline')
        with open(target, "wb") as cmdline_file:
            cmdline_file.write(cmdline.encode('utf-8'))
            cmdline_file.write(b'\0\0')
        return target

    def _get_initrd_parts(self, location, path):
        if path is None:
            raise ex.GenerateError('No initrd-parts directory.',
                                   location=location)

        initrd_parts = []
        for f in glob.glob(os.path.join(path, '*')):
            if os.path.isfile(f):
                initrd_parts.append(f)
        if not initrd_parts:
            raise ex.GenerateError('No initrd-parts found in directory "{}".'
                                   .format(path), location=location)
        return initrd_parts

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        if system_context.substitution('ROOT_DEVICE') is None:
            ex.GenerateError('ROOT_DEVICE must be set when '
                             'creating EFI kernel.', location=location)

        output = args[0]
        kernel = kwargs.get('kernel', '')
        initrd_files = self._get_initrd_parts(location, kwargs.get('initrd'))
        cmdline_input = kwargs.get('commandline')
        osrelease_file = system_context.file_name('/usr/lib/os-release')
        efistub = system_context.file_name('/usr/lib/systemd/boot/efi/'
                                           'linuxx64.efi.stub')

        printer.debug('{}: Kernel   : {}.'.format(self.name(), kernel))
        printer.debug('{}: Initrd   : {}.'.format(self.name(), ', '.join(initrd_files)))
        printer.debug('{}: cmdline  : {}.'.format(self.name(), cmdline_input))
        printer.debug('{}: osrelease: {}.'.format(self.name(), osrelease_file))
        printer.debug('{}: efistub  : {}.'.format(self.name(), efistub))

        self._validate_files(kernel, *initrd_files, osrelease_file, efistub)
        with tempfile.TemporaryDirectory() as tmp:
            initrd = self._create_initrd(tmp, *initrd_files)
            cmdline = self._create_cmdline_file(tmp, cmdline_input)

            system_context.run(system_context.ctx.binary(ctx.Binaries.OBJCOPY),
                               '--add-section',
                               '.osrel={}'.format(osrelease_file),
                               '--change-section-vma', '.osrel=0x20000',
                               '--add-section',
                               '.cmdline={}'.format(cmdline),
                               '--change-section-vma', '.cmdline=0x30000',
                               '--add-section',
                               '.linux={}'.format(kernel),
                               '--change-section-vma', '.linux=0x40000',
                               '--add-section',
                               '.initrd={}'.format(initrd),
                               '--change-section-vma', '.initrd=0x3000000',
                               efistub, output, outside=True)

            os.remove(initrd)
            os.remove(cmdline)
