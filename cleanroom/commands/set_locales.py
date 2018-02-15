"""set_locales command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.exceptions as ex
import cleanroom.helper.generic.file as file
import cleanroom.parser as parser

import os.path


class SetLocalesCommand(cmd.Command):
    """The set_default_target command."""

    def __init__(self):
        """Constructor."""
        self._file_name = None
        self._line_number = -1

        super().__init__('set_locales <LOCALE> [<MORE_LOCALES>]',
                         'Set the system locales.')

    def validate_arguments(self, file_name, line_number, *args, **kwargs):
        """Validate the arguments."""
        if len(args) < 1:
            raise ex.ParseError(file_name, line_number,
                                'set_locales needs at least one locale.')

        self._file_name = file_name
        self._line_number = line_number

        return None

    def __call__(self, run_context, *args, **kwargs):
        """Execute command."""
        locales_dir = os.path.join(run_context.fs_directory(),
                                   'usr/share/locale')
        locales = []
        for a in args:
            if not os.path.isdir(os.path.join(locales_dir, a))\
               and not os.path.isdir(os.path.join(locales_dir, a[0:2])):
                raise ex.ParseError(self._file_name, self._line_number,
                                    'Locale "{}" not found in '
                                    '/usr/share/locale.'.format(a))
            locales.append('{}.UTF8 UTF8'.format(a))

        all_locales = '\n'.join(locales).encode('utf-8')
        file.create_file(run_context, '/etc/locale.gen', all_locales,
                         force=True)
        self._setup_hooks(run_context)

    def _setup_hooks(self, run_context):
        if run_context.flags.get('locales_setup', None) is None:
            run_context.add_hook('export',
                                 parser.Parser.create_execute_object(
                                    '<set_locales>', 1,
                                    'run', '/usr/bin/locale-gen'))
            run_context.add_hook('export',
                                 parser.Parser.create_execute_object(
                                    '<set_locales>', 2,
                                    'remove',
                                    '/usr/share/locale/*',
                                    '/etc/locale.gen', '/usr/bin/locale-gen',
                                    '/usr/bin/localedef',
                                    force=True, recursive=True
                                 ))
        run_context.flags['locales_setup'] = True
