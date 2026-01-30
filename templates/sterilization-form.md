# Sterilization Record

```yaml
# Example sterilization record
date: 2025-12-21T10:00:00Z
technician: Jane Doe
instrument:
  id: NB-12345
  model: EnviroProbe
  serial: SN-0001
location: Field - Vehicle A
checklist:
  pre_clean: true
  mechanical_clean: true
  disinfection: true
  uvc_used: false
  functional_check: true
notes: "No visible contamination after cleaning. Optical alignment within tolerance."
files:
  photos: ["photos/instrument_before.jpg","photos/instrument_after.jpg"]
```

Fill and store one record per procedure; keep copies in `data/sterilization-records/` for auditing.
