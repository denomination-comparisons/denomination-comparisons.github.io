// server.js
// Minimal Express server stub for demo purposes.
// NOT production-ready. Replace JSON file storage with DB for real app.

const express = require('express');
const bodyParser = require('body-parser');
const fs = require('fs');
const path = require('path');
const { v4: uuidv4 } = require('uuid');

const DATA_DIR = path.join(__dirname, 'data');
if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR);

const USERS_FILE = path.join(DATA_DIR, 'users.json');
const PROGRESS_FILE = path.join(DATA_DIR, 'progress.json');
const CONSENTS_FILE = path.join(DATA_DIR, 'consents.json');

function readJSON(filePath) {
  try {
    if (!fs.existsSync(filePath)) return {};
    const raw = fs.readFileSync(filePath, 'utf8');
    return raw ? JSON.parse(raw) : {};
  } catch (e) {
    console.error('readJSON error', e);
    return {};
  }
}
function writeJSON(filePath, obj) {
  fs.writeFileSync(filePath, JSON.stringify(obj, null, 2), 'utf8');
}

// init files if missing
if (!fs.existsSync(USERS_FILE)) writeJSON(USERS_FILE, {});
if (!fs.existsSync(PROGRESS_FILE)) writeJSON(PROGRESS_FILE, {});
if (!fs.existsSync(CONSENTS_FILE)) writeJSON(CONSENTS_FILE, {});

const app = express();
app.use(bodyParser.json());

// CORS helper for local demo usage (adjust in production)
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', req.headers.origin || '*');
  res.header('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  if (req.method === 'OPTIONS') return res.sendStatus(200);
  next();
});

/**
 * POST /api/user
 * Body: { userId? , username?, ageCategory, consentStatus?, ... }
 * - create or update user
 */
app.post('/api/user', (req, res) => {
  const payload = req.body || {};
  const users = readJSON(USERS_FILE);

  let id = payload.userId;
  if (!id) {
    id = uuidv4();
  }

  // minimal normalization
  const existing = users[id] || {};
  const user = {
    ...existing,
    userId: id,
    username: payload.username || existing.username || null,
    ageCategory: payload.ageCategory || existing.ageCategory || null,
    birthYear: payload.birthYear || existing.birthYear || null,
    consentStatus: payload.consentStatus || existing.consentStatus || { parentalConsent: false },
    pathProgress: payload.pathProgress || existing.pathProgress || { currentPath: null, completedStations: [], activeQuests: [], reflectionJournal: [] },
    insights: payload.insights || existing.insights || { total: 0, breakdown: {}, depthScore: 0 },
    preferredLanguage: payload.preferredLanguage || existing.preferredLanguage || 'sv',
    createdAt: existing.createdAt || new Date().toISOString(),
    updatedAt: new Date().toISOString()
  };

  users[id] = user;
  writeJSON(USERS_FILE, users);
  res.json({ ok: true, user });
});

/**
 * GET /api/user/:id
 */
app.get('/api/user/:id', (req, res) => {
  const users = readJSON(USERS_FILE);
  const user = users[req.params.id];
  if (!user) return res.status(404).json({ ok: false, error: 'User not found' });
  res.json({ ok: true, user });
});

/**
 * POST /api/progress/:userId
 * Body: { action: 'append'|'set', progress: {...} }
 * - store per-user progress object for later retrieval
 */
app.post('/api/progress/:userId', (req, res) => {
  const { userId } = req.params;
  const { action = 'append', progress } = req.body || {};
  if (!progress) return res.status(400).json({ ok: false, error: 'Missing progress' });

  const all = readJSON(PROGRESS_FILE);
  const userProgress = all[userId] || { entries: [] };

  if (action === 'append') {
    const entry = { id: uuidv4(), ts: new Date().toISOString(), payload: progress };
    userProgress.entries.push(entry);
  } else if (action === 'set') {
    userProgress.current = progress;
    userProgress.updatedAt = new Date().toISOString();
  } else {
    return res.status(400).json({ ok: false, error: 'Invalid action' });
  }

  all[userId] = userProgress;
  writeJSON(PROGRESS_FILE, all);
  res.json({ ok: true, userProgress: all[userId] });
});

