"""Finish a video: mix audio (voice + sfx cues + music), burn word captions, mux the mp4.
python tools/finish.py <slug> [--no-captions] [--music path] [--music-speed 1.5] [--music-mode speed|tempo]
reads  videos/<slug>/frames/####.png, audio/voice.wav, audio/words.json, audio/cues.json
music  --music path, else the first audio/video file in studio/music/ (the house bed, used on every video).
       It is sped up (default 1.5x, "speed" = sped-up trend style, pitch goes up; "tempo" keeps pitch)
       and written to audio/music.wav, then mixed under the voice (ducked).
writes videos/<slug>/audio/mix.m4a, captions.ass, out/final.mp4 and out/final_phone.mp4
(out/final_nocaptions.mp4 only with --no-captions)"""
import argparse, glob, json, os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
STUDIO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import kit  # noqa: E402
CFG = kit.cfg()
ap = argparse.ArgumentParser()
ap.add_argument("slug"); ap.add_argument("--no-captions", action="store_true"); ap.add_argument("--music", default="")
ap.add_argument("--music-db", default="-8"); ap.add_argument("--sfx-db", default="-12")
ap.add_argument("--music-speed", type=float, default=float(CFG["music_speed"]))
ap.add_argument("--music-mode", default=CFG["music_mode"])  # tempo = same pitch (house choice), speed = pitched up
ap.add_argument("--no-music", action="store_true")
o = ap.parse_args()
vdir = os.path.join(STUDIO, "videos", o.slug)
adir = os.path.join(vdir, "audio"); odir = os.path.join(vdir, "out"); os.makedirs(odir, exist_ok=True)


def duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


src = o.music
if not src and not o.no_music:
    mdir = os.path.join(STUDIO, "music")
    cands = sorted(f for f in glob.glob(os.path.join(mdir, "*"))
                   if os.path.splitext(f)[1].lower() in (".mp3", ".wav", ".m4a", ".mp4", ".aac", ".ogg", ".flac", ".webm"))
    src = cands[0] if cands else ""
for f in glob.glob(os.path.join(adir, "music.*")):
    os.remove(f)
if src and not o.no_music:
    if duration(src) < 2.0:
        print(f"warning: music file looks broken ({src}), mixing without music")
    else:
        sp = o.music_speed
        af = (f"asetrate=44100*{sp},aresample=44100" if o.music_mode == "speed" else f"atempo={sp}")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vn", "-ac", "2", "-ar", "44100", "-af",
                        "aresample=44100," + af, os.path.join(adir, "music.wav")], check=True)
        print(f"music: {os.path.basename(src)} x{sp} ({o.music_mode}) -> audio/music.wav")
else:
    print("music: none (put the bed in studio/music/ or pass --music)")

# 1. audio mix
subprocess.run([sys.executable, os.path.join(HERE, "mix.py"), "--video", o.slug, "--music-db", o.music_db,
                "--sfx-db", o.sfx_db], check=True)

# 2. captions (script words, one at a time; same look as the reference)
words = json.load(open(os.path.join(adir, "words.json"), encoding="utf-8"))
LAG = 1.3 / 30


def ts(t):
    cs = int(round(max(t, 0) * 100))
    return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"


head = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Word,{FONT},150,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,1,0,1,9,3,5,20,20,20,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
lines, caps = [], []
for i, w in enumerate(words):
    txt = re.sub(r"[^\w'$%,.]", "", w["word"]).strip(",.").upper()
    if not txt:
        continue
    s = 0.0 if i == 0 else w["start"] + LAG
    e = (words[i + 1]["start"] + LAG) if i + 1 < len(words) else w["end"] + 0.4
    lines.append(f"Dialogue: 0,{ts(s)},{ts(e)},Word,,0,0,0,,{{\\pos(540,1607)}}{txt}")
    caps.append((s, e, txt))
