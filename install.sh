#!/bin/bash

set -e

ppas=( utappia/stable )
aptSoftwares=( ucaresystem-core git zsh copyq bat yarn chromium-browser )
snapSoftwares=( code spotify slack snowflake )

echo "Start installation..."

# Install PPAs #
for i in "${ppas[@]}"
do 
  if ! grep -q "^deb .*$i" /etc/apt/sources.list /etc/apt/sources.list.d/*; then
    echo "Adding $i PPA"
    sudo apt-add-repository "ppa:$i" -y
  fi
done

# Configure Yarn Debian package repository
if [ ! -f /etc/apt/sources.list.d/yarn.list ]; then 
  wget -qO- https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
  echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
fi

# Check for non installed apt softwares
aptSoftwaresToInstall=""
for i in "${aptSoftwares[@]}"
do 
  if [ $(dpkg-query -W -f='${Status}' $i 2>/dev/null | grep -c "ok installed") -eq 0 ];
  then
     aptSoftwaresToInstall="${aptSoftwaresToInstall} $i"
  fi
done

if [ -n "$aptSoftwaresToInstall" ]
then
 echo "Installing apt $aptSoftwaresToInstall..."
 
 sudo apt update
 sudo apt install -y $aptSoftwaresToInstall
 
 echo "Apt installation done"
fi

# Install snap softwares
for i in "${snapSoftwares[@]}"
do 
   if ! hash "$i" >/dev/null 2>&1; then
     echo "Installing snap $i..."
     sudo snap install --classic "$i"
     echo "Snap installation done"
   fi
done

# Install nvm
wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/v0.35.3/install.sh | bash

# Prevents antigen error
rm -f ~/.antigen/.lock

# Install oh-my-zsh
if [ ! -f ~/.zshrc ] && [ ! -h ~/.zshrc ]; then 
  sh -c "$(wget https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh -O -)"
else
  zsh -i -c "omz update"
fi

# Setup nerdfont
wget https://github.com/ryanoasis/nerd-fonts/releases/latest/download/FiraCode.zip -P /tmp
unzip -o /tmp/FiraCode.zip -d ~/.fonts
rm -f /tmp/FiraCode.zip
fc-cache -fv

# Setup antigen & starship
wget git.io/antigen -O ~/antigen.zsh
wget https://raw.github.com/neilime/ubuntu-config/master/antigenrc -O ~/.antigenrc
zsh -i -c "$(wget https://starship.rs/install.sh -O -)" '' -f

wget https://raw.github.com/neilime/ubuntu-config/master/zshrc -O ~/.zshrc

# Configure git
wget https://raw.github.com/neilime/ubuntu-config/master/gitconfig -O ~/.gitconfig

# Create default directories
mkdir -p ~/Documents/dev-projects

echo "Cleaning..."
sudo ucaresystem-core

echo "Installation done"

zsh -i -c "exec zsh"
