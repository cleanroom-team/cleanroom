"""pkg_intel_kms command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.location import Location
from cleanroom.generator.command import Command
from cleanroom.generator.systemcontext import SystemContext

import typing


class PkgIntelKmsCommand(Command):
    """The pkg_intel_kms command."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__('pkg_intel_kms',
                         help_string='Set up Kernel Mode Setting for Intel GPU.',
                         file=__file__)

    def validate_arguments(self, location: Location, *args: typing.Any, **kwargs: typing.Any) \
            -> typing.Optional[str]:
        """Validate the arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

        return None

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""

        # enable kms:
        system_context.execute(location, 'sed',
                               's/^MODULES=(/MODULES=(intel_agp i915 /',
                               '/etc/mkinitcpio.conf')
