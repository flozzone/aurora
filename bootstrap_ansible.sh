#!/usr/bin/env bash
#
# Bootstrap the vagrant VM by installing Ansible and
# letting ansible do the provisioning in local connection mode
#
version=$(ansible version 2>&1)

if echo "$version" | grep -q -i 'command not found'
then
  echo "[Vagrant] Ansible not found, installing.."

  add-apt-repository -y ppa:rquillo/ansible 2>&1 >> /home/vagrant/provision.log
  apt-get update
  apt-get install -y ansible
fi

echo 'localhost              ansible_connection=local' > /home/vagrant/hosts
PYTHONUNBUFFERED=1 ansible-playbook /vagrant/provision_vagrant_vm.yml -i /home/vagrant/hosts
