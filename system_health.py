#!/usr/bin/env python3
"""
NetworkBuster System Health Monitor
Monitor system resources and server health with admin capabilities
"""

import ctypes
import subprocess
import sys
import os
import time
import json
from pathlib import Path
from datetime import datetime

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

PROJECT_PATH = Path(__file__).parent.resolve()
HEALTH_LOG = PROJECT_PATH / "logs" / "health.log"


def is_admin():
    """Check if running as administrator."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def ensure_log_dir():
    """Ensure log directory exists."""
    log_dir = PROJECT_PATH / "logs"
    log_dir.mkdir(exist_ok=True)
    return log_dir


def log_health(message, level="INFO"):
    """Log health check message."""
    ensure_log_dir()
    timestamp = datetime.now().isoformat()
    log_entry = f"[{timestamp}] [{level}] {message}\n"
    
    with open(HEALTH_LOG, "a") as f:
        f.write(log_entry)
    
    # Color codes for terminal
    colors = {
        "INFO": "\033[94m",
        "SUCCESS": "\033[92m",
        "WARNING": "\033[93m",
        "ERROR": "\033[91m",
        "RESET": "\033[0m"
    }
    
    color = colors.get(level, colors["INFO"])
    print(f"{color}[{level}]{colors['RESET']} {message}")


def run_powershell(command):
    """Run PowerShell command and return output."""
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", command],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()


class SystemHealth:
    """Monitor system health and resources."""
    
    def __init__(self):
        self.servers = [
            {"name": "Web Server", "port": 3000},
            {"name": "API Server", "port": 3001},
            {"name": "Audio Server", "port": 3002},
        ]
    
    def check_cpu(self):
        """Check CPU usage."""
        if PSUTIL_AVAILABLE:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            status = "OK" if cpu_percent < 80 else "HIGH"
            log_health(f"CPU: {cpu_percent}% ({cpu_count} cores) - {status}", 
                      "SUCCESS" if status == "OK" else "WARNING")
            return {"usage": cpu_percent, "cores": cpu_count, "status": status}
        else:
            # Fallback to PowerShell
            cpu = run_powershell("(Get-CimInstance Win32_Processor).LoadPercentage")
            log_health(f"CPU: {cpu}%", "INFO")
            return {"usage": float(cpu) if cpu else 0, "status": "UNKNOWN"}
    
    def check_memory(self):
        """Check memory usage."""
        if PSUTIL_AVAILABLE:
            mem = psutil.virtual_memory()
            used_gb = mem.used / (1024**3)
            total_gb = mem.total / (1024**3)
            percent = mem.percent
            
            status = "OK" if percent < 85 else "HIGH"
            log_health(f"Memory: {used_gb:.1f}GB / {total_gb:.1f}GB ({percent}%) - {status}",
                      "SUCCESS" if status == "OK" else "WARNING")
            return {"used_gb": used_gb, "total_gb": total_gb, "percent": percent, "status": status}
        else:
            # Fallback to PowerShell
            mem_info = run_powershell("""
