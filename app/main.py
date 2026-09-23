"""Tech Pack Agent — FastAPI application.

Run:  .venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
"""
import io
import os
import re
import secrets

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image

from .agent.pipeline import run_generation

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOBS = os.path.join(BASE, "jobs")
os.makedirs(JOBS, exist_ok=True)

app = FastAPI(title="Tech Pack Agent")

JOB_RE = re.compile(r"^[a-z0-9]{8,24}$")


def job_dir(job_id: str) -> str:
    if not JOB_RE.match(job_id or ""):
        raise HTTPException(404, "Job not found")
    d = os.path.join(JOBS, job_id)
    if not os.path.isdir(d):
        raise HTTPException(404, "Job not found")
    return d


app.mount("/static", StaticFiles(directory=os.path.join(BASE, "app", "static")), name="static")


@app.get("/")
def index():
    return FileResponse(os.path.join(BASE, "app", "static", "index.html"))


@app.post("/api/generate")
async def generate(
    file: UploadFile = File(...),
    brand: str = Form(""),
    style_name: str = Form(""),
    style_code: str = Form(""),
    season: str = Form(""),
    garment_type: str = Form("auto"),
    size_range: str = Form("XS-XL"),
    sample_size: str = Form("M"),
    units: str = Form("cm"),
    version: str = Form("1.0"),
    date: str = Form(""),
    use_ai: str = Form("1"),
):
    data = await file.read()
    if not data:
        raise HTTPException(400, "Empty file")
    try:
        img = Image.open(io.BytesIO(data))
        img.verify()
    except Exception:
        raise HTTPException(400, "Upload must be a valid image file (JPG/PNG/WebP)")

    job_id = secrets.token_hex(4)
    form = {
        "filename": file.filename or "photo.jpg",
        "brand": brand, "style_name": style_name, "style_code": style_code,
        "season": season, "garment_type": garment_type, "size_range": size_range,
        "sample_size": sample_size, "units": units, "version": version,
        "date": date, "use_ai": use_ai,
    }

    def stream():
        try:
            for chunk in run_generation(form, data, job_id, JOBS):
                yield chunk
        except Exception as e:  # surface pipeline errors as an SSE event
            import json
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        stream(), media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@app.get("/api/jobs/{job_id}/pack.json")
def get_pack(job_id: str):
    d = job_dir(job_id)
    return FileResponse(os.path.join(d, "pack.json"), media_type="application/json")


@app.get("/api/jobs/{job_id}/techpack.pdf")
def get_pdf(job_id: str):
    d = job_dir(job_id)
    return FileResponse(os.path.join(d, "techpack.pdf"), media_type="application/pdf",
                        filename="techpack.pdf")


@app.get("/api/jobs/{job_id}/techpack.md")
def get_md(job_id: str):
    d = job_dir(job_id)
    return FileResponse(os.path.join(d, "techpack.md"), media_type="text/markdown",
                        filename="techpack.md")


@app.get("/api/jobs/{job_id}/photo")
def get_photo(job_id: str):
    d = job_dir(job_id)
    p = os.path.join(d, "photo_thumb.jpg")
    if not os.path.exists(p):
        p = os.path.join(d, "photo.jpg")
    return FileResponse(p, media_type="image/jpeg")


@app.get("/api/jobs/{job_id}/flat.svg")
def get_flat(job_id: str):
    d = job_dir(job_id)
    return FileResponse(os.path.join(d, "flat.svg"), media_type="image/svg+xml")
