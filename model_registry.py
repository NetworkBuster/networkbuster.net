"""
Model Registry
Utilities to save, load, and restore models for different classifier types.
Provides a central place to standardize checkpoint naming and restore workflows.
"""

import os
import joblib
from typing import Optional
from datetime import datetime


def get_checkpoint_dir():
    d = os.environ.get('MODEL_CHECKPOINT_DIR', 'checkpoints')
    os.makedirs(d, exist_ok=True)
    return d


def checkpoint_path(name: str) -> str:
    d = get_checkpoint_dir()
    return os.path.join(d, f"{name}.joblib")


def save_model(name: str, model, path: Optional[str] = None) -> str:
    if path is None:
        path = checkpoint_path(name)
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    joblib.dump(model, path)
    return path


def load_model(name: str, path: Optional[str] = None):
    if path is None:
        path = checkpoint_path(name)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Checkpoint not found: {path}")
    return joblib.load(path)


def restore_all_models(names):
    restored = {}
    for name in names:
        try:
            restored[name] = load_model(name)
        except FileNotFoundError:
            restored[name] = None
    return restored


def backup_checkpoint(name: str, backup_root: Optional[str] = None) -> str:
    import shutil
    src = checkpoint_path(name)
    if not os.path.exists(src):
        raise FileNotFoundError(src)
    if backup_root is None:
        backup_root = os.environ.get('INSTALLER_BACKUP_DIR', 'backups')
    ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    dest_dir = os.path.join(backup_root, ts)
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, os.path.basename(src))
    shutil.copy2(src, dest)
    return dest
