Notifications and Labels

- MQTT alerts: enable by setting environment variable `CHECK_MON_MQTT=1` and optionally `CHECK_MON_MQTT_HOST`, `CHECK_MON_MQTT_PORT`, `CHECK_MON_MQTT_TOPIC`.
- Email alerts: enable by setting `CHECK_MON_EMAIL=1` and SMTP settings `CHECK_MON_SMTP_HOST`, `CHECK_MON_SMTP_PORT`, `CHECK_MON_FROM`, `CHECK_MON_TO`, `CHECK_MON_SMTP_USER`, `CHECK_MON_SMTP_PASS`.

Label generation:
- Run `python firmware/generate_labels.py --db firmware/checksums_db.json --out labels --base-url "https://github.com/Cleanskiier27/Networkbuster.net/releases"`
- PNGs and a PDF will be created in `labels/` ready for printing.

Dashboard integration:
- `checksum_monitor.py` writes `firmware/last_scan.json` and `web-app/data/checksums.json` for dashboard consumption.
