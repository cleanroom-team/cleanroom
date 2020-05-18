# -*- coding: utf-8 -*-
"""set_root_device command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.exceptions import GenerateError, ParseError
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import os.path
import typing


class SetRootDeviceCommand(Command):
    """The set_root_device command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "set_root_device",
            syntax="<DEVICE>",
            help_string="Set the device of the root partition.",
            file=__file__,
            **services
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate the arguments."""
        self._validate_arguments_exact(
            location, 1, '"{}" needs a device.', *args, **kwargs
        )

        device = args[0]
        if not device.startswith("/dev/") and not device.startswith("/sys/"):
            raise ParseError(
                '"{}": Root device "{}" does not start with /dev/ or /sys/.'.format(
                    self.name, device
                ),
                location=location,
            )

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any
    ) -> None:
        """Execute command."""
        device = args[0]

        root_device_key = "ROOT_DEVICE"

        dev = system_context.substitution(root_device_key)
        if dev is not None:
            raise GenerateError(
                '"{}" root device is already set to "{}".'.format(self.name, dev),
                location=location,
            )

        system_context.set_substitution(root_device_key, device)

        if " " in device:
            device = '"{}"'.format(device)

        cmdline = system_context.substitution("KERNEL_CMDLINE", "")
        cmdline = " ".join((cmdline, "root={}".format(device), "rootflags=ro"))
        system_context.set_substitution("KERNEL_CMDLINE", cmdline)
