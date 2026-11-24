---
name: roblox-story-kit
description: Make an original Roblox-style 3D animated story video (9:16 short, 60-120s, "In this world, X makes you Y" format, first-person narrator) end to end, fully on this computer with no accounts or credits: a local neural narrator voice (Kokoro, or macOS say), character designs rendered by the kit's own Blender rig, Pillow textures and cover, and Blender for the animation, plus silences cut, sound effects, fast cuts, captions and music. Use when the user says "roblox story", "roblox animation video", "make a story video about X", "make a roblox short about X", asks for story ideas for this format, or sends popular Roblox animation story videos to learn the pattern from. It stops once by default, for the user to pick the lead character from three rendered designs; "autopilot" in the request skips that stop too. Also use for first-time setup or updating of the kit ("set up the roblox kit", "update the roblox kit").
---

# Roblox story kit (local edition)

A complete studio for fast, high-retention Roblox-style story shorts, running entirely on this
computer: no subscriptions, no accounts, no credits. **Kokoro** (an offline neural TTS) reads the
narration (macOS `say` is the fallback), **Blender**, running from Python, builds and animates the
blocky 3D characters, sets and camera moves and also renders the character designs, and **Pillow**
draws the signs, boards, screens and the cover. One video = one folder `videos/<slug>/`.

## 0. Before anything (every time)

**Workspace.** The kit's code lives next to this file; videos are made in a separate workspace
(default `~/RobloxStories`). `~/.roblox-story-kit.json` holds `{"workspace", "python", "kit"}`.
- If that file is missing, or the user asks to set up or update: run
  `python "<this skill's folder>/setup.py"` (`--update` after unzipping a new kit version). It
  copies the engine, makes a private Python env (`.venv`), installs numpy, Pillow,
  faster-whisper, yt-dlp and kokoro-onnx, downloads the Kokoro voice model (~340 MB), finds
  Blender and ffmpeg, downloads the music and renders one test frame. It prints `READY` or exactly what is missing and the command that fixes it.
- Missing ffmpeg, Blender or a new enough Python (3.10-3.13): give the user the fix line setup
  printed and offer to run it (winget on Windows, brew on Mac). Ask first: it installs software.
  Blender must be 5.x. Run setup.py with that Python (e.g. `python3.12 setup.py`).
- Run every command below **from the workspace folder** with the kit's python:
  `PY` = the `python` path in `~/.roblox-story-kit.json`.

**Narrator voice.** `tools/tts.py` reads the script with Kokoro (config `tts_voice`, default
`am_puck`, an energetic young male voice; `am_michael`, `am_adam`, `af_heart`, `af_bella` and
others work too). If Kokoro isn't installed it uses macOS `say` (`say_voice`). If the user sends
their own recorded voiceover, skip tts.py and feed their file to `voice_run.py`.

**ElevenLabs (optional).** If `config.json` has `"tts_engine": "elevenlabs"`, tts.py reads the script
with the user's ElevenLabs account (their credits, ~1 per character). The key lives only in
`~/.config/elevenlabs/key` (or `$ELEVENLABS_API_KEY`): never read it out, copy it, or write it
anywhere yourself; if it is missing, tell the user to put it there. `$PY tools/tts.py --list-voices`
lists their voices; save the chosen one with `$PY tools/kit.py set elevenlabs_voice_id <id>`.

Read `PLAYBOOK.md` in the workspace before writing: the numbers to hit, beat sheet, hook
checklist, shot grammar, camera, acting, captions and sound rules distilled from 9 popular
reference videos. Worked examples: `videos/laugh_float/shots.py` (73 shots, 88s) and
`videos/sneeze_teleport/shots.py` (66 shots, 71s). Copy their style. Both ship with their script,
shots and word timings but no voice recording, so the first test is `$PY tools/tts.py sneeze_teleport`,
the three voice-processing commands of step 4, then `$PY tools/blend.py sneeze_teleport cues`,
`$PY tools/blend.py sneeze_teleport final` and `$PY tools/finish.py sneeze_teleport`: a real video
with no credits.

