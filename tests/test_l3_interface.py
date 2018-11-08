#
# Copyright 2018 Red Hat, Inc.
#
# This file is part of ansible-nmstate.
#
# ansible-nmstate is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ansible-nmstate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ansible-nmstate.  If not, see <https://www.gnu.org/licenses/>.
#
""" Unit tests for nmstate_l3_interface.py """

try:
    from unittest import mock
except ImportError:  # py2
    import mock


from testlib import ANSIBLE_MOCK_MODULES


with mock.patch.dict("sys.modules", ANSIBLE_MOCK_MODULES):
    # E402 module level import not at top of file
    import nmstate_l3_interface as nli  # noqa: E402


def test_create_ip_dict_ipv4():
    ipv4 = "198.51.100.31/24"
    assert nli.create_ip_dict(ipv4) == {"ip": "198.51.100.31", "prefix-length": 24}


def test_add_ipv4_addresses(base_state):
    # test ip addresses are from:
    # https://tools.ietf.org/html/rfc5737
    ipv4 = ["198.51.100.31/24"]
    ip4config = nli.add_addresses({}, ipv4)
    assert len(ip4config["address"]) == 1
    assert ip4config["address"][0]["ip"] == ipv4[0].split("/")[0]

    # add second IP address
    ipv4_old = ipv4
    ipv4 = ["192.0.2.8/24"]
    ip4config = nli.add_addresses(ip4config, ipv4)
    assert len(ip4config["address"]) == 2
    assert ip4config["address"][0]["ip"] == ipv4_old[0].split("/")[0]
    assert ip4config["address"][1]["ip"] == ipv4[0].split("/")[0]

    # Set only one address
    ip4config = nli.set_addresses(ip4config, ipv4)
    assert len(ip4config["address"]) == 1
    assert ip4config["address"][0]["ip"] == ipv4[0].split("/")[0]

    # Set only one (different) address
    ipv4 = ["203.0.113.5/24"]
    ip4config = nli.set_addresses(ip4config, ipv4)
    assert len(ip4config["address"]) == 1
    assert ip4config["address"][0]["ip"] == ipv4[0].split("/")[0]


def test_add_ipv4_address_twice(base_state):
    ipv4 = ["198.51.100.31/24"]
    ip4config = nli.add_addresses({}, ipv4)
    assert len(ip4config["address"]) == 1
    assert ip4config["address"][0]["ip"] == ipv4[0].split("/")[0]
    ip4config = nli.add_addresses({}, ipv4)
    assert len(ip4config["address"]) == 1
    assert ip4config["address"][0]["ip"] == ipv4[0].split("/")[0]


def test_add_two_ipv4_addressess_at_once(base_state):
    ipv4 = ["198.51.100.31/24", "192.0.2.8/24"]
    ip4config = nli.add_addresses({}, ipv4)
    assert len(ip4config["address"]) == 2
    assert ip4config["address"][0]["ip"] == ipv4[0].split("/")[0]
    assert ip4config["address"][1]["ip"] == ipv4[1].split("/")[0]


def test_remove_ipv4_address_empty(base_state):
    ipv4 = ["198.51.100.31/24"]
    ip4config = nli.remove_addresses({}, ipv4)

    assert ip4config == {}


def test_set_remove_ipv4_address_not_existing(base_state):
    ipv4 = ["198.51.100.31/24"]
    ip4config = nli.add_addresses({}, ipv4)
    assert len(ip4config["address"]) == 1
    assert ip4config["address"][0]["ip"] == ipv4[0].split("/")[0]

    # add second IP address
    ipv4_old = ipv4
    ipv4 = ["192.0.2.8/24"]
    ip4config = nli.add_addresses(ip4config, ipv4)
    assert len(ip4config["address"]) == 2
    assert ip4config["address"][0]["ip"] == ipv4_old[0].split("/")[0]
    assert ip4config["address"][1]["ip"] == ipv4[0].split("/")[0]

    # remove non existing address
    ip4config = nli.remove_addresses(ip4config, ["203.0.113.7/24"])
    assert len(ip4config["address"]) == 2
    assert ip4config["address"][0]["ip"] == ipv4_old[0].split("/")[0]
    assert ip4config["address"][1]["ip"] == ipv4[0].split("/")[0]

    ip4config = nli.remove_addresses(ip4config, ipv4_old)
    assert len(ip4config["address"]) == 1
    assert ip4config["address"][0]["ip"] == ipv4[0].split("/")[0]


