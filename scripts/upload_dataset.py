import os
import asyncio
from pathlib import Path
import importlib.util

# Load the pipeline module
spec = importlib.util.spec_from_file_location(
    "ai_training_pipeline",
    Path(__file__).resolve().parents[1] / "ai-training-pipeline.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

async def upload(connection_string: str, local_path: str, blob_name: str = None):
    if not blob_name:
        blob_name = Path(local_path).name

    manager = module.TrainingDatasetManager(connection_string)
    ok = await manager.upload_dataset(local_path, blob_name)
    if ok:
        print(f"Uploaded {local_path} to {blob_name}")
    else:
        print(f"Failed to upload {local_path}")

if __name__ == '__main__':
    conn = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    if not conn:
        print('AZURE_STORAGE_CONNECTION_STRING not set')
    else:
        # example: python scripts\upload_dataset.py ./ai-training/datasets/visitor-behavior-sample.csv
        import sys
        if len(sys.argv) < 2:
            print('Usage: upload_dataset.py <local_path> [blob_name]')
        else:
            local = sys.argv[1]
            blob = sys.argv[2] if len(sys.argv) > 2 else None
            asyncio.run(upload(conn, local, blob))