#!/usr/bin/env bash
# Simple script to run inside WSL distro to update packages
set -euo pipefail

echo "Running apt update && full-upgrade && autoremove inside WSL distro"
sudo apt update
sudo apt full-upgrade -y
sudo apt autoremove -y

echo "Update complete"
