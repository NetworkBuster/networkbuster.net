import { ServiceBusClient } from '@azure/service-bus';
import fs from 'fs';
import { promises as fsPromises } from 'fs';
import path from 'path';
import crypto from 'crypto';

const queueBase = path.join(process.cwd(), 'data', 'queue');
const TOPIC_NAME = 'device-registrations.v1';

let sbClient = null;
let useAzure = false;

function initAzureServiceBus() {
  const connectionString = process.env.AZURE_SERVICEBUS_CONNECTION_STRING;
  if (connectionString) {
    sbClient = new ServiceBusClient(connectionString);
    useAzure = true;
    console.log('Using Azure Service Bus for queue operations');
  } else {
    console.log('No Azure Service Bus connection string; falling back to file-based queue');
  }
}

initAzureServiceBus();

async function ensureDir() {
  try {
    await fsPromises.access(queueBase);
  } catch {
    await fsPromises.mkdir(queueBase, { recursive: true });
  }
}

export async function enqueue(topic, payload) {
  if (useAzure && topic === TOPIC_NAME) {
    const sender = sbClient.createSender(topic);
    try {
      const message = {
        body: payload,
        messageId: crypto.randomUUID(),
        contentType: 'application/json'
      };
      await sender.sendMessages(message);
      await sender.close();
      return { id: message.messageId, topic, payload };
    } catch (err) {
      console.error('Failed to enqueue to Azure Service Bus:', err);
      throw err;
    }
  } else {
    // Fallback to file-based
    await ensureDir();
    const dir = path.join(queueBase, topic);
    try {
      await fsPromises.access(dir);
    } catch {
      await fsPromises.mkdir(dir, { recursive: true });
    }
    const id = Date.now().toString() + '-' + crypto.randomBytes(4).toString('hex');
    const msg = {
      id,
      topic,
      timestamp: new Date().toISOString(),
      payload
    };
    const fn = path.join(dir, `${id}.json`);
    await fsPromises.writeFile(fn, JSON.stringify(msg, null, 2), 'utf8');
    return msg;
  }
}

export async function dequeue(topic) {
  if (useAzure && topic === TOPIC_NAME) {
    const receiver = sbClient.createReceiver(topic);
    try {
      const messages = await receiver.receiveMessages(1, { maxWaitTimeInMs: 5000 });
      if (messages.length > 0) {
        const msg = messages[0];
        const payload = {
          id: msg.messageId,
          topic,
          timestamp: msg.enqueuedTimeUtc?.toISOString() || new Date().toISOString(),
          payload: msg.body
        };
        await receiver.completeMessage(msg);
        await receiver.close();
        return payload;
      }
      await receiver.close();
      return null;
    } catch (err) {
      console.error('Failed to dequeue from Azure Service Bus:', err);
      await receiver?.close();
      throw err;
    }
  } else {
    // Fallback to file-based
    const dir = path.join(queueBase, topic);
    try {
      await fsPromises.access(dir);
    } catch {
      return null;
    }
    const files = (await fsPromises.readdir(dir)).filter(f => f.endsWith('.json')).sort();
    if (files.length === 0) return null;
    const fn = path.join(dir, files[0]);
    const data = await fsPromises.readFile(fn, 'utf8');
    const msg = JSON.parse(data);
    // Move to processed
    const processedDir = path.join(queueBase, `${topic}-processed`);
    try {
      await fsPromises.access(processedDir);
    } catch {
      await fsPromises.mkdir(processedDir, { recursive: true });
    }
    await fsPromises.rename(fn, path.join(processedDir, files[0]));
    return msg;
  }
}

export async function list(topic) {
  if (useAzure) {
    // For Azure, we can't easily list; return empty for compatibility
    console.warn('list() not supported with Azure Service Bus; use Azure portal or CLI');
    return [];
  }
  const dir = path.join(queueBase, topic);
  try {
    await fsPromises.access(dir);
  } catch {
    return [];
  }
  const files = (await fsPromises.readdir(dir)).filter(f => f.endsWith('.json'));
  
  // Read all files in parallel for better performance
  const results = await Promise.all(
    files.map(async (f) => {
      try {
        const data = await fsPromises.readFile(path.join(dir, f), 'utf8');
        return JSON.parse(data);
      } catch (err) {
        console.error(`Error reading ${f}:`, err.message);
        return null;
      }
    })
  );
  
  return results.filter(r => r !== null);
}
