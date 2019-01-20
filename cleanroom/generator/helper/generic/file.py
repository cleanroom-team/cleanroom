# -*- coding: utf-8 -*-
"""Helpers for file system actions.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.exceptions import GenerateError
from cleanroom.printer import debug, info, trace, verbose

from .group import group_data
from .user import user_data

import distutils.dir_util
import glob
import os
import os.path
import shutil


def file_name(system_context, f):
    """Return the full (outside) file path to a absolute (inside) file."""
    if not os.path.isabs(f):
        raise GenerateError('File path "{}" is not absolute.'.format(f))

    full_path = os.path.normpath(f)
    if system_context is not None:
        root_path = '/'

        root_path = os.path.realpath(system_context.fs_directory())
        full_path = os.path.normpath(os.path.join(root_path, f[1:]))

        if full_path != root_path and not full_path.startswith(root_path + '/'):
            raise GenerateError('File path "{}" is outside of "{}"'
                                .format(full_path, root_path))

    trace('Mapped file path "{}" to "{}".'.format(f, full_path))

    return full_path


def expand_files(system_context, *files, recursive=False):
    """Prepend the system directory and expand glob patterns.

    Prepend system directory to files iff the system_context is given.
    Expand glob patterns.
    """
    if system_context:
        to_iterate = map(lambda f: file_name(system_context, f), files)
    else:
        to_iterate = map(lambda f: os.path.join(os.getcwd(), f), files)

    for pattern in to_iterate:
        debug('expand_files: Matching pattern: {}.'.format(pattern))
        for match in glob.iglob(pattern, recursive=recursive):
            debug('expand_files: --- match {}.'.format(match))
            yield match


def _check_file(system_context, f, op, description, work_directory=None):
    """Run op on a file f."""
    old_work_directory = os.getcwd()
    if work_directory is not None:
        work_directory = file_name(system_context, work_directory)
        os.chdir(work_directory)

    to_test = f
    if os.path.isabs(f):
        to_test = file_name(system_context, f)

    result = op(to_test)

    # Report result:
    if work_directory is None:
        trace('{}: {} = {}'.format(description, to_test, result))
    else:
        trace('{}: {} (relative to {}) = {}'
              .format(description, to_test, work_directory, result))

    os.chdir(old_work_directory)
    return result


def exists(system_context, f, work_directory=None):
    """Check whether a file exists."""
    return _check_file(system_context, f, os.path.exists, 'file exists:',
                       work_directory=work_directory)


def isfile(system_context, f, work_directory=None):
    """Check whether a file exists and is a file."""
    return _check_file(system_context, f, os.path.isfile, 'isfile:',
                       work_directory=work_directory)


def isdir(system_context, f, work_directory=None):
    """Check whether a file exists and is a directory."""
    return _check_file(system_context, f, os.path.isdir, 'isdir:',
                       work_directory=work_directory)


def symlink(system_context, source, destination, work_directory=None):
    """Create a symbolic link."""
    if work_directory is not None:
        os.chdir(file_name(system_context, work_directory))

    if os.path.isabs(destination):
        destination = file_name(system_context, destination)

    if os.path.isdir(destination):
        destination = os.path.join(destination, os.path.basename(source))

    trace('Symlinking "{}"->"{}".'.format(source, destination))
    os.symlink(source, destination)


def makedirs(system_context, *dirs, user=0, group=0, mode=None, force=False):
    """Make directories in the system filesystem."""
    for d in dirs:
        info('Creating "{}" with mode={}, uid={}, gid={} ({}).'
             .format(d, mode, user, group, force))
        full_path = file_name(system_context, d)
        os.makedirs(full_path, exist_ok=force)
        _chmod(system_context, mode, full_path)
        _chown(system_context,
               _get_uid(system_context, user),
               _get_gid(system_context, group), full_path)


def _chmod(system_context, mode, *files):
    """For internal use only."""
    if mode is None:
        return
    for f in files:
        trace('Chmod of "{}" to {}.'.format(f, mode))
        if os.path.islink(f):
            debug(' -> {} is a symlink, skipping for chmod.'.format(f))
            continue
        os.chmod(f, mode)


def chmod(system_context, mode, *files, recursive=False):
    """Chmod in the system filesystem."""
    return _chmod(system_context, mode,
                  *expand_files(system_context, *files, recursive=recursive))


def _chown(system_context, uid, gid, *files):
    """Change owner of files."""
    assert uid is not str
    assert gid is not str

    for f in files:
        trace('Chown of "{}" to {}:{}.'.format(f, uid, gid))
        os.chown(f, uid, gid, follow_symlinks=False)


def _get_uid(system_context, user):
    trace('Getting UID of {} ({}).'.format(user, type(user)))
    if user is None:
        info('UID: Mapped None to 0.')
        return 0
    if isinstance(user, int):
        info('UID: Mapped numeric user to {}.'.format(user))
        return user
    if isinstance(user, str) and user.isdigit():
        uid = int(user)
        info('UID: Mapped numeric string to {}.'.format(uid))
        return uid
    data = user_data(system_context, user)
    if data is None:  # No user file was found!
        info('UID: User file not found, mapped to 0.')
        return 0
    info('UID: User name {} mapped to {}.'.format(user, data.gid))
    return data.uid


def _get_gid(system_context, group):
    trace('Getting GID of {} ({}).'.format(group, type(group)))
    if group is None:
        info('GID: Mapped None to 0.')
        return 0
    if isinstance(group, int):
        info('GID: Mapped numeric group to {}.'.format(group))
        return group
    if isinstance(group, str) and group.isdigit():
        gid = int(group)
        info('GID: Mapped numeric string to {}.'.format(gid))
        return gid
    data = group_data(system_context, group)
    if data is None:  # No group file was found!
        info('GID: Group file not found, mapped to 0.')
        return 0
    info('GID: Group name {} mapped to {}.'.format(group, data.gid))
    return data.gid


def chown(system_context, user, group, *files, recursive=False):
    """Change ownership of a file in the system filesystem."""
    return _chown(system_context,
                  _get_uid(system_context, user),
                  _get_gid(system_context, group),
                  *expand_files(system_context, *files, recursive=recursive))


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
        raise GenerateError('"{}" exists when trying to create a '
                            'file there.'.format(full_path))

    with open(full_path, 'wb') as f:
        f.write(contents)

    trace('Changing permissions of {} to {}.'.format(full_path, mode))
    os.chmod(full_path, mode)
    uid = _get_uid(system_context, user)
    gid = _get_gid(system_context, group)
    trace('Changing ownership of {} to {}:{}.'.format(full_path, uid, gid))
    _chown(system_context, uid, gid, full_path)


def append_file(system_context, file, contents, *, force=False):
    """Append contents to an existing file."""
    full_path = file_name(system_context, file)

    if not os.path.exists(full_path) and not force:
        raise GenerateError('"{}" does not exist when trying to append to it.'
                            .format(full_path))

    with open(full_path, 'ab') as f:
        f.write(contents)


def prepend_file(system_context, file, contents):
    """Prepend contents to an existing file."""
    full_path = file_name(system_context, file)

    if not os.path.exists(full_path):
        raise GenerateError('"{}" does not exist when trying to append to it.'
                            .format(full_path))

    with open(full_path, 'r+b') as f:
        existing_contents = f.read()
        f.seek(0, 0)
        f.write(contents + existing_contents)


def _file_op(system_context, op, description, *args,
             to_outside=False, from_outside=False, ignore_missing_sources=True,
             recursive=False, force=False, **kwargs):
    assert(not to_outside or not from_outside)
    sources = args[:-1]
    destination = args[-1]

    desc = description.format(sources, destination)
    debug('File_op(raw): {}'.format(desc))
    sources = tuple(expand_files(None if from_outside else system_context,
                                 *sources, recursive=True))
    destination = file_name(None if to_outside else system_context,
                            destination)
    desc = description.format(sources, destination)
    debug('File_op(mapped): {}.'.format(desc))

    assert sources or ignore_missing_sources

    trace(description.format('", "'.join(sources), destination))
    for source in sources:
        if not source:
            if ignore_missing_sources:
                continue
            else:
                raise OSError('Source failed to map.')

        s = os.path.normpath(source)
        if not os.path.exists(s):
            if ignore_missing_sources:
                continue
            else:
                raise OSError('Source file "{}" does not exist.'.format(s))

        d = os.path.normpath(destination)
        if os.path.isfile(d):
            if not force:
                raise OSError('Destination "{}" exists already.'.format(d))

        if os.path.isdir(d):
            d = os.path.join(d, os.path.basename(s))

        assert s != d
        desc = description.format(s, d)
        debug('File_op(running once): {}.'.format(desc))
        op(s, d, **kwargs)


def _copy_op(source, destination, **kwargs):
    shutil.copyfile(source, destination, **kwargs)


def _recursive_copy_op(source, destination, **kwargs):
    if os.path.isdir(source):
        assert os.path.isdir(destination) or not os.path.exists(destination)
        distutils.dir_util.copy_tree(source, destination)
    else:
        assert not os.path.isdir(destination)
        assert not os.path.exists(destination)
        shutil.copyfile(source, destination, **kwargs)


def copy(system_context, *args, recursive=False, **kwargs):
    """Copy files."""
    if recursive:
        return _file_op(system_context, _recursive_copy_op,
                        'Copying "{}" to "{}" (recursive).', *args, **kwargs)
    return _file_op(system_context, _copy_op,
                    'Copying "{}" to "{}".', *args, **kwargs)


def move(system_context, *args, **kwargs):
    """Move files."""
    return _file_op(system_context, shutil.move, 'Moving "{}" to "{}".',
                    *args, **kwargs)


def remove(system_context, *files, recursive=False, force=False, outside=False):
    """Delete a file inside of a system."""
    sc = None if outside else system_context
    for file in expand_files(sc, *files, recursive=True):
        trace('Removing "{}".'.format(file))

        if not os.path.exists(file):
            if force:
                continue
            raise GenerateError('Failed to delete: "{}" does not exist.'
                                .format(file))
        if os.path.isdir(file) and not os.path.islink(file):
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
                    verbose('Failed to unlink "{}".'.format(file))
