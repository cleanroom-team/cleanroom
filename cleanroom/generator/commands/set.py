# -*- coding: utf-8 -*-
"""set command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.generator.command import Command


class SetDefaultTargetCommand(Command):
    """The set command."""

    def __init__(self):
        """Constructor."""
        super().__init__('set', syntax='<KEY> <VALUE> [local=True]',
                         help='Set up a substitution.', file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_arguments_exact(location, 2,
                                       '"{}" needs a key and a value.',
                                       *args, **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        key = args[0]
        value = args[1]

        system_context.set_substitution(key, value, **kwargs)