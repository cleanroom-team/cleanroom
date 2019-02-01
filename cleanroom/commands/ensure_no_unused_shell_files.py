# -*- coding: utf-8 -*-
"""ensure_no_unused_shell_files command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import typing


class EnsureNoUnusedShellFilesCommand(Command):
    """The ensure_no_unused_shell_files command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__('ensure_no_unused_shell_files',
                         help_string='Clean out files for shells that are not installed.',
                         file=__file__, **services)

    def validate(self, location: Location,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Validate the arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""

        # Shell cleanup:
        location.set_description('Clear shell files')
        self._add_hook(location, system_context,
                       '_teardown', 'run', 'test', '-x', '/usr/bin/zsh',
                       '&&', 'rm', '-rf', '/usr/share/zsh',
                       shell=True, returncode=None)
        self._add_hook(location, system_context,
                       '_teardown', 'run', 'test', '-x', '/usr/bin/bash',
                       '&&', 'rm', '-rf', '/usr/share/bash-completion',
                       shell=True, returncode=None)
