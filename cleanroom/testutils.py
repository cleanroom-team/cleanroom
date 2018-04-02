# -*- coding: utf-8 -*-
"""Test infrastructure for cleanroom tests.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.context as context
import cleanroom.parser as parser
import cleanroom.printer as printer


class TestCommand(cmd.Command):
    """Dummy command implementation."""

    pass


class BaseParserTest:
    """Test for Parser class of cleanroom."""

    def _create_and_setup_parser(self, verbosity=0):
        """Set up method."""
        printer.Printer(verbosity)
        self.ctx = context.Context()
        parser.Parser.find_commands(self.ctx.commands_directory())
        self.parser = parser.Parser()
        parser.Parser._commands['_setup'] \
            = (TestCommand('_setup', help='placeholder'), '<placeholder>')
        parser.Parser._commands['_teardown'] \
            = (TestCommand('_teardown', help='placeholder'), '<placeholder>')

    def _parse(self, data):
        """Call Parser._parse_lines and map the result."""
        input = (data,) if type(data) is str else data
        return list(map(lambda x: (x.command(), x.arguments(),
                                   x.kwargs(), x.location().line_number),
                        self.parser._parse_lines(input, '<TEST_DATA>')))

    def _verify(self, data, expected):
        """Verify one line of input to the Parser."""
        result = self._parse(data)
        self.assertTrue(len(result) >= 2)
        self.assertEqual(result[0], ('_setup', (), {}, 1))
        self.assertEqual(result[-1], ('_teardown', (), {}, 1))
        self.assertEqual(result[1:-1], expected)
