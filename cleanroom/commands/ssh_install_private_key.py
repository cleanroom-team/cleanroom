# -*- coding: utf-8 -*-
"""ssh_install_private_key command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.exceptions import GenerateError
from cleanroom.location import Location
from cleanroom.generator.command import Command
from cleanroom.generator.systemcontext import SystemContext
from cleanroom.generator.helper.generic.file import chmod, chown, exists, isdir, makedirs
from cleanroom.generator.helper.generic.user import user_data
from cleanroom.printer import debug, trace

import os.path
import typing


class SshInstallPrivateKeyCommand(Command):
    """The ssh_install_private_key command."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__('ssh_install_private_key', syntax='<USER> <KEYFILE>',
                         help_string='Install <KEYFILE> as private key for <USER>.',
                         file=__file__)

    def validate_arguments(self, location: Location, *args: typing.Any, **kwargs: typing.Any) \
            -> typing.Optional[str]:
        """Validate the arguments."""
        self._validate_arguments_exact(location, 2,
                                       '"{}" needs a user and a keyfile.',
                                       *args, **kwargs)

        return None

    def _check_or_create_directory(self, location: Location, system_context: SystemContext,
                                   directory: str, **kwargs: typing.Any) -> None:
        if not exists(system_context, directory):
            makedirs(system_context, directory, **kwargs)
            return
        if not isdir(system_context, directory):
            raise GenerateError('"{}" needs directory "{}", but that exists and is not a directory.'
                                .format(self.name(), directory),
                                location=location)

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        user_name = args[0]
        key_file = args[1]

        user = user_data(system_context, user_name)
        if user is None:
            raise GenerateError('"{}" could not find user "{}".'.format(self.name(), user_name),
                                location=location)

        debug('Installing "{}" to user "{}" ({}).'.format(key_file, user_name, user.home))

        self._check_or_create_directory(location, system_context, user.home,
                                        mode=0o750, user=user.uid, group=user.gid)
        ssh_directory = os.path.join(user.home, '.ssh')
        self._check_or_create_directory(location, system_context,
                                        ssh_directory,
                                        mode=0o600, user=user.uid, group=user.gid)

        installed_key_file = os.path.join(ssh_directory, os.path.basename(key_file))

        system_context.execute(location.next_line(), 'copy', key_file,
                               installed_key_file, from_outside=True)
        trace('Copied key.')
        chown(system_context, user.uid, user.gid, installed_key_file)
        trace('Ownership adjusted.')
        chmod(system_context, 0o600, installed_key_file)
        trace('Mode adjusted.')
