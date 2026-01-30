"""
Backup installers script
Copies installers to a timestamped backup folder and records a manifest.
"""

import os
import shutil
from datetime import datetime
import hashlib
import json

INSTALLERS_DIR = os.path.join(os.path.dirname(__file__), 'installers')
BACKUP_ROOT = os.environ.get('INSTALLER_BACKUP_DIR', os.path.join(os.path.dirname(__file__), 'backups'))


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def backup_installers():
    if not os.path.exists(INSTALLERS_DIR):
        raise FileNotFoundError("installers directory not found")
    ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    dest_dir = os.path.join(BACKUP_ROOT, ts)
    os.makedirs(dest_dir, exist_ok=True)

    manifest = {
        'timestamp': ts,
        'files': []
    }

    for fname in os.listdir(INSTALLERS_DIR):
        src = os.path.join(INSTALLERS_DIR, fname)
        if os.path.isfile(src):
            dst = os.path.join(dest_dir, fname)
            shutil.copy2(src, dst)
            manifest['files'].append({'name': fname, 'sha256': sha256(dst), 'size': os.path.getsize(dst)})

    with open(os.path.join(dest_dir, 'manifest.json'), 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f"Backed up installers to {dest_dir}")
    return dest_dir


if __name__ == '__main__':
    backup_installers()
