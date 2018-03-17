"""export_rootfs command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

import cleanroom.exportcommand as cmd


class ExportRootFsCommand(cmd.ExportCommand):
    """The export_rootfs Command."""

    def __init__(self):
        """Constructor."""
        super().__init__('export_rootfs',
                         'Export the root filesystem.')

    def create_export_directory(self, run_context):
        """Return the root directory."""
        return run_context.fs_directory()

    def delete_export_directory(self, run_context, export_directory):
        """Nothing to see, move on."""
        pass  # Filesystem will be cleaned up automatically.
