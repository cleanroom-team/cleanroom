# -*- coding: utf-8 -*-
"""run command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.binarymanager import Binaries
from cleanroom.command import Command
from cleanroom.helper.run import run
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

from string import Template
import typing


class RunCommand(Command):
    """The run command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__('run',
                         syntax='<COMMAND> [<ARGS>] [inside=False] '
                         '[shell=False] [returncode=0] [stdout=None] '
                         '[stderr=None]',
                         help_string='Run a command inside/outside of the '
                         'current system.', file=__file__, **services)

    def validate(self, location: Location,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Validate the arguments."""
        self._validate_args_at_least(location, 1,
                                     '"{}" needs a command to run and '
                                     'optional arguments.', *args)
        self._validate_kwargs(location, ('returncode', 'inside', 'shell',
                                         'stderr', 'stdout'),
                              **kwargs)

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        if kwargs.pop('inside', 'False'):
            kwargs['chroot'] = system_context.fs_directory
            kwargs['chroot_helper'] = self._binary(Binaries.CHROOT_HELPER)

        run(*Command._stringify_args(system_context, args), **kwargs)
