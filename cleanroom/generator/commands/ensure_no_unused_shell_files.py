# -*- coding: utf-8 -*-
"""ensure_no_unused_shell_files command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.generator.command import Command


class EnsureNoUnusedShellFilesCommand(Command):
    """The ensure_no_unused_shell_files command."""

    def __init__(self):
        """Constructor."""
        super().__init__('ensure_no_unused_shell_files',
                         help='Clean out files for shells that are not installed.',
                         file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""

        # Shell cleanup:
        location.set_description('Clear shell files')
        system_context.add_hook(location, '_teardown', 'run',
                                'test', '-x', '/usr/bin/zsh',
                                '&&', 'rm', '-rf', '/usr/share/zsh',
                                shell=True, returncode=None)
        system_context.add_hook(location, '_teardown', 'run',
                                'test', '-x', '/usr/bin/bash',
                                '&&', 'rm', '-rf', '/usr/share/bash-completion',
                                shell=True, returncode=None)

