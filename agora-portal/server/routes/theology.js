import express from "express";
import fs from "fs";
import path from "path";

const router = express.Router();
const BASE = "./core/theology";

router.get("/:id", (req, res) => {
  const file = path.join(BASE, req.params.id + ".json");
  if (!fs.existsSync(file)) return res.status(404).json({ error: "Not found" });

  res.type("application/json").send(fs.readFileSync(file));
});

router.get("/", (req, res) => {
  const files = fs.readdirSync(BASE).filter(f => f.endsWith(".json"));
  res.json(files.map(f => f.replace(".json", "")));
});

export default router;
