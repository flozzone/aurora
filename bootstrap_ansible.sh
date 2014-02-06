#!/usr/bin/env bash
#
# Bootstrap the vagrant VM by installing Ansible and
# letting ansible do the provisioning in local connection mode
#
sudo apt-get update
sudo apt-get install -y python-software-properties
sudo add-apt-repository -y ppa:rquillo/ansible
sudo apt-get update
sudo apt-get install -y ansible
echo 'localhost              ansible_connection=local' > /home/vagrant/hosts
#cp /vagrant/hosts /home/vagrant/
#chmod 666 /home/vagrant/hosts
ansible-playbook /vagrant/provision_vagrant_vm.yml -i /home/vagrant/hosts
