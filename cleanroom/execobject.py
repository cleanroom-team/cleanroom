#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parse system definition files.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from . import exceptions as ex


class ExecObject:
    """Describe command in system definition file.

    Describe the command to execute later during generation phase.
    """

    def __init__(self, name, file_name, line_number, line_offset,
                 dependency, command, *args, **kwargs):
        """Constructor."""
        self._name = name
        self._command = command
        self._args = args
        self._kwargs = kwargs
        self._dependency = dependency
        self._file_name = file_name
        self._line_number = line_number
        self._line_offset = line_offset

    def dependency(self):
        """Return dependency of the system (or None)."""
        return self._dependency

    def __str__(self):
        """Turn into string object."""
        return '{}:{}({})): {}'.format(self._file_name,
                                       self._line_number,
                                       self._line_offset,
                                       self._name)

    def execute(self, run_context):
        """Execute the command."""
        command_object = self._command
        run_context.set_command(self._name,
                                file_name=self._file_name,
                                line_number=self._line_number,
                                line_offset=self._line_offset)
        run_context.ctx.printer.debug('Running "{}" with arguments ({}:{}).'
                                      .format(self._name,
                                              ', '.join(self._args),
                                              ', '.join(self._kwargs)))

        try:
            command_object(run_context, *self._args, **self._kwargs)
        except ex.CleanRoomError as e:
            run_context.ctx.printer.fail('{}: Failed to run: {}.'
                                         .format(self, e),
                                         verbosity=1)
            if not run_context.ctx.ignore_errors:
                raise
        else:
            run_context.ctx.printer.success('{}: ok.'.format(self),
                                            verbosity=1)
        finally:
            run_context.reset_command()
