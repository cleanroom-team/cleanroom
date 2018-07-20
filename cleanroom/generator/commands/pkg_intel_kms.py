"""pkg_intel_kms command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.generator.command import Command
from cleanroom.generator.helper.generic.file import exists

import os.path


class PkgIntelKmsCommand(Command):
    """The pkg_intel_kms command."""

    def __init__(self):
        """Constructor."""
        super().__init__('pkg_intel_kms',
                         help='Set up Kernel Mode Setting for Intel GPU.',
                         file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""

        # enable kms:
        system_context.execute(location, 'sed',
                               's/^MODULES=(/MODULES=(intel_agp i915 /',
                               '/etc/mkinitcpio.conf')
