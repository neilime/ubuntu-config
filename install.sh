#!/usr/bin/env sh

set -eu

REPOSITORY_URL="${REPOSITORY_URL:-https://github.com/neilime/ubuntu-config.git}"
REPOSITORY_BRANCH="${REPOSITORY_BRANCH:-main}"
ANSIBLE_CHECKOUT_DIR="${ANSIBLE_CHECKOUT_DIR:-/tmp/ubuntu-config-v1}"
TARGET_USER="${UBUNTU_CONFIG_USER:-${SUDO_USER:-${USER:-ubuntu}}}"
TARGET_USER_HOME="${UBUNTU_CONFIG_USER_HOME:-${HOME:-/home/${TARGET_USER}}}"

info() {
	printf '%s\n' "> $*"
}

fail() {
	printf '%s\n' "x $*" >&2
	exit 1
}

require_sudo() {
	command -v sudo >/dev/null 2>&1 || fail "sudo is required"
	sudo -v || fail "sudo access is required"
}

install_bootstrap_packages() {
	if command -v ansible-playbook >/dev/null 2>&1 && command -v ansible-pull >/dev/null 2>&1; then
		return
	fi

	info "Installing bootstrap packages"
	sudo apt-get update
	sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
		ansible-core \
		ca-certificates \
		git
}

run_ansible_pull() {
	info "Running ansible-pull from $REPOSITORY_URL#$REPOSITORY_BRANCH"
	sudo env \
		UBUNTU_CONFIG_USER="$TARGET_USER" \
		UBUNTU_CONFIG_USER_HOME="$TARGET_USER_HOME" \
		ansible-pull \
		-U "$REPOSITORY_URL" \
		-C "$REPOSITORY_BRANCH" \
		-d "$ANSIBLE_CHECKOUT_DIR" \
		-i "localhost," \
		-c local \
		ansible/setup.yml
}

main() {
	require_sudo
	install_bootstrap_packages
	run_ansible_pull

	info "Installation completed"
}

main "$@"
