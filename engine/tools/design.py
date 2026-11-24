"""Character designs rendered by the kit's own 3D rig (replaces generated character sheets).
    python tools/design.py <slug> characters/_options/<slug>_A.json [..._B.json ..._C.json]
    python tools/design.py --one characters/maya.json        just characters/maya_sheet.png
Each json holds Char arguments (see SKILL.md step 2). For each one this renders a front/side/back
turnaround in Blender with a row of colour swatches under it (-> same path, .png), then puts the
options in one labelled picture, videos/<slug>/character_options.jpg (via tools/options.py).
What you see is exactly what the video will use: the picture IS the rig."""
import json, os, subprocess, sys
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit  # noqa: E402

TOOLS = os.path.dirname(os.path.abspath(__file__))


def render(js):
    js = os.path.abspath(js)
    png = os.path.splitext(js)[0] + ("_sheet.png" if "--one" in sys.argv else ".png")
    b = kit.find_blender()
    if not b:
        sys.exit("Blender not found. Install Blender 5.x, or put its path in config.json as \"blender\".")
    r = subprocess.run([b, "-b", "--factory-startup", "-P", os.path.join(TOOLS, "char_render.py"), "--", js, png],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if not os.path.exists(png):
        sys.exit("render failed:\n" + "\n".join((r.stdout + r.stderr).strip().splitlines()[-20:]))
    swatches(png, json.load(open(js, encoding="utf-8")))
    return png


def swatches(png, a):
    im = Image.open(png).convert("RGB")
    cols = [("skin", a.get("skin", "#f1dfc6")), ("hair", a.get("hair_color", "#a05f37")),
            ("shirt", a.get("shirt", "#8db8ee")), ("pants", a.get("pants", "#3d5fb8"))]
    for k in ("shirt_c2", "pants_c2", "vneck", "bolt"):
        if isinstance(a.get(k), str):
            cols.append((k.replace("_c2", " 2"), a[k]))
    H = 150
    out = Image.new("RGB", (im.width, im.height + H), (255, 255, 255))
    out.paste(im, (0, 0))
    d = ImageDraw.Draw(out)
    f, fb = kit.font("arialbd.ttf", 26), kit.font("ariblk.ttf", 40)
    d.text((40, im.height + H // 2), a.get("name", ""), fill=(30, 30, 36), font=fb, anchor="lm")
    x = 420
    for label, hx in cols:
        d.rounded_rectangle((x, im.height + 18, x + 110, im.height + 88), 12, fill=hx, outline=(60, 60, 60), width=2)
        d.text((x + 55, im.height + 112), f"{label} {hx}", fill=(50, 50, 56), font=f, anchor="mm")
        x += 200
    desc = f"hair: {a.get('hair', '')}   face: {a.get('face', '')}   extras: {', '.join(a.get('extras') or []) or 'none'}"
    d.text((im.width - 40, im.height + H // 2), desc, fill=(90, 90, 96), font=f, anchor="rm")
    out.save(png)


args = [x for x in sys.argv[1:] if not x.startswith("--")]
if "--one" in sys.argv:
    if not args:
        sys.exit(__doc__)
    print(render(args[0]))
    sys.exit(0)
if len(args) < 2:
    sys.exit(__doc__)
slug, files = args[0], args[1:5]
pngs = [render(f) for f in files]
if len(pngs) == 1:
    print(pngs[0])
else:
    subprocess.run([sys.executable, os.path.join(TOOLS, "options.py"), slug] + pngs, check=True)
