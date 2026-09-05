"""One scheduled run = one Short: pick script -> voice -> images -> captions -> assemble -> upload -> log."""
import json, shutil, traceback, datetime as dt
from . import config
from .state import load_state, save_state, load_calendar, save_calendar, log
from . import voice, visuals, captions, assemble, youtube, notify
from .script_gen import description
from .optimize import pick_next
from .refill import refill

def main():
    state = load_state()
    try:
        refill(state)
    except Exception as e:
        log(f"refill failed (non-fatal): {e}")
    cal = load_calendar()
    queue = [s for s in cal["scripts"] if s.get("status") == "queued"]
    script = pick_next(queue, state)
    if not script:
        notify.send("[WHDT] Queue empty", "No queued scripts. Add topics to content/topics.txt.")
        return
    sid = script["id"]
    work = config.WORK; shutil.rmtree(work, ignore_errors=True); work.mkdir()
    log(f"start {sid}")
    try:
        text = " ".join([script["hook"], script["body"], script["fix"]])
        words = voice.synthesize(text, work / "vo.mp3")
        images = []
        for i, prompt in enumerate(script["scenes"][:4]):
            p = work / f"scene{i}.png"
            url = visuals.generate(prompt, p)
            images.append(str(p))
            visuals.log_license("pending", sid, f"scene{i}.png", "replicate/" + config.IMAGE_MODEL,
                                "generated from own prompt (FLUX-schnell, Apache-2.0 model)", prompt)
        visuals.log_license("pending", sid, "vo.mp3", "elevenlabs/" + config.ELEVENLABS_VOICE_ID,
                            "ElevenLabs paid plan commercial license", "script text")
        captions.write_ass(words, work / "caps.ass")
        variant = state.get("ab_next", "A")
        title = script["title_a"] if variant == "A" else script["title_b"]
        title = f"{title} #Shorts" if len(title) < 90 else title
        mp4 = assemble.build(images, str(work / "vo.mp3"), str(work / "caps.ass"), script["hook"], str(work / f"{sid}.mp4"))
        thumb = assemble.thumbnail(mp4, str(work / "thumb.jpg"))
        if config.DRY_RUN:
            log(f"dry run: built {mp4} with title '{title}'")
            return
        vid = youtube.upload(mp4, title, description(script), script["tags"] + ["shorts", "home repair", "why houses do that"], config.PUBLISH_PRIVACY)
        youtube.set_thumbnail(vid, thumb)
        hour = dt.datetime.utcnow().hour
        slot = "morning" if hour < 17 else "evening"
        state["published"].append({"video_id": vid, "script_id": sid, "hook_style": script["hook_style"],
                                   "title_variant": variant, "title": title, "slot": slot,
                                   "published_at": dt.datetime.utcnow().isoformat(timespec="seconds") + "Z"})
        state["ab_next"] = "B" if variant == "A" else "A"
        script["status"] = "published"; script["video_id"] = vid
        save_calendar(cal); save_state(state)
        # backfill video id in license log
        lic = config.ASSETS / "license_log.csv"
        lic.write_text(lic.read_text().replace(f"pending,{sid},", f"{vid},{sid},"))
        log(f"published {vid} '{title}' privacy={config.PUBLISH_PRIVACY}")
    except Exception:
        tb = traceback.format_exc()
        log(f"FAILED {sid}\n{tb}")
        notify.send(f"[WHDT] Pipeline failed on {sid}", tb)
        raise

if __name__ == "__main__":
    main()
