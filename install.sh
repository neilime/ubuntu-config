#!/usr/bin/env sh

set -eu
printf '\n'

if [ -z "$REPOSITORY_URL" ]; then
	export REPOSITORY_URL=https://github.com/neilime/ubuntu-config.git
fi

if [ -z "$REPOSITORY_BRANCH" ]; then
	export REPOSITORY_BRANCH=main
fi

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
	if [ -n "${ZSH_VERSION+x}" ]; then
		error "Running installation script with \`zsh\` is known to cause errors."
		error "Please use \`sh\` instead."
		exit 1
	elif [ -n "${BASH_VERSION+x}" ] && [ -z "${POSIXLY_CORRECT+x}" ]; then
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

	if [ -n "${BITWARDEN_EMAIL+x}" ] && [ -n "${BITWARDEN_PASSWORD+x}" ]; then
		completed "Bitwarden credentials already set"
		return
	fi

	if [ -z "${BITWARDEN_EMAIL+x}" ]; then
		prompt_for_env_variable "BITWARDEN_EMAIL" "Enter your Bitwarden email: " false
	fi

	if [ -z "${BITWARDEN_PASSWORD+x}" ]; then
		prompt_for_env_variable "BITWARDEN_PASSWORD" "Enter your Bitwarden password: " true
	fi

	completed "Bitwarden credentials set"
}

prompt_for_env_variable() {
	var_name="$1"
	prompt_text="$2"
	secret="$3"
	max_attempts=10
	attempts=0

	while true; do
		# Evaluate variable value at runtime
		eval current_value="\$$var_name"

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
			warn "$var_name cannot be empty. Please try again." >&2
			attempts=$((attempts + 1))
		else
			# Set and export the variable
			eval "$var_name=\"$input_value\""
			export var_name
		fi
	done
}

install_pipx() {
	info "Installing pipx..."

	# Install pipx
	if ! has pipx; then
		sudo DEBIAN_FRONTEND=noninteractive apt-get update -y
		sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends python3-venv pipx
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
		sudo PIPX_BIN_DIR=/usr/local/bin pipx inject ansible jmespath
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
		completed "git installation done"
	else
		completed "Git is already installed"
	fi
}

run_setup_playbook() {

	ANSIBLE_USER=${USER}

	info "Running \"install-requirements\" playbook..."
	sudo ansible-pull \
		--purge \
		-U "$REPOSITORY_URL" \
		-C "$REPOSITORY_BRANCH" \
		-d "/tmp/ubuntu-config" -i "/tmp/ubuntu-config/ansible/inventory.yml" \
		--extra-vars "ansible_user=${ANSIBLE_USER}" \
		--limit "localhost" \
		-v \
		"/tmp/ubuntu-config/ansible/install-requirements.yml" || {
		error "Playbook \"install-requirements\" failed"
		exit 1
	}

	completed "Playbook \"install-requirements\" done"

	info "Running \"setup\" and \"cleanup\" playbooks..."
	sudo ansible-pull \
		--purge \
		-U "$REPOSITORY_URL" \
		-C "$REPOSITORY_BRANCH" \
		-d "/tmp/ubuntu-config" -i "/tmp/ubuntu-config/ansible/inventory.yml" \
		--extra-vars "ansible_user=${ANSIBLE_USER}" \
		--extra-vars "BITWARDEN_EMAIL=${BITWARDEN_EMAIL}" \
		--extra-vars "BITWARDEN_PASSWORD=${BITWARDEN_PASSWORD}" \
		--limit "localhost" \
		"/tmp/ubuntu-config/ansible/setup.yml" \
		"/tmp/ubuntu-config/ansible/cleanup.yml" \
		--diff \
		-v || {
		error "Playbook \"setup\" and \"cleanup\" failed"
		exit 1
	}

	completed "Playbook \"setup\" and \"cleanup\" done"
}

#######################################

printf "\n%s\n" "#######################################"
printf "#        %s        #\n" "${GREEN}Install ${BOLD}ubuntu-config${NO_COLOR}"
printf "%s\n\n" "#######################################"

info "${BOLD}User${NO_COLOR}: ${GREEN}${USER}${NO_COLOR}"
info "${BOLD}Repository url${NO_COLOR}: ${GREEN}${REPOSITORY_URL}${NO_COLOR}"
info "${BOLD}Repository branch${NO_COLOR}: ${GREEN}${REPOSITORY_BRANCH}${NO_COLOR}"

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

run_setup_playbook || {
	error "Playbook run failed"
	exit 1
}

completed "Installation done"
