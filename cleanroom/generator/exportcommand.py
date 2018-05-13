# -*- coding: utf-8 -*-
"""Base class for export related commands.

The Command class will be used to derive all export_* commands from.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from .command import Command

from ..exceptions import GenerateError
from ..printer import (debug, h2, trace)

import os.path


class ExportCommand(Command):
    """The export Command."""

    def __init__(self, *args, **kwargs):
        """Constructor."""
        super().__init__(*args, **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        h2('Exporting system "{}".'.format(system_context.system))
        debug('Running Hooks.')
        self._run_hooks(system_context)

        trace('Preparing system for export.')
        self.prepare_for_export(location, system_context)

        trace('Validating installation for export.')
        self._validate_installation(location, system_context)

        export_directory \
            = self.create_export_directory(location, system_context)

        # Document export_type
        with open(os.path.join(export_directory, 'export_type'), 'wb') as et:
            et.write(self.name().encode('utf-8'))

        system_context.set_substitution('EXPORT_DIRECTORY', export_directory)

        trace('Exporting all data in {}.'.format(export_directory))
        self._export(location, system_context, export_directory)

        trace('Cleaning up export location.')
        self.delete_export_directory(system_context, export_directory)

    def prepare_for_export(self, location, system_context):
        """Prepare the current system for export.

        Called before the actual export directory is created."""
        pass

    def create_export_directory(self, location, system_context):
        """Override to put all data to export into export_directory.

        Must return the directory to actually export.
        """
        assert(False)

    def delete_export_directory(self, system_context, export_directory):
        """Override to clean up the export_directory again."""
        assert(False)

    def extra_validation(self, location, system_context):
        """Add extra validation steps here."""
        pass

    def _validate_installation(self, location, system_context):
        hostname = system_context.substitution('HOSTNAME')
        if hostname is None:
            raise GenerateError('Trying to export a system without a hostname.',
                                location=location)
        machine_id = system_context.substitution('MACHINE_ID')
        if machine_id is None:
            raise GenerateError('Trying to export a system without a machine_id.',
                                location=location)
        self.extra_validation(location, system_context)

    def _run_hooks(self, system_context):
        system_context.run_hooks('_teardown')
        system_context.run_hooks('export')

        # Now do tests!
        system_context.run_hooks('testing')

    def _export(self, location, system_context, export_directory):
        system_context.execute(location, '_export_directory', export_directory)
