# -*- coding: utf-8 -*-
"""export_rootfs command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

import cleanroom.exportcommand as cmd


class ExportRootFsCommand(cmd.ExportCommand):
    """The export_rootfs Command."""

    def __init__(self):
        """Constructor."""
        super().__init__('export_rootfs', help='Export the root filesystem.',
                         file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

    def create_export_directory(self, location, system_context):
        """Return the root directory."""
        return system_context.fs_directory()

    def delete_export_directory(self, system_context, export_directory):
        """Nothing to see, move on."""
        pass  # Filesystem will be cleaned up automatically.
