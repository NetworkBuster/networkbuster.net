# Installer package selection: Power Modules

Provide optional packages and toggles during installation for power subsystem support.

Packages:
- `power-monitor` : telemetry & dashboard hooks (required for display)
- `mppt-driver` : MPPT controller driver and calibration tools
- `bms-driver` : Battery management and SOC monitor
- `wakonradio` : Wake-on-Radio radio firmware / kernel hooks

UI toggles:
- Enable Power Telemetry (on/off)
- Select battery chemistry (LiFePO4/Li-ion/supercap)
- Enable automatic power-mode switching
- Configure upload interval and retention

Installation notes:
- Add post-install scripts to load kernel modules or firmware blobs for specialized radios and MPPT controllers
- Offer a test-harness to run the simulation or run device calibration routines
