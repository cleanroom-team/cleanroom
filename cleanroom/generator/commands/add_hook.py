# -*- coding: utf-8 -*-
"""add_hook command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.generator.command import Command


class AddHookCommand(Command):
    """The add_hook command."""

    def __init__(self):
        """Constructor."""
        super().__init__('add_hook', syntax='<HOOK_NAME> <COMMAND> '
                         '<ARGS>* [message=<MESSAGE>] [<KWARGS>]',
                         help='Add a hook running command with arguments.',
                         file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_args_at_least(location, 1,
                                     '"{}" needs a hook name and a '
                                     'command and optional arguments.', *args)

    def __call__(self, location, system_context, *args, message='', **kwargs):
        """Execute command."""
        location.next_line_offset(message)
        system_context.add_hook(location, *args, **kwargs)
