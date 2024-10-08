# -*- coding: utf-8 -*-
"""_create_initrd_dracut command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

from cleanroom.binarymanager import Binaries
from cleanroom.command import Command
from cleanroom.helper.file import copy, remove, move
from cleanroom.helper.run import run
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext
from cleanroom.printer import info

import os
import typing


class CreateInitrdDracutCommand(Command):
    """The _create_initrd_dracut command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "_create_initrd_dracut",
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

    def _install_dracut(self, location: Location, system_context: SystemContext):
        location.set_description("Install dracut")
        self._execute(location, system_context, "pacman", "dracut", "busybox")

    def _remove_dracut(self, location: Location, system_context: SystemContext):
        # FIXME: Remove mkinitcpio once linux and ostree no longer depend on it!
        self._execute(
            location,
            system_context,
            "pacman",
            "dracut",
            "busybox",
            "--assume-installed",
            "initramfs",
            "--assume-installed",
            "dracut",
            remove=True,
        )

        remove(system_context, "/boot/vmlinuz")

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

        self._install_dracut(location, system_context)

        copy(
            system_context,
            os.path.join(system_context.boot_directory, "vmlinuz"),
            "/boot/vmlinuz",
            from_outside=True,
        )

        dracut_args: typing.List[str] = []

        kernel_version = system_context.substitution_expanded("KERNEL_VERSION", "")
        assert kernel_version

        run(
            "/usr/bin/dracut",
            *dracut_args,
            "--no-early-microcode",
            "--no-hostonly",
            "--no-compress",
            "--reproducible",
            "--omit",
            "iscsi nbd network network-legacy nfs qemu qemu-net stratis",
            "--add",
            "busybox",
            "/boot/initramfs.img",
            kernel_version,
            chroot=system_context.fs_directory,
            chroot_helper=self._binary(Binaries.SYSTEMD_NSPAWN),
        )

        initrd_directory = os.path.dirname(initrd)
        os.makedirs(initrd_directory, exist_ok=True)
        move(system_context, "/boot/initramfs.img", initrd, to_outside=True)

        self._remove_dracut(location, system_context)

        assert os.path.isfile(initrd)
