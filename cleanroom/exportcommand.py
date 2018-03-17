#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Base class for export related commands.

The Command class will be used to derive all export_* commands from.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from . import command as cmd
from . import context as context
from . import exceptions as ex


class ExportCommand(cmd.Command):
    """The export Command."""

    def __init__(self, syntax_string, help_string):
        """Constructor."""
        super().__init__(syntax_string, help_string)

    def __call__(self, file_name, line_number, run_context, *args, **kwargs):
        """Execute command."""
        run_context.ctx.printer.h2('Exporting system "{}".'
                                   .format(run_context.system))
        run_context.ctx.printer.debug('Running Hooks.')
        self._run_hooks(run_context)

        run_context.ctx.printer.debug('Validating installation for export.')
        self._validate_installation(run_context,
                                    file_name=file_name,
                                    line_number=line_number)

        export_directory = self.create_export_directory(run_context)

        run_context.ctx.printer.debug('Exporting all data in {}.'
                                      .format(export_directory))
        self._export(run_context, export_directory)

        run_context.ctx.printer.debug('Cleaning up export location.')
        self.delete_export_directory(run_context, export_directory)

    def create_export_directory(self, run_context):
        """Override to put all data to export into export_directory.

        Must return the directory to actually export.
        """
        assert(False)

    def delete_export_directory(self, run_context, export_directory):
        """Override to put all data to export into export_directory."""
        assert(False)

    def extra_validation(self, run_context, *, file_name='', line_number=-1):
        """Add extra validation steps here."""
        pass

    def _validate_installation(self, run_context, *,
                               file_name='', line_number=-1):
        hostname = run_context.substitution('HOSTNAME')
        if hostname is None:
            raise ex.GenerateError('Trying to export a system without '
                                   'a hostname.',
                                   file_name=file_name,
                                   line_number=line_number)
        machine_id = run_context.substitution('MACHINE_ID')
        if machine_id is None:
            raise ex.GenerateError('Trying to export a system without '
                                   'a machine_id.',
                                   file_name=file_name,
                                   line_number=line_number)
        self.extra_validation(run_context,
                              file_name=file_name, line_number=line_number)

    def _run_hooks(self, run_context):
        run_context.run_hooks('_teardown')
        run_context.run_hooks('export')

        # Now do tests!
        run_context.run_hooks('testing')

    def _export(self, run_context, export_directory):
        repository = run_context.ctx.export_repository()
        if repository == '':
            return

        borg = run_context.ctx.binary(context.Binaries.BORG)
        backup_name = run_context.system + '-' + run_context.timestamp

        run_context.run(borg, 'create', '--compression', 'zstd,22',
                        '--numeric-owner', '--noatime',
                        '{}::{}'.format(repository, backup_name),
                        export_directory, outside=True)


class Command:
    """A command that can be used in to set up machines."""

    def __init__(self, syntax_string, help_string):
        """Constructor."""
        self._syntax_string = syntax_string
        self._help_string = help_string

    def name(self):
        """Return the command name."""
        return self.__module__[19:]  # minus cleanroom.commands.

    def validate_arguments(self, file_name, line_number, *args, **kwargs):
        """Validate all arguments.

        Validate all arguments and optionally return a dependency for
        the system.
        """
        if len(args) != 0:
            raise ex.ParseError('Command does not take arguments.',
                                file_name=file_name, line_number=line_number)
        return None

    def __call__(self, file_name, line_number, run_context, *args, **kwargs):
        """Execute command."""
        return True

    def syntax(self):
        """Return syntax description."""
        return self._syntax_string

    def help(self):
        """Print help string."""
        return self._help_string
