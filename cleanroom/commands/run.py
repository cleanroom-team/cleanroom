"""Run command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

import cleanroom.command as cmd


class RunCommand(cmd.Command):
    """The Run Command."""

    def __init__(self):
        """Constructor."""
        super().__init__("run <COMMAND> [<ARGUMENTS>]",
                         "Run a shell command with arguments.")