head = head.replace("{FONT}", kit.caption_font(CFG))
open(os.path.join(vdir, "captions.ass"), "w", encoding="utf-8").write(head + "\n".join(lines) + "\n")

# 3. mux
os.chdir(vdir)
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                            os.path.join("audio", "mix.m4a")], capture_output=True, text=True).stdout)
base = ["ffmpeg", "-v", "error", "-y", "-framerate", "30", "-i", os.path.join("frames", "%04d.png"),
        "-i", os.path.join("audio", "mix.m4a")]
enc = ["-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p", "-c:a", "copy", "-t", f"{dur:.3f}",
       "-movflags", "+faststart"]
if o.no_captions:      # the no-captions file is only made when asked for (the user posts the captioned one)
    subprocess.run(base + enc + [os.path.join("out", "final_nocaptions.mp4")], check=True)


def has_ass():
    r = subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True)
    return any(l.split()[1:2] == ["ass"] for l in r.stdout.splitlines() if len(l.split()) > 1)


def burn_with_pillow():
    """ffmpeg without libass (e.g. Homebrew's): draw the same captions onto copies of the frames."""
    from PIL import Image, ImageDraw
    fnt = kit.font(kit.caption_font(CFG).replace(" ", "") + ".ttf", 132)
    if kit.font_path(kit.caption_font(CFG).replace(" ", "") + ".ttf") is None:
        fnt = kit.font("ariblk.ttf", 132)
    tmp = "frames_cap"
    shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
    frames = sorted(glob.glob(os.path.join("frames", "*.png")))
    cache = {}
    for k, fp in enumerate(frames):
        t = k / 30.0
        word = next((c[2] for c in caps if c[0] <= t < c[1]), None)
        im = Image.open(fp).convert("RGB")
        if word:
            if word not in cache:
                f = fnt
                lay = Image.new("RGBA", (1080, 400), (0, 0, 0, 0))
                d = ImageDraw.Draw(lay)
                size = 132
                while d.textbbox((0, 0), word, font=f, stroke_width=10)[2] > 1020 and size > 50:
                    size -= 8; f = kit.font("ariblk.ttf", size)
                d.text((546, 206), word, font=f, fill=(0, 0, 0, 120), anchor="mm", stroke_width=10, stroke_fill=(0, 0, 0, 120))
                d.text((540, 200), word, font=f, fill="white", anchor="mm", stroke_width=10, stroke_fill="black")
                cache[word] = lay
            im.paste(cache[word], (0, 1607 - 200), cache[word])
        im.save(os.path.join(tmp, os.path.basename(fp)), compress_level=1)
    cmd = ["ffmpeg", "-v", "error", "-y", "-framerate", "30", "-i", os.path.join(tmp, "%04d.png"),
           "-i", os.path.join("audio", "mix.m4a")] + enc + [os.path.join("out", "final.mp4")]
    subprocess.run(cmd, check=True)
    shutil.rmtree(tmp, ignore_errors=True)


if not o.no_captions:
    if has_ass():
        subprocess.run(base + ["-vf", "ass=captions.ass"] + enc + [os.path.join("out", "final.mp4")], check=True)
    else:
        print("captions: this ffmpeg has no libass, drawing them with Pillow")
        burn_with_pillow()
# 4. phone copy (under ~25 MB so it can be sent to a phone)
src_v = os.path.join("out", "final.mp4" if not o.no_captions else "final_nocaptions.mp4")
vbr = max(800, int(25 * 8 * 1024 / dur) - 160)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src_v, "-vf", "scale=720:1280", "-c:v", "libx264", "-preset", "slow",
                "-b:v", f"{vbr}k", "-maxrate", f"{int(vbr * 1.2)}k", "-bufsize", f"{vbr * 2}k", "-c:a", "aac", "-b:a", "128k",
                "-movflags", "+faststart", os.path.join("out", "final_phone.mp4")], check=True)
print("done:", os.path.join(vdir, "out", "final.mp4"), f"{dur:.2f}s")
