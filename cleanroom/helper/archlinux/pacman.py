#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The class that drives the system generation.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.context as context
import cleanroom.exceptions as ex
import cleanroom.helper.generic.file as file

import os
import os.path


class Pacman:
    """Drives Pacman."""

    def __init__(self, run_context):
        """Constructor."""
        self._run_context = run_context
        assert(self._package_type() is None or
               self._package_type() == 'pacman')

    def _package_type(self):
        return self._run_context.flags.get('package_type', None)

    def _set_package_type(self):
        self._run_context.flags['package_type'] = 'pacman'

    def target_gpg_directory(self):
        """Return the gpg directory path inside the system filesystem."""
        return '/usr/lib/pacman/gpg'

    def host_gpg_directory(self):
        """Return the host location of the pacman GPG configuration."""
        return file.file_name(self._run_context, self.target_gpg_directory())

    def target_db_directory(self):
        """Return the pacman db directory path inside the system filesystem."""
        return '/usr/lib/pacman/db'

    def host_db_directory(self):
        """Return the host location of the pacman DB."""
        return file.file_name(self._run_context, self.target_db_directory())

    def target_cache_directory(self):
        """Return the target pacman cache directory path."""
        return '/var/cache/pacman'

    def host_cache_directory(self):
        """Return the host location of the pacman cache."""
        return file.file_name(self._run_context, self.target_cache_directory())

    def initial_pacstrap_configuration_file(self, run_context):
        """Return the host configuration for initial pacstrap run."""
        init_config_path = os.path.join(
            self._run_context.system_definition_directory(),
            'pacstrap.conf')
        if not os.path.isfile(init_config_path):
            raise ex.GenerateError('Could not find: "{}".'
                                   .format(init_config_path))
        return init_config_path

    def pacstrap(self, config, packages):
        """Run pacstrap on host."""
        assert(self._package_type() is None)

        self._sync_host(config)

        all_packages = []
        for a in packages:
            all_packages += a.split()

        self._run_context.run(
            self._run_context.ctx.binary(context.Binaries.PACSTRAP),
            '-c',  # use cache on host
            '-d',  # No mount point
            '-M',  # Do not copy host mirrorlist
            '-G',  # Do not copy host keyring
            '-C', config,  # Use config file
            self._run_context.fs_directory(),
            '--dbpath={}'.format(self.host_db_directory()),
            '--gpgdir={}'.format(self.host_gpg_directory()),
            *all_packages,
            work_directory=self._run_context.ctx.systems_directory(),
            outside=True)

        self._set_package_type()

    def _sync_host(self, config):
        """Run pacman -Syu on the host."""
        os.makedirs(self.host_db_directory())
        self._run_context.run(
            self._run_context.ctx.binary(context.Binaries.PACMAN),
            '-Syu', '--config', config, '--dbpath', self.host_db_directory(),
            outside=True)

    def pacman(self, *packages):
        """Use pacman to install packages."""
        assert(self._package_type() == 'pacman')

        self._run_context.ctx.printer.info('Installing {}'
                                           .format(', '.join(packages)))
        self._run_context.run(
            self._run_context.ctx.binary(context.Binaries.PACMAN),
            '-S', *packages)


if __name__ == '__main__':
    pass
