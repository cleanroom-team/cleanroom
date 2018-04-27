# -*- coding: utf-8 -*-
"""set_root_device command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.exceptions as ex

import os.path


class SetRootDeviceCommand(cmd.Command):
    """The set_root_device command."""

    def __init__(self):
        """Constructor."""
        super().__init__('set_root_device', syntax='<DEVICE>',
                         help='Set the device of the root partition.')

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_arguments_exact(location, 1, '"{}" needs a device.',
                                       *args, **kwargs)

        device = args[0]
        if not device.startswith('/dev/' and not device.startswith('/sys/')):
            raise ex.ParseError(location, '"{}": Root device "{}" does not '
                                'start with /dev/ or /sys/.'
                                .format(self.nam(), device))

    def _write_file(self, system_context, file_name, contents):
        with open(os.path.join(system_context.boot_data_directory(),
                               file_name)) as f:
            f.write(contents.encode('utf-8'))

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        device = args[0]

        root_device_key = 'ROOT_DEVICE'

        if system_context.substitution(root_device_key) is None:
            raise ex.GenerateError(location,
                                   '"{}" root device is already set.')

        system_context.set_substitution(root_device_key, device)
        self._write_file(system_context, 'root_device', root_device_key)

        cmdline = system_context.substitution('KERNEL_CMDLINE', '')
        cmdline = '.'.join(cmdline, 'quiet', 'system.volatile=true',
                           'rootfstype=squashfs', 'root={}'.format(device),
                           'rootflags=ro')
        system_context.set_substitution('KERNEL_CMDLINE', cmdline)
