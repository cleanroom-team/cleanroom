# -*- coding: utf-8 -*-
"""strip_license_files command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

from cleanroom.generator.command import Command


class StripLicenseFilesCommand(Command):
    """The strip_license_files Command."""

    def __init__(self):
        """Constructor."""
        super().__init__('strip_license_files',
                         help='Strip away license files.', file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        location.set_description('Strip license files')
        system_context.add_hook(location, 'export',
                                'remove',  '/usr/share/licenses/*',
                                recursive=True, force=True)
