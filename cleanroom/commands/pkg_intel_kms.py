"""pkg_intel_kms command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import typing


class PkgIntelKmsCommand(Command):
    """The pkg_intel_kms command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "pkg_intel_kms",
            help_string="Set up Kernel Mode Setting for Intel GPU.",
            file=__file__,
            **services
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate the arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any
    ) -> None:
        """Execute command."""

        # enable kms:
        system_context.set_or_append_substitution(
            "INITRD_EXTRA_MODULES", "intel_agp i915"
        )
