#!/usr/bin/env bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"

KEY_PATH="$SCRIPT_DIR/id_rsa"

if [ -f "$KEY_PATH" ]; then
  echo "SSH key already exists"
else
  ssh-keygen -t rsa -b 4096 -f "$KEY_PATH" -N ""
fi

CLOUD_INIT_CONFIG=$(cat <<EOF
#cloud-config
users:
  - name: ubuntu
    sudo: ['ALL=(ALL) NOPASSWD:ALL']
    ssh-authorized-keys:
      - $(cat $KEY_PATH.pub)
EOF
)

echo "$CLOUD_INIT_CONFIG" >"$SCRIPT_DIR/cloud-init.yaml"