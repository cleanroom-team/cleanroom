# -*- coding: utf-8 -*-
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
        super().__init__('useradd',
                         syntax='<NAME> [comment=<COMMENT>] [home=<HOMEDIR>] '
                         '[gid=<GID>] [uid=<UID>] [groups=<GROUP1>,<GROUP2>] '
                         '[lock=False] [password=<CRYPTED_PASSWORD>] '
                         '[shell=<PATH>] [expire=<EXPIRE_DATE>]',
                         help='Modify an existing user.')

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        if len(args) != 1:
            raise ex.ParseError('useradd needs a username.',
                                location=location)
        if len(kwargs) == 0:
            raise ex.ParseError('useradd needs keyword arguments',
                                location=location)

        lock = kwargs.get('lock', None)
        if lock not in (True, None, False):
            raise ex.ParseError('"lock" must be either True, False or None.',
                                location=location)

        return None

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        user.useradd(system_context, args[0], **kwargs)
