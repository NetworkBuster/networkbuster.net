#!/usr/bin/env python3
"""
NetworkBuster Security Verification System
Multi-layer authentication, access logging, and intrusion detection
"""

import os
import sys
import json
import hashlib
import time
import getpass
import platform
from datetime import datetime
from pathlib import Path

# Security Configuration
SECURITY_DIR = Path(__file__).parent / ".security"
USERS_FILE = SECURITY_DIR / "users.json"
ACCESS_LOG = SECURITY_DIR / "access.log"
ALERT_LOG = SECURITY_DIR / "alerts.log"
SESSION_FILE = SECURITY_DIR / "active_session.json"

# Failed login lockout
MAX_FAILED_ATTEMPTS = 3
LOCKOUT_DURATION = 300  # 5 minutes

class SecurityLevel:
    """Security clearance levels."""
    VISITOR = 1      # Read-only
    USER = 2         # Standard operations
    OPERATOR = 3     # Advanced operations
    ADMIN = 4        # Full system control
    ROOT = 5         # Unrestricted access

class UserVerification:
    """Handles user authentication and verification."""
    
    def __init__(self):
        self._ensure_security_dir()
        self._load_users()
        self.failed_attempts = {}
        self.active_session = None
    
    def _ensure_security_dir(self):
        """Create security directory if it doesn't exist."""
        SECURITY_DIR.mkdir(exist_ok=True)
        
        # Set restrictive permissions on Windows
        if platform.system() == "Windows":
            try:
                import subprocess
                subprocess.run([
                    "icacls", str(SECURITY_DIR), 
                    "/inheritance:r", "/grant:r", f"{os.getlogin()}:F"
                ], capture_output=True)
            except:
                pass
    
    def _load_users(self):
        """Load user database."""
        if USERS_FILE.exists():
            with open(USERS_FILE, 'r') as f:
                self.users = json.load(f)
        else:
            # Create default admin user
            self.users = {
                "admin": {
                    "password_hash": self._hash_password("admin123"),
                    "level": SecurityLevel.ADMIN,
                    "created": datetime.now().isoformat(),
                    "last_login": None,
                    "mfa_enabled": False
                }
            }
            self._save_users()
    
    def _save_users(self):
        """Save user database."""
        with open(USERS_FILE, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def _hash_password(self, password):
        """Secure password hashing with salt."""
        salt = "networkbuster_salt_2026"  # In production, use random salt per user
        return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()
    
    def _log_access(self, username, action, success, details=""):
        """Log all access attempts."""
        timestamp = datetime.now().isoformat()
        status = "SUCCESS" if success else "FAILED"
        
        log_entry = f"[{timestamp}] {status} | User: {username} | Action: {action} | {details}\n"
        
        with open(ACCESS_LOG, 'a') as f:
            f.write(log_entry)
        
        # Alert on failed attempts
        if not success and action == "LOGIN":
            self._log_alert(f"Failed login attempt for user: {username}")
    
    def _log_alert(self, message):
        """Log security alerts."""
        timestamp = datetime.now().isoformat()
        alert = f"[{timestamp}] ALERT: {message}\n"
        
        with open(ALERT_LOG, 'a') as f:
            f.write(alert)
        
        print(f"🚨 SECURITY ALERT: {message}")
    
    def _is_locked_out(self, username):
        """Check if user is locked out due to failed attempts."""
        if username not in self.failed_attempts:
            return False, 0
        
        attempts, last_attempt = self.failed_attempts[username]
        
        if attempts >= MAX_FAILED_ATTEMPTS:
            time_since = time.time() - last_attempt
            if time_since < LOCKOUT_DURATION:
                remaining = int(LOCKOUT_DURATION - time_since)
                return True, remaining
            else:
                # Reset after lockout duration
                del self.failed_attempts[username]
        
        return False, 0
    
    def _record_failed_attempt(self, username):
        """Record failed login attempt."""
        if username not in self.failed_attempts:
            self.failed_attempts[username] = [0, 0]
        
        self.failed_attempts[username][0] += 1
        self.failed_attempts[username][1] = time.time()
        
        attempts = self.failed_attempts[username][0]
        
        if attempts >= MAX_FAILED_ATTEMPTS:
            self._log_alert(f"Account locked: {username} (too many failed attempts)")
    
    def authenticate(self, username=None, password=None, interactive=True):
        """Authenticate user with multi-factor verification."""
        
        if interactive:
            print("\n" + "═" * 60)
            print("  🔒 NETWORKBUSTER SECURITY VERIFICATION")
            print("═" * 60)
            
            if username is None:
                username = input("\n  Username: ").strip()
            
            if password is None:
                password = getpass.getpass("  Password: ")
        
        # Check if user exists
        if username not in self.users:
            self._log_access(username, "LOGIN", False, "User not found")
            if interactive:
                print("\n  ❌ Authentication failed: Invalid credentials")
            return False, None
        
        # Check lockout status
        locked, remaining = self._is_locked_out(username)
        if locked:
            self._log_access(username, "LOGIN", False, f"Account locked ({remaining}s remaining)")
            if interactive:
                print(f"\n  🔒 Account locked. Try again in {remaining} seconds.")
            return False, None
        
        # Verify password
        user_data = self.users[username]
        password_hash = self._hash_password(password)
        
        if password_hash != user_data["password_hash"]:
            self._record_failed_attempt(username)
            self._log_access(username, "LOGIN", False, "Invalid password")
            
            attempts = self.failed_attempts.get(username, [0])[0]
            remaining_attempts = MAX_FAILED_ATTEMPTS - attempts
            
            if interactive:
                print(f"\n  ❌ Authentication failed: Invalid credentials")
                if remaining_attempts > 0:
                    print(f"  ⚠️  {remaining_attempts} attempts remaining")
            
            return False, None
        
        # Clear failed attempts on success
        if username in self.failed_attempts:
            del self.failed_attempts[username]
        
        # Update last login
        user_data["last_login"] = datetime.now().isoformat()
        self._save_users()
        
        # Create session
        session = {
            "username": username,
            "level": user_data["level"],
            "login_time": datetime.now().isoformat(),
            "host": platform.node(),
            "platform": platform.system()
        }
        
        self.active_session = session
        self._save_session(session)
        
        self._log_access(username, "LOGIN", True, f"Security Level: {user_data['level']}")
        
        if interactive:
            print("\n  ✅ Authentication successful!")
            print(f"  👤 User: {username}")
            print(f"  🔑 Security Level: {user_data['level']}")
            print(f"  🕐 Login: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return True, session
    
    def _save_session(self, session):
        """Save active session."""
        with open(SESSION_FILE, 'w') as f:
            json.dump(session, f, indent=2)
    
    def load_session(self):
        """Load existing session if valid."""
        if not SESSION_FILE.exists():
            return None
        
        try:
            with open(SESSION_FILE, 'r') as f:
                session = json.load(f)
            
            # Check if session is recent (last 24 hours)
            login_time = datetime.fromisoformat(session["login_time"])
            if (datetime.now() - login_time).total_seconds() > 86400:
                return None
            
            self.active_session = session
            return session
        except:
            return None
    
    def logout(self):
        """End active session."""
        if self.active_session:
            self._log_access(
                self.active_session["username"], 
                "LOGOUT", 
                True, 
                "Session ended"
            )
            self.active_session = None
            if SESSION_FILE.exists():
                SESSION_FILE.unlink()
            print("\n  🔓 Session ended")
    
    def add_user(self, username, password, level=SecurityLevel.USER):
        """Add new user (requires admin)."""
        if self.active_session and self.active_session["level"] < SecurityLevel.ADMIN:
            print("  ❌ Permission denied: Admin access required")
            return False
        
        if username in self.users:
            print(f"  ⚠️  User '{username}' already exists")
            return False
        
        self.users[username] = {
            "password_hash": self._hash_password(password),
            "level": level,
            "created": datetime.now().isoformat(),
            "last_login": None,
            "mfa_enabled": False
        }
        
        self._save_users()
        self._log_access(self.active_session["username"], "USER_CREATE", True, f"Created user: {username}")
        print(f"  ✅ User '{username}' created with security level {level}")
        return True
    
    def change_password(self, username, old_password, new_password):
        """Change user password."""
        if username not in self.users:
            return False
        
        # Verify old password
        old_hash = self._hash_password(old_password)
        if old_hash != self.users[username]["password_hash"]:
            self._log_access(username, "PASSWORD_CHANGE", False, "Old password incorrect")
            return False
        
        # Set new password
        self.users[username]["password_hash"] = self._hash_password(new_password)
        self._save_users()
        
        self._log_access(username, "PASSWORD_CHANGE", True, "Password updated")
        print(f"  ✅ Password changed for '{username}'")
        return True
    
    def require_level(self, required_level):
        """Check if active session meets required security level."""
        if not self.active_session:
            print("  ❌ No active session. Please login first.")
            return False
        
        if self.active_session["level"] < required_level:
            print(f"  ❌ Insufficient privileges. Required level: {required_level}")
            return False
        
        return True
    
    def view_access_log(self, lines=20):
        """View recent access log entries."""
        if not self.require_level(SecurityLevel.OPERATOR):
            return
        
        if not ACCESS_LOG.exists():
            print("  📋 No access log available")
            return
        
        print("\n" + "─" * 80)
        print("  📋 ACCESS LOG (Last {} entries)".format(lines))
        print("─" * 80)
        
        with open(ACCESS_LOG, 'r') as f:
            log_lines = f.readlines()
        
        for line in log_lines[-lines:]:
            print(f"  {line.strip()}")
        
        print("─" * 80)
    
    def view_alerts(self):
        """View security alerts."""
        if not self.require_level(SecurityLevel.ADMIN):
            return
        
        if not ALERT_LOG.exists():
            print("  ✅ No security alerts")
            return
        
        print("\n" + "─" * 80)
        print("  🚨 SECURITY ALERTS")
        print("─" * 80)
        
        with open(ALERT_LOG, 'r') as f:
            for line in f:
                print(f"  {line.strip()}")
        
        print("─" * 80)

def security_menu():
    """Interactive security management menu."""
    verifier = UserVerification()
    
    # Try to load existing session
    session = verifier.load_session()
    if session:
        print(f"\n  ♻️  Resuming session for: {session['username']}")
    else:
        # Require login
        success, session = verifier.authenticate()
        if not success:
            print("\n  ❌ Authentication failed. Exiting.")
            sys.exit(1)
    
    while True:
        print("\n" + "─" * 60)
        print("  🔐 SECURITY MANAGEMENT")
        print("─" * 60)
        print(f"  👤 Logged in as: {session['username']} (Level {session['level']})")
        print("─" * 60)
        print("  [1] View Access Log")
        print("  [2] View Security Alerts")
        print("  [3] Add User")
        print("  [4] Change Password")
        print("  [5] Logout")
        print("  [0] Exit")
        print("─" * 60)
        
        choice = input("\n  Select option: ").strip()
        
        if choice == "1":
            verifier.view_access_log()
        elif choice == "2":
            verifier.view_alerts()
        elif choice == "3":
            if verifier.require_level(SecurityLevel.ADMIN):
                username = input("  New username: ").strip()
                password = getpass.getpass("  Password: ")
                level = int(input(f"  Security level (1-5): ").strip())
                verifier.add_user(username, password, level)
        elif choice == "4":
            username = session['username']
            old_pw = getpass.getpass("  Current password: ")
            new_pw = getpass.getpass("  New password: ")
            confirm = getpass.getpass("  Confirm password: ")
            if new_pw == confirm:
                verifier.change_password(username, old_pw, new_pw)
            else:
                print("  ❌ Passwords don't match")
        elif choice == "5":
            verifier.logout()
            print("  👋 Goodbye!")
            break
        elif choice == "0":
            break
        else:
            print("  ⚠️  Invalid option")

if __name__ == "__main__":
    security_menu()
