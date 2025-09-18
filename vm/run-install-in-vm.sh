#!/usr/bin/env sh
set -eu

# Helper to stream the repository's install.sh into the lima VM while
# exporting environment variables sourced from .env (if present).

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$ROOT_DIR/.env"

# Load .env if present
if [ -f "$ENV_FILE" ]; then
	# shellcheck disable=SC1090
	. "$ENV_FILE"
fi

# Build env export prefix for the streamed script (POSIX-safe)
export_vars=""
for var in BITWARDEN_CLIENT_ID BITWARDEN_CLIENT_SECRET BITWARDEN_EMAIL BITWARDEN_PASSWORD SKIP_SETUP SKIP_CLEANUP SKIP_INSTALL_REQUIREMENTS; do
	# Pre-declare val so static analyzers (shellcheck) know it exists.
	val=""
	# POSIX-safe indirect expansion using eval.
	# This sets val to the value of the variable named in $var, or to an empty
	# string if it's undefined. The quoting below is careful to work in /bin/sh.
	eval "val=\"\${${var}-}\""
	# append to the export_vars string
	export_vars="$export_vars $var=\"$val\""
done

echo "Streaming install script into VM and exporting env: BITWARDEN_CLIENT_ID=${BITWARDEN_CLIENT_ID:-unset}"

# Fetch the install script from the host 'git' service and execute it inside the VM
docker compose exec -T git wget -qO- "http://git/?p=ubuntu-config.git;a=blob_plain;f=install.sh;hb=HEAD" |
	limactl shell ubuntu-config-test -- sh -lc "$export_vars USER=$(id -un) HOME=$HOME sh -s --"
