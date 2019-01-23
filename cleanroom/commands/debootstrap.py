# -*- coding: utf-8 -*-
"""debootstrap command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.exceptions import ParseError
from cleanroom.location import Location
from cleanroom.generator.command import Command
from cleanroom.generator.helper.debian.apt import debootstrap
from cleanroom.generator.systemcontext import SystemContext

import typing


class DebootstrapCommand(Command):
    """The debootstrap command."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__('debootstrap', syntax='suite=<SUITE> '
                         'mirror=<MIRROR> [variant=<VARIANT>] '
                         '[include=<INCLUDE>] [exclude=<EXCLUDE>]',
                         help_string='Run debootstrap to install a <SUITE> in <VARIANT>'
                         'from <MIRROR>. Include <INCLUDE> and exclude <EXCLUDE> '
                         'packages.',
                         file=__file__)

    def validate_arguments(self, location: Location,
                           *args: str, **kwargs: typing.Any) -> typing.Optional[str]:
        """Validate the arguments."""
        self._validate_no_args(location, *args)
        self._validate_kwargs(location,
                              ('suite', 'mirror', 'variant', 'include', 'exclude',),
                              **kwargs)
        self._require_kwargs(location, ('suite', 'mirror',), **kwargs)

        if not kwargs.get('suite', ''):
            raise ParseError('"{}" needs a suite.'
                             .format(self.name()), location=location)

        return None

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: str, **kwargs: typing.Any) -> None:
        """Execute command."""
        debootstrap(system_context, suite=kwargs.get('suite', ''),
                    target=system_context.fs_directory(),
                    mirror=kwargs.get('mirror', ''),
                    variant=kwargs.get('variant', None),
                    include=kwargs.get('include', None),
                    exclude=kwargs.get('exclude', None))

        location.set_description('Move systemd files into /usr')
        system_context.add_hook(location, '_teardown', 'systemd_cleanup')
