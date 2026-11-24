"""YouTube Shorts cover from a rendered frame, made locally with Pillow.
    python tools/cover.py <slug> "<TITLE>" [--frame 0412 | --time 12.5] [--color #ffe14d]
Takes videos/<slug>/frames/<frame>.png (or the frame at --time seconds; default: the frame with the
most colour and contrast in the first third), punches up the colour, adds a vignette and a big
2-4 word title in white with a thick black outline (the last word in --color). Writes
videos/<slug>/out/cover.jpg (1080x1920)."""
import argparse, glob, os, sys
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageStat

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("slug"); ap.add_argument("title")
ap.add_argument("--frame"); ap.add_argument("--time", type=float)
ap.add_argument("--color", default="#ffe14d")
o = ap.parse_args()
vdir = os.path.join(kit.STUDIO, "videos", o.slug)
frames = sorted(glob.glob(os.path.join(vdir, "frames", "*.png")))
if not frames:
    frames = sorted(glob.glob(os.path.join(vdir, "preview", "shot_*.png")))
if not frames:
    sys.exit("No frames yet: render the video (or at least a preview) first.")

if o.frame:
    src = os.path.join(vdir, "frames", f"{int(o.frame):04d}.png")
elif o.time is not None:
    src = os.path.join(vdir, "frames", f"{int(round(o.time * 30)) + 1:04d}.png")
else:
    pool = frames[: max(1, len(frames) // 3)][::max(1, len(frames) // 90)]
    def score(p):
        s = ImageStat.Stat(Image.open(p).convert("HSV").resize((108, 192)))
        return s.mean[1] + s.stddev[2]          # saturation + contrast
    src = max(pool, key=score)

im = Image.open(src).convert("RGB").resize((1080, 1920), Image.LANCZOS)
im = ImageEnhance.Color(im).enhance(1.3)
im = ImageEnhance.Contrast(im).enhance(1.1)
W, H = im.size
vig = Image.new("L", (W, H), 0)
ImageDraw.Draw(vig).ellipse((-W * 0.25, -H * 0.1, W * 1.25, H * 1.1), fill=255)
vig = vig.filter(ImageFilter.GaussianBlur(160))
im = Image.composite(im, Image.new("RGB", (W, H), (0, 0, 0)), vig)

d = ImageDraw.Draw(im)
words = o.title.upper().split()
# break into 1-2 lines, at most ~12 characters each
lines, cur = [], ""
for w in words:
    if cur and len(cur) + 1 + len(w) > 12:
        lines.append(cur); cur = w
    else:
        cur = (cur + " " + w).strip()
lines.append(cur)
size = 260
while size > 60:
    f = kit.font("ariblk.ttf", size)
    if all(d.textbbox((0, 0), l, font=f)[2] <= W * 0.9 for l in lines):
        break
    size -= 10
f = kit.font("ariblk.ttf", size)
y = H * 0.16
for k, l in enumerate(lines):
    last = k == len(lines) - 1
    col = o.color if last and len(lines) > 1 else "#ffffff"
    d.text((W / 2, y), l, font=f, fill=col, anchor="mt", stroke_width=max(8, size // 14), stroke_fill="#000000")
    y += size * 1.05
out_dir = os.path.join(vdir, "out")
os.makedirs(out_dir, exist_ok=True)
out = os.path.join(out_dir, "cover.jpg")
im.save(out, quality=92)
print(f"{out} (from {os.path.basename(src)})")
