"""pacstrap command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.context as context
import cleanroom.exceptions as ex
import cleanroom.helper.archlinux.pacman as pacman
import cleanroom.helper.generic.file as file
import cleanroom.parser as parser


class PacstrapCommand(cmd.Command):
    """The pacstrap command."""

    def __init__(self):
        """Constructor."""
        super().__init__('pacstrap <PACKAGES> config=<CONFIG_FILE>',
                         'Run pacstrap to install <PACKAGES>.\n'
                         'Hooks: Will runs _setup hooks after pacstrapping.')

    def validate_arguments(self, file_name, line_number, *args, **kwargs):
        """Validate the arguments."""
        if len(args) < 1:
            raise ex.ParseError('pacstrap needs at least '
                                'one package or group to install.',
                                file_name=file_name, line_number=line_number)

        if 'config' not in kwargs:
            raise ex.ParseError('pacstrap needs a "config" keyword argument.',
                                file_name=file_name, line_number=line_number)
        return None

    def __call__(self, file_name, line_number, run_context, *args, **kwargs):
        """Execute command."""
        assert(run_context.flags.get('package_type', None) is None)

        pac_object = pacman.Pacman(run_context)

        pacstrap_config = kwargs['config']
        self._prepare_keyring(run_context, pac_object, pacstrap_config)

        pac_object.pacstrap(pacstrap_config, args)

        # Install pacman.conf:
        file.copy(run_context, pacstrap_config, '/etc/pacman.conf',
                  from_outside=True)

        # Make sure DB is up-to-date:
        run_context.run('/usr/bin/pacman-db-upgrade')

        run_context.set_substitution('PACKAGE_TYPE', 'pacman')

        file.move(run_context, '/opt', '/usr')
        file.symlink(run_context, 'usr/opt', 'opt', base_directory='/')

        run_context.run_hooks('_setup')

        # Make sure pacman DB is up-to-date:
        run_context.run('/usr/bin/pacman', '-Sy')
        run_context.run('/usr/bin/pacman', '-Fy')

    def _prepare_keyring(self, run_context, pac_object, pacstrap_config):
        # Make sure important pacman directories exist:
        file.makedirs(run_context, pac_object.host_gpg_directory())
        pacman_key = run_context.ctx.binary(context.Binaries.PACMAN_KEY)
        run_context.run(pacman_key,
                        '--config', pacstrap_config,
                        '--gpgdir', pac_object.host_gpg_directory(),
                        '--init',
                        exit_code=0, outside=True,
                        work_directory=run_context.ctx.systems_directory())
        run_context.run(pacman_key,
                        '--config', pacstrap_config,
                        '--gpgdir', pac_object.host_gpg_directory(),
                        '--populate', 'archlinux',
                        exit_code=0, outside=True,
                        work_directory=run_context.ctx.systems_directory())

        gpgdir = pac_object.target_gpg_directory()
        packageFiles = pac_object.target_cache_directory() + '/pkg/*'

        run_context.add_hook('_teardown',
                             parser.Parser.create_execute_object(
                                 '<pacstrap command>', 1,
                                 'remove',
                                 gpgdir + '/S.*',
                                 gpgdir + '/pubring.gpg~',
                                 '/var/log/pacman.log',
                                 packageFiles,
                                 force=True, recursive=True,
                                 message='cleanup pacman-key files'))

        run_context.add_hook('export',
                             parser.Parser.create_execute_object(
                                 '<pacstrap command>', 2,
                                 'remove',
                                 gpgdir + '/secring.gpg*',
                                 force=True,
                                 message='Remove pacman secret keyring'))
