# -*- coding: utf-8 -*-
"""sshd_install_knownhosts command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.exceptions import GenerateError
from cleanroom.location import Location
from cleanroom.generator.command import Command
from cleanroom.generator.helper.generic.file import isdir
from cleanroom.generator.systemcontext import SystemContext

import typing


class SshdInstallKnownhostsCommand(Command):
    """The sshd_install_knownhosts command."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__('sshd_install_knownhosts',
                         help_string='Install system wide knownhosts file.',
                         file=__file__)

    def validate_arguments(self, location: Location, *args: typing.Any, **kwargs: typing.Any) \
            -> typing.Optional[str]:
        """Validate the arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

        return None

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        # FIXME: Implement this!
        # self._validate_key_directory(location, key_directory)
        if not isdir(system_context, '/etc/ssh'):
            raise GenerateError('"{}": No /etc/ssh directory found in system.'
                                .format(self.name()), location=location)
