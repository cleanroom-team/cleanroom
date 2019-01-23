# -*- coding: utf-8 -*-
"""pkg_glusterfs command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.location import Location
from cleanroom.generator.command import Command
from cleanroom.generator.systemcontext import SystemContext

import typing


class PkgGlusterfsCommand(Command):
    """The pkg_glusterfs command."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__('pkg_glusterfs', help_string='Setup glusterfs.',
                         file=__file__)

    def validate_arguments(self, location: Location, *args: typing.Any, **kwargs: typing.Any) \
            -> typing.Optional[str]:
        """Validate the arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

        return None

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        system_context.execute(location.next_line(),
                               'pacman', 'glusterfs', 'grep', 'python3')

        system_context.execute(location.next_line(),
                               'create', '/usr/lib/tmpfiles.d/mnt-gluster.conf',
                               '''d /mnt/glusterfs   0700 root root - -
d /mnt/glusterfs/0 0755 root root - -
d /mnt/glusterfs/1 0755 root root - -
d /mnt/glusterfs/2 0755 root root - -
d /mnt/glusterfs/4 0755 root root - -''',
                               mode=0o644)

        system_context.execute(location.next_line(),
                               'mkdir',
                               '/usr/lib/systemd/system/glusterd.service.d',
                               mode=0o755)
        system_context.execute(location.next_line(),
                               'create',
                               '/usr/lib/systemd/system/glusterd.service.d/override.conf',
                               '''[Service]
Type=simple
ExecStart=
ExecStart=/usr/bin/glusterd -N --log-file=- --log-level INFO
KillMode=
Environment=
EnvironmentFile=
''',
                               mode=0o644)

        system_context.execute(location.next_line(),
                               'systemd_harden_unit', 'glusterd.service')
