#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Helpers for file system actions.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from ... import exceptions as ex

import glob
import os
import os.path
import shutil


def file_name(run_context, f):
    """Return the full (outside) file path to a absolute (inside) file."""
    if not os.path.isabs(f):
        raise ex.GenerateError('File path "{}" is not absolute.'.format(f))

    root_path = os.path.realpath(run_context.fs_directory())
    if root_path.endswith('/'):
        root_path = root_path[:-1]

    full_path = os.path.normpath(root_path + f)
    run_context.ctx.printer.trace('Mapped file path "{}" to "{}".'
                                  .format(f, full_path))

    if full_path != root_path and not full_path.startswith(root_path + '/'):
        raise ex.GenerateError('File path "{}" is outside of "{}"'
                               .format(full_path, root_path))
    return full_path


def expand_files(run_context, *files):
    """Prepend the system directory and expand glob patterns.

    Prepend system directory to files iff the run_context is given.
    Expand glob patterns.
    """
    to_iterate = files
    if run_context is not None:
        to_iterate = map(lambda f: file_name(run_context, f), files)

    for pattern in to_iterate:
        for match in glob.iglob(pattern):
            yield match


def _check_file(run_context, f, op, description, base_directory=None):
    """Run op on a file f."""
    if base_directory is not None:
        base_directory = file_name(run_context, base_directory)
        os.chdir(base_directory)

    to_test = f
    if os.path.isabs(f):
        to_test = file_name(run_context, f)

    result = op(to_test)

    # Report result:
    if base_directory is None:
        run_context.ctx.printer.trace('{}: {} = {}'
                                      .format(description, to_test, result))
    else:
        run_context.ctx.printer.trace('{}: {} (relative to {}) = {}'
                                      .format(description, to_test,
                                              base_directory, result))
    return result


def exists(run_context, f, base_directory=None):
    """Check whether a file exists."""
    return _check_file(run_context, f, os.path.exists, 'file exists:',
                       base_directory=base_directory)


def isfile(run_context, f, base_directory=None):
    """Check whether a file exists and is a file."""
    return _check_file(run_context, f, os.path.isfile, 'isfile:',
                       base_directory=base_directory)


def isdir(run_context, f, base_directory=None):
    """Check whether a file exists and is a directory."""
    return _check_file(run_context, f, os.path.isdir, 'isdir:',
                       base_directory=base_directory)


def symlink(run_context, source, destination, base_directory=None):
    """Create a symbolic link."""
    if base_directory is not None:
        os.chdir(file_name(run_context, base_directory))

    if os.path.isabs(destination):
        destination = file_name(run_context, destination)

    run_context.ctx.printer.trace('Symlinking "{}"->"{}".'
                                  .format(source, destination))
    os.symlink(source, destination)


def makedirs(run_context, *dirs, user=0, group=0, mode=None):
    """Make directories in the system filesystem."""
    for d in dirs:
        full_path = file_name(run_context, d)
        if os.makedirs(full_path):
            _chmod(run_context, mode, full_path)
        _chown(run_context, user, group, full_path)


def _chmod(run_context, mode, *files):
    """For internal use only."""
    for f in files:
        run_context.ctx.printer.trace('Chmod of "{}" to {}.'
                                      .format(f, mode))
        os.chmod(f, mode)


def chmod(run_context, mode, *files):
    """Chmod in the system filesystem."""
    return _chmod(run_context, mode, *expand_files(run_context, *files))


def _chown(run_context, user, group, *files):
    """Change owner of files."""
    if user == 'root':
        user = 0
    if group == 'root':
        group = 0

    assert(user is not str)
    assert(group is not str)

    for f in files:
        run_context.ctx.printer.trace('Chown of "{}" to {}:{}.'
                                      .format(f, user, group))
        os.chown(f, user, group)


def chown(run_context, user, group, *files):
    """Change ownership of a file in the system filesystem."""
    return _chown(run_context, user, group, *expand_files(run_context, *files))


def create_file(run_context, file, contents, force=False):
    """Create a new file with the given contents."""
    full_path = file_name(run_context, file)

    if os.path.exists(full_path) and not force:
        raise ex.GenerateError('"{}" exists when trying to create a '
                               'file there.'.format(full_path))

    with open(full_path, 'wb') as f:
        f.write(contents)


def append_file(run_context, file, contents):
    """Append contents to an existing file."""
    full_path = file_name(run_context, file)

    if not os.path.exists(full_path):
        raise ex.GenerateError('"{}" does not exist when trying to append to '
                               'it.'.format(full_path))

    with open(full_path, 'ab') as f:
        f.write(contents)


def prepend_file(run_context, file, contents):
    """Prepend contents to an existing file."""
    full_path = file_name(run_context, file)

    if not os.path.exists(full_path):
        raise ex.GenerateError('"{}" does not exist when trying to append to '
                               'it.'.format(full_path))

    with open(full_path, 'r+b') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(contents + content)


def _file_op(run_context, op, description, *args,
             to_outside=False, from_outside=False, ignore_missing_sources=True,
             **kwargs):
    assert(not to_outside or not from_outside)
    sources = args[:-1]
    destination = args[-1]

    if from_outside:
        sources = tuple(expand_files(None, *sources))
    else:
        sources = tuple(expand_files(run_context, *sources))

    if not to_outside:
        destination = file_name(run_context, destination)

    if ignore_missing_sources and not sources:
        return

    assert(sources)

    run_context.ctx.printer.trace(description
                                  .format('", "'.join(sources), destination))
    for source in sources:
        op(source, destination, **kwargs)


def copy(run_context, *args, **kwargs):
    """Copy files."""
    return _file_op(run_context, shutil.copyfile, 'Copying "{}" to "{}".',
                    *args, **kwargs)


def move(run_context, *args, **kwargs):
    """Move files."""
    return _file_op(run_context, shutil.move, 'Moving "{}" to "{}".',
                    *args, **kwargs)


def remove(run_context, *files, recursive=False, force=False):
    """Delete a file inside of a system."""
    for file in expand_files(run_context, *files):
        run_context.ctx.printer.trace('Removing "{}".'.format(file))

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
            os.unlink(file)


if __name__ == '__main__':
    pass
