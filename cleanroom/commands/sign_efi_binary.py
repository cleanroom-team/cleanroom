# -*- coding: utf-8 -*-
"""sign_efi_binary command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.binarymanager import Binaries
from cleanroom.command import Command
from cleanroom.helper.run import run
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext
from cleanroom.printer import info, trace

import os
import typing


class SignEfiBinaryCommand(Command):
    """The sign_efi_binary command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "sign_efi_binary",
            syntax="<FILE> [key=<KEY>] [cert=<CERT>] [outside=False] "
            "[keep_unsigned=False]",
            help_string="Sign <FILE> using <KEY> and <CERT>.",
            file=__file__,
            **services,
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate the arguments."""
        self._validate_args_exact(location, 1, '"{}" needs a file to sign.', *args)
        self._validate_kwargs(
            location, ("key", "cert", "outside", "keep_unsigned"), **kwargs
        )

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> None:
        """Execute command."""
        to_sign = args[0]
        keep_unsigned = kwargs.get("keep_unsigned", False)
        if not kwargs.get("outside", False):
            to_sign = system_context.file_name(to_sign)
        systems_directory = system_context.systems_definition_directory
        key = os.path.join(systems_directory, kwargs.get("key", "config/efi/sign.key"))
        cert = os.path.join(
            systems_directory, kwargs.get("cert", "config/efi/sign.crt")
        )

        info(
            f"Signing EFI binary {to_sign} using key {key} and cert {cert} (keep unsigned: {keep_unsigned})."
        )

        signed = to_sign + ".signed"

        assert os.path.isfile(key)
        assert os.path.isfile(cert)
        assert os.path.isfile(to_sign)
        assert not os.path.exists(signed)

        run(
            self._binary(Binaries.SBSIGN),
            "--key",
            key,
            "--cert",
            cert,
            "--output",
            signed,
            to_sign,
        )

        if keep_unsigned:
            assert os.path.isfile(to_sign)
            assert os.path.isfile(signed)
        else:
            trace(f"Moving {signed} to {to_sign}.")
            os.remove(to_sign)
            os.rename(signed, to_sign)

            assert os.path.isfile(to_sign)
