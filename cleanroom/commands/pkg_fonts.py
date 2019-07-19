"""pkg_fonts command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.helper.file import symlink
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import typing


class PkgFontsCommand(Command):
    """The pkg_fonts command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__('pkg_fonts',
                         help_string='Set up some extra fonts.',
                         file=__file__, **services)

    def validate(self, location: Location,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Validate the arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        self._execute(location, system_context, 'pacman',
                      'adobe-source-code-pro-fonts',
                      'ttf-bitstream-vera', 'ttf-dejavu',
                      'ttf-gentium', 'ttf-inconsolata', 'ttf-ms-fonts',
                      'noto-fonts', 'noto-fonts-cjk', 'noto-fonts-emoji',
                      'noto-fonts-extra', 'ttf-roboto')

        symlink(system_context,
                '../conf.avail.d/11-lcdfilter-default.conf',
                '11-lcdfilter-default.conf',
                work_directory='/etc/fonts/conf.d')
        symlink(system_context,
                '../conf.avail.d/10-subpixel-rgb.conf',
                '10-subpixel-rgb.conf',
                work_directory='/etc/fonts/conf.d')
