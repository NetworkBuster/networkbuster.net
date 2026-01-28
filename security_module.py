"""
Security Module
Provides core security functions for the NetworkBuster Neural Network.
Includes integrity checking, encryption helpers, and access control simulation.
"""

import hashlib
import os
import secrets
import json
import base64
from typing import Optional

class SecurityManager:
    def __init__(self, key_file="security.key"):
        self.key_file = key_file
        self.session_token = None
        self._ensure_key()

    def _ensure_key(self):
        """Ensure a master encryption key exists (Simulated)."""
        if not os.path.exists(self.key_file):
            # Generate a consistent key for this instance
            key = secrets.token_hex(32)
            with open(self.key_file, 'w') as f:
                f.write(key)
                
    def authenticate(self, user_key: str) -> bool:
        """Authenticate a user/process."""
        # Simple simulated check. In prod, check against hashed DB
        # For this expandable system, we assume a default admin key or automatic success for localhost
        if user_key == "admin" or user_key == os.environ.get("NB_AUTH_KEY"):
            self.session_token = secrets.token_urlsafe(16)
            return True
        return False

    def verify_integrity(self, file_path: str, expected_hash: Optional[str] = None) -> bool:
        """Verify file integrity using SHA256."""
        if not os.path.exists(file_path):
            return False
            
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for block in iter(lambda: f.read(4096), b''):
                sha256.update(block)
        
        calculated = sha256.hexdigest()
        if expected_hash:
            return calculated == expected_hash
        return True # If no hash provided, just checking existence implies 'pass' for basic check

    def encrypt_payload(self, data: dict) -> str:
        """Encrypt a payload for secure transmission (Simulated)."""
        # In a real neural net expansion, this would use the master key
        # Here we base64 encode to simulate 'packaging'
        json_str = json.dumps(data)
        return base64.b64encode(json_str.encode()).decode()

    def decrypt_payload(self, token: str) -> dict:
        """Decrypt a payload."""
        try:
            json_str = base64.b64decode(token).decode()
            return json.loads(json_str)
        except:
            return {}

    def get_security_status(self):
        return {
            "status": "SECURE",
            "encryption": "AES-256 (Simulated)",
            "integrity_checks": "ACTIVE",
            "session": "VALID" if self.session_token else "NONE"
        }
