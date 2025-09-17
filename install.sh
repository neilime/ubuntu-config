#!/usr/bin/env sh
# -----------------------------------------------------------------------------
# Script: install.sh
# Description: This script automates the setup of an Ubuntu system by:
#              - Checking system requirements
#              - Installing necessary tools (pipx, ansible-pull, git)
#              - Running Ansible playbooks for configuration
#
# Usage:
#   Run this script using `sh install.sh`. Ensure you have the necessary
#   permissions to execute the script and install software.
#
# Main Actions:
#   1. Check system requirements (e.g., sudo availability, shell compatibility).
#   2. Prompt for Bitwarden credentials (email/password or API key) if not already set.
#   3. Install pipx, ansible-pull, and git if not already installed.
#   4. Run Ansible playbooks to configure the system.
#
# Supported Environment Variables:
#   - REPOSITORY_URL: URL of the Git repository containing the Ansible playbooks.
#                     Default: https://github.com/neilime/ubuntu-config.git
#   - REPOSITORY_BRANCH: Branch of the repository to use.
#                        Default: main
#   - BITWARDEN_EMAIL: Email address for Bitwarden login.
#   - BITWARDEN_PASSWORD: Password for Bitwarden login.
#   - BITWARDEN_CLIENT_ID: Client ID for Bitwarden API key authentication (alternative to email/password).
#   - BITWARDEN_CLIENT_SECRET: Client Secret for Bitwarden API key authentication (alternative to email/password).
#   - SKIP_INSTALL_REQUIREMENTS: If set to "true", the install-requirements playbook will be skipped.
#   - INSTALL_REQUIREMENTS_TAGS: Tags to filter tasks in the "install-requirements" playbook. Default: all
#   - SKIP_SETUP: If set to "true", the setup playbook will be run.
#   - SETUP_TAGS: Tags to filter tasks in the "setup" playbook. Default: all
#   - SKIP_CLEANUP: If set to "true", the cleanup playbook will be skipped.
#   - CLEANUP_TAGS: Tags to filter tasks in the "cleanup" playbook. Default: all
#
# Requirements:
#   - A POSIX-compliant shell (e.g., `sh`).
#   - `sudo` must be installed and configured.
#   - Internet access to download dependencies and clone repositories.
#
# Notes:
#   - Avoid running this script with `zsh` or non-POSIX `bash` as it may cause errors.
#   - The script will prompt for missing environment variables if not set.
#
# Exit Codes:
#   - 0: Success
#   - Non-zero: An error occurred during execution.
#
# -----------------------------------------------------------------------------

set -eu
printf '\n'

BOLD="$(tput bold 2>/dev/null || printf '')"
GREY="$(tput setaf 0 2>/dev/null || printf '')"
RED="$(tput setaf 1 2>/dev/null || printf '')"
GREEN="$(tput setaf 2 2>/dev/null || printf '')"
YELLOW="$(tput setaf 3 2>/dev/null || printf '')"
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
	if [ -z "$1" ]; then
		error "No command provided to check"
		return 1
	fi

	if [ -z "${2+x}" ]; then
		with_sudo=false
	else
		with_sudo=true
	fi

	if $with_sudo; then
		sudo -i command -v "$1" 1>/dev/null 2>&1
	else
		command -v "$1" 1>/dev/null 2>&1
	fi
}

