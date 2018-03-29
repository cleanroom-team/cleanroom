# -*- coding: utf-8 -*-
"""add_hook command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd


class AddHookCommand(cmd.Command):
    """The add_hook command."""

    def __init__(self):
        """Constructor."""
        super().__init__('add_hook', syntax='<HOOK_NAME> <COMMAND> '
                         '[<ARGS>] [message=<MESSAGE>] [<KWARGS>]',
                         help='Add a hook running command with arguments.')

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_args_at_least(location, 1,
                                     '"{}" needs a hook name and a '
                                     'command and optional arguments.', *args)
        self._validate_kwargs(location, ('message',), **kwargs)
        return None

    def __call__(self, location, system_context, *args, message='', **kwargs):
        """Execute command."""
        hook = args[0]
        cmd = args[1]
        cmd_args = args[2:]
        cmd_kwargs = kwargs
        location.next_line_offset(message)

        system_context.add_hook(hook, location, cmd, *cmd_args,
                                **cmd_kwargs)
