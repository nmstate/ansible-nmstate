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
module: nmstate_interface
version_added: "2.6"
author: "Till Maas (@tyll)"
short_description: Configure network interface with nmstate
"""

EXAMPLES = """
"""

RETURN = """
state:
    description: Network state after running the module
    type: dict
"""


class AnsibleNMStateInterface(AnsibleNMState):
    def run(self):
        name = self.params["name"]
        full_interface_state = get_interface_state(self.interfaces, name)

        interface_state = {"name": name, "type": full_interface_state["type"]}

        state = self.params["state"]

        # "present" does not need to be mentioned in the state sent to nmstate
        if state != "present":
            interface_state["state"] = state

        if self.params["mtu"]:
            interface_state["mtu"] = int(self.params["mtu"])

        ethernet_state = {}

        if self.params["duplex"]:
            ethernet_state["auto-negotiation"] = self.params["duplex"] == "auto"

        if self.params["duplex"] and self.params["duplex"] != "auto":
            ethernet_state["duplex"] = self.params["duplex"]

        if self.params["speed"]:
            ethernet_state["speed"] = int(self.params["speed"])

        if ethernet_state:
            interface_state["ethernet"] = ethernet_state

        if self.params["description"] is not None:
            interface_state["description"] = self.params["description"]

        self.apply_partial_interface_state(interface_state)


def run_module():
    element_spec = dict(
        delay=dict(default=10, type="int"),
        description=dict(),
        duplex=dict(choices=["full", "half", "auto"]),
        enabled=dict(default=True, type="bool"),
        mtu=dict(),
        name=dict(),
        rx_rate=dict(),
        speed=dict(),
        state=dict(default="present", choices=["present", "absent", "up", "down"]),
        tx_rate=dict(),
    )

    aggregate_spec = deepcopy(element_spec)
    aggregate_spec["name"] = dict(required=True)

    # remove default in aggregate spec, to handle common arguments
    remove_default_spec(aggregate_spec)

    argument_spec = dict(
        aggregate=dict(type="list", elements="dict", options=aggregate_spec),
        purge=dict(default=False, type="bool"),
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

    nmstate_module = AnsibleNMStateInterface(module, "nmstate_interface")
    if module.params["aggregate"]:
        # FIXME implement aggregate
        module.fail_json(msg="Aggregate not yet supported", **nmstate_module.result)

    nmstate_module.run()


def main():
    run_module()


if __name__ == "__main__":
    main()
