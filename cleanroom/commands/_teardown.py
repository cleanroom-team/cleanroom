"""_teardown command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""

import cleanroom.command as cmd

import pickle


class _TeardownCommand(cmd.Command):
    """The _teardown Command."""

    def __init__(self):
        """Constructor."""
        super().__init__("_teardown <SYSTEM>",
                         "Implicitly run after any other command of a "
                         "system is run.")

    def execute(self, run_context, args):
        """Execute command."""
        pickle_jar = run_context.pickle_jar()

        ctx = run_context.ctx
        run_context.ctx = None  # Do not pickle the context!

        ctx.printer.debug('Pickling run_context into {}.'.format(pickle_jar))

        with open(pickle_jar, 'wb') as jar:
            pickle.dump(run_context, jar, pickle.HIGHEST_PROTOCOL)

        run_context.ctx = ctx  # Restore context to run_context again!

        return super().execute(run_context, args)