/**
 * GET /api/progress/:userId
 */
app.get('/api/progress/:userId', (req, res) => {
  const all = readJSON(PROGRESS_FILE);
  res.json({ ok: true, progress: all[req.params.userId] || null });
});

/**
 * POST /api/consent/request
 * Body: { userId, guardianEmail, method: 'email'|'sms' }
 * Simulates sending a consent link (mock).
 * Returns consentRequestId that the guardian can "verify".
 */
app.post('/api/consent/request', (req, res) => {
  const { userId, guardianEmail, method = 'email' } = req.body || {};
  if (!userId || !guardianEmail) return res.status(400).json({ ok: false, error: 'userId and guardianEmail required' });

  const consents = readJSON(CONSENTS_FILE);
  const id = uuidv4();
  const record = {
    id,
    userId,
    guardianEmail,
    method,
    status: 'pending',
    createdAt: new Date().toISOString(),
    expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString() // 7 days
  };
  consents[id] = record;
  writeJSON(CONSENTS_FILE, consents);

  // In production: send email/SMS with link containing consentRequestId.
  console.log(`MOCK: consent request created for user ${userId}, guardian ${guardianEmail}, id ${id}`);

  res.json({ ok: true, consentRequestId: id, message: 'Consent request created (mock).' });
});

/**
 * POST /api/consent/verify
 * Body: { consentRequestId, approve: true|false }
 * Simulates guardian approving or rejecting.
 */
app.post('/api/consent/verify', (req, res) => {
  const { consentRequestId, approve } = req.body || {};
  if (!consentRequestId || typeof approve === 'undefined') return res.status(400).json({ ok: false, error: 'Missing parameters' });

  const consents = readJSON(CONSENTS_FILE);
  const rec = consents[consentRequestId];
  if (!rec) return res.status(404).json({ ok: false, error: 'Consent request not found' });

  rec.status = approve ? 'approved' : 'denied';
  rec.verifiedAt = new Date().toISOString();
  consents[consentRequestId] = rec;
  writeJSON(CONSENTS_FILE, consents);

  // If approved, update user consentStatus
  if (approve) {
    const users = readJSON(USERS_FILE);
    const u = users[rec.userId] || null;
    if (u) {
      u.consentStatus = u.consentStatus || {};
      u.consentStatus.parentalConsent = true;
      u.consentStatus.consentDate = new Date().toISOString();
      // set renewal due 1 year from now
      u.consentStatus.renewalDue = new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString();
      users[rec.userId] = u;
      writeJSON(USERS_FILE, users);
      console.log(`MOCK: consent approved and user ${rec.userId} updated`);
    }
  }

  res.json({ ok: true, consent: rec });
});

/**
 * POST /api/bankid/init
 * Minimal BankID stub to show integration pattern.
 * Body: { personalNumber, email, purpose }
 */
app.post('/api/bankid/init', (req, res) => {
  const { personalNumber, email, purpose } = req.body || {};
  if (!personalNumber || !email) return res.status(400).json({ ok: false, error: 'Missing personalNumber or email' });

  const orderRef = uuidv4();
  // In real integration: call BankID API & return orderRef / autoStartToken
  console.log(`MOCK: BankID init for ${personalNumber} (${email}) purpose=${purpose} -> orderRef=${orderRef}`);

  res.json({
    ok: true,
    orderRef,
    autoStartToken: `mock-autostart-${orderRef}`,
    message: 'BankID stub: start authentication in front-end using returned autoStartToken/orderRef'
  });
});

/**
 * Simple health-check
 */
app.get('/', (req, res) => {
  res.send('Wisdom Wayfarer server stub running');
});

const PORT = process.env.PORT || 4000;
app.listen(PORT, () => {
  console.log(`Server stub listening on port ${PORT}`);
});
