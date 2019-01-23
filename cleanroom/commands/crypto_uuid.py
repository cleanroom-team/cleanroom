# -*- coding: utf-8 -*-
"""crypto_uuid command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.exceptions import GenerateError
from cleanroom.location import Location
from cleanroom.generator.command import Command
from cleanroom.generator.systemcontext import SystemContext

import typing


class CryptoUuidCommand(Command):
    """The crypto_uuid command."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__('crypto_uuid', syntax='<UUID> <NAME>',
                         help_string='Set the UUID of the crypto partition and the NAME to bind to it.',
                         file=__file__)

    def validate_arguments(self, location: Location, *args: typing.Any, **kwargs: typing.Any) \
            -> typing.Optional[str]:
        """Validate the arguments."""
        self._validate_arguments_exact(location, 2,
                                       '"{}" needs a UUID and NAME to set up.', *args)

        return None

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        uuid = args[0]
        cmdline = system_context.substitution('KERNEL_CMDLINE', '')

        if 'rd.luks.name=' in cmdline:
            raise GenerateError('rd.luks.name already set.', location=location)

        if cmdline:
            cmdline += ' '
        cmdline += 'rd.luks.name={}={} rd.luks.options=discard'.format(uuid, args[1])

        system_context.set_substitution('KERNEL_CMDLINE', cmdline)
