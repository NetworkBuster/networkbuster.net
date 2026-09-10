"""
NetworkBuster Neural Network System
Main Entry Point
Integrates Training, continuous learning, security, and distribution into a single dashboard.
"""

import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import time
import json
import os

# Internal Modules
from security_module import SecurityManager
from continuous_learning import ContinuousLearner
from gemini_cli import GeminiAgent
from software_distributor import SoftwareDistributor

class NetworkBusterDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("NetworkBuster Neural Network Control")
        self.root.geometry("1000x700")
        
        self.security = SecurityManager()
        self.learner = ContinuousLearner()
        self.gemini = GeminiAgent()
        
        self.is_running = False
        
        self.setup_ui()
        self.auth_check()

    def auth_check(self):
        """Simulate a secure login."""
        # For simplicity in this demo, we auto-authenticate or prompt
        # In a real app, this would be a login dialog
        if not self.security.authenticate("admin"):
            messagebox.showwarning("Security Alert", "Authentication failed. Running in Restricted Mode.")

    def setup_ui(self):
        # Header
        header = ttk.Frame(self.root, padding="10")
        header.pack(fill=tk.X)
        ttk.Label(header, text="NetworkBuster Neural Network", font=("Helvetica", 24, "bold")).pack(side=tk.LEFT)
        self.lbl_status = ttk.Label(header, text="SYSTEM OFF", foreground="red", font=("Helvetica", 12, "bold"))
        self.lbl_status.pack(side=tk.RIGHT)

        # Main Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tab 1: Neural Visualizer
        self.tab_viz = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_viz, text="Neural Visualizer")
        self.setup_viz_tab()

        # Tab 2: Continuous Learning
        self.tab_learn = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_learn, text="Evolution Engine")
        self.setup_learning_tab()

        # Tab 3: Security & Logs
        self.tab_sec = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_sec, text="Security & Gemini")
        self.setup_security_tab()

        # Control Bar
        controls = ttk.Frame(self.root, padding="10")
        controls.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.btn_start = ttk.Button(controls, text="ACTIVATE NEURAL NET", command=self.toggle_system)
        self.btn_start.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(controls, text="Exit", command=self.root.quit).pack(side=tk.RIGHT, padx=5)

    def setup_viz_tab(self):
        # A canvas to draw nodes/connections visualizing "Expansion"
        self.canvas = tk.Canvas(self.tab_viz, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.nodes = []

    def setup_learning_tab(self):
        frame = ttk.Frame(self.tab_learn, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Exponential Logic Growth Status", font=("Arial", 16)).pack(pady=10)
        
        self.lbl_gen = ttk.Label(frame, text="Current Generation: 0")
        self.lbl_gen.pack()
        
        self.lbl_samples = ttk.Label(frame, text="Processed Samples: 0")
        self.lbl_samples.pack()
        
        ttk.Label(frame, text="Recent Activity Log:").pack(pady=5, anchor=tk.W)
        self.log_text = tk.Text(frame, height=15)
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def setup_security_tab(self):
        frame = ttk.Frame(self.tab_sec, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Gemini Interface
        ttk.Label(frame, text="Gemini Agent (Secure Channel)", font=("Arial", 14)).pack(pady=5)
        self.gemini_input = ttk.Entry(frame, width=80)
        self.gemini_input.pack(pady=5)
        self.gemini_input.bind("<Return>", self.ask_gemini)
        
        self.gemini_output = tk.Text(frame, height=10, bg="#f0f0f0")
        self.gemini_output.pack(fill=tk.X, pady=5)
        
        # Security Status
        ttk.Label(frame, text="Security Monitor", font=("Arial", 14)).pack(pady=10)
        self.lbl_sec_status = ttk.Label(frame, text="Integrity: OK | Encryption: AES-256")
        self.lbl_sec_status.pack()

    def ask_gemini(self, event):
        query = self.gemini_input.get()
        if not query: return
        self.gemini_output.insert(tk.END, f"User> {query}\n")
        response = self.gemini.respond(query)
        self.gemini_output.insert(tk.END, f"{response}\n\n")
        self.gemini_output.see(tk.END)
        self.gemini_input.delete(0, tk.END)

    def toggle_system(self):
        if not self.is_running:
            self.is_running = True
            self.lbl_status.config(text="SYSTEM ONLINE", foreground="green")
            self.btn_start.config(text="DEACTIVATE")
            
            # Start background threads
            threading.Thread(target=self.run_visualizer, daemon=True).start()
            threading.Thread(target=self.run_learning_monitor, daemon=True).start()
        else:
            self.is_running = False
            self.lbl_status.config(text="SYSTEM OFF", foreground="red")
            self.btn_start.config(text="ACTIVATE NEURAL NET")

    def run_visualizer(self):
        """Simulate visual network expansion."""
        while self.is_running:
            # Add a random node
            x, y = 500, 350 # Center
            import random
            dx = random.randint(-400, 400)
            dy = random.randint(-300, 300)
            
            node_id = self.canvas.create_oval(x+dx-5, y+dy-5, x+dx+5, y+dy+5, fill="#00ff00", outline="#00ff00")
            
            # Connect to random existing node
            if self.nodes:
                target = random.choice(self.nodes)
                coords = self.canvas.coords(target)
                tx, ty = (coords[0]+coords[2])/2, (coords[1]+coords[3])/2
                self.canvas.create_line(x+dx, y+dy, tx, ty, fill="#003300")
            
            self.nodes.append(node_id)
            if len(self.nodes) > 100: # Keep it clean
                old = self.nodes.pop(0)
                self.canvas.delete(old)
                
            time.sleep(0.5)

    def run_learning_monitor(self):
        """Poll the continuous learning state."""
        while self.is_running:
            try:
                # Poll state from file (shared with continuous_learning.py)
                state_file = "evolution_state.json"
                if os.path.exists(state_file):
                    with open(state_file, 'r') as f:
                        state = json.load(f)
                    
                    self.root.after(0, lambda s=state: self.update_learning_ui(s))
            except:
                pass
            time.sleep(2)

    def update_learning_ui(self, state):
        self.lbl_gen.config(text=f"Current Generation: {state.get('generation', 0)}")
        self.lbl_samples.config(text=f"Processed Samples: {state.get('total_samples_processed', 0)}")
        
        # Add to log if new activity
        # (Simplified: just timestamp)
        # self.log_text.insert(tk.END, f"Synced state at {datetime.now().time()}\n")

def main():
    root = tk.Tk()
    app = NetworkBusterDashboard(root)
    root.mainloop()

if __name__ == "__main__":
    main()
