# -*- coding: utf-8 -*-
"""tar command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.generator.command import Command
from cleanroom.generator.context import Binaries
from cleanroom.helper.run import run


class TarCommand(Command):
    """The tar command."""

    def __init__(self):
        """Constructor."""
        super().__init__('tar',
                         syntax='<SOURCE> <TARGET> '
                         '[to_outside=False] [compress=False] '
                         '[work_directory=<DIR>]',
                         help='Create a tarball.', file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_args_exact(location, 2,
                                  '"{}" needs a source and a target.', *args)
        self._validate_kwargs(location,
                              ('to_outside', 'compress', 'work_directory',),
                              **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        source = args[0]
        target = args[1]
        to_outside = kwargs.get('to_ouside', False)
        compress = kwargs.get('compress', False)
        work_directory = kwargs.get('work_directory', None)

        args = ['-c']
        if compress:
            args += ['-z']

        if work_directory:
            work_directory = system_context.file_name(work_directory)
        source = system_context.file_name(source)
        if to_outside:
            assert os.path.isabs(target)
        else:
            target = system_context.file_name(target)

        system_context.run(system_context.binary(Binaries.TAR),
                           *args, '-f', target, source,
                           work_directory=work_directory,
                           outside=True)
