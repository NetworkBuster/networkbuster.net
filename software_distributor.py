"""
Software Distribution Manager
Handles software distribution logic, download links, and deployment.
"""

import os
import json
import hashlib
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import webbrowser


class SoftwareDistributor:
    """Main class for managing software distribution and downloads."""
    
    def __init__(self, config_file: str = "distribution_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.download_queue: List[Dict] = []
        self.active_downloads: Dict[str, float] = {}
        
    def load_config(self) -> Dict:
        """Load distribution configuration."""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        else:
            # Default configuration
            default_config = {
                "software_catalog": [],
                "download_directory": "./downloads",
                "distribution_servers": [],
                "cdn_enabled": True,
                "auto_verify_checksums": True,
                "max_concurrent_downloads": 3,
                "retry_attempts": 3,
                "timeout_seconds": 300
            }
            self.save_config(default_config)
            return default_config
    
    def save_config(self, config: Optional[Dict] = None) -> None:
        """Save configuration to file."""
        if config is None:
            config = self.config
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)
    
    def add_software(self, name: str, version: str, download_url: str, 
                     file_size: int, checksum: str, description: str = "") -> None:
        """Add software to distribution catalog."""
        software_entry = {
            "id": hashlib.md5(f"{name}{version}".encode()).hexdigest(),
            "name": name,
            "version": version,
            "download_url": download_url,
            "file_size": file_size,
            "checksum": checksum,
            "description": description,
            "added_date": datetime.now().isoformat(),
            "download_count": 0
        }
        
        self.config["software_catalog"].append(software_entry)
        self.save_config()
        print(f"Added {name} v{version} to catalog")
    
    def get_software_list(self) -> List[Dict]:
        """Get list of available software."""
        return self.config.get("software_catalog", [])
    
    def generate_download_link(self, software_id: str, base_url: Optional[str] = None) -> str:
        """Generate download link for software."""
        software = self.find_software_by_id(software_id)
        if not software:
            return ""
        
        if base_url:
            # Custom base URL
            return f"{base_url}/download/{software_id}/{software['name']}-{software['version']}"
        else:
            # Use configured download URL
            return software.get("download_url", "")
    
    def find_software_by_id(self, software_id: str) -> Optional[Dict]:
        """Find software entry by ID."""
        for software in self.config["software_catalog"]:
            if software["id"] == software_id:
                return software
        return None
    
    def verify_checksum(self, file_path: str, expected_checksum: str) -> bool:
        """Verify file checksum."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        calculated_checksum = sha256_hash.hexdigest()
        return calculated_checksum == expected_checksum
    
    def download_software(self, software_id: str, destination: Optional[str] = None,
                         progress_callback=None) -> bool:
        """Download software from catalog."""
        software = self.find_software_by_id(software_id)
        if not software:
            print(f"Software with ID {software_id} not found")
            return False
        
        download_url = software["download_url"]
        if not destination:
            destination = os.path.join(
                self.config["download_directory"],
                f"{software['name']}-{software['version']}.zip"
            )
        
        # Create download directory if it doesn't exist
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        
        try:
            print(f"Downloading {software['name']} from {download_url}")
            
            def report_progress(block_num, block_size, total_size):
                if progress_callback and total_size > 0:
                    downloaded = block_num * block_size
                    progress = min(100, (downloaded / total_size) * 100)
                    progress_callback(progress)
            
            urllib.request.urlretrieve(download_url, destination, reporthook=report_progress)
            
            # Verify checksum if enabled
            if self.config.get("auto_verify_checksums", True):
                if self.verify_checksum(destination, software["checksum"]):
                    print("Checksum verification successful")
                else:
                    print("Warning: Checksum verification failed")
                    return False
            
            # Update download count
            software["download_count"] += 1
            self.save_config()
            
            print(f"Download completed: {destination}")
            return True
            
        except Exception as e:
            print(f"Download failed: {e}")
            return False
    
    def export_catalog_html(self, output_file: str = "software_catalog.html") -> None:
        """Export software catalog as HTML page with download links."""
        html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Software Distribution Catalog</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .software-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        .software-card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .software-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        .software-name {
            font-size: 20px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        }
        .software-version {
            color: #7f8c8d;
            font-size: 14px;
            margin-bottom: 10px;
        }
        .software-description {
            color: #555;
            margin-bottom: 15px;
            line-height: 1.5;
        }
        .software-info {
            font-size: 12px;
            color: #95a5a6;
            margin-bottom: 15px;
        }
        .download-btn {
            display: inline-block;
            background-color: #3498db;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
            transition: background-color 0.3s;
        }
        .download-btn:hover {
            background-color: #2980b9;
        }
        .stats {
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;
            text-align: center;
        }
    </style>
</head>
<body>
    <h1>Software Distribution Catalog</h1>
    
    <div class="stats">
        <h3>Total Software Packages: {total_count}</h3>
        <p>Last Updated: {last_updated}</p>
    </div>
    
    <div class="software-grid">
        {software_cards}
    </div>
    
    <footer style="text-align: center; margin-top: 50px; color: #7f8c8d;">
        <p>Powered by Software Distribution Manager</p>
    </footer>
</body>
</html>"""
        
        software_cards = ""
        for software in self.config["software_catalog"]:
            download_link = self.generate_download_link(software["id"])
            file_size_mb = software.get("file_size", 0) / (1024 * 1024)
            
            card = f"""
        <div class="software-card">
            <div class="software-name">{software['name']}</div>
            <div class="software-version">Version: {software['version']}</div>
            <div class="software-description">{software.get('description', 'No description available')}</div>
            <div class="software-info">
                Size: {file_size_mb:.2f} MB<br>
                Downloads: {software.get('download_count', 0)}
            </div>
            <a href="{download_link}" class="download-btn">Download</a>
        </div>"""
            software_cards += card
        
        html_content = html_content.format(
            total_count=len(self.config["software_catalog"]),
            last_updated=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            software_cards=software_cards
        )
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Catalog exported to {output_file}")


