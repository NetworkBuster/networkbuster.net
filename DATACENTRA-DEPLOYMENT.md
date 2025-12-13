# DATACENTRA Branch Deployment

## Overview
The DATACENTRA branch is a deployment branch for the NetworkBuster.net project.

## Branch Information
- **Branch Name**: DATACENTRA
- **Purpose**: Deployment target for DATACENTRA environment
- **Base Branch**: copilot/push-to-datacentra

## Pushing to Remote

To push the DATACENTRA branch to the remote origin repository, use:

```bash
git push -u origin DATACENTRA
```

Or run the provided script:

```bash
./push-to-datacentra.sh
```

## Prerequisites
- Git installed and configured
- Appropriate GitHub authentication (HTTPS or SSH)
- Write access to the NetworkBuster/networkbuster.net repository

## Branch Status
The DATACENTRA branch has been created locally and is ready to be pushed to origin.

## Notes
- The `-u` flag sets up tracking between the local DATACENTRA branch and remote origin/DATACENTRA
- After the first push with `-u`, subsequent pushes can be done with just `git push`
