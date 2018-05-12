# -*- coding: utf-8 -*-
"""set_root_device command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.generator.command import Command

from cleanroom.exceptions import (GenerateError, ParseError)

import os.path


class SetRootDeviceCommand(Command):
    """The set_root_device command."""

    def __init__(self):
        """Constructor."""
        super().__init__('set_root_device', syntax='<DEVICE>',
                         help='Set the device of the root partition.',
                         file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_arguments_exact(location, 1, '"{}" needs a device.',
                                       *args, **kwargs)

        device = args[0]
        if not device.startswith('/dev/') and not device.startswith('/sys/'):
            raise ParseError('"{}": Root device "{}" does not start with /dev/ or /sys/.'
                             .format(self.nam(), device),
                             location=location)

    def _write_file(self, system_context, file_name, contents):
        with open(os.path.join(system_context.boot_data_directory(),
                               file_name), 'wb') as f:
            f.write(contents.encode('utf-8'))

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        device = args[0]

        root_device_key = 'ROOT_DEVICE'

        dev = system_context.substitution(root_device_key)
        if dev is not None:
            raise GenerateError('"{}" root device is already set to "{}".'
                                .format(self.name(), dev),
                                location=location)

        system_context.set_substitution(root_device_key, device)
        self._write_file(system_context, 'root_device', root_device_key)

        if ' ' in device:
            device = '"{}"'.format(device)

        cmdline = system_context.substitution('KERNEL_CMDLINE', '')
        cmdline = ' '.join((cmdline, 'root={}'.format(device), 'rootflags=ro'))
        system_context.set_substitution('KERNEL_CMDLINE', cmdline)
