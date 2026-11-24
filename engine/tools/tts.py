"""Narrator voice, made on this computer (no account, no credits).
    python tools/tts.py <slug> [--engine kokoro|say|elevenlabs] [--voice NAME_OR_ID] [--speed 1.0]
    python tools/tts.py --list-voices          ElevenLabs voices on your account (name + id)
Reads videos/<slug>/script.txt (lines starting with # are notes), writes videos/<slug>/audio/raw.wav,
which then goes to tools/voice_run.py like any recorded voiceover.

Engines (config.json "tts_engine", default "kokoro", falls back to "say" if Kokoro is missing):
  kokoro  Kokoro-82M neural TTS (kokoro-onnx), runs offline. Model files live in models/ (setup.py
          downloads them, ~340 MB). Voices: am_puck am_michael am_adam am_echo am_eric am_liam am_fenrir
          af_heart af_bella af_nicole af_sarah bf_emma bm_george ... (config "tts_voice", default am_puck).
  say     macOS built-in voices (`say -v '?'` lists them; config "say_voice", default "Eddy (English (US))").
  elevenlabs  your ElevenLabs account (uses your credits, ~1 per character). The API key is read from
          $ELEVENLABS_API_KEY or the file ~/.config/elevenlabs/key (never put it in config.json or chat).
          Voice: --voice or config "elevenlabs_voice_id"; model: config "elevenlabs_model" (eleven_multilingual_v2).
To use your own recorded voice instead, skip this tool and pass your file to voice_run.py --voice."""
import argparse, os, re, shutil, subprocess, sys, wave

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit  # noqa: E402

c = kit.cfg()
ap = argparse.ArgumentParser()
ap.add_argument("slug", nargs="?")
ap.add_argument("--list-voices", action="store_true")
ap.add_argument("--engine", default=c.get("tts_engine") or "kokoro")
ap.add_argument("--voice", default=None)
ap.add_argument("--speed", type=float, default=float(c.get("tts_speed") or 1.0))
o = ap.parse_args()


def el_key():
    k = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    kp = os.path.expanduser("~/.config/elevenlabs/key")
    if not k and os.path.exists(kp):
        k = open(kp, encoding="utf-8").read().strip()
    if not k:
        sys.exit("No ElevenLabs API key: put it in ~/.config/elevenlabs/key (or $ELEVENLABS_API_KEY).")
    return k


def el_request(path, body=None):
    import json as _j, urllib.request, urllib.error
    req = urllib.request.Request("https://api.elevenlabs.io" + path, headers={"xi-api-key": el_key(),
                                 "Content-Type": "application/json", "Accept": "*/*"},
                                 data=_j.dumps(body).encode() if body is not None else None)
    try:
        return urllib.request.urlopen(req, timeout=300).read()
    except urllib.error.HTTPError as e:
        sys.exit(f"ElevenLabs error {e.code}: {e.read().decode(errors='replace')[:400]}")


if o.list_voices:
    import json as _j
    for v in _j.loads(el_request("/v1/voices"))["voices"]:
        print(f"{v['voice_id']}  {v['name']}  ({v.get('category', '')})")
    sys.exit(0)
if not o.slug:
    sys.exit(__doc__)

vdir = os.path.join(kit.STUDIO, "videos", o.slug)
adir = os.path.join(vdir, "audio")
os.makedirs(adir, exist_ok=True)
lines = [l.strip() for l in open(os.path.join(vdir, "script.txt"), encoding="utf-8")
         if l.strip() and not l.lstrip().startswith("#")]
out = os.path.join(adir, "raw.wav")
SR = 24000


def kokoro_files():
    md = os.path.join(kit.STUDIO, "models")
    return os.path.join(md, "kokoro-v1.0.onnx"), os.path.join(md, "voices-v1.0.bin")


def run_kokoro():
    import numpy as np
    from kokoro_onnx import Kokoro
    model, voices = kokoro_files()
    k = Kokoro(model, voices)
    voice = o.voice or c.get("tts_voice") or "am_puck"
    lang = "en-gb" if voice[:1] == "b" else "en-us"
    parts, gap = [], None
    for i, line in enumerate(lines):
        # one sentence at a time keeps the prosody punchy and avoids the model's length limit
        for sent in [s for s in re.split(r"(?<=[.!?])\s+", line) if s.strip()]:
            samples, sr = k.create(sent, voice=voice, speed=o.speed, lang=lang)
            parts.append(np.asarray(samples, dtype=np.float32))
            gap = np.zeros(int(sr * 0.18), dtype=np.float32)
            parts.append(gap)
        print(f"  line {i + 1}/{len(lines)}", flush=True)
    audio = np.concatenate(parts) if parts else np.zeros(SR, dtype=np.float32)
    peak = float(np.max(np.abs(audio))) or 1.0
    pcm = (audio / peak * 0.95 * 32767).astype("<i2")
    with wave.open(out, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm.tobytes())
    return f"kokoro / {voice}"


