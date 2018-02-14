#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The class that runs a list of commands on a system.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from . import runcontext

import os
import os.path


class Executor:
    """Run a list of commands on a system."""

    def run(self, ctx, system, command_list):
        """Run the command_list for the system the executor was set up for."""
        ctx.printer.h2('Running commands for system "{}".'.format(system),
                       verbosity=2)
        run_context = runcontext.RunContext(ctx, system)
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
