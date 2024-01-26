#!/usr/bin/env bash

set -e -o pipefail
set -x

{ # this ensures the entire script is downloaded #

#################################################################################################
#                                       SETUP                                                   #
#################################################################################################

if [ -z "$REPOSITORY_URL" ]; then
  export REPOSITORY_URL=https://raw.github.com/neilime/ubuntu-config/main
fi

#################################################################################################
#                                       INSTALLATION                                            #
#################################################################################################

install_configuration() {
  # Fix System limit for number of file watchers reached
  echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf && sudo sysctl -p

  utils_download_repository_file ".dot/zshrc" ~/.zshrc

  # Configure git
  utils_download_repository_file ".dot/gitconfig" ~/.gitconfig

  # Create default directories
  mkdir -p ~/Documents/dev-projects

  # Configure autostart
  mkdir -p ~/.config/autostart;
  utils_download_repository_file ".dot/config/autostart/sh.desktop" ~/.config/autostart/sh.desktop
  
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

  # install_apt
  # install_localization
  # install_snap
  # install_docker
  # install_nvm
  # install_yarn
  # install_php
  # install_fonts
  # install_zsh
  install_configuration
  
  utils_echo "Installation done"
  
  utils_echo "Start cleaning..."
  do_cleaning
  utils_echo "Cleaning done"
}

do_install

} # this ensures the entire script is downloaded #
