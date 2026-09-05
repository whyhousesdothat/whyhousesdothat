import json, datetime as dt
from .config import CONTENT, LOGS

STATE = CONTENT / "state.json"
CAL = CONTENT / "calendar.json"

def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {"published": [], "hook_weights": {}, "slot_weights": {}, "ab_next": "A", "last_weekly": None}

def save_state(s):
    STATE.write_text(json.dumps(s, indent=2))

def load_calendar():
    return json.loads(CAL.read_text())

def save_calendar(c):
    CAL.write_text(json.dumps(c, indent=2))

def log(msg):
    LOGS.mkdir(exist_ok=True)
    line = f"{dt.datetime.utcnow().isoformat(timespec='seconds')}Z {msg}"
    print(line, flush=True)
    with open(LOGS / f"{dt.date.today():%Y-%m}.log", "a") as f:
        f.write(line + "\n")
