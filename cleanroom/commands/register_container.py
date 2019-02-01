"""register_container command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.helper.file import exists
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import os.path
import textwrap
import typing


def _nspawnify(what: str, *systems: str) -> str:
    clean = [s for s in systems if s]
    if len(clean) > 0:
        return '\n{}={}'.format(what, ' '.join(*clean))
    return ''


class RegisterContainerCommand(Command):
    """The register_container command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__('register_container', syntax='<SYSTEM> '
                         'description=<DESC> extra_args=<ARG>(,<ARG>)* '
                         'timeout=3m after=<SYSTEM>(,<SYSTEM>)* '
                         'requires=<SYSTEM>(,<SYSTEM>)*'
                         'enable=False [machine=<directory>]',
                         help_string='Register a container with a system.',
                         file=__file__, **services)

    def validate(self, location: Location,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Validate the arguments."""
        self._validate_args_exact(location, 1, '"{}" needs a system to '
                                  'install as a container.', *args)
        self._validate_kwargs(location, ('description', 'extra_args', 'after',
                                         'requires', 'timeout', 'enable', 'machine'),
                              **kwargs)
        self._require_kwargs(location, ('description',), **kwargs)

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        system = args[0]
        description = kwargs.get('description', '')
        extra_args_input = kwargs.get('extra_args', '')
        after_input = kwargs.get('after', '')
        requires_input = kwargs.get('requires', '')
        timeout = kwargs.get('timeout', '3m')
        enable = kwargs.get('enable', False)
        machine = kwargs.get('machine', system)

        bin_directory = '/usr/bin'
        systemd_directory = '/usr/lib/systemd/system'

        location.set_description('Update update-all-containers.sh')
        updater_script = os.path.join(bin_directory,
                                      'update-all-containers.sh')

        if not exists(system_context, updater_script):
            self._execute(location.next_line(), system_context,
                          'create', updater_script, '#!/usr/bin/bash\n')
        self._execute(location.next_line(), system_context,
                      'append', updater_script, '/usr/bin/update-container.sh "{}" || exit 1\n')

        location.set_description('')
        override_dir = '{}/systemd-nspawn@{}.service.d'.format(systemd_directory, system)
        self._execute(location.next_line(), system_context, 'mkdir', override_dir)

        extra_args = ' \\\n    '.join(extra_args_input.split(','))
        if extra_args:
            extra_args = ' \\\n    ' + extra_args + '\n'
        after = _nspawnify('After', *after_input.split(','))
        requires = _nspawnify('Requires', *requires_input.split(','))

        self._execute(location.next_line(), system_context,
                      'create', '{}/override.conf'.format(override_dir),
                      textwrap.dedent('''\
                      [Unit]
                      Description=Container {system}: {description}{after}{requires}
                       
                      [Service]
                      TimeoutStartSec={timeout}
                      ExecStart=
                      ExecStart=/usr/bin/systemd-nspawn --quiet --keep-unit --boot --ephemeral \\
                          --machine={machine}{extra_args}
                      ''').format(system=system, description=description,
                                  after=after, requires=requires, extra_args=extra_args,
                                  timeout=timeout, machine=machine))

        if enable:
            location.set_description('Enabling container')
            self._execute(location.next_line(), system_context, 'symlink',
                          '../systemd-nspawn@.service',
                          'systemd-nspawn@{}.service'.format(system),
                          work_directory='{}/machines.target.wants'
                          .format(systemd_directory))
