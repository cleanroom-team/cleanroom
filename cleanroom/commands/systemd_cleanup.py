# -*- coding: utf-8 -*-
"""systemd_cleanup command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.exceptions as ex
import cleanroom.printer as printer

import os.path
import shutil


class SystemdCleanupCommand(cmd.Command):
    """The systemd_cleanup command."""

    def __init__(self):
        """Constructor."""
        super().__init__('systemd_cleanup',
                         help='Make sure /etc/systemd/system is empty by '
                         'moving files and links to the appropriate /usr '
                         'directory.')

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        return self._validate_no_arguments(location, *args, **kwargs)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        old_base = system_context.file_name('/etc/systemd/system') + '/'
        new_base = system_context.file_name('/usr/lib/systemd/system') + '/'

        printer.trace("walking:", old_base)

        for root, dirs, files in os.walk(old_base):
            for f in files:
                full_path = os.path.join(root, f)
                printer.trace("Checking", full_path)
                if os.path.islink(full_path):
                    printer.trace('Moving link', full_path)
                    self._move_symlink(location, system_context,
                                       old_base, new_base, full_path)
                else:
                    printer.trace('Moving file', full_path)
                    self._move_file(location, old_base, new_base, full_path)

        system_context.execute(location, 'remove', '/etc/systemd/system/*',
                               recursive=True, force=True)

    def _map_base(self, old_base, new_base, input):
        assert(old_base.endswith('/'))

        input = os.path.normpath(input)
        if not input.startswith(old_base):
            return (input, input)

        input_relative_to_oldbase = input[len(old_base):]
        output = os.path.join(new_base, input_relative_to_oldbase)

        return (output, input)

    def _map_target_link(self, old_base, new_base, link, link_target):
        assert(old_base.endswith('/'))
        assert(new_base.endswith('/'))
        assert(link.startswith(old_base))

        link_directory = os.path.dirname(link)

        (link, old_link) \
            = self._map_base(old_base, new_base, link)
        (link_target, old_link_target) \
            = self._map_base(old_base, new_base,
                             os.path.join(link_directory, link_target))

        if link_target.startswith(new_base):
            relative_link_target = os.path.relpath(link_target,
                                                   os.path.dirname(link))
            return (link, relative_link_target)
        else:
            return (link, link_target)

    def _map_host_link(self, root_directory, old_base, new_base,
                       link, link_target):
        assert(root_directory.endswith('/'))
        assert(old_base.startswith(root_directory))
        assert(new_base.startswith(root_directory))

        assert(old_base.endswith('/'))
        assert(new_base.endswith('/'))
        assert(link.startswith(old_base))

        assert(not link_target.startswith(root_directory))

        root_directory_length = len(root_directory) - 1  # minus last '/'

        host_old_base = old_base[root_directory_length:]
        host_new_base = new_base[root_directory_length:]
        host_link = link[root_directory_length:]

        (host_link, link_target) \
            = self._map_target_link(host_old_base, host_new_base,
                                    host_link, link_target)

        assert(os.path.isabs(host_link))
        return (os.path.join(root_directory, host_link[1:]), link_target)

    def _move_symlink(self, location, system_context,
                      old_base, new_base, link):
        """Move a symlink."""
        root_directory = system_context.fs_directory() + '/'
        link_target = os.readlink(link)
        (output_link, output_link_target) \
            = self._map_host_link(root_directory,
                                  old_base, new_base, link, link_target)

        printer.trace('Moving link {}->{}: {} to {}'
                      .format(link, link_target, output_link,
                              output_link_target))
        os.makedirs(os.path.dirname(output_link), mode=0o755, exist_ok=True)

        if not os.path.isdir(os.path.dirname(output_link)):
            raise ex.GenerateError('"{}" is no directory when trying to move '
                                   '"{}" into /usr.'
                                   .format(output_link, link),
                                   location=location)

        if os.path.exists(output_link):
            if not os.path.islink(output_link):
                raise ex.GenerateError('"{}" exists and is not a link when '
                                       'trying to move "{}" into /usr.'
                                       .format(output_link, link),
                                       location=location)
            else:
                old_link_target = os.readlink(output_link)
                if old_link_target != output_link_target:
                    raise ex.GenerateError('"{}" exists but points to "{}" '
                                           'when "{}" was expected.'
                                           .format(link, old_link_target,
                                                   output_link_target),
                                           location=location)
                else:
                    return  # Already correct
        else:
            os.symlink(output_link_target, output_link)

    def _move_file(self, location, old_base, new_base, path):
        """Move a file."""
        path_dir = os.path.dirname(path)
        path_name = os.path.basename(path)

        new_dir = self._map_base(old_base, new_base, path_dir)
        if os.path.exists(new_dir) and not os.path.isdir(new_dir):
            raise ex.GenerateError('"{}" is not a directory when moving "{}".'
                                   .format(new_dir, path),
                                   location=location)

        if not os.path.exists(new_dir):
            os.makedirs(new_dir, 0o755)

        new_path = os.path.join(new_dir, path_name)
        if os.path.exists(new_path):
            raise ex.GenerateError('"{}" already exists when moving "{}".'
                                   .format(new_path, path),
                                   location=location)

        shutil.copyfile(path, new_path)
