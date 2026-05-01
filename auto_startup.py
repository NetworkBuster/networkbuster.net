#!/usr/bin/env python3
"""
NetworkBuster Auto-Startup Manager
Configure automatic startup of services on Windows boot
"""

import ctypes
import subprocess
import sys
import os
import winreg
from pathlib import Path

PROJECT_PATH = Path(__file__).parent.resolve()


def is_admin():
    """Check if running as administrator."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_as_admin():
    """Restart script with admin privileges."""
    if is_admin():
        return True
    
    print("↑ Requesting Administrator privileges...")
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable,
        ' '.join([f'"{arg}"' for arg in sys.argv]),
        str(PROJECT_PATH), 1
    )
    sys.exit(0)


def run_powershell(command):
    """Run PowerShell command."""
    result = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
        capture_output=True,
        text=True
    )
    return result


class AutoStartupManager:
    """Manage auto-startup configurations."""
    
    def __init__(self):
        self.task_prefix = "NetworkBuster"
        self.startup_scripts = {
            "servers": {
                "name": "NetworkBuster-Servers",
                "description": "Start NetworkBuster Web, API, and Audio servers",
                "command": f'node "{PROJECT_PATH / "start-servers.js"}"',
                "working_dir": str(PROJECT_PATH)
            },
            "health": {
                "name": "NetworkBuster-HealthMonitor",
                "description": "Start NetworkBuster health monitoring",
                "command": f'python "{PROJECT_PATH / "system_health.py"}" --monitor 60',
                "working_dir": str(PROJECT_PATH)
            },
            "power": {
                "name": "NetworkBuster-PowerManager",
                "description": "Start NetworkBuster power management",
                "command": f'node "{PROJECT_PATH / "power-manager.js"}"',
                "working_dir": str(PROJECT_PATH)
            }
        }
    
    def create_startup_task(self, task_key, run_at_logon=True, run_as_admin_task=False):
        """Create a Windows Task Scheduler task for auto-startup."""
        if task_key not in self.startup_scripts:
            print(f"✗ Unknown task: {task_key}")
            return False
        
        task = self.startup_scripts[task_key]
        
        # Build the PowerShell command to create the task
        trigger_type = "AtLogon" if run_at_logon else "AtStartup"
        run_level = "Highest" if run_as_admin_task else "Limited"
        
        ps_script = f'''
$taskName = "{task['name']}"
$description = "{task['description']}"

# Remove existing task if present
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue

# Create action
$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument '/c {task["command"]}' -WorkingDirectory "{task['working_dir']}"

# Create trigger
$trigger = New-ScheduledTaskTrigger -{trigger_type}

# Create settings
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 0)

# Create principal
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -LogonType Interactive -RunLevel {run_level}

# Register task
$task = Register-ScheduledTask -TaskName $taskName -Description $description -Action $action -Trigger $trigger -Settings $settings -Principal $principal

if ($task) {{
    Write-Output "SUCCESS: Task '$taskName' created"
}} else {{
    Write-Output "FAILED: Could not create task"
}}
'''
        
        print(f"📌 Creating startup task: {task['name']}")
        result = run_powershell(ps_script)
        
        if "SUCCESS" in result.stdout:
            print(f"✓ Task created: {task['name']}")
            print(f"  Trigger: {trigger_type}")
            print(f"  Run Level: {run_level}")
            return True
        else:
            print(f"✗ Failed: {result.stderr or result.stdout}")
            return False
    
    def remove_startup_task(self, task_key):
        """Remove a startup task."""
        if task_key not in self.startup_scripts:
            print(f"✗ Unknown task: {task_key}")
            return False
        
        task_name = self.startup_scripts[task_key]["name"]
        
        result = run_powershell(f'Unregister-ScheduledTask -TaskName "{task_name}" -Confirm:$false')
        
        if result.returncode == 0:
            print(f"✓ Task removed: {task_name}")
            return True
        else:
            print(f"⚠ Task not found or already removed: {task_name}")
            return False
    
    def list_tasks(self):
        """List all NetworkBuster scheduled tasks."""
        print("\n📋 NetworkBuster Scheduled Tasks:")
        print("-" * 60)
        
        result = run_powershell('''
Get-ScheduledTask | Where-Object {$_.TaskName -like "NetworkBuster*"} | ForEach-Object {
    $info = Get-ScheduledTaskInfo -TaskName $_.TaskName -ErrorAction SilentlyContinue
    [PSCustomObject]@{
        Name = $_.TaskName
        State = $_.State
        LastRun = if ($info.LastRunTime) { $info.LastRunTime.ToString("yyyy-MM-dd HH:mm") } else { "Never" }
        NextRun = if ($info.NextRunTime) { $info.NextRunTime.ToString("yyyy-MM-dd HH:mm") } else { "N/A" }
    }
} | Format-Table -AutoSize
''')
        
        if result.stdout.strip():
            print(result.stdout)
        else:
            print("  No NetworkBuster tasks found")
            print("\n  Available tasks to create:")
            for key, task in self.startup_scripts.items():
                print(f"    - {key}: {task['description']}")
    
    def run_task_now(self, task_key):
        """Manually run a scheduled task."""
        if task_key not in self.startup_scripts:
            print(f"✗ Unknown task: {task_key}")
            return False
        
        task_name = self.startup_scripts[task_key]["name"]
        
        result = run_powershell(f'Start-ScheduledTask -TaskName "{task_name}"')
        
        if result.returncode == 0:
            print(f"✓ Task started: {task_name}")
            return True
        else:
            print(f"✗ Failed to start task: {result.stderr}")
            return False
    
    def add_to_registry_startup(self, name, command):
        """Add program to Windows Registry startup (current user)."""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, command)
            winreg.CloseKey(key)
            print(f"✓ Added to Registry startup: {name}")
            return True
        except Exception as e:
            print(f"✗ Failed to add to Registry: {e}")
            return False
    
    def remove_from_registry_startup(self, name):
        """Remove program from Windows Registry startup."""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE
            )
            winreg.DeleteValue(key, name)
            winreg.CloseKey(key)
            print(f"✓ Removed from Registry startup: {name}")
            return True
        except FileNotFoundError:
            print(f"⚠ Entry not found: {name}")
            return False
        except Exception as e:
            print(f"✗ Failed to remove from Registry: {e}")
            return False
    
    def create_startup_batch(self):
        """Create a batch file for startup folder."""
        batch_content = f'''@echo off
title NetworkBuster Auto-Start
cd /d "{PROJECT_PATH}"

echo Starting NetworkBuster Services...
echo.

:: Start servers in background
start "NetworkBuster Servers" /min cmd /c "node start-servers.js"

:: Wait a moment
timeout /t 5 /nobreak > nul

echo NetworkBuster services started!
echo.
echo Close this window or it will close in 10 seconds...
timeout /t 10
'''
        
        batch_file = PROJECT_PATH / "networkbuster-autostart.bat"
        with open(batch_file, "w") as f:
            f.write(batch_content)
        
        print(f"✓ Created startup batch: {batch_file}")
        print("\n  To add to startup folder, run:")
        print(f'  copy "{batch_file}" "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\"')
        
        return batch_file
    
    def setup_all(self, elevated=False):
        """Set up all auto-startup configurations."""
        print("\n🚀 Setting up NetworkBuster Auto-Startup")
        print("=" * 60)
        
        if elevated and not is_admin():
            run_as_admin()
        
        # Create scheduled tasks
        print("\n[1/3] Creating scheduled tasks...")
        self.create_startup_task("servers", run_at_logon=True, run_as_admin_task=elevated)
        
        # Create startup batch
        print("\n[2/3] Creating startup batch file...")
        self.create_startup_batch()
        
        # List created tasks
        print("\n[3/3] Verifying setup...")
        self.list_tasks()
        
        print("\n✓ Auto-startup setup complete!")


def main():
    """Main menu."""
    manager = AutoStartupManager()
    
    print("=" * 60)
    print("  NetworkBuster Auto-Startup Manager")
    print("=" * 60)
    
    admin_status = "✓ Administrator" if is_admin() else "⚠ Standard User"
    print(f"  Status: {admin_status}")
    
    while True:
        print("\n📋 Menu:")
        print("  1. List scheduled tasks")
        print("  2. Create server startup task")
        print("  3. Create health monitor task")
        print("  4. Remove a task")
        print("  5. Run task now")
        print("  6. Create startup batch file")
        print("  7. Setup all (recommended)")
        print("  8. Exit")
        print()
        
        choice = input("Select option (1-8): ").strip()
        
        if choice == "1":
            manager.list_tasks()
        elif choice == "2":
            elevated = input("Run as admin? (y/n): ").lower() == 'y'
            manager.create_startup_task("servers", run_as_admin_task=elevated)
        elif choice == "3":
            manager.create_startup_task("health")
        elif choice == "4":
            print("Available: servers, health, power")
            task = input("Task to remove: ").strip()
            manager.remove_startup_task(task)
        elif choice == "5":
            print("Available: servers, health, power")
            task = input("Task to run: ").strip()
            manager.run_task_now(task)
        elif choice == "6":
            manager.create_startup_batch()
        elif choice == "7":
            elevated = input("Setup with admin privileges? (y/n): ").lower() == 'y'
            manager.setup_all(elevated)
        elif choice == "8":
            print("👋 Goodbye!")
            break
        else:
            print("Invalid option")


if __name__ == "__main__":
    main()
