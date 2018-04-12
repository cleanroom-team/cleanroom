#!/usr/bin/python
"""Test for the built-in commands of cleanroom.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import cleanroom.commands.systemd_cleanup as systemd_cleanup

import unittest


class SystemdCleanupCommandTest(unittest.TestCase):
    """Test for systemd_cleanup command."""

    # _map_base:
    def test_map_base(self):
        """Test mapping a path to the new base."""
        cmd = systemd_cleanup.SystemdCleanupCommand()
        result = cmd._map_base('/etc/systemd/system/',
                               '/usr/lib/systemd/system/',
                               '/etc/systemd/system/test')
        self.assertEqual(result, ('/usr/lib/systemd/system/test',
                                  '/etc/systemd/system/test'))

    def test_map_base_elsewhere(self):
        """Test mapping a path from elsewhere to itself."""
        cmd = systemd_cleanup.SystemdCleanupCommand()
        result = cmd._map_base('/etc/systemd/system/',
                               '/usr/lib/systemd/system/',
                               '/tmp/test')
        self.assertEqual(result, ('/tmp/test', '/tmp/test'))

    def test_map_base_test_paths(self):
        """Test mapping a path from test paths."""
        cmd = systemd_cleanup.SystemdCleanupCommand()
        result = cmd._map_base('/foo/bar/',
                               '/foo/baz/bar/',
                               '/foo/bar/baz/test')
        self.assertEqual(result,
                         ('/foo/baz/bar/baz/test', '/foo/bar/baz/test'))

    def test_map_base_relative_paths(self):
        """Test mapping a path from test paths."""
        cmd = systemd_cleanup.SystemdCleanupCommand()
        result = cmd._map_base('/foo/bar/',
                               '/foo/baz/bar/',
                               '/foo/bar/baz/../test')
        self.assertEqual(result,
                         ('/foo/baz/bar/test', '/foo/bar/test'))

    def test_map_base_relative_paths_outside_base(self):
        """Test mapping a path from test paths."""
        cmd = systemd_cleanup.SystemdCleanupCommand()
        result = cmd._map_base('/foo/bar/',
                               '/foo/baz/bar/',
                               '/foo/bar/baz/../../test')
        self.assertEqual(result,
                         ('/foo/test', '/foo/test'))

    # _map_target_link:
    def test_map_target_link(self):
        """Test mapping a target symlink."""
        cmd = systemd_cleanup.SystemdCleanupCommand()
        result = cmd._map_target_link(
                    '/etc/systemd/system/',
                    '/usr/lib/systemd/system/',
                    '/etc/systemd/system/foo.service',
                    '/etc/systemd/system/bar.service')
        self.assertEqual(result,
                         ('/usr/lib/systemd/system/foo.service',
                          'bar.service'))

    def test_map_target_link_to_parent_dir(self):
        """Test mapping a target symlink to a parent dir."""
        cmd = systemd_cleanup.SystemdCleanupCommand()
        result = cmd._map_target_link(
                    '/etc/systemd/system/',
                    '/usr/lib/systemd/system/',
                    '/etc/systemd/system/baz.wants/foo.service',
                    '../bar.service')
        self.assertEqual(result,
                         ('/usr/lib/systemd/system/baz.wants/foo.service',
                          '../bar.service'))

    def test_map_target_link_to_parent_dir_absolute(self):
        """Test mapping a target symlink to a parent dir (absolute)."""
        cmd = systemd_cleanup.SystemdCleanupCommand()
        result = cmd._map_target_link(
                    '/etc/systemd/system/',
                    '/usr/lib/systemd/system/',
                    '/etc/systemd/system/baz.wants/foo.service',
                    '/etc/systemd/system/bar.service')
        self.assertEqual(result,
                         ('/usr/lib/systemd/system/baz.wants/foo.service',
                          '../bar.service'))

    def test_map_target_link_to_dev_null(self):
        """Test mapping a target symlink to dev_null."""
        cmd = systemd_cleanup.SystemdCleanupCommand()
        result = cmd._map_target_link(
                    '/etc/systemd/system/',
                    '/usr/lib/systemd/system/',
                    '/etc/systemd/system/baz.wants/foo.service',
                    '/dev/null')
        self.assertEqual(result,
                         ('/usr/lib/systemd/system/baz.wants/foo.service',
                          '/dev/null'))

    def test_map_target_link_to_relative_dev_null(self):
        """Test mapping a target symlink to dev_null."""
        cmd = systemd_cleanup.SystemdCleanupCommand()
        result = cmd._map_target_link(
                    '/etc/systemd/system/',
                    '/usr/lib/systemd/system/',
                    '/etc/systemd/system/baz.wants/foo.service',
                    '../../../../dev/null')
        self.assertEqual(result,
                         ('/usr/lib/systemd/system/baz.wants/foo.service',
                          '/dev/null'))

    def test_map_target_link_to_relative_dev_null_too_many_ups(self):
        """Test mapping a target symlink to dev_null."""
        cmd = systemd_cleanup.SystemdCleanupCommand()
        result = cmd._map_target_link(
                    '/etc/systemd/system/',
                    '/usr/lib/systemd/system/',
                    '/etc/systemd/system/baz.wants/foo.service',
                    '../../../../../../../../../../../../dev/null')
        self.assertEqual(result,
                         ('/usr/lib/systemd/system/baz.wants/foo.service',
                          '/dev/null'))

    # Error cases:
    def test_map_target_link_assert_on_no_old_slash(self):
        """Test mapping a target link without old_base ending in slash."""
        cmd = systemd_cleanup.SystemdCleanupCommand()
        with self.assertRaises(AssertionError):
            cmd._map_target_link(
                '/etc/systemd/system',
                '/usr/lib/systemd/system/',
                '/etc/systemd/system/baz.wants/foo.service',
                '../../../../../../../../../../../../dev/null')

    def test_map_target_link_assert_on_no_new_slash(self):
        """Test mapping a target link without new_base ending in slash."""
        cmd = systemd_cleanup.SystemdCleanupCommand()
        with self.assertRaises(AssertionError):
            cmd._map_target_link(
                '/etc/systemd/system/',
                '/usr/lib/systemd/system',
                '/etc/systemd/system/baz.wants/foo.service',
                '../../../../../../../../../../../../dev/null')

    def test_map_target_link_assert_on_link_in_oldbase(self):
        """Test mapping a target link without new_base ending in slash."""
        cmd = systemd_cleanup.SystemdCleanupCommand()
        with self.assertRaises(AssertionError):
            cmd._map_target_link(
                '/etc/systemd/system/',
                '/usr/lib/systemd/system',
                '/usr/lib/systemd/system/baz.wants/foo.service',
                '../../../../../../../../../../../../dev/null')

    # _map_host_link:
    def test_map_host_link(self):
        """Test mapping a target symlink."""
        cmd = systemd_cleanup.SystemdCleanupCommand()
        result = cmd._map_host_link(
                    '/tmp/foo/',
                    '/tmp/foo/etc/systemd/system/',
                    '/tmp/foo/usr/lib/systemd/system/',
                    '/tmp/foo/etc/systemd/system/foo.service',
                    '/etc/systemd/system/bar.service')
        self.assertEqual(result,
                         ('/tmp/foo/usr/lib/systemd/system/foo.service',
                          'bar.service'))

    def test_map_host_link_to_parent_dir(self):
        """Test mapping a target symlink to a parent dir."""
        cmd = systemd_cleanup.SystemdCleanupCommand()
        result = cmd._map_host_link(
                    '/tmp/foo/',
                    '/tmp/foo/etc/systemd/system/',
                    '/tmp/foo/usr/lib/systemd/system/',
                    '/tmp/foo/etc/systemd/system/baz.wants/foo.service',
                    '../bar.service')
        self.assertEqual(result,
                         ('/tmp/foo/usr/lib/systemd/system/baz.wants/foo.service',
                          '../bar.service'))

    def test_map_host_link_to_parent_dir_absolute(self):
        """Test mapping a target symlink to a parent dir (absolute)."""
        cmd = systemd_cleanup.SystemdCleanupCommand()
        result = cmd._map_host_link(
                    '/tmp/foo/',
                    '/tmp/foo/etc/systemd/system/',
                    '/tmp/foo/usr/lib/systemd/system/',
                    '/tmp/foo/etc/systemd/system/baz.wants/foo.service',
                    '/etc/systemd/system/bar.service')
        self.assertEqual(result,
                         ('/tmp/foo/usr/lib/systemd/system/baz.wants/foo.service',
                          '../bar.service'))

    def test_map_host_link_to_dev_null(self):
        """Test mapping a target symlink to dev_null."""
        cmd = systemd_cleanup.SystemdCleanupCommand()
        result = cmd._map_host_link(
                    '/tmp/foo/',
                    '/tmp/foo/etc/systemd/system/',
                    '/tmp/foo/usr/lib/systemd/system/',
                    '/tmp/foo/etc/systemd/system/baz.wants/foo.service',
                    '/dev/null')
        self.assertEqual(result,
                         ('/tmp/foo/usr/lib/systemd/system/baz.wants/foo.service',
                          '/dev/null'))

    def test_map_host_link_to_relative_dev_null(self):
        """Test mapping a target symlink to dev_null."""
        cmd = systemd_cleanup.SystemdCleanupCommand()
        result = cmd._map_host_link(
                    '/tmp/foo/',
                    '/tmp/foo/etc/systemd/system/',
                    '/tmp/foo/usr/lib/systemd/system/',
                    '/tmp/foo/etc/systemd/system/baz.wants/foo.service',
                    '../../../../dev/null')
        self.assertEqual(result,
                         ('/tmp/foo/usr/lib/systemd/system/baz.wants/foo.service',
                          '/dev/null'))

    def test_map_host_link_to_relative_dev_null_too_many_ups(self):
        """Test mapping a target symlink to dev_null."""
        cmd = systemd_cleanup.SystemdCleanupCommand()
        result = cmd._map_host_link(
                    '/tmp/foo/',
                    '/tmp/foo/etc/systemd/system/',
                    '/tmp/foo/usr/lib/systemd/system/',
                    '/tmp/foo/etc/systemd/system/baz.wants/foo.service',
                    '../../../../../../../../../../../../dev/null')
        self.assertEqual(result,
                         ('/tmp/foo/usr/lib/systemd/system/baz.wants/foo.service',
                          '/dev/null'))

    # Error cases:
    def test_map_host_link_assert_on_no_old_slash(self):
        """Test mapping a target link without old_base ending in slash."""
        cmd = systemd_cleanup.SystemdCleanupCommand()
        with self.assertRaises(AssertionError):
            cmd._map_host_link(
                '/tmp/foo/',
                '/tmp/foo/etc/systemd/system',
                '/tmp/foo/usr/lib/systemd/system/',
                '/tmp/foo/etc/systemd/system/baz.wants/foo.service',
                '../../../../../../../../../../../../dev/null')

    def test_map_host_link_assert_on_no_new_slash(self):
        """Test mapping a target link without new_base ending in slash."""
        cmd = systemd_cleanup.SystemdCleanupCommand()
        with self.assertRaises(AssertionError):
            cmd._map_host_link(
                '/tmp/foo/',
                '/tmp/foo/etc/systemd/system/',
                '/tmp/foo/usr/lib/systemd/system',
                '/tmp/foo/etc/systemd/system/baz.wants/foo.service',
                '../../../../../../../../../../../../dev/null')

    def test_map_host_link_assert_on_link_in_oldbase(self):
        """Test mapping a target link without new_base ending in slash."""
        cmd = systemd_cleanup.SystemdCleanupCommand()
        with self.assertRaises(AssertionError):
            cmd._map_host_link(
                '/tmp/foo/',
                '/tmp/foo/etc/systemd/system/',
                '/tmp/foo/usr/lib/systemd/system',
                '/tmp/foo/usr/lib/systemd/system/baz.wants/foo.service',
                '../../../../../../../../../../../../dev/null')


if __name__ == '__main__':
    unittest.main()
