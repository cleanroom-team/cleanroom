# -*- coding: utf-8 -*-
"""dnf command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

from cleanroom.binarymanager import Binaries
from cleanroom.command import Command
from cleanroom.exceptions import ParseError
from cleanroom.helper.fedora.dnf_packager import dnf
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import typing


class dnfCommand(Command):
    """The dnf command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "dnf",
            target_distribution="fedora",
            syntax="<PACKAGES> config=<config> remove=<BOOL> exclude=<PKGS> group_levels=<GROUPS>",
            help_string="Run dnf to install <PACKAGES>.\n\n"
            "Hooks: Will runs _setup hooks after dnf.",
            file=__file__,
            **services,
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate the arguments."""
        if not self._binary(Binaries.DNF):
            raise ParseError("No dnf binary was found.")

        self._validate_args_at_least(
            location, 1, '"{}" needs at least one package or group to install.', *args
        )
        self._validate_kwargs(
            location, ("config", "remove", "exclude", "group_levels"), **kwargs
        )

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> None:
        """Execute command."""

        kwargs["exclude"] = kwargs.get("exclude", "").split(",")
        kwargs["group_levels"] = kwargs.get("group_levels", "").split(",")

        dnf(system_context, *args, dnf_command=self._binary(Binaries.DNF), **kwargs)

        if kwargs.get("config", ""):
            # Config is used only the first time round!
            self._execute(location.next_line(), system_context, "create_os_release")

            self._setup_hooks(location, system_context)

    def _setup_hooks(self, location: Location, system_context: SystemContext) -> None:
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

        system_context.set_substitution("DISTRO_ID_LIKE", "fedora")
