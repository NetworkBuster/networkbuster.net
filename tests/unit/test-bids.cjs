const assert = require('assert');
const admin = require('../../thruster/admin.cjs');

(function(){
  const before = admin.listBids().length;
  const b = admin.addBid({ name: 'Test', email: 't@example.com', body: 'We bid $1' });
  assert(b && b.id, 'bid created');
  const after = admin.listBids().length;
  assert(after === before + 1, 'bid persisted');
  console.log('test-bids: OK');
})();