#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The class that holds context data for the executor.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import datetime
import os
import os.path
import string


class RunContext:
    """Context data for the execution os commands."""

    def __init__(self, ctx, system):
        """Constructor."""
        self.ctx = ctx
        self.system = system
        self.base = None
        self.timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        self.baseContext = None
        self.hooks = {}
        self.substitutions = {}

        self._command = None

        self._setup_substitutions()

        assert(self.ctx)
        assert(self.system)

    def _setup_substitutions(self):
        self.set_substitution('TIMESTAMP', self.timestamp)
        self.set_substitution('SYSTEM', self.system)

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
        self.hooks = base_context.hooks
        self.substitutions = base_context.substitutions

        self._setup_substitutions()  # Override critical substitutions again:-)

    def system_definition_directory(self):
        """Return the top level system definition directory of a system."""
        return self.ctx.system_definition_directory(self.system)

    def set_command(self, command_name):
        """Set the command name."""
        self._command = command_name

    def add_hook(self, hook, exec_object):
        """Add a hook."""
        self.hooks.setdefault(hook, []).append(exec_object)
        self.ctx.printer.trace('Hook {} has {} entries.'
                               .format(hook, len(self.hooks[hook])))

    def run_hooks(self, hook):
        """Run all the registered hooks."""
        command_list = self.hooks.setdefault(hook, [])
        self.ctx.printer.trace('Runnnig hook {} with {} entries.'
                               .format(hook, len(command_list)))
        if not command_list:
            return

        self.ctx.printer.h2('Running {} hooks.'.format(hook))
        for command in command_list:
            command.execute(self)

    def set_substitution(self, key, value):
        """Add a substitution to the substitution table."""
        self.substitutions[key] = value

    def substitute(self, text):
        """Substitute variables in text."""
        template = string.Template(text)
        return template.substitute(self.substitutions)


if __name__ == '__main__':
    pass
