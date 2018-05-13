# -*- coding: utf-8 -*-
"""The class that holds context data for the executor.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from .command import Command
from .helper.generic.file import (expand_files, file_name)
from .parser import Parser

from ..location import Location
from ..printer import (debug, h3, info, trace,)

from ..helper.run import run

import os
import os.path
import pickle
import string


class _SystemContextPickler(pickle.Pickler):
    """Pickler for the SystemContext."""

    def persistent_id(self, obj):
        """Treat commands special when pickling."""
        if isinstance(obj, Command):
            return ('Command', obj.name())
        return None


class _SystemContextUnpickler(pickle.Unpickler):
    """Unpickler for the SystemContext."""

    def persistent_load(self, pid):
        tag, cmd = pid

        if tag == 'Command':
            return Parser.command(cmd)
        else:
            raise pickle.UnpicklingError('Unsupported persistent object.')


class SystemContext:
    """Context data for the execution os commands."""

    def __init__(self, ctx, *, system, timestamp=None):
        """Constructor."""
        self.ctx = ctx
        self.system = system
        self.base_context = None
        self.timestamp = timestamp
        self.hooks = {}
        self.hooks_that_already_ran = []
        self.substitutions = {}
        self.bases = ()

        self._setup_core_substitutions()

        assert(self.ctx)
        assert(self.system)

    def _setup_core_substitutions(self):
        """Core substitutions that may not get overriden by base system."""
        if self.base_context:
            self.set_substitution('BASE_SYSTEM', self.base_context.system)
        else:
            self.set_substitution('BASE_SYSTEM', '')

        self.set_substitution('ROOT', self.fs_directory())
        self.set_substitution('SYSTEM', self.system)
        ts = 'unknown' if self.timestamp is None else self.timestamp
        self.set_substitution('TIMESTAMP', ts)
        self.set_substitution('CLRM_BASES', ':'.join(self.bases))

    def binary(self, selector):
        """Forwarded to Context.binary."""
        return self.ctx.binary(selector)

    def current_system_directory(self):
        """Forwarded to Context.current_system_directory."""
        return self.ctx.current_system_directory()

    # Important Directories:
    def storage_directory(self):
        """Location to store system when finished building it."""
        return os.path.join(self.ctx.storage_directory(), self.system)

    def fs_directory(self):
        """Location of the systems filesystem root."""
        return os.path.join(self.ctx.current_system_directory(), 'fs')

    def boot_data_directory(self):
        """Location of the systems filesystem root."""
        return os.path.join(self.ctx.current_system_directory(), 'boot')

    def meta_directory(self):
        """Location of the systems meta-data directory."""
        return os.path.join(self.ctx.current_system_directory(), 'meta')

    # Work with system files:
    def expand_files(self, *files):
        """Map and expand files from inside to outside paths."""
        return expand_files(self, *files)

    def file_name(self, path):
        """Map a file from inside to outside path."""
        if not os.path.isabs(path):
            return path
        return file_name(self, path)

    # Handle Hooks:
    def _add_hook(self, hook, exec_object):
        """Add a hook."""
        assert(exec_object is not None)

        info('Adding hook "{}": {}.'.format(hook, exec_object))
        self.hooks.setdefault(hook, []).append(exec_object)
        trace('Hook {} has {} entries.'.format(hook, len(self.hooks[hook])))

    def add_hook(self, location, hook, *args, **kwargs):
        """Add a hook."""
        assert(isinstance(hook, str))
        self._add_hook(hook, Parser.create_execute_object(location,
                                                          *args, **kwargs))

    def run_hooks(self, hook):
        """Run all the registered hooks."""
        if hook in self.hooks_that_already_ran:
            trace('Skipping hooks "{}": Already ran them.'.format(hook))
            return

        command_list = self.hooks.setdefault(hook, [])
        trace('Runnnig hook {} with {} entries.'.format(hook, len(command_list)))
        if not command_list:
            return

        h3('Running {} hooks.'.format(hook), verbosity=1)
        for cmd in command_list:
            os.chdir(self.ctx.systems_directory())
            self.execute(cmd.location(),
                         cmd.command(), *cmd.arguments(), **cmd.kwargs())

        self.hooks_that_already_ran.append(hook)

    # Handle substitutions:
    def set_substitution(self, key, value):
        """Add a substitution to the substitution table."""
        self.substitutions[key] = value
        trace('Added substitution: "{}"="{}".'.format(key, value))

    def substitution(self, key, default_value=None):
        """Get substitution value."""
        return self.substitutions.get(key, default_value)

    def has_substitution(self, key):
        """Check wether a substitution is defined."""
        return key in self.substitutions

    def substitute(self, text):
        """Substitute variables in text."""
        return string.Template(text).substitute(**self.substitutions)

    # Run shell commands:
    def run(self, *args, outside=False, **kwargs):
        """Run a command in this system_context."""
        assert('chroot' not in kwargs)

        args = map(lambda a: self.substitute(str(a)), args)

        stdout = kwargs.get('stdout', None)
        if stdout is not None:
            stdout = self.substitute(stdout)
        kwargs['stdout'] = stdout

        stderr = kwargs.get('stderr', None)
        if stderr is not None:
            stderr = self.substitute(stderr)
        kwargs['stderr'] = stderr

        if not outside:
            kwargs['chroot'] = self.fs_directory()

        return run(*args, trace_output=debug, **kwargs)

    # execute cleanroom commands:
    def execute(self, location, command, *args,
                expected_dependency=None, **kwargs):
        """Execute a command."""
        assert(isinstance(location, Location))
        assert(isinstance(command, str))
        debug('Executing {}: {}.'.format(location, command))
        cmd = Parser.command(command)
        dependency = cmd.validate_arguments(location, *args, **kwargs)
        assert(expected_dependency == dependency)
        trace('{}: Argument validation complete.'.format(command))
        location.next_line_offset(command)
        trace('{}: Execute...'.format(command))
        cmd(location, self, *args, **kwargs)

    # Store/Restore a system:
    def install_base_context(self, base_context):
        """Set up base context."""
        assert(base_context.system)

        self.base_context = base_context
        self.timestamp = base_context.timestamp
        self.hooks = base_context.hooks
        self.substitutions = base_context.substitutions
        self.bases = (*base_context.bases, base_context.system)

        self._setup_core_substitutions()  # Fore core substitutions

    def _pickle_jar(self):
        return os.path.join(self.meta_directory(), 'pickle_jar.bin')

    def pickle(self):
        """Pickle this system_context."""
        ctx = self.ctx

        pickle_jar = self._pickle_jar()
        hooks_that_ran = self.hooks_that_already_ran

        debug('Pickling system_context into {}.'.format(pickle_jar))
        self.ctx = None  # Disconnect context for the pickling!
        self.hooks_that_already_ran = []

        with open(pickle_jar, 'wb') as jar:
            _SystemContextPickler(jar).dump(self)

        # Restore state that should not get saved:
        self.ctx = ctx
        self.hooks_that_already_ran = hooks_that_ran

    def unpickle(self):
        """Create a new system_context by unpickling a file."""
        pickle_jar = self._pickle_jar()

        debug('Unpickling system_context from {}.'.format(pickle_jar))
        with open(pickle_jar, 'rb') as jar:
            base_context = _SystemContextUnpickler(jar).load()
        return base_context
