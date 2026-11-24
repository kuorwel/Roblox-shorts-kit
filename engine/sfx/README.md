# Sound effects

`pack.json` lists the sounds the shots use, with each one's level (`gain`, in dB) and `lead`
(the seconds before the peak, so the hit lands right on the cue). The repo doesn't include the
`.wav` files.

Put your own 48 kHz mono `<name>.wav` files here, or in `~/RobloxStories/sfx/` after setup.
`tools/sfxprep.py raw.mp3 sfx/<name>.wav` trims and levels a raw sound. Name variants
`poof_1.wav`, `poof_2.wav` and so on, and they play in rotation. If a cue has no file, it's
skipped with a warning.

Names the example videos use: aww boing bonk boom buzzer cashier chat cheer click clink coin
confetti crickets crowd ding door footsteps gasp glitch hammer jet kids_laugh meow paper pigeon
place poof pop rimshot rise rocket rope sneeze snort sparkle splat stomp teleport thud whoosh
wind window zombie alarm
