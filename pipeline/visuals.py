"""Replicate FLUX-schnell image generation. Every image is generated from our own prompt -> we own the output."""
import time, requests, csv, datetime as dt
from . import config

def generate(prompt, out_png):
    h = {"Authorization": f"Bearer {config.REPLICATE_API_TOKEN}", "Content-Type": "application/json"}
    body = {"input": {"prompt": config.STYLE_PREFIX + prompt, "aspect_ratio": "9:16",
                      "output_format": "png", "num_outputs": 1, "go_fast": True}}
    r = requests.post(f"https://api.replicate.com/v1/models/{config.IMAGE_MODEL}/predictions",
                      headers={**h, "Prefer": "wait=60"}, json=body, timeout=120)
    r.raise_for_status()
    pred = r.json()
    while pred["status"] not in ("succeeded", "failed", "canceled"):
        time.sleep(3)
        pred = requests.get(pred["urls"]["get"], headers=h, timeout=60).json()
    if pred["status"] != "succeeded":
        raise RuntimeError(f"image generation failed: {pred.get('error')}")
    url = pred["output"][0] if isinstance(pred["output"], list) else pred["output"]
    open(out_png, "wb").write(requests.get(url, timeout=120).content)
    return url

def log_license(video_id, script_id, asset, source, license_, ref):
    with open(config.ASSETS / "license_log.csv", "a", newline="") as f:
        csv.writer(f).writerow([video_id, script_id, asset, source, license_, ref,
                                dt.datetime.utcnow().isoformat(timespec="seconds")])
