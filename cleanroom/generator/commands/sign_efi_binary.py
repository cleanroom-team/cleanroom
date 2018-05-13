# -*- coding: utf-8 -*-
"""sign_efi_binary command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.generator.command import Command
from cleanroom.generator.context import Binaries

from cleanroom.printer import verbose

import os
import os.path
import shutil


class SignEfiBinaryCommand(Command):
    """The sign_efi_binary command."""

    def __init__(self):
        """Constructor."""
        super().__init__('sign_efi_binary',
                         syntax='<FILE> [key=<KEY>] [cert=<CERT>] [outside=False]',
                         help='Sign <FILE> using <KEY> and <CERT>.',
                         file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_args_exact(location, 1, '"{}" needs a file to sign.',
                                  *args)
        self._validate_kwargs(location, ('key', 'cert', 'outside'), **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        to_sign = args[0]
        if not kwargs.get('outside', False):
            to_sign = system_context.file_name(to_sign)
        key = os.path.join(system_context.ctx.systems_directory(),
                           kwargs.get('key', 'config/efi/sign.key'))
        cert = os.path.join(system_context.ctx.systems_directory(),
                            kwargs.get('cert', 'config/efi/sign.crt'))

        verbose('Signing EFI binary {} using key {} and cert {}.'
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