check_requirements() {
	info "Checking requirements..."
	if env_var_is_not_empty "ZSH_VERSION"; then
		error "Running installation script with \`zsh\` is known to cause errors."
		error "Please use \`sh\` instead."
		exit 1
	elif env_var_is_not_empty "BASH_VERSION" && ! env_var_is_not_empty "POSIXLY_CORRECT"; then
		error "Running installation script with non-POSIX \`bash\` may cause errors."
		error "Please use \`sh\` instead."
		exit 1
	else
		true # No-op: no issues detected
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
	info "Asking for Bitwarden credentials..."

	# Check if API key credentials are provided
	if env_var_is_not_empty "BITWARDEN_CLIENT_ID" && env_var_is_not_empty "BITWARDEN_CLIENT_SECRET"; then
		completed "Bitwarden API key credentials already set"

		# Even with API key, we still need the master password to unlock the vault
		if ! env_var_is_not_empty "BITWARDEN_PASSWORD"; then
			prompt_for_env_variable "BITWARDEN_PASSWORD" "Enter your Bitwarden master password (required to unlock vault): " true
		fi
		return
	fi

	# Check if email/password credentials are provided
	if env_var_is_not_empty "BITWARDEN_EMAIL" && env_var_is_not_empty "BITWARDEN_PASSWORD"; then
		completed "Bitwarden email/password credentials already set"
		return
	fi

	# If neither set of credentials is complete, prompt for email/password (default)
	if ! env_var_is_not_empty "BITWARDEN_EMAIL"; then
		prompt_for_env_variable "BITWARDEN_EMAIL" "Enter your Bitwarden email (or leave empty to use API key): " false false
	fi

	# If email is provided but password is not, prompt for password
	if env_var_is_not_empty "BITWARDEN_EMAIL" && ! env_var_is_not_empty "BITWARDEN_PASSWORD"; then
		prompt_for_env_variable "BITWARDEN_PASSWORD" "Enter your Bitwarden password: " true
	fi

	# If email is empty, prompt for API key credentials
	if ! env_var_is_not_empty "BITWARDEN_EMAIL"; then
		if ! env_var_is_not_empty "BITWARDEN_CLIENT_ID"; then
			prompt_for_env_variable "BITWARDEN_CLIENT_ID" "Enter your Bitwarden API Client ID: " false
		fi

		if ! env_var_is_not_empty "BITWARDEN_CLIENT_SECRET"; then
			prompt_for_env_variable "BITWARDEN_CLIENT_SECRET" "Enter your Bitwarden API Client Secret: " true
		fi

		# Even with API key, we still need the master password to unlock the vault
		if ! env_var_is_not_empty "BITWARDEN_PASSWORD"; then
			prompt_for_env_variable "BITWARDEN_PASSWORD" "Enter your Bitwarden master password (required to unlock vault): " true
		fi
	fi

	completed "Bitwarden credentials set"
}

prompt_for_env_variable() {
	var_name="$1"
	prompt_text="$2"
	secret="$3"
	required="${4:-true}"
	max_attempts=10
	attempts=0

	while true; do
		# Evaluate variable value at runtime
		eval current_value="\${$var_name:-}"

		if [ -n "$current_value" ]; then
			break
		fi

		if [ "$attempts" -ge "$max_attempts" ]; then
			error "Too many failed attempts to provide $var_name" >&2
			exit 1
		fi

		if [ "$secret" = "true" ]; then
			printf "%s" "$prompt_text"
			stty -echo
			read -r input_value
			stty echo
			printf "\n"
		else
			printf "%s" "$prompt_text"
			read -r input_value
		fi

		if [ -z "$input_value" ]; then
			if [ "$required" = "false" ]; then
				# Allow empty value for optional variables
				break
			fi

			warn "$var_name cannot be empty. Please try again." >&2
			attempts=$((attempts + 1))
		else
			# Set and export the variable
			eval "$var_name=\"$input_value\""
			export var_name
		fi
	done
}

env_var_is_not_empty() {
	if [ -z "$1" ]; then
		error "No variable name provided to check"
		return 1
	fi

	eval var_value="\${$1:-}"

	if [ -n "$var_value" ]; then
		return 0
	else
		return 1
	fi
}

