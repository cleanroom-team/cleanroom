# -*- coding: utf-8 -*-
"""The class that holds context data for the executor.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from __future__ import annotations

from .location import Location
from .printer import h2, info, success, trace
from .execobject import ExecObject

import os
import os.path
import pickle
import string
import typing


class SystemContext:
    """Context data for the execution os print_commands."""

    def __init__(self, *,
                 scratch_directory: str,
                 systems_definition_directory: str,
                 system_name: str, timestamp: str) -> None:
        """Constructor."""
        assert scratch_directory
        assert systems_definition_directory

        self._system_name = system_name
        self._timestamp = timestamp
        self._scratch_directory = scratch_directory
        self._systems_definition_directory = systems_definition_directory

        self._base_context: typing.Optional[SystemContext] = None
        self._hooks: typing.Dict[str, typing.List[ExecObject]] = {}
        self._hooks_that_already_ran: typing.List[str] = []
        self._substitutions: typing.MutableMapping[str, str] = {}

        self._setup_core_substitutions()

    def __enter__(self) -> typing.Any:
        h2('Creating system {}'.format(self._system_name))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        success('System {} created.'.format(self._system_name))
        return False

    @property
    def timestamp(self) -> str:
        return self._timestamp

    @property
    def system_name(self) -> str:
        return self._system_name

    @property
    def system_helper_directory(self) -> str:
        return os.path.join(self._systems_definition_directory, self.system_name)

    @property
    def system_tests_directory(self) -> str:
        return os.path.join(self._systems_definition_directory, 'tests')

    @property
    def scratch_directory(self) -> str:
        return self._scratch_directory

    @property
    def fs_directory(self) -> str:
        return os.path.join(self._scratch_directory, 'fs')

    @property
    def boot_directory(self) -> str:
        return os.path.join(self._scratch_directory, 'boot')

    @property
    def meta_directory(self) -> str:
        return os.path.join(self._scratch_directory, 'meta')

    @property
    def cache_directory(self) -> str:
        return os.path.join(self._scratch_directory, 'cache')

    def _setup_core_substitutions(self) -> None:
        """Core substitutions that may not get overridden by base system."""
        if self.base_context:
            self.set_substitution('BASE_SYSTEM', self.base_context.system_name)
        else:
            self.set_substitution('BASE_SYSTEM', '')

        self.set_substitution('ROOT', self.fs_directory)
        self.set_substitution('META', self.meta_directory)
        self.set_substitution('CACHE', self.cache_directory)
        self.set_substitution('SYSTEM', self.system_name)
        ts = 'unknown' if self.timestamp is None else self.timestamp
        self.set_substitution('TIMESTAMP', ts)
        self.set_substitution('BASE_SYSTEM', ':'.join(self.base_context.system_name) \
            if self.base_context else '')

        self.set_substitution('DISTRO_NAME', 'cleanroom')
        self.set_substitution('DISTRO_PRETTY_NAME', 'cleanroom')
        self.set_substitution('DISTRO_ID', 'clrm')
        self.set_substitution('DISTRO_VERSION', ts)
        self.set_substitution('DISTRO_VERSION_ID', ts)

        self.set_substitution('DEFAULT_VG', 'vg_int')

        self.set_substitution('IMAGE_FS', 'btrfs')
        self.set_substitution('IMAGE_OPTIONS', 'rw,subvol=/.images')
        self.set_substitution('IMAGE_DEVICE', '/dev/disk/by-partlabel/fs_btrfs')

    # Handle Hooks:
    def _add_hook(self, hook: str, exec_obj: ExecObject) -> None:
        """Add a hook."""
        if not exec_obj:
            return

        info('FIXME: Adding hook "{}": {}.'.format(hook, exec_obj))
        # FIXME: Implement this!
        # self.hooks.setdefault(hook, []).append(exec_obj)
        # trace('Hook {} has {} entries.'.format(hook, len(self.hooks[hook])))

    def add_hook(self, location: Location, hook: str,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Add a hook."""
        assert len(args) > 0
        self._add_hook(hook, ExecObject(location=location,
                                        command=args[0],
                                        args=args[1:],
                                        kwargs=kwargs))

    def hooks(self, hook_name: str) -> typing.Sequence[ExecObject]:
        """Run all the registered hooks."""
        return self._hooks.get(hook_name, [])

        # exec_obj_list = self._hooks.setdefault(hook, [])
        # trace('Runnnig hook {} with {} entries.'.format(hook, len(exec_obj_list)))
        # if not exec_obj_list:
        #     return
        #
        # h3('Running {} hooks.'.format(hook), verbosity=1)
        # for exec_obj in exec_obj_list:
        #     os.chdir(self.systems_directory())
        #     self.execute(exec_obj.location(),
        #                  exec_obj.command(), *exec_obj.arguments(), **exec_obj.kwargs())
        # success('All {} hooks were run successfully.'.format(hook), verbosity=2)
        #
        # self.hooks_that_already_ran.append(hook)

    # Handle substitutions:
    @property
    def substitutions(self) -> typing.Mapping[str, str]:
        return self._substitutions

    def set_substitution(self, key: str, value: str) -> None:
        """Add a substitution to the substitution table."""
        self._substitutions[key] = value
        trace('Added substitution: "{}"="{}".'.format(key, value))

    def substitution(self, key: str,
                     default_value: typing.Optional[str] = None) -> typing.Any:
        """Get substitution value."""
        return self.substitutions.get(key, default_value)

    def has_substitution(self, key: str) -> bool:
        """Check wether a substitution is defined."""
        return key in self.substitutions

    def substitute(self, text: str) -> str:
        """Substitute variables in text."""
        return string.Template(text).substitute(**self.substitutions)

    # # Run shell print_commands:
    # def run(self, *args: typing.Any, outside: bool = False,
    #         **kwargs: typing.Any) -> subprocess.CompletedProcess:
    #     """Run a command in this system_context."""
    #     assert 'chroot' not in kwargs
    #
    #     mapped_args = map(lambda a: self.substitute(str(a)), args)
    #
    #     stdout = kwargs.get('stdout', None)
    #     if stdout is not None:
    #         stdout = self.substitute(stdout)
    #     kwargs['stdout'] = stdout
    #
    #     stderr = kwargs.get('stderr', None)
    #     if stderr is not None:
    #         stderr = self.substitute(stderr)
    #     kwargs['stderr'] = stderr
    #
    #     if not outside:
    #         kwargs['chroot'] = self.fs_directory()
    #
    #     return run(*mapped_args, trace_output=debug,
    #                chroot_helper=self.binary(Binaries.CHROOT_HELPER),
    #                **kwargs)
    #
    # # execute cleanroom print_commands:
    # def execute(self, location: Location, command: str, *args: typing.Any,
    #             expected_dependency: typing.Optional[str] = None,
    #             **kwargs: typing.Any) -> None:
    #     """Execute a command."""
    #     assert location is not None
    #     assert location.is_valid()
    #     assert isinstance(location, Location)
    #     assert isinstance(command, str)
    #
    #     debug('Executing {}: {}.'.format(location, command))
    #
    #     cmd = self._command_manager.command(command)
    #     if not cmd:
    #         raise GenerateError('Command {} not found.'.format(command),
    #                             location=location)
    #
    #     child = location.create_child(file_name='<COMMAND "{}">'.format(command),
    #                                   description='{} {},{}'.format(command, args, kwargs))
    #
    #     dependency = cmd.validate_arguments(child, *args, **kwargs)
    #     if expected_dependency != dependency:
    #         raise GenerateError('Command {} returned an unexpected dependency (got: {}, expected: {}).'
    #                             .format(command, dependency, expected_dependency),
    #                             location=location)
    #
    #     trace('{}: Argument validation complete.'.format(command))
    #     trace('{}: Execute...'.format(command))
    #
    #     assert child is not None
    #     cmd(child, self, *args, **kwargs)

    # Store/Restore a system:
    def install_base_context(self, base_context: SystemContext) -> None:
        """Set up base context."""
        assert base_context.system_name

        self._base_context = base_context
        self._timestamp = base_context._timestamp
        self._hooks = base_context._hooks
        self._substitutions = base_context._substitutions

    @property
    def base_context(self) -> typing.Optional[SystemContext]:
        return self._base_context

    def _pickle_jar(self) -> str:
        return os.path.join(self.meta_directory, 'pickle_jar.bin')

    def pickle(self) -> None:
        """Pickle this system_context."""
        pickle_jar = self._pickle_jar()

        # Remember stuff that should not get saved:
        hooks_that_ran = self._hooks_that_already_ran
        self._hooks_that_already_ran = []

        trace('Pickling system_context into {}.'.format(pickle_jar))
        with open(pickle_jar, 'wb') as pj:
            pickle.dump(self, pj)

        # Restore state that should not get saved:
        self._hooks_that_already_ran = hooks_that_ran

    def unpickle(self) -> SystemContext:
        """Create a new system_context by unpickling a file."""
        pickle_jar = self._pickle_jar()

        with open(pickle_jar, 'rb') as pj:
            base_context = pickle.load(pj)
        trace('Base context was unpickled.')
        return base_context
