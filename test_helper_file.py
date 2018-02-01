#!/usr/bin/python
"""Test for the file helper module.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

import cleanroom.context as context
import cleanroom.exceptions as exceptions
import cleanroom.helper.generic.file as filehelper
import cleanroom.runcontext as runcontext

import unittest


class ModFileTest(unittest.TestCase):
    """Test for helper/generic/file.py."""

    def setUp(self):
        """Set up method."""
        ctx = context.Context.Create()
        ctx.set_directories('/tmp/system_dir', '/tmp/work_dir')
        self._run_context = runcontext.RunContext(ctx, 'test-system')
        self._system_dir = '/tmp/work_dir/systems/test-system/fs'

        assert(self._system_dir == self._run_context.fs_directory())

    def test_file_name(self):
        """Test absolute input file name."""
        input_file = '/root/test.txt'
        result = filehelper.file_name(self._run_context, input_file)

        self.assertEqual(result, self._system_dir + input_file)

    # Error cases:
    def test_file_name_relative(self):
        """Test relative input file name."""
        input_file = './test.txt'

        with self.assertRaises(exceptions.GenerateError):
            filehelper.file_name(self._run_context, input_file)


if __name__ == '__main__':
    unittest.main()