$mem = Get-CimInstance Win32_OperatingSystem
$total = [math]::Round($mem.TotalVisibleMemorySize/1MB, 1)
$free = [math]::Round($mem.FreePhysicalMemory/1MB, 1)
"$($total - $free)/$total"
""")
            log_health(f"Memory: {mem_info} GB", "INFO")
            return {"info": mem_info, "status": "UNKNOWN"}
    
    def check_disk(self):
        """Check disk usage."""
        if PSUTIL_AVAILABLE:
            results = {}
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    used_gb = usage.used / (1024**3)
                    total_gb = usage.total / (1024**3)
                    percent = usage.percent
                    
                    status = "OK" if percent < 90 else "LOW"
                    drive = partition.device
                    log_health(f"Disk {drive}: {used_gb:.1f}GB / {total_gb:.1f}GB ({percent}%) - {status}",
                              "SUCCESS" if status == "OK" else "WARNING")
                    results[drive] = {"used_gb": used_gb, "total_gb": total_gb, "percent": percent}
                except:
                    pass
            return results
        else:
            # Fallback to PowerShell
            disk_info = run_powershell("Get-PSDrive -PSProvider FileSystem | Select-Object Name, Used, Free | Format-Table")
            log_health(f"Disk Info:\n{disk_info}", "INFO")
            return {"info": disk_info}
    
    def check_ports(self):
        """Check if server ports are active."""
        log_health("Checking server ports...", "INFO")
        results = {}
        
        for server in self.servers:
            port = server["port"]
            name = server["name"]
            
            # Check if port is listening
            check = run_powershell(f"Get-NetTCPConnection -LocalPort {port} -State Listen -ErrorAction SilentlyContinue")
            
            if check:
                log_health(f"  {name} (:{port}): RUNNING", "SUCCESS")
                results[name] = {"port": port, "status": "running"}
            else:
                log_health(f"  {name} (:{port}): STOPPED", "WARNING")
                results[name] = {"port": port, "status": "stopped"}
        
        return results
    
    def check_node_processes(self):
        """Check Node.js processes."""
        if PSUTIL_AVAILABLE:
            node_procs = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
                if 'node' in proc.info['name'].lower():
                    mem_mb = proc.info['memory_info'].rss / (1024**2) if proc.info['memory_info'] else 0
                    node_procs.append({
                        'pid': proc.info['pid'],
                        'memory_mb': mem_mb,
                        'cpu': proc.info['cpu_percent']
                    })
            
            if node_procs:
                log_health(f"Found {len(node_procs)} Node.js process(es)", "SUCCESS")
                for p in node_procs:
                    log_health(f"  PID {p['pid']}: {p['memory_mb']:.1f}MB RAM", "INFO")
            else:
                log_health("No Node.js processes found", "WARNING")
            
            return node_procs
        else:
            node_info = run_powershell("Get-Process node -ErrorAction SilentlyContinue | Select-Object Id, WorkingSet64 | Format-Table")
            log_health(f"Node processes: {node_info or 'None'}", "INFO")
            return {"info": node_info}
    
    def check_network(self):
        """Check network connectivity."""
        log_health("Checking network connectivity...", "INFO")
        
        # Check localhost
        localhost_check = run_powershell("Test-NetConnection -ComputerName localhost -Port 3000 -WarningAction SilentlyContinue | Select-Object TcpTestSucceeded")
        
        # Check internet
        internet_check = run_powershell("Test-NetConnection -ComputerName 8.8.8.8 -WarningAction SilentlyContinue | Select-Object PingSucceeded")
        
        results = {
            "localhost": "TcpTestSucceeded : True" in localhost_check,
            "internet": "PingSucceeded : True" in internet_check
        }
        
        log_health(f"  Localhost (3000): {'OK' if results['localhost'] else 'FAIL'}", 
                  "SUCCESS" if results['localhost'] else "ERROR")
        log_health(f"  Internet: {'OK' if results['internet'] else 'FAIL'}",
                  "SUCCESS" if results['internet'] else "ERROR")
        
        return results
    
    def full_health_check(self):
        """Run comprehensive health check."""
        print("\n" + "=" * 60)
        print("  NetworkBuster System Health Check")
        print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("=" * 60 + "\n")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "admin": is_admin(),
            "cpu": self.check_cpu(),
            "memory": self.check_memory(),
            "disk": self.check_disk(),
            "ports": self.check_ports(),
            "node": self.check_node_processes(),
            "network": self.check_network()
        }
        
        # Save results
        results_file = PROJECT_PATH / "logs" / "health-latest.json"
        ensure_log_dir()
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        print("\n" + "=" * 60)
        print(f"  Health check complete. Log: {HEALTH_LOG}")
        print("=" * 60)
        
        return results
    
    def monitor_continuous(self, interval=30):
        """Run continuous health monitoring."""
        print(f"\n🔄 Starting continuous monitoring (every {interval}s)")
        print("   Press Ctrl+C to stop\n")
        
        try:
            while True:
                self.full_health_check()
                print(f"\n⏳ Next check in {interval} seconds...\n")
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n\n👋 Monitoring stopped")


def main():
    """Main entry point."""
    health = SystemHealth()
    
    if not PSUTIL_AVAILABLE:
        print("⚠ psutil not installed. Some features will use PowerShell fallback.")
        print("  Install with: pip install psutil\n")
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--monitor":
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            health.monitor_continuous(interval)
        elif sys.argv[1] == "--ports":
            health.check_ports()
        elif sys.argv[1] == "--network":
            health.check_network()
        else:
            print("Usage: python system_health.py [--monitor [interval]] [--ports] [--network]")
    else:
        health.full_health_check()


if __name__ == "__main__":
    main()
