"""usermod command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.exceptions as ex


class UsermodCommand(cmd.Command):
    """The usermod command."""

    def __init__(self):
        """Constructor."""
        super().__init__('usermod <NAME> [comment=<COMMENT>] [home=<HOMEDIR>] '
                         '[gid=<GID>] [uid=<UID>] [rename=<NEW_NAME>] '
                         '[groups=<GROUP1>,<GROUP2>] [lock=False] '
                         '[password=<CRYPTED_PASSWORD>] [shell=<PATH>] '
                         '[expire=<EXPIRE_DATE>], [append=False]',
                         'Modify an existing user.')

    def validate_arguments(self, run_context, *args, **kwargs):
        """Validate the arguments."""
        if len(args) != 1:
            raise ex.ParseError('usermod needs a username.',
                                run_context=run_context)
        if len(kwargs) == 0:
            raise ex.ParseError('usermod needs keyword arguments',
                                run_context=run_context)

        lock = kwargs.get('lock', None)
        if lock not in (True, None, False):
            raise ex.ParseError('"lock" must be either True, False or None.',
                                run_context=run_context)

        append = kwargs.get('append', False)
        if append not in (True, False):
            raise ex.ParseError('"append" must have either True or False as '
                                'value.',
                                run_context=run_context)

        if append and kwargs.get('groups', '') == '':
            raise ex.ParseError('"append" needs "groups" to be set, too.',
                                run_context=run_context)

        return None

    def __call__(self, run_context, *args, **kwargs):
        """Execute command."""
        user = args[0]
        command = ['/usr/bin/usermod', user]

        comment = kwargs.get('comment', '')
        if comment:
            command += ['--comment', comment]

        home = kwargs.get('home', '')
        if home:
            command += ['--home', home]

        gid = kwargs.get('gid', '')
        if gid:
            command += ['--gid', gid]

        uid = kwargs.get('uid', '')
        if uid:
            command += ['--uid', uid]

        lock = kwargs.get('lock', None)
        if lock is not None:
            if lock:
                command.append('--lock')
            else:
                command.append('--unlock')

        shell = kwargs.get('shell', '')
        if shell:
            command += ['--shell', shell]

        rename = kwargs.get('rename', '')
        if rename:
            command += ['--login', rename]

        append = kwargs.get('append', False)
        if append:
            command.append('--append')

        groups = kwargs.get('groups', '')
        if groups:
            command += ['--groups', groups]

        passwd = kwargs.get('password', '')
        if passwd:
            command += ['--password', passwd]

        expire = kwargs.get('expire', '')
        if expire:
            if expire == 'None':
                command.append('--expire-date')
            else:
                command += ['--expire-date', expire]

        run_context.run(*command)
