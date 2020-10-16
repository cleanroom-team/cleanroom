"""pkg_kernel command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import typing
import os


class PkgKernelCommand(Command):
    """The pkg_kernel command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "pkg_kernel",
            syntax_string="[variant=(lts|hardened|DEFAULT)]",
            help_string="Set up a Kernel. If no variant is given, then the default kernel is installed.",
            file=__file__,
            **services,
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate the arguments."""
        self._validate_no_args(location, *args)
        self._validate_kwargs(location, ("variant",), **kwargs)

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> None:
        """Execute command."""

        kernel = "linux"
        variant = kwargs.get("variant", "")
        if variant:
            kernel = f"{kernel}-{variant}"

        self._execute(
            location,
            system_context,
            "pacman",
            "--assume-installed",
            "initramfs",
            kernel,
        )

        vmlinuz = os.path.join(system_context.boot_directory, "vmlinuz")

        lib_modules = system_context.file_name("/usr/lib/modules")
        module_dirs = [
            d
            for d in os.listdir(lib_modules)
            if os.path.isdir(os.path.join(lib_modules, d)) and "-arch" in d
        ]
        assert len(module_dirs) == 1

        kernel_version = module_dirs[0]
        system_context.set_substitution("KERNEL_VERSION", kernel_version)

        # New style linux packages that put vmlinuz into /usr/lib/modules:
        self._execute(
            location.next_line(),
            system_context,
            "move",
            f"/usr/lib/modules/{kernel_version}/vmlinuz",
            vmlinuz,
            to_outside=True,
            ignore_missing_sources=True,
        )

        assert os.path.isfile(vmlinuz)
