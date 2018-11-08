#!/usr/bin/python
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

from copy import deepcopy

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.network.common.utils import remove_default_spec

from ansible.module_utils.ansible_nmstate import AnsibleNMState
from ansible.module_utils.ansible_nmstate import get_interface_state


ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = """
---
module: nmstate_l3_interface
version_added: "2.6"
author: "Till Maas (@tyll)"
short_description: Configure IP addresses (layer 3) with nmstate
description:
    - "This module allows to configure IP addresses (layer 3) with nmstate
       https://github.com/nmstate/nmstate"
options:
  name:
    description:
      - Name of the L3 interface.
  ipv4:
    description:
      - IPv4 of the L3 interface.
  ipv6:
    description:
      - IPv6 of the L3 interface.
  aggregate:
    description: List of L3 interfaces definitions
  purge:
    description:
      - Purge L3 interfaces not defined in the I(aggregate) parameter.
    default: no
  state:
    description:
      - State of the L3 interface configuration.
    default: present
    choices: ['present', 'absent']
"""

EXAMPLES = """
- name: Set eth0 IPv4 address
  net_l3_interface:
    name: eth0
    ipv4: 192.168.0.1/24

- name: Remove eth0 IPv4 address
  net_l3_interface:
    name: eth0
    state: absent

- name: Set IP addresses on aggregate
  net_l3_interface:
    aggregate:
      - { name: eth1, ipv4: 192.168.2.10/24 }
      - { name: eth2, ipv4: 192.168.3.10/24, ipv6: "fd5d:12c9:2201:1::1/64" }

- name: Remove IP addresses on aggregate
  net_l3_interface:
    aggregate:
      - { name: eth1, ipv4: 192.168.2.10/24 }
      - { name: eth2, ipv4: 192.168.3.10/24, ipv6: "fd5d:12c9:2201:1::1/64" }
    state: absent
"""

RETURN = """
state:
    description: Network state after running the module
    type: dict
"""


class AnsibleNMStateL3Interface(AnsibleNMState):
    def run(self):
        if self.params["name"]:
            interface_config = collect_settings([self.params])
        elif self.params["aggregate"]:
            interface_config = collect_settings(self.params["aggregate"])
        else:
            self.module.fail_json(
                msg="name or aggregate parameter missing", **self.result
            )

        interface_state = []
        for interface, config in interface_config.items():
            if self.params["state"] == "absent":
                new_state = self._handle_absent_interface(interface, config)
            else:
                new_state = self._handle_present_interface(interface, config)

            if new_state:
                interface_state.append(new_state)

        if interface_state:
            self.apply_partial_interface_state(interface_state)

        else:
            self.result["changed"] = False
            self.module.exit_json(**self.result)

    def _handle_present_interface(self, name, config):
        full_interface_state = get_interface_state(self.interfaces, name)
        if not full_interface_state:
            self.module.fail_json(
                msg='Interface "%s" not found' % (name,), **self.result
            )

        interface_state = {
            "name": name,
            "type": full_interface_state["type"],
            "ipv4": full_interface_state.get("ipv4", {}),
            "ipv6": full_interface_state.get("ipv6", {}),
            "state": "up",
        }

        for protocol in ("ipv4", "ipv6"):
            ipconfig = interface_state[protocol]
            addresses = config.get(protocol, [])

            if self.params["purge"]:
                updated_ipconfig = set_addresses(ipconfig, addresses)
                interface_state[protocol] = updated_ipconfig
            elif addresses:
                updated_ipconfig = add_addresses(ipconfig, addresses)
                interface_state[protocol] = updated_ipconfig

        return interface_state

    def _handle_absent_interface(self, name, config):
        full_interface_state = get_interface_state(self.interfaces, name)
        if full_interface_state:
            interface_state = {
                "name": name,
                "type": full_interface_state["type"],
                "ipv4": full_interface_state.get("ipv4", {}),
                "ipv6": full_interface_state.get("ipv6", {}),
            }

            for protocol in ("ipv4", "ipv6"):
                ipconfig = interface_state.setdefault(protocol, {})
                addresses = config.get(protocol)

                if addresses:
                    ipconfig.update(remove_addresses(ipconfig, addresses))

                # handle state:absent, ipv4:None, ipv6:None
                elif not (config.get("ipv4") or config.get("ipv6")):
                    ipconfig.update(set_addresses(ipconfig, []))

                # if no ip addresses remain, disable the family
                if not ipconfig.get("address"):
                    # FIXME: Disabling ipv6 is not supported in nmstate
                    if protocol != "ipv6":
                        ipconfig["enabled"] = False

            return interface_state


def collect_settings(aggregate):
    interface_config = {}
    for setting in aggregate:
        interface = setting["name"]
        config = interface_config.setdefault(interface, {})
        for protocol in ("ipv4", "ipv6"):
            address = setting[protocol]
            if address:
                config.setdefault(protocol, []).append(address)
    return interface_config


def set_addresses(ipconfig, new_addresses):
    ipconfig["address"] = []
    return add_addresses(ipconfig, new_addresses)


def add_addresses(ipconfig, new_addresses):
    ipconfig["enabled"] = True
    addresses = ipconfig.setdefault("address", [])
    new_addresses = (create_ip_dict(a) for a in new_addresses)

    for addr in new_addresses:
        if addr not in addresses:
            addresses.append(addr)

    return ipconfig


def remove_addresses(ipconfig, addresses):
    if not ipconfig:
        return ipconfig

    current_addresses = ipconfig.get("address")

    if not current_addresses:
        return ipconfig

    for address in addresses:
        addr = create_ip_dict(address)
        try:
            current_addresses.remove(addr)
        except ValueError:
            pass
    return ipconfig


def create_ip_dict(ciddr_addr):
    ip, prefix = ciddr_addr.split("/")
    addr = {"ip": ip, "prefix-length": int(prefix)}
    return addr


def run_module():
    element_spec = dict(name=dict(), ipv4=dict(), ipv6=dict())

    aggregate_spec = deepcopy(element_spec)
    aggregate_spec["name"] = dict(required=True)

    # remove default in aggregate spec, to handle common arguments
    remove_default_spec(aggregate_spec)

    argument_spec = dict(
        aggregate=dict(type="list", elements="dict", options=aggregate_spec),
        purge=dict(default=False, type="bool"),
        state=dict(default="present", choices=["present", "absent"]),
        # not in net_* specification
        debug=dict(default=False, type="bool"),
    )

    argument_spec.update(element_spec)

    required_one_of = [["name", "aggregate"]]
    mutually_exclusive = [["name", "aggregate"]]

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_one_of=required_one_of,
        mutually_exclusive=mutually_exclusive,
        supports_check_mode=True,
    )

    nmstate_module = AnsibleNMStateL3Interface(module, "nmstate_l3_interface")

    nmstate_module.run()


def main():
    run_module()


if __name__ == "__main__":
    main()
