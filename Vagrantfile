require 'yaml'
CONFIG_FILE = 'ansible/group_vars/vagrant.yml'
parms = YAML::load File.open(CONFIG_FILE)

Vagrant.configure("2") do |config|
  config.vm.box     = 'ubuntu14'
  config.vm.box_url = 'https://cloud-images.ubuntu.com/vagrant/trusty/current/trusty-server-cloudimg-i386-vagrant-disk1.box'

  config.vm.provider "virtualbox" do |v|
    v.customize ["modifyvm", :id, "--memory", 2048]
  end

  config.vm.synced_folder '.', parms["app_path"]
  config.vm.network :private_network, ip: "192.168.33.91"

  config.vm.provision :ansible do |ansible|
    ansible.playbook = 'ansible/vagrant.yml'
    ansible.inventory_path = 'ansible/hosts'
    ansible.limit = 'vagrant'
    ansible.host_key_checking = false
    ansible.sudo = true
    ansible.extra_vars = { ansible_ssh_user: 'vagrant' }
    ansible.verbose = 'v'
  end
end
