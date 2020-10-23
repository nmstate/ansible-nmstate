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
#

""" unit tests for nmstate_apply.py """

from unittest import mock

from testlib import ANSIBLE_MOCK_MODULES


with mock.patch.dict("sys.modules", ANSIBLE_MOCK_MODULES):
    # E402 module level import not at top of file
    import nmstate_apply  # noqa: E402


def test_unchanged(base_state):
    module_params = {"state": base_state}
    nmstate_module, applied_state = run_module(module_params, base_state)
    assert applied_state == base_state
    assert not nmstate_module.result["changed"]


def run_module(module_params, current_state):
    ansible_module = mock.Mock()
    ansible_module.check_mode = False
    ansible_module.params = module_params

    with mock.patch(
        "ansible_nmstate.libnmstate.show", return_value=current_state
    ) as mock_show:
        nmstate_module = nmstate_apply.AnsibleNMStateApply(
            ansible_module, "nmstate_apply_mock"
        )
        assert mock_show.called

        with mock.patch("ansible_nmstate.libnmstate.apply") as mock_apply:
            nmstate_module.run()

    assert mock_show.call_count == 2
    assert mock_apply.called
    applied_state = mock_apply.call_args[0][0]
    return nmstate_module, applied_state
