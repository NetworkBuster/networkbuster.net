#!/usr/bin/env sh
# Generated add-admin script for request 67f6a780a186
# REVIEW BEFORE RUNNING AS ROOT
set -euo pipefail

USERNAME=test-admin
PUBKEY_B64='c3NoLXJzYSBBQUFBQjNUZXN0S2V5'

# create user if not exists
if ! id "$USERNAME" >/dev/null 2>&1; then
  useradd -m -s /bin/bash "$USERNAME"
fi
mkdir -p /home/$USERNAME/.ssh
# decode base64 pubkey to authorized_keys
echo "$PUBKEY_B64" | base64 -d > /home/$USERNAME/.ssh/authorized_keys
chmod 600 /home/$USERNAME/.ssh/authorized_keys
chown -R $USERNAME:$USERNAME /home/$USERNAME/.ssh

# add user to wheel or admin group if exists
if getent group sudo >/dev/null 2>&1; then
  usermod -aG sudo "$USERNAME" || true
fi
if getent group wheel >/dev/null 2>&1; then
  usermod -aG wheel "$USERNAME" || true
fi

# Additional: create limited sudoers entry

# Add restricted sudoers entry (edit per policy)
echo "test-admin ALL=(ALL) NOPASSWD: /usr/bin/systemctl, /bin/journalctl" > /etc/sudoers.d/test-admin
chmod 440 /etc/sudoers.d/test-admin


echo "User $USERNAME created and ssh key installed. Please verify sudoers entry at /etc/sudoers.d/$USERNAME."
