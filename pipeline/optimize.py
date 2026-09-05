"""Turn analytics into weights the picker and the refill use."""
from collections import defaultdict

def update_weights(state, analytics):
    by_id = {v["id"]: v for v in analytics["videos"]}
    hook_views, slot_views = defaultdict(list), defaultdict(list)
    for p in state["published"]:
        a = by_id.get(p["video_id"])
        if not a:
            continue
        p["views"] = a["views"]; p["avg_view_pct"] = a["avg_view_pct"]
        hook_views[p["hook_style"]].append(a["views"])
        slot_views[p["slot"]].append(a["views"])
        ab = p.get("title_variant")
        if ab:
            state.setdefault("ab", {}).setdefault(ab, []).append(a["views"])
    def norm(d):
        avg = {k: sum(v) / len(v) for k, v in d.items() if v}
        if not avg:
            return {}
        top = max(avg.values()) or 1
        return {k: round(max(0.2, v / top), 3) for k, v in avg.items()}
    if hook_views:
        state["hook_weights"] = norm(hook_views)
    if slot_views:
        state["slot_weights"] = norm(slot_views)
    return state

def best_hooks(state, n=2):
    hw = state.get("hook_weights") or {}
    return [k for k, _ in sorted(hw.items(), key=lambda kv: -kv[1])[:n]]

def pick_next(queue, state):
    """Prefer higher-weight hook styles, otherwise FIFO. Keep some exploration."""
    if not queue:
        return None
    hw = state.get("hook_weights") or {}
    if not hw or len(state["published"]) % 4 == 0:   # every 4th video explores
        return queue[0]
    return max(queue, key=lambda s: (hw.get(s["hook_style"], 0.6), -queue.index(s)))
