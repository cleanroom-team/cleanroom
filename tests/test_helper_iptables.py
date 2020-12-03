#!/usr/bin/python

# """Test for the built-in print_commands of cleanroom.
#
# @author: Tobias Hunger <tobias.hunger@gmail.com>
# """


import pytest  # type: ignore

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cleanroom.exceptions import GenerateError
import cleanroom.helper.archlinux.iptables as ipt


def _validate_rules_files(system_context, *extra_matches) -> None:
    _validate_rules_file(
        system_context.file_name("/etc/iptables/iptables.rules"), *extra_matches
    )
    _validate_rules_file(
        system_context.file_name("/etc/iptables/ip6tables.rules"), *extra_matches
    )


def _validate_rules_file(file_name: str, *extra_matches) -> None:
    assert os.path.isfile(file_name)

    with open(file_name, "r") as rules_fd:
        rules_contents = rules_fd.read()

    print(f"Contents: {rules_contents}<<<<<")

    for match in (*extra_matches, ipt._FORWARD_MAGIC, ipt._TCP_MAGIC, ipt._UDP_MAGIC):
        assert ("\n" + match + "\n") in rules_contents


def test_create_iptables_rules(location, system_context):
    ipt.install_rules(location, system_context)

    _validate_rules_files(
        system_context, "-A FORWARD -j LOGDROP", "-A INPUT -j LOGDROP", "COMMIT"
    )


def test_open_port_default(location, system_context):
    ipt.install_rules(location, system_context)

    ipt.open_port(system_context, 4242, comment="test port")

    _validate_rules_files(
        system_context, "# test port:", "-A TCP -p tcp -m tcp --dport 4242 -j ACCEPT"
    )


def test_open_port_tcp(location, system_context):
    ipt.install_rules(location, system_context)

    ipt.open_port(system_context, 4242, protocol="tcp", comment="test port")

    _validate_rules_files(
        system_context, "# test port:", "-A TCP -p tcp -m tcp --dport 4242 -j ACCEPT"
    )


def test_open_port_udp(location, system_context):
    ipt.install_rules(location, system_context)

    ipt.open_port(system_context, 4242, protocol="udp", comment="test port")

    _validate_rules_files(
        system_context, "# test port:", "-A UDP -p udp -m udp --dport 4242 -j ACCEPT"
    )


def test_open_port_default_no_comment(location, system_context):
    ipt.install_rules(location, system_context)

    ipt.open_port(system_context, 4242)

    _validate_rules_files(system_context, "-A TCP -p tcp -m tcp --dport 4242 -j ACCEPT")


def test_open_port_tcp_no_comment(location, system_context):
    ipt.install_rules(location, system_context)

    ipt.open_port(system_context, 4242, protocol="tcp", comment="test port")

    _validate_rules_files(system_context, "-A TCP -p tcp -m tcp --dport 4242 -j ACCEPT")


def test_open_port_udp_no_comment(location, system_context):
    ipt.install_rules(location, system_context)

    ipt.open_port(system_context, 4242, protocol="udp")

    _validate_rules_files(system_context, "-A UDP -p udp -m udp --dport 4242 -j ACCEPT")


def test_interface_forward(location, system_context):
    ipt.install_rules(location, system_context)

    ipt.forward_interface(system_context, "ve-testiface", comment="test iface")

    _validate_rules_files(
        system_context,
        "# test iface:",
        "-A FORWARD -i ve-testiface -j ACCEPT",
        "-A FORWARD -o ve-testiface -m conntrack "
        "--ctstate RELATED,ESTABLISHED -j ACCEPT",
    )


def test_interface_forward_no_comment(location, system_context):
    ipt.install_rules(location, system_context)

    ipt.forward_interface(system_context, "ve-testiface")

    _validate_rules_files(
        system_context,
        "-A FORWARD -i ve-testiface -j ACCEPT",
        "-A FORWARD -o ve-testiface -m conntrack "
        "--ctstate RELATED,ESTABLISHED -j ACCEPT",
    )


def test_interface_no_double_entries(location, system_context):
    ipt.install_rules(location, system_context)

    ipt.forward_interface(system_context, "ve-testiface", comment="test iface")
    with pytest.raises(GenerateError):
        ipt.forward_interface(system_context, "ve-testiface")
