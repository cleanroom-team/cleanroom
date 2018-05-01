# -*- coding: utf-8 -*-
"""sign_efi_binary command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.context as ctx

import os
import os.path


class SignEfiBinaryCommand(cmd.Command):
    """The sign_efi_binary command."""

    def __init__(self):
        """Constructor."""
        super().__init__('sign_efi_binary',
                         syntax='<FILE> [key=<KEY>] [cert=<CERT>]',
                         help='Sign <FILE> using <KEY> and <CERT>.',
                         file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_args_exact(location, 1, '"{}" needs a file to sign.',
                                  *args)
        self._validate_kwargs(location, ('key', 'cert'), **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        input = system_context.file_name(args[0])
        output = input + '.signed'
        key = kwargs.get('key', 'keys/efi_sign.key')
        cert = kwargs.get('cert', 'keys/efi_sign.crt')

        assert os.path.isfile(key)
        assert os.path.isfile(cert)
        assert os.path.isfile(input)
        assert not os.path.exists(output)

        system_context.run(system_context.ctx.binary(ctx.Binaries.SBSIGN),
                           '--key', key, '--cert', cert, '--output', output,
                           input, outside=True)

        system_context.execute(location, 'move', output, input)
        system_context.execute(location, 'chmod', 0o755, input)
