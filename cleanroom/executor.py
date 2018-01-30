#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The class that runs a list of commands on a system.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import datetime
import os
import os.path


class RunContext:
    """Context data for the execution os commands."""

    def __init__(self, ctx, system):
        """Constructor."""
        self.ctx = ctx
        self.system = system
        self.base = None
        self.vars = dict()
        self.timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        self.baseContext = None

        assert(self.ctx)
        assert(self.system)
        assert(not self.vars)

    def _work_directory(self, system=None):
        """Find base directory for all temporary system files."""
        if system is None:
            system = self.system
        return os.path.join(self.ctx.work_systems_directory(), system)

    def system_directory(self):
        """Location of temporary system files."""
        return self._work_directory()

    def fs_directory(self):
        """Location of the systems filesystem root."""
        return os.path.join(self._work_directory(), 'fs')

    def meta_directory(self, system=None):
        """Location of the systems meta-data directory."""
        return os.path.join(self._work_directory(system), 'meta')

    def pickle_jar(self, system=None):
        """Location of the system's pickle jar."""
        return os.path.join(self.meta_directory(system), 'pickle_jar.bin')

    def system_complete_flag(self):
        """Flag-file set when system was completely set up."""
        return os.path.join(self._work_directory(), 'done')

    def install_base_context(self, base_context):
        """Set up base context."""
        self.baseContext = base_context
        self.timestamp = base_context.timestamp
        print('Timestamp is now:', self.timestamp)


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
        run_context.ctx.printer\
            .trace('Setup for execution of commands of "{}".'
                   .format(run_context.system))

        os.makedirs(run_context.fs_directory())
        os.makedirs(run_context.meta_directory())

        return not os.path.exists(run_context.system_complete_flag())

    def _run_commands(self, command_list, run_context):
        """Run commands."""
        run_context.ctx.printer\
            .trace('Running commands for system "{}".'
                   .format(run_context.system))

        for command in command_list:
            command.execute(run_context)

    def _store_result(self, run_context):
        """Store execution context and extra data."""
        run_context.ctx.printer.\
            trace('Store execution results for system "{}".'
                  .format(run_context.system))


if __name__ == '__main__':
    pass
