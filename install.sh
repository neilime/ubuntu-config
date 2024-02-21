#!/usr/bin/env bash

set -e

if [ -z "$REPOSITORY_URL" ]; then
  export REPOSITORY_URL=https://github.com/neilime/ubuntu-config.git
fi

if [ -z "$REPOSITORY_BRANCH" ]; then
  export REPOSITORY_BRANCH=main
fi

BOLD="$(tput bold 2>/dev/null || printf '')"
GREY="$(tput setaf 0 2>/dev/null || printf '')"
UNDERLINE="$(tput smul 2>/dev/null || printf '')"
RED="$(tput setaf 1 2>/dev/null || printf '')"
GREEN="$(tput setaf 2 2>/dev/null || printf '')"
YELLOW="$(tput setaf 3 2>/dev/null || printf '')"
BLUE="$(tput setaf 4 2>/dev/null || printf '')"
MAGENTA="$(tput setaf 5 2>/dev/null || printf '')"
NO_COLOR="$(tput sgr0 2>/dev/null || printf '')"

info() {
  printf '%s\n' "${BOLD}${GREY}>${NO_COLOR} $*"
}

warn() {
  printf '%s\n' "${YELLOW}! $*${NO_COLOR}"
}

error() {
  printf '%s\n' "${RED}x $*${NO_COLOR}" >&2
}

completed() {
  printf '%s\n' "${GREEN}✓${NO_COLOR} $*"
}

has() {
  command -v "$1" 1>/dev/null 2>&1
}

check_requirements() {
  info "Checking requirements..."
  if [ -z "${BASH_VERSION}" ] || [ -n "${ZSH_VERSION}" ]; then
    # shellcheck disable=SC2016
    utils_echo >&2 'Error: the install instructions explicitly say to pipe the install script to `bash`; please follow them'
    exit 1
  fi

  if ! has sudo; then
    error 'Could not find the command "sudo", needed to get permissions for install.'
    info "rerun this script. Otherwise, please install sudo."
    exit 1
  fi

  # Check if sudo needs password
  if ! sudo -n true 2>/dev/null; then
    if ! sudo -v; then
      error "Superuser not granted, aborting installation"
      exit 1
    fi
  fi
}

ask_for_bitwarden_credentials() {
  if [ -n "$BITWARDEN_EMAIL" ] && [ -n "$BITWARDEN_PASSWORD" ]; then
    return
  fi
  
  while [ -z "$BITWARDEN_EMAIL" ]; do
    read -p "Bitwarden email: " BITWARDEN_EMAIL
  done
  export BITWARDEN_EMAIL

  while [ -z "$BITWARDEN_PASSWORD" ]; do
    read -s -p "Bitwarden password: " BITWARDEN_PASSWORD
  done

  export BITWARDEN_PASSWORD
}

# Install APT softwares
install_pipx() {
  info "Installing pipx..."
  # Install pipx
  if ! command -v pipx &> /dev/null; then
    sudo DEBIAN_FRONTEND=noninteractive apt-get update -y
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends python3-venv pipx
    completed "pipx installation of $i done"
  else
    completed "pipx already installed"
  fi
  sudo PIPX_BIN_DIR=/usr/local/bin pipx ensurepath
}

install_ansible_pull() {
  info "Installing ansible-pull..."
  # Install ansible
  if [ ! -f "/usr/local/bin/ansible-pull" ]; then
    sudo PIPX_BIN_DIR=/usr/local/bin pipx install --force --include-deps ansible
    sudo PIPX_BIN_DIR=/usr/local/bin pipx inject ansible jmespath
    completed "ansible-pull installation done"
  else
    completed "ansible-pull already installed"
  fi
}

run_setup_playbook() {
  info "Running setup playbook..."

  ANSIBLE_USER=${USER}

  sudo ansible-pull \
    --purge \
    -U "$REPOSITORY_URL" \
    -C "$REPOSITORY_BRANCH" \
    -d "/tmp/ubuntu-config" -i "/tmp/ubuntu-config/ansible/inventory.yml" \
    --extra-vars "ansible_user=${ANSIBLE_USER}" \
    --limit "localhost" \
    "/tmp/ubuntu-config/ansible/install-requirements.yml"

  sudo ansible-pull \
    --purge \
    -U "$REPOSITORY_URL" \
    -C "$REPOSITORY_BRANCH" \
    -d "/tmp/ubuntu-config" -i "/tmp/ubuntu-config/ansible/inventory.yml" \
    --extra-vars "ansible_user=${ANSIBLE_USER}" \
    --limit "localhost" \
    "/tmp/ubuntu-config/ansible/install-requirements.yml" \
    "/tmp/ubuntu-config/ansible/setup.yml" \
    "/tmp/ubuntu-config/ansible/cleanup.yml" \
    --diff
}

#######################################

printf "\n%s\n" "#######################################"
printf "#        %s        #\n" "${BOLD}Install ubuntu-config${NO_COLOR}"
printf "%s\n\n" "#######################################"


info "${BOLD}User${NO_COLOR}: ${GREEN}${USER}${NO_COLOR}"
info "${BOLD}Repository url${NO_COLOR}: ${GREEN}${REPOSITORY_URL}${NO_COLOR}"
info "${BOLD}Repository branch${NO_COLOR}: ${GREEN}${REPOSITORY_BRANCH}${NO_COLOR}"

printf "\n%s\n\n" "---------------------------------------"

info "Start installation..."

check_requirements
ask_for_bitwarden_credentials
install_pipx
install_ansible_pull
run_setup_playbook

completed "Installation done"