#!/usr/bin/env bash

set -euo pipefail

vm_name="${1:-ubuntu-config-v1}"
ssh_host="lima-${vm_name}"
tooling_image="${TOOLING_IMAGE:-ubuntu-config-tooling:local}"
host_home="${HOME}"
workspace_dir="$(pwd)"
ssh_config_path="${host_home}/.lima/${vm_name}/ssh.config"
report_dir="${REPORTS_DIR:-}"
report_host_file=""
pytest_junit_option=""

if [[ -n "$report_dir" ]]; then
	report_host_file="$report_dir/tests/e2e-test.junit.xml"
	pytest_junit_option="--junitxml=/workspace/$report_host_file"
	mkdir -p "$(dirname "$report_host_file")"
fi

docker run --rm \
	--network host \
	--user "$(id -u):$(id -g)" \
	--env HOME=/tmp \
	--env XDG_CACHE_HOME=/tmp/.cache \
	--env PIP_DISABLE_PIP_VERSION_CHECK=1 \
	--volume /etc/passwd:/etc/passwd:ro \
	--volume /etc/group:/etc/group:ro \
	--volume "$workspace_dir:/workspace" \
	--volume "$host_home/.lima:$host_home/.lima:ro" \
	--workdir /workspace \
	"$tooling_image" \
	bash -lc "
set -euo pipefail
python3 -m pip install --user -q -r e2e-tests/requirements.txt
export PATH=\"\$HOME/.local/bin:\$PATH\"
if [ -n \"$pytest_junit_option\" ]; then
	pytest -q -o cache_dir=/tmp/pytest-cache \
		--ssh-config=\"$ssh_config_path\" \
		--hosts=\"ssh://$ssh_host\" \
		\"$pytest_junit_option\" \
		e2e-tests
else
	pytest -q -o cache_dir=/tmp/pytest-cache \
		--ssh-config=\"$ssh_config_path\" \
		--hosts=\"ssh://$ssh_host\" \
		e2e-tests
fi
"
