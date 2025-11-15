import express from "express";
import fs from "fs";
const router = express.Router();

const USERS_FILE = "./server/data/users.json";

function loadUsers() {
  try { return JSON.parse(fs.readFileSync(USERS_FILE)); }
  catch { return {}; }
}
function saveUsers(u) {
  fs.writeFileSync(USERS_FILE, JSON.stringify(u, null, 2));
}

router.post("/grant", (req, res) => {
  const { userId, guardianEmail } = req.body;
  if (!userId) return res.status(400).json({ error: "Missing userId" });

  const users = loadUsers();
  users[userId] = users[userId] || {};

  users[userId].consentStatus = {
    parentalConsent: true,
    guardianEmail,
    consentDate: Date.now(),
    renewalDue: Date.now() + 365 * 24 * 3600 * 1000
  };

  saveUsers(users);
  res.json({ success: true, consent: users[userId].consentStatus });
});

router.post("/revoke", (req, res) => {
  const { userId } = req.body;
  if (!userId) return res.status(400).json({ error: "Missing userId" });

  const users = loadUsers();
  if (!users[userId]) return res.status(404).json({ error: "Unknown user" });

  users[userId].consentStatus = { parentalConsent: false };
  saveUsers(users);

  res.json({ success: true });
});

export default router;

