# -*- coding: utf-8 -*-
"""k8s_node command.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


from cleanroom.command import Command
from cleanroom.exceptions import ParseError
from cleanroom.helper.file import create_file
from cleanroom.location import Location
from cleanroom.systemcontext import SystemContext

import os
import textwrap
import typing


def _setup_network(
    location: Location,
    system_context: SystemContext,
    *,
    cluster_name: str,
    cluster_id: int,
    node_id: int,
    outside_match: str,
    cluster_match: str,
    gateway: str,
    dns: str,
    ntp: str,
) -> None:
    create_file(
        system_context,
        "/usr/lib/systemd/network/20-cbr0-bridge.netdev",
        textwrap.dedent(
            """\
                [NetDev]
                Description=Internal POD bridge
                Name=cbr0
                Kind=bridge
                """
        ).encode("utf-8"),
        mode=0o644,
    )

    create_file(
        system_context,
        "/usr/lib/systemd/network/10-extern.network",
        textwrap.dedent(
            f"""\
                [Match]
                {outside_match}
                
                [Network]
                Description=Node network
                Address=10.128.{cluster_id}.{node_id}/8
                Gateway={gateway}
                DNS={dns}
                NTP={ntp}
                IPForward=yes
                IPMasquerade=yes
                """
        ).encode("utf-8"),
        mode=0o644,
    )

    create_file(
        system_context,
        "/usr/lib/systemd/network/30-cbr.network",
        textwrap.dedent(
            f"""\
                [Match]
                Name=cbr0
                
                [Network]
                Description={cluster_name} pod bridge setup
                Address=10.{cluster_offset}.{node_id}.1/16
                """
        ).encode("utf-8"),
        mode=0o644,
    )

    create_file(
        system_context,
        "/usr/lib/systemd/network/40-cbr-outside-if.network",
        textwrap.dedent(
            f"""\
                [Match]
                {cluster_match}
                
                [Network]
                Description={cluster_name} pod bridge outside connectivity
                Bridge=cbr0
                """
        ).encode("utf-8"),
        mode=0o644,
    )


def _setup_docker(location: Location, system_context: SystemContext) -> None:
    os.makedirs(system_context.file_name("/usr/lib/systemd/system/docker.service.d"))
    create_file(
        system_context,
        "/usr/lib/systemd/system/docker.service.d/override.conf",
        textwrap.dedent(
            """\
                [Service]
                ExecStart=
                ExecStart=/usr/bin/dockerd -H fd:// \\
                    --bridge=cb0 \\
                    --iptables=false \\
                    --ip-masq=false \\
                    --insecure-registry 10.0.0.0/8
                """
        ).encode("utf-8"),
        mode=0o644,
    )


def _setup_kubelet(
    location: Location, system_context: SystemContext, *, master_ip: str, node_ip: str
) -> None:
    create_file(
        system_context,
        "/usr/lib/tmpfiles.d/kubelet.conf",
        "d /var/lib/kubelet 0700 - - -".encode("utf-8"),
        mode=0o644,
    )

    os.makedirs("/usr/lib/systemd/system/kubelet.service.d")
    create_file(
        system_context,
        "/usr/lib/systemd/system/kubelet.service.d/override.conf",
        textwrap.dedent(
            f"""\
                [Service]
                EnvironmentFile=
                ExecStart=
                ExecStart=/usr/bin/kubelet --logtostderr=true --v=0 \\
                    --master={master_ip} \\
                    --address={node_ip} --port 10250 \\
                    --api-servers=http://{master_ip}:8080/
                """
        ).encode("utf-8"),
        mode=0o644,
    )


def _setup_kube_proxy(
    location: Location, system_context: SystemContext, *, master_ip: str
) -> None:
    os.makedirs("/usr/lib/systemd/system/kube-proxy.service.d")
    create_file(
        system_context,
        "/usr/lib/systemd/system/kube-proxy.service.d/override.conf",
        textwrap.dedent(
            f"""\
                [Service]
                EnvironmentFile=
                ExecStart=
                ExecStart=/usr/bin/kube-proxy --logtostderr=true --v=0 \\
                    --master={master_ip} 
                """
        ).encode("utf-8"),
        mode=0o644,
    )


class K8sNodeCommand(Command):
    """The k8s_node command."""

    def __init__(self, **services: typing.Any) -> None:
        """Constructor."""
        super().__init__(
            "k8s_node",
            syntax="cluster_name=<STRING> "
            "cluster_id=<INT> node_id=<INT> "
            "[outside_match=<MACAddress=52:54:00:12:<cid>:<nid>>] "
            "[cluster_match=<MACAddress=52:54:00:13:<cid>:<nid>>] "
            "[gateway=<10.0.2.2>] [dns=<10.0.2.3>] [ntp=<10.42.0.1>]",
            help_string="Set up cluster node network.",
            file=__file__,
            **services,
        )

    def validate(
        self, location: Location, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        """Validate the arguments."""
        self._validate_no_args(location, *args)
        self._validate_kwargs(
            location,
            (
                "outside_match",
                "cluster_match",
                "cluster_name",
                "cluster_id",
                "node_id",
                "gateway",
                "dns",
                "ntp",
            ),
            **kwargs,
        )
        self._require_kwargs(
            location, ("cluster_name", "cluster_id", "node_id"), **kwargs
        )
        cluster_id = int(kwargs.get("cluster_id", -1))
        if cluster_id < 1 or cluster_id > 63:
            raise ParseError("cluster_id must be between 1 and 63", location=location)
        node_id = int(kwargs.get("node_id", -1))
        if node_id < 1 or node_id > 63:
            raise ParseError("node_id must be between 1 and 63", location=location)

    def __call__(
        self,
        location: Location,
        system_context: SystemContext,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> None:
        """Execute command."""
        cluster_name = kwargs.get("cluster_name", "")
        cluster_id = int(kwargs.get("cluster_id", -1))
        node_id = int(kwargs.get("node_id", -1))

        outside_match = kwargs.get(
            "outside_match",
            f"MACAddress=52:54:00:12:{cluster_id:02x}:{node_id:02x}",
        )
        cluster_match = kwargs.get(
            "cluster_match",
            f"MACAddress=52:54:00:13:{cluster_id:02x}:{node_id:02x}",
        )
        gateway = kwargs.get("gateway", "10.0.2.2")
        dns = kwargs.get("dns", "10.0.2.3")
        ntp = kwargs.get("ntp", "10.42.0.1")

        master_ip = f"10.128.{cluster_id}.1"
        node_ip = f"10.128.{cluster_id}.{node_id}"

        _setup_network(
            location,
            system_context,
            cluster_name=cluster_name,
            cluster_id=cluster_id,
            node_id=node_id,
            outside_match=outside_match,
            cluster_match=cluster_match,
            gateway=gateway,
            dns=dns,
            ntp=ntp,
        )

        self._install_packages(location, system_context)

        _setup_docker(location, system_context)

        _setup_kubelet(location, system_context, master_ip=master_ip, node_ip=node_ip)
        _setup_kube_proxy(location, system_context, master_ip=master_ip)

    def _install_packages(
        self, location: Location, system_context: SystemContext
    ) -> None:
        self._execute(location, system_context, "pacman", "docker", "kubernetes-bin")

        # Debug packages: Remove again:
        self._execute(
            location, system_context, "pacman", "wget", "net-tools", "gnu-netcat"
        )
