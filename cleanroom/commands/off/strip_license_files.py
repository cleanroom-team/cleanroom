# -*- coding: utf-8 -*-
"""strip_license_files command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.location import (Location,)
from cleanroom.generator.command import (Command,)
from cleanroom.generator.systemcontext import (SystemContext,)

import typing


class StripLicenseFilesCommand(Command):
    """The strip_license_files Command."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__('strip_license_files',
                         help_string='Strip away license files.', file=__file__)

    def validate_arguments(self, location: Location, *args: typing.Any, **kwargs: typing.Any) \
            -> typing.Optional[str]:
        """Validate arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

        return None

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        location.set_description('Strip license files')
        system_context.add_hook(location, 'export',
                                'remove',  '/usr/share/licenses/*',
                                recursive=True, force=True)