def run_say():
    if not shutil.which("say"):
        sys.exit("The 'say' engine needs macOS. Install Kokoro instead (re-run setup.py).")
    voice = o.voice or c.get("say_voice") or "Eddy (English (US))"
    txt, aiff = os.path.join(adir, "tts_text.txt"), os.path.join(adir, "tts_raw.aiff")
    open(txt, "w", encoding="utf-8").write("\n".join(lines))
    rate = str(int(185 * o.speed))
    r = subprocess.run(["say", "-v", voice, "-r", rate, "-o", aiff, "-f", txt], capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"say failed ({r.stderr.strip()}). List voices with: say -v '?'")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", aiff, "-ar", "48000", "-ac", "1", out], check=True)
    os.remove(aiff); os.remove(txt)
    return f"say / {voice}"


def run_elevenlabs():
    voice = o.voice or c.get("elevenlabs_voice_id") or ""
    if not voice:
        sys.exit("Pick a voice: python tools/tts.py --list-voices, then python tools/kit.py set elevenlabs_voice_id <id>")
    model = c.get("elevenlabs_model") or "eleven_multilingual_v2"
    text = "\n".join(lines)
    # Short requests: one long request drifts (gets louder, noisier and smeared toward the end), so send
    # ~500-character chunks, give each its neighbours as previous_text/next_text for continuity,
    # and level every chunk to the same loudness before joining.
    chunks, cur = [], ""
    for l in lines:
        if cur and len(cur) + len(l) > int(c.get("elevenlabs_chunk") or 4500):
            chunks.append(cur); cur = l
        else:
            cur = (cur + "\n" + l).strip()
    chunks.append(cur)
    parts = []
    for k, ch in enumerate(chunks):
        body = {"text": ch, "model_id": model, "voice_settings": {"stability": float(c.get("elevenlabs_stability") or 0.4), "similarity_boost": 0.8,
                                                                     "style": float(c.get("elevenlabs_style") or 0.3), "speed": o.speed}}
        if k > 0: body["previous_text"] = chunks[k - 1][-400:]
        if k + 1 < len(chunks): body["next_text"] = chunks[k + 1][:400]
        mp3 = el_request(f"/v1/text-to-speech/{voice}?output_format=mp3_44100_128", body)
        pp = os.path.join(adir, f"el_part{k}.mp3")
        open(pp, "wb").write(mp3)
        r = subprocess.run(["ffmpeg", "-hide_banner", "-i", pp, "-af", "volumedetect", "-f", "null", "-"],
                           capture_output=True, text=True).stderr
        mean = float(re.search(r"mean_volume: (-?[\d.]+) dB", r).group(1))
        wp = os.path.join(adir, f"el_part{k}.wav")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", pp, "-af", f"volume={-16.0 - mean:.2f}dB,afade=t=in:d=0.02,areverse,afade=t=in:d=0.02,areverse,apad=pad_dur=0.25",
                        "-ar", "48000", "-ac", "1", wp], check=True)
        parts += [pp, wp]
        print(f"  chunk {k + 1}/{len(chunks)}: {len(ch)} chars, level {mean:.1f} dB", flush=True)
    lst = os.path.join(adir, "el_parts.txt")
    open(lst, "w").write("".join(f"file '{p}'\n" for p in parts if p.endswith(".wav")))
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-af", "alimiter=limit=0.95",
                    "-ar", "48000", "-ac", "1", out], check=True)
    for p in parts + [lst]:
        os.remove(p)
    return f"elevenlabs / {voice} / {model} ({len(text)} characters in {len(chunks)} chunks)"


engine = o.engine
if engine == "kokoro":
    try:
        import kokoro_onnx  # noqa: F401
        ok = all(os.path.exists(p) for p in kokoro_files())
    except ImportError:
        ok = False
    if not ok:
        print("Kokoro is not installed (re-run setup.py to add it); using macOS 'say' instead.", file=sys.stderr)
        engine = "say"
used = run_elevenlabs() if engine == "elevenlabs" else run_kokoro() if engine == "kokoro" else run_say()
words = sum(len(l.split()) for l in lines)
print(f"voice: {out} ({used}, {words} words)")
