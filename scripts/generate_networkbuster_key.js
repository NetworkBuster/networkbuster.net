#!/usr/bin/env node
const admin = require('../thruster/admin.cjs');
try {
  const k = admin.generateKey('networkbuster-app');
  console.log(JSON.stringify(k, null, 2));
} catch (err) {
  console.error('error', err.message || err);
  process.exit(2);
}
