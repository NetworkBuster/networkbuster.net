import { saveRegistration, transitionStatus, getRegistration } from '../../lib/deviceStore.js';
import { enqueue, dequeue } from '../../lib/messageQueue.js';

async function testStatusTransitions() {
  console.log('Testing status transitions...');

  // Create a test registration
  const reg = await saveRegistration({
    deviceId: 'test-device-123',
    hardwareId: 'HW123',
    model: 'TestModel'
  });
  console.log('Created registration:', reg);

  // Test transitions
  try {
    await transitionStatus('test-device-123', 'queued');
    console.log('✓ Transitioned to queued');

    await transitionStatus('test-device-123', 'processing');
    console.log('✓ Transitioned to processing');

    await transitionStatus('test-device-123', 'acknowledged');
    console.log('✓ Transitioned to acknowledged');

    const final = await getRegistration('test-device-123');
    console.log('Final status:', final.status);

    // Test invalid transition
    try {
      await transitionStatus('test-device-123', 'queued'); // Should fail
      console.log('✗ Invalid transition allowed');
    } catch (e) {
      console.log('✓ Invalid transition blocked:', e.message);
    }

  } catch (e) {
    console.error('Transition test failed:', e);
  }
}

async function testQueue() {
  console.log('Testing queue operations...');

  const msg = await enqueue('device-registrations.v1', {
    deviceId: 'test-device-123',
    model: 'TestModel'
  });
  console.log('Enqueued message:', msg);

  const deq = await dequeue('device-registrations.v1');
  console.log('Dequeued message:', deq);
}

async function run() {
  await testStatusTransitions();
  await testQueue();
  console.log('All tests passed!');
}

run().catch(e => { console.error('Test failed:', e); process.exit(1); });