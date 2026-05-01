#!/usr/bin/env python3
"""
NetworkBuster Admin Runner
Run any script/command with elevated privileges on Windows
"""

import ctypes
import sys
import os
import subprocess
from pathlib import Path

PROJECT_PATH = Path(__file__).parent.resolve()


def is_admin():
    """Check if the script is running with administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_as_admin(command=None, script=None, wait=True):
    """
    Re-run the current script or a specific command as administrator.
    
    Args:
        command: Optional command to run (list of strings)
        script: Optional script path to run
        wait: Whether to wait for the process to complete
    """
    if is_admin():
        print("✓ Already running as Administrator")
        return True
    
    if command:
        # Run a specific command elevated
        cmd_str = ' '.join(command) if isinstance(command, list) else command
        params = f'/c {cmd_str}'
        executable = 'cmd.exe'
    elif script:
        # Run a specific script elevated
        params = f'"{script}"'
        executable = sys.executable
    else:
        # Re-run this script elevated
        params = ' '.join([f'"{arg}"' for arg in sys.argv])
        executable = sys.executable
    
    print(f"↑ Requesting Administrator privileges...")
    
    try:
        result = ctypes.windll.shell32.ShellExecuteW(
            None,           # Parent window
            "runas",        # Operation (run as admin)
            executable,     # Program
            params,         # Parameters
            str(PROJECT_PATH),  # Working directory
            1 if wait else 0    # Show window
        )
        
        if result > 32:
            print("✓ Elevated process started successfully")
            return True
        else:
            print(f"✗ Failed to elevate (error code: {result})")
            return False
    except Exception as e:
        print(f"✗ Error requesting elevation: {e}")
        return False


def run_elevated_command(cmd, capture_output=False):
    """
    Run a command that requires admin privileges.
    
    Args:
        cmd: Command as string or list
        capture_output: Whether to capture and return output
    """
    if not is_admin():
        print("⚠ This command requires Administrator privileges")
        return run_as_admin(command=cmd)
    
    if isinstance(cmd, str):
        cmd = cmd.split()
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=capture_output,
            text=True,
            cwd=PROJECT_PATH
        )
        return result if capture_output else result.returncode == 0
    except Exception as e:
        print(f"✗ Command failed: {e}")
        return False


def main():
    """Main entry point - demonstrates admin capabilities."""
    print("=" * 60)
    print("  NetworkBuster Admin Runner")
    print("=" * 60)
    print()
    
    if is_admin():
        print("✓ Running with Administrator privileges")
        print()
        
        # Show what we can do as admin
        print("Available admin operations:")
        print("  1. Manage Windows services")
        print("  2. Modify system firewall")
        print("  3. Access protected directories")
        print("  4. Run elevated PowerShell scripts")
        print()
        
        # Example: Check execution policy
        result = subprocess.run(
            ["powershell", "-Command", "Get-ExecutionPolicy"],
            capture_output=True,
            text=True
        )
        print(f"Current Execution Policy: {result.stdout.strip()}")
        
    else:
        print("⚠ Not running as Administrator")
        print()
        response = input("Would you like to restart with admin privileges? (y/n): ")
        if response.lower() == 'y':
            run_as_admin()
            sys.exit(0)


if __name__ == "__main__":
    main()
