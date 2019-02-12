# Integration Tests #

The integration tests are written as Ansible playbooks targeted for all hosts.
They follow the [Fedora's Standard Test
Interface](https://fedoraproject.org/wiki/CI/Standard_Test_Interface) and can
be run by the [Linux System Roles Test
Harness](https://github.com/linux-system-roles/test-harness).
With Ansible and the inventory scripts from the [Standard Test
Roles](https://pagure.io/standard-test-roles) you can run the tests against
OpenStack images like the [CentOS 7 Cloud
Images](https://cloud.centos.org/centos/7/images/) as follows:

```
wget https://cloud.centos.org/centos/7/images/CentOS-7-x86_64-GenericCloud.qcow2c
yum install standard-test-roles
TEST_SUBJECTS=CentOS-7-x86_64-GenericCloud.qcow2c TEST_ARTIFACTS=$PWD ansible-playbook -i /usr/share/ansible/inventory/standard-inventory-qcow2 tests_*.yml
```

The tests are defined in Ansible playbooks named `tests_*.yml` that must run
successfully when the tests passes or skips and fail otherwise.
