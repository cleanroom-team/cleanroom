# -*- coding: utf-8 -*-
"""pkg_glusterfs command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.generator.command import Command


class PkgGlusterfsCommand(Command):
    """The pkg_glusterfs command."""

    def __init__(self):
        """Constructor."""
        super().__init__('pkg_glusterfs', help='Setup glusterfs.',
                         file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        system_context.execute(location.next_line(),
                               'pacman', 'glusterfs', 'grep', 'python3')

        system_context.execute(location.next_line(),
                               'create', '/usr/lib/tmpfiles.d/mnt-gluster.conf',
                               '''d /mnt/gluster   0700 root root - -
d /mnt/gluster/0 0755 root root - -
d /mnt/gluster/1 0755 root root - -
d /mnt/gluster/2 0755 root root - -
d /mnt/gluster/4 0755 root root - -''',
                               mode=0o644)

        system_context.execute(location.next_line(),
                               'create',
                               '/usr/lib/systemd/system/glusterd.service.d/override.conf',
                               '''[Service]
Type=simple
ExecStart=/usr/bin/glusterd -N --log-file=- --log-level INFO
KillMode=
Environment=
EnvironmentFile=
''',
                               mode=0o644)

        system_context.execute(location.next_line(),
                               'create',
                               '/usr/lib/systemd/system/glusterd.service.d/security.conf',
                               '''[Service]
ProtectSystem=strict
ProtectHome=tmpfs
ProtectKernelTuneables=true
ProtectKernelModules=true
ProtectControlGroups=true
SystemCallArchitectures=native
PrivateTmp=true
ReadWritePaths=/mnt/glusterfs
RuntimeDirectory=gluster
StateDirectory=glusterd
LogsDirectory=glusterfs
ConfigurationDirectory=glusterfs
''',
                               mode=0o644)
