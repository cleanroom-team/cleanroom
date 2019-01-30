# -*- coding: utf-8 -*-
"""Manage pacman and pacstrap calls.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from ...systemcontext import SystemContext
from ...printer import debug, info, verbose
from ..run import run

import os
import os.path
import shutil
import stat
import typing


def _package_type(system_context: SystemContext) -> typing.Optional[str]:
    return system_context.substitution('CLRM_PACKAGE_TYPE', '')


def _set_package_type(system_context: SystemContext) -> None:
    system_context.set_substitution('CLRM_PACKAGE_TYPE', 'pacman')


def _pacman_state(system_context: SystemContext) -> bool:
    return system_context.substitution('PACMAN_INSTALL_STATE', str(False))


def _set_pacman_state(system_context: SystemContext, internal: bool = False) -> None:
    system_context.set_substitution('PACMAN_INSTALL_STATE', str(internal))


def _fs_directory(system_context: SystemContext) -> str:
    return system_context.fs_directory


def _pacman_directory(system_context: SystemContext, internal: bool = False) -> str:
    if internal:
        return system_context.file_name('/usr/lib/pacman')
    return os.path.join(system_context.meta_directory, 'pacman')


def _config_file(system_context: SystemContext, internal: bool = False) -> str:
    if internal:
        return system_context.file_name('/etc/pacman.conf')
    return os.path.join(_pacman_directory(system_context, internal), 'pacman.conf')


def _db_directory(system_context: SystemContext, internal: bool = False) -> str:
    return os.path.join(_pacman_directory(system_context, internal), 'db')


def _hooks_directory(system_context: SystemContext, internal: bool = False) -> str:
    return os.path.join(_pacman_directory(system_context, internal), 'hooks')


def _gpg_directory(system_context: SystemContext, internal: bool = False) -> str:
    """Return the host location of the pacman GPG configuration."""
    return os.path.join(_pacman_directory(system_context, internal), 'gpg')


def _base_cache_directory(system_context: SystemContext, internal: bool = False) -> str:
    if internal:
        return os.path.join(system_context.fs_directory, 'var/cache')
    return system_context.cache_directory


def _cache_directory(system_context: SystemContext, internal: bool = False) -> str:
    """Return the host location of the pacman GPG configuration."""
    return os.path.join(_base_cache_directory(system_context, internal), 'pacman')


def _log(system_context: SystemContext, internal: bool = False) -> str:
    return os.path.join(_cache_directory(system_context, internal), 'log')


def _setup_directories(system_context: SystemContext, internal: bool) -> None:
    info('Setting up directories.')
    os.makedirs(_db_directory(system_context, internal))
    debug('DB directory created.')
    os.makedirs(_gpg_directory(system_context, internal))
    debug('GPG directory created.')
    os.makedirs(_hooks_directory(system_context, internal))
    debug('Hook directory created.')

    cache = _cache_directory(system_context, internal)
    if (not os.path.isdir(cache)):
        os.makedirs(cache)
    debug('Cache directory created.')


def _sanity_check(system_context: SystemContext) -> None:
    assert os.path.isdir(system_context.file_name('/var/lib/machines'))
    assert os.path.isdir(system_context.file_name('/var/lib/portables'))

    mode = os.stat(system_context.file_name('/dev/null')).st_mode
    assert stat.S_ISCHR(mode)


def _pacman_args(system_context: SystemContext, installed_pacman: bool = False) \
        -> typing.List[str]:
    return ['--config', _config_file(system_context, internal=installed_pacman),
            '--root', _fs_directory(system_context),
            '--cachedir', _cache_directory(system_context, internal=installed_pacman),
            '--dbpath', _db_directory(system_context, internal=installed_pacman),
            '--hookdir', _hooks_directory(system_context, internal=installed_pacman),
            '--logfile', _log(system_context, internal=installed_pacman),
            '--gpgdir', _gpg_directory(system_context, internal=installed_pacman),
            '--noconfirm']


def _pacman_keyinit(system_context: SystemContext) -> None:
    run(
        system_context.binary(Binaries.PACMAN_KEY),
        '--init', '--gpgdir', _gpg_directory(system_context),
        work_directory=system_context.ctx.systems_directory(),
        outside=True)
    run(
        system_context.binary(Binaries.PACMAN_KEY),
        '--populate', 'archlinux', '--gpgdir', _gpg_directory(system_context),
        work_directory=system_context.ctx.systems_directory(),
        outside=True)


def _run_pacman(system_context: SystemContext, *args: str, **kwargs) -> None:
    assert system_context.ctx
    _sanity_check(system_context)

    internal_pacman = (_pacman_state(system_context) == 'True')
    all_args = _pacman_args(system_context, internal_pacman) + list(args)
    run(
        system_context.binary(Binaries.PACMAN), *all_args,
        work_directory=system_context.ctx.systems_directory(),
        outside=True, timeout=600, **kwargs)


def pacstrap(system_context: SystemContext, *packages: str, config: str='') -> None:
    """Run pacstrap on host."""
    assert not _package_type(system_context)

    info('Setting up directories for pacman.')
    _setup_directories(system_context, False)

    shutil.copyfile(config, _config_file(system_context, False))

    info('Setting up pacman\'s keyring.')
    _pacman_keyinit(system_context)

    _set_pacman_state(system_context, False)
    _set_package_type(system_context)

    # Make sure pacman DB is up-to-date:
    _run_pacman(system_context, '-Sy')
    _run_pacman(system_context, '-Fy')

    pacman(system_context, *packages)


def _copy_state(system_context: SystemContext, internal_pacman: bool) -> None:
    outside = _db_directory(system_context, False)
    inside = _db_directory(system_context, True)
    debug('Copying configuration file.')
    shutil.copyfile(_config_file(system_context, not internal_pacman),
                    _config_file(system_context, internal_pacman))
    
    debug('Inside: {}, outside: {}'.format(inside, outside))
    if internal_pacman:
        shutil.rmtree(inside)
        info('Copy pacman DB into the filesystem.')
        shutil.copytree(outside, inside)
        info('Copy pacman GPG data into the filesystem.')
        shutil.rmtree(_gpg_directory(system_context, True))
        shutil.copytree(_gpg_directory(system_context, False),
                        _gpg_directory(system_context, True))
        debug('Removing pacman DB outside the filesystem.')
        shutil.rmtree(outside)
    else:
        debug('Copy pacman DB out of the filesystem.')
        shutil.copytree(inside, outside)
        debug('Removing pacman DB inside the filesystem.')
        shutil.rmtree(inside)


def _move_pacman_data(system_context: SystemContext, internal_pacman: bool) -> None:
    verbose('Pacman was installed, moving pacman data into filesystem.')
    _set_pacman_state(system_context, internal_pacman)
    _setup_directories(system_context, internal_pacman)

    info('Copying pacman state.')
    _copy_state(system_context, internal_pacman)

    # Update DB:
    if internal_pacman:
        info('Upgrading pacman DB.')
        run('/usr/bin/pacman-db-upgrade')


def pacman(system_context: SystemContext, *packages: str,
           remove: bool = False, assume_installed: str = '',
           overwrite: str = '') -> None:
    """Use pacman to install packages."""
    assert _package_type(system_context) == 'pacman'

    action: typing.List[str] = []

    if remove:
        info('Removing {}'.format(', '.join(packages)))
        action = ['-Rs',]
    else:
        info('Installing {}'.format(', '.join(packages)))
        action = ['-S', '--needed']
        if overwrite:
            action += ['--overwrite', overwrite]
        if assume_installed:
            action += ['--assume-installed', assume_installed]

    _run_pacman(system_context, *action, *packages)

    var_lib_pacman = system_context.file_name('/var/lib/pacman')
    if os.path.isdir(var_lib_pacman):
        shutil.rmtree(var_lib_pacman)

    if (_pacman_state(system_context) == 'False'
            and os.path.isfile(system_context.file_name('/usr/bin/pacman'))):
        _set_pacman_state(system_context, True)
        _move_pacman_data(system_context, not remove)


def pacman_report(system_context: SystemContext, directory: str) -> None:
    """Print pacman information into FS."""
    if _pacman_state(system_context) == 'True':
        return
        
    os.makedirs(directory)

    qi = os.path.join(directory, 'pacman-Qi.txt')
    action = ['-Qi',]
    _run_pacman(system_context, *action, stdout=qi)
    
    # Generate file list:
    qlin = os.path.join(directory, 'pacman-Ql.txt.in')
    action = ['-Ql',]
    _run_pacman(system_context, *action, stdout=qlin)
    
    # Filter prefix from file list:
    with open(qlin, 'r') as input:
        with open(os.path.join(directory, 'pacman-Ql.txt'), 'w') as output:
            for line in input:
                output.write(line.replace(system_context.fs_directory, ''))

    # Remove prefix-ed version:
    os.remove(qlin)
