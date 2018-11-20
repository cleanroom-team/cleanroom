# -*- coding: utf-8 -*-
"""pkg_quasselcore command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.generator.command import Command


class PkgQuasselcoreCommand(Command):
    """The pkg_quasselcore command."""

    def __init__(self):
        """Constructor."""
        super().__init__('pkg_quasselcore', help='Setup quasselcore.',
                         file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_no_arguments(location, *args, **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        password=kwargs.get('password', '')
        system_context.execute(location.next_line(),
                               'pacman', 'quassel-core', 'postgresql-libs')

        system_context.execute(location.next_line(),
                               'mkdir', '/usr/lib/systemd/system/quasselcore.service.d',
                               mode=0o755)
        system_context.execute(location.next_line(),
                               'create', '/usr/lib/systemd/system/quasselcore.service.d/harden.conf',
                               '''[Service]
PrivateTmp=true
ProtectSystem=full
ProtectHome=tmpfs
ProtectKernelTuneables=true
ProtectKernelModules=true
ProtectControlGroups=true
RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6
RestrictRealtime=yes
NoNewPrivileges=true
PIDFile=/run/quassel/pid
RuntimeDirectory=quassel
RuntimeDirectoryMode=700
EnvironmentFile=
''',
                               mode=0o644)

