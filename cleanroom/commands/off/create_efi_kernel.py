# -*- coding: utf-8 -*-
"""create_efi_kernel command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.location import Location
from cleanroom.generator.command import Command
from cleanroom.generator.context import Binaries
from cleanroom.generator.systemcontext import SystemContext
from cleanroom.exceptions import GenerateError
from cleanroom.printer import debug

from glob import glob
import os.path
import tempfile
import typing


def _create_initrd(directory: str, *files: str) -> str:
    target = os.path.join(directory, 'initrd')
    with open(target, "wb") as target_file:
        for f in files:
            with open(f, 'rb') as source_file:
                target_file.write(source_file.read())
    return target


def _create_cmdline_file(directory: str, cmdline: str) -> str:
    target = os.path.join(directory, 'cmdline')
    with open(target, "wb") as cmdline_file:
        cmdline_file.write(cmdline.encode('utf-8'))
        cmdline_file.write(b'\0\0')
    return target


def _get_initrd_parts(location: Location, path: str) -> typing.Sequence[str]:
    if path is None:
        raise GenerateError('No initrd-parts directory.', location=location)

    initrd_parts = []  # type: typing.List[str]
    for f in glob(os.path.join(path, '*')):
        if os.path.isfile(f):
            initrd_parts.append(f)
    if not initrd_parts:
        raise GenerateError('No initrd-parts found in directory "{}".'
                            .format(path), location=location)
    return initrd_parts


class CreateEfiKernelCommand(Command):
    """The create_efi_kernel command."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__('create_efi_kernel',
                         syntax='<EFI_KERNEL> kernel=<KERNEL> '
                         'initrd=<INITRD_PARTS_DIRECTORY> '
                         'commandline=<KERNEL_COMMANDLINE>',
                         help_string='Create a efi kernel with built-in initrd.',
                         file=__file__)

    def validate_arguments(self, location: Location, *args: typing.Any, **kwargs: typing.Any) \
            -> typing.Optional[str]:
        """Validate the arguments."""
        self._validate_args_exact(location, 1, '"{}" needs a efi kernel '
                                               'image to create.',
                                  *args)
        self._validate_kwargs(location, ('kernel', 'initrd', 'commandline'),
                              **kwargs)
        self._require_kwargs(location, ('kernel', 'initrd', 'commandline'),
                             **kwargs)

        return None

    def _validate_files(self, location: Location, *files: str) -> None:
        for f in files:
            if f and not os.path.isfile(f):
                raise GenerateError('"{}": referrenced file "{}" does not exist.'
                                    .format(self.name(), f), location=location)

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        if system_context.substitution('ROOT_DEVICE') is None:
            GenerateError('ROOT_DEVICE must be set when creating EFI kernel.',
                          location=location)

        output = args[0]
        kernel = kwargs.get('kernel', '')
        initrd_files = _get_initrd_parts(location, kwargs.get('initrd', ''))
        cmdline_input = kwargs.get('commandline', '')
        osrelease_file = system_context.file_name('/usr/lib/os-release')
        efistub = system_context.file_name('/usr/lib/systemd/boot/efi/'
                                           'linuxx64.efi.stub')

        debug('{}: Kernel   : {}.'.format(self.name(), kernel))
        debug('{}: Initrd   : {}.'.format(self.name(), ', '.join(initrd_files)))
        debug('{}: cmdline  : {}.'.format(self.name(), cmdline_input))
        debug('{}: osrelease: {}.'.format(self.name(), osrelease_file))
        debug('{}: efistub  : {}.'.format(self.name(), efistub))

        self._validate_files(kernel, *initrd_files, osrelease_file, efistub)
        with tempfile.TemporaryDirectory() as tmp:
            initrd = _create_initrd(tmp, *initrd_files)
            cmdline = _create_cmdline_file(tmp, cmdline_input)

            system_context.run(system_context.binary(Binaries.OBJCOPY),
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
