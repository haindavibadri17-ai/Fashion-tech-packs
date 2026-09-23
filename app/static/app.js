/* Tech Pack Agent — front-end logic */
"use strict";

const $ = (s) => document.querySelector(s);
const drop = $("#drop"), fileInput = $("#file"), preview = $("#preview"),
      dropInner = $("#dropInner"), go = $("#go"), stepsBox = $("#steps"),
      report = $("#report"), empty = $("#empty"), form = $("#form");

let currentFile = null;
let packRef = null;

/* ---------- upload ---------- */
function setFile(f) {
  if (!f || !f.type.startsWith("image/")) return;
  currentFile = f;
  const url = URL.createObjectURL(f);
  preview.src = url;
  preview.hidden = false;
  dropInner.style.display = "none";
  go.disabled = false;
}
drop.addEventListener("click", () => fileInput.click());
drop.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") fileInput.click(); });
fileInput.addEventListener("change", () => setFile(fileInput.files[0]));
["dragenter", "dragover"].forEach((ev) => drop.addEventListener(ev, (e) => {
  e.preventDefault(); drop.classList.add("over");
}));
["dragleave", "drop"].forEach((ev) => drop.addEventListener(ev, (e) => {
  e.preventDefault(); drop.classList.remove("over");
}));
drop.addEventListener("drop", (e) => setFile(e.dataTransfer.files[0]));

/* default date = today */
$("#date").value = new Date().toISOString().slice(0, 10);

/* ---------- agent steps ---------- */
const STEP_LABELS = [
  ["ingest", "Saving photo & analysing image (colour, structure)"],
  ["classify", "Identifying garment type"],
  ["vision", "AI vision pass (optional)"],
  ["specs", "Building specifications — fabric, BOM, measurements, grading, construction"],
  ["drawings", "Generating flat technical sketch"],
  ["reports", "Rendering PDF & Markdown reports"],
];
function initSteps() {
  stepsBox.innerHTML = "<h4>Agent working…</h4>" + STEP_LABELS.map(([id, label]) =>
    `<div class="step" id="step-${id}"><div class="dot"></div><div class="txt">${label}<span class="detail"></span></div></div>`
  ).join("");
  stepsBox.hidden = false;
}
function setStep(id, status, detail) {
  const el = document.getElementById("step-" + id);
  if (!el) return;
  el.className = "step " + (status === "done" ? "done" : "running");
  if (detail) el.querySelector(".detail").textContent = detail;
}

/* ---------- SSE reader ---------- */
async function readSSE(resp) {
  const reader = resp.body.getReader();
  const dec = new TextDecoder();
  let buf = "";
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buf += dec.decode(value, { stream: true });
    let idx;
    while ((idx = buf.indexOf("\n\n")) >= 0) {
      const frame = buf.slice(0, idx);
      buf = buf.slice(idx + 2);
      let ev = "message", data = "";
      for (const line of frame.split("\n")) {
        if (line.startsWith("event: ")) ev = line.slice(7).trim();
        else if (line.startsWith("data: ")) data = line.slice(6);
      }
      if (!data) continue;
      const payload = JSON.parse(data);
      if (ev === "step") setStep(payload.id, payload.status, payload.detail || "");
      else if (ev === "done") { packRef = payload; renderReport(payload); }
      else if (ev === "error") alert("Error: " + payload.error);
    }
  }
}

/* ---------- form submit ---------- */
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  if (!currentFile) return;
  const fd = new FormData();
  fd.append("file", currentFile);
  for (const id of ["brand", "style_name", "style_code", "season", "garment_type",
                    "size_range", "sample_size", "units", "version", "date"]) {
    fd.append(id, $("#" + id).value);
  }
  fd.append("use_ai", "1");

  go.disabled = true;
  go.textContent = "Working…";
  initSteps();
  empty.hidden = true;
  report.hidden = true;
  report.innerHTML = "";
  try {
    const resp = await fetch("/api/generate", { method: "POST", body: fd });
    if (!resp.ok) {
      let msg = "Request failed (" + resp.status + ")";
      try { msg = (await resp.json()).detail || msg; } catch (_) {}
      alert(msg);
    } else {
      await readSSE(resp);
    }
  } catch (err) {
    alert("Network error: " + err.message);
  }
  go.disabled = false;
  go.textContent = "Generate tech pack";
});