def test_add_and_remove_ipv4_address(base_state):
    ipv4 = ["198.51.100.31/24"]
    ip4config = nli.add_addresses({}, ipv4)
    assert len(ip4config["address"]) == 1
    assert ip4config["address"][0]["ip"] == ipv4[0].split("/")[0]

    ip4config = nli.remove_addresses(ip4config, ["203.0.113.7/24"])
    assert len(ip4config["address"]) == 1
    assert ip4config["address"][0]["ip"] == ipv4[0].split("/")[0]

    ip4config = nli.remove_addresses(ip4config, ipv4)
    assert len(ip4config["address"]) == 0

    ip4config_b = nli.remove_addresses(ip4config, ipv4)
    assert ip4config == ip4config_b


def test_collect_single_settings():
    aggregate = [{"name": "eth0", "ipv4": "198.51.100.31/24", "ipv6": "2001:db8::1/32"}]
    expected_config = {
        "eth0": {"ipv4": ["198.51.100.31/24"], "ipv6": ["2001:db8::1/32"]}
    }
    interface_config = nli.collect_settings(aggregate)

    assert interface_config == expected_config


def test_collect_multiple_ipv4_settings():
    aggregate = [
        {"name": "eth0", "ipv4": "192.0.2.14/30", "ipv6": None},
        {"name": "eth1", "ipv4": "192.0.2.15/30", "ipv6": None},
        {"name": "eth0", "ipv4": "192.0.2.12/30", "ipv6": None},
    ]
    expected_config = {
        "eth0": {"ipv4": ["192.0.2.14/30", "192.0.2.12/30"]},
        "eth1": {"ipv4": ["192.0.2.15/30"]},
    }
    interface_config = nli.collect_settings(aggregate)

    assert interface_config == expected_config


def test_single_addresses_present(base_state):
    module_params = dict(
        name="eth0",
        state="present",
        ipv4="198.51.100.31/24",
        ipv6="2001:db8::1/32",
        purge=False,
    )

    applied_state = run_module(module_params, base_state)
    interface_state = applied_state["interfaces"][0]

    relevant_interface_state = {
        "name": interface_state["name"],
        "state": interface_state["state"],
        "ipv4": interface_state["ipv4"],
        "ipv6": interface_state["ipv6"],
    }

    expected_interface_state = {
        "name": "eth0",
        "state": "up",
        "ipv4": {
            "address": [{"ip": "198.51.100.31", "prefix-length": 24}],
            "enabled": True,
        },
        "ipv6": {
            "address": [{"ip": "2001:db8::1", "prefix-length": 32}],
            "enabled": True,
        },
    }

    assert relevant_interface_state == expected_interface_state
    assert len(applied_state["interfaces"]) == 1


def test_aggregate_present(base_state):
    module_params = dict(
        name=None,
        state="present",
        aggregate=[dict(name="eth0", ipv4="198.51.100.31/24", ipv6="2001:db8::1/32")],
        purge=False,
    )

    applied_state = run_module(module_params, base_state)
    interface_state = applied_state["interfaces"][0]

    relevant_interface_state = {
        "name": interface_state["name"],
        "state": interface_state["state"],
        "ipv4": interface_state["ipv4"],
        "ipv6": interface_state["ipv6"],
    }

    expected_interface_state = {
        "name": "eth0",
        "state": "up",
        "ipv4": {
            "address": [{"ip": "198.51.100.31", "prefix-length": 24}],
            "enabled": True,
        },
        "ipv6": {
            "address": [{"ip": "2001:db8::1", "prefix-length": 32}],
            "enabled": True,
        },
    }

    assert relevant_interface_state == expected_interface_state
    assert len(applied_state["interfaces"]) == 1


def test_aggregate_present_ipv4(base_state):
    module_params = dict(
        name=None,
        state="present",
        aggregate=[dict(name="eth0", ipv4="198.51.100.31/24", ipv6=None)],
        purge=False,
    )

    applied_state = run_module(module_params, base_state)
    interface_state = applied_state["interfaces"][0]

    relevant_interface_state = {
        "name": interface_state["name"],
        "state": interface_state["state"],
        "ipv4": interface_state["ipv4"],
        "ipv6": interface_state["ipv6"],
    }

    expected_interface_state = {
        "name": "eth0",
        "state": "up",
        "ipv4": {
            "address": [{"ip": "198.51.100.31", "prefix-length": 24}],
            "enabled": True,
        },
        "ipv6": {},
    }

    assert relevant_interface_state == expected_interface_state
    assert len(applied_state["interfaces"]) == 1


