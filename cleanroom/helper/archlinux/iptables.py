# -*- coding: utf-8 -*-
"""Generic support for iptables firewall management.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


import cleanroom.helper.archlinux.pacman as arch


def install(system_context):
    """Install basic firewall rules."""
    assert(_firewall_type(system_context) is None)
    _set_firewall_type(system_context)

    _install_packages(system_context)

    _install_v4_rules(system_context, '/etc/iptables/iptables.rules')
    _install_v6_rules(system_context, '/etc/iptables/ip6tables.rules')

    # FIXME: Fix systemd install section to run iptables services earlier!

    system_context.execute('systemd_enable',
                           'iptables.service', 'ip6tables.service')


def _install_packages(system_context):
    arch.pacman(system_context, 'iptables')


def _firewall_type(system_context):
    return system_context.substituion('CLRM_FIREWALL', None)


def _set_firewall_type(system_context):
    system_context.set_substitution('CLRM_FIREWALL', 'iptables')


def _install_v4_rules(system_context, rule_file):
    system_context.execute('create', rule_file, """
# iptables rules:

*filter
:INPUT DROP [0:0]
:FORWARD DROP [0:0]
:OUTPUT ACCEPT [66:5016]
:TCP - [0:0]
:UDP - [0:0]
:LOGDROP - [0:0]

-A LOGDROP -m limit --limit 5/m --limit-burst 10 -j LOG
-A LOGDROP -j DROP

-A FORWARD -m physdev --physdev-is-bridged -j ACCEPT
#### Custom FORWARD rules:

-A FORWARD -j LOGDROP

-A INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
-A INPUT -i lo -j ACCEPT
-A INPUT -m conntrack --ctstate INVALID -j DROP
-A INPUT -p icmp -m icmp --icmp-type 8 -m conntrack --ctstate NEW -j ACCEPT
-A INPUT -p udp --dport 67:68 --sport 67:68 -j ACCEPT
-A INPUT -p udp -m conntrack --ctstate NEW -j UDP
-A INPUT -p tcp -m conntrack --ctstate NEW -j TCP
-A INPUT -p udp -j REJECT --reject-with icmp-port-unreachable
-A INPUT -p tcp -j REJECT --reject-with tcp-reset
-A INPUT -j REJECT --reject-with icmp-proto-unreachable
-A INPUT -j LOGDROP

-A OUTPUT -p udp --dport 67:68 --sport 67:68 -j ACCEPT

#### Allowed TCP ports:

#### Allowed UDP ports:

COMMIT
""")
    system_context.execute('chmod', 0o644, rule_file)


def _install_v6_rules(self, system_context, rule_file):
    system_context.execute('create', rule_file, """
# ip6tables rules:

*filter
:INPUT DROP [0:0]
:FORWARD DROP [0:0]
:OUTPUT ACCEPT [0:0]

:TCP - [0:0]
:UDP - [0:0]
:LOGDROP - [0:0]

-A LOGDROP -m limit --limit 5/m --limit-burst 10 -j LOG
-A LOGDROP -j DROP

-A FORWARD -m physdev --physdev-is-bridged -j ACCEPT
#### Custom FORWARD rules:

-A FORWARD -j LOGDROP

-A INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
-A INPUT -i lo -j ACCEPT
-A INPUT -m conntrack --ctstate INVALID -j DROP
-A INPUT -p icmpv6 -j ACCEPT
-A INPUT -p udp --dport 67:68 --sport 67:68 -j ACCEPT
-A INPUT -p udp -m conntrack --ctstate NEW -j UDP
-A INPUT -p tcp -m conntrack --ctstate NEW -j TCP
-A INPUT -p udp -j REJECT --reject-with icmp6-port-unreachable
-A INPUT -p tcp -j REJECT --reject-with tcp-reset
-A INPUT -j REJECT --reject-with icmp6-port-unreachable
-A INPUT -j LOGDROP

-A OUTPUT -p udp --dport 67:68 --sport 67:68 -j ACCEPT

#### Allowed TCP ports:

#### Allowed UDP ports:

COMMIT
""")
    system_context.execute('chmod', 0o644, rule_file)
