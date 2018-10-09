# -*- coding: utf-8 -*-
"""_pacman_write_package_data command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.generator.command import Command
from cleanroom.generator.helper.archlinux.pacman import pacman_report


class PacmanWritePackageDataCommand(Command):
    """The pacman command."""

    def __init__(self):
        """Constructor."""
        super().__init__('_pacman_write_package_data',
                         help='Write pacman package data into the filesystem.',
                         file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        pacman_report(system_context, system_context.file_name('/usr/lib/pacman'))
