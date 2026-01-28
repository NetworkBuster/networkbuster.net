"""
Device Classifiers

Provides scaffolded implementations for three device classification use cases:
- DeviceTypeClassifier: classify device type (robot, actuator, sensor, etc.)
- TaskClassifier: classify automation task types
- HealthClassifier: detect anomalous/failed device states (predictive maintenance)

Each classifier includes simple training/evaluation scaffolds and example usage.
"""

from typing import Any, Dict, Optional, Tuple
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import numpy as np
import joblib
import os
from ai_training_pipeline import PipelineConfig, AITrainingPipeline, create_default_pipeline


class DeviceTypeClassifier:
    """Simple classifier for device types using scikit-learn RandomForest."""

    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or PipelineConfig(framework="sklearn")
        self.model = RandomForestClassifier(n_estimators=100)

    def train(self, X: np.ndarray, y: np.ndarray):
        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
        self.model.fit(X_train, y_train)
        preds = self.model.predict(X_val)
        acc = accuracy_score(y_val, preds)
        print(f"DeviceTypeClassifier validation accuracy: {acc:.4f}")
        return acc

    def evaluate(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        preds = self.model.predict(X)
        acc = accuracy_score(y, preds)
        precision, recall, f1, _ = precision_recall_fscore_support(y, preds, average="weighted")
        return {"accuracy": acc, "precision": precision, "recall": recall, "f1": f1}

    def save(self, path: str):
        os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
        joblib.dump(self.model, path)
        print(f"Saved DeviceTypeClassifier to {path}")

    def load(self, path: str):
        self.model = joblib.load(path)
        print(f"Loaded DeviceTypeClassifier from {path}")


class TaskClassifier:
    """Classification scaffold for automation tasks. Uses RandomForest by default but can be replaced with TF/PyTorch."""

    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or PipelineConfig(framework="sklearn")
        self.model = RandomForestClassifier(n_estimators=150)

    def train(self, X: np.ndarray, y: np.ndarray):
        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
        self.model.fit(X_train, y_train)
        preds = self.model.predict(X_val)
        acc = accuracy_score(y_val, preds)
        print(f"TaskClassifier validation accuracy: {acc:.4f}")
        return acc

    def evaluate(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        preds = self.model.predict(X)
        acc = accuracy_score(y, preds)
        precision, recall, f1, _ = precision_recall_fscore_support(y, preds, average="weighted")
        return {"accuracy": acc, "precision": precision, "recall": recall, "f1": f1}

    def save(self, path: str):
        os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
        joblib.dump(self.model, path)
        print(f"Saved TaskClassifier to {path}")

    def load(self, path: str):
        self.model = joblib.load(path)
        print(f"Loaded TaskClassifier from {path}")


class HealthClassifier:
    """Anomaly detection for device health using IsolationForest."""

    def __init__(self, contamination: float = 0.01):
        self.model = IsolationForest(contamination=contamination, random_state=42)

    def train(self, X: np.ndarray):
        # Unsupervised: fit on normal behavior
        self.model.fit(X)
        print("HealthClassifier trained on provided normal data")

    def predict_anomaly_score(self, X: np.ndarray) -> np.ndarray:
        # Higher negative score -> more anomalous
        if hasattr(self.model, 'decision_function'):
            return -self.model.decision_function(X)
        return self.model.score_samples(X)

    def predict(self, X: np.ndarray) -> np.ndarray:
        # Returns -1 for anomaly, 1 for normal
        return self.model.predict(X)

    def save(self, path: str):
        os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
        joblib.dump(self.model, path)
        print(f"Saved HealthClassifier to {path}")

    def load(self, path: str):
        self.model = joblib.load(path)
        print(f"Loaded HealthClassifier from {path}")


# Helper utilities

def example_device_type_pipeline():
    """Example: train a DeviceTypeClassifier using random data (placeholder)."""
    X = np.random.rand(1000, 16)  # 16 arbitrary features
    y = np.random.randint(0, 3, 1000)  # three classes: 0,1,2

    clf = DeviceTypeClassifier()
    clf.train(X, y)
    clf.save("checkpoints/device_type_classifier.joblib")


def example_task_pipeline():
    X = np.random.rand(800, 24)
    y = np.random.randint(0, 5, 800)  # five task classes

    clf = TaskClassifier()
    clf.train(X, y)
    clf.save("checkpoints/task_classifier.joblib")


def example_health_pipeline():
    X_normal = np.random.rand(2000, 12)
    hc = HealthClassifier(contamination=0.02)
    hc.train(X_normal)
    hc.save("checkpoints/health_classifier.joblib")


if __name__ == "__main__":
    print("Running example device classifier trainings...")
    example_device_type_pipeline()
    example_task_pipeline()
    example_health_pipeline()


# Small integration helper to plug into AITrainingPipeline if needed

def device_model_builder_for_pipeline(config: PipelineConfig, task: str = "device_type"):
    """Return a small model-like placeholder that AITrainingPipeline can accept as 'model'.
    This function is intentionally simple: it returns a dict describing the classifier.
    """
    return {"task": task, "framework": config.framework, "status": "stub"}
