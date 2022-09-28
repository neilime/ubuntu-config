#!/usr/bin/env bash

set -e -o pipefail
set -x

{ # this ensures the entire script is downloaded #

#################################################################################################
#                                       SETUP                                                   #
#################################################################################################

ppas=( utappia/stable )
aptKeys=(https://download.docker.com/linux/ubuntu/gpg https://dl.yarnpkg.com/debian/pubkey.gpg)
aptKeyFingerprints=( 0EBFCD88 )

aptSoftwares=( \
  # Cleaning
  localepurge ucaresystem-core \
  # System
  apt-transport-https ca-certificates gnupg-agent software-properties-common ubuntu-release-upgrader-core gnome-shell-extensions \
  # Common tools
  wget curl unzip bat zsh copyq thefuck make \
  # Needed by thefuck (https://bugs.launchpad.net/ubuntu/+source/thefuck/+bug/1875178)
  python3-distutils \
  # Apps
  chromium-browser simple-scan krita
  # Common dev
  git docker-ce docker-ce-cli containerd.io \
  # Js dev
  yarn \
  # Php
  php-zip php-cli \
)
snapSoftwares=( deja-dup code spotify slack jdownloader2 vlc htop )

timezone="Europe/Paris"
locale="en_US.UTF-8"

if [ -e "$REPOSITORY_URL" ]; then
  REPOSITORY_URL=https://raw.github.com/neilime/ubuntu-config/main
fi

#################################################################################################
#                                       INSTALLATION                                            #
#################################################################################################


utils_echo() {
  command printf %s\\n "$*" 2>/dev/null
}

utils_try_with_attempts() {

  # Retrieve command from arguments
  COMMAND="$*"
  # Try 3 attempts
  attempts=0
  while [ $attempts -lt 3 ]; do
    set +e
    # Execute command
    eval "$COMMAND"
    COMMAND_RESULT=$?
    set -e
    if [ $COMMAND_RESULT -eq 0 ]; then
      break
    fi

    sleep 3
    attempts=$((attempts+1))
    if [ $attempts -eq 3 ]; then
      utils_echo >&2 "Error: failed to run command"
      exit 1
    fi
    
  done
}

check_requirements() {
  utils_echo "Checking requirements..."
  if [ -z "${BASH_VERSION}" ] || [ -n "${ZSH_VERSION}" ]; then
    # shellcheck disable=SC2016
    utils_echo >&2 'Error: the install instructions explicitly say to pipe the install script to `bash`; please follow them'
    exit 1
  fi
}

get_latest_release() {
  wget -q "https://api.github.com/repos/$1/releases/latest" -O - | # Get latest release from GitHub api
    grep '"tag_name":' |                                            # Get tag line
    sed -E 's/.*"([^"]+)".*/\1/'                                    # Pluck JSON value
}

install_localization() {

  if [ ! -f /etc/localtime ]; then
    sudo ln -snf /usr/share/zoneinfo/$timezone /etc/localtime
  fi

  if [ ! -f /etc/timezone ]; then
    echo "$timezone" | sudo tee -a /etc/timezone
  fi

  sudo locale-gen --purge "$locale"
  sudo dpkg-reconfigure -f noninteractive localepurge
}

# Install PPAs
install_ppas() {
  for i in "${ppas[@]}"
  do 
    if ! grep -q "^deb .*$i" /etc/apt/sources.list /etc/apt/sources.list.d/*; then
      utils_echo "Adding $i PPA"
      sudo apt-add-repository "ppa:$i" -y
    fi
  done
}

# Install nvm
install_nvm() {
  NVM_VERSION=$(get_latest_release "nvm-sh/nvm") # https://github.com/nvm-sh/nvm/releases/latest
  wget -qO- "https://raw.githubusercontent.com/nvm-sh/nvm/$NVM_VERSION/install.sh" | bash

  NVM_DIR="$([ -z "${XDG_CONFIG_HOME-}" ] && printf %s "${HOME}/.nvm" || printf %s "${XDG_CONFIG_HOME}/nvm")";
  # shellcheck disable=SC1091
  [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh";

  nvm install 'lts/*' --reinstall-packages-from=current --latest-npm
}

install_apt() {

  # Install APT keys
  for i in "${aptKeys[@]}"
  do
    utils_echo "Adding APT key $i"
    wget -qO- "$i" | sudo apt-key add -
  done

  # Install APT key fingerprints
  for i in "${aptKeyFingerprints[@]}"
  do 
    utils_echo "Adding APT key fingerprint $i"
    sudo apt-key fingerprint "$i"
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

  # Upgrade APT packages
  sudo apt -yqq update
  sudo apt -yqq upgrade

  # Check for non installed apt softwares
  utils_echo "Check for non installed apt softwares..."
  aptSoftwaresToInstall=""
  for i in "${aptSoftwares[@]}"
  do
    set +e
    INSTALLED_PACKAGE=$(dpkg-query -W -f='${Status}' "$i" 2>/dev/null | grep -c "ok installed")
    set -e
    if [ "$INSTALLED_PACKAGE" -eq 0 ];
    then
       aptSoftwaresToInstall="${aptSoftwaresToInstall} $i"
    fi
  done

  if [ -n "$aptSoftwaresToInstall" ]
  then
    for i in "${aptSoftwaresToInstall[@]}"
    do 
      utils_echo "Installing apt $i..."
      utils_try_with_attempts sudo DEBIAN_FRONTEND=noninteractive apt -yq install "$i"
      utils_echo "APT installation of $i done"
    done

  else
    utils_echo "No APT software to install"
  fi
}

install_snap() {
  # Install snap softwares
  for i in "${snapSoftwares[@]}"
  do 
    if ! hash "$i" >/dev/null 2>&1; then
      utils_echo "Installing snap $i..."
      utils_try_with_attempts sudo DEBIAN_FRONTEND=noninteractive snap install --classic "$i"       
      utils_echo "Snap installation of $i done"
    fi
  done

  # Upgrade Snap packages
  sudo snap refresh
}

install_docker() {
  # Docker post-install
  if ! grep -q docker /etc/group; then
    sudo groupadd docker   
  fi

  if ! getent group docker | grep -q "\b${USER}\b"; then
    sudo usermod -aG docker "$USER"
  fi

  # Install docker-compose
  sudo wget "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -O /usr/local/bin/docker-compose
  sudo chmod +x /usr/local/bin/docker-compose
}

install_php() {
  # Install composer
  sudo wget -qO-  https://getcomposer.org/installer | php
  sudo mv composer.phar /usr/local/bin/composer
}

install_fonts() {
  # Setup nerdfont
  rm -f /tmp/FiraCode.zip
  wget https://github.com/ryanoasis/nerd-fonts/releases/latest/download/FiraCode.zip -P /tmp
  unzip -o /tmp/FiraCode.zip -d ~/.fonts
  rm -f /tmp/FiraCode.zip
  fc-cache -fv
}

# Install oh-my-zsh
install_zsh() {
  if [ ! -f ~/.zshrc ] && [ ! -h ~/.zshrc ]; then 
    sh -c "$(wget https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh -O -)"
  else 
    if command -v omz &> /dev/null; then
      zsh -i -c "omz update"
    fi
  fi

  # Setup starship
  sh -i -c "$(wget https://starship.rs/install.sh -O -)" '' -f
}

install_configuration() {
  # Fix System limit for number of file watchers reached
  echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf && sudo sysctl -p

  wget $REPOSITORY_URL/.dot/zshrc -O ~/.zshrc

  # Configure git
  wget $REPOSITORY_URL/.dot/gitconfig -O ~/.gitconfig

  # Create default directories
  mkdir -p ~/Documents/dev-projects

  # Configure autostart
  mkdir -p ~/.config/autostart;
  wget $REPOSITORY_URL/.dot/config/autostart/sh.desktop -O ~/.config/autostart/sh.desktop
  
  # Configure default applications
  xdg-settings set default-web-browser chromium-browser.desktop
  
  # Configure favorite applications
  gsettings set org.gnome.shell favorite-apps "['gnome-control-center.desktop', 'snap-store_ubuntu-software.desktop', 'org.gnome.Nautilus.desktop', 'org.gnome.Terminal.desktop', 'chromium_chromium.desktop', 'code_code.desktop', 'slack_slack.desktop', 'spotify_spotify.desktop']"
  
  # Configure appearance
  gsettings set org.gnome.desktop.interface color-scheme prefer-dark
  
  # Configure copyq
  copyq --start-server
  copyq eval "var cmds = commands();var cmd = cmds.find(command => command.internalId === 'copyq_global_toggle'); if(cmd){cmd.globalShortcuts = ['ctrl+shift+v'];}setCommands(cmds)"
}

do_cleaning() {
  # Remove globally packages installed with npm
  NPM_GLOBAL_PACKAGES=$(npm ls -gp --depth=0 | awk -F/ '/node_modules/ && !/\/npm$/ {print $NF}');
  # shellcheck disable=SC2086
  [ -n "$NPM_GLOBAL_PACKAGES" ] && npm -g rm $NPM_GLOBAL_PACKAGES;

  # Remove globally packages installed with yarn
  YARN_GLOBAL_PACKAGES=$(yarn global list  | awk -F\" '/info "/ {print $2}' | awk -F@ '{print $1}');
  # shellcheck disable=SC2086
  [ -n "$YARN_GLOBAL_PACKAGES" ] && yarn global remove $YARN_GLOBAL_PACKAGES;

  # Clear caches
  yarn cache clean --all
  nvm cache clear
  npm cache clean --force 

  # Clear useless docker resources
  sudo docker system prune --force

  sudo localepurge
  set +e
  sudo ucaresystem-core -u
  set -e
}

do_install() {
  utils_echo "Start installation..."

  install_ppas
  install_apt
  install_localization
  # install_snap
  install_docker
  install_nvm
  install_php
  install_fonts
  install_zsh
  install_configuration
  
  utils_echo "Installation done"
  
  utils_echo "Start cleaning..."
  do_cleaning
  utils_echo "Cleaning done"
}

do_install

} # this ensures the entire script is downloaded #
