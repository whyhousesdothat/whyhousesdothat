import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
WORK = ROOT / "work"
LOGS = ROOT / "logs"
ASSETS = ROOT / "assets"

CHANNEL_NAME = "Why Houses Do That"
HANDLE = "@whyhousesdothat"

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = "claude-sonnet-4-6"

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
# Default voice: "Daniel" (ElevenLabs premade, licensed for commercial use on paid plans)
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID") or "onwK4e9ZLuTAKqWW03F9"
ELEVENLABS_MODEL = "eleven_turbo_v2_5"

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN", "")
IMAGE_MODEL = "black-forest-labs/flux-schnell"

YT_CLIENT_ID = os.getenv("YT_CLIENT_ID", "")
YT_CLIENT_SECRET = os.getenv("YT_CLIENT_SECRET", "")
YT_REFRESH_TOKEN = os.getenv("YT_REFRESH_TOKEN", "")
# "private" until the Google API compliance audit clears, then set repo variable to "public"
PUBLISH_PRIVACY = os.getenv("PUBLISH_PRIVACY") or "private"

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
ALERT_EMAIL = os.getenv("ALERT_EMAIL", "")

AMAZON_TAG = os.getenv("AMAZON_TAG", "").strip()

DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"

MIN_QUEUE = 20          # refill scripts when fewer than this are queued
WIDTH, HEIGHT = 1080, 1920
FONT = "DejaVu Sans"

STYLE_PREFIX = (
    "Clean technical cutaway illustration, isometric cross-section of a residential house detail, "
    "muted blueprint palette with one warm orange accent, soft studio lighting, high detail, "
    "no text, no people, no logos, vertical 9:16 composition. "
)
