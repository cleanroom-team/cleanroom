# -*- coding: utf-8 -*-
"""k8s_node_network command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.generator.command import Command

from cleanroom.exceptions import ParseError


class K8sNodeNetworkCommand(Command):
    """The k8s_node_network command."""

    def __init__(self):
        """Constructor."""
        super().__init__('k8s_node_network',
                         syntax='cluster_name=<STRING> '
                            'cluster_id=<INT> node_id=<INT> '
                            '[outside_match=<MACAddress=52:54:00:12:<cid>:<nid>>] '
                            '[cluster_match=<MACAddress=52:54:00:13:<cid>:<nid>>] '
                            '[gateway=<10.0.2.2>] [dns=<10.0.2.3>] [ntp=<10.42.0.1>]',
                         help='Set up cluster node network.', file=__file__)

    def validate_arguments(self, location, *args, **kwargs):
        """Validate the arguments."""
        self._validate_no_args(location, *args)
        self._validate_kwargs(location,
                              ('outside_match', 'cluster_match',
                               'cluster_name', 'cluster_id', 'node_id',
                               'gateway', 'dns', 'ntp'), **kwargs)
        self._require_kwargs(location,
                             ('cluster_name', 'cluster_id', 'node_id'), **kwargs)
        cluster_id = int(kwargs.get('cluster_id'))
        if (cluster_id < 1 or cluster_id > 63):
            raise ParseError('cluster_id must be between 1 and 63',
                             location=location)
        node_id = int(kwargs.get('node_id'))
        if (node_id < 1 or node_id > 63):
            raise ParseError('node_id must be between 1 and 63',
                             location=location)

    def __call__(self, location, system_context, *args, **kwargs):
        """Execute command."""
        cluster_name = kwargs['cluster_name']
        cluster_id = kwargs['cluster_id']
        node_id = kwargs['node_id']

        outside_match = kwargs.get('outside_match',
                                   'MACAddress=52:54:00:12:{:02x}:{:02x}'.
                                   format(cluster_id, node_id))
        cluster_match = kwargs.get('cluster_match',
                                   'MACAddress=52:54:00:13:{:02x}:{:02x}'.
                                   format(cluster_id, node_id))
        gateway = kwargs.get('gateway', '10.0.2.2')
        dns = kwargs.get('dns', '10.0.2.3')
        ntp = kwargs.get('ntp', '10.42.0.1')
        
        system_context.execute(location, 'create', '/usr/lib/systemd/network/10-extern.network', '''[Match]
{outside_match}

[Network]
Description=Node network
Address=10.128.{cluster_id}.{node_id}/8
Gateway={gateway}
DNS={dns}
NTP={ntp}
IPForward=yes
IPMasquerade=yes
'''.format(outside_match=outside_match,
           cluster_id=cluster_id, node_id=node_id,
           gateway=gateway, dns=dns, ntp=ntp),
            mode=0o644)

        system_context.execute(location, 'create', '/usr/lib/systemd/network/30-cbr.network', '''[Match]
Name=cbr0

[Network]
Description={cluster_name} pod bridge setup
Address=10.{cluster_offset}.{node_id}.1/16
'''.format(cluster_name=cluster_name,
           cluster_offset=cluster_id + 128, node_id=node_id),
            mode=0o644)
            
        system_context.execute(location, 'create', '/usr/lib/systemd/network/40-cbr-outside-if.network', '''[Match]
{cluster_match}

[Network]
Description={cluster_name} pod bridge outside connectivity
Bridge=cbr0
'''.format(cluster_name=cluster_name, cluster_match=cluster_match),
           mode=0o644)
