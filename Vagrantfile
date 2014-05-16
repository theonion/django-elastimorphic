# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "precise32"
  
  config.vm.network :private_network, ip: "192.168.33.101"
  config.vm.network "forwarded_port", guest: 9200, host: 9220

  config.vm.provider :virtualbox do |v, override|
    override.vm.box_url = "http://files.vagrantup.com/precise32.box"
  
    v.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
    v.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
  end

  config.vm.provision :shell do |shell|
    shell.path = "test_provision.sh"
  end
end
