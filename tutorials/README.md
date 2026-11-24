# Tutorial series: making Roblox-style story shorts with the kit

An outline for a video or written series. Each episode ends with something you can see on
screen, and episodes 2 to 6 follow one new story from idea to upload. Commands assume
`PY=.venv/bin/python` on Mac (`$PY = ".venv\Scripts\python.exe"` on Windows) and are run from
`~/RobloxStories`.

---

## 0. Trailer (1 min)
- Show a finished short, then the same video as a contact sheet of shots.
- The promise: one sentence in, an mp4 out, everything on your own computer.
- Who it's for: you're fine with a terminal, but you don't need to know Blender.

## 1. Setup and your first render (10-15 min)
- Install Blender 5.2+, ffmpeg, Python 3.12, git and Claude Code, on Mac and on Windows.
- `git clone` into `~/.claude/skills/roblox-story-kit`, then run `setup.py` and read its output.
  Each line is `ok`, `note` or `MISSING` plus a fix.
- Tour of the workspace: `tools/`, `rbx/`, `videos/`, `characters/`, `music/`, `config.json`,
  `.venv`.
- Render the example: `tts.py sneeze_teleport`, the voice steps, `blend.py ... preview all`,
  `contact.py`.
- Payoff on screen: the preview contact sheet, `full.jpg`.

## 2. Writing a script that holds attention (10 min)
- The shell: an everyday thing plus one impossible rule ("In this world, X makes you Y").
- Walk through the beat sheet in `PLAYBOOK.md`: result-first hook, "You see, in this world...",
  society examples, the "But" pivot, the escalation ladder, "Then I noticed something", the
  payoff, a 2-6 word button.
- The numbers: 300-400 words, 65-75 words in the first 15 s, onomatopoeia on every hit.
- Write `videos/<slug>/script.txt` live, with `#` note lines. Check it with `script_text.py`.
- Option: the same thing done by Claude ("make a roblox story about...") and how to steer it.

## 3. Voice: Kokoro, ElevenLabs or your own (8-10 min)
- `tts.py <slug>`: change voices with `--voice am_michael`, or try `--engine say`.
- Voice processing: `voice_run.py` (speed-up, silence cuts, whisper word timings), then
  `tighten.py` and `retempo.py`.
- Read `audio/words.json`: the target is 255-280 wpm with no gap over ~0.45 s.
- Optional ElevenLabs: where the key goes (`~/.config/elevenlabs/key`, never in the project),
  `--list-voices`, and setting the voice id.
- Fix mispronounced names by respelling them in the script.

## 4. Characters and textures (10 min)
- The `Char` json: hair, face, sleeves, stripes, bolt, extras.
- `design.py <slug> A.json B.json C.json` makes the three-option picture. Then
  `design.py --one characters/<key>.json` and `from_sheet("<key>", ...)` in shots.
- Built-in cast for side characters and crowds: `kid(i)`, `townie`, `crowd`.
- `texture.py <name> "HEADLINE|line" --style chalk`: signs, boards and screens. Put one on a prop
  with `card(...)` and `img_mat(...)`.

## 5. Making shots (20 min, the core episode)
- `shots.py` anatomy: `Video(__file__)`, `story.bind(V)`, and `@S(id, w0, w1, "note")` timing by
  script word index, so a new voice take never breaks the edit.
- Shot grammar: cut on the word that brings a new image, 50-60 cuts per minute, a reaction
  close-up after every surprise, wide/close/insert.
- Cameras: `cam.push`, `orbit`, `crash`, `whip`, `track`, `handheld`. Every shot moves.
- Acting: `face(t, "shock")`, `act(t, "cheer")`, `look`, `jump`, `talk`.
- Sets: `W.town`, `W.classroom_day`, `W2.cabin`, and so on. Sound: `sfx(t, "poof")`.
- Build five shots live, starting from a copy of the `sneeze_teleport` style.

## 6. Preview and fix (10-15 min)
- `blend.py <slug> preview all`, then `contact.py <slug> all 12 full`: how to read the sheet.
- One frame: `blend.py <slug> still:12.3 14`. To re-preview a few shots: `preview 3,7,12`.
- The traps list from `SKILL.md`, shown as before/after:
  - a blank single-colour tile means the camera is inside a prop or house
  - visibility keys on the same frame
  - prop scale
  - props parented to the head, not the root
  - framing math: width = 2 x distance x 6.75 / lens
- Fix, re-preview, repeat until every tile reads.

## 7. Final render, mix, captions, cover (10 min)
- `blend.py <slug> cues`, then `blend.py <slug> final` in the background (render times, and
  never two at once).
- `finish.py <slug>`: the voice, SFX and music bus, ducking, one-word captions, `final.mp4` and
  `final_phone.mp4`.
- QA the final file with the ffmpeg tile command, then re-render only the bad shots
  (`final 14,22`).
- `cover.py <slug> "2-4 WORD TITLE"`, plus `--frame` / `--time` to pick the moment.
- `clean.py <slug>` frees the several GB of frames.

## 8. Bonus episodes
- **Your own sound pack:** `sfxprep.py`, variants (`poof_1.wav`), numpy-synthesized tones, and
  `pack.json` gain and lead.
- **Learning from references:** `analyze_inspo.py` for cut pacing and word timing (learn the
  pattern, never copy a plot).
- **A new set:** a small `rbx` function with primitives and materials, reused across videos.
- **Full autopilot:** "make me a roblox story, autopilot", start to finish with no input.
