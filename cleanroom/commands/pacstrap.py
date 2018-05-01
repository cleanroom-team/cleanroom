# -*- coding: utf-8 -*-
"""pacstrap command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.context as context
import cleanroom.helper.archlinux.pacman as arch
import cleanroom.helper.generic.file as file

import os.path


class PacstrapCommand(cmd.Command):
    """The pacstrap command."""

    def __init__(self):
        """Constructor."""
        super().__init__('pacstrap', syntax='<PACKAGES> config=<CONFIG_FILE>',
                         help='Run pacstrap to install <PACKAGES>.\n'
                         'Hooks: Will runs _setup hooks after pacstrapping.',
                         file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_args_at_least(location, 1,
                                     '"{}" needs at least one package '
                                     'or group to install.', *args)
        self._validate_kwargs(location, ('config',), **kwargs)
        self._require_kwargs(location, ('config',), **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        pacstrap_config = kwargs['config']
        self._prepare_keyring(system_context, location, pacstrap_config)

        arch.pacstrap(system_context, pacstrap_config, *args)

        # Install pacman.conf:
        system_context.execute(location, 'copy',
                               os.path.join(
                                   system_context.ctx.systems_directory(),
                                   pacstrap_config),
                               '/etc/pacman.conf', from_outside=True, force=True)

        # Make sure DB is up-to-date:
        system_context.run('/usr/bin/pacman-db-upgrade')

        system_context.execute(location, 'remove', '/var/lib/pacman',
                               recursive=True, force=True)

        system_context.set_substitution('PACKAGE_TYPE', 'pacman')

        system_context.run_hooks('_setup')

        # Make sure pacman DB is up-to-date:
        system_context.run('/usr/bin/pacman', '-Sy')
        system_context.run('/usr/bin/pacman', '-Fy')

        system_context.add_hook(location, 'export', 'move', '/opt', '/usr')
        system_context.add_hook(location, 'export', 'symlink',
                                'usr/opt', 'opt', base_directory='/')

    def _prepare_keyring(self, system_context, location, pacstrap_config):
        # Make sure important pacman directories exist:
        file.makedirs(system_context, arch.host_gpg_directory(system_context))
        pacman_key = system_context.ctx.binary(context.Binaries.PACMAN_KEY)
        systems_directory = system_context.ctx.systems_directory()
        system_context.run(pacman_key,
                           '--config', pacstrap_config,
                           '--gpgdir', arch.host_gpg_directory(system_context),
                           '--init',
                           exit_code=0, outside=True,
                           work_directory=systems_directory)
        system_context.run(pacman_key,
                           '--config', pacstrap_config,
                           '--gpgdir', arch.host_gpg_directory(system_context),
                           '--populate', 'archlinux',
                           exit_code=0, outside=True,
                           work_directory=systems_directory)

        gpgdir = arch.target_gpg_directory()
        packageFiles = arch.target_cache_directory() + '/pkg/*'

        location.next_line_offset('cleanup pacman-key files')
        system_context.add_hook(location, '_teardown', 'remove',
                                gpgdir + '/S.*', gpgdir + '/pubring.gpg~',
                                '/var/log/pacman.log',
                                packageFiles,
                                recursive=True, force=True)
        location.next_line_offset('Move systemd files into /usr')
        system_context.add_hook(location, '_teardown', 'systemd_cleanup')
        location.next_line_offset('Remove pacman secret keyring')
        system_context.add_hook(location, 'export',
                                'remove', gpgdir + '/secring.gpg*', force=True)
