# -*- coding: utf-8 -*-
"""tar command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

from cleanroom.generator.command import Command
from cleanroom.generator.context import Binaries
from cleanroom.generator.systemcontext import SystemContext
from cleanroom.location import Location

import os.path
import typing


class TarCommand(Command):
    """The tar command."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__('tar',
                         syntax='<SOURCE> <TARGET> '
                         '[to_outside=False] [compress=False] '
                         '[work_directory=<DIR>]',
                         help_string='Create a tarball.', file=__file__)

    def validate_arguments(self, location: Location, *args: typing.Any, **kwargs: typing.Any) \
            -> typing.Optional[str]:
        """Validate the arguments."""
        self._validate_args_exact(location, 2,
                                  '"{}" needs a source and a target.', *args)
        self._validate_kwargs(location,
                              ('to_outside', 'compress', 'work_directory',),
                              **kwargs)

        return None

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        source = args[0]
        target = args[1]
        to_outside = kwargs.get('to_ouside', False)
        compress = kwargs.get('compress', False)
        work_directory = kwargs.get('work_directory', None)

        arguments = ['-c']
        if compress:
            arguments += ['-z']

        if work_directory:
            work_directory = system_context.file_name(work_directory)
        source = system_context.file_name(source)
        if to_outside:
            assert os.path.isabs(target)
        else:
            target = system_context.file_name(target)

        system_context.run(system_context.binary(Binaries.TAR),
                           *arguments, '-f', target, source,
                           work_directory=work_directory,
                           outside=True)