install_pipx() {
	info "Installing pipx..."

	# Install pipx
	if ! has pipx; then
		sudo DEBIAN_FRONTEND=noninteractive apt-get update -y
		sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends python3-venv pipx

		# Ensure pipx binaries are in PATH
		if ! has pipx; then
			error "pipx installation failed: pipx command not found after installation"
			exit 1
		fi

		completed "pipx installation done"
	else
		completed "pipx already installed"
	fi

	sudo PIPX_BIN_DIR=/usr/local/bin pipx ensurepath --force
}

install_ansible_pull() {
	info "Installing ansible-pull..."

	if ! has ansible-pull true; then
		sudo PIPX_BIN_DIR=/usr/local/bin pipx install --force --include-deps ansible
		sudo PIPX_BIN_DIR=/usr/local/bin pipx inject ansible nbconvert jmespath

		if ! has ansible-pull true; then
			error "ansible-pull installation failed: ansible-pull command not found after installation"
			exit 1
		fi

		completed "ansible-pull installation done"
	else
		completed "ansible-pull already installed"
	fi
}

install_git() {
	info "Installing git..."

	if ! has git; then
		sudo apt update
		sudo apt install -y git

		if ! has git; then
			error "Git installation failed: git command not found after installation"
			exit 1
		fi

		completed "git installation done"
	else
		completed "Git is already installed"
	fi
}

run_install_requirements_playbook() {

	if [ -n "${SKIP_INSTALL_REQUIREMENTS+x}" ] && [ "$SKIP_INSTALL_REQUIREMENTS" = "true" ]; then
		completed "Skipping install-requirements playbook"
		return
	fi

	if [ -z "${INSTALL_REQUIREMENTS_TAGS+x}" ]; then
		INSTALL_REQUIREMENTS_TAGS="all"
	fi

	run_playbook "install-requirements" --tags "$INSTALL_REQUIREMENTS_TAGS"
}

run_setup_playbook() {
	if [ -n "${SKIP_SETUP+x}" ] && [ "$SKIP_SETUP" = "true" ]; then
		completed "Skipping setup playbook"
		return
	fi

	if [ -z "${SETUP_TAGS+x}" ]; then
		SETUP_TAGS="all"
	fi

	# Build extra-vars for Bitwarden credentials, only if defined
	extra_vars=""
	if [ -n "${BITWARDEN_EMAIL:-}" ]; then
		extra_vars="$extra_vars --extra-vars BITWARDEN_EMAIL=$BITWARDEN_EMAIL"
	fi
	if [ -n "${BITWARDEN_PASSWORD:-}" ]; then
		extra_vars="$extra_vars --extra-vars BITWARDEN_PASSWORD=$BITWARDEN_PASSWORD"
	fi
	if [ -n "${BITWARDEN_CLIENT_ID:-}" ]; then
		extra_vars="$extra_vars --extra-vars BITWARDEN_CLIENT_ID=$BITWARDEN_CLIENT_ID"
	fi
	if [ -n "${BITWARDEN_CLIENT_SECRET:-}" ]; then
		extra_vars="$extra_vars --extra-vars BITWARDEN_CLIENT_SECRET=$BITWARDEN_CLIENT_SECRET"
	fi

	# Use eval to properly expand the extra_vars
	if [ -n "$extra_vars" ]; then
		eval "run_playbook \"setup\" --tags \"$SETUP_TAGS\" $extra_vars"
	else
		run_playbook "setup" --tags "$SETUP_TAGS"
	fi
}

run_cleanup_playbook() {
	if [ -n "${SKIP_CLEANUP+x}" ] && [ "$SKIP_CLEANUP" = "true" ]; then
		completed "Skipping cleanup playbook"
		return
	fi

	if [ -z "${CLEANUP_TAGS+x}" ]; then
		CLEANUP_TAGS="all"
	fi

	run_playbook "cleanup" --tags "$CLEANUP_TAGS"
}

