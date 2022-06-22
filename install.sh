#!/bin/bash --init-file
set -e

# If not running interactively, don't do anything
[ -z "$PS1" ] && echo "$0 must be running interactively" &&  exit 1 

# Versions
get_latest_release() {
  wget -q "https://api.github.com/repos/$1/releases/latest" -O - | # Get latest release from GitHub api
    grep '"tag_name":' |                                            # Get tag line
    sed -E 's/.*"([^"]+)".*/\1/'                                    # Pluck JSON value
}

REPOSITORY_URL=https://raw.github.com/neilime/ubuntu-config/master

NVM_VERSION=$(get_latest_release "nvm-sh/nvm") # https://github.com/nvm-sh/nvm/releases/latest

ppas=( utappia/stable )
aptKeys=(https://download.docker.com/linux/ubuntu/gpg https://dl.yarnpkg.com/debian/pubkey.gpg)
aptKeyFingerprints=( 0EBFCD88 )
aptSoftwares=( \
  # System
  ucaresystem-core localepurge apt-transport-https ca-certificates gnupg-agent software-properties-common \
  # Common tools
  bat zsh copyq thefuck \
  # Needed by thefuck (https://bugs.launchpad.net/ubuntu/+source/thefuck/+bug/1875178)
  python3-distutils \
  # Apps
  chromium-browser
  # Common dev
  git docker-ce docker-ce-cli containerd.io \
  # Js dev
  yarn \
  # Php
  php-curl php-gd php-intl php-json php-mbstring php-xml php-zip php-cli \
)
snapSoftwares=( code spotify slack snowflake jdownloader2 vlc )

echo "Start installation..."

# Install PPAs #
for i in "${ppas[@]}"
do 
  if ! grep -q "^deb .*$i" /etc/apt/sources.list /etc/apt/sources.list.d/*; then
    echo "Adding $i PPA"
    sudo apt-add-repository "ppa:$i" -y
  fi
done

# Install nvm
wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/$NVM_VERSION/install.sh | bash

source ~/.bashrc

nvm install 'lts/*' --reinstall-packages-from=current --latest-npm

# Install APT keys
for i in "${aptKeys[@]}"
do 
  echo "Adding APT key $i"
  wget -qO- $i | sudo apt-key add -
done

# Install APT key fingerprints
for i in "${aptKeyFingerprints[@]}"
do 
  echo "Adding APT key fingerprint $i"
  sudo apt-key fingerprint $i
done

# Configure Docker Debian package repository
sudo add-apt-repository \
  "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) \
  stable"

# Configure Yarn Debian package repository
if [ ! -f /etc/apt/sources.list.d/yarn.list ]; then 
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

# Upgrade APT packages
sudo apt-get update
sudo apt-get upgrade -y

if [ -n "$aptSoftwaresToInstall" ]
then
 echo "Installing apt $aptSoftwaresToInstall..."

 sudo apt-get install -y $aptSoftwaresToInstall

 echo "APT installation done"
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

# Upgrade Snap packages
sudo snap refresh

# Fix System limit for number of file watchers reached
echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf && sudo sysctl -p

# Docker post-install
if ! grep -q docker /etc/group; then
  sudo groupadd docker   
fi

if ! getent group docker | grep -q "\b${USER}\b"; then
  sudo usermod -aG docker $USER
fi

# Install docker-compose
sudo wget "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -O /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install composer
sudo wget -qO-  https://getcomposer.org/installer | php
sudo mv composer.phar /usr/local/bin/composer

# Install oh-my-zsh
if [ ! -f ~/.zshrc ] && [ ! -h ~/.zshrc ]; then 
  sh -c "$(wget https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh -O -)"
else 
  if command -v omz &> /dev/null; then
    zsh -i -c "omz update"
  fi
fi

# Setup nerdfont
rm -f /tmp/FiraCode.zip
wget https://github.com/ryanoasis/nerd-fonts/releases/latest/download/FiraCode.zip -P /tmp
unzip -o /tmp/FiraCode.zip -d ~/.fonts
rm -f /tmp/FiraCode.zip
fc-cache -fv

# Setup starship
sh -i -c "$(wget https://starship.rs/install.sh -O -)" '' -f

wget $REPOSITORY_URL/.dot/zshrc -O ~/.zshrc

# Configure git
wget $REPOSITORY_URL/.dot/gitconfig -O ~/.gitconfig

# Configure CopyQ
sed -i '/^\[Shortcuts\]$/,/^\[/ s/^show_clipboard_content\s*=.*/show_clipboard_content=ctrl+shift+c/' ~/.config/copyq/copyq.conf

# Create default directories
mkdir -p ~/Documents/dev-projects

# Configure autostart
mkdir -p ~/.config/autostart;
wget $REPOSITORY_URL/.dot/config/autostart/sh.desktop -O ~/.config/autostart/sh.desktop

echo "Cleaning..."

# Remove globally packages installed with npm
NPM_GLOBAL_PACKAGES=$(npm ls -gp --depth=0 | awk -F/ '/node_modules/ && !/\/npm$/ {print $NF}');
[ ! -z "$NPM_GLOBAL_PACKAGES" ] && npm -g rm $NPM_GLOBAL_PACKAGES;

# Remove globally packages installed with yarn
YARN_GLOBAL_PACKAGES=$(yarn global list  | awk -F\" '/info "/ {print $2}' | awk -F@ '{print $1}');
[ ! -z "$YARN_GLOBAL_PACKAGES" ] && yarn global remove $YARN_GLOBAL_PACKAGES;

# Clear caches
yarn cache clean --all
nvm cache clear
npm cache clean --force 

# Clear useless docker resources
sudo docker system prune --force

sudo ucaresystem-core -u

echo "Installation done"

zsh -i -c "exec zsh"