/* ---------- rendering helpers ---------- */
const esc = (s) => String(s).replace(/[&<>"]/g,
  (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
function table(headers, rows) {
  const th = headers.map((h) => `<th>${esc(h)}</th>`).join("");
  const trs = rows.map((r) =>
    "<tr>" + r.map((c, i) =>
      `<td${i === 0 ? ' class="k"' : ""}${i > 0 && /^\s*[\d±.]/.test(String(c)) ? ' class="num"' : ""}>${esc(c)}</td>`
    ).join("") + "</tr>").join("");
  return `<table><thead><tr>${th}</tr></thead><tbody>${trs}</tbody></table>`;
}
function kvTable(rows) {
  const trs = rows.map(([k, v]) => `<tr><td class="k">${esc(k)}</td><td>${esc(v)}</td></tr>`).join("");
  return `<table class="kv"><tbody>${trs}</tbody></table>`;
}
function card(no, title, bodyHtml) {
  return `<section class="card"><div class="card-h"><span class="no">${no}</span><h3>${title}</h3></div><div class="card-b">${bodyHtml}</div></section>`;
}

/* ---------- report ---------- */
async function renderReport(payload) {
  const p = payload.pack, files = payload.files, st = p.style;
  let flatSvg = "";
  try {
    const r = await fetch(files.flat);
    flatSvg = await r.text();
  } catch (_) {}

  const chips = [
    ["Garment", st.garment], ["Season", st.season], ["Size range", st.size_range],
    ["Sample size", st.sample_size], ["Units", p.meta.units],
    ["Colourway", st.colourway], ["Version", st.version], ["Date", st.date],
  ].map(([k, v]) => `<span class="chip"><b>${esc(k)}:</b> ${esc(v)}</span>`).join("");

  report.innerHTML = `
    <div class="rp-head">
      <div class="rp-kicker">Tech pack · ${esc(st.style_code)}</div>
      <h1>${esc(st.style_name)}</h1>
      <div class="rp-code">${esc(st.brand)} — generated ${esc(st.date)} by the Tech Pack Agent</div>
      <div class="chips">${chips}</div>
      <div class="dl">
        <a href="${files.pdf}" target="_blank" download>⬇ Download PDF</a>
        <a class="alt" href="${files.md}" target="_blank" download>Markdown</a>
        <a class="alt" href="${files.json}" target="_blank" download>JSON</a>
      </div>
    </div>`;

  // notes
  report.insertAdjacentHTML("beforeend", `
    <div class="ai-note">${st.notes.map(esc).join("<br>")}<br>
    Figures are standard production baselines — verify against the approved sample.</div>`);

  // 01 style
  report.insertAdjacentHTML("beforeend", card("01", "Style information", kvTable([
    ["Brand", st.brand], ["Style name", st.style_name], ["Style code", st.style_code],
    ["Season", st.season], ["Date", st.date], ["Version", st.version],
    ["Sample size", st.sample_size], ["Size range", st.size_range],
    ["Units", p.meta.units], ["Colourway", st.colourway],
  ])));

  // 02 drawings
  const details = p.drawings.details.map((d) => `<li>${esc(d)}</li>`).join("");
  report.insertAdjacentHTML("beforeend", card("02", "Technical drawings", `
    <div class="draws">
      <figure class="draw"><img src="${files.image}" alt="Uploaded garment photo" loading="lazy">
        <figcaption>Reference photo (as uploaded)</figcaption></figure>
      <figure class="draw">${flatSvg || ""}
        <figcaption>${esc(p.drawings.flat_title)}</figcaption></figure>
    </div>
    <p class="note">Detail close-ups:</p><ul>${details}</ul>
    <p class="note">${esc(p.drawings.photo_note)}</p>`));

  // 03 fabric
  report.insertAdjacentHTML("beforeend", card("03", "Fabric specifications",
    kvTable(p.fabric.rows)));

  // 04 BOM
  report.insertAdjacentHTML("beforeend", card("04", "Bill of materials",
    table(["Item", "Material / specification", "Qty per piece"], p.bom.rows)));

  // 05 measurements
  report.insertAdjacentHTML("beforeend", card("05", "Garment measurements", `
    <p class="note">${esc(p.measurements.note)}</p>
    ${table(["Measurement", "Where / how to measure", "Size " + st.sample_size, "Tolerance (±)"], p.measurements.rows)}`));

  // 06 grading
  const g = p.grading;
  report.insertAdjacentHTML("beforeend", card("06", "Size grading", `
    ${table(["Measurement", ...g.sizes, "Step"], g.rows)}
    <p class="note">${esc(g.rules)}</p>`));

  // 07 construction
  const c = p.construction;
  report.insertAdjacentHTML("beforeend", card("07", "Construction details", `
    ${table(["Area", "Stitch / method", "Specification"], c.rows)}
    <div style="height:14px"></div>
    ${table(["Thread / machine setting", "Specification"], c.thread)}
    <div style="height:14px"></div>
    ${table(["Stitch code", "Type", "SPC", "Typical use"], c.stitches)}`));

  // 08 colours
  const col = p.colours;
  const sw = col.swatches.map((s) => `
    <div class="sw"><div class="chipc" style="background:${esc(s.hex)}"></div>
    <div class="nm">${esc(s.name)}</div>
    <div class="hx">${esc(s.hex)} · ${esc(s.coverage)}%</div></div>`).join("");
  report.insertAdjacentHTML("beforeend", card("08", "Colours and artwork", `
    <div class="swatches">${sw}</div>
    ${table(["Role", "Colour", "Hex", "Coverage", "Suggested Pantone TCX (verify on swatch)"], col.colorway_rows)}
    <div style="height:14px"></div>
    ${table(["Artwork", "Size & placement (TBC)", "File spec"], col.artwork)}
    <p class="note">${esc(col.requirements)}</p>`));

  // 09 labels
  report.insertAdjacentHTML("beforeend", card("09", "Labels and packaging",
    table(["Item", "Specification", "Placement / note"], p.labels_packaging.rows)));

  // 10 sample feedback
  const fb = p.sample_feedback;
  report.insertAdjacentHTML("beforeend", card("10", "Sample feedback and revisions", `
    ${table(["#", "Item", "Comment", "Correction", "Date", "Status"], fb.rows)}
    <div style="height:14px"></div>
    ${table(["Version", "Date", "Author", "Notes"], fb.revisions)}
    <div style="height:14px"></div>
    ${table(["Role", "Name", "Date", "Signature"], fb.approvals)}`));

  // AI observations (if any)
  if (p.ai && p.ai.observations) {
    const rows = Object.entries(p.ai.observations).map(([k, v]) => [k, Array.isArray(v) ? v.join(", ") : v]);
    report.insertAdjacentHTML("beforeend", card("AI", "AI observations (reference only)",
      table(["Observation", "Value"], rows) +
      `<p class="note">Automatic vision-model output (provider: ${esc(p.ai.provider || "n/a")}) — always verify against the physical sample.</p>`));
  }

  empty.hidden = true;
  report.hidden = false;
  window.scrollTo({ top: 0, behavior: "smooth" });
}
