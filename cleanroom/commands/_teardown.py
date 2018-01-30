"""_teardown command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

import cleanroom.command as cmd


class _TeardownCommand(cmd.Command):
    """The _teardown Command."""

    def __init__(self, ctx):
        """Constructor."""
        super().__init__("_teardown <SYSTEM>",
                         "Implicitly run after any other command of a "
                         "system is run.")
        self._ctx = ctx
