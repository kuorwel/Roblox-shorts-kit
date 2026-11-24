# Roblox Shorts Kit

Make original Roblox-style 3D story shorts (9:16, 60-120 s) from one sentence, all on your own
computer. You tell Claude Code "make a roblox story about hiccups making you shrink". It writes the
story, a local neural voice (Kokoro) reads it, and Blender builds and animates every shot: blocky
characters, sets and fast camera moves. Then the kit adds sound effects, music and captions, makes
the cover, and gives you an mp4.

You don't need subscriptions, accounts or credits. ElevenLabs is an optional voice upgrade.

```
one sentence -> script.txt -> Kokoro voice -> word timings (faster-whisper)
             -> shots.py (Blender, timed by script word) -> preview + fix -> final render
             -> mix + captions + music -> out/final.mp4 + cover.jpg
```

The repo is a [Claude Code skill](https://docs.claude.com/en/docs/claude-code/skills): `SKILL.md`
tells Claude how to run the whole pipeline. You can also run each tool by hand. The
[tutorials](tutorials/) folder does it step by step.

## What you need

| | Mac | Windows |
|---|---|---|
| Claude Code | desktop app (Code tab) or the `claude` CLI | same |
| Blender 5.2 or newer | `brew install --cask blender` or blender.org | `winget install --id BlenderFoundation.Blender -e` |
| ffmpeg | `brew install ffmpeg` | `winget install --id Gyan.FFmpeg -e` |
| Python 3.10 to 3.13 | python.org or `brew install python@3.12` | python.org (tick "Add python to PATH") |
| git | `xcode-select --install` | `winget install --id Git.Git -e` |

You also need a decent graphics card. A 70 s video renders in about an hour on a gaming laptop
GPU, and much slower on CPU alone. While a video renders it takes about 5 GB of disk.
`tools/clean.py` deletes the frames afterwards.

## Install

Clone the repo into your Claude Code skills folder. The folder must be named `roblox-story-kit`.

**Mac**

```bash
git clone https://github.com/kuorwel/Roblox-shorts-kit.git ~/.claude/skills/roblox-story-kit
```

```bash
python3 ~/.claude/skills/roblox-story-kit/setup.py
```

**Windows (PowerShell)**

```powershell
git clone https://github.com/kuorwel/Roblox-shorts-kit.git "$HOME\.claude\skills\roblox-story-kit"
python "$HOME\.claude\skills\roblox-story-kit\setup.py"
```

Instead of running setup yourself, you can open Claude Code and say **"set up the roblox kit"**.

### What setup does

`setup.py [workspace] [--update] [--no-pip] [--no-music] [--no-test]` is safe to re-run. It:

1. copies the engine (`engine/rbx`, `engine/tools`, `engine/assets`, `engine/sfx`, `PLAYBOOK.md`)
   and the two example videos into a **workspace**, `~/RobloxStories` by default. Your videos are
   made there, never in the skill folder;
2. creates a private Python env at `~/RobloxStories/.venv` with numpy, Pillow, faster-whisper,
   yt-dlp and kokoro-onnx;
3. finds ffmpeg and Blender and writes `config.json`;
4. downloads the music bed into `music/` (see [What is not in this repo](#what-is-not-in-this-repo));
5. downloads the Kokoro voice model (~340 MB) into `models/`;
6. renders one test frame and prints `READY`. If something is missing, it prints the exact
   command that fixes it.

Setup also writes `~/.roblox-story-kit.json`, which tells Claude where the workspace and its
Python are.

To update after a `git pull`, run `setup.py --update`. It refreshes the engine and keeps your
videos, characters, music and settings.

## Quickstart: render the example video

`sneeze_teleport` ships with its script, its 66 shots and its word timings. This makes the full
71 s video. Run everything from the workspace with the kit's Python.

**Mac**

```bash
cd ~/RobloxStories && PY=.venv/bin/python
```

**Windows (PowerShell)**

```powershell
cd $HOME\RobloxStories; $PY = ".venv\Scripts\python.exe"
```

Then run these (on Windows, put `&` in front: `& $PY tools\tts.py sneeze_teleport`):

```bash
$PY tools/tts.py sneeze_teleport                       # Kokoro voice -> audio/raw.wav
$PY tools/voice_run.py --video sneeze_teleport --voice videos/sneeze_teleport/audio/raw.wav --speed 1.15
$PY tools/tighten.py sneeze_teleport --max-gap 0.45    # trim breaths
$PY tools/retempo.py sneeze_teleport --wpm 258         # hit the target pace
$PY tools/blend.py sneeze_teleport preview all         # fast low-res pass
$PY tools/contact.py sneeze_teleport all 12 full       # contact sheet -> videos/sneeze_teleport/full.jpg
$PY tools/blend.py sneeze_teleport cues                # sound cue list
$PY tools/blend.py sneeze_teleport final               # the long one: run it and walk away
$PY tools/finish.py sneeze_teleport                    # mix, captions, mp4
$PY tools/cover.py sneeze_teleport "I SNEEZED"         # cover image
```

The first `voice_run.py` downloads the whisper model (~1.5 GB). The result lands in
`videos/sneeze_teleport/out/`:

- `final.mp4`: 1080x1920, the upload file
- `final_phone.mp4`: a 720p copy, ~25 MB
- `cover.jpg`: the cover

Without any sound files in `sfx/`, the video finishes with no sound effects. See
[Sound effects](#sound-effects).

## Use it as a Claude Code skill

Once it's installed, talk to Claude Code from any folder:

- **"make me a roblox story"** or **"make a roblox story about \<idea\>"**: Claude writes the
  story, renders three designs for the lead character and stops once to ask "A, B or C?". After
  you answer, the next thing you get is the finished video.
- **"make me a roblox story, autopilot"**: no stop. Claude picks the character too.
- **"give me 10 roblox story ideas"**
- **"render the example video"**: the quickstart above, done for you.
- **"set up the roblox kit"** or **"update the roblox kit"**

Describe as much of the story or character as you like and Claude follows it. Anything you leave
out, it decides. Characters you design are saved in `~/RobloxStories/characters/` and reused.

## Settings (`~/RobloxStories/config.json`)

You can edit the file, or use `$PY tools/kit.py set <key> <value>`:

- `tts_engine`: `kokoro` (default), `say` (macOS voices) or `elevenlabs`
- `tts_voice`: the Kokoro voice. The default is `am_puck`; try `am_michael`, `am_adam` or `af_heart`.
- `music_mode`: `tempo` keeps the music's pitch (default); `speed` pitches it up
- `blender`: the path to Blender, if setup couldn't find it
- `whisper_model`: the faster-whisper model for word timings (default `medium.en`)

To use your own voiceover, skip `tts.py` and pass your file to `voice_run.py --voice`.

**ElevenLabs (optional).** Set `tts_engine` to `elevenlabs` and put your key in
`~/.config/elevenlabs/key` (or in `$ELEVENLABS_API_KEY`). The key is never stored in the
workspace or in this repo. Run `$PY tools/tts.py --list-voices` to see your voices, then
`$PY tools/kit.py set elevenlabs_voice_id <id>` to pick one.

## Repo layout

```
SKILL.md            the skill: the whole pipeline, for Claude (and a good read for humans)
setup.py            one-time setup / update (copies engine/ into the workspace)
VERSION
engine/
  PLAYBOOK.md       numbers to hit, beat sheet, hook checklist, shot grammar, captions, sound
  rbx/              Blender library: primitives + camera (core), R6 characters (chars),
                    faces + gestures (acting), cast + story helpers (story), sets (world, world2,
                    sets, locs), fire FX (fx)
  tools/            the pipeline: tts, voice_run, tighten, retempo, blend, contact, finish, mix,
                    cover, texture, design, clean, analyze_inspo, kit (config) ...
  assets/faces/     layered eye/mouth textures (made by tools/make_faces*.py)
  assets/tex/       sign/poster/board textures (made by tools/make_textures*.py, tools/texture.py)
  sfx/pack.json     sound-effect levels and lead times (sounds not included)
  videos/           two worked examples: laugh_float (73 shots, 88 s), sneeze_teleport (66 shots, 71 s)
tutorials/          outline for a tutorial series about the kit
```

## Sound effects

The shots call sounds by name (`sfx(t, "poof")`). `engine/sfx/pack.json` lists the names with
their levels, but the repo doesn't include the sounds. Put your own 48 kHz `.wav` files in
`~/RobloxStories/sfx/<name>.wav`. To trim and level a raw sound, run
`$PY tools/sfxprep.py raw.mp3 sfx/poof.wav`. You can also synthesize one with numpy. If a cue has
no sound, it's skipped with a warning.

## What is not in this repo

| Thing | Why | Where it comes from |
|---|---|---|
| Music bed (TEMPOREX, "Numbers") | the artist owns it, under its own license | `setup.py` downloads it into `music/`. Check the artist's terms before you monetize, or drop any audio file you have rights to into `music/` |
| Kokoro voice model | large (~340 MB); Apache-2.0, from [kokoro-onnx](https://github.com/thewh1teagle/kokoro-onnx) | `setup.py` downloads it into `models/` |
| Whisper model | large (~1.5 GB) | faster-whisper downloads it on the first `voice_run.py` |
| Sound-effect `.wav` files | unclear redistribution rights | bring your own (see above) |
| Example voice recordings, rendered frames, videos | large, and made per machine | `tts.py` + `blend.py` + `finish.py` |
| Keys (ElevenLabs, YouTube) | secrets | `~/.config/...` on your machine only |

## Rules for stories

Stories must be original: your own characters, sets and plots. Don't use real Roblox UI, logos,
avatars or game sounds, and don't copy other creators' plots. "Roblox-style" means the blocky look.
This project isn't affiliated with or endorsed by Roblox Corporation.

## License

See [LICENSE](LICENSE). Third-party tools and models keep their own licenses: Blender (GPL),
ffmpeg (LGPL/GPL), Kokoro (Apache-2.0), kokoro-onnx (MIT), faster-whisper (MIT), and the music
track (its artist's terms).
