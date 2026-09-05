"""Word timings -> ASS subtitle file with 2-3 word pop captions."""
from . import config

HEADER = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {config.WIDTH}
PlayResY: {config.HEIGHT}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{config.FONT},92,&H00FFFFFF,&H0000FFFF,&H00101010,&H80000000,-1,0,0,0,100,100,0,0,1,7,2,5,60,60,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

def _ts(t):
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def write_ass(words, out_path, group=3):
    lines = [HEADER]
    for i in range(0, len(words), group):
        chunk = words[i:i + group]
        text = " ".join(w["w"] for w in chunk).upper()
        lines.append(f"Dialogue: 0,{_ts(chunk[0]['s'])},{_ts(chunk[-1]['e'] + 0.05)},Cap,,0,0,0,,{{\\fad(60,60)}}{text}")
    open(out_path, "w").write("\n".join(lines) + "\n")
