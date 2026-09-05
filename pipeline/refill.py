"""Keep the calendar topped up so the schedule never runs dry."""
import random
from . import config
from .state import load_calendar, save_calendar, log
from .script_gen import generate
from .optimize import best_hooks

def refill(state, n=10):
    cal = load_calendar()
    queued = [s for s in cal["scripts"] if s.get("status") == "queued"]
    if len(queued) >= config.MIN_QUEUE:
        return 0
    used = {s["topic"].lower() for s in cal["scripts"]}
    bank = [t.strip() for t in (config.CONTENT / "topics.txt").read_text().splitlines() if t.strip()]
    fresh = [t for t in bank if t.lower() not in used]
    random.shuffle(fresh)
    topics = fresh[:n]
    if not topics:
        log("refill: topic bank exhausted; add lines to content/topics.txt")
        return 0
    new = generate(topics, hook_bias=best_hooks(state) or None)
    for s in new:
        s["status"] = "queued"
        s["id"] = s["id"] + "-" + str(random.randint(100, 999))
    cal["scripts"].extend(new)
    save_calendar(cal)
    log(f"refill: added {len(new)} scripts")
    return len(new)
