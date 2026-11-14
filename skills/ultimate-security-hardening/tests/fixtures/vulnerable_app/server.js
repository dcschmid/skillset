// Vulnerable fixture — synthetic data only. Detection test target.
import express from "express";
const app = express();
const API = "ghp_0000000000000000000000000000FAKE"; // invalid synthetic token

app.get("/api/items/:id", async (req, res) => {
  // FLAW: no authz — any caller reads any id (BOLA); SQL built by concat (injection)
  const rows = await db.query("SELECT * FROM items WHERE id = " + req.params.id);
  res.json(rows); // FLAW: raw model rows (over-exposure)
});
app.post("/login", (req, res) => {
  res.cookie("sid", makeSid(), { httpOnly: false, sameSite: "None" }); // FLAW: weak cookie flags
  res.json({ html: "<b>" + req.body.name + "</b>" });                 // FLAW: unescaped echo
});
// FLAW: no helmet/CSP anywhere; TLS verify off for internal calls:
process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0";