run_playbook() {
	if [ -z "$1" ]; then
		error "No playbook name provided to run"
		return 1
	fi

	playbook_name="$1"
	shift

	info "Running \"$playbook_name\" playbook..."

	sudo ansible-pull \
		--purge \
		-U "$REPOSITORY_URL" \
		-C "$REPOSITORY_BRANCH" \
		-d "/tmp/ubuntu-config" -i "/tmp/ubuntu-config/ansible/inventory.yml" \
		--extra-vars "ansible_user=${USER}" \
		--limit "localhost" \
		-v \
		"$@" \
		"/tmp/ubuntu-config/ansible/$playbook_name.yml" || {
		error "Playbook \"$playbook_name\" failed"
		exit 1
	}

	completed "Playbook \"$playbook_name\" done"
}

#######################################

printf "\n%s\n" "#######################################"
printf "#        %s        #\n" "${GREEN}Install ${BOLD}ubuntu-config${NO_COLOR}"
printf "%s\n\n" "#######################################"

if ! env_var_is_not_empty "REPOSITORY_URL"; then
	export REPOSITORY_URL=https://github.com/neilime/ubuntu-config.git
fi

if ! env_var_is_not_empty "REPOSITORY_BRANCH"; then
	export REPOSITORY_BRANCH=main
fi

info "${BOLD}User${NO_COLOR}: ${GREEN}${USER}${NO_COLOR}"
info "${BOLD}Repository url${NO_COLOR}: ${GREEN}${REPOSITORY_URL}${NO_COLOR}"
info "${BOLD}Repository branch${NO_COLOR}: ${GREEN}${REPOSITORY_BRANCH}${NO_COLOR}"
info "${BOLD}Bitwarden email${NO_COLOR}: ${GREEN}${BITWARDEN_EMAIL:-not set}${NO_COLOR}"
info "${BOLD}Bitwarden password${NO_COLOR}: ${GREEN}$([ -n "${BITWARDEN_PASSWORD:-}" ] && echo '********' || echo 'not set')${NO_COLOR}"
info "${BOLD}Bitwarden client ID${NO_COLOR}: ${GREEN}${BITWARDEN_CLIENT_ID:-not set}${NO_COLOR}"
info "${BOLD}Bitwarden client secret${NO_COLOR}: ${GREEN}$([ -n "${BITWARDEN_CLIENT_SECRET:-}" ] && echo '********' || echo 'not set')${NO_COLOR}"

info "${BOLD}Skip install-requirements${NO_COLOR}: ${GREEN}${SKIP_INSTALL_REQUIREMENTS:-not set}${NO_COLOR}"
info "${BOLD}Skip setup${NO_COLOR}: ${GREEN}${SKIP_SETUP:-not set}${NO_COLOR}"
info "${BOLD}Skip cleanup${NO_COLOR}: ${GREEN}${SKIP_CLEANUP:-not set}${NO_COLOR}"

info "${BOLD}Install-requirements tags${NO_COLOR}: ${GREEN}${INSTALL_REQUIREMENTS_TAGS:-all}${NO_COLOR}"
info "${BOLD}Setup tags${NO_COLOR}: ${GREEN}${SETUP_TAGS:-all}${NO_COLOR}"
info "${BOLD}Cleanup tags${NO_COLOR}: ${GREEN}${CLEANUP_TAGS:-all}${NO_COLOR}"

printf "\n%s\n\n" "---------------------------------------"

info "Start installation..."

check_requirements || {
	error "Requirements check failed"
	exit 1
}

ask_for_bitwarden_credentials || {
	error "Bitwarden credentials check failed"
	exit 1
}

install_pipx || {
	error "pipx installation failed"
	exit 1
}

install_ansible_pull || {
	error "ansible-pull installation failed"
	exit 1
}

install_git || {
	error "git installation failed"
	exit 1
}

run_install_requirements_playbook || {
	error "Install-requirements playbook failed"
	exit 1
}

run_setup_playbook || {
	error "Setup playbook failed"
	exit 1
}

run_cleanup_playbook || {
	error "Cleanup playbook failed"
	exit 1
}

completed "Installation done"
