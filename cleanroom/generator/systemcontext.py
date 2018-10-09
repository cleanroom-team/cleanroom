# -*- coding: utf-8 -*-
"""The class that holds context data for the executor.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from __future__ import annotations

from .command import Command
from .commandmanager import CommandManager
from .context import Binaries, Context
from .execobject import ExecObject
from .helper.generic.file import (expand_files, file_name)

from ..exceptions import GenerateError
from ..location import Location
from ..printer import (debug, h3, info, success, trace,)

from ..helper.run import run

import os
import os.path
import pickle
import string
import typing


class _SystemContextPickler(pickle.Pickler):
    """Pickler for the SystemContext."""

    def persistent_id(self, obj: typing.Any) -> typing.Optional[typing.Tuple[str, str]]:
        """Treat commands special when pickling."""
        if isinstance(obj, Command):
            return ('Command', obj.name())
        return None


class _SystemContextUnpickler(pickle.Unpickler):
    """Unpickler for the SystemContext."""

    def __init__(self, jar: typing.IO[bytes],
                 command_manager: CommandManager) -> None:
        self._command_manager = command_manager
        super().__init__(jar)

    def persistent_load(self, pid) -> typing.Optional[Command]:
        tag, cmd = pid

        if tag == 'Command':
            return self._command_manager.command(cmd)
        else:
            raise pickle.UnpicklingError('Unsupported persistent object.')


class SystemContext:
    """Context data for the execution os commands."""

    def __init__(self, ctx: Context, command_manager: CommandManager, *,
                 system: str, timestamp: typing.Optional[str]=None) -> None:
        """Constructor."""
        self.ctx: typing.Optional[Context] = ctx
        self._command_manager = command_manager
        self.system = system
        self.base_context: typing.Optional[SystemContext] = None
        self.timestamp = timestamp
        self.hooks: typing.Dict[str, typing.List[ExecObject]] = {}
        self.hooks_that_already_ran: typing.List[str] = []
        self.substitutions: typing.MutableMapping[str, str] = {}
        self.bases: typing.Tuple[str, ...] = ()

        self._setup_core_substitutions()

        assert self.ctx
        assert self.system

    def create_system_context(self, system: str) -> SystemContext:
        assert self.ctx
        return SystemContext(self.ctx, self._command_manager, system=system,
                             timestamp=self.timestamp)

    def _setup_core_substitutions(self) -> None:
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

        self.set_substitution('DISTRO_NAME', 'cleanroom')
        self.set_substitution('DISTRO_PRETTY_NAME', 'cleanroom')
        self.set_substitution('DISTRO_ID', 'clrm')
        self.set_substitution('DISTRO_VERSION', ts)
        self.set_substitution('DISTRO_VERSION_ID', ts)

        self.set_substitution('DEFAULT_VG', 'vg_int')

        self.set_substitution('IMAGE_FS', 'ext2')
        self.set_substitution('IMAGE_OPTIONS', 'rw')
        self.set_substitution('IMAGE_DEVICE', '')

    def binary(self, selector: Binaries) -> typing.Optional[str]:
        """Forwarded to Context.binary."""
        assert self.ctx
        return self.ctx.binary(selector)

    def systems_directory(self) -> str:
        assert self.ctx
        base = self.ctx.systems_directory()
        assert base
        return base

    def current_system_directory(self) -> str:
        """Forwarded to Context.current_system_directory."""
        assert self.ctx
        base = self.ctx.current_system_directory()
        assert base
        return base

    # Important Directories:
    def storage_directory(self) -> str:
        """Location to store system when finished building it."""
        assert self.ctx
        base = self.ctx.storage_directory()
        assert base
        return os.path.join(base, self.system)

    def fs_directory(self) -> str:
        """Location of the systems filesystem root."""
        return os.path.join(self.current_system_directory(), 'fs')

    def boot_data_directory(self) -> str:
        """Location of the systems filesystem root."""
        return os.path.join(self.current_system_directory(), 'boot')

    def meta_directory(self) -> str:
        """Location of the systems meta-data directory."""
        return os.path.join(self.current_system_directory(), 'meta')

    def cache_directory(self) -> str:
        """Location of the systems meta-data directory."""
        return os.path.join(self.current_system_directory(), 'cache')

    # Work with system files:
    def expand_files(self, *files: str) -> typing.List[str] :
        """Map and expand files from inside to outside paths."""
        return expand_files(self, *files)

    def file_name(self, path: str) -> str:
        """Map a file from inside to outside path."""
        if not os.path.isabs(path):
            return path
        return file_name(self, path)

    # Handle Hooks:
    def _add_hook(self, hook: str, exec_obj: typing.Optional[ExecObject]) -> None:
        """Add a hook."""
        if not exec_obj:
            return

        info('Adding hook "{}": {}.'.format(hook, exec_obj))
        self.hooks.setdefault(hook, []).append(exec_obj)
        trace('Hook {} has {} entries.'.format(hook, len(self.hooks[hook])))

    def add_hook(self, location: Location, hook: str,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Add a hook."""
        assert isinstance(hook, str)
        if len(args) == 0:
            raise GenerateError('No command passed to add_hook.', location=location)
        command_name = args[0]
        cmd = self._command_manager.command(command_name)
        if not cmd:
            raise GenerateError('Invalid command passed to add_hook.',
                                location=location)
        self._add_hook(hook, cmd.exec_object(location, *args[1:], **kwargs))

    def run_hooks(self, hook: str):
        """Run all the registered hooks."""
        if hook in self.hooks_that_already_ran:
            trace('Skipping hooks "{}": Already ran them.'.format(hook))
            return

        exec_obj_list = self.hooks.setdefault(hook, [])
        trace('Runnnig hook {} with {} entries.'.format(hook, len(exec_obj_list)))
        if not exec_obj_list:
            return

        h3('Running {} hooks.'.format(hook), verbosity=1)
        for exec_obj in exec_obj_list:
            os.chdir(self.systems_directory())
            self.execute(exec_obj.location(),
                         exec_obj.command(), *exec_obj.arguments(), **exec_obj.kwargs())
        success('All {} hooks were run successfully.', verbosity=2)

        self.hooks_that_already_ran.append(hook)

    # Handle substitutions:
    def set_substitution(self, key: str, value: str):
        """Add a substitution to the substitution table."""
        self.substitutions[key] = value
        trace('Added substitution: "{}"="{}".'.format(key, value))

    def substitution(self, key: str, default_value: typing.Optional[str]=None):
        """Get substitution value."""
        return self.substitutions.get(key, default_value)

    def has_substitution(self, key: str) -> bool:
        """Check wether a substitution is defined."""
        return key in self.substitutions

    def substitute(self, text: str) -> str:
        """Substitute variables in text."""
        return string.Template(text).substitute(**self.substitutions)

    # Run shell commands:
    def run(self, *args: typing.Any, outside: bool=False, **kwargs: typing.Any):
        """Run a command in this system_context."""
        assert 'chroot' not in kwargs

        mapped_args = map(lambda a: self.substitute(str(a)), args)

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

        return run(*mapped_args, trace_output=debug, **kwargs)

    # execute cleanroom commands:
    def execute(self, location: Location, command: str, *args: typing.Any,
                expected_dependency: typing.Optional[str]=None, **kwargs: typing.Any) -> None:
        """Execute a command."""
        assert location is not None
        assert location.is_valid()
        assert isinstance(location, Location)
        assert isinstance(command, str)

        debug('Executing {}: {}.'.format(location, command))

        cmd = self._command_manager.command(command)
        if not cmd:
            raise GenerateError('Command {} not found.'.format(command),
                                location=location)

        child = location.create_child(file_name='<COMMAND "{}">'.format(command),
                                      description='{} {},{}'.format(command, args, kwargs))

        dependency = cmd.validate_arguments(child, *args, **kwargs)
        if expected_dependency != dependency:
            raise GenerateError('Command {} returned an unexpected dependency (got: {}, expected: {}).'
                                .format(command, dependency, expected_dependency),
                                location=location)

        trace('{}: Argument validation complete.'.format(command))
        trace('{}: Execute...'.format(command))

        assert child is not None
        cmd(child, self, *args, **kwargs)

    # Store/Restore a system:
    def install_base_context(self, base_context: SystemContext) -> None:
        """Set up base context."""
        assert base_context.system

        self.base_context = base_context
        self.timestamp = base_context.timestamp
        self.hooks = base_context.hooks
        self.substitutions = base_context.substitutions
        self.bases = (*base_context.bases, base_context.system)

        self._setup_core_substitutions()  # Fore core substitutions

    def _pickle_jar(self) -> str:
        return os.path.join(self.meta_directory(), 'pickle_jar.bin')

    def pickle(self) -> None:
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

    def unpickle(self) -> None:
        """Create a new system_context by unpickling a file."""
        pickle_jar = self._pickle_jar()

        debug('Unpickling system_context from {}.'.format(pickle_jar))
        with open(pickle_jar, 'rb') as jar:
            base_context = _SystemContextUnpickler(jar, self._command_manager).load()
        debug('Unpickled base context.')
        return base_context
