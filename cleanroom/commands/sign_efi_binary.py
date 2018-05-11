# -*- coding: utf-8 -*-
"""sign_efi_binary command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.context as ctx
import cleanroom.printer as printer

import os
import os.path
import shutil


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
        input = args[0]
        output = input + '.signed'
        key = os.path.join(system_context.ctx.systems_directory(),
                           kwargs.get('key', 'config/efi/sign.key'))
        cert = os.path.join(system_context.ctx.systems_directory(),
                            kwargs.get('cert', 'config/efi/sign.crt'))

        printer.trace('key   : {}.'.format(key))
        assert os.path.isfile(key)
        printer.trace('cert  : {}.'.format(cert))
        assert os.path.isfile(cert)
        printer.trace('input : {}.'.format(input))
        assert os.path.isfile(input)
        printer.trace('output: {}.'.format(output))
        assert not os.path.exists(output)

        system_context.run(system_context.ctx.binary(ctx.Binaries.SBSIGN),
                           '--key', key, '--cert', cert, '--output', output,
                           input, outside=True)

        os.remove(input)
        shutil.move(output, input)
