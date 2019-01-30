"""pkg_fonts command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.location import Location
from cleanroom.generator.command import Command
import cleanroom.generator.helper.generic.file as file
from cleanroom.generator.systemcontext import SystemContext

import typing


class PkgFontsCommand(Command):
    """The pkg_fonts command."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__('pkg_fonts',
                         help_string='Set up some extra fonts.',
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
                               'adobe-source-code-pro-fonts',
                               'ttf-bitstream-vera', 'ttf-dejavu', 'ttf-freefont',
                               'ttf-gentium', 'ttf-inconsolata', 'ttf-ms-fonts')

        file.symlink(system_context,
                     '../conf.avail.d/11-lcdfilter-default.conf',
                     '11-lcdfilter-default.conf',
                     work_directory='/etc/fonts/conf.d')
        file.symlink(system_context,
                     '../conf.avail.d/10-subpixel-rgb.conf',
                     '10-subpixel-rgb.conf',
                     work_directory='/etc/fonts/conf.d')
