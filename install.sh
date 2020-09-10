#!/bin/bash

ppas=( ppa:utappia/stable )
softwares=( ucaresystem-core )

###################
# Install PPAs #
for i in "${ppas[@]}"
do 
  if ! grep -q "^deb .*$i" /etc/apt/sources.list /etc/apt/sources.list.d/*; then
    echo "Adding $i PPA"
    sudo apt-add-repository "$i" -y
  fi
done

# Check for non installed softwares
softwaresToInstall=""
for i in "${softwares[@]}"
do 
   if ! hash ucaresystem-core >/dev/null 2>&1; then
     softwaresToInstall="${softwaresToInstall} $i"
   fi
done

if [ ! -z "$softwaresToInstall" ]
then
 echo "Installing $softwaresToInstall..."
 
 sudo apt update
 sudo apt install $softwaresToInstall
 
 echo "Installation done"
fi

echo "Cleaning..."
sudo ucaresystem-core
