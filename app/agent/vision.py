"""Optional AI-vision enrichment.

If OPENAI_API_KEY or ANTHROPIC_API_KEY is set in the environment, the agent
asks a vision model for structured observations (garment type, neckline,
closure, fabric guess, embellishments) and merges them into the pack as
clearly-labelled "AI observations". Without a key the agent runs fully local.
"""
import base64
import json
import mimetypes
import os
import urllib.error
import urllib.request

PROMPT = (
    "You are a senior garment technical designer. Analyse this clothing photo and reply with ONLY "
    "a JSON object with these keys: garment_type (one of: tshirt, top, shirt, hoodie, jacket, pants, "
    "shorts, dress, skirt), gender (mens/womens/unisex), neckline, sleeve_length, closure, "
    "pockets (array), fabric_guess (type + estimated GSM), wash_or_finish (e.g. garment-dyed, washed denim), "
    "embellishments (array), other_details (array of short strings), confidence (0-1). Be concise."
)


def _post(url, headers, payload, timeout=90):
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", **headers}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def _b64_image(image_path):
    mime = mimetypes.guess_type(image_path)[0] or "image/jpeg"
    with open(image_path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    return f"data:{mime};base64,{data}"


def _openai(image_path):
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        return None
    payload = {
        "model": os.environ.get("VISION_MODEL", "gpt-4o"),
        "max_tokens": 700,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "user", "content": [
                {"type": "text", "text": PROMPT},
                {"type": "image_url", "image_url": {"url": _b64_image(image_path)}},
            ]},
        ],
    }
    resp = _post("https://api.openai.com/v1/chat/completions",
                 {"Authorization": f"Bearer {key}"}, payload)
    text = resp["choices"][0]["message"]["content"]
    return _clean(text)


def _anthropic(image_path):
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return None
    models = [os.environ.get("VISION_MODEL", ""), "claude-sonnet-4-5", "claude-3-5-sonnet-20241022"]
    last_err = None
    for model in [m for m in models if m]:
        payload = {
            "model": model, "max_tokens": 700,
            "messages": [{"role": "user", "content": [
                {"type": "text", "text": PROMPT},
                {"type": "image", "source": {"type": "base64",
                 "media_type": "image/jpeg", "data": _b64_image(image_path).split(",", 1)[1]}},
            ]}],
        }
        try:
            resp = _post("https://api.anthropic.com/v1/messages",
                         {"x-api-key": key, "anthropic-version": "2023-06-01"}, payload)
            return _clean(resp["content"][0]["text"])
        except (urllib.error.HTTPError, KeyError, ValueError) as e:
            last_err = e
    raise RuntimeError(f"vision model unavailable: {last_err}")


def _clean(text):
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text)


def vision_observe(image_path, provider="auto"):
    """Return (observations dict | None, provider used | error string)."""
    try:
        if provider in ("auto", "openai") and os.environ.get("OPENAI_API_KEY"):
            return _openai(image_path), "openai"
        if provider in ("auto", "anthropic") and os.environ.get("ANTHROPIC_API_KEY"):
            return _anthropic(image_path), "anthropic"
        return None, "no API key configured — local analysis only"
    except Exception as e:  # never break the pipeline on vision errors
        return None, f"vision call failed ({e}); local analysis only"
