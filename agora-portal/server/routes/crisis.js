import express from "express";
import fs from "fs";

const router = express.Router();
const CRISIS_LOG = "./server/data/crisis-log.json";

function load() {
  try { return JSON.parse(fs.readFileSync(CRISIS_LOG)); }
  catch { return []; }
}
function save(d) { fs.writeFileSync(CRISIS_LOG, JSON.stringify(d, null, 2)); }

router.post("/log", (req, res) => {
  const { userId, text, detectedType, severity } = req.body;
  const log = load();

  log.push({
    userId,
    text,
    detectedType,
    severity,
    time: Date.now()
  });
  save(log);

  res.json({ success: true });
});

export default router;
