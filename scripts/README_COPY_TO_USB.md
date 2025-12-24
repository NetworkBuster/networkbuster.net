# Copy Project to USB - Scripts

This folder contains helper scripts to copy the repository to a USB flash drive.

Files:
- `copy-project-to-usb.sh` — Generic macOS/Linux script (rsync/zip, excludes configurable).
- `copy-project-to-usb-custom.sh` — Wrapper that defaults SOURCE to the repo root (parent of `scripts/`).
- `Copy-ProjectToUsb.ps1` — Windows PowerShell helper (uses `robocopy` or `Compress-Archive`).

Examples:
- macOS/Linux: `./scripts/copy-project-to-usb.sh . /Volumes/FLASHDRIVE/project`
- Create zip: `./scripts/copy-project-to-usb.sh . /Volumes/FLASHDRIVE -z -c`
- Auto-detect and prompt for mount: `./scripts/copy-project-to-usb.sh . -a`
- Auto-detect and accept first mount: `./scripts/copy-project-to-usb.sh . -A`
- Custom wrapper: `./scripts/copy-project-to-usb-custom.sh /Volumes/FLASHDRIVE/NetworkBuster`
- Windows PowerShell: `.\scripts\Copy-ProjectToUsb.ps1 -Destination 'E:\NetworkBuster'`
- Windows PowerShell (auto-detect): `.\scripts\Copy-ProjectToUsb.ps1 -AutoDetect`

Notes:
- The scripts exclude `node_modules`, `.git`, and `dist` by default. Add additional excludes with `-e` (bash) or `-Exclude` (PowerShell).
- Use `-a` to auto-detect mount points and prompt for selection, or `-A` to auto-select the first detected mount on macOS/Linux.
- PowerShell supports `-AutoDetect` to detect removable drives and prompt selection when multiple are present.
- Make the shell scripts executable: `chmod +x scripts/*.sh` on macOS/Linux.
- Verify free space on the USB drive before copying.
