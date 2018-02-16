#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The class that holds context data for the executor.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as command
import cleanroom.helper.generic.run as run
import cleanroom.parser as parser

import datetime
import os
import os.path
import pickle
import string


class _RunContextPickler(pickle.Pickler):
    """Pickler for the RunContext."""

    def persistent_id(self, obj):
        """Treat commands special when pickling."""
        if isinstance(obj, command.Command):
            return ('Command', obj.name())
        return None


class _RunContextUnpickler(pickle.Unpickler):
    """Unpickler for the RunContext."""

    def persistent_load(self, pid):
        tag, cmd = pid

        if tag == 'Command':
            return parser.Parser.command(cmd)
        else:
            raise pickle.UnpicklingError('Unsupported persistent object.')


class RunContext:
    """Context data for the execution os commands."""

    def __init__(self, ctx, system):
        """Constructor."""
        self.ctx = ctx
        self.system = system
        self.base_system = None
        self.timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        self.base_context = None
        self.hooks = {}
        self.hooks_that_already_ran = []
        self.substitutions = {}
        self.flags = {}

        self._command = None

        self._setup_substitutions()

        assert(self.ctx)
        assert(self.system)

    def _setup_substitutions(self):
        self.set_substitution('TIMESTAMP', self.timestamp)
        self.set_substitution('SYSTEM', self.system)

    @staticmethod
    def _work_directory(ctx, system):
        """Find base directory for all temporary system files."""
        return os.path.join(ctx.work_systems_directory(), system)

    @staticmethod
    def _meta_directory(ctx, system):
        """Find the metadata directory of system."""
        return os.path.join(RunContext._work_directory(ctx, system), 'meta')

    def _fs_directory(ctx, system):
        """Find the root filesystem directory of a system."""
        return os.path.join(RunContext._work_directory(ctx, system), 'fs')

    def system_directory(self, system=None):
        """Location of temporary system files."""
        if system is None:
            system = self.system
        return RunContext._work_directory(self.ctx, system)

    def fs_directory(self, system=None):
        """Location of the systems filesystem root."""
        if system is None:
            system = self.system
        return RunContext._fs_directory(self.ctx, system)

    def meta_directory(self, system=None):
        """Location of the systems meta-data directory."""
        if system is None:
            system = self.system
        return RunContext._meta_directory(self.ctx, system)

    @staticmethod
    def _pickle_jar(ctx, system):
        """Location of the system's pickle jar."""
        return os.path.join(RunContext._meta_directory(ctx, system),
                            'pickle_jar.bin')

    def _install_base_context(self, base_context):
        """Set up base context."""
        self.base_context = base_context
        self.timestamp = base_context.timestamp
        self.hooks = base_context.hooks
        self.substitutions = base_context.substitutions
        self.flags = base_context.flags

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
        if hook in self.hooks_that_already_ran:
            self.ctx.printer.trace('Skipping hooks "{}": Already ran them.'
                                   .format(hook))
            return

        command_list = self.hooks.setdefault(hook, [])
        self.ctx.printer.trace('Runnnig hook {} with {} entries.'
                               .format(hook, len(command_list)))
        if not command_list:
            return

        self.ctx.printer.h2('Running {} hooks.'.format(hook), verbosity=1)
        for cmd in command_list:
            cmd.execute(self)

        self.hooks_that_already_ran.append(hook)

    def set_substitution(self, key, value):
        """Add a substitution to the substitution table."""
        self.substitutions[key] = value

    def substitute(self, text):
        """Substitute variables in text."""
        template = string.Template(text)
        return template.substitute(self.substitutions)

    def run(self, *args, outside=False, **kwargs):
        """Run a command in this run_context."""
        assert('chroot' not in kwargs)

        if not outside:
            kwargs['chroot'] = self.fs_directory()
        return run.run(*args, trace_output=self.ctx.printer.trace, **kwargs)

    def pickle(self):
        """Pickle this run_context."""
        pickle_jar = RunContext._pickle_jar(self.ctx, self.system)

        ctx = self.ctx
        hooks_that_ran = self.hooks_that_already_ran

        ctx.printer.debug('Pickling run_context into {}.'.format(pickle_jar))
        self.ctx = None  # Disconnect context for the pickling!
        self.hooks_that_already_ran = []

        with open(pickle_jar, 'wb') as jar:
            _RunContextPickler(jar).dump(self)

        # Restore state that should not get saved:
        self.ctx = ctx
        self.hooks_that_already_ran = hooks_that_ran

    def unpickle_base_context(self, system):
        """Create a new run_context by unpickling a file."""
        pickle_jar = RunContext._pickle_jar(self.ctx, system)

        self.ctx.printer.debug('Unpickling base run_context from {}.'
                               .format(pickle_jar))
        with open(pickle_jar, 'rb') as jar:
            base_context = _RunContextUnpickler(jar).load()
        self._install_base_context(base_context)


if __name__ == '__main__':
    pass
