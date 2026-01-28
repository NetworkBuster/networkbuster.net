# AI Training Pipeline - Integration Guide

## Overview
This module provides a flexible AI training pipeline for robot and automation systems. It supports multiple ML frameworks and can be easily integrated into any program.

## Features
- **Multi-Framework Support**: PyTorch, TensorFlow, Scikit-learn
- **Easy Configuration**: JSON-based configuration files
- **Flexible Architecture**: Custom model builders and callbacks
- **Training Management**: Automatic checkpointing, early stopping, and logging
- **Model Export**: Multiple export formats for deployment
- **Extensible**: Easy to add custom functionality

## Quick Start

### 1. Basic Usage

```python
from ai_training_pipeline import AITrainingPipeline, PipelineConfig

# Create configuration
config = PipelineConfig(
    model_type="robot_controller",
    framework="pytorch",
    learning_rate=0.001,
    batch_size=64,
    epochs=100
)

# Initialize pipeline
pipeline = AITrainingPipeline(config)

# Build model
pipeline.build_model()

# Train model
history = pipeline.train(train_data, train_labels, val_data, val_labels)

# Evaluate
results = pipeline.evaluate(test_data, test_labels)

# Export for deployment
pipeline.export_model("model_export.onnx", format="onnx")
```

### 2. Using Configuration Files

```python
from ai_training_pipeline import AITrainingPipeline

# Create pipeline
pipeline = AITrainingPipeline()

# Load configuration from JSON
pipeline.load_config("ai_pipeline_config_example.json")

# Build and train
pipeline.build_model()
pipeline.train(train_data, train_labels)
```

### 3. Custom Model Builder

```python
def custom_model_builder(config):
    """Your custom model architecture"""
    # Define your model here
    model = YourCustomModel(
        input_size=config.input_shape,
        output_size=config.output_shape
    )
    return model

# Use custom builder
pipeline = AITrainingPipeline(config)
pipeline.build_model(custom_builder=custom_model_builder)
```

### 4. Adding Callbacks

```python
def training_callback(metrics):
    """Custom callback for training monitoring"""
    print(f"Epoch {metrics.epoch}: Loss = {metrics.train_loss}")
    # Add custom logic (e.g., send to monitoring dashboard)

pipeline.add_callback(training_callback)
pipeline.train(train_data, train_labels)
```

## Integration Examples

### Example 1: Robot Control System

> **Message:** Build and train a reliable, real-time robot navigation model—this walkthrough shows data collection, configuration, safe training practices, and deployment steps for production robot systems.

**Description:** Robot control models require high-frequency inference, low-latency inputs from multiple sensors, and robust handling of edge cases. This example shows how to configure the pipeline for navigation/control tasks and integrates safety checks (validation, checkpointing, and staged rollout).

**Walkthrough:**

1. **Collect data** — Record synchronized sensor logs (IMU, lidar, cameras, encoders) and control signals. Store timestamps and environment/context metadata. Split into train/validation/test sets and keep an isolated validation log for safety tests.
2. **Preprocess** — Normalize sensor inputs, align timestamps, downsample or window data to match control frequency, and create input/label pairs for sequence-to-sequence or policy models.
3. **Configure the pipeline** — Use a config optimized for control frequency and batch size. Example:

```python
config = {
    "model_type": "robot_navigation",
    "framework": "pytorch",
    "learning_rate": 0.0005,
    "batch_size": 128,
    "epochs": 200,
    "custom_params": {
        "control_frequency": 50,  # Hz
        "input_window": 10,       # timesteps
        "sensor_inputs": 12,
        "actuator_outputs": 6
    }
}
```

4. **Build a model** — Use a custom model builder for RNNs, temporal CNNs, or transformer-based controllers. Example:

```python
def robot_model_builder(cfg):
    # Return a PyTorch model tailored to cfg.input_window and sensor count
    return MyRobotController(cfg)

pipeline = create_default_pipeline(config)
pipeline.build_model(custom_builder=robot_model_builder)
```

5. **Training with safety** — Add callbacks to log metrics and halt training if validation performance degrades on safety-critical tests. Use checkpointing and early stopping.

```python
def safety_callback(metrics):
    # Example: stop if validation loss spikes
    if metrics.val_loss > 2.0 * metrics.train_loss:
        raise RuntimeError("Potential instability detected")
pipeline.add_callback(safety_callback)

history = pipeline.train(train_data, train_labels, val_data, val_labels)
```

6. **Evaluate** — Validate on held-out scenarios (obstacle courses, edge cases). Monitor false positives/negatives, latency, and closed-loop performance in simulation.
7. **Export and deploy** — Export to ONNX or platform-specific format and integrate into the robot runtime for real-time inference. Start in simulation, then staged field tests.

