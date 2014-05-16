# installs and fires up elasticsearch
sudo sh -c "apt-get update -y"
sudo sh -c "wget -O - http://packages.elasticsearch.org/GPG-KEY-elasticsearch | apt-key add -"
sudo sh -c "echo deb http://packages.elasticsearch.org/elasticsearch/1.0/debian stable main \ >> /etc/apt/sources.list"
sudo sh -c "apt-get update -y"
sudo sh -c "apt-get install -y openjdk-7-jre elasticsearch"
sudo sh -c "update-rc.d elasticsearch defaults 95 10"
sudo sh -c "sudo /etc/init.d/elasticsearch start"
