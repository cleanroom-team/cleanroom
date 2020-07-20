# -*- coding: utf-8 -*-
"""Helpers for file system actions.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from ..exceptions import GenerateError
from ..printer import debug, info, trace, verbose
from ..systemcontext import SystemContext
from .group import GroupHelper
from .user import UserHelper

from distutils.dir_util import copy_tree

import glob
import os
import os.path
import shutil
import typing


def file_name(system_context: typing.Optional[SystemContext], f: str) -> str:
    """Return the full (outside) file path to a absolute (inside) file."""
    if not os.path.isabs(f):
        raise GenerateError('File path "{}" is not absolute.'.format(f))

    full_path = os.path.normpath(f)
    if system_context:
        root_path = os.path.realpath(system_context.fs_directory)
        full_path = os.path.normpath(os.path.join(root_path, f[1:]))

        if full_path != root_path and not full_path.startswith(root_path + "/"):
            raise GenerateError(
                'File path "{}" is outside of "{}"'.format(full_path, root_path)
            )

    trace('Mapped file path "{}" to "{}".'.format(f, full_path))

    return full_path


def expand_files(
    system_context: typing.Optional[SystemContext], *files: str, recursive: bool = False
) -> typing.Generator[str, None, None]:
    """Prepend the system directory and expand glob patterns.

    Prepend system directory to files iff the system_context is given.
    Expand glob patterns.
    """

    def func(f: str):
        return (
            file_name(system_context, f)
            if system_context
            else os.path.join(os.getcwd(), f)
        )

    to_iterate = map(func, files)

    for pattern in to_iterate:
        debug("expand_files: Matching pattern: {}.".format(pattern))
        for match in glob.iglob(pattern, recursive=recursive):
            debug("expand_files: --- match {}.".format(match))
            yield match


def _check_file(
    system_context: SystemContext,
    f: str,
    op: typing.Callable[..., bool],
    description: str,
    work_directory: typing.Optional[str] = None,
) -> bool:
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
        trace("{}: {} = {}".format(description, to_test, result))
    else:
        trace(
            "{}: {} (relative to {}) = {}".format(
                description, to_test, work_directory, result
            )
        )

    os.chdir(old_work_directory)
    return result


def exists(
    system_context: SystemContext, f: str, work_directory: typing.Optional[str] = None
) -> bool:
    """Check whether a file exists."""
    return _check_file(
        system_context, f, os.path.exists, "file exists:", work_directory=work_directory
    )


def isfile(
    system_context: SystemContext, f: str, work_directory: typing.Optional[str] = None
) -> bool:
    """Check whether a file exists and is a file."""
    return _check_file(
        system_context, f, os.path.isfile, "isfile:", work_directory=work_directory
    )


def isdir(
    system_context: SystemContext, f: str, work_directory: typing.Optional[str] = None
) -> bool:
    """Check whether a file exists and is a directory."""
    return _check_file(
        system_context, f, os.path.isdir, "isdir:", work_directory=work_directory
    )


def symlink(
    system_context: SystemContext,
    source: str,
    destination: str,
    work_directory: typing.Optional[str] = None,
) -> None:
    """Create a symbolic link."""
    if work_directory is not None:
        os.chdir(file_name(system_context, work_directory))

    if os.path.isabs(destination):
        destination = file_name(system_context, destination)

    if os.path.isdir(destination):
        destination = os.path.join(destination, os.path.basename(source))

    trace('Symlinking "{}"->"{}".'.format(source, destination))
    os.symlink(source, destination)


def makedirs(
    system_context: SystemContext,
    *dirs: str,
    user: int = 0,
    group: int = 0,
    mode: typing.Optional[int] = None,
    exist_ok: bool = False
) -> None:
    """Make directories in the system filesystem."""
    for d in dirs:
        info(
            'Creating "{}" with mode={}, uid={}, gid={} (exist_ok: {}).'.format(
                d, mode, user, group, exist_ok
            )
        )
        full_path = file_name(system_context, d)
        os.makedirs(full_path, exist_ok=exist_ok)
        if mode:
            _chmod(mode, full_path)
        _chown(
            _get_uid(system_context, user), _get_gid(system_context, group), full_path
        )


def _chmod(mode: int, *files: str) -> None:
    """For internal use only."""
    if mode is None:
        return
    for f in files:
        trace('Chmod of "{}" to {}.'.format(f, mode))
        if os.path.islink(f):
            debug(" -> {} is a symlink, skipping for chmod.".format(f))
            continue
        os.chmod(f, mode)


def chmod(
    system_context: SystemContext, mode: int, *files: str, recursive: bool = False
) -> None:
    """Chmod in the system filesystem."""
    _chmod(mode, *expand_files(system_context, *files, recursive=recursive))


def _chown(uid: int, gid: int, *files: str) -> None:
    """Change owner of files."""
    assert uid is not str
    assert gid is not str

    for f in files:
        trace('Chown of "{}" to {}:{}.'.format(f, uid, gid))
        os.chown(f, uid, gid, follow_symlinks=False)


def _get_uid(system_context: SystemContext, user: typing.Any) -> int:
    if user is None:
        trace("UID: Mapped None to 0.")
        return 0
    if isinstance(user, int):
        trace("UID: Mapped numeric user to {}.".format(user))
        return user
    if isinstance(user, str) and user.isdigit():
        uid = int(user)
        trace("UID: Mapped numeric string to {}.".format(uid))
        return uid
    data = UserHelper.user_data(user, root_directory=system_context.fs_directory)
    if data is None:  # No user file was found!
        info("UID: User file not found, mapped to 0.")
        return 0
    trace("UID: User name {} mapped to {}.".format(user, data.gid))
    return data.uid


def _get_gid(system_context: SystemContext, group: typing.Any) -> int:
    if group is None:
        trace("GID: Mapped None to 0.")
        return 0
    if isinstance(group, int):
        trace("GID: Mapped numeric group to {}.".format(group))
        return group
    if isinstance(group, str) and group.isdigit():
        gid = int(group)
        trace("GID: Mapped numeric string to {}.".format(gid))
        return gid
    data = GroupHelper.group_data(group, root_directory=system_context.fs_directory)
    if data is None:  # No group file was found!
        info("GID: Group file not found, mapped to 0.")
        return 0
    trace("GID: Group name {} mapped to {}.".format(group, data.gid))
    return data.gid


def chown(
    system_context: SystemContext,
    user: typing.Any,
    group: typing.Any,
    *files: str,
    recursive: bool = False
) -> None:
    """Change ownership of a file in the system filesystem."""
    _chown(
        _get_uid(system_context, user),
        _get_gid(system_context, group),
        *expand_files(system_context, *files, recursive=recursive)
    )


def read_file(system_context: SystemContext, file: str, outside: bool = False) -> bytes:
    """Read the contents of a file."""
    if not outside:
        file = system_context.file_name(file)
    with open(file, "rb") as f:
        return f.read()


def create_file(
    system_context: SystemContext,
    file: str,
    contents: bytes,
    force: bool = False,
    mode: int = 0o644,
    user: typing.Any = 0,
    group: typing.Any = 0,
) -> None:
    """Create a new file with the given contents."""
    full_path = file_name(system_context, file)

    if os.path.exists(full_path) and not force:
        raise GenerateError(
            '"{}" exists when trying to create a ' "file there.".format(full_path)
        )

    with open(full_path, "wb") as f:
        f.write(contents)

    trace("Changing permissions of {} to {}.".format(full_path, mode))
    os.chmod(full_path, mode)
    uid = _get_uid(system_context, user)
    gid = _get_gid(system_context, group)
    trace("Changing ownership of {} to {}:{}.".format(full_path, uid, gid))
    _chown(uid, gid, full_path)


def append_file(
    system_context: SystemContext, file: str, contents: bytes, *, force: bool = False
) -> None:
    """Append contents to an existing file."""
    full_path = file_name(system_context, file)

    if not os.path.exists(full_path) and not force:
        raise GenerateError(
            '"{}" does not exist when trying to append to it.'.format(full_path)
        )

    with open(full_path, "ab") as f:
        f.write(contents)


def prepend_file(
    system_context: SystemContext, file: str, contents: bytes, *, force: bool = False
) -> None:
    """Prepend contents to an existing file."""
    full_path = file_name(system_context, file)

    if not os.path.exists(full_path) and not force:
        raise GenerateError(
            '"{}" does not exist when trying to append to it.'.format(full_path)
        )

    with open(full_path, "r+b") as f:
        existing_contents = f.read()
        f.seek(0, 0)
        f.write(contents + existing_contents)


def _file_op(
    system_context: typing.Optional[SystemContext],
    op: typing.Callable[..., None],
    description: str,
    *args: str,
    to_outside: bool = False,
    from_outside: bool = False,
    ignore_missing_sources: bool = True,
    force: bool = False,
    **kwargs: typing.Any
) -> None:
    assert not to_outside or not from_outside
    sources = args[:-1]
    destination = args[-1]

    desc = description.format(sources, destination)
    debug("File_op(raw): {}".format(desc))
    sources = tuple(
        expand_files(None if from_outside else system_context, *sources, recursive=True)
    )
    destination = file_name(None if to_outside else system_context, destination)
    desc = description.format(sources, destination)
    debug("File_op(mapped): {}.".format(desc))

    assert sources or ignore_missing_sources

    trace(description.format('", "'.join(sources), destination))
    for source in sources:
        if not source:
            if ignore_missing_sources:
                continue
            else:
                raise OSError("Source failed to map.")

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
        debug("File_op(running once): {}.".format(desc))
        op(s, d, **kwargs)


def _copy_op(source: str, destination: str, **kwargs: typing.Any) -> None:
    shutil.copyfile(source, destination, **kwargs)


def _recursive_copy_op(source: str, destination: str, **kwargs: typing.Any) -> None:
    if os.path.isdir(source):
        assert os.path.isdir(destination) or not os.path.exists(destination)
        copy_tree(source, destination)
    else:
        assert not os.path.isdir(destination)
        assert not os.path.exists(destination)
        shutil.copyfile(source, destination, **kwargs)


def copy(
    system_context: typing.Optional[SystemContext],
    *args: str,
    recursive: bool = False,
    **kwargs: typing.Any
) -> None:
    """Copy files."""
    if recursive:
        return _file_op(
            system_context,
            _recursive_copy_op,
            'Copying "{}" to "{}" (recursive).',
            *args,
            **kwargs
        )
    return _file_op(system_context, _copy_op, 'Copying "{}" to "{}".', *args, **kwargs)


def move(
    system_context: typing.Optional[SystemContext], *args: str, **kwargs: typing.Any
) -> None:
    """Move files."""
    return _file_op(
        system_context, shutil.move, 'Moving "{}" to "{}".', *args, **kwargs
    )


def remove(
    system_context: typing.Optional[SystemContext],
    *files: str,
    recursive: bool = False,
    force: bool = False,
    outside: bool = False
) -> None:
    """Delete a file inside of a system."""
    sc = None if outside else system_context
    for file in expand_files(sc, *files, recursive=recursive):
        trace('Removing "{}".'.format(file))

        if not os.path.exists(file):
            if force:
                continue
            raise GenerateError('Failed to delete: "{}" does not exist.'.format(file))
        if os.path.isdir(file) and not os.path.islink(file):
            if recursive:
                shutil.rmtree(file)
            else:
                os.rmdir(file)
        else:
            try:
                os.unlink(file)
            except Exception:
                if not force:
                    raise
                else:
                    verbose('Failed to unlink "{}".'.format(file))
