"""useradd command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.exceptions as ex
import cleanroom.helper.generic.user as user


class UseraddCommand(cmd.Command):
    """The useradd command."""

    def __init__(self):
        """Constructor."""
        super().__init__('useradd <NAME> [comment=<COMMENT>] [home=<HOMEDIR>] '
                         '[gid=<GID>] [uid=<UID>] [groups=<GROUP1>,<GROUP2>] '
                         '[lock=False] [password=<CRYPTED_PASSWORD>] '
                         '[shell=<PATH>] [expire=<EXPIRE_DATE>]',
                         'Modify an existing user.')

    def validate_arguments(self, file_name, line_number, *args, **kwargs):
        """Validate the arguments."""
        if len(args) != 1:
            raise ex.ParseError('useradd needs a username.',
                                file_name=file_name, line_number=line_number)
        if len(kwargs) == 0:
            raise ex.ParseError('useradd needs keyword arguments',
                                file_name=file_name, line_number=line_number)

        lock = kwargs.get('lock', None)
        if lock not in (True, None, False):
            raise ex.ParseError('"lock" must be either True, False or None.',
                                file_name=file_name, line_number=line_number)

        return None

    def __call__(self, file_name, line_number, run_context, *args, **kwargs):
        """Execute command."""
        user.useradd(run_context, args[0], **kwargs)
