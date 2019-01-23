# -*- coding: utf-8 -*-
"""sign_efi_binary command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.location import Location
from cleanroom.generator.command import Command
from cleanroom.generator.context import Binaries
from cleanroom.generator.systemcontext import SystemContext
from cleanroom.printer import info

import os
import os.path
import shutil
import typing


class SignEfiBinaryCommand(Command):
    """The sign_efi_binary command."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__('sign_efi_binary',
                         syntax='<FILE> [key=<KEY>] [cert=<CERT>] [outside=False]',
                         help_string='Sign <FILE> using <KEY> and <CERT>.',
                         file=__file__)

    def validate_arguments(self, location: Location, *args: typing.Any, **kwargs: typing.Any) \
            -> typing.Optional[str]:
        """Validate the arguments."""
        self._validate_args_exact(location, 1, '"{}" needs a file to sign.',
                                  *args)
        self._validate_kwargs(location, ('key', 'cert', 'outside'), **kwargs)

        return None

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        to_sign = args[0]
        if not kwargs.get('outside', False):
            to_sign = system_context.file_name(to_sign)
        assert system_context.ctx
        systems_directory = system_context.ctx.systems_directory()
        assert systems_directory
        key = os.path.join(systems_directory, kwargs.get('key', 'config/efi/sign.key'))
        cert = os.path.join(systems_directory, kwargs.get('cert', 'config/efi/sign.crt'))

        info('Signing EFI binary {} using key {} and cert {}.'
             .format(input, key, cert))
        output = to_sign + '.signed'
        assert os.path.isfile(key)
        assert os.path.isfile(cert)
        assert os.path.isfile(to_sign)
        assert not os.path.exists(output)

        system_context.run(system_context.binary(Binaries.SBSIGN),
                           '--key', key, '--cert', cert, '--output', output,
                           to_sign, outside=True)

        os.remove(to_sign)
        shutil.move(output, to_sign)
