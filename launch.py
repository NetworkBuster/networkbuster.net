#!/usr/bin/env python3
"""
NetworkBuster Master Launcher
Cross-platform launcher with user role management (Windows/Unix)
Supports: admin, user, visitor modes with bypass options
"""

import subprocess
import sys
import os
import time
import platform
import getpass
from pathlib import Path

# Import security verification
try:
    from security_verification import UserVerification, SecurityLevel
    SECURITY_ENABLED = True
except ImportError:
    SECURITY_ENABLED = False

PROJECT_PATH = Path(__file__).parent.resolve()
IS_WINDOWS = platform.system() == "Windows"
IS_UNIX = platform.system() in ("Linux", "Darwin")

# User role definitions
USER_ROLES = {
    "admin": {
        "level": 3,
        "permissions": ["all", "firewall", "services", "startup", "kill_process"],
        "description": "Full system access"
    },
    "user": {
        "level": 2,
        "permissions": ["start", "stop", "status", "health", "dashboard"],
        "description": "Standard operations"
    },
    "visitor": {
        "level": 1,
        "permissions": ["status", "health", "dashboard"],
        "description": "Read-only access"
    }
}

# Current session
CURRENT_ROLE = "user"
BYPASS_MODE = False


def detect_platform():
    """Detect and display platform info."""
    info = {
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "python": platform.python_version(),
        "user": getpass.getuser()
    }
    return info


def is_admin():
    """Check if running as administrator/root (cross-platform)."""
    if IS_WINDOWS:
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    else:
        # Unix/Linux - check for root
        return os.geteuid() == 0


def is_sudo_available():
    """Check if sudo is available on Unix systems."""
    if IS_WINDOWS:
        return False
    try:
        result = subprocess.run(["which", "sudo"], capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False


def run_as_admin(args=None):
    """Restart script with admin/root privileges (cross-platform)."""
    print("↑ Requesting elevated privileges...")
    
    if IS_WINDOWS:
        try:
            import ctypes
            script_args = f'"{__file__}"'
            if args:
                script_args += f' {args}'
            result = ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable,
                script_args, str(PROJECT_PATH), 1
            )
            if result > 32:
                sys.exit(0)
            else:
                print("✗ Failed to elevate. Running without admin...")
                return False
        except Exception as e:
            print(f"✗ Elevation error: {e}")
            return False
    else:
        # Unix/Linux - use sudo
        if is_sudo_available():
            cmd = ["sudo", sys.executable, __file__]
            if args:
                cmd.extend(args.split())
            os.execvp("sudo", cmd)
        else:
            print("✗ sudo not available. Run as root manually.")
            return False


def run_with_sudo(command):
    """Run a command with sudo on Unix (cross-platform wrapper)."""
    if IS_WINDOWS:
        return subprocess.run(command, capture_output=True, text=True, shell=True)
    else:
        if isinstance(command, list):
            cmd = ["sudo"] + command
        else:
            cmd = f"sudo {command}"
        return subprocess.run(cmd, capture_output=True, text=True, shell=isinstance(cmd, str))


def set_user_role(role):
    """Set the current user role."""
    global CURRENT_ROLE
    if role in USER_ROLES:
        CURRENT_ROLE = role
        print(f"✓ Role set to: {role} ({USER_ROLES[role]['description']})")
        return True
    else:
        print(f"✗ Invalid role: {role}")
        return False


def has_permission(permission):
    """Check if current role has a permission."""
    global BYPASS_MODE, CURRENT_ROLE
    if BYPASS_MODE:
        return True
    role_perms = USER_ROLES.get(CURRENT_ROLE, {}).get("permissions", [])
    return "all" in role_perms or permission in role_perms


def toggle_bypass():
    """Toggle bypass mode (requires admin confirmation)."""
    global BYPASS_MODE
    if is_admin():
        BYPASS_MODE = not BYPASS_MODE
        status = "ENABLED" if BYPASS_MODE else "DISABLED"
        print(f"⚡ Bypass mode: {status}")
        return True
    else:
        print("✗ Bypass requires admin privileges")
        return False


