"""net_firewall_iptables command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.command as cmd
import cleanroom.exceptions as ex
import cleanroom.helper.archlinux.iptables as fw


class MoveCommand(cmd.Command):
    """The net_firewall_iptables command."""

    def __init__(self):
        """Constructor."""
        super().__init__('net_firewall_iptables',
                         'Set up basic iptables firewall.')

    def validate_arguments(self, run_context, *args, **kwargs):
        """Validate the arguments."""
        if len(args) > 0:
            raise ex.ParseError('net_firewall_iptables does not take '
                                'arguments.', run_context=run_context)

        return None

    def __call__(self, run_context, *args, **kwargs):
        """Execute command."""
        fw.install(run_context)
