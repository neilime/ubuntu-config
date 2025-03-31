#!/usr/bin/env bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"

KEY_PATH="$SCRIPT_DIR/id_rsa"

if [ -f "$KEY_PATH" ]; then
	echo "SSH key already exists"
else
	ssh-keygen -t rsa -b 4096 -f "$KEY_PATH" -N ""
fi

SSH_PUBLIC_KEY=$(cat "$KEY_PATH.pub")
