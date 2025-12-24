import { dequeue } from '../lib/messageQueue.js';
import fetch from 'node-fetch';

const TOPIC = 'device-registrations.v1';
const INGESTION_ENDPOINT = process.env.INGESTION_ENDPOINT || 'http://localhost:3001/api/ingestion/mock';

import { dequeue } from '../lib/messageQueue.js';
import { transitionStatus } from '../lib/deviceStore.js';
import fetch from 'node-fetch';

const TOPIC = 'device-registrations.v1';
const INGESTION_ENDPOINT = process.env.INGESTION_ENDPOINT || 'http://localhost:3001/api/ingestion/mock';
const MAX_RETRIES = 3;

async function processMessage(msg, retryCount = 0) {
  const deviceId = msg.payload.deviceId;
  console.log(`Processing message ${msg.id} for device ${deviceId} (attempt ${retryCount + 1})`);

  try {
    // Mark as processing
    transitionStatus(deviceId, 'processing', { processingStartedAt: new Date().toISOString() });

    // Forward to ingestion endpoint
    const res = await fetch(INGESTION_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(msg.payload)
    });

    const result = await res.json();

    if (res.ok && result.status === 'acknowledged') {
      // Success
      transitionStatus(deviceId, 'acknowledged', {
        acknowledgedAt: new Date().toISOString(),
        ingestionResult: result,
        processingAttempts: retryCount + 1
      });
      console.log(`✓ Message ${msg.id} acknowledged for ${deviceId}`);
      return { success: true, result };
    } else {
      // Ingestion failed
      throw new Error(`Ingestion failed: ${res.status} - ${result.error || 'Unknown error'}`);
    }
  } catch (err) {
    console.error(`✗ Processing failed for ${deviceId}:`, err.message);
    
    if (retryCount < MAX_RETRIES - 1) {
      // Retry after delay
      const delay = Math.pow(2, retryCount) * 1000; // Exponential backoff
      console.log(`Retrying ${deviceId} in ${delay}ms...`);
      await new Promise(r => setTimeout(r, delay));
      return processMessage(msg, retryCount + 1);
    } else {
      // Max retries exceeded
      transitionStatus(deviceId, 'failed', {
        failedAt: new Date().toISOString(),
        error: err.message,
        processingAttempts: retryCount + 1
      });
      console.error(`✗ Max retries exceeded for ${deviceId}`);
      return { success: false, error: err.message };
    }
  }
}

async function runConsumer() {
  console.log('Device registration consumer started. Polling for messages...');
  console.log(`Ingestion endpoint: ${INGESTION_ENDPOINT}`);

  setInterval(async () => {
    try {
      const msg = await dequeue(TOPIC);
      if (msg) {
        await processMessage(msg);
      }
    } catch (e) {
      console.error('Consumer error:', e);
    }
  }, 2000); // Poll every 2 seconds
}

if (import.meta.url === `file://${process.cwd()}/workers/deviceConsumer.js`) {
  runConsumer();
}

export { processMessage, runConsumer };