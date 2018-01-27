"""Run command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

import cleanroom.command as cmd


class RunCommand(cmd.Command):
    """The Run Command."""

    def __init__(self, ctx):
        """Constructor."""
        super().__init__()
        self._ctx = ctx

    def validate_arguments(self, state, args):
        """Validate arguments."""
        return super().validate_arguments(state, args)

    def execute(self, *args):
        """Execute run command."""
        super().execute(*args)
