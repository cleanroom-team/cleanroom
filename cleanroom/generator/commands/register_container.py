"""register_container command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.generator.command import Command
from cleanroom.generator.helper.generic.file import exists

import os.path


class RegisterContainerCommand(Command):
    """The register_container command."""

    def __init__(self):
        """Constructor."""
        super().__init__('register_container', syntax='<SYSTEM> '
                         'description=<DESC> extra_args=<ARG>(,<ARG>)* '
                         'timeout=3m after=<SYSTEM>(,<SYSTEM>)* '
                         'requires=<SYSTEM>(,<SYSTEM>)*'
                         'enable=False [machine=<directory>]',
                         help='Register a container with a system.',
                         file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_args_exact(location, 1, '"{}" needs a system to '
                                  'install as a container.', *args)
        self._validate_kwargs(location, ('description', 'extra_args', 'after',
                                         'requires', 'timeout', 'enable', 'machine'),
                              **kwargs)
        self._require_kwargs(location, ('description',), **kwargs)

    def _nspawnify(self, what, *systems):
        clean = [s for s in systems if s]
        if len(clean) > 0:
            return '\n{}={}'.format(what, ' '.join(*clean))
        return ''

    def __call__(self, location, system_context, *args, **kwargs):
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
            system_context.execute(location.next_line(), 'create', updater_script,
                                   '#!/usr/bin/bash\n')
        system_context.execute(location.next_line(), 'append', updater_script,
                               '/usr/bin/update-container.sh "{}" || exit 1\n')

        location.set_description('')
        override_dir = '{}/systemd-nspawn@{}.service.d'.format(systemd_directory, system)
        system_context.execute(location.next_line(), 'mkdir', override_dir)

        extra_args = ' \\\n    '.join(extra_args_input.split(','))
        if extra_args:
            extra_args = ' \\\n    ' + extra_args + '\n'
        after = self._nspawnify('After', *after_input.split(','))
        requires = self._nspawnify('Requires', *requires_input.split(','))

        system_context.execute(location.next_line(), 'create',
                               '{}/override.conf'.format(override_dir),
                               '''[Unit]
Description=Container {system}: {description}{after}{requires}

[Service]
TimeoutStartSec={timeout}
ExecStart=
ExecStart=/usr/bin/systemd-nspawn --quiet --keep-unit --boot --ephemeral \\
    --machine={machine}{extra_args}
'''.format(system=system, description=description, after=after,
           requires=requires, extra_args=extra_args, timeout=timeout,
           machine=machine))

        if enable:
            location.set_description('Enabling container')
            system_context.execute(location.next_line(), 'symlink',
                                   '../systemd-nspawn@.service',
                                   'systemd-nspawn@{}.service'.format(system),
                                   work_directory='{}/machines.target.wants'
                                   .format(systemd_directory))