def require_permission(permission):
    """Decorator to check permissions before running a function."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if has_permission(permission):
                return func(*args, **kwargs)
            else:
                print(f"✗ Permission denied: requires '{permission}'")
                print(f"  Current role: {CURRENT_ROLE}")
                return None
        return wrapper
    return decorator


def check_node():
    """Check if Node.js is available."""
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        version = result.stdout.strip()
        print(f"✓ Node.js: {version}")
        return True
    except:
        print("✗ Node.js not found!")
        return False


def check_python_deps():
    """Check and install Python dependencies."""
    print("\n[2/5] Checking Python dependencies...")
    
    try:
        import psutil
        print("  ✓ psutil installed")
        return True
    except ImportError:
        print("  ⚠ psutil not found, attempting install...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "psutil", "-q"],
                check=True,
                capture_output=True
            )
            print("  ✓ psutil installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print("  ⚠ psutil install failed (optional dependency)")
            print("  ℹ Some monitoring features will be limited")
            return False
        except Exception as e:
            print(f"  ⚠ Could not install psutil: {e}")
            return False


def setup_firewall():
    """Setup firewall rules (requires admin) - cross-platform."""
    if not has_permission("firewall"):
        print("  ⚠ Permission denied for firewall")
        return
    
    if not is_admin() and not BYPASS_MODE:
        print("  ⚠ Skipping firewall (no admin)")
        return
    
    print("\n[3/5] Configuring firewall...")
    
    ports = [
        (3000, "NetworkBuster-Web"),
        (3001, "NetworkBuster-API"),
        (3002, "NetworkBuster-Audio"),
    ]
    
    for port, name in ports:
        if IS_WINDOWS:
            subprocess.run([
                "powershell", "-Command",
                f'New-NetFirewallRule -DisplayName "{name}" -Direction Inbound -Protocol TCP -LocalPort {port} -Action Allow -ErrorAction SilentlyContinue'
            ], capture_output=True)
        elif IS_UNIX:
            # Try ufw first (Ubuntu/Debian), then firewalld (CentOS/RHEL), then iptables
            result = subprocess.run(["which", "ufw"], capture_output=True)
            if result.returncode == 0:
                run_with_sudo(["ufw", "allow", str(port)])
            else:
                result = subprocess.run(["which", "firewall-cmd"], capture_output=True)
                if result.returncode == 0:
                    run_with_sudo(["firewall-cmd", "--add-port", f"{port}/tcp", "--permanent"])
                else:
                    run_with_sudo(["iptables", "-A", "INPUT", "-p", "tcp", "--dport", str(port), "-j", "ACCEPT"])
        print(f"  ✓ Port {port} opened")


def kill_existing_servers():
    """Kill any existing Node.js processes on our ports - cross-platform."""
    if not has_permission("kill_process") and not has_permission("stop"):
        print("  ⚠ Permission denied")
        return
    
    print("\n[4/5] Cleaning up existing processes...")
    
    if IS_WINDOWS:
        for port in [3000, 3001, 3002]:
            subprocess.run([
                "powershell", "-Command",
                f"$p = Get-NetTCPConnection -LocalPort {port} -ErrorAction SilentlyContinue; if ($p) {{ Stop-Process -Id $p.OwningProcess -Force -ErrorAction SilentlyContinue }}"
            ], capture_output=True)
    else:
        # Unix - use lsof and kill
        for port in [3000, 3001, 3002]:
            result = subprocess.run(
                f"lsof -ti:{port} | xargs kill -9 2>/dev/null || true",
                shell=True, capture_output=True
            )
    
    print("  ✓ Cleaned up old processes")
    time.sleep(1)


def start_servers():
    """Start all NetworkBuster servers - cross-platform."""
    if not has_permission("start"):
        print("  ⚠ Permission denied: requires 'start' permission")
        return
    
    print("\n[5/5] Starting servers...")
    
    os.chdir(PROJECT_PATH)
    
    if IS_WINDOWS:
        # Start servers in a new console window
        subprocess.Popen(
            ["cmd", "/c", "start", "NetworkBuster Servers", "node", "start-servers.js"],
            cwd=PROJECT_PATH
        )
    else:
        # Unix - use nohup or screen if available
        result = subprocess.run(["which", "screen"], capture_output=True)
        if result.returncode == 0:
            subprocess.Popen(
                ["screen", "-dmS", "networkbuster", "node", "start-servers.js"],
                cwd=PROJECT_PATH
            )
            print("  ℹ Use 'screen -r networkbuster' to attach")
        else:
            subprocess.Popen(
                ["nohup", "node", "start-servers.js", "&"],
                cwd=PROJECT_PATH,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
    
    print("  ✓ Servers launching")


def start_health_monitor():
    """Start health monitoring in background."""
    health_script = PROJECT_PATH / "system_health.py"
    if health_script.exists():
        subprocess.Popen(
            [sys.executable, str(health_script), "--monitor", "60"],
            creationflags=subprocess.CREATE_NEW_CONSOLE,
            cwd=PROJECT_PATH
        )
        print("  ✓ Health monitor started")


def show_status():
    """Show final status."""
    print("\n" + "=" * 60)
    print("  NetworkBuster Started Successfully!")
    print("=" * 60)
    print()
    print("  🌐 Web Server:   http://localhost:3000")
    print("  🔌 API Server:   http://localhost:3001")
    print("  🔊 Audio Server: http://localhost:3002")
    print()
    print("  📋 Quick Commands:")
    print("     python quick_admin.py   - Admin menu")
    print("     python system_health.py - Health check")
    print()
    print("=" * 60)


def show_menu():
    """Display main menu with role info."""
    global CURRENT_ROLE, BYPASS_MODE
    
    print("\n" + "─" * 60)
    print("  📋 MAIN MENU")
    print("─" * 60)
    
    # Show role and bypass status
    role_info = USER_ROLES.get(CURRENT_ROLE, {})
    bypass_str = " [BYPASS]" if BYPASS_MODE else ""
    print(f"  👤 Role: {CURRENT_ROLE.upper()}{bypass_str} - {role_info.get('description', '')}")
    print("─" * 60)
    
    # Server operations
    print("  [1] 🚀 Launch All Servers")
    print("  [2] 🛑 Stop All Servers")
    print("  [3] 🔌 Check Port Status")
    print("  [4] 🌐 Open Dashboard")
    print()
    
    # Tools
    print("  [5] 🔧 Quick Admin Tools")
    print("  [6] 📊 System Health Check")
    print("  [7] ⚙️  Service Manager")
    print("  [8] 🔄 Auto-Startup Setup")
    print()
    
    # Cloud & Admin
    print("  [9] 🔥 Configure Firewall (admin)")
    print("  [c] ☁️  Cloud Device Manager (Azure/Vercel)")
    print("  [m] 📱 Mobile Deployment (iOS/Android/PWA)")
    print("  [d] 🛸 Drone Flight System (Scan/Auto)")
    print("  [v] 🌐 Vercel Domain Setup")
    print()
    
    # Role management
    print("  [r] 👤 Change Role (admin/user/visitor)")
    print("  [b] ⚡ Toggle Bypass Mode (admin only)")
    print("  [e] ↑  Elevate to Admin")
    print("  [i] ℹ️  System Info")
    print()
    
    # Security
    if SECURITY_ENABLED:
        print("  [s] 🔐 Security Verification")
    
    print("  [0] ❌ Exit")
    print("─" * 60)


def stop_all_servers():
    """Stop all Node.js processes - cross-platform."""
    if not has_permission("stop"):
        print("  ⚠ Permission denied: requires 'stop' permission")
        return
    
    print("\n🛑 Stopping all servers...")
    
    if IS_WINDOWS:
        subprocess.run([
            "powershell", "-Command",
            "Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force"
        ], capture_output=True)
    else:
        # Unix - kill all node processes
        subprocess.run("pkill -f 'node.*start-servers' || killall node 2>/dev/null || true", shell=True)
    
    print("✓ All Node.js processes stopped")


def check_port_status():
    """Check status of server ports - cross-platform."""
    if not has_permission("status"):
        print("  ⚠ Permission denied")
        return
    
    print("\n🔌 Port Status:")
    print("-" * 40)
    
    for port, name in [(3000, "Web"), (3001, "API"), (3002, "Audio")]:
        if IS_WINDOWS:
            result = subprocess.run([
                "powershell", "-Command",
                f"Get-NetTCPConnection -LocalPort {port} -State Listen -ErrorAction SilentlyContinue"
            ], capture_output=True, text=True)
            is_running = bool(result.stdout.strip())
        else:
            # Unix - use netstat or ss
            result = subprocess.run(
                f"ss -tlnp 2>/dev/null | grep :{port} || netstat -tlnp 2>/dev/null | grep :{port}",
                shell=True, capture_output=True, text=True
            )
            is_running = bool(result.stdout.strip())
        
        status = "🟢 RUNNING" if is_running else "⚪ STOPPED"
        print(f"  Port {port} ({name}): {status}")


def open_dashboard():
    """Open dashboard in browser."""
    import webbrowser
    print("\n🌐 Opening http://localhost:3000...")
    webbrowser.open("http://localhost:3000")


def run_external_script(script_name):
    """Run another Python script."""
    script_path = PROJECT_PATH / script_name
    if script_path.exists():
        subprocess.run([sys.executable, str(script_path)], cwd=PROJECT_PATH)
    else:
        print(f"✗ Script not found: {script_name}")


def launch_all():
    """Full launch sequence."""
    print("\n" + "-" * 60)
    
    # Step 1: Check Node.js
    print("\n[1/5] Checking Node.js...")
    if not check_node():
        print("\n✗ Please install Node.js first!")
        return False
    
    # Step 2: Python deps
    check_python_deps()
    
    # Step 3: Firewall
    setup_firewall()
    
    # Step 4: Kill existing
    kill_existing_servers()
    
    # Step 5: Start servers
    start_servers()
    
    # Wait for servers to start
    print("\n⏳ Waiting for servers to initialize...")
    time.sleep(3)
    
    # Show status
    show_status()
    return True


def show_system_info():
    """Display system information."""
    info = detect_platform()
    
    print("\n" + "─" * 60)
    print("  ℹ️  SYSTEM INFORMATION")
    print("─" * 60)
    print(f"  Platform:    {info['system']} {info['release']}")
    print(f"  Machine:     {info['machine']}")
    print(f"  Python:      {info['python']}")
    print(f"  User:        {info['user']}")
    print(f"  Admin:       {'Yes' if is_admin() else 'No'}")
    print(f"  Project:     {PROJECT_PATH}")
    print(f"  Role:        {CURRENT_ROLE}")
    print(f"  Bypass:      {'Enabled' if BYPASS_MODE else 'Disabled'}")
    
    if IS_UNIX:
        print(f"  Sudo:        {'Available' if is_sudo_available() else 'Not available'}")
    
    print("─" * 60)


def change_role():
    """Change user role interactively."""
    print("\n👤 Available Roles:")
    for role, info in USER_ROLES.items():
        print(f"  - {role}: {info['description']}")
        print(f"    Permissions: {', '.join(info['permissions'])}")
    
    new_role = input("\n  Enter role (admin/user/visitor): ").strip().lower()
    
    if new_role == "admin" and not is_admin():
        print("⚠ Admin role requires elevated privileges")
        resp = input("  Elevate now? (y/n): ").strip().lower()
        if resp == 'y':
            run_as_admin()
            return
    
    set_user_role(new_role)


def main():
    """Main launcher with menu."""
    global CURRENT_ROLE
    
    # Auto-detect role based on privileges
    if is_admin():
        CURRENT_ROLE = "admin"
    
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + "  NetworkBuster Master Launcher".center(58) + "║")
    print("║" + f"  {platform.system()} | Python {platform.python_version()}".center(58) + "║")
    print("╚" + "═" * 58 + "╝")
    
    # Admin check
    admin_status = "✓ Administrator" if is_admin() else "⚠ Standard User"
    print(f"\n  Status: {admin_status}")
    print(f"  Project: {PROJECT_PATH}")
    
    while True:
        show_menu()
        choice = input("\n  Select option: ").strip().lower()
        
        if choice == "1":
            launch_all()
        elif choice == "2":
            stop_all_servers()
        elif choice == "3":
            check_port_status()
        elif choice == "4":
            open_dashboard()
        elif choice == "5":
            run_external_script("quick_admin.py")
        elif choice == "6":
            run_external_script("system_health.py")
        elif choice == "7":
            run_external_script("service_manager.py")
        elif choice == "8":
            run_external_script("auto_startup.py")
        elif choice == "9":
            if has_permission("firewall"):
                setup_firewall()
            else:
                print("\n⚠ Firewall requires 'firewall' permission")
                resp = input("  Elevate to admin? (y/n): ").strip().lower()
                if resp == 'y':
                    run_as_admin()
        elif choice == "c":
            run_external_script("cloud_devices.py")
        elif choice == "m":
            run_external_script("mobile_deployment.py")
        elif choice == "d":
            run_external_script("drone_flight_system.py")
        elif choice == "v":
            run_external_script("vercel_domain_setup.py")
        elif choice == "r":
            change_role()
        elif choice == "b":
            toggle_bypass()
        elif choice == "e":
            run_as_admin()
        elif choice == "i":
            show_system_info()
        elif choice == "s":
            if SECURITY_ENABLED:
                run_external_script("security_verification.py")
            else:
                print("\n⚠ Security module not available")
        elif choice == "0":
            print("\n👋 Goodbye!")
            break
        else:
            print("\n⚠ Invalid option.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
