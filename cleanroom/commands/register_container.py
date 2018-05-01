"""register_container command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.helper.generic.file as file

import os.path


class RegisterContainerCommand(cmd.Command):
    """The register_container command."""

    def __init__(self):
        """Constructor."""
        super().__init__('register_container', syntax='<SYSTEM> '
                         'description=<DESC> extra_args=<ARG>(,<ARG>)* '
                         'timeout=3m after=<SYSTEM>(,<SYSTEM>)* '
                         'requires=<SYSTEM>(,<SYSTEM>)*',
                         help='Register a container with a system.',
                         file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_args_exact(location, 1, '"{}" needs a system to '
                                  'install as a container.', *args)
        self._validate_kwargs(location, ('description', 'extra_args', 'after',
                                         'requires', 'timeout'),
                              **kwargs)
        self._require_kwargs(location, ('description',), **kwargs)

    def _nspawnify(*systems):
        result = ' '.join(map(lambda a: 'systemd-nspawn@{}.service'.format(a),
                              systems))
        if result:
            result += '\n'
        return result

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        system = args[0]
        description = kwargs.get('description', '')
        extra_args_input = kwargs.get('extra_args', '')
        after_input = kwargs.get('after', '')
        requires_input = kwargs.get('requires', '')
        timeout = kwargs.get('timeout', '3m')

        bin_directory = '/usr/bin'
        systemd_directory = '/usr/lib/systemd/system'

        location.next_line_offset('Update update-all-containers.sh')
        updater_script = os.path.join(bin_directory,
                                      'update-all-containers.sh')

        if not file.exists(system_context, updater_script):
            system_context.execute(location, 'create', updater_script,
                                   '#!/usr/bin/bash\n')
        system_context.execute(location, 'append', updater_script,
                               '/usr/bin/update-container.sh "{}" || exit 1\n')

        location.next_line_offset('')
        system_context.execute(location, 'mkdir', '{}/systemd-nspawn@{}.d'
                               .format(systemd_directory, system))

        extra_args = '\n'.join(extra_args_input.split(','))
        if extra_args:
            extra_args = '\n' + extra_args + '\n'
        after = self._nspawnify(after_input.split(','))
        requires = self._nspawnify(requires_input.split(','))

        system_context.execute(location, 'create',
                               '{}/systemd-nspawn@{}.d/'
                               'override.conf'
                               .format(systemd_directory, system), '''[Unit]
Description=Container {system}: {description}
{after}{requires}
[Service]
TimeoutStartSec={timeout}m
ExecStart=
ExecStart=/usr/bin/systemd-nspawn --quiet --keep-unit --boot --ephemeral \
    --machine={system}{extra_args}
'''.format(system=system, description=description, after=after,
           requires=requires, extra_args=extra_args, timeout=timeout))

        location.next_line_offset('Enabling container')
        system_context.execute(location, 'symlink',
                               '../systemd-nspawn@.service',
                               'systemd-nspawn@{}.service'.format(system),
                               base_directory='{}/machines.target.wants'
                               .format(systemd_directory))
