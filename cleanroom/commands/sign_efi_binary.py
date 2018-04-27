# -*- coding: utf-8 -*-
"""sign_efi_binary command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.context as ctx
import cleanroom.helper.generic.file as file

import os


class SignEfiBinaryCommand(cmd.Command):
    """The sign_efi_binary command."""

    def __init__(self):
        """Constructor."""
        super().__init__('sign_efi_binary',
                         syntax='<FILE> [key=<KEY>] [cert=<CERT>]',
                         help='Sign <FILE> using <KEY> and <CERT>.')

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_args_exact(location, 1, '"{}" needs a file to sign.',
                                  *args)
        return self._validate_kwargs(location, ('key', 'cert'), **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        input = args[0]
        output = file + '.signed'
        key = kwargs.get('key', 'keys/efi_sign.key')
        cert = kwargs.get('cert', 'keys/efi_sign.crt')

        assert os.exists(key)
        assert os.exists(cert)
        assert os.exists(input)
        assert not os.exists(output)

        system_context.run(location,
                           system_context.ctx.binary(ctx.Binaries.SBSIGN),
                           '--key', key, '--cert', cert, '--output', output,
                           input)

        os.move(output, input)
        os.chmod(0o755, input)
