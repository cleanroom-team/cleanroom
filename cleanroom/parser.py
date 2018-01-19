#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import importlib.util
import inspect
import os


class Parser:
    ''' Parse a container.conf file '''

    _commands = {}
    ''' A list of known commands '''

    @staticmethod
    def find_commands(ctx):
        ctx.printer.trace('Checking for commands.')
        checked_dirs = []
        for path in ( ctx.systemsCommandsDirectory(), ctx.commandsDirectory()):
            if path in checked_dirs:
                continue
            checked_dirs.append(path)
            ctx.printer.trace('Checking "{}" for command files.'.format(path))
            for f in os.listdir(path):
                if not f.endswith('.py'):
                   continue

                f_path = os.path.join(path, f)
                ctx.printer.trace('Found file: {}'.format(f_path))

                cmd = f[:-3]
                name = 'cr_cmd_' + cmd + '.py'

                spec = importlib.util.spec_from_file_location(name, f_path)
                cmd_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(cmd_module)

                predicate = lambda x : inspect.isclass(x) and \
                                       x.__name__.endswith('Command') and \
                                       x.__module__ == name
                klass = inspect.getmembers(cmd_module, predicate)
                print(klass)
                instance = klass[0][1](ctx)
                print(instance)
                Parser._commands[cmd] = instance

    def __init__(self, ctx, system):
        self._ctx = ctx

        self._ctx.printer.verbose('    Parser created for {}...'.format(system))

