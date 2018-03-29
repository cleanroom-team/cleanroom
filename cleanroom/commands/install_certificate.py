# -*- coding: utf-8 -*-
"""install_certificate command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd

import os
import os.path
import stat


class InstallCertificatesCommand(cmd.Command):
    """The install_certificate command."""

    def __init__(self):
        """Constructor."""
        super().__init__('install_certificate',
                         syntax='<CA_CERT> [<MORE_CA_CERTS>]',
                         help='Install CA certificates.')

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        return self._validate_arguments_at_least(location, 1,
                                                 '"{}" needs at least one '
                                                 'ca certificate to add',
                                                 *args, **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        # RSH "Update trust" <<< /usr/bin/trust extract-compat >>>
        for f in args:
            source = f if os.path.isabs(f) \
                else os.path.join(system_context.ctx.systems_directory(), f)
            dest = os.path.join('/etc/ca-certificates/trust-source/anchors',
                                os.path.basename(f))
            system_context.execute(location, 'copy',
                                   source, dest, from_outside=True)
            system_context.execute(location, 'chmod',
                                   stat.S_IRUSR | stat.S_IWUSR
                                   | stat.S_IRGRP | stat.S_IROTH, dest)

        system_context.run('/usr/bin/trust', 'extract-compat')
