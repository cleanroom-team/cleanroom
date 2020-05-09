"""pkg_xorg command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.helper.file import chmod, chown, copy, create_file
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import textwrap
import typing


class PkgXorgCommand(Command):
    """The pkg_xorg command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "pkg_xorg", help_string="Set up Xorg.", file=__file__, **services
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate the arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any
    ) -> None:
        """Execute command."""
        self._execute(
            location, system_context, "pacman", "xorg-server", "xorg-server-xwayland"
        )

        # Copy snippets from systems config folder:
        copy(
            system_context,
            self._config_directory(system_context) + "/*",
            "/etc/X11/xorg.conf.d",
            from_outside=True,
            recursive=True,
        )
        chown(system_context, 0, 0, "/etc/X11/xorg.conf.d/*")
        chmod(system_context, 0o644, "/etc/X11/xorg.conf.d/*")

        create_file(
            system_context,
            "/etc/X11/xinit/xinitrc.d/99-access-to-user.sh",
            textwrap.dedent(
                """\
                    #!/usr/bin/bash

                    # Allow local access for the user:
                    xhost "+local:$$USER"
                    """
            ).encode("utf-8"),
            mode=0o755,
        )

        # Install some extra fonts:
        self._execute(location.next_line(), system_context, "pkg_fonts")
