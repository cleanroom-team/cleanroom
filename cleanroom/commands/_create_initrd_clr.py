# -*- coding: utf-8 -*-
"""_create_initrd_clr command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

from cleanroom.command import Command
from cleanroom.helper.file import copy, remove
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext
from cleanroom.printer import debug, info

import os
import shutil
import typing


class CreateInitrdDracutCommand(Command):
    """The _create_initrd_clr command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "_create_initrd_clr",
            syntax="<INITRD_FILE>",
            help_string="Create an initrd.",
            file=__file__,
            **services,
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate the arguments."""
        self._validate_arguments_exact(
            location, 1, '"{}" takes an initrd to create.', *args, **kwargs
        )

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> None:
        """Execute command."""
        if not os.path.exists(os.path.join(system_context.boot_directory, "vmlinuz")):
            info("Skipping initrd generation: No vmlinuz in boot directory.")
            return

        initrd = args[0]

        copy(
            system_context,
            os.path.join(system_context.boot_directory, "vmlinuz"),
            "/boot/vmlinuz",
            from_outside=True,
        )

        # Use pre-created initrs if possible!
        pre_created = os.path.join(system_context.initrd_parts_directory, "50-clr")
        assert os.path.exists(pre_created)
        if pre_created != initrd:
            shutil.copyfile(pre_created, initrd)

        assert os.path.isfile(initrd)
