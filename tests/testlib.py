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

""" common code for testing the nmstate Ansible modules """
try:
    from unittest import mock
except ImportError:  # py2
    import mock

ANSIBLE_MOCK_MODULES = {}
ANSIBLE_MOCK_MODULES["ansible"] = mock.Mock()
ANSIBLE_MOCK_MODULES["ansible.module_utils.basic"] = mock.Mock()
ANSIBLE_MOCK_MODULES["ansible.module_utils"] = mock.Mock()
ANSIBLE_MOCK_MODULES["ansible.module_utils.network.common"] = mock.Mock()
ANSIBLE_MOCK_MODULES["ansible.module_utils.network.common.utils"] = mock.Mock()
ANSIBLE_MOCK_MODULES["ansible.module_utils.network"] = mock.Mock()

ANSIBLE_MOCK_MODULES["ansible.module_utils.ansible_nmstate"] = __import__(
    "ansible_nmstate"
)
