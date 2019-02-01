# -*- coding: utf-8 -*-
"""install_certificate command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.binarymanager import Binaries
from cleanroom.command import Command
from cleanroom.helper.run import run
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import os
import os.path
import stat
import typing


class InstallCertificatesCommand(Command):
    """The install_certificate command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__('install_certificate', syntax='<CA_CERT>+',
                         help_string='Install CA certificates.',
                         file=__file__, **services)

    def validate(self, location: Location,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Validate the arguments."""
        self._validate_arguments_at_least(location, 1,
                                          '"{}" needs at least one '
                                          'ca certificate to add',
                                          *args, **kwargs)

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        for f in args:
            source = f if os.path.isabs(f) \
                else os.path.join(system_context.systems_definition_directory or '', f)
            dest = os.path.join('/etc/ca-certificates/trust-source/anchors',
                                os.path.basename(f))
            self._execute(location.next_line(), system_context,
                          'copy', source, dest, from_outside=True)
            self._execute(location.next_line(), system_context,
                          'chmod', stat.S_IRUSR | stat.S_IWUSR
                                   | stat.S_IRGRP | stat.S_IROTH,
                          dest)

        run('/usr/bin/trust', 'extract-compat',
            chroot=system_context.fs_directory,
            chroot_helper=self._binary(Binaries.CHROOT_HELPER))
