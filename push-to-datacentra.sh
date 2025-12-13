#!/bin/bash
# Script to push the DATACENTRA branch to remote origin
# This script should be run with proper GitHub authentication

set -e

echo "Pushing DATACENTRA branch to origin..."
git push -u origin DATACENTRA:DATACENTRA

if [ $? -eq 0 ]; then
    echo "Successfully pushed DATACENTRA branch to origin"
    echo "Branch DATACENTRA is now tracking origin/DATACENTRA"
else
    echo "Failed to push DATACENTRA branch"
    exit 1
fi
