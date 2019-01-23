"""pkg_xorg command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.location import Location
from cleanroom.generator.command import Command
import cleanroom.generator.helper.generic.file as file
from cleanroom.generator.systemcontext import SystemContext

import os.path
import typing


class PkgXorgCommand(Command):
    """The pkg_xorg command."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__('pkg_xorg',
                         help_string='Set up Xorg.',
                         file=__file__)

    def validate_arguments(self, location: Location, *args: typing.Any, **kwargs: typing.Any) \
            -> typing.Optional[str]:
        """Validate the arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

        return None

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""

        system_context.execute(location.next_line(), 'pacman',
                               'xorg-server', 'xorg-server-xwayland')

        # Copy snippets from systems config folder:
        file.copy(system_context,
                  os.path.join(self.config_directory(system_context)) + '/*',
                  '/etc/X11/xorg.conf.d', from_outside=True, recursive=True)
        file.chown(system_context, 0, 0, '/etc/X11/xorg.conf.d/*')
        file.chmod(system_context, 0o644, '/etc/X11/xorg.conf.d/*')

        file.create_file(system_context,
                         '/etc/X11/xinit/xinitrc.d/99-access-to-user.sh',
                         '''#!/usr/bin/bash

# Allow local access for the user:
xhost "+local:$$USER"
'''.encode('utf-8'), mode=0o755)

        # Install some extra fonts:
        system_context.execute(location.next_line(), 'pkg_fonts')
