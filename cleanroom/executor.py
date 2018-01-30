#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The class that runs a list of commands on a system.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import os
import os.path


class RunContext:
    """Context data for the execution os commands."""

    def __init__(self, ctx, system):
        """Constructor."""
        self._ctx = ctx
        self._system = system
        self._vars = dict()

        assert(self._ctx)
        assert(self._system)
        assert(not self._vars)

    def _base_directory(self):
        """Find base directory for all temporary system files."""
        return os.path.join(self._ctx.work_systems_directory(), self._system)

    def system_directory(self):
        """Location of temporary system files."""
        return self._base_directory()

    def fs_directory(self):
        """Location of the systems filesystem root."""
        return os.path.join(self._base_directory(), 'fs')

    def meta_directory(self):
        """Location of the systems meta-data directory."""
        return os.path.join(self._base_directory(), 'meta')

    def system_complete_flag(self):
        """Flag-file set when system was completely set up."""
        return os.path.join(self._base_directory(), 'done')


class Executor:
    """Run a list of commands on a system."""

    def run(self, ctx, system, command_list):
        """Run the command_list for the system the executor was set up for."""
        ctx.printer.debug('Running commands for system "{}".'.format(system))
        run_context = RunContext(ctx, system)
        if not self._setup_for_execution(run_context):
            return  # Return early when system already set up

        self._run_commands(command_list, run_context)
        self._store_result(run_context)

    def _setup_for_execution(self, run_context):
        """Set up execution context."""
        run_context._ctx.printer\
            .trace('Setup for execution of commands of "{}".'
                   .format(run_context._system))

        os.makedirs(run_context.fs_directory())
        os.makedirs(run_context.meta_directory())

        return not os.path.exists(run_context.system_complete_flag())

    def _run_commands(self, command_list, run_context):
        """Run commands."""
        run_context._ctx.printer\
            .trace('Running commands for system "{}".'
                   .format(run_context._system))

        for command in command_list:
            command.execute(run_context)

    def _store_result(self, run_context):
        """Store execution context and extra data."""
        run_context._ctx.printer.\
            trace('Store execution results for system "{}".'
                  .format(run_context._system))


if __name__ == '__main__':
    pass
