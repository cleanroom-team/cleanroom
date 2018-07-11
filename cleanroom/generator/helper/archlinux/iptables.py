# -*- coding: utf-8 -*-
"""Generic support for iptables firewall management.

@author: Tobias Hunger <tobias.hunger@gmail.com>
"""


_TCP_MAGIC = '#### Allowed TCP ports:'
_UDP_MAGIC = '#### Allowed UDP ports:'

_IPv4_RULES = '/etc/iptables/iptables.rules'
_IPv6_RULES = '/etc/iptables/ip6tables.rules'


def install_rules(location, system_context):
    """Install basic firewall rules."""
    assert(firewall_type(system_context) is None)
    set_firewall_type(system_context)

    _install_v4_rules(location, system_context, _IPv4_RULES)
    _install_v6_rules(location, system_context, _IPv6_RULES)


def enable_firewall(location, system_context):
    """Enable the firewall."""
    # FIXME: Fix systemd install section to run iptables services earlier!
    assert(firewall_type(system_context) == 'iptables')
    location.set_description('Enable firewall')
    system_context.execute(location, 'systemd_enable',
                           'iptables.service', 'ip6tables.service')


def firewall_type(system_context):
    """Get type of firewall or None if none is active."""
    return system_context.substitution('CLRM_FIREWALL', None)


def set_firewall_type(system_context):
    """Set the type of firewall."""
    system_context.set_substitution('CLRM_FIREWALL', 'iptables')


def open_port(location, system_context, port, protocol='tcp', comment=None):
    """Open a port in the firewall."""
    magic = _TCP_MAGIC if protocol == 'tcp' else _UDP_MAGIC
    output = '-A {0} -p {1} -m {1} --dport {2} -j ACCEPT' \
             .format(protocol.upper(), protocol, port)
    if comment is not None:
        output += ' ### {}'.format(comment)

    pattern = '/{}/ a{}'.format(magic, output)
    location.set_description('Open IPv4 port')
    system_context.execute(location, 'sed', pattern, _IPv4_RULES)
    location.set_description('Open IPv6 port')
    system_context.execute(location, 'sed', pattern, _IPv6_RULES)


def _install_v4_rules(location, system_context, rule_file):
    location.set_description('Install IPv4 rules')
    system_context.execute(location, 'create', rule_file, """
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

{}

{}

COMMIT
""".format(_TCP_MAGIC, _UDP_MAGIC))
    location.set_description('Chmod IPv4 rules')
    system_context.execute(location, 'chmod', 0o644, rule_file)


def _install_v6_rules(location, system_context, rule_file):
    location.set_description('Install IPv6 rules')
    system_context.execute(location, 'create', rule_file, """
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

{}

{}

COMMIT
""".format(_TCP_MAGIC, _UDP_MAGIC))
    location.set_description('Chmod IPv6 rules')
    system_context.execute(location, 'chmod', 0o644, rule_file)
