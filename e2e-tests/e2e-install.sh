#!/usr/bin/env bash

set -euo pipefail

vm_name="${1:-ubuntu-config-v1}"
origin_url="$(git config --get remote.origin.url)"
target_user="$(limactl shell --workdir / "$vm_name" whoami | tr -d '\r')"
target_user_home="$(limactl shell --workdir / "$vm_name" env sh -lc 'printenv HOME' | tr -d '\r')"

command -v curl >/dev/null 2>&1 || {
	printf '%s\n' "curl is required" >&2
	exit 1
}

branch_name="${E2E_REPOSITORY_REF:-$(git branch --show-current)}"

if [[ -z "$branch_name" ]]; then
	branch_name="$(git rev-parse HEAD)"
fi

case "$origin_url" in
git@github.com:*)
	repo_path="${origin_url#git@github.com:}"
	;;
https://github.com/*)
	repo_path="${origin_url#https://github.com/}"
	;;
ssh://git@github.com/*)
	repo_path="${origin_url#ssh://git@github.com/}"
	;;
*)
	printf '%s\n' "unsupported origin URL for e2e install: $origin_url" >&2
	exit 1
	;;
esac

repo_path="${repo_path%.git}"
install_script_url="https://raw.githubusercontent.com/${repo_path}/${branch_name}/install.sh"

curl -fsSL "$install_script_url" |
	limactl shell --workdir / "$vm_name" \
		env \
		REPOSITORY_URL="https://github.com/${repo_path}.git" \
		REPOSITORY_BRANCH="$branch_name" \
		UBUNTU_CONFIG_USER="$target_user" \
		UBUNTU_CONFIG_USER_HOME="$target_user_home" \
		sh
