import cleanroom.command as cmd

class RunCommand(cmd.Command):

    def __init__(self, ctx):
        super().__init__()
        self._ctx = ctx

    def execute(self, *args):
        self._ctx.printer.print('Run:', *args)
