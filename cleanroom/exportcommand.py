# -*- coding: utf-8 -*-
"""Base class for export related commands.

The Command class will be used to derive all export_* commands from.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.exceptions as ex
import cleanroom.printer as printer


class ExportCommand(cmd.Command):
    """The export Command."""

    def __init__(self, *args, **kwargs):
        """Constructor."""
        super().__init__(*args, **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        printer.h2('Exporting system "{}".'.format(system_context.system))
        printer.debug('Running Hooks.')
        self._run_hooks(system_context)

        printer.debug('Validating installation for export.')
        self._validate_installation(location, system_context)

        export_directory = self.create_export_directory(system_context)
        system_context.set_substitution('EXPORT_DIRECTORY', export_directory)

        printer.debug('Exporting all data in {}.'.format(export_directory))
        self._export(location, system_context, export_directory)

        printer.debug('Cleaning up export location.')
        self.delete_export_directory(system_context, export_directory)

    def create_export_directory(self, system_context):
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
            raise ex.GenerateError('Trying to export a system without '
                                   'a hostname.',
                                   location=location)
        machine_id = system_context.substitution('MACHINE_ID')
        if machine_id is None:
            raise ex.GenerateError('Trying to export a system without '
                                   'a machine_id.',
                                   location=location)
        self.extra_validation(location, system_context)

    def _run_hooks(self, system_context):
        system_context.run_hooks('_teardown')
        system_context.run_hooks('export')

        # Now do tests!
        system_context.run_hooks('testing')

    def _export(self, location, system_context, export_directory):
        system_context.execute(location, '_export_directory', export_directory)
