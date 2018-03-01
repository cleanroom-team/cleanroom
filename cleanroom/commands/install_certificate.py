"""install_certificate command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.exceptions as ex
import cleanroom.helper.generic.file as file

import os
import os.path
import stat


class InstallCertificatesCommand(cmd.Command):
    """The install_certificate command."""

    def __init__(self):
        """Constructor."""
        super().__init__('install_certificate <CA_CERT> [<MORE_CA_CERTS>]',
                         'Install CA certificates.')

    def validate_arguments(self, file_name, line_number, *args, **kwargs):
        """Validate the arguments."""
        if len(args) < 1:
            raise ex.ParseError('install_certificates needs at least one '
                                'certificate to install.',
                                file_name=file_name, line_number=line_number)

        return None

    def __call__(self, file_name, line_number, run_context, *args, **kwargs):
        """Execute command."""
        # RSH "Update trust" <<< /usr/bin/trust extract-compat >>>
        for f in args:
            if os.path.isabs(f):
                source = f
            else:
                source = os.path.join(run_context.ctx.systems_directory(), f)
            dest = os.path.join('/etc/ca-certificates/trust-source/anchors',
                                os.path.basename(f))
            file.copy(run_context, source, dest, from_outside=True)
            file.chmod(run_context,
                       stat.S_IRUSR | stat.S_IWUSR
                       | stat.S_IRGRP | stat.S_IROTH,
                       dest)

        run_context.run('/usr/bin/trust', 'extract-compat')
