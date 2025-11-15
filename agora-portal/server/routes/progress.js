import express from "express";
import fs from "fs";
const router = express.Router();

const PROGRESS_FILE = "./server/data/progress.json";

function load() { try { return JSON.parse(fs.readFileSync(PROGRESS_FILE)); } catch { return {}; } }
function save(d) { fs.writeFileSync(PROGRESS_FILE, JSON.stringify(d, null, 2)); }

router.post("/update", (req, res) => {
  const { userId, pathId, completedStations, journalEntry } = req.body;
  if (!userId) return res.status(400).json({ error: "Missing userId" });

  const store = load();
  store[userId] = store[userId] || {};

  if (pathId) store[userId].pathId = pathId;
  if (completedStations) store[userId].completedStations = completedStations;
  if (journalEntry) {
    store[userId].journal = store[userId].journal || [];
    store[userId].journal.push({
      text: journalEntry,
      time: Date.now()
    });
  }

  save(store);
  res.json({ success: true, progress: store[userId] });
});

router.get("/:userId", (req, res) => {
  const store = load();
  res.json(store[req.params.userId] || {});
});

export default router;
