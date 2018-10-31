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

from copy import deepcopy
import json
import os
import tempfile
import time


from libnmstate import netapplier
from libnmstate import netinfo


def write_debug_state(module_name, state):
    debugfile, debugname = tempfile.mkstemp(
        prefix="{}_debug-{}-".format(module_name, int(time.time()))
    )
    debugfile = os.fdopen(debugfile, "w")
    debugfile.write(json.dumps(state, indent=4))

    return debugname


def get_interface_state(interfaces, name):
    """
    Get the state for first interface with the specified name
    """
    for interface_state in interfaces:
        if interface_state["name"] == name:
            break
    else:
        interface_state = None
    return interface_state


class AnsibleNMState(object):
    def __init__(self, module, module_name):
        self.previous_state = netinfo.show()
        self.interfaces = deepcopy(self.previous_state["interfaces"])
        self.module = module
        self.params = module.params
        self.result = dict(changed=False)
        self.module_name = module_name

    def run(self):
        action = getattr(self, "handle_" + self.params["state"])
        action()

    def apply_partial_interface_state(self, interface_state):
        if isinstance(interface_state, list):
            interfaces = interface_state
        else:
            interfaces = [interface_state]
        new_partial_state = {"interfaces": interfaces}

        if self.params.get("debug"):
            self.result["previous_state"] = self.previous_state
            self.result["new_partial_state"] = new_partial_state
            self.result["debugfile"] = write_debug_state(
                self.module_name, new_partial_state
            )

        if self.module.check_mode:
            new_full_state = deepcopy(self.previous_state)
            new_full_state.update(new_partial_state)
            self.result["state"] = new_full_state

            # TODO: maybe compare only the state of the defined interfaces
            if self.previous_state != new_full_state:
                self.result["changed"] = True

            self.module.exit_json(**self.result)
        else:
            netapplier.apply(new_partial_state)
        current_state = netinfo.show()
        if current_state != self.previous_state:
            self.result["changed"] = True
        self.result["state"] = current_state

        self.module.exit_json(**self.result)
