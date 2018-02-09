#!/usr/bin/python
"""Test infrastructure for cleanroom tests.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from . import context
from . import parser
from . import command as cmd


class TestCommand(cmd.Command):
    """Dummy command implementation."""

    pass


class BaseParserTest:
    """Test for Parser class of cleanroom."""

    def _create_and_setup_parser(self, verbosity=0):
        """Set up method."""
        self.ctx = context.Context.Create(verbosity)
        self.parser = parser.Parser(self.ctx)
        parser.Parser._commands['_setup'] \
            = (TestCommand('_setup', 'placeholder'), '<placeholder>')
        parser.Parser._commands['_teardown'] \
            = (TestCommand('_setup', 'placeholder'), '<placeholder>')

    def _parse(self, data):
        """Call Parser._parse_lines and map the result."""
        input = (data,) if type(data) is str else data
        return list(map(lambda x: (x._name, x._args, x._kwargs),
                        self.parser._parse_lines(input, '<TEST_DATA>')))

    def _verify(self, data, expected):
        """Verify one line of input to the Parser."""
        result = self._parse(data)
        self.assertTrue(len(result) >= 2)
        self.assertEqual(result[0], ('_setup', (), {}))
        self.assertEqual(result[-1], ('_teardown', (), {}))
        self.assertEqual(result[1:-1], expected)
