#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Helpers for file system actions.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from ... import exceptions as ex

import os
import os.path
import shutil


def file_name(run_context, f):
    """Return the full (outside) file path to a absolute (inside) file."""
    if not os.path.isabs(f):
        raise ex.GenerateError('File path "{}" is not absolute.'.format(f))

    root_path = os.path.realpath(run_context.fs_directory())
    if not root_path.endswith('/'):
        root_path += '/'

    full_path = os.path.realpath(root_path + f)

    if not full_path.startswith(root_path):
        raise ex.GenerateError('File path "{}" is outside of "{}"'
                               .format(full_path, root_path))
    return full_path


def makedirs(run_context, *dirs, user=0, group=0, mode=None):
    """Make directories in the system filesystem."""
    for d in dirs:
        full_path = file_name(run_context, d)
        if os.makedirs(full_path):
            _chmod(full_path, mode)
        _chown(full_path, user, group)


def _chmod(file_path, mode):
    """For internal use only."""
    if mode:
        return os.chmod(file_path, mode)
    return True


def chmod(run_context, f, mode):
    """Chmod in the system filesystem."""
    full_path = file_name(run_context, f)
    return _chmod(full_path, mode)


def _chown(file_path, user, group):
    if user == 'root':
        user = 0
    if group == 'root':
        group = 0

    assert(user is not str)
    assert(group is not str)

    return os.chown(file_path, user, group)


def chown(run_context, f, user, group):
    """Change ownership of a file in the system filesystem."""
    full_path = file_name(run_context, f)

    return _chown(full_path, user, group)


def create_file(run_context, f, contents):
    """Create a new file with the given contents."""
    full_path = file_name(run_context, f)

    if os.exists(full_path):
        raise ex.GenerateError('"{}" exists when trying to create a '
                               'file there.'.format(full_path))

    with open(full_path, 'wb') as f:
        f.write(contents)


def replace_file(run_context, f, contents):
    """Replace an existing file with the given contents."""
    full_path = file_name(run_context, f)

    if not os.exists(full_path):
        raise ex.GenerateError('"{}" does not exist when trying to replace '
                               'the file.'.format(full_path))

    if not os.path.isfile(full_path):
        raise ex.GenerateError('"{}" is not a file when trying to replace it.'
                               .format(full_path))

    with open(full_path, 'wb') as f:
        f.write(contents)


def append_file(run_context, f, contents):
    """Append contents to an existing file."""
    pass


def prepend_file(run_context, f, contents):
    """Prepend contents to an existing file."""
    pass


def copy_into(run_context, source, destination):
    """Copy a file into a system."""
    full_path = file_name(run_context, destination)
    shutil.copyfile(source, full_path)


def remove(run_context, dest, *, recursive=False):
    """Delete a file inside of a system."""
    full_path = file_name(run_context, dest)
    if os.path.isdir(full_path):
        if recursive:
            shutil.rmtree(full_path)
        else:
            os.rmdir(full_path)
    else:
        os.remove(full_path)


class Deleter:
    """Delete files in the system directory."""

    def __call__(self, run_context, *args, **kwargs):
        """Run delete operations on the files in args."""
        print('!!!!!!!!!!!!!!!!!!!!! Deleter !!!!!!!!!!!!!!!!!!!!!')
        pass


if __name__ == '__main__':
    pass
