# nbapp Install Helper

This document explains how to use `install-nbapp-service.ps1` to fetch, build, and optionally install
`github.com/NetworkBuster/nbapp` as a Windows service using the existing NSSM helper.

Quick usage:

- Clone/build only (no service):
  ```powershell
  .\install-nbapp-service.ps1 -Repo 'https://github.com/NetworkBuster/nbapp.git' -InstallDir 'C:\apps\nbapp'
  ```

- Clone/build and install as a service (UAC required):
  ```powershell
  .\install-nbapp-service.ps1 -InstallDir 'C:\apps\nbapp' -InstallService -ServiceName 'nbapp'
  ```

Notes & prerequisites:

- `git` must be on PATH. The script will clone or update the target directory.
- If the app uses Node, `npm` should be available to run `npm install`. The script will attempt to find
  a node runtime in either `tools/node` (repo-local) or system PATH.
- Installing the service requires elevation (UAC). The script delegates to `install-service-nssm.ps1` which
  will download/install NSSM if missing and register a Windows service named as provided.
- The script attempts to choose the correct start command (`node <file>` or `npm start`). For complex start
  commands you may need to review and edit the `AppArgs` after installation.

Logs and files:

- Application installation dir: whatever you pass in `-InstallDir` (default `S:\apps\nbapp`).
- Service logs are written to the provided `-LogDir` (default `S:\apps\nbapp\logs`).

If you want, I can also:

- Automatically enable firewall rules for the installed service, or
- Run the installer non-interactively and attempt to start the service now (requires UAC).
