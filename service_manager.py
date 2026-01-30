#!/usr/bin/env python3
"""
NetworkBuster Service Manager
Manage Windows services and scheduled tasks with admin privileges
"""

import ctypes
import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime

PROJECT_PATH = Path(__file__).parent.resolve()
SERVICE_CONFIG = PROJECT_PATH / "service-config.json"


def is_admin():
    """Check if running as administrator."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def require_admin(func):
    """Decorator to ensure admin privileges."""
    def wrapper(*args, **kwargs):
        if not is_admin():
            print("✗ This operation requires Administrator privileges")
            print("  Run this script as Administrator")
            sys.exit(1)
        return func(*args, **kwargs)
    return wrapper


def run_powershell(command, capture=True):
    """Run a PowerShell command and return output."""
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", command],
        capture_output=capture,
        text=True
    )
    return result


class ServiceManager:
    """Manage NetworkBuster services."""
    
    def __init__(self):
        self.services = {
            "NetworkBusterWeb": {
                "display": "NetworkBuster Web Server",
                "port": 3000,
                "script": "server-universal.js"
            },
            "NetworkBusterAPI": {
                "display": "NetworkBuster API Server",
                "port": 3001,
                "script": "api/server-universal.js"
            },
            "NetworkBusterAudio": {
                "display": "NetworkBuster Audio Server",
                "port": 3002,
                "script": "server-audio.js"
            }
        }
    
    def list_services(self):
        """List all NetworkBuster-related services."""
        print("\n📋 NetworkBuster Services Status:")
        print("-" * 50)
        
        for name, info in self.services.items():
            # Check if port is in use
            port_check = run_powershell(
                f"Get-NetTCPConnection -LocalPort {info['port']} -ErrorAction SilentlyContinue"
            )
            status = "🟢 Running" if port_check.stdout.strip() else "🔴 Stopped"
            print(f"  {info['display']}")
            print(f"    Port: {info['port']} - {status}")
            print(f"    Script: {info['script']}")
            print()
    
    @require_admin
    def create_scheduled_task(self, task_name, script_path, trigger="startup"):
        """Create a Windows scheduled task for auto-start."""
        script_full = PROJECT_PATH / script_path
        
        if trigger == "startup":
            trigger_cmd = "-AtStartup"
        elif trigger == "daily":
            trigger_cmd = "-Daily -At 6am"
        else:
            trigger_cmd = "-AtStartup"
        
        ps_command = f'''
$action = New-ScheduledTaskAction -Execute "node" -Argument "{script_full}" -WorkingDirectory "{PROJECT_PATH}"
$trigger = New-ScheduledTaskTrigger {trigger_cmd}
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName "{task_name}" -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force
'''
        
        print(f"📌 Creating scheduled task: {task_name}")
        result = run_powershell(ps_command)
        
        if result.returncode == 0:
            print(f"✓ Task '{task_name}' created successfully")
            return True
        else:
            print(f"✗ Failed to create task: {result.stderr}")
            return False
    
    @require_admin
    def remove_scheduled_task(self, task_name):
        """Remove a scheduled task."""
        result = run_powershell(f'Unregister-ScheduledTask -TaskName "{task_name}" -Confirm:$false')
        
        if result.returncode == 0:
            print(f"✓ Task '{task_name}' removed")
            return True
        else:
            print(f"⚠ Task not found or already removed")
            return False
    
    def list_scheduled_tasks(self):
        """List NetworkBuster scheduled tasks."""
        print("\n📅 NetworkBuster Scheduled Tasks:")
        print("-" * 50)
        
        result = run_powershell('Get-ScheduledTask | Where-Object {$_.TaskName -like "*NetworkBuster*"} | Format-Table TaskName, State -AutoSize')
        
        if result.stdout.strip():
            print(result.stdout)
        else:
            print("  No NetworkBuster tasks found")
    
    @require_admin
    def open_firewall_port(self, port, name):
        """Open a firewall port for a service."""
        ps_command = f'''
New-NetFirewallRule -DisplayName "{name}" -Direction Inbound -Protocol TCP -LocalPort {port} -Action Allow
'''
        result = run_powershell(ps_command)
        
        if result.returncode == 0:
            print(f"✓ Firewall port {port} opened for {name}")
            return True
        else:
            print(f"✗ Failed to open port: {result.stderr}")
            return False
    
    @require_admin
    def setup_all_firewall_rules(self):
        """Set up firewall rules for all services."""
        print("\n🔥 Setting up firewall rules...")
        
        for name, info in self.services.items():
            self.open_firewall_port(info['port'], info['display'])
    
    def check_ports(self):
        """Check which ports are in use."""
        print("\n🔌 Port Status:")
        print("-" * 50)
        
        ports = [3000, 3001, 3002, 3003, 8080]
        
        for port in ports:
            result = run_powershell(
                f"Get-NetTCPConnection -LocalPort {port} -ErrorAction SilentlyContinue | Select-Object -First 1 OwningProcess"
            )
            
            if result.stdout.strip() and "OwningProcess" in result.stdout:
                # Get process name
                pid_result = run_powershell(
                    f"(Get-NetTCPConnection -LocalPort {port} -ErrorAction SilentlyContinue | Select-Object -First 1).OwningProcess"
                )
                pid = pid_result.stdout.strip()
                if pid:
                    proc_result = run_powershell(f"(Get-Process -Id {pid} -ErrorAction SilentlyContinue).ProcessName")
                    proc_name = proc_result.stdout.strip() or "unknown"
                    print(f"  Port {port}: 🟢 In use by {proc_name} (PID: {pid})")
                else:
                    print(f"  Port {port}: 🟢 In use")
            else:
                print(f"  Port {port}: ⚪ Available")


def main():
    """Main menu for service management."""
    manager = ServiceManager()
    
    print("=" * 60)
    print("  NetworkBuster Service Manager")
    print("=" * 60)
    
    admin_status = "✓ Administrator" if is_admin() else "⚠ Standard User"
    print(f"  Status: {admin_status}")
    print()
    
    while True:
        print("\n📋 Menu:")
        print("  1. List services status")
        print("  2. Check port usage")
        print("  3. List scheduled tasks")
        print("  4. Create startup task (requires admin)")
        print("  5. Setup firewall rules (requires admin)")
        print("  6. Exit")
        print()
        
        choice = input("Select option (1-6): ").strip()
        
        if choice == "1":
            manager.list_services()
        elif choice == "2":
            manager.check_ports()
        elif choice == "3":
            manager.list_scheduled_tasks()
        elif choice == "4":
            if is_admin():
                manager.create_scheduled_task("NetworkBusterServers", "start-servers.js", "startup")
            else:
                print("⚠ Please run as Administrator for this option")
        elif choice == "5":
            if is_admin():
                manager.setup_all_firewall_rules()
            else:
                print("⚠ Please run as Administrator for this option")
        elif choice == "6":
            print("👋 Goodbye!")
            break
        else:
            print("Invalid option")


if __name__ == "__main__":
    main()
