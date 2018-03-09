"""set_hostname command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.exceptions as ex
import cleanroom.helper.generic.file as file


class SetHostnameCommand(cmd.Command):
    """The set_hostname command."""

    def __init__(self):
        """Constructor."""
        super().__init__('set_hostname <STATIC> [pretty=<PRETTY>]',
                         'Set the hostname of the system.')

    def validate_arguments(self, file_name, line_number, *args, **kwargs):
        """Validate the arguments."""
        if len(args) != 1:
            raise ex.ParseError('set_hostname needs the static hostname.',
                                file_name=file_name, line_number=line_number)

        return None

    def __call__(self, file_name, line_number, run_context, *args, **kwargs):
        """Execute command."""
        static_hostname = args[0]
        pretty_hostname = kwargs.get('pretty', static_hostname)

        if run_context.has_substitution('HOSTNAME'):
            raise ex.GenerateError('Hostname was already set.',
                                   file_name=file_name,
                                   line_number=line_number)

        run_context.set_substitution('HOSTNAME', static_hostname)
        run_context.set_substitution('PRETTY_HOSTNAME', pretty_hostname)

        file.create_file(run_context, '/etc/hostname',
                         static_hostname.encode('utf-8'))
        pattern = \
            's/^PRETTY_HOSTNAME=.*$/PRETTY_HOSTNAME=\\"{}\\"/'\
            .format(pretty_hostname)
        run_context.run('/usr/bin/sed', '-i', '-e', pattern,
                        '/etc/machine.info')
