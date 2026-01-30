import os
import asyncio
import json
from datetime import datetime
from pathlib import Path
import importlib.util

# Load the ai-training-pipeline module (filename has hyphens)
spec = importlib.util.spec_from_file_location(
    "ai_training_pipeline",
    Path(__file__).resolve().parents[1] / "ai-training-pipeline.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

async def main(connection_string: str, dataset_name: str = "training-sample.csv", model_key: str = "visitor-behavior-model"):
    # 1. Create a small sample dataset
    datasets_dir = Path("./datasets")
    datasets_dir.mkdir(exist_ok=True)
    sample_path = datasets_dir / dataset_name
    sample_content = "user_id,feature1,feature2,label\n1,0.1,0.2,1\n2,0.3,0.6,0\n3,0.5,0.1,1\n"
    sample_path.write_text(sample_content)

    # 2. Upload dataset
    manager = module.TrainingDatasetManager(connection_string)
    ok = await manager.upload_dataset(str(sample_path), dataset_name)
    if not ok:
        print("Failed to upload dataset")
        return

    # 3. Enqueue job
    queue_client = module.QueueClient.from_connection_string(connection_string, module.AITrainingPipelineConfig.TRAINING_QUEUE_NAME)
    try:
        queue_client.create_queue()
    except Exception:
        pass

    message = json.dumps({
        'job_id': model_key,
        'dataset': dataset_name,
        'submitted_at': datetime.now().isoformat()
    })
    queue_client.send_message(message)
    print(f"Enqueued job: {model_key}")

    # 4. Optionally run the orchestrator processing now (poll once)
    orchestrator = module.TrainingOrchestrator(connection_string)
    await orchestrator.process_training_queue()

if __name__ == '__main__':
    conn = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    if not conn:
        print('AZURE_STORAGE_CONNECTION_STRING not set')
    else:
        asyncio.run(main(conn))