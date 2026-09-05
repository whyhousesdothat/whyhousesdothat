"""ffmpeg: N images with slow zoom, crossfades, voiceover, burned captions, title card overlay -> 1080x1920 mp4."""
import subprocess, shlex
from . import config

def _run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

def audio_duration(path):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                   "-of", "default=nw=1:nk=1", path])
    return float(out.strip())

def build(images, mp3, ass_path, hook_text, out_mp4):
    dur = audio_duration(mp3) + 0.6
    n = len(images)
    per = dur / n
    fps = 30
    inputs, filters = [], []
    for i, img in enumerate(images):
        inputs += ["-loop", "1", "-t", f"{per + 0.5:.2f}", "-i", img]
        # gentle Ken Burns: zoom 1.0 -> 1.12 over the clip
        filters.append(
            f"[{i}:v]scale=1296:2304,zoompan=z='min(zoom+0.0009,1.12)':d={int(per*fps)+15}:s={config.WIDTH}x{config.HEIGHT}:fps={fps},"
            f"setsar=1,format=yuv420p[v{i}]")
    # chain crossfades
    prev = "v0"
    for i in range(1, n):
        off = per * i - 0.4 * i
        filters.append(f"[{prev}][v{i}]xfade=transition=fade:duration=0.4:offset={off:.2f}[x{i}]")
        prev = f"x{i}"
    hook = hook_text.replace("'", "\u2019").replace(":", "\\:")
    filters.append(
        f"[{prev}]drawbox=x=0:y=0:w=iw:h=ih:color=black@0.0:t=fill,"
        f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='{hook}':fontsize=64:fontcolor=white:"
        f"box=1:boxcolor=black@0.55:boxborderw=24:x=(w-text_w)/2:y=200:enable='lt(t,2.8)',"
        f"ass={ass_path},trim=0:{dur:.2f}[vout]")
    cmd = ["ffmpeg", "-y", *inputs, "-i", mp3,
           "-filter_complex", ";".join(filters),
           "-map", "[vout]", "-map", f"{n}:a",
           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-r", str(fps),
           "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out_mp4]
    _run(cmd)
    return out_mp4

def thumbnail(mp4, out_jpg, at=1.0):
    _run(["ffmpeg", "-y", "-ss", str(at), "-i", mp4, "-frames:v", "1", "-q:v", "2", out_jpg])
    return out_jpg
