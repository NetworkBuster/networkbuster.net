const assert = require('assert');
const admin = require('../../thruster/admin.cjs');
const fs = require('fs');

// cleanup any preexisting requests for test isolation
const all = admin.listRequests();
for (const r of all) {
  if (r.githubUser && r.githubUser.startsWith('test-')) {
    // leave old tests, ignore
  }
}

(async () => {
  const r = admin.requestAccess({ githubUser: 'test-crew', publicKey: 'ssh-rsa AAAAB3NzaTestKey', reason: 'unit test', contact: 'test@example.com' });
  assert(r && r.id, 'request created');
  const before = admin.listRequests().length;
  const res = admin.approveRequest(r.id, 'tester');
  assert(res.ok && res.scriptPath, 'approve produced script');
  assert(fs.existsSync(res.scriptPath), 'script file exists');
  const after = admin.listRequests().length;
  assert(after === before, 'request list length stable');
  console.log('test-admin-requests: OK');
})();