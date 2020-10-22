#!/usr/bin/python
#
# Copyright 2020 Red Hat, Inc.
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

from ansible.module_utils.ansible_nmstate import write_debug_state

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.network.common.utils import remove_default_spec


import libnmstate

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = """
---
module: nmstate_apply
version_added: "2.9"
author: "Till Maas (@tyll)"
short_description:
description:
    - "This module allows to apply a network state with nmstate
       https://github.com/nmstate/nmstate"
options:
  state:
    description:
      - Nmstate state definition
"""

EXAMPLES = """
"""

RETURN = """
state:
    description: Network state after running the module
    type: dict
"""


class AnsibleNMStateApply:
    def __init__(self, module, module_name):
        self.previous_state = libnmstate.show()
        self.module = module
        self.params = module.params
        self.result = dict(changed=False)
        self.module_name = module_name

    def run(self):
        state = self.params["state"]

        if self.params.get("debug"):
            self.result["previous_state"] = self.previous_state
            self.result["desired_state"] = state
            self.result["debugfile"] = write_debug_state(self.module_name, state)

        libnmstate.apply(state)

        current_state = libnmstate.show()
        if current_state != self.previous_state:
            self.result["changed"] = True
        self.result["state"] = current_state

        self.module.exit_json(**self.result)


def run_module():
    argument_spec = dict(
        state=dict(required=True, type="dict"),
        debug=dict(default=False, type="bool"),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=False,
    )

    nmstate_module = AnsibleNMStateApply(module, "nmstate_apply")

    nmstate_module.run()


def main():
    run_module()


if __name__ == "__main__":
    main()
