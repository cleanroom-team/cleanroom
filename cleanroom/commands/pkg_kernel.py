"""pkg_kernel command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom import systemcontext
from cleanroom.command import Command
from cleanroom.exceptions import GenerateError
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

    def _find_kernel_version(self, system_context: SystemContext) -> str:
        lib_modules = system_context.file_name("/usr/lib/modules")
        module_dirs = [
            d
            for d in os.listdir(lib_modules)
            if os.path.isdir(os.path.join(lib_modules, d))
        ]
        assert len(module_dirs) == 1

        kernel_version = module_dirs[0]

        return kernel_version

    def _arch_install(
        self, location: Location, system_context: SystemContext, package: str
    ) -> typing.Tuple[(str, str)]:
        self._execute(
            location,
            system_context,
            "pacman",
            package,
            "--assume-installed",
            "initramfs",
        )

        kernel_version = self._find_kernel_version(system_context)

        return (kernel_version, f"/usr/lib/modules/{kernel_version}/vmlinuz")

    def _fedora_install(
        self, location: Location, system_context: SystemContext, package: str
    ) -> typing.Tuple[(str, str)]:
        self._execute(
            location,
            system_context,
            "dnf",
            package,
        )

        kernel_version = self._find_kernel_version(system_context)

        return (kernel_version, f"/usr/lib/modules/{kernel_version}/vmlinuz")

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> None:
        """Execute command."""
        variant = kwargs.get("variant", "")

        ctx = system_context.substitution_expanded("DISTRO_ID_LIKE", "")

        kernel_version, kernel_file = "", ""
        if ctx == "archlinux":
            kernel = "linux"
            if variant:
                kernel = f"{kernel}-{variant}"
            kernel_version, kernel_file = self._arch_install(
                location, system_context, kernel
            )
        elif ctx == "fedora":
            if variant:
                raise GenerateError("Variant not supported by fedora.")
            kernel_version, kernel_file = self._fedora_install(
                location, system_context, "kernel"
            )
        else:
            raise GenerateError("Unsupported distribution")

        vmlinuz = os.path.join(system_context.boot_directory, "vmlinuz")

        system_context.set_substitution("KERNEL_VERSION", kernel_version)

        self._execute(
            location.next_line(),
            system_context,
            "move",
            kernel_file,
            vmlinuz,
            to_outside=True,
            ignore_missing_sources=True,
        )

        assert os.path.isfile(vmlinuz)
