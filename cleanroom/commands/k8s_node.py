# -*- coding: utf-8 -*-
"""k8s_node command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.exceptions import ParseError
from cleanroom.location import Location
from cleanroom.generator.command import Command
from cleanroom.generator.systemcontext import SystemContext

import typing


def _setup_network(location: Location, system_context: SystemContext, *,
                   cluster_name: str, cluster_id: int, node_id: int,
                   outside_match: str, cluster_match: str,
                   gateway: str, dns: str, ntp: str) -> None:
    system_context.execute(location, 'create', '/usr/lib/systemd/network/20-cbr0-bridge.netdev', '''[NetDev]
Description=Internal POD bridge
Name=cbr0
Kind=bridge
''', mode=0o644)

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
           cluster_offset=cluster_id + 128,
           node_id=node_id),
           mode=0o644)

    system_context.execute(location, 'create', '/usr/lib/systemd/network/40-cbr-outside-if.network', '''[Match]
{cluster_match}

[Network]
Description={cluster_name} pod bridge outside connectivity
Bridge=cbr0
'''.format(cluster_name=cluster_name,
           cluster_match=cluster_match),
           mode=0o644)


def _install_packages(location: Location, system_context: SystemContext) -> None:
    system_context.execute(location, 'pacman', 'docker', 'kubernetes-bin')

    # Debug packages: Remove again:
    system_context.execute(location, 'pacman', 'wget', 'net-tools', 'gnu-netcat')


def _setup_docker(location: Location, system_context: SystemContext) -> None:
    system_context.execute(location, 'mkdir', '/usr/lib/systemd/system/docker.service.d')
    system_context.execute(location, 'create', '/usr/lib/systemd/system/docker.service.d/override.conf', '''[Service]
ExecStart=
ExecStart=/usr/bin/dockerd -H fd:// \
--bridge=cb0 \
--iptables=false \
--ip-masq=false \
--insecure-registry 10.0.0.0/8
''', mode=0o644)


def _setup_kubelet(location: Location, system_context: SystemContext, *,
                   master_ip: str, node_ip: str) -> None:
    system_context.execute(location, 'create',
                           '/usr/lib/tmpfiles.d/kubelet.conf',
                           'd /var/lib/kubelet 0700 - - -', mode=0o644)

    system_context.execute(location, 'mkdir',
                           '/usr/lib/systemd/system/kubelet.service.d')
    system_context.execute(location, 'create',
                           '/usr/lib/systemd/system/kubelet.service.d/override.conf',
                           '''[Service]
EnvironmentFile=
ExecStart=
ExecStart=/usr/bin/kubelet --logtostderr=true --v=0 \
 --master={master_ip} \
 --address={node_ip} --port 10250 \
 --api-servers=http://{master_ip}:8080/
'''.format(master_ip=master_ip, node_ip=node_ip), mode=0o644)


def _setup_kube_proxy(location: Location, system_context: SystemContext, *,
                      master_ip: str) -> None:
    system_context.execute(location, 'mkdir',
                           '/usr/lib/systemd/system/kube-proxy.service.d')
    system_context.execute(location, 'create',
                           '/usr/lib/systemd/system/kube-proxy.service.d/override.conf',
                           '''[Service]
EnvironmentFile=
ExecStart=
ExecStart=/usr/bin/kube-proxy --logtostderr=true --v=0 \
 --master={master_ip} 
'''.format(master_ip=master_ip), mode=0o644)


class K8sNodeCommand(Command):
    """The k8s_node command."""

    def __init__(self) -> None:
        """Constructor."""
        super().__init__('k8s_node',
                         syntax='cluster_name=<STRING> '
                                'cluster_id=<INT> node_id=<INT> '
                                '[outside_match=<MACAddress=52:54:00:12:<cid>:<nid>>] '
                                '[cluster_match=<MACAddress=52:54:00:13:<cid>:<nid>>] '
                                '[gateway=<10.0.2.2>] [dns=<10.0.2.3>] [ntp=<10.42.0.1>]',
                         help_string='Set up cluster node network.', file=__file__)

    def validate_arguments(self, location: Location, *args: typing.Any, **kwargs: typing.Any) \
            -> typing.Optional[str]:
        """Validate the arguments."""
        self._validate_no_args(location, *args)
        self._validate_kwargs(location,
                              ('outside_match', 'cluster_match',
                               'cluster_name', 'cluster_id', 'node_id',
                               'gateway', 'dns', 'ntp'), **kwargs)
        self._require_kwargs(location,
                             ('cluster_name', 'cluster_id', 'node_id'), **kwargs)
        cluster_id = int(kwargs.get('cluster_id', -1))
        if cluster_id < 1 or cluster_id > 63:
            raise ParseError('cluster_id must be between 1 and 63',
                             location=location)
        node_id = int(kwargs.get('node_id', -1))
        if node_id < 1 or node_id > 63:
            raise ParseError('node_id must be between 1 and 63',
                             location=location)

        return None

    def __call__(self, location: Location, system_context: SystemContext,
                 *args: typing.Any, **kwargs: typing.Any) -> None:
        """Execute command."""
        cluster_name = kwargs.get('cluster_name', '')
        cluster_id = int(kwargs.get('cluster_id', -1))
        node_id = int(kwargs.get('node_id', -1))

        outside_match = kwargs.get('outside_match',
                                   'MACAddress=52:54:00:12:{:02x}:{:02x}'.
                                   format(cluster_id, node_id))
        cluster_match = kwargs.get('cluster_match',
                                   'MACAddress=52:54:00:13:{:02x}:{:02x}'.
                                   format(cluster_id, node_id))
        gateway = kwargs.get('gateway', '10.0.2.2')
        dns = kwargs.get('dns', '10.0.2.3')
        ntp = kwargs.get('ntp', '10.42.0.1')
        
        master_ip = '10.128.{cluster_id}.1'.format(cluster_id=cluster_id)
        node_ip = '10.128.{cluster_id}.{node_id}' \
            .format(cluster_id=cluster_id, node_id=node_id)

        _setup_network(location, system_context,
                       cluster_name=cluster_name,
                       cluster_id=cluster_id, node_id=node_id,
                       outside_match=outside_match, cluster_match=cluster_match,
                       gateway=gateway, dns=dns, ntp=ntp)

        _install_packages(location, system_context)

        _setup_docker(location, system_context)

        _setup_kubelet(location, system_context, master_ip=master_ip, node_ip=node_ip)
        _setup_kube_proxy(location, system_context, master_ip=master_ip)