def test_aggregate_present_single_purge(base_state):
    module_params = dict(
        name=None,
        state="present",
        aggregate=[dict(name="eth0", ipv4="198.51.100.31/24", ipv6="2001:db8::1/32")],
        purge=True,
    )

    applied_state = run_module(module_params, base_state)
    interface_state = applied_state["interfaces"][0]

    relevant_interface_state = {
        "name": interface_state["name"],
        "state": interface_state["state"],
        "ipv4": interface_state["ipv4"],
        "ipv6": interface_state["ipv6"],
    }

    expected_interface_state = {
        "name": "eth0",
        "state": "up",
        "ipv4": {
            "address": [{"ip": "198.51.100.31", "prefix-length": 24}],
            "enabled": True,
        },
        "ipv6": {
            "address": [{"ip": "2001:db8::1", "prefix-length": 32}],
            "enabled": True,
        },
    }

    assert relevant_interface_state == expected_interface_state
    assert len(applied_state["interfaces"]) == 1


def test_aggregate_absent(base_state):
    module_params = dict(
        name=None,
        state="absent",
        aggregate=[dict(name="eth0", ipv4="198.51.100.32/24", ipv6="2001:db8::2/32")],
        purge=False,
    )

    base_state["interfaces"][0].update(
        {
            "ipv4": {
                "address": [
                    {"ip": "198.51.100.31", "prefix-length": 24},
                    {"ip": "198.51.100.32", "prefix-length": 24},
                ],
                "enabled": True,
            },
            "ipv6": {
                "address": [
                    {"ip": "2001:db8::1", "prefix-length": 32},
                    {"ip": "2001:db8::2", "prefix-length": 32},
                ],
                "enabled": True,
            },
        }
    )

    applied_state = run_module(module_params, base_state)
    interface_state = applied_state["interfaces"][0]

    relevant_interface_state = {
        "name": interface_state["name"],
        "ipv4": interface_state["ipv4"],
        "ipv6": interface_state["ipv6"],
    }

    expected_interface_state = {
        "name": "eth0",
        "ipv4": {
            "address": [{"ip": "198.51.100.31", "prefix-length": 24}],
            "enabled": True,
        },
        "ipv6": {
            "address": [{"ip": "2001:db8::1", "prefix-length": 32}],
            "enabled": True,
        },
    }

    assert relevant_interface_state == expected_interface_state
    assert "state" not in interface_state
    assert len(applied_state["interfaces"]) == 1


def test_aggregate_present_purge(base_state):
    module_params = dict(
        name=None,
        state="present",
        aggregate=[dict(name="eth0", ipv4="198.51.100.32/24", ipv6="2001:db8::2/32")],
        purge=True,
    )

    base_state["interfaces"][0].update(
        {
            "ipv4": {
                "address": [
                    {"ip": "198.51.100.31", "prefix-length": 24},
                    {"ip": "198.51.100.32", "prefix-length": 24},
                ],
                "enabled": True,
            },
            "ipv6": {
                "address": [
                    {"ip": "2001:db8::1", "prefix-length": 32},
                    {"ip": "2001:db8::2", "prefix-length": 32},
                ],
                "enabled": True,
            },
        }
    )

    applied_state = run_module(module_params, base_state)
    interface_state = applied_state["interfaces"][0]

    relevant_interface_state = {
        "name": interface_state["name"],
        "ipv4": interface_state["ipv4"],
        "ipv6": interface_state["ipv6"],
    }

    expected_interface_state = {
        "name": "eth0",
        "ipv4": {
            "address": [{"ip": "198.51.100.32", "prefix-length": 24}],
            "enabled": True,
        },
        "ipv6": {
            "address": [{"ip": "2001:db8::2", "prefix-length": 32}],
            "enabled": True,
        },
    }

    assert relevant_interface_state == expected_interface_state
    assert len(applied_state["interfaces"]) == 1


def run_module(module_params, current_state):
    ansible_module = mock.Mock()
    ansible_module.check_mode = False
    ansible_module.params = module_params

    with mock.patch(
        "ansible_nmstate.netinfo.show", return_value=current_state
    ) as mock_show:
        nmstate_module = nli.AnsibleNMStateL3Interface(
            ansible_module, "nmstate_interface_mock"
        )
        assert mock_show.called

        with mock.patch("ansible_nmstate.netapplier.apply") as mock_apply:
            nmstate_module.run()

    assert mock_show.call_count == 2
    assert mock_apply.called
    applied_state = mock_apply.call_args[0][0]
    return applied_state
