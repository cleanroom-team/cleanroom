"""_setup command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

import cleanroom.command as cmd


class _SetupCommand(cmd.Command):
    """The _setup Command."""

    def __init__(self, ctx):
        """Constructor."""
        super().__init__("_setup <SYSTEM>",
                         "Implicitly run before any other command of a "
                         "system is run.")
        self._ctx = ctx
