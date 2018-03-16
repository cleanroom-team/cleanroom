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

        run_context.ctx.printer\
            .trace('Running commands for system "{}".'
                   .format(run_context.system))

        self._run_commands(command_list, run_context)

    def _setup_for_execution(self, run_context):
        if self._system_already_built(run_context):
            return False

        """Set up execution context."""
        run_context.ctx.printer\
            .trace('Setup for execution of commands of "{}".'
                   .format(run_context.system))

        return True

    def _system_already_built(self, run_context):
        """Check whether system has been built already."""
        return os.path.isdir(run_context.storage_directory(run_context.system))

    def _run_commands(self, command_list, run_context):
        """Run commands."""
        for command in command_list:
            os.chdir(run_context.ctx.systems_directory())
            command.execute(run_context)


if __name__ == '__main__':
    pass
