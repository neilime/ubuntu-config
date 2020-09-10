#!/bin/bash

ppas=( ppa:utappia/stable )
aptSoftwares=( ucaresystem-core )
snapSoftwares=( code spotify )

# Install zsh
sh -c "$(wget https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh -O -)"

# Install PPAs #
for i in "${ppas[@]}"
do 
  if ! grep -q "^deb .*$i" /etc/apt/sources.list /etc/apt/sources.list.d/*; then
    echo "Adding $i PPA"
    sudo apt-add-repository "$i" -y
  fi
done

# Check for non installed apt softwares
aptSoftwaresToInstall=""
for i in "${aptSoftwares[@]}"
do 
   if ! hash "$i" >/dev/null 2>&1; then
     aptSoftwaresToInstall="${aptSoftwaresToInstall} $i"
   fi
done

if [ -n "$aptSoftwaresToInstall" ]
then
 echo "Installing $aptSoftwaresToInstall..."
 
 sudo apt update
 sudo apt install -y "$aptSoftwaresToInstall"
 
 echo "Installation done"
fi

# Check for non installed snap softwares
snapSoftwaresToInstall=""
for i in "${snapSoftwares[@]}"
do 
   if ! hash "$i" >/dev/null 2>&1; then
     snapSoftwaresToInstall="${snapSoftwaresToInstall} $i"
   fi
done

if [ -n "$snapSoftwaresToInstall" ]
then
 echo "Installing $snapSoftwaresToInstall..."
 
 sudo snap install --classic "$snapSoftwaresToInstall"
 
 echo "Installation done"
fi


echo "Cleaning..."
# sudo ucaresystem-core
