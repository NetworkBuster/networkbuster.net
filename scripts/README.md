# WSL Update Scripts

This folder contains helper scripts to update WSL distributions.

Files:
- `update-wsl.ps1` — PowerShell host script that enumerates WSL distros and runs `apt update && apt full-upgrade -y && apt autoremove -y` inside each. Run from an elevated PowerShell session.
- `update-wsl.sh` — Minimal shell script intended to be run *inside* a WSL distro (e.g., `bash update-wsl.sh`).

Usage (PowerShell host):
- Elevate PowerShell (Run as Administrator)
- Update all distros: `.\scripts\update-wsl.ps1` (or `.\scripts\update-wsl.ps1 -DryRun` to see commands)
- Update a single distro: `.\scripts\update-wsl.ps1 -Distro ubuntu`
- Run the script from a specific folder (e.g., `G:\kodak`):
  - `& 'G:\kodak\networkbuster.net\scripts\update-wsl.ps1' -WorkingDir 'G:\kodak'`
- Run updates as root (non-interactive sudo) with `-UseRoot`:
  - `& 'G:\kodak\networkbuster.net\scripts\update-wsl.ps1' -WorkingDir 'G:\kodak' -UseRoot`
- Register scheduled task that runs updates as root daily and write logs to G:\cadil\logs:
  - `& 'G:\kodak\networkbuster.net\scripts\update-wsl.ps1' -WorkingDir 'G:\kodak' -RegisterScheduledTask -UseRoot -LogDir 'G:\kodak\logs' -ScheduleTime '03:00'`
- One-off run writing log to a specific folder:
  - `& 'G:\kodak\networkbuster.net\scripts\update-wsl.ps1' -WorkingDir 'G:\kodak' -UseRoot -LogDir 'G:\kodak\logs'`

Copying artifacts to a drive
- `scripts/copy-to-drive.ps1` – safely copy LFS artifacts or repo working tree to a destination drive (e.g., `E:` or `G:`):
  - Copy default LFS output to `E:`: `.\	ests\scripts\copy-to-drive.ps1 -DestDrive 'E:'` (run from repo root in PowerShell)
  - Copy entire repo working tree (no `.git`): `.\scripts\copy-to-drive.ps1 -DestDrive 'E:' -IncludeRepo`
  - Write logs to a folder: `.\scripts\copy-to-drive.ps1 -DestDrive 'E:' -LogDir 'E:\logs'`
  - Create a zip after copying: add `-Zip`.

Security note: `-UseRoot` executes the update command as the root user inside WSL (`wsl -d <distro> -u root`). This suppresses sudo prompts but grants the script elevated privileges inside the distro; use with caution.

Usage (inside WSL):
- `chmod +x scripts/update-wsl.sh && ./scripts/update-wsl.sh`

Scheduling:
- Register a daily scheduled task that runs the script (requires elevated PowerShell):
  - `.\scripts\update-wsl.ps1 -WorkingDir 'G:\kodak' -RegisterScheduledTask -ScheduleTime '03:00'`
  - This creates/updates a scheduled task named `WSL-Update` to run daily at the specified time.

Safety notes:
- These scripts use `sudo` inside WSL; you'll be prompted for the distro user's password if required.
- Review and run manually if you need more control over upgrades or reboots.
