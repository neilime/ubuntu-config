
#!/bin/bash

###################
# Install ucaresystem-core #
if ! grep -q "ansible/ansible" /etc/apt/sources.list /etc/apt/sources.list.d/*; then
    echo "Adding Utappia PPA"
    sudo apt-add-repository ppa:utappia/stable -y
fi

sudo apt update
sudo apt install ucaresystem-core