```python
pipeline.export_model("robot_controller.onnx", format="onnx")
```

8. **Monitoring & Rollout** — Keep continuous monitoring, collect new failure cases, and schedule retraining with collected data. Use staged rollout and automatic rollback on safety metric violation.

### Example 2: Automation Task Learning

> **Message:** Quickly train models that learn automation tasks from demonstrations or logs; follow this walkthrough to set up training, validation, and safe deployment in an automated environment.

**Description:** Automation task learning covers pick-and-place, assembly steps, and sequence learning. Models may be classification, sequence prediction, or imitation learning architectures depending on the task.

**Walkthrough:**

1. **Define the task** — Determine whether the problem is classification (task ID), sequence prediction (action sequence), or imitation learning (state->action mapping). Collect demonstrations or labeled logs accordingly.
2. **Prepare data** — Annotate actions, normalize sensor streams, and augment rare classes. Create time-windowed samples for temporal models.
3. **Choose model & config** — For sequence tasks, TensorFlow RNN/LSTM/Transformer models are common. Example config:

```python
config = PipelineConfig(
    model_type="task_automation",
    framework="tensorflow",
    learning_rate=0.001,
    batch_size=32,
    epochs=150,
)
```

4. **Add monitoring and checkpoints** — Use callbacks to capture validation accuracy and domain-specific metrics (e.g., task completion rate).

```python
def monitor_performance(metrics):
    if metrics.val_accuracy > 0.95:
        print("Target accuracy reached!")

pipeline = AITrainingPipeline(config)
pipeline.add_callback(monitor_performance)
```

5. **Train iteratively** — Start small, validate, expand dataset, and re-train. Use transfer learning where available to speed convergence.
6. **Validate in simulator** — Run learned policies or classifiers in a controlled simulation before hardware deployment. Measure task success rate and error modes.
7. **Deploy & integrate** — Package trained models as a service or embed into the automation controller. Provide fallbacks and human-in-the-loop approval for critical operations.

```python
pipeline.build_model()
pipeline.train(task_data, task_labels)
pipeline.export_model("task_model.onnx")
```

### Example 3: Predictive Maintenance

> **Message:** Detect anomalies before failures occur—follow this walkthrough to prepare features, tune thresholds, and deploy a lightweight model for real-time monitoring.

**Description:** Predictive maintenance models detect anomalies or predict remaining useful life using historical sensor data. They are often lightweight, require careful feature engineering, and emphasize high precision for failure detection.

**Walkthrough:**

1. **Collect and label data** — Aggregate historical sensor readings, maintenance logs, and failure events. Label windows preceding failures for supervised approaches or use unsupervised anomaly detection for unlabeled data.
2. **Feature engineering** — Extract statistical features, FFTs, rolling-window aggregates, and domain-specific indicators. Scale and remove seasonal trends if needed.
3. **Select model & config** — For unsupervised anomaly detection, sklearn models such as IsolationForest or OneClassSVM are practical; for supervised LSTM-based RUL prediction, use sequence models.

```python
pipeline = create_default_pipeline({
    "model_type": "anomaly_detection",
    "framework": "sklearn",
    "custom_params": {
        "detection_threshold": 0.85,
        "feature_count": 24
    }
})
```

4. **Train and tune** — Use cross-validation, tune thresholds for the desired precision/recall trade-off, and measure AUC and F1 on hold-out data.

```python
pipeline.build_model()
pipeline.train(train_features, train_labels, val_data=val_features, val_labels=val_labels)
```

5. **Validate** — Evaluate on unseen machines or time periods, and run backtesting to ensure low false-alarm rate.
6. **Deploy for real-time inference** — Export model and serve via a lightweight service or embed on edge devices for low-latency prediction.

```python
pipeline.export_model("maintenance_model.onnx")
# Example prediction
predictions = pipeline.predict(live_sensor_data)
```

7. **Monitoring & retraining** — Continuously collect new failures and retrain regularly; set up alerts for drift and degraded performance.

---

## Device Classification Examples ✅

> **Message:** Three ready-made classifier scaffolds are provided—Device Type, Task, and Health (anomaly) classifiers. Use these to bootstrap real device classification tasks or integrate them into the main AI pipeline.

**Overview:** The `device_classifiers.py` module contains three classes:
- `DeviceTypeClassifier` — supervised classifier for device categories (e.g., robot, sensor, actuator).
- `TaskClassifier` — supervised classifier for automation task types (pick-and-place, welding, inspection, etc.).
- `HealthClassifier` — unsupervised anomaly detector for device health (IsolationForest).

### Quick start (examples)

```python
# Train all example classifiers with dummy data
python train_device_classifiers.py --which all

# Train only the health (anomaly) detector
python train_device_classifiers.py --which health
```

