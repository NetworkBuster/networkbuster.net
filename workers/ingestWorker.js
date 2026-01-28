import { dequeue } from '../lib/messageQueue.js';
import { transitionStatus } from '../lib/deviceStore.js';

const TOPIC = 'device-registrations.v1';

async function processNext() {
  const msg = await dequeue(TOPIC);
  if (!msg) return false;
  console.log(`Processing message ${msg.id} for device ${msg.payload.deviceId}`);

  // Simulate processing (e.g., call model ingestion endpoint)
  try {
    // Simulated processing delay
    await new Promise(r => setTimeout(r, 500));

    // Update status to processed/acknowledged
    transitionStatus(msg.payload.deviceId, 'acknowledged', { processedAt: new Date().toISOString(), processedBy: 'ingestWorker' });
    console.log(`Message ${msg.id} processed for ${msg.payload.deviceId}`);
    return true;
  } catch (err) {
    console.error('Processing failed for', msg.id, err);
    transitionStatus(msg.payload.deviceId, 'failed', { error: String(err), failedAt: new Date().toISOString() });
    return false;
  }
}

async function runLoop() {
  console.log('Ingest worker started. Polling for messages...');
  // simple polling loop
  setInterval(async () => {
    try {
      const handled = await processNext();
      if (!handled) {
        // nothing to do
      }
    } catch (e) {
      console.error('Worker error:', e);
    }
  }, 1000);
}

if (import.meta.url === `file://${process.cwd()}/workers/ingestWorker.js`) {
  runLoop();
}

export { processNext, runLoop };
