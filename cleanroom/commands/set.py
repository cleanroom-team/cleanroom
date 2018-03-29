# -*- coding: utf-8 -*-
"""set command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd


class SetDefaultTargetCommand(cmd.Command):
    """The set command."""

    def __init__(self):
        """Constructor."""
        super().__init__('set', syntax='<KEY> <VALUE> [local=True]',
                         help='Set up a substitution.')

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        return self._validate_exact_arguments(location, 2,
                                              '"{}" needs a key and a value.',
                                              *args, **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        key = args[0]
        value = args[1]

        system_context.set_substitution(key, value, **kwargs)