### Device Type Classifier (walkthrough)

1. **Collect labeled examples** — Gather feature vectors for each device class and label them (e.g., robot=0, sensor=1, actuator=2).
2. **Preprocess** — Normalize and impute missing values.
3. **Train** — Use `DeviceTypeClassifier().train(X, y)` and check validation accuracy.
4. **Export** — Save the model with `save(path)` and ship alongside the runtime.

```python
from device_classifiers import DeviceTypeClassifier
clf = DeviceTypeClassifier()
clf.train(X_train, y_train)
clf.save("checkpoints/device_type_classifier.joblib")
```

### Task Classifier (walkthrough)

1. **Collect task-labeled traces** — Encode sequence or aggregated features representing task runs.
2. **Train & validate** — Tune hyperparameters and inspect per-class metrics.
3. **Deploy** — Export and serve as a microservice or embed into the controller.

```python
from device_classifiers import TaskClassifier
clf = TaskClassifier()
clf.train(X_train, y_train)
clf.save("checkpoints/task_classifier.joblib")
```

### Health Classifier (walkthrough)

1. **Collect normal operation data** — Train the model on healthy behavior to learn a baseline.
2. **Train** — `HealthClassifier().train(X_normal)` where X_normal contains only nominal data.
3. **Flag anomalies** — Use `predict(X)` or `predict_anomaly_score(X)` to identify outliers.

```python
from device_classifiers import HealthClassifier
hc = HealthClassifier(contamination=0.02)
 hc.train(X_normal)
 scores = hc.predict_anomaly_score(X_live)
```

**Note:** These modules are scaffolds—replace RandomForest/IsolationForest with your production models, add feature extraction, and integrate the resulting saved models into the runtime environment.

---


## Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model_type` | str | "neural_network" | Type of model to train |
| `framework` | str | "pytorch" | ML framework (pytorch/tensorflow/sklearn) |
| `learning_rate` | float | 0.001 | Learning rate for optimization |
| `batch_size` | int | 32 | Training batch size |
| `epochs` | int | 100 | Number of training epochs |
| `validation_split` | float | 0.2 | Validation data split ratio |
| `checkpoint_dir` | str | "./checkpoints" | Directory for model checkpoints |
| `log_dir` | str | "./logs" | Directory for training logs |
| `early_stopping` | bool | true | Enable early stopping |
| `patience` | int | 10 | Early stopping patience (epochs) |
| `custom_params` | dict | {} | Custom parameters for specific use cases |

## Advanced Features

### Distributed Training
```python
config.custom_params["distributed_training"] = True
config.custom_params["num_workers"] = 4
```

### GPU Acceleration
```python
config.custom_params["gpu_enabled"] = True
config.custom_params["device"] = "cuda:0"
```

### Mixed Precision Training
```python
config.custom_params["mixed_precision"] = True
```

### Custom Loss Functions
```python
config.custom_params["loss_function"] = "custom_mse"
config.custom_params["loss_weights"] = [0.7, 0.3]
```

## API Reference

### AITrainingPipeline Class

#### Methods

- `__init__(config: PipelineConfig)` - Initialize pipeline
- `load_config(config_path: str)` - Load configuration from JSON
- `save_config(config_path: str)` - Save configuration to JSON
- `build_model(custom_builder: Callable)` - Build the AI model
- `add_callback(callback: Callable)` - Add training callback
- `train(train_data, train_labels, val_data, val_labels)` - Train the model
- `evaluate(test_data, test_labels)` - Evaluate model performance
- `predict(input_data)` - Make predictions
- `save_checkpoint(checkpoint_name: str)` - Save model checkpoint
- `load_checkpoint(checkpoint_name: str)` - Load model checkpoint
- `export_model(export_path: str, format: str)` - Export model for deployment

## Best Practices

1. **Always save your configuration** - Use `save_config()` to track experiments
2. **Use callbacks for monitoring** - Add custom callbacks for real-time monitoring
3. **Enable early stopping** - Prevent overfitting with early stopping
4. **Regular checkpointing** - Save checkpoints during long training sessions
5. **Validate before deployment** - Always evaluate on test data before exporting

## Troubleshooting

### Issue: Model not training
- Check that `build_model()` is called before `train()`
- Verify data format matches expected input shape
- Check learning rate isn't too high or too low

### Issue: Poor performance
- Increase epochs or adjust learning rate
- Check validation split ratio
- Try different frameworks or model architectures

### Issue: Out of memory
- Reduce batch size
- Disable mixed precision training
- Use gradient accumulation

## Support & Contribution

For issues, feature requests, or contributions, please refer to the main project documentation.

## License

See main project license file.
