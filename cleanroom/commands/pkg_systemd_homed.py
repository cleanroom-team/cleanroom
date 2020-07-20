# -*- coding: utf-8 -*-
"""pkg_systemd_homed command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.exceptions import GenerateError
from cleanroom.helper.file import chmod, chown, create_file, makedirs
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import textwrap
import typing


class PkgSystemdHomedCommand(Command):
    """The pkg_systemd_homed command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "pkg_systemd_homed",
            syntax="<PRIVATE_KEY_DATA> <PUBLIC_KEY_DATA>",
            help_string="Setup systemd-homed.",
            file=__file__,
            **services
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate the arguments."""
        self._validate_args_exact(
            location,
            2,
            '"{}" requires the private key data ' "and the public key data",
            *args
        )
        self._validate_kwargs(location, (), **kwargs)

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any
    ) -> None:
        """Execute command."""

        private_key = args[0]
        public_key = args[1]

        location.set_description("Validate keys")
        if not "BEGIN PRIVATE KEY" in private_key:
            raise GenerateError(
                "Private key blob is not a private key.", location=location
            )

        if not "BEGIN PUBLIC KEY" in public_key:
            raise GenerateError(
                "Public key blob is not a public key.", location=location
            )

        # enable the daemon (actually set up socket activation)
        location.set_description("Enableing homed service")
        self._execute(
            location.next_line(),
            system_context,
            "systemd_enable",
            "systemd-homed.service",
        )

        # Install keys into /usr:
        location.set_description("Setup keys")
        makedirs(system_context, "/usr/share/factory/var/lib/systemd/home", mode=0o700)
        create_file(
            system_context,
            "/usr/share/factory/var/lib/systemd/home/local.private",
            private_key.encode("utf-8"),
            mode=0o600,
        )
        create_file(
            system_context,
            "/usr/share/factory/var/lib/systemd/home/local.public",
            public_key.encode("utf-8"),
            mode=0o600,
        )
        chmod(system_context, 0o600, "/usr/share/factory/var/lib/systemd/home/*")
        chown(system_context, 0, 0, "/usr/share/factory/var/lib/systemd/home/*")

        # Set up copying of keys to var:
        create_file(
            system_context,
            "/usr/lib/tmpfiles.d/systemd-homed.conf",
            textwrap.dedent(
                """\
                    C /var/lib/systemd/home - - - - 
                    """
            ).encode("utf-8"),
            mode=0o644,
        )

        # Fix up pam:
        location.set_description("Setting up PAM for homed")
        create_file(
            system_context,
            "/etc/pam.d/nss-auth",
            textwrap.dedent(
                """\
                #%PAM-1.0

                auth     sufficient pam_unix.so try_first_pass nullok
                auth     sufficient pam_systemd_home.so
                auth     required   pam_deny.so

                account  sufficient pam_unix.so
                account  sufficient pam_systemd_home.so
                account  required   pam_deny.so

                password sufficient pam_unix.so try_first_pass nullok sha512 shadow
                password sufficient pam_systemd_home.so
                password required   pam_deny.so
                """
            ).encode("utf-8"),
            mode=0o644,
        )
        create_file(
            system_context,
            "/etc/pam.d/system-auth",
            textwrap.dedent(
                """\
                #%PAM-1.0

                auth      substack   nss-auth
                auth      optional   pam_permit.so
                auth      required   pam_env.so

                account   substack   nss-auth
                account   optional   pam_permit.so
                account   required   pam_time.so

                password  substack   nss-auth
                password  optional   pam_permit.so

                session   required  pam_limits.so
                session   optional  pam_systemd_home.so
                session   required  pam_unix.so
                session   optional  pam_permit.so
                """
            ).encode("utf-8"),
            mode=0o644,
            force=True,
        )
