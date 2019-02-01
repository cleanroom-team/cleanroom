# -*- coding: utf-8 -*-
"""tar command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

from cleanroom.binarymanager import Binaries
from cleanroom.command import Command
from cleanroom.helper.run import run
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import os.path
import typing


class TarCommand(Command):
    """The tar command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__('tar',
                         syntax='<SOURCE> <TARGET> '
                         '[to_outside=False] [compress=False] '
                         '[work_directory=<DIR>]',
                         help_string='Create a tarball.',
                         file=__file__, **services)

    def validate(self, location: Location,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Validate the arguments."""
        self._validate_args_exact(location, 2,
                                  '"{}" needs a source and a target.', *args)
        self._validate_kwargs(location,
                              ('to_outside', 'compress', 'work_directory',),
                              **kwargs)

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        source = system_context.file_name(args[0])

        to_outside = kwargs.get('to_outside', False)

        target = args[1] if to_outside else system_context.file_name(args[1])
        assert os.path.isabs(target)

        compress = kwargs.get('compress', False)
        work_directory = system_context.file_name(kwargs.get('work_directory', '/'))

        arguments = ['-c']
        if compress:
            arguments += ['-z']

        run(self._binary(Binaries.TAR), *arguments, '-f', target, source,
            work_directory=work_directory)
