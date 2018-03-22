"""pacstrap command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.context as context
import cleanroom.exceptions as ex
import cleanroom.helper.archlinux.pacman as arch
import cleanroom.helper.generic.file as file

import os.path


class PacstrapCommand(cmd.Command):
    """The pacstrap command."""

    def __init__(self):
        """Constructor."""
        super().__init__('pacstrap <PACKAGES> config=<CONFIG_FILE>',
                         'Run pacstrap to install <PACKAGES>.\n'
                         'Hooks: Will runs _setup hooks after pacstrapping.')

    def validate_arguments(self, run_context, *args, **kwargs):
        """Validate the arguments."""
        if len(args) < 1:
            raise ex.ParseError('pacstrap needs at least '
                                'one package or group to install.',
                                run_context=run_context)

        if 'config' not in kwargs:
            raise ex.ParseError('pacstrap needs a "config" keyword argument.',
                                run_context=run_context)
        return None

    def __call__(self, run_context, *args, **kwargs):
        """Execute command."""
        pacstrap_config = kwargs['config']
        self._prepare_keyring(run_context, pacstrap_config)

        arch.pacstrap(run_context, pacstrap_config, *args)

        # Install pacman.conf:
        run_context.execute('copy',
                            os.path.join(run_context.ctx.systems_directory(),
                                         pacstrap_config),
                            '/etc/pacman.conf',
                            from_outside=True)

        # Make sure DB is up-to-date:
        run_context.run('/usr/bin/pacman-db-upgrade')

        run_context.execute('remove', '/var/lib/pacman',
                            recursive=True, force=True)

        run_context.set_substitution('PACKAGE_TYPE', 'pacman')

        run_context.execute('move', '/opt', '/usr')
        run_context.execute('symlink', 'usr/opt', 'opt', base_directory='/')

        run_context.run_hooks('_setup')

        # Make sure pacman DB is up-to-date:
        run_context.run('/usr/bin/pacman', '-Sy')
        run_context.run('/usr/bin/pacman', '-Fy')

    def _prepare_keyring(self, run_context, pacstrap_config):
        # Make sure important pacman directories exist:
        file.makedirs(run_context, arch.host_gpg_directory(run_context))
        pacman_key = run_context.ctx.binary(context.Binaries.PACMAN_KEY)
        run_context.run(pacman_key,
                        '--config', pacstrap_config,
                        '--gpgdir', arch.host_gpg_directory(run_context),
                        '--init',
                        exit_code=0, outside=True,
                        work_directory=run_context.ctx.systems_directory())
        run_context.run(pacman_key,
                        '--config', pacstrap_config,
                        '--gpgdir', arch.host_gpg_directory(run_context),
                        '--populate', 'archlinux',
                        exit_code=0, outside=True,
                        work_directory=run_context.ctx.systems_directory())

        gpgdir = arch.target_gpg_directory()
        packageFiles = arch.target_cache_directory() + '/pkg/*'

        run_context.add_hook('_teardown', 'remove',
                             gpgdir + '/S.*', gpgdir + '/pubring.gpg~',
                             '/var/log/pacman.log', packageFiles,
                             recursive=True, force=True,
                             message='cleanup pacman-key files')
        run_context.add_hook('_teardown', 'systemd_cleanup',
                             message='Move systemd files into /usr')
        run_context.add_hook('export', 'remove', gpgdir + '/secring.gpg*',
                             force=True,
                             message='Remove pacman secret keyring')
