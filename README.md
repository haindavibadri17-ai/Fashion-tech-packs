# Tech Pack Agent

Upload a photo of a garment → get a **production-ready tech pack** containing every
section a manufacturer needs:

| # | Section | What the agent fills in |
|---|---------|--------------------------|
| 1 | **Style information** | Brand, style name/code, sample size, size range, date, version |
| 2 | **Technical drawings** | Auto-drawn front flat sketch with measurement callouts + the uploaded reference photo + detail close-ups (neckline, closures, pockets, embellishments) |
| 3 | **Fabric specifications** | Fabric type, fibre composition, GSM, colour, finish, lining, colourfastness, shrinkage, supplier reference, fabric consumption |
| 4 | **Bill of materials** | Outer fabric, lining, thread, zips, buttons, elastic, rib, labels, hangtags, bags — with quantities |
| 5 | **Garment measurements** | Finished-garment (flat) measurements, where to measure, units, and acceptable variation (**tolerance**) |
| 6 | **Size grading** | Full XS→XL/XXL measurement table with per-size steps and grading rules |
| 7 | **Construction details** | Seam & stitch types (301/404/406/504/69), hem finishes, reinforcement/bar-tack points, thread & machine settings |
| 8 | **Colours and artwork** | Colour palette extracted from the photo (hex + name + coverage + suggested Pantone TCX), colourway roles, artwork size/placement/repeat specs |
| 9 | **Labels and packaging** | Label artwork, dimensions, placement, hangtags, poly bags, carton & packing instructions |
| 10 | **Sample feedback and revisions** | Dated feedback/corrections log, revision history, approval sign-off block |

The agent also exports the whole pack as **PDF**, **Markdown** and **JSON**.

## How it works

```
app/
├── main.py                  # FastAPI app: SSE endpoint + static UI + downloads
├── agent/
│   ├── pipeline.py          # Agent orchestrator (streams steps over SSE)
│   ├── image_analyzer.py    # Local image tools: k-means palette, foreground crop,
│   │                        #   structure profile, leg-gap detection, thumbnail
│   ├── classifier.py        # Heuristic garment classifier (transparent confidence)
│   ├── vision.py            # Optional AI-vision enrichment (needs an API key)
│   └── knowledge.py         # Industry knowledge base: 9 garment categories with
│                            #   measurements, grading steps, tolerances, BOMs,
│                            #   construction specs, stitch tables, packaging
└── report/
    ├── flat.py              # Flat-sketch geometry → SVG (web) + reportlab (PDF)
    ├── pdf.py               # A4 tech-pack PDF renderer
    └── markdown.py          # Markdown export
```

**Pipeline steps** (streamed live to the UI):

1. **Ingest** — save the photo, extract the dominant colour palette (k-means),
   crop the garment foreground, compute the silhouette profile.
2. **Classify** — guess the garment type from structure (leg-gap detection,
   flare, sleeve band, aspect ratio). You can override it on the form; the
   agent always reports its confidence and reasoning in the pack.
3. **Vision (optional)** — if `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` is set,
   a vision model adds structured observations (neckline, closure, fabric guess,
   embellishments) as a clearly-labelled reference section. Without a key the
   agent runs 100% local.
4. **Specs** — assemble the 10 sections from the category knowledge base,
   filling in the measured colours, size range, units (cm/in) and style info.
5. **Drawings** — generate the flat technical sketch for the category.
6. **Reports** — render PDF + Markdown.

> All figures are **standard production baselines** (industry-standard base
> sizes, grading steps and tolerances). Every generated pack carries an explicit
> "verify against the approved sample" note — treat the output as a strong
> starting template, not a finished spec.

## Quick start

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open http://localhost:8000 — drop a garment photo, fill in the style details
(all optional; sensible defaults are used), and hit **Generate tech pack**.
Two sample photos are in `jobs/_test/` (T-shirt, jeans) for a quick try.

## API

| Endpoint | Description |
|----------|-------------|
| `POST /api/generate` | multipart: `file` + optional form fields (`brand`, `style_name`, `style_code`, `season`, `garment_type=auto\|tshirt\|top\|shirt\|hoodie\|jacket\|pants\|shorts\|dress\|skirt`, `size_range=XS-XL`, `sample_size`, `units=cm\|in`, `version`, `date`). Streams **SSE**: `step` events (running/done) then a final `done` event with the full pack JSON. |
| `GET /api/jobs/{id}/techpack.pdf` | PDF export |
| `GET /api/jobs/{id}/techpack.md` | Markdown export |
| `GET /api/jobs/{id}/pack.json` | Full structured pack |
| `GET /api/jobs/{id}/photo` | Processed reference photo |
| `GET /api/jobs/{id}/flat.svg` | Flat technical sketch |

Jobs are stored under `jobs/{id}/` (git-ignored).

## Notes & limitations

- Garment auto-classification is a transparent heuristic, not deep-learning
  vision — always confirm the garment type (one click on the form).
- Colours/Pantone references are suggestions from the photo; confirm against a
  physical swatch and lab dip.
- Set `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` (optionally `VISION_MODEL`) on the
  server to enable the optional AI-vision pass.
