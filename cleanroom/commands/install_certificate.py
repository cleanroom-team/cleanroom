# -*- coding: utf-8 -*-
"""install_certificate command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.location import Location
from cleanroom.generator.command import Command
from cleanroom.generator.systemcontext import SystemContext

import os
import os.path
import stat
import typing


class InstallCertificatesCommand(Command):
    """The install_certificate command."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__('install_certificate', syntax='<CA_CERT>+',
                         help_string='Install CA certificates.', file=__file__)

    def validate_arguments(self, location: Location, *args: typing.Any, **kwargs: typing.Any) \
            -> typing.Optional[str]:
        """Validate the arguments."""
        self._validate_arguments_at_least(location, 1,
                                          '"{}" needs at least one '
                                          'ca certificate to add',
                                          *args, **kwargs)

        return None

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        assert system_context.ctx
        for f in args:
            source = f if os.path.isabs(f) \
                else os.path.join(system_context.ctx.systems_directory() or '', f)
            dest = os.path.join('/etc/ca-certificates/trust-source/anchors',
                                os.path.basename(f))
            system_context.execute(location.next_line(), 'copy',
                                   source, dest, from_outside=True)
            system_context.execute(location.next_line(), 'chmod',
                                   stat.S_IRUSR | stat.S_IWUSR
                                   | stat.S_IRGRP | stat.S_IROTH, dest)

        system_context.run('/usr/bin/trust', 'extract-compat')
