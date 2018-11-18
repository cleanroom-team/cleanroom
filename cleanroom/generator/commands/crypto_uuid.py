# -*- coding: utf-8 -*-
"""crypto_uuid command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.generator.command import Command
from cleanroom.generator.systemcontext import SystemContext


class CryptoUuidCommand(Command):
    """The crypto_uuid command."""

    def __init__(self):
        """Constructor."""
        super().__init__('crypto_uuid', syntax='<UUID> <NAME>',
                         help='Set the UUID of the crypto partition and the NAME to bind to it.',
                         file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_arguments_exact(location, 2,
                                       '"{}" needs a UUID and NAME to set up.', *args)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        uuid = args[0]
        cmdline = system_context.substitution('KERNEL_CMDLINE', '')

        if 'rd.luks.name=' in cmdline:
            raise GenerateError('rd.luks.name already set.', location=location)

        if cmdline:
            cmdline += ' '
        cmdline += 'rd.luks.name={}={} rd.luks.options=discard'.format(uuid, args[1])

        system_context.set_substitution('KERNEL_CMDLINE', cmdline)
