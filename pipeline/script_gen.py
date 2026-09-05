"""Claude writes new scripts in the channel format. Used by refill (auto) and by anyone wanting more."""
import json, anthropic
from . import config

SYSTEM = """You write 40-55 second YouTube Shorts scripts for the channel "Why Houses Do That".
Voice: a calm, blunt residential contractor who has seen it a thousand times. First person plural is fine ("we see this on every third job").
Format each script as JSON with keys:
 id (slug), topic, hook_style (one of: question, confession, inspector_reveal, myth_bust, countdown),
 hook (<=12 words, spoken first), body (90-120 words: what is happening physically, why, when it matters),
 fix (25-40 words: the specific fix, what to buy if anything, when to call a pro),
 scenes (list of 4 short image prompts describing a cutaway/diagram of the house detail, no text in image),
 title_a, title_b (two different title angles, <=60 chars, no clickbait lies),
 tags (8-12), affiliate_search (an Amazon search phrase for one relevant product, or null),
 safety_note (null, or a one-line caution for anything involving gas, electrical, structural, or mold).
Rules: physically accurate, no medical claims, never tell viewers to open electrical panels or touch gas lines,
state uncertainty when a symptom has several causes. Every script must contain one specific detail a generic
AI channel would not know (a number, a tool name, a tell-tale sign). Spoken text only in hook/body/fix. Return ONLY a JSON array."""

def generate(topics, hook_bias=None):
    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    bias = f"\nPrefer these hook styles (they perform best): {hook_bias}" if hook_bias else ""
    msg = client.messages.create(model=config.CLAUDE_MODEL, max_tokens=8000, system=SYSTEM,
        messages=[{"role": "user", "content": f"Write one script for each topic:\n" + "\n".join(f"- {t}" for t in topics) + bias}])
    text = msg.content[0].text.strip()
    text = text[text.find("["): text.rfind("]") + 1]
    return json.loads(text)

def description(script):
    lines = [script["hook"], "", script["fix"], ""]
    if config.AMAZON_TAG and script.get("affiliate_search"):
        q = script["affiliate_search"].replace(" ", "+")
        lines += [f"Tool mentioned: https://www.amazon.com/s?k={q}&tag={config.AMAZON_TAG}",
                  "(As an Amazon Associate we earn from qualifying purchases.)", ""]
    if script.get("safety_note"):
        lines += ["Safety: " + script["safety_note"], ""]
    lines += ["Original script, narration and illustrations by Why Houses Do That.", "#Shorts #homerepair #whyhousesdothat"]
    return "\n".join(lines)
