# -*- coding: utf-8 -*-
"""_store command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.generator.command import Command
from cleanroom.generator.context import Binaries

from cleanroom.helper.btrfs import create_snapshot
import cleanroom.printer as printer


class StoreCommand(Command):
    """The _store command."""

    def __init__(self):
        """Constructor."""
        super().__init__('_store', help='Store a system.', file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        printer.debug('Storing {} into {}.'
                      .format(system_context.current_system_directory(),
                              system_context.storage_directory()))
        create_snapshot(system_context.current_system_directory(),
                        system_context.storage_directory(), read_only=True,
                        command=system_context.binary(Binaries.BTRFS))
