"""
Continuous Learning & Evolution Module

This module implements the "Exponential Logic Growth" system.
It automates the feedback loop between deployed devices and the central training pipeline.

Features:
1. Data Ingestion: Automatically ingests logs and feedback from connected devices.
2. Drift Detection: Monitors model performance and data distribution changes.
3. Automated Retraining: Triggers fine-tuning or full retraining when criteria are met.
4. Model Promotion: Safely promotes improved models to the registry for the next release cycle.
5. Device Repurposing: Detects when a device capabilities can be extended based on new data patterns.
"""

import os
import json
import time
import shutil
import numpy as np
from datetime import datetime
from typing import List, Dict, Optional
import logging

# Internal imports
from ai_training_pipeline import AITrainingPipeline, PipelineConfig, TrainingMetrics, create_default_pipeline
from model_registry import save_model, load_model, checkpoint_path, get_checkpoint_dir
from device_classifiers import DeviceTypeClassifier, TaskClassifier, HealthClassifier

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ContinuousLearner")

class InternalState:
    """Tracks the state of the evolution engine."""
    def __init__(self, state_file="evolution_state.json"):
        self.state_file = state_file
        self.load()

    def load(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {
                "generation": 0,
                "last_update": None,
                "models": {},
                "total_samples_processed": 0
            }

    def save(self):
        self.data["last_update"] = datetime.utcnow().isoformat()
        with open(self.state_file, 'w') as f:
            json.dump(self.data, f, indent=4)

    def increment_generation(self):
        self.data["generation"] += 1
        self.save()

class ContinuousLearner:
    def __init__(self, incoming_data_dir="data/incoming", processed_data_dir="data/processed"):
        self.incoming_dir = incoming_data_dir
        self.processed_dir = processed_data_dir
        self.state = InternalState()
        
        os.makedirs(self.incoming_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)
        
        # Load active models
        self.device_classifier = DeviceTypeClassifier()
        try:
            self.device_classifier.load() # Loads from default registry path
        except:
            logger.warning("No existing DeviceTypeClassifier found. Starting fresh.")

    def scan_for_feedback(self) -> List[str]:
        """Scans the incoming directory for new device data logs."""
        files = [os.path.join(self.incoming_dir, f) for f in os.listdir(self.incoming_dir) if f.endswith('.json') or f.endswith('.npy')]
        if files:
            logger.info(f"Found {len(files)} new data packets from devices.")
        return files

    def ingest_and_evaluate(self, file_paths: List[str]):
        """
        Process incoming data. 
        If data suggests drift or new capabilities (repurposing), trigger evolution.
        """
        aggregated_X = []
        aggregated_y = []
        
        # Simulate loading data (in prod, parse JSON/NPY properly)
        # For this logic demo, we assume these are feature vectors and labels
        for fp in file_paths:
            try:
                # Mock ingestion logic for different file types
                if fp.endswith('.npy'):
                    data = np.load(fp, allow_pickle=True).item()
                    X_new = data.get('features')
                    y_new = data.get('labels')
                elif fp.endswith('.json'):
                    with open(fp, 'r') as f:
                        data = json.load(f)
                    X_new = np.array(data.get('features'))
                    y_new = np.array(data.get('labels'))
                
                if X_new is not None and y_new is not None:
                    aggregated_X.append(X_new)
                    aggregated_y.append(y_new)
                    
                # Move to processed
                shutil.move(fp, os.path.join(self.processed_dir, os.path.basename(fp)))
                
            except Exception as e:
                logger.error(f"Failed to ingest {fp}: {e}")

        if not aggregated_X:
            return

        # Stack data
        X_batch = np.vstack(aggregated_X)
        y_batch = np.hstack(aggregated_y)
        
        self.state.data["total_samples_processed"] += len(X_batch)
        
        # 1. Evaluate Current Model on New Data (Drift Check)
        drift_detected = self._check_drift(X_batch, y_batch)
        
        # 2. Check for Repurposing Opportunities (New Classes?)
        repurposing_detected = self._check_repurposing(y_batch)

        if drift_detected or repurposing_detected:
            logger.info("Evolution criteria met. Initiating logic growth cycle...")
            self.evolve_model(X_batch, y_batch)
        else:
            logger.info("Data ingested. No immediate retraining required.")
        
        self.state.save()

    def _check_drift(self, X, y, threshold=0.85):
        """Check if current model performance on new data is below expectation."""
        metrics = self.device_classifier.evaluate(X, y)
        acc = metrics.get('accuracy', 0.0)
        logger.info(f"Performance on new batch: Accuracy={acc:.4f}")
        return acc < threshold

    def _check_repurposing(self, y):
        """Check if new labels have appeared that the model didn't know about."""
        # Simple heuristic: if we see labels outside known range (mock logic)
        # Real implementation would check against model.classes_
        return False # Placeholder

    def evolve_model(self, new_X, new_y):
        """
        Retrain the model mixing old knowledge (if viable) and new data.
        This is where 'Exponential Growth' happens - the model adapts to new conditions.
        """
        logger.info(f"Training Generation {self.state.data['generation'] + 1}...")
        
        # In a real system, you would load historical data here to prevent catastrophic forgetting
        # For this scaffold, we fine-tune on the new batch (Online Learning style)
        
        # Update Pipeline Config for Fine-tuning
        pipeline = create_default_pipeline({
            "model_type": "device_classifier_evolver",
            "framework": "sklearn",
            "epochs": 10 # Short fine-tuning
        })
        
        # Re-train (Wrapper around the specific classifier logic)
        # Depending on the underlying model (RandomForest vs Neural Net), this differs.
        # For RandomForest, we might train a new one and ensemble or replace.
        
        current_acc = 0
        try:
           metrics = self.device_classifier.evaluate(new_X, new_y)
           current_acc = metrics['accuracy']
        except:
            pass

        # "Grow" the logic: Train a candidate model
        candidate_clf = DeviceTypeClassifier()
        # Merge datasets logic would go here
        candidate_acc = candidate_clf.train(new_X, new_y)
        
        logger.info(f"Candidate Model Accuracy: {candidate_acc:.4f} vs Current: {current_acc:.4f}")
        
        if candidate_acc >= current_acc:
            logger.info("Candidate model is superior. Promoting to Registry.")
            self.state.increment_generation()
            
            # Save to registry (overwrites 'latest' or creates versioned)
            version_name = f"device_type_v{self.state.data['generation']}"
            save_model(version_name, candidate_clf.model)
            
            # Update 'latest' pointer
            self.device_classifier = candidate_clf
            self.device_classifier.save(None) # Saves to default 'latest' path via registry
            
            logger.info(f"Logic upgraded to Generation {self.state.data['generation']}")
        else:
            logger.info("Candidate model failed to improve. Discarding.")

def run_continuous_learning_loop(interval_seconds=60, max_cycles=None):
    """Main loop process."""
    learner = ContinuousLearner()
    print("Continuous Learning Engine Online.")
    print("Watching for device feedback streams...")
    
    cycles = 0
    try:
        while True:
            if max_cycles is not None and cycles >= max_cycles:
                print(f"Completed {max_cycles} cycles. Exiting.")
                break
                
            new_files = learner.scan_for_feedback()
            if new_files:
                learner.ingest_and_evaluate(new_files)
            
            cycles += 1
            if max_cycles is None or cycles < max_cycles:
                time.sleep(interval_seconds)
            
    except KeyboardInterrupt:
        print("Shutting down Continuous Learning Engine.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--cycles", type=int, default=None, help="Number of cycles to run (default: infinite)")
    parser.add_argument("--interval", type=int, default=5, help="Seconds between checks")
    args = parser.parse_args()

    # Create dummy incoming data for demonstration if empty
    incoming = "data/incoming"
    if not os.path.exists(incoming):
        os.makedirs(incoming)
    
    # Generate a sample packet if none exists to demonstrate immediate reaction
    dummy_packet = os.path.join(incoming, "device_feedback_sample_001.json")
    if not os.path.exists(dummy_packet):
        import numpy as np
        data = {
            "features": np.random.rand(50, 16).tolist(), # Matches DeviceTypeClassifier shape
            "labels": np.random.randint(0, 3, 50).tolist(),
            "device_id": "robot_unit_alpha_1",
            "timestamp": datetime.utcnow().isoformat()
        }
        with open(dummy_packet, 'w') as f:
            json.dump(data, f)
            
    run_continuous_learning_loop(interval_seconds=args.interval, max_cycles=args.cycles)
