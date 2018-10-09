# -*- coding: utf-8 -*-
"""pacstrap command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.generator.command import Command
from cleanroom.generator.helper.archlinux.pacman import pacstrap
from cleanroom.generator.systemcontext import SystemContext
from cleanroom.location import Location

import os.path
import typing


class PacstrapCommand(Command):
    """The pacstrap command."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__('pacstrap', syntax='<PACKAGES> config=<config>',
                         help='Run pacstrap to install <PACKAGES>.\n'
                         'Hooks: Will runs _setup hooks after pacstrapping.',
                         file=__file__)

    def validate_arguments(self, location: Location,
                           *args: str, **kwargs: typing.Any) -> typing.Optional[str]:
        """Validate the arguments."""
        self._validate_args_at_least(location, 1,
                                     '"{}" needs at least one package '
                                     'or group to install.', *args)
        self._validate_kwargs(location, ('config',), **kwargs)
        self._require_kwargs(location, ('config',), **kwargs)

        return None

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: str, **kwargs: typing.Any) -> bool:
        """Execute command."""
        pacstrap(system_context, *args, **kwargs)

        system_context.run_hooks('_setup')

        system_context.execute(location.next_line(), 'create_os_release')

        self._setup_hooks(location, system_context)

        return True

    def _setup_hooks(self, location: Location, system_context: SystemContext) -> None:
        igpgdir = '/usr/lib/pacman/gpg'
        ipackages = '/var/cache/pacman/pkg/*'

        location.set_description('cleanup pacman-key files (internal)')
        system_context.add_hook(location, '_teardown', 'remove',
                                igpgdir + '/S.*', igpgdir + '/pubring.gpg~',
                                igpgdir + '/secring.gpg*',
                                '/var/log/pacman.log', ipackages,
                                recursive=True, force=True)

        location.set_description('Cleanup pacman-key files (external)')
        ogpgdir = os.path.join(system_context.meta_directory(), 'pacman/gpg')
        system_context.add_hook(location, '_teardown', 'remove',
                                ogpgdir + '/S.*', ogpgdir + '/pubring.gpg~',
                                ogpgdir + '/secring.gpg*',
                                recursive=True, force=True, outside=True)

        location.set_description('Move systemd files into /usr')
        system_context.add_hook(location, '_teardown', 'systemd_cleanup')

        location.set_description('Moving /opt into /usr')
        system_context.add_hook(location.next_line(), 'export', 'move', '/opt', '/usr')
        system_context.add_hook(location, 'export', 'symlink',
                                'usr/opt', 'opt', base_directory='/')

        location.set_description('Writing package information to FS.')
        system_context.add_hook(location.next_line(), 'export',
                                '_pacman_write_package_data')
