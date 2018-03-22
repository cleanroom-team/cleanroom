#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Manage pacman and pacstrap calls.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.context as context
import cleanroom.exceptions as ex
import cleanroom.helper.generic.file as file

import os
import os.path


def _package_type(run_context):
    return run_context.flags.get('package_type', None)


def _set_package_type(run_context):
    run_context.flags['package_type'] = 'pacman'


def target_gpg_directory():
    """Return the gpg directory path inside the system filesystem."""
    return '/usr/lib/pacman/gpg'


def host_gpg_directory(run_context):
    """Return the host location of the pacman GPG configuration."""
    return file.file_name(run_context, target_gpg_directory())


def target_db_directory():
    """Return the pacman db directory path inside the system filesystem."""
    return '/usr/lib/pacman/db'


def host_db_directory(run_context):
    """Return the host location of the pacman DB."""
    return file.file_name(run_context, target_db_directory())


def target_cache_directory():
    """Return the target pacman cache directory path."""
    return '/var/cache/pacman'


def host_cache_directory(run_context):
    """Return the host location of the pacman cache."""
    return file.file_name(run_context, target_cache_directory())


def initial_pacstrap_configuration_file(run_context):
    """Return the host configuration for initial pacstrap run."""
    init_config_path = os.path.join(
        run_context.system_definition_directory(),
        'pacstrap.conf')
    if not os.path.isfile(init_config_path):
        raise ex.GenerateError('Could not find: "{}".'
                               .format(init_config_path))
    return init_config_path


def pacstrap(run_context, config, *packages):
    """Run pacstrap on host."""
    assert(_package_type(run_context) is None)

    _sync_host(run_context, config)

    run_context.run(
        run_context.ctx.binary(context.Binaries.PACSTRAP),
        '-c',  # use cache on host
        '-d',  # No mount point
        '-M',  # Do not copy host mirrorlist
        '-G',  # Do not copy host keyring
        '-C', config,  # Use config file
        run_context.fs_directory(),
        '--dbpath={}'.format(host_db_directory(run_context)),
        '--gpgdir={}'.format(host_gpg_directory(run_context)),
        *packages,
        work_directory=run_context.ctx.systems_directory(),
        outside=True)

    _set_package_type(run_context)


def _sync_host(run_context, config):
    """Run pacman -Syu on the host."""
    os.makedirs(host_db_directory(run_context))
    run_context.run(
        run_context.ctx.binary(context.Binaries.PACMAN),
        '-Syu', '--config', config, '--dbpath', host_db_directory(run_context),
        outside=True)


def pacman(self, run_context, *packages):
    """Use pacman to install packages."""
    assert(_package_type(run_context) == 'pacman')

    run_context.ctx.printer.info('Installing {}'
                                 .format(', '.join(packages)))
    run_context.run(
        run_context.ctx.binary(context.Binaries.PACMAN),
        '-S', '--noconfirm', '--needed', *packages)


if __name__ == '__main__':
    pass
