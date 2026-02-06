const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const DATA_DIR = path.resolve(__dirname, '..', 'data', 'admin');
const REQ_FILE = path.join(DATA_DIR, 'requests.json');
const SCRIPTS_DIR = path.join(DATA_DIR, 'scripts');

if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, { recursive: true });
if (!fs.existsSync(SCRIPTS_DIR)) fs.mkdirSync(SCRIPTS_DIR, { recursive: true });
if (!fs.existsSync(REQ_FILE)) fs.writeFileSync(REQ_FILE, JSON.stringify([]));

function _readRequests() {
  return JSON.parse(fs.readFileSync(REQ_FILE, 'utf8'));
}
function _writeRequests(reqs) {
  fs.writeFileSync(REQ_FILE, JSON.stringify(reqs, null, 2));
}

function _makeId() { return crypto.randomBytes(6).toString('hex'); }

/**
 * Request server admin access.
 * input: { githubUser, publicKey, reason, contact }
 * returns request object
 */
function requestAccess(input) {
  if (!input || !input.githubUser || !input.publicKey) throw new Error('githubUser_and_publicKey_required');
  const reqs = _readRequests();
  const id = _makeId();
  const now = Date.now();
  const r = { id, githubUser: input.githubUser, publicKey: input.publicKey, reason: input.reason || '', contact: input.contact || '', status: 'pending', createdAt: now };
  reqs.push(r);
  _writeRequests(reqs);
  return r;
}

/**
 * Approve a request. This generates a shell script to be run by a human operator (never executed automatically).
 * Returns { ok, scriptPath }
 */
function approveRequest(id, approver) {
  const reqs = _readRequests();
  const r = reqs.find(x => x.id === id);
  if (!r) return { ok: false, error: 'not_found' };
  if (r.status !== 'pending') return { ok: false, error: 'already_processed' };

  const scriptName = `add_admin_${id}.sh`;
  const scriptPath = path.join(SCRIPTS_DIR, scriptName);

  // Build a safe script (POSIX shell) that creates a user, installs the key, and adds to sudoers.d.
  const username = r.githubUser.replace(/[^a-zA-Z0-9_-]/g, '').toLowerCase().slice(0, 32) || `crew${id}`;
  // encode public key as base64 to avoid shell quoting issues
  const pubkeyB64 = Buffer.from(r.publicKey, 'utf8').toString('base64');
  const addSudo = `\n# Add restricted sudoers entry (edit per policy)\necho "${username} ALL=(ALL) NOPASSWD: /usr/bin/systemctl, /bin/journalctl" > /etc/sudoers.d/${username}\nchmod 440 /etc/sudoers.d/${username}\n`;

  const script = `#!/usr/bin/env sh
# Generated add-admin script for request ${id}
# REVIEW BEFORE RUNNING AS ROOT
set -euo pipefail

USERNAME=${username}
PUBKEY_B64='${pubkeyB64}'

# create user if not exists
if ! id "$USERNAME" >/dev/null 2>&1; then
  useradd -m -s /bin/bash "$USERNAME"
fi
mkdir -p /home/$USERNAME/.ssh
# decode base64 pubkey to authorized_keys
echo "$PUBKEY_B64" | base64 -d > /home/$USERNAME/.ssh/authorized_keys
chmod 600 /home/$USERNAME/.ssh/authorized_keys
chown -R $USERNAME:$USERNAME /home/$USERNAME/.ssh

# add user to wheel or admin group if exists
if getent group sudo >/dev/null 2>&1; then
  usermod -aG sudo "$USERNAME" || true
fi
if getent group wheel >/dev/null 2>&1; then
  usermod -aG wheel "$USERNAME" || true
fi

# Additional: create limited sudoers entry
${addSudo}

echo "User $USERNAME created and ssh key installed. Please verify sudoers entry at /etc/sudoers.d/$USERNAME."
`;

  fs.writeFileSync(scriptPath, script, { mode: 0o750 });

  // mark request as approved
  r.status = 'approved';
  r.approvedBy = approver || 'unknown';
  r.approvedAt = Date.now();
  r.scriptPath = scriptPath;
  _writeRequests(reqs);

  return { ok: true, scriptPath };
}

function listRequests() {
  return _readRequests();
}

module.exports = { requestAccess, approveRequest, listRequests, DATA_DIR };
