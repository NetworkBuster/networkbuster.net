"""
Simulate Device Feedback

Generates synthetic feedback streams from multiple 'devices' to test the 
continuous learning module's ability to repurpose and grow logic.
"""

import os
import json
import time
import numpy as np
import random
from datetime import datetime

INCOMING_DIR = "data/incoming"

def generate_feedback_stream(num_packets=5, interval=2):
    os.makedirs(INCOMING_DIR, exist_ok=True)
    
    device_roles = ["assembler", "welder", "inspector", "repurposed_scout"]
    
    print(f"Simulating feedback from {len(device_roles)} active devices...")
    
    for i in range(num_packets):
        role = random.choice(device_roles)
        device_id = f"device_{role}_{random.randint(100, 999)}"
        
        # Simulate data drift or repurposing:
        # If 'repurposed_scout', generate slightly different feature distribution
        if role == "repurposed_scout":
            features = np.random.rand(20, 16) * 1.5 + 0.2 # Shifted distribution
            labels = np.random.randint(0, 3, 20)
        else:
            features = np.random.rand(20, 16)
            labels = np.random.randint(0, 3, 20)
            
        packet = {
            "device_id": device_id,
            "role": role,
            "timestamp": datetime.utcnow().isoformat(),
            "features": features.tolist(),
            "labels": labels.tolist(),
            "metrics": {
                "battery": random.uniform(20.0, 100.0),
                "temperature": random.uniform(30.0, 75.0)
            }
        }
        
        fname = f"feedback_{int(time.time())}_{device_id}.json"
        path = os.path.join(INCOMING_DIR, fname)
        
        with open(path, 'w') as f:
            json.dump(packet, f)
            
        print(f"[{datetime.now().time()}] Device {device_id} uploaded feedback packet ({len(labels)} samples)")
        time.sleep(interval)

if __name__ == "__main__":
    generate_feedback_stream()
