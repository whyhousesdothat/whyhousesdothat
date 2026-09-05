"""ElevenLabs TTS with character timestamps -> mp3 + word timings for captions."""
import base64, json, requests
from . import config

def synthesize(text, out_mp3):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{config.ELEVENLABS_VOICE_ID}/with-timestamps"
    r = requests.post(url, headers={"xi-api-key": config.ELEVENLABS_API_KEY},
        json={"text": text, "model_id": config.ELEVENLABS_MODEL,
              "voice_settings": {"stability": 0.45, "similarity_boost": 0.8, "style": 0.35}},
        timeout=180)
    r.raise_for_status()
    data = r.json()
    open(out_mp3, "wb").write(base64.b64decode(data["audio_base64"]))
    al = data["alignment"]
    return _words(al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"])

def _words(chars, starts, ends):
    words, cur, s0 = [], "", None
    for c, s, e in zip(chars, starts, ends):
        if c.isspace():
            if cur:
                words.append({"w": cur, "s": s0, "e": prev_e})
                cur, s0 = "", None
            continue
        if s0 is None:
            s0 = s
        cur += c
        prev_e = e
    if cur:
        words.append({"w": cur, "s": s0, "e": prev_e})
    return words
