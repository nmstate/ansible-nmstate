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

""" unit tests for nmstate_interface.py """

try:
    from unittest import mock
except ImportError:  # py2
    import mock

from testlib import ANSIBLE_MOCK_MODULES


with mock.patch.dict("sys.modules", ANSIBLE_MOCK_MODULES):
    # E402 module level import not at top of file
    import nmstate_interface as nif  # noqa: E402


def test_import_succeeded():
    assert nif


def test_all_settings(base_state):
    ansible_module = mock.Mock()
    ansible_module.check_mode = False
    ansible_module.params = dict(
        name="eth0",
        state="present",
        enabled="yes",
        delay="10",
        mtu="1500",
        duplex="full",
        description="test_description",
        speed="1000",
    )

    with mock.patch(
        "ansible_nmstate.netinfo.show", return_value=base_state
    ) as mock_show:
        nmstate_module = nif.AnsibleNMStateInterface(
            ansible_module, "nmstate_interface_mock"
        )
        assert mock_show.called

        with mock.patch("ansible_nmstate.netapplier.apply") as mock_apply:
            nmstate_module.run()

    assert mock_show.call_count == 2
    assert mock_apply.called
    applied_state = mock_apply.call_args[0][0]

    interface_state = applied_state["interfaces"][0]

    relevant_interface_state = {
        "name": interface_state["name"],
        "description": interface_state["description"],
        "mtu": interface_state["mtu"],
        "ethernet": {
            "auto-negotiation": interface_state["ethernet"]["auto-negotiation"],
            "duplex": interface_state["ethernet"]["duplex"],
            "speed": interface_state["ethernet"]["speed"],
        },
    }

    expected_interface_state = {
        "name": "eth0",
        "description": "test_description",
        "mtu": 1500,
        "ethernet": {"auto-negotiation": False, "duplex": "full", "speed": 1000},
    }

    assert relevant_interface_state == expected_interface_state
    # state=present, means to not mention the state in the state to send to
    # nmstate
    assert "state" not in interface_state
    assert len(applied_state["interfaces"]) == 1
