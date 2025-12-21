# Plan: Install as Windows Service (NSSM) — Steps & Considerations

Goal: run NetworkBuster as a native Windows service with automatic restart and robust management.

Steps (high level):
1. Download NSSM (https://nssm.cc) and place `nssm.exe` in a fixed path (e.g., `C:\tools\nssm\nssm.exe`).
3. Install service (example using NSSM):
   - Install script included: `scripts/install-service-nssm.ps1` (run as Administrator)
   - Example manual command: `nssm install NetworkBuster "powershell.exe" "-NoProfile -ExecutionPolicy Bypass -File \"S:\NetworkBuster_Production\scripts\watchdog.ps1\" -AppExe \"C:\Program Files\nodejs\node.exe\" -AppArgs \"start-servers.js\" -WorkingDir \"S:\NetworkBuster_Production\" -LogDir \"S:\NetworkBuster_Production\logs\" -HealthUrl \"http://localhost:3001/api/health\"`
   - Configure Startup directory: `S:\NetworkBuster_Production`
3. Configure service settings via NSSM (or nssm set commands):
   - Log output to `S:\NetworkBuster_Production\logs\service.out.log` and `service.err.log`.
   - On exit, set Restart on unexpected exit, with a delay (e.g., 5 seconds) and no back-off limit.
4. Set Windows Recovery options (Services.msc > Recovery): First failure: Restart Service; Second failure: Restart; Subsequent: Run Program/Restart.
5. Configure service to run under a dedicated service account if the app needs network or drive access to mapped volumes (create `NetworkBusterSvc` with least privileges and grant necessary file permissions to S:).
6. Health checking: configure a secondary small monitor process or use NSSM's stdout health hooks; consider a scheduled monitor script to verify `/api/health` and restart service via `nssm restart` if necessary.

Notes & safety:
- Installing a service requires admin privileges.
- If you prefer an installed, signed service, consider building a real Windows Service wrapper (.NET worker) which provides tighter integration and telemetry.

Rollback:
- nssm remove NetworkBuster confirm
- Remove service account permissions

I can implement this plan once you confirm and grant admin for install steps (or I can provide a script you run as admin).