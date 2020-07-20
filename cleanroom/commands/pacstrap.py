# -*- coding: utf-8 -*-
"""pacstrap command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.binarymanager import Binaries
from cleanroom.command import Command
from cleanroom.helper.archlinux.pacman import (
    gpg_directory,
    pacstrap,
    pacman_keyinit,
    pacman_setup,
)
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import os.path
import typing


class PacstrapCommand(Command):
    """The pacstrap command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "pacstrap",
            syntax="<PACKAGES> config=<config>",
            help_string="Run pacstrap to install <PACKAGES>.\n"
            "After the pacman keyring is initialized, this will call\n"
            "the _pacman_keyring command.\n\n"
            "Hooks: Will runs _setup hooks after pacstrapping.",
            file=__file__,
            **services
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate the arguments."""
        self._validate_args_at_least(
            location,
            1,
            '"{}" needs at least one package ' "or group to install.",
            *args
        )
        self._validate_kwargs(location, ("config",), **kwargs)
        self._require_kwargs(location, ("config",), **kwargs)

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any
    ) -> None:
        """Execute command."""
        pacman_setup(system_context, kwargs.get("config", ""))

        pacman_key_command = self._binary(Binaries.PACMAN_KEY)
        pacman_keyinit(system_context, pacman_key_command=pacman_key_command)
        # Allow for customizations of the pacman keyring to happen:
        self._execute(
            location.next_line(),
            system_context,
            "_pacman_keyinit",
            pacman_key=pacman_key_command,
            gpg_dir=gpg_directory(system_context),
        )

        pacstrap(
            system_context,
            *args,
            pacman_command=self._binary(Binaries.PACMAN),
            chroot_helper=self._binary(Binaries.CHROOT_HELPER),
            **kwargs
        )

        self._execute(location.next_line(), system_context, "create_os_release")

        self._setup_hooks(location, system_context)

    def _setup_hooks(self, location: Location, system_context: SystemContext) -> None:
        i_gpg_dir = "/usr/lib/pacman/gpg"
        i_packages = "/var/cache/pacman/pkg/*"

        location.set_description("cleanup pacman-key files (internal)")
        self._add_hook(
            location,
            system_context,
            "_teardown",
            "remove",
            i_gpg_dir + "/S.*",
            i_gpg_dir + "/pubring.gpg~",
            i_gpg_dir + "/secring.gpg*",
            "/var/log/pacman.log",
            i_packages,
            recursive=True,
            force=True,
        )

        location.set_description("Cleanup pacman-key files (external)")
        o_gpg_dir = os.path.join(system_context.meta_directory, "pacman/gpg")

        self._add_hook(
            location,
            system_context,
            "_teardown",
            "remove",
            o_gpg_dir + "/S.*",
            o_gpg_dir + "/pubring.gpg~",
            o_gpg_dir + "/secring.gpg*",
            recursive=True,
            force=True,
            outside=True,
        )

        location.set_description("Move systemd files into /usr")
        self._add_hook(location, system_context, "_teardown", "systemd_cleanup")

        location.set_description("Moving /opt into /usr")
        self._add_hook(
            location.next_line(), system_context, "export", "move", "/opt", "/usr"
        )
        self._add_hook(
            location,
            system_context,
            "export",
            "symlink",
            "usr/opt",
            "opt",
            work_directory="/",
        )

        location.set_description("Writing package information to FS.")
        self._add_hook(
            location.next_line(), system_context, "export", "_pacman_write_package_data"
        )