class DistributionGUI:
    """GUI application for software distribution management."""
    
    def __init__(self):
        self.distributor = SoftwareDistributor()
        self.root = tk.Tk()
        self.root.title("Software Distribution Manager")
        self.root.geometry("900x600")
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface."""
        # Create notebook (tabs)
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab 1: Software Catalog
        catalog_frame = ttk.Frame(notebook)
        notebook.add(catalog_frame, text="Software Catalog")
        self.setup_catalog_tab(catalog_frame)
        
        # Tab 2: Add Software
        add_frame = ttk.Frame(notebook)
        notebook.add(add_frame, text="Add Software")
        self.setup_add_tab(add_frame)
        
        # Tab 3: Downloads
        download_frame = ttk.Frame(notebook)
        notebook.add(download_frame, text="Downloads")
        self.setup_download_tab(download_frame)
        
        # Tab 4: Export
        export_frame = ttk.Frame(notebook)
        notebook.add(export_frame, text="Export Catalog")
        self.setup_export_tab(export_frame)
        
    def setup_catalog_tab(self, parent):
        """Setup catalog viewing tab."""
        # Treeview for software list
        columns = ("Name", "Version", "Size (MB)", "Downloads")
        self.catalog_tree = ttk.Treeview(parent, columns=columns, show='tree headings')
        
        for col in columns:
            self.catalog_tree.heading(col, text=col)
            self.catalog_tree.column(col, width=150)
        
        self.catalog_tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Buttons
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(btn_frame, text="Refresh", command=self.refresh_catalog).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Copy Download Link", command=self.copy_link).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Download Selected", command=self.download_selected).pack(side='left', padx=5)
        
        self.refresh_catalog()
        
    def setup_add_tab(self, parent):
        """Setup add software tab."""
        # Form fields
        ttk.Label(parent, text="Software Name:").grid(row=0, column=0, sticky='w', padx=10, pady=5)
        self.name_entry = ttk.Entry(parent, width=40)
        self.name_entry.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(parent, text="Version:").grid(row=1, column=0, sticky='w', padx=10, pady=5)
        self.version_entry = ttk.Entry(parent, width=40)
        self.version_entry.grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(parent, text="Download URL:").grid(row=2, column=0, sticky='w', padx=10, pady=5)
        self.url_entry = ttk.Entry(parent, width=40)
        self.url_entry.grid(row=2, column=1, padx=10, pady=5)
        
        ttk.Label(parent, text="File Size (bytes):").grid(row=3, column=0, sticky='w', padx=10, pady=5)
        self.size_entry = ttk.Entry(parent, width=40)
        self.size_entry.grid(row=3, column=1, padx=10, pady=5)
        
        ttk.Label(parent, text="Checksum (SHA256):").grid(row=4, column=0, sticky='w', padx=10, pady=5)
        self.checksum_entry = ttk.Entry(parent, width=40)
        self.checksum_entry.grid(row=4, column=1, padx=10, pady=5)
        
        ttk.Label(parent, text="Description:").grid(row=5, column=0, sticky='nw', padx=10, pady=5)
        self.description_text = tk.Text(parent, width=40, height=5)
        self.description_text.grid(row=5, column=1, padx=10, pady=5)
        
        ttk.Button(parent, text="Add Software", command=self.add_software).grid(row=6, column=1, pady=20)
        
    def setup_download_tab(self, parent):
        """Setup downloads tab."""
        ttk.Label(parent, text="Download Manager", font=('Arial', 14, 'bold')).pack(pady=10)
        
        self.download_list = tk.Listbox(parent, height=15)
        self.download_list.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.progress = ttk.Progressbar(parent, mode='determinate')
        self.progress.pack(fill='x', padx=10, pady=5)
        
        self.status_label = ttk.Label(parent, text="Ready")
        self.status_label.pack(pady=5)
        
    def setup_export_tab(self, parent):
        """Setup export tab."""
        ttk.Label(parent, text="Export Distribution Catalog", font=('Arial', 14, 'bold')).pack(pady=20)
        
        ttk.Label(parent, text="Export catalog as HTML webpage with download links").pack(pady=10)
        
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="Export to HTML", command=self.export_html).pack(side='left', padx=10)
        ttk.Button(btn_frame, text="Open in Browser", command=self.open_catalog_html).pack(side='left', padx=10)
        
        self.export_status = ttk.Label(parent, text="")
        self.export_status.pack(pady=10)
        
    def refresh_catalog(self):
        """Refresh the catalog list."""
        self.catalog_tree.delete(*self.catalog_tree.get_children())
        
        for software in self.distributor.get_software_list():
            size_mb = software.get('file_size', 0) / (1024 * 1024)
            self.catalog_tree.insert('', 'end', software['id'], values=(
                software['name'],
                software['version'],
                f"{size_mb:.2f}",
                software.get('download_count', 0)
            ))
    
    def add_software(self):
        """Add software to catalog."""
        try:
            name = self.name_entry.get()
            version = self.version_entry.get()
            url = self.url_entry.get()
            size = int(self.size_entry.get())
            checksum = self.checksum_entry.get()
            description = self.description_text.get("1.0", "end-1c")
            
            if not all([name, version, url, checksum]):
                messagebox.showerror("Error", "Please fill in all required fields")
                return
            
            self.distributor.add_software(name, version, url, size, checksum, description)
            messagebox.showinfo("Success", f"Added {name} v{version} to catalog")
            
            # Clear form
            self.name_entry.delete(0, 'end')
            self.version_entry.delete(0, 'end')
            self.url_entry.delete(0, 'end')
            self.size_entry.delete(0, 'end')
            self.checksum_entry.delete(0, 'end')
            self.description_text.delete("1.0", "end")
            
            self.refresh_catalog()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add software: {e}")
    
    def copy_link(self):
        """Copy download link to clipboard."""
        selected = self.catalog_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a software item")
            return
        
        software_id = selected[0]
        download_link = self.distributor.generate_download_link(software_id)
        
        self.root.clipboard_clear()
        self.root.clipboard_append(download_link)
        messagebox.showinfo("Success", f"Download link copied to clipboard:\n{download_link}")
    
    def download_selected(self):
        """Download selected software."""
        selected = self.catalog_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a software item")
            return
        
        software_id = selected[0]
        
        def progress_callback(progress):
            self.progress['value'] = progress
            self.status_label.config(text=f"Downloading... {progress:.1f}%")
            self.root.update_idletasks()
        
        def download_thread():
            success = self.distributor.download_software(software_id, progress_callback=progress_callback)
            if success:
                self.status_label.config(text="Download completed!")
                messagebox.showinfo("Success", "Download completed successfully")
            else:
                self.status_label.config(text="Download failed")
                messagebox.showerror("Error", "Download failed")
            self.progress['value'] = 0
        
        threading.Thread(target=download_thread, daemon=True).start()
    
    def export_html(self):
        """Export catalog as HTML."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")]
        )
        
        if file_path:
            self.distributor.export_catalog_html(file_path)
            self.export_status.config(text=f"Exported to: {file_path}")
            messagebox.showinfo("Success", f"Catalog exported to:\n{file_path}")
    
    def open_catalog_html(self):
        """Open exported catalog in browser."""
        catalog_file = "software_catalog.html"
        if not os.path.exists(catalog_file):
            self.distributor.export_catalog_html(catalog_file)
        
        webbrowser.open(f"file://{os.path.abspath(catalog_file)}")
        self.export_status.config(text="Opened in browser")
    
    def run(self):
        """Run the GUI application."""
        self.root.mainloop()


def main():
    """Main entry point."""
    print("=" * 60)
    print("Software Distribution Manager")
    print("=" * 60)
    
    # Start GUI
    app = DistributionGUI()
    app.run()


if __name__ == "__main__":
    main()
