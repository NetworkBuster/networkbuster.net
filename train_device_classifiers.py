"""Simple CLI to train one or more device classifiers for examples and integration tests."""

import argparse
import numpy as np
from device_classifiers import DeviceTypeClassifier, TaskClassifier, HealthClassifier


def generate_dummy_data(device_type: str):
    if device_type == "device_type":
        X = np.random.rand(1000, 16)
        y = np.random.randint(0, 3, 1000)
        return X, y
    if device_type == "task":
        X = np.random.rand(800, 24)
        y = np.random.randint(0, 5, 800)
        return X, y
    if device_type == "health":
        X = np.random.rand(2000, 12)
        return X, None
    raise ValueError("Unknown device type")


def main():
    parser = argparse.ArgumentParser(description="Train device classifiers")
    parser.add_argument("--which", choices=["device_type", "task", "health", "all"], default="all")
    args = parser.parse_args()

    if args.which in ("device_type", "all"):
        X, y = generate_dummy_data("device_type")
        clf = DeviceTypeClassifier()
        clf.train(X, y)
        clf.save("checkpoints/device_type_classifier.joblib")

    if args.which in ("task", "all"):
        X, y = generate_dummy_data("task")
        clf = TaskClassifier()
        clf.train(X, y)
        clf.save("checkpoints/task_classifier.joblib")

    if args.which in ("health", "all"):
        X, _ = generate_dummy_data("health")
        hc = HealthClassifier(contamination=0.02)
        hc.train(X)
        hc.save("checkpoints/health_classifier.joblib")

    print("Training complete")


if __name__ == "__main__":
    main()
