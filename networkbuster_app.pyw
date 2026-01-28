"""
NetworkBuster GUI Application Launcher
Silent launcher without console window
"""

import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import threading
import webbrowser
from datetime import datetime

# Ensure we're in the right directory
os.chdir(Path(__file__).parent)

class NetworkBusterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NetworkBuster Control Panel")
        self.root.geometry("600x700")
        self.root.resizable(False, False)
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Header
        header_frame = tk.Frame(root, bg="#1e1e1e", height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="NetworkBuster",
            font=("Segoe UI", 24, "bold"),
            bg="#1e1e1e",
            fg="#00ff00"
        )
        title_label.pack(pady=10)
        
        subtitle_label = tk.Label(
            header_frame,
            text="All-in-One Network Management Suite",
            font=("Segoe UI", 10),
            bg="#1e1e1e",
            fg="#888888"
        )
        subtitle_label.pack()
        
        # Main container
        main_frame = tk.Frame(root, bg="#2d2d2d")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Status section
        status_frame = tk.LabelFrame(
            main_frame,
            text="System Status",
            font=("Segoe UI", 11, "bold"),
            bg="#2d2d2d",
            fg="#ffffff",
            padx=10,
            pady=10
        )
        status_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.status_label = tk.Label(
            status_frame,
            text="⚪ System Idle",
            font=("Segoe UI", 10),
            bg="#2d2d2d",
            fg="#ffff00"
        )
        self.status_label.pack()
        
        # Scheduled launch section
        schedule_frame = tk.LabelFrame(
            main_frame,
            text="Scheduled Launch",
            font=("Segoe UI", 11, "bold"),
            bg="#2d2d2d",
            fg="#ffffff",
            padx=10,
            pady=10
        )
        schedule_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.schedule_label = tk.Label(
            schedule_frame,
            text="📅 January 17, 2026 at 9:00 AM\n⏰ Countdown: 14 days",
            font=("Segoe UI", 10),
            bg="#2d2d2d",
            fg="#ffffff"
        )
        self.schedule_label.pack()
        
        # Quick actions
        actions_frame = tk.LabelFrame(
            main_frame,
            text="Quick Actions",
            font=("Segoe UI", 11, "bold"),
            bg="#2d2d2d",
            fg="#ffffff",
            padx=10,
            pady=10
        )
        actions_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Button grid
        btn_frame = tk.Frame(actions_frame, bg="#2d2d2d")
        btn_frame.pack(fill=tk.X)
        
        # Row 1
        self.create_button(btn_frame, "🚀 Start All Services", self.start_services, 0, 0)
        self.create_button(btn_frame, "🛑 Stop All Services", self.stop_services, 0, 1)
        
        # Row 2
        self.create_button(btn_frame, "📊 Check Status", self.check_status, 1, 0)
        self.create_button(btn_frame, "⚡ Max Power Mode", self.max_power, 1, 1)
        
        # Dashboards section
        dash_frame = tk.LabelFrame(
            main_frame,
            text="Dashboards",
            font=("Segoe UI", 11, "bold"),
            bg="#2d2d2d",
            fg="#ffffff",
            padx=10,
            pady=10
        )
        dash_frame.pack(fill=tk.X, pady=(0, 15))
        
        dash_btn_frame = tk.Frame(dash_frame, bg="#2d2d2d")
        dash_btn_frame.pack(fill=tk.X)
        
        self.create_button(dash_btn_frame, "🎮 Mission Control", lambda: self.open_url("http://localhost:5000"), 0, 0)
        self.create_button(dash_btn_frame, "🔍 API Tracer", lambda: self.open_url("http://localhost:8000"), 0, 1)
        self.create_button(dash_btn_frame, "🗺️ Network Map", lambda: self.open_url("http://localhost:6000"), 1, 0)
        self.create_button(dash_btn_frame, "🚀 Universal Launch", lambda: self.open_url("http://localhost:7000"), 1, 1)
        
        # Service status display
        service_frame = tk.LabelFrame(
            main_frame,
            text="Service Monitor",
            font=("Segoe UI", 11, "bold"),
            bg="#2d2d2d",
            fg="#ffffff",
            padx=10,
            pady=10
        )
        service_frame.pack(fill=tk.BOTH, expand=True)
        
        self.service_text = tk.Text(
            service_frame,
            height=10,
            font=("Consolas", 9),
            bg="#1e1e1e",
            fg="#00ff00",
            insertbackground="#00ff00",
            relief=tk.FLAT
        )
        self.service_text.pack(fill=tk.BOTH, expand=True)
        self.service_text.insert("1.0", "Click 'Check Status' to view service information...")
        
        # Auto-refresh status
        self.refresh_status()
    
    def create_button(self, parent, text, command, row, col):
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=("Segoe UI", 10, "bold"),
            bg="#0078d4",
            fg="#ffffff",
            activebackground="#005a9e",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            cursor="hand2",
            height=2,
            width=20
        )
        btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
        parent.grid_columnconfigure(col, weight=1)
    
    def run_command(self, command):
        """Run command in background"""
        def execute():
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    cwd=Path(__file__).parent
                )
                return result.stdout
            except Exception as e:
                return f"Error: {e}"
        
        thread = threading.Thread(target=execute)
        thread.daemon = True
        thread.start()
    
    def start_services(self):
        self.status_label.config(text="🟢 Starting services...", fg="#00ff00")
        self.run_command("python networkbuster_launcher.py --start")
        self.root.after(3000, self.check_status)
    
    def stop_services(self):
        self.status_label.config(text="🟡 Stopping services...", fg="#ffff00")
        self.run_command("python networkbuster_launcher.py --stop")
        self.root.after(1000, lambda: self.status_label.config(text="⚪ Services stopped", fg="#888888"))
    
    def check_status(self):
        self.status_label.config(text="🔄 Checking status...", fg="#00ffff")
        
        def get_status():
            try:
                result = subprocess.run(
                    "python networkbuster_launcher.py --status",
                    shell=True,
                    capture_output=True,
                    text=True,
                    cwd=Path(__file__).parent
                )
                self.service_text.delete("1.0", tk.END)
                self.service_text.insert("1.0", result.stdout)
                self.status_label.config(text="🟢 Status updated", fg="#00ff00")
            except Exception as e:
                self.service_text.delete("1.0", tk.END)
                self.service_text.insert("1.0", f"Error: {e}")
                self.status_label.config(text="🔴 Status check failed", fg="#ff0000")
        
        thread = threading.Thread(target=get_status)
        thread.daemon = True
        thread.start()
    
    def max_power(self):
        response = messagebox.askyesno(
            "Max Power Mode",
            "Enable maximum power production mode?\n\n" +
            "This will:\n" +
            "• Set High Performance power plan\n" +
            "• Disable CPU throttling\n" +
            "• Optimize network settings\n" +
            "• Set realtime priority\n\n" +
            "Administrator privileges required."
        )
        
        if response:
            self.status_label.config(text="⚡ Enabling max power...", fg="#ffff00")
            subprocess.Popen(
                'powershell -Command "Start-Process powershell -ArgumentList \'-ExecutionPolicy Bypass -File run_launcher_admin.ps1\' -Verb RunAs"',
                shell=True
            )
    
    def open_url(self, url):
        webbrowser.open(url)
    
    def refresh_status(self):
        """Auto-refresh status every 10 seconds"""
        # Update countdown
        launch_date = datetime(2026, 1, 17, 9, 0, 0)
        now = datetime.now()
        delta = launch_date - now
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        countdown_text = f"📅 January 17, 2026 at 9:00 AM\n⏰ Countdown: {days}d {hours}h {minutes}m"
        self.schedule_label.config(text=countdown_text)
        
        # Schedule next refresh
        self.root.after(10000, self.refresh_status)

def main():
    root = tk.Tk()
    app = NetworkBusterApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
