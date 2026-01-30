import os
import asyncio
from pathlib import Path
import importlib.util
import logging

# Setup simple logging to file (ensure UTF-8 to avoid encoding errors)
import sys
import io
logs = Path(__file__).resolve().parents[1] / "logs"
logs.mkdir(exist_ok=True)
file_handler = logging.FileHandler(logs / 'orchestrator.log', encoding='utf-8')
stream = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
stream_handler = logging.StreamHandler(stream)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[file_handler, stream_handler]
)
logger = logging.getLogger('orchestrator_runner')

# Load the pipeline module
spec = importlib.util.spec_from_file_location(
    "ai_training_pipeline",
    Path(__file__).resolve().parents[1] / "ai-training-pipeline.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

async def main():
    conn = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    if not conn:
        logger.error('AZURE_STORAGE_CONNECTION_STRING not set; exiting')
        return

    orchestrator = module.TrainingOrchestrator(conn)
    try:
        await orchestrator.run_continuous_pipeline()
    except Exception as e:
        logger.exception('Orchestrator stopped due to error')

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Orchestrator stopped by user')
