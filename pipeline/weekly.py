"""Monday: pull analytics, reweight hooks/slots, refill queue biased to winners, send one-paragraph summary."""
import datetime as dt
from .state import load_state, save_state, log
from . import youtube, notify
from .optimize import update_weights, best_hooks
from .refill import refill

def main():
    state = load_state()
    a = youtube.analytics(days=7)
    ch = youtube.channel_stats()
    before = dict(state.get("hook_weights") or {})
    state = update_weights(state, a)
    added = 0
    try:
        added = refill(state, n=12)
    except Exception as e:
        log(f"weekly refill failed: {e}")
    state["last_weekly"] = str(dt.date.today())
    save_state(state)
    hooks = best_hooks(state)
    slots = state.get("slot_weights") or {}
    best_slot = max(slots, key=slots.get) if slots else "n/a"
    rev = "not yet monetized" if a["revenue"] is None else f"${a['revenue']:.2f}"
    changed = []
    if hooks and hooks != [k for k, _ in sorted(before.items(), key=lambda kv: -kv[1])[:2]]:
        changed.append(f"now favoring {', '.join(hooks)} hooks")
    if added:
        changed.append(f"queued {added} new scripts")
    if not changed:
        changed.append("no changes; not enough data yet")
    para = (f"Week ending {dt.date.today():%b %d}: {int(a['views']):,} views, {int(a['subs_gained']):+} subscribers "
            f"({ch.get('subscriberCount')} total), {a['avg_view_pct']:.0f}% average retention, revenue {rev}. "
            f"Best posting slot so far: {best_slot}. Changes: {'; '.join(changed)}.")
    notify.send("[WHDT] Weekly summary", para)
    log("weekly: " + para)

if __name__ == "__main__":
    main()
