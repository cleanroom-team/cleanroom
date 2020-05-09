#!/usr/bin/python
"""Test for the systemd_cleanup of cleanroom.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import pytest  # type: ignore

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import cleanroom.commands.systemd_cleanup as systemd_cleanup


@pytest.mark.parametrize(
    ("test_input", "expected"),
    [
        pytest.param(
            (
                "/etc/systemd/system/",
                "/usr/lib/systemd/system/",
                "/etc/systemd/system/test",
            ),
            ("/usr/lib/systemd/system/test", "/etc/systemd/system/test"),
            id="basic",
        ),
        pytest.param(
            ("/etc/systemd/system/", "/usr/lib/systemd/system/", "/tmp/test"),
            ("/tmp/test", "/tmp/test"),
            id="elsewhere",
        ),
        pytest.param(
            ("/foo/bar/", "/foo/baz/bar/", "/foo/bar/baz/test"),
            ("/foo/baz/bar/baz/test", "/foo/bar/baz/test"),
            id="test paths",
        ),
        pytest.param(
            ("/foo/bar/", "/foo/baz/bar/", "/foo/bar/baz/../test"),
            ("/foo/baz/bar/test", "/foo/bar/test"),
            id="relative paths",
        ),
        pytest.param(
            ("/foo/bar/", "/foo/baz/bar/", "/foo/bar/baz/../../test"),
            ("/foo/test", "/foo/test"),
            id="relative path outside base",
        ),
    ],
)
def test_map_base(test_input, expected):
    """Test map_base."""
    cmd = systemd_cleanup
    result = cmd._map_base(*test_input)
    assert result == expected


# _map_target_link:
@pytest.mark.parametrize(
    ("test_input", "expected"),
    [
        pytest.param(
            (
                "/etc/systemd/system/",
                "/usr/lib/systemd/system/",
                "/etc/systemd/system/foo.service",
                "/etc/systemd/system/bar.service",
            ),
            ("/usr/lib/systemd/system/foo.service", "bar.service"),
            id="basic",
        ),
        pytest.param(
            (
                "/etc/systemd/system/",
                "/usr/lib/systemd/system/",
                "/etc/systemd/system/baz.wants/foo.service",
                "../bar.service",
            ),
            ("/usr/lib/systemd/system/baz.wants/foo.service", "../bar.service"),
            id="to parent dir",
        ),
        pytest.param(
            (
                "/etc/systemd/system/",
                "/usr/lib/systemd/system/",
                "/etc/systemd/system/baz.wants/foo.service",
                "/etc/systemd/system/bar.service",
            ),
            ("/usr/lib/systemd/system/baz.wants/foo.service", "../bar.service"),
            id="to parent dir absolute",
        ),
        pytest.param(
            (
                "/etc/systemd/system/",
                "/usr/lib/systemd/system/",
                "/etc/systemd/system/baz.wants/foo.service",
                "/dev/null",
            ),
            ("/usr/lib/systemd/system/baz.wants/foo.service", "/dev/null"),
            id="to /dev/null",
        ),
        pytest.param(
            (
                "/etc/systemd/system/",
                "/usr/lib/systemd/system/",
                "/etc/systemd/system/baz.wants/foo.service",
                "../../../../dev/null",
            ),
            ("/usr/lib/systemd/system/baz.wants/foo.service", "/dev/null"),
            id="relative /dev/null",
        ),
        pytest.param(
            (
                "/etc/systemd/system/",
                "/usr/lib/systemd/system/",
                "/etc/systemd/system/baz.wants/foo.service",
                "../../../../../../../../../../../../dev/null",
            ),
            ("/usr/lib/systemd/system/baz.wants/foo.service", "/dev/null"),
            id="relative /dev/null too many up",
        ),
    ],
)
def test_map_target_link(test_input, expected):
    """Test map_target_link."""
    cmd = systemd_cleanup
    result = cmd._map_target_link(*test_input)
    assert result == expected


# Error cases:
@pytest.mark.parametrize(
    "test_input",
    [
        pytest.param(
            (
                "/etc/systemd/system",
                "/usr/lib/systemd/system/",
                "/etc/systemd/system/baz.wants/foo.service",
                "../../../../../../../../../../../../dev/null",
            ),
            id="no old slash",
        ),
        pytest.param(
            (
                "/etc/systemd/system",
                "/usr/lib/systemd/system/",
                "/etc/systemd/system/baz.wants/foo.service",
                "../../../../../../../../../../../../dev/null",
            ),
            id="no old slash",
        ),
        pytest.param(
            (
                "/etc/systemd/system/",
                "/usr/lib/systemd/system",
                "/etc/systemd/system/baz.wants/foo.service",
                "../../../../../../../../../../../../dev/null",
            ),
            id="no new slash",
        ),
        pytest.param(
            (
                "/etc/systemd/system/",
                "/usr/lib/systemd/system",
                "/usr/lib/systemd/system/baz.wants/foo.service",
                "../../../../../../../../../../../../dev/null",
            ),
            id="link in oldbase",
        ),
    ],
)
def test_map_target_link_errors(test_input):
    """Test map_target_link with errors."""
    cmd = systemd_cleanup
    with pytest.raises(AssertionError):
        cmd._map_target_link(*test_input)


# _map_host_link:
@pytest.mark.parametrize(
    ("test_input", "expected"),
    [
        pytest.param(
            (
                "/tmp/foo/",
                "/tmp/foo/etc/systemd/system/",
                "/tmp/foo/usr/lib/systemd/system/",
                "/tmp/foo/etc/systemd/system/foo.service",
                "/etc/systemd/system/bar.service",
            ),
            ("/tmp/foo/usr/lib/systemd/system/foo.service", "bar.service"),
            id="basic",
        ),
        pytest.param(
            (
                "/tmp/foo/",
                "/tmp/foo/etc/systemd/system/",
                "/tmp/foo/usr/lib/systemd/system/",
                "/tmp/foo/etc/systemd/system/baz.wants/foo.service",
                "../bar.service",
            ),
            ("/tmp/foo/usr/lib/systemd/system/baz.wants/foo.service", "../bar.service"),
            id="to parent dir",
        ),
        pytest.param(
            (
                "/tmp/foo/",
                "/tmp/foo/etc/systemd/system/",
                "/tmp/foo/usr/lib/systemd/system/",
                "/tmp/foo/etc/systemd/system/baz.wants/foo.service",
                "/etc/systemd/system/bar.service",
            ),
            ("/tmp/foo/usr/lib/systemd/system/baz.wants/foo.service", "../bar.service"),
            id="to parent dir absolute",
        ),
        pytest.param(
            (
                "/tmp/foo/",
                "/tmp/foo/etc/systemd/system/",
                "/tmp/foo/usr/lib/systemd/system/",
                "/tmp/foo/etc/systemd/system/baz.wants/foo.service",
                "/dev/null",
            ),
            ("/tmp/foo/usr/lib/systemd/system/baz.wants/foo.service", "/dev/null"),
            id="to /dev/null",
        ),
        pytest.param(
            (
                "/tmp/foo/",
                "/tmp/foo/etc/systemd/system/",
                "/tmp/foo/usr/lib/systemd/system/",
                "/tmp/foo/etc/systemd/system/baz.wants/foo.service",
                "../../../../dev/null",
            ),
            ("/tmp/foo/usr/lib/systemd/system/baz.wants/foo.service", "/dev/null"),
            id="to relative /dev/null",
        ),
        pytest.param(
            (
                "/tmp/foo/",
                "/tmp/foo/etc/systemd/system/",
                "/tmp/foo/usr/lib/systemd/system/",
                "/tmp/foo/etc/systemd/system/baz.wants/foo.service",
                "../../../../../../../../../../../../dev/null",
            ),
            ("/tmp/foo/usr/lib/systemd/system/baz.wants/foo.service", "/dev/null"),
            id="to relative /dev/null too many ups",
        ),
    ],
)
def test_map_host_link(test_input, expected):
    """Test map_host_link."""
    cmd = systemd_cleanup
    result = cmd._map_host_link(*test_input)
    assert result == expected


# Error cases:
@pytest.mark.parametrize(
    "test_input",
    [
        pytest.param(
            (
                "/tmp/foo/",
                "/tmp/foo/etc/systemd/system",
                "/tmp/foo/usr/lib/systemd/system/",
                "/tmp/foo/etc/systemd/system/baz.wants/foo.service",
                "../../../../../../../../../../../../dev/null",
            ),
            id="no old slash",
        ),
        pytest.param(
            (
                "/tmp/foo/",
                "/tmp/foo/etc/systemd/system/",
                "/tmp/foo/usr/lib/systemd/system",
                "/tmp/foo/etc/systemd/system/baz.wants/foo.service",
                "../../../../../../../../../../../../dev/null",
            ),
            id="no new slash",
        ),
        pytest.param(
            (
                "/tmp/foo/",
                "/tmp/foo/etc/systemd/system/",
                "/tmp/foo/usr/lib/systemd/system",
                "/tmp/foo/usr/lib/systemd/system/baz.wants/foo.service",
                "../../../../../../../../../../../../dev/null",
            ),
            id="in old base",
        ),
    ],
)
def test_map_host_link_errors(test_input):
    """Test map_host_link errors."""
    cmd = systemd_cleanup
    with pytest.raises(AssertionError):
        cmd._map_host_link(*test_input)
