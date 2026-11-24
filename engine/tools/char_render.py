"""Blender side of tools/design.py: render one character json as a front / side / back turnaround.
blender -b --factory-startup -P tools/char_render.py -- <character.json> <out.png>"""
import json, math, os, sys
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import shotkit  # noqa: E402,F401  (sets up rbx paths)
from rbx.core import reset, setup_render, world, mat, plane, light, Cam, hexc  # noqa: E402
from rbx import chars, story  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:]
src, out = argv[0], argv[1]
a = json.load(open(src, encoding="utf-8"))
nm = a.get("name") or "KID"
if "extras" in a:   # a bare backpack would print the rig's default label, so use the character's name
    a["extras"] = ["backpack:" + nm.upper() if e == "backpack" else e for e in a["extras"]]
for k in ("sheet", "notes", "name"):
    a.pop(k, None)
if "extras" in a:
    a["extras"] = tuple(a["extras"])

reset()
setup_render(1, 1, res=(1920, 1080), samples=32, pct=100, blur=False)
world((1.0, 1.0, 1.0), 1.0)
plane("floor", 80, 80, (0, 0, 0), mat("floor", (0.93, 0.93, 0.95), 0.6))
# three copies of the character: front (faces -Y, the camera), side, back
for i, (x, rot) in enumerate(((-5.2, 0.0), (0.0, -90.0), (5.2, 180.0))):   # degrees
    ch = chars.Char(f"D{i}", loc=(x, 0, 0), rot=rot, seed=1, **a)
    try:
        story._live(ch, 0.0, 0.1, "happy")
    except Exception as e:
        print("face:", e)
light("key", "AREA", (-6, -12, 12), 2600, size=10, target=(0, 0, 2.5))
light("fill", "AREA", (8, -10, 6), 900, size=8, target=(0, 0, 2.5))
light("rim", "AREA", (0, 10, 10), 1200, size=8, target=(0, 0, 3))
cam = Cam("Cam", lens=60)
cam.key(1, (0, -24, 3.2), (0, 0, 2.7), lens=60)
sc = bpy.context.scene
try:
    sc.view_settings.look = "AgX - Punchy"
except TypeError:
    pass
sc.frame_set(1)
sc.render.filepath = out
bpy.ops.render.render(write_still=True)
print("rendered", out)
