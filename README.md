# Ansible Support for nmstate
[![Build Status](https://travis-ci.org/nmstate/ansible-nmstate.svg?branch=master)](https://travis-ci.org/nmstate/ansible-nmstate)
[![Coverage Status](https://coveralls.io/repos/github/nmstate/ansible-nmstate/badge.svg?branch=master)](https://coveralls.io/github/nmstate/ansible-nmstate?branch=master)

Ansible-NMState allows to configure the network state with
[NMState](https://nmstate.github.io/) through Ansible.

## Development Environment

Run unit tests:
```shell
tox
```

## Basic Operations

Set an IP address for the interface `web-bond` on the host `rhel7-cloud`:

```shell
ANSIBLE_MODULE_UTILS=$PWD/module_utils ansible -M $PWD/library -m net_l3_interface -a 'name=web-bond state=present ipv4=192.0.2.7/24' -e ansible_network_os=nmstate -i rhel7-cloud, all
```

For example playbooks, see the `examples/` directory. Run a playbook:

```shell
ANSIBLE_MODULE_UTILS=$PWD/module_utils ansible-playbook -M $PWD/library examples/web-bond.yml -i rhel7-cloud,
```
