# -*- coding: utf-8 -*-
"""pkg_glusterfs command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import textwrap
import typing


class PkgGlusterfsCommand(Command):
    """The pkg_glusterfs command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__('pkg_glusterfs', help_string='Setup glusterfs.',
                         file=__file__, **services)

    def validate(self, location: Location,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Validate the arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        self._execute(location, system_context, 'pacman',
                      'glusterfs', 'grep', 'python3')

        self._execute(location.next_line(),system_context,
                      'create', '/usr/lib/tmpfiles.d/mnt-gluster.conf',
                      textwrap.dedent('''\
                      d /mnt/gluster   0700 root root - -
                      d /mnt/gluster/0 0755 root root - -
                      d /mnt/gluster/1 0755 root root - -
                      d /mnt/gluster/2 0755 root root - -
                      d /mnt/gluster/4 0755 root root - -
                      '''), mode=0o644)

        self._execute(location.next_line(), system_context,
                      'mkdir', '/usr/lib/systemd/system/glusterd.service.d',
                      mode=0o755)
        self._execute(location.next_line(), system_context,
                      'create', '/usr/lib/systemd/system/glusterd.service.d/override.conf',
                      textwrap.dedent('''\
                      [Service]
                      Type=simple
                      ExecStart=
                      ExecStart=/usr/bin/glusterd -N --log-file=- --log-level INFO
                      KillMode=
                      Environment=
                      EnvironmentFile=
                      StateDirectory=glusterd
                      RunDirectory=gluster
                      '''), mode=0o644)

        self._execute(location.next_line(), system_context,
                      'systemd_harden_unit', 'glusterd.service', PrivateUsers=False)
