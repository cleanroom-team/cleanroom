"""export command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

import cleanroom.command as cmd


class ExportCommand(cmd.Command):
    """The export Command."""

    def __init__(self):
        """Constructor."""
        super().__init__('export',
                         'Export a system and make it available '
                         'for deployment.')

    def __call__(self, file_name, line_number, run_context, *args, **kwargs):
        """Execute command."""
        run_context.run_hooks('_teardown')
        run_context.run_hooks('export')
        run_context.run_hooks('testing')
