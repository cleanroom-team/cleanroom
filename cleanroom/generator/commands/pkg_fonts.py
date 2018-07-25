"""pkg_fonts command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.generator.command import Command
import cleanroom.generator.helper.generic.file as file

import os.path


class PkgFontsCommand(Command):
    """The pkg_fonts command."""

    def __init__(self):
        """Constructor."""
        super().__init__('pkg_fonts',
                         help='Set up some extra fonts.',
                         file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""

        system_context.execute(location.next_line(), 'pacman',
             'ttf-adobe-fonts', 'ttf-adobe-source-code-pro',
             'ttf-bitstream-vera', 'ttf-dejavu', 'ttf-freefont',
             'ttf-gentium', 'ttf-inconsolata', 'ttf-ms-fonts')

        file.symlink(system_context,
                     '../conf.avail.d/11-lcdfilter-default.conf',
                     '11-lcdfilter-default.conf',
                     base_directory='/etc/fonts/conf.d')
        file.symlink(system_context,
                     '../conf.avail.d/10-subpixel-rgb.conf',
                     '10-subpixel-rgb.conf',
                     base_directory='/etc/fonts/conf.d')

