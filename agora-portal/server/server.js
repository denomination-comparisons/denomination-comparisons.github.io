import express from "express";
import cors from "cors";
import fs from "fs";
import path from "path";

import consentRoutes from "./routes/consent.js";
import progressRoutes from "./routes/progress.js";
import crisisRoutes from "./routes/crisis.js";
import theologyRoutes from "./routes/theology.js";

const app = express();
app.use(express.json());

app.use(cors({
  origin: [
    "https://denomination-comparisons.github.io",
    "http://localhost:3000"
  ],
  methods: "GET,POST,PUT"
}));

app.use("/api/consent", consentRoutes);
app.use("/api/progress", progressRoutes);
app.use("/api/crisis", crisisRoutes);
app.use("/api/theology", theologyRoutes);

app.get("/", (req, res) => {
  res.json({ status: "Agora Server OK", time: Date.now() });
});

const PORT = process.env.PORT || 8080;
app.listen(PORT, () => console.log("Server running on port", PORT));
