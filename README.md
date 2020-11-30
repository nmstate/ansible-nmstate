# Ansible Support for nmstate
[![Build Status](https://travis-ci.com/nmstate/ansible-nmstate.svg?branch=main)](https://travis-ci.org/nmstate/ansible-nmstate)
[![Coverage Status](https://coveralls.io/repos/github/nmstate/ansible-nmstate/badge.svg?branch=main)](https://coveralls.io/github/nmstate/ansible-nmstate?branch=main)
[![Code Style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

Ansible-Nmstate allows to configure the network state with
[Nmstate](https://nmstate.github.io/) through Ansible.

## Development Environment

Run unit tests:
```shell
tox
```

## Installation

To install the modules, run:

```shell
make install
```

To install them system-wide, run this command as root. Alternatively the path
to the module utils and the library can be specified on the command line:

```shell
ANSIBLE_MODULE_UTILS=$PWD/module_utils ansible -M $PWD/library ...
```

or for playbooks:

```shell
ANSIBLE_MODULE_UTILS=$PWD/module_utils ansible-playbook -M $PWD/library ...
```

Using aliases keeps the command-line shorter:

```shell
alias ansible="ANSIBLE_MODULE_UTILS=$PWD/module_utils ansible -M $PWD/library"
alias ansible-playbook="ANSIBLE_MODULE_UTILS=$PWD/module_utils ansible-playbook -M $PWD/library"
```

Another possiblity for testing is to install [direnv](https://direnv.net/) to
automatically activate the necessary environment when entering the repository.

## Basic Operations

For example playbooks, see the `playbooks/` directory. Run a playbook:

```shell
ansible-playbook playbooks/bond.yml -i rhel8-cloud,
```
Note, in order to run the above playbook, nmstate 0.4 or later version must be
already installed on target machine.
