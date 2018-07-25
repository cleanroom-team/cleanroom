"""pkg_xorg command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.generator.command import Command
import cleanroom.generator.helper.generic.file as file

import os.path


class PkgXorgCommand(Command):
    """The pkg_xorg command."""

    def __init__(self):
        """Constructor."""
        super().__init__('pkg_xorg',
                         help='Set up Xorg.',
                         file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
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
