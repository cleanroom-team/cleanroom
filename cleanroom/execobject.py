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

    def __init__(self, location, name, dependency, command, *args, **kwargs):
        """Constructor."""
        self._name = name
        self._command = command
        self._args = args
        self._kwargs = kwargs
        self._dependency = dependency
        self._location = location

    def dependency(self):
        """Return dependency of the system (or None)."""
        return self._dependency

    def __str__(self):
        """Turn into string object."""
        return '{}({}): {}'.format(self._location[0], self._location[1],
                                   self._name)

    def execute(self, run_context):
        """Execute the command."""
        command_object = self._command
        run_context.set_command(self._name)
        run_context.ctx.printer.debug('Running "{}" with arguments ({}).'
                                      .format(self._name,
                                              ', '.join(self._args),
                                              ', '.join(self._kwargs)))

        try:
            command_object(run_context, *self._args, **self._kwargs)
        except ex.CleanRoomError as e:
            run_context.ctx.printer.fail('{}: Failed to run "{}" with '
                                         'arguments ({}): {}.'
                                         .format(self._location,
                                                 self._name,
                                                 ', '.join(self._args),
                                                 ', '.join(self._kwargs), e),
                                         verbosity=1)
            if not run_context.ctx.ignore_errors:
                raise
        else:
            run_context.ctx.printer.success('{}: Ran "{}" with '
                                            'arguments ({}, {}).'
                                            .format(self._location,
                                                    self._name,
                                                    ', '.join(self._args),
                                                    ', '.join(self._kwargs)),
                                            verbosity=1)
        finally:
            run_context.set_command(None)
