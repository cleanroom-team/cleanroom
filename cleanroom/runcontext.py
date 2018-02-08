#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The class that holds context data for the executor.

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
        self.hooks = {}

        self._command = None

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

    def system_definition_directory(self):
        """Return the top level system definition directory of a system."""
        return self.ctx.system_definition_directory(self.system)

    def set_command(self, command_name):
        """Set the command name."""
        self._command = command_name

    def add_hook(self, hook, executable_object):
        """Add a hook."""
        self.hooks[hook] += [executable_object]


if __name__ == '__main__':
    pass
