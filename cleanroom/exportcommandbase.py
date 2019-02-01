# -*- coding: utf-8 -*-
"""Base class for export related commands.

The Command class will be used to derive all export_* commands from.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from .command import Command
from .exceptions import GenerateError
from .location import Location
from .printer import debug, h2, info, verbose
from .systemcontext import SystemContext

import os.path
import typing


class ExportCommandBase(Command):
    """The export Command."""

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        """Constructor."""
        super().__init__(*args, **kwargs)

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        self.set_args_and_kwargs(*args, **kwargs)
        
        h2('Exporting system "{}".'.format(system_context.system_name))
        debug('Running Hooks.')
        self._run_all_exportcommand_hooks(system_context)

        verbose('Preparing system for export.')
        self.prepare_for_export(location, system_context)

        info('Validating installation for export.')
        self._validate_installation(location.next_line(), system_context)

        export_directory \
            = self.create_export_directory(location.next_line(), system_context)
        assert export_directory

        # Document export_type
        with open(os.path.join(export_directory, 'export_type'), 'wb') as et:
            et.write(self.name.encode('utf-8'))

        system_context.set_substitution('EXPORT_DIRECTORY', export_directory)

        verbose('Exporting all data in {}.'.format(export_directory))
        self._execute(location.next_line(), system_context,
                      '_export_directory', export_directory)

        info('Cleaning up export location.')
        self.delete_export_directory(system_context, export_directory)

    def set_args_and_kwargs(self, *args: typing.Any, **kwargs: typing.Any) \
            -> None:
        """Set arguments and kwargs."""
        pass

    def prepare_for_export(self, location: Location,
                           system_context: SystemContext) -> None:
        """Prepare the current system for export.

        Called before the actual export directory is created."""
        pass

    def create_export_directory(self, location: Location,
                                system_context: SystemContext) -> str:
        """Override to put all data to export into export_directory.

        Must return the directory to actually export.
        """
        return ''

    def delete_export_directory(self, system_context: SystemContext,
                                export_directory: str) -> None:
        """Override to clean up the export_directory again."""
        assert False

    def extra_validation(self, location: Location,
                         system_context: SystemContext) -> None:
        """Add extra validation steps here."""
        pass

    def _validate_installation(self, location: Location,
                               system_context: SystemContext) -> None:
        hostname = system_context.substitution('HOSTNAME')
        if hostname is None:
            raise GenerateError('Trying to export a system without a hostname.',
                                location=location)
        if hostname != system_context.system_name:
            raise GenerateError('Trying to export a system with an '
                                'unexpected hostname.',
                                location=location)
        machine_id = system_context.substitution('MACHINE_ID')
        if machine_id is None:
            raise GenerateError('Trying to export a system without '
                                'a machine_id.',
                                location=location)
        self.extra_validation(location, system_context)

    def _run_all_exportcommand_hooks(self, system_context: SystemContext) \
            -> None:
        self._run_hooks(system_context, '_teardown')
        self._run_hooks(system_context, 'export')

        # Now do tests!
        self._run_hooks(system_context, 'testing')