Stories must be original: our own characters, sets and plots, no real Roblox UI, logos, avatars
or game sounds, and no copied plots of other creators' videos.

## How a run goes

The user's request is the brief. Anything it leaves out (the idea, the story, the characters, the
title) you decide yourself: never ask about it. Anything it describes (a story, a character, a
place) you follow.

- **Default: two prompts.** Request, then you do everything up to the lead character's three
  rendered designs, then **the one stop** (step 2): the designs, the story flow in a few lines
  and "Which one, A, B or C?". Their answer, then the finished video with no
  more questions.
- **Autopilot: one prompt.** The request says "autopilot" (or "make every decision", "don't ask
  me anything"): no stop at all. You make one design for the lead and pick it, and the next thing
  the user sees is the finished video.
- If the request already settles the lead (names a saved character, "same character as last
  time"), there is nothing to pick, so there is no stop either.
- **A standing lead**: if the user has said their lead is always the same saved character
  (`characters/<key>.json`, used with `from_sheet("<key>", ...)`), there is no design stop: go
  straight from the request to the finished video. Design a different lead only if the user asks
  for one in that request.

Never stop to show the script or to report progress. The only other stop: first-time setup has
to install software (ask first). Long steps (voice processing, the final render) run in the background:
carry on as soon as each one finishes, without asking the user to come back.

## The pipeline

1. **Idea + script** (`videos/<slug>/script.txt`, `#` lines are notes). Shell: everyday thing +
   one impossible rule. Beat sheet from the playbook: result-first hook line, "You see, in this
   world, ...", 2-3 society examples (each its own location), "But" pivot, escalation ladder
   with onomatopoeia ("Poof!", "Bonk!") and short shouted lines, "Then I noticed something"
   (win using the world's own rule), payoff, 2-6 word button that reopens the loop (a callback
   works great). 300-400 words; ~65-75 words must land in the first 15s.
   Don't show the script for approval: nobody reads it. It feeds the story flow at the stop.

2. **Lead character (rendered designs) and the one stop.**
   **Designs.** Give the lead three clearly different looks (hair, colors, one accessory each),
   all fitting the story; if the user described the character, make three takes on that
   description. Each design is a `Char` json (format below) in
   `characters/_options/<slug>_A.json` (`_B`, `_C`); on autopilot, make one. Then render them all:
   `$PY tools/design.py <slug> characters/_options/<slug>_A.json characters/_options/<slug>_B.json characters/_options/<slug>_C.json`
   Each gets a front/side/back turnaround from the kit's own rig with colour swatches, and they
   go in one labelled picture, `videos/<slug>/character_options.jpg`. Look at it: if a design
   reads badly (colours too close, hair clashing), fix the json and re-render that one.

   **The stop** (skip it on autopilot). One message with:
   - the picture: send the file if your app can show it (for example SendUserFile in the Claude
     desktop app), and always give its full path;
   - the story flow: the title, the world's rule in one line, then 4-6 short lines of what the
     lead does and what happens, ending on the twist;
   - saved leads from `characters/`, if there are any, on one line ("or reuse Maya");
   - one question: "Which one, A, B or C? You can change anything in the story in the same reply."
   Wait for the answer. It can also change the story or the look ("B with a red cap"): apply it
   (rewrite the script, edit the json, re-render) and carry on without asking again.

   **After the pick** (or your own pick on autopilot): copy the chosen json to
   `characters/<key>.json`, set its `name`, `notes` and `"sheet": "characters/<key>_sheet.png"`,
   and run `$PY tools/design.py --one characters/<key>.json` to save its sheet:
   ```json
   {"name": "Maya", "skin": "#EED7BC", "hair": "bob", "hair_color": "#5B3F2E",
    "shirt": "#7EBDE6", "pants": "#31496B", "face": "girl", "sleeves": "short",
    "bolt": null, "vneck": null, "shirt_kind": null, "extras": ["glasses"],
    "sheet": "characters/maya_sheet.png", "notes": "the narrator's best friend"}
   ```
   Options the rig has: `hair` spiky messy short slick buzz bob bun cap helmet tophat pilot bald
   none; `face` kid hero girl plain mustache villain hero_blood; `sleeves` short long;
   `shirt_kind`/`pants_kind` stripes checker (second color in `shirt_c2`/`pants_c2`); `bolt` = a
   lightning logo color on the chest; `vneck` = collar color; `extras` glasses beard collar
   backpack (`"backpack:TEXT"`), `collar:#hex`. In shots: `M = from_sheet("maya", t0, t1, "happy")` (from `rbx.story`). Sheets
   are reused across videos, so a character is designed once.

   **Other characters.** Named side characters who matter to the story get one json each
   (`characters/<key>.json`, then `design.py --one` to check the look), without asking. Background people and crowds use
   the built-in cast (`kid(i)`, `townie`, `crowd`) and need no sheet.

3. **Voice (local).** `$PY tools/script_text.py <slug>` prints the exact narration text and its
   length. Then `$PY tools/tts.py <slug>` writes `videos/<slug>/audio/raw.wav` (Kokoro: a few
   seconds to a minute on CPU; `--voice am_michael` etc. to change the narrator for one video,
   `--engine say` to force the macOS voice). Listen-free check: the duration printed by
   `ffprobe videos/<slug>/audio/raw.wav` should be roughly words / 3 seconds.

4. **Voice processing** (from the workspace):
   ```
   $PY tools/voice_run.py --video <slug> --voice videos/<slug>/audio/raw.wav --speed 1.15
   $PY tools/tighten.py <slug> --max-gap 0.45
   $PY tools/retempo.py <slug> --wpm 258
   ```
   voice_run = speed up, cut silences (0.10s inside sentences, 0.22s between, so it never
   sounds chopped), then faster-whisper word timestamps aligned to the script (first run
   downloads the whisper model, ~1.5 GB; on CPU it takes a few minutes). tighten trims breaths
   the silence cutter keeps. Then check `audio/words.json`: 255-280 wpm, 65-75 words before 15s,
   no gap over ~0.45s.

5. **Textures (Pillow).** Every sign, poster, chalkboard, TV screen, billboard, book cover or
   backdrop the story shows:
   `$PY tools/texture.py <name> "HEADLINE|smaller line" --style sign --aspect 16:9`
   (styles: sign poster chalk screen banner paper neon warning; `--bg/--fg/--accent #hex`).
   Short text only, readable at a glance. It writes `assets/tex/<name>.png`. For a prop that needs
   a drawing (a clock, a crack, a lotto ticket), write a small Pillow function like the ones in
   `tools/make_textures.py`. Use it with `classroom_day(board="<name>.png")`, or on any prop:
   `card("my_sign", w, h, loc, img_mat("my_sign", os.path.join(W.TEX, "<name>.png"), 0.6), "-Y")`.
   Reuse textures across videos instead of redrawing.

6. **Sound effects**: the shots use a pack in `sfx/` (`aww boing bonk boom buzzer cashier chat
   cheer click clink coin confetti crickets crowd ding door footsteps gasp glitch hammer jet
   kids_laugh meow paper pigeon place poof pop rimshot rise rocket rope sneeze snort sparkle
   splat stomp teleport thud whoosh wind window zombie alarm`). The public repo ships only
   `sfx/pack.json` (levels and lead times), not the sounds: put your own `<name>.wav` files in
   `sfx/` (`tools/sfxprep.py raw.mp3 sfx/poof.wav` trims and levels one). A cue with no sound is
   skipped with a warning, so a video still finishes. Reuse the pack, or synthesize a simple new tone with numpy into `sfx/<name>.wav`
   and add `lead`/`gain` to `sfx/pack.json` (lead = seconds before the peak, so the hit lands on
   the cue).

7. **Shots** (`videos/<slug>/shots.py`):
   ```python
   from shotkit import *
   from rbx import story
   from rbx.story import *
   V = Video(__file__); story.bind(V)
   @S(1, 0, 7, "HOOK: ...")          # shot = script words 0..7; last shot uses None
   def s01(t0, t1): ...
   ```
   Timing is by script word index, so re-generating the voice never breaks the edit. Cut on the
   word that brings a new image, 50-60 cuts per minute (~1.1s average), every noun on screen,
   reaction close-up after every surprise, alternate wide/close/insert. Every shot needs camera
   motion (`cam.push/orbit/crash/whip/track/handheld`; `ensure_motion` adds a drift if you
   forget). Hook: first frame already mid-action and mid-move, crash zoom and whip in the first
   3s. Put `sfx(t, "name")` on every hit, whoosh, poof and reveal.

8. **Preview + fix** (fast: ~2 min for 66 shots on a decent GPU):
   ```
   $PY tools/blend.py <slug> preview all
   $PY tools/contact.py <slug> all 12 full        # -> videos/<slug>/full.jpg, look at it
   $PY tools/blend.py <slug> still:12.3 14 16     # one frame of shot 14 at t=12.3s, half res
   ```
   Look at every tile. Fix, re-preview just those shots (`preview 3,7,12`), repeat until every
   frame reads: face visible, subject framed, nothing blocking the lens.

9. **Render**: `$PY tools/blend.py <slug> cues` (writes `audio/cues.json`), then
   `$PY tools/blend.py <slug> final` in the background. Roughly 1.5-2.5 s per frame on a gaming
   laptop GPU (~1h for 80s), much slower without a GPU; never run two finals at once.

10. **Finish**: `$PY tools/finish.py <slug>` mixes voice + SFX + music, burns one-word captions,
    writes `out/final.mp4` and `out/final_phone.mp4` (720p, ~25 MB). No captionless copy: the user
    only posts the captioned video (`--no-captions` makes one only when asked).
    Music: the first audio file in `music/` (setup downloads TEMPOREX "Numbers"), sped up 1.5x at
    the same pitch, ~10 dB under the voice and ducked while it talks. Use the same house track for
    every video unless the user asks for another bed (`--music <file>`). The track belongs to its
    artist: check its license before you monetize. Synthesized sound effects are fine.

11. **QA the final file**, not just previews:
    `ffmpeg -i videos/<slug>/out/final.mp4 -vf "fps=1/1.8,scale=216:384,tile=10x4" -frames:v 1 videos/<slug>/qa.jpg`.
    Fix any bad shot, `final <ids>` just those shots, re-run finish.

12. **Cover image (local).** Always make one: it is part of the finished video.
    `$PY tools/cover.py <slug> "<2-4 WORD TITLE>"` picks the most colourful, contrasty frame from
    the first third of `frames/` (or pass `--frame 0412` / `--time 12.5` for a specific moment),
    punches up the colour and adds the title in white with a black outline. Writes
    `videos/<slug>/out/cover.jpg`. Look at it; pick another frame if the faces are hidden by the
    title.

13. **Report**: where the video and cover are, anything not checked. You cannot hear the mix, so say so and ask the user to watch it with
    sound. Offer `$PY tools/clean.py <slug>` to delete the rendered frames (several GB) once they
    are happy.

## Toolkit map

- `rbx/core.py` primitives, materials (`mat`, `img_mat`), `card`, `Cam` (push, orbit, crash,
  whip, track, handheld), `sfx`.
- `rbx/chars.py` R6 characters (`Char`, presets `eddie`, `kid(i)`...); options listed in step 2.
- `rbx/acting.py` layered faces: `face(t, "shock")` or `face(t, eyes=, mouth=)`, `blink`,
  `talk` (lip flaps), `act(t, gesture)` with overshoot, `look`, `nod`, `shake`, `jump`, `run`,
  `panic`, `wiggle`, `breathe`. Gestures: idle shock hands_head hands_face cheer point point_l
  shrug recoil lean slump think cross phone reach push hold wave fists facepalm brace.
- `rbx/story.py` cast (eddie, leo, pickle, grandma, pilot, mayor, gus, townie, `from_sheet`),
  `laugh`, `drift`, `dangle`, `fly`, `look_at`, `facing`, `lips`, `class_scene`, `kids_float`,
  `sky_scene`, `cloud_ring`, `town_scene`, `crowd_src` + `crowd` (instanced crowds, cheap),
  `human_chain`, `confetti`, `stars_ring`, `spin`, `puff`.
- `rbx/world.py` (W): `sky`, `space_world`, `sun`, `cloud`, `classroom_day(board=)` (front-row
  desks `E_DESK`/`L_DESK`, hinged window), `town` (school + streets + playground; the area
  around (0,-30) is open street), `comedy_club`, `cockpit`, `tv_room`, `hallway_day`, props
  `pigeon dog car crater toupee`. `W.TEX` = the textures folder.
- `rbx/world2.py` (W2): `cat`, `airliner`, `cabin` (+`seat_root`), `earth`, `moon`,
  `astronaut_helmet`, `pepper_jail`, `flower_shop`, `parking_lot`, `seated_audience`, and the
  teleport kit `poof`, `vanish`, `appear`, `sneeze` (wind-up + CHOO + mist), `tomato`.
- Older sets in `rbx/sets.py` / `rbx/locs.py`: bedroom, mirrors, burning hallway, bathrooms,
  living room, dusk street, dark hall, school corridor, classroom (dim), fire FX in `rbx/fx.py`.
- `tools/kit.py get|set <key>`: settings in `config.json` (tts engine/voice, Blender path, music).
- `tools/tts.py <slug>`: local narrator voice -> `audio/raw.wav`.
- `tools/design.py <slug> <A.json> <B.json> [<C.json>]` / `--one <key.json>`: rig turnarounds +
  the labelled options picture (uses `tools/options.py`).
- `tools/texture.py <name> "TEXT|line"`: prop textures. `tools/cover.py <slug> "TITLE"`: cover.
- `tools/analyze_inspo.py <folder> <out>`: pacing/cut/word-timing analysis of reference videos
  the user sends, to learn a pattern (never to copy a plot).

## Traps already hit (check these in every preview)

- **Camera inside a house / prop**: ground cameras in `town` must stay in the open area
  (x -40..40, y -55..10). Blank single-colour preview tiles almost always mean this.
- **Visibility keys on the same frame**: show/hide keys less than one frame apart collapse into
  one key and the object is hidden for the whole shot. `W2.vanish` keys one full frame earlier.
- **Prop scale**: a Roblox head is ~1.24 wide. Cats and props at 0.5-0.6 scale; never put a
  prop between the lens and the face.
- **Props riding on a character** (cat on head, hats): parent to `ch.head` (see `cat_on_head` in
  sneeze_teleport), never to `ch.root` with a guessed offset.
- **Poofs**: `s=0.6` indoors, 1.5-6 outdoors for vehicles.
- **Framing math**: visible width = 2 x distance x 6.75 / lens. Two characters 3 units apart
  need ~5.5 units of width (lens 20 at distance 8).
- **Brows under hair**: keep the fringe above the brow line or angry reads as "wide".
- **Tall buildings shadow the street**; the town keeps the centre low.
- **No custom attributes on bpy objects** (`obj.head = ...` fails): look things up by name.
- Sky looks pale under AgX: `W.sky()` defaults are already saturated, don't wash them out.
- **Kokoro mispronounces a name**: respell it phonetically in script.txt (the captions follow the
  script, so keep the spelling readable) or swap the word.
- Long Python in a shell heredoc can fail on Windows: write patch scripts to a file and run them.
