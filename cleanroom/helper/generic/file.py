# -*- coding: utf-8 -*-
"""Helpers for file system actions.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.exceptions as ex
import cleanroom.printer as printer

from . import group as groupdb
from . import user as userdb

import glob
import os
import os.path
import shutil


def file_name(system_context, f):
    """Return the full (outside) file path to a absolute (inside) file."""
    if not os.path.isabs(f):
        raise ex.GenerateError('File path "{}" is not absolute.'.format(f))

    root_path = os.path.realpath(system_context.fs_directory())
    if root_path.endswith('/'):
        root_path = root_path[:-1]

    full_path = os.path.normpath(root_path + f)
    printer.trace('Mapped file path "{}" to "{}".'.format(f, full_path))

    if full_path != root_path and not full_path.startswith(root_path + '/'):
        raise ex.GenerateError('File path "{}" is outside of "{}"'
                               .format(full_path, root_path))
    return full_path


def expand_files(system_context, *files):
    """Prepend the system directory and expand glob patterns.

    Prepend system directory to files iff the system_context is given.
    Expand glob patterns.
    """
    to_iterate = files
    if system_context is not None:
        to_iterate = map(lambda f: file_name(system_context, f), files)

    for pattern in to_iterate:
        for match in glob.iglob(pattern):
            yield match


def _check_file(system_context, f, op, description, base_directory=None):
    """Run op on a file f."""
    if base_directory is not None:
        base_directory = file_name(system_context, base_directory)
        os.chdir(base_directory)

    to_test = f
    if os.path.isabs(f):
        to_test = file_name(system_context, f)

    result = op(to_test)

    # Report result:
    if base_directory is None:
        printer.trace('{}: {} = {}'.format(description, to_test, result))
    else:
        printer.trace('{}: {} (relative to {}) = {}'
                      .format(description, to_test, base_directory, result))
    return result


def exists(system_context, f, base_directory=None):
    """Check whether a file exists."""
    return _check_file(system_context, f, os.path.exists, 'file exists:',
                       base_directory=base_directory)


def isfile(system_context, f, base_directory=None):
    """Check whether a file exists and is a file."""
    return _check_file(system_context, f, os.path.isfile, 'isfile:',
                       base_directory=base_directory)


def isdir(system_context, f, base_directory=None):
    """Check whether a file exists and is a directory."""
    return _check_file(system_context, f, os.path.isdir, 'isdir:',
                       base_directory=base_directory)


def symlink(system_context, source, destination, base_directory=None):
    """Create a symbolic link."""
    if base_directory is not None:
        os.chdir(file_name(system_context, base_directory))

    if os.path.isabs(destination):
        destination = file_name(system_context, destination)

    printer.trace('Symlinking "{}"->"{}".'.format(source, destination))
    os.symlink(source, destination)


def makedirs(system_context, *dirs, user=0, group=0, mode=None):
    """Make directories in the system filesystem."""
    for d in dirs:
        full_path = file_name(system_context, d)
        if os.makedirs(full_path):
            _chmod(system_context, mode, full_path)
        _chown(system_context, _get_uid(user), _get_gid(group), full_path)


def _chmod(system_context, mode, *files):
    """For internal use only."""
    for f in files:
        printer.trace('Chmod of "{}" to {}.'.format(f, mode))
        os.chmod(f, mode)


def chmod(system_context, mode, *files):
    """Chmod in the system filesystem."""
    return _chmod(system_context, mode, *expand_files(system_context, *files))


def _chown(system_context, uid, gid, *files):
    """Change owner of files."""
    assert(uid is not str)
    assert(gid is not str)

    for f in files:
        printer.trace('Chown of "{}" to {}:{}.'.format(f, uid, gid))
        os.chown(f, uid, gid)


def _get_uid(system_context, user):
    if not user:
        return 0
    if user is int:
        return user
    data = userdb.user_data(system_context, user)
    assert data is not None
    return data.uid


def _get_gid(system_context, group):
    if not group:
        return 0
    if group is int:
        return group
    data = groupdb.group_data(system_context, group)
    assert data is not None
    return data.gid


def chown(system_context, user, group, *files):
    """Change ownership of a file in the system filesystem."""
    uid = _get_uid(user)
    gid = _get_gid(group)

    return _chown(system_context, uid, gid,
                  *expand_files(system_context, *files))


def read_file(system_context, file, outside=False):
    """Read the contents of a file."""
    if not outside:
        file = system_context.file_name(file)
    with open(file, 'rb') as f:
        return f.read()

def create_file(system_context, file, contents, force=False, mode=0o644,
                user=0, group=0):
    """Create a new file with the given contents."""
    full_path = file_name(system_context, file)

    if os.path.exists(full_path) and not force:
        raise ex.GenerateError('"{}" exists when trying to create a '
                               'file there.'.format(full_path))

    with open(full_path, 'wb') as f:
        f.write(contents)

    os.chmod(full_path, mode)
    _chown(_get_uid(user), _get_gid(group), full_path)


def append_file(system_context, file, contents):
    """Append contents to an existing file."""
    full_path = file_name(system_context, file)

    if not os.path.exists(full_path):
        raise ex.GenerateError('"{}" does not exist when trying to append to '
                               'it.'.format(full_path))

    with open(full_path, 'ab') as f:
        f.write(contents)


def prepend_file(system_context, file, contents):
    """Prepend contents to an existing file."""
    full_path = file_name(system_context, file)

    if not os.path.exists(full_path):
        raise ex.GenerateError('"{}" does not exist when trying to append to '
                               'it.'.format(full_path))

    with open(full_path, 'r+b') as f:
        existing_contents = f.read()
        f.seek(0, 0)
        f.write(contents + existing_contents)


def _file_op(system_context, op, description, *args,
             to_outside=False, from_outside=False, ignore_missing_sources=True,
             **kwargs):
    assert(not to_outside or not from_outside)
    sources = args[:-1]
    destination = args[-1]

    if from_outside:
        sources = tuple(expand_files(None, *sources))
    else:
        sources = tuple(expand_files(system_context, *sources))

    if not to_outside:
        destination = file_name(system_context, destination)

    if ignore_missing_sources and not sources:
        return

    assert(sources)

    printer.trace(description.format('", "'.join(sources), destination))
    for source in sources:
        op(source, destination, **kwargs)


def copy(system_context, *args, **kwargs):
    """Copy files."""
    return _file_op(system_context, shutil.copyfile, 'Copying "{}" to "{}".',
                    *args, **kwargs)


def move(system_context, *args, **kwargs):
    """Move files."""
    return _file_op(system_context, shutil.move, 'Moving "{}" to "{}".',
                    *args, **kwargs)


def remove(system_context, *files, recursive=False, force=False):
    """Delete a file inside of a system."""
    for file in expand_files(system_context, *files):
        printer.trace('Removing "{}".'.format(file))

        if not os.path.exists(file):
            if force:
                continue
            raise ex.GenerateError('Failed to delete: "{}" does not exist.'
                                   .format(file))
        if os.path.isdir(file):
            if recursive:
                shutil.rmtree(file)
            else:
                os.rmdir(file)
        else:
            try:
                os.unlink(file)
            except Exception as e:
                if not force:
                    raise
                else:
                    printer.verbose('Failed to unlink "{}".'.format(file))
