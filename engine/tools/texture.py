"""Prop textures drawn with Pillow (signs, posters, chalkboards, screens, banners, book covers).
    python tools/texture.py <name> "LINE ONE|line two" [--style sign] [--aspect 16:9] [--bg #hex] [--fg #hex]
                                                       [--accent #hex] [--emoji-free]
Styles: sign (bold board with a frame), poster (big title, stripe bands), chalk (green chalkboard,
hand-written), screen (glowing TV / phone UI), banner (wide party banner), paper (lined notebook),
neon (dark wall, glowing letters), warning (yellow/black hazard).
'|' separates lines; the first line is the headline. Writes assets/tex/<name>.png and prints the path.
For anything more specific, write a small Pillow function like the ones in tools/make_textures.py."""
import argparse, os, random, sys
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit  # noqa: E402

STYLES = {  # bg, fg, accent, headline font, body font
    "sign": ("#2f6fd6", "#ffffff", "#ffd23f", "ariblk.ttf", "arialbd.ttf"),
    "poster": ("#ffcf3a", "#1d1d2b", "#e8413a", "ariblk.ttf", "arialbd.ttf"),
    "chalk": ("#2c4a3a", "#f2f2ea", "#f7e27a", "segoeprb.ttf", "segoeprb.ttf"),
    "screen": ("#10131f", "#7ef2ff", "#ff4fd8", "ariblk.ttf", "arialbd.ttf"),
    "banner": ("#e84a8a", "#ffffff", "#ffe14d", "ariblk.ttf", "arialbd.ttf"),
    "paper": ("#fbfbf6", "#26304a", "#d93a3a", "segoeprb.ttf", "segoeprb.ttf"),
    "neon": ("#17121f", "#ff5cf0", "#5cf3ff", "ariblk.ttf", "arialbd.ttf"),
    "warning": ("#ffd400", "#111111", "#111111", "ariblk.ttf", "ariblk.ttf"),
}

ap = argparse.ArgumentParser()
ap.add_argument("name"); ap.add_argument("text")
ap.add_argument("--style", default="sign", choices=sorted(STYLES))
ap.add_argument("--aspect", default="16:9")
ap.add_argument("--bg"); ap.add_argument("--fg"); ap.add_argument("--accent")
o = ap.parse_args()
bg, fg, ac, fh, fb = STYLES[o.style]
bg, fg, ac = o.bg or bg, o.fg or fg, o.accent or ac
aw, ah = (float(x) for x in o.aspect.split(":"))
W = 1600 if aw >= ah else round(1600 * aw / ah)
H = round(W * ah / aw)
lines = [l.strip() for l in o.text.split("|") if l.strip()]
rnd = random.Random(o.name)

im = Image.new("RGB", (W, H), bg)
d = ImageDraw.Draw(im)
m = int(min(W, H) * 0.05)
if o.style == "sign":
    d.rounded_rectangle((m, m, W - m, H - m), m, outline=ac, width=max(8, m // 3))
elif o.style == "poster":
    for k in range(0, W + H, 120):
        d.line([(k, 0), (k - H, H)], fill=ac, width=30)
    d.rectangle((m, m, W - m, H - m), fill=bg)
elif o.style == "chalk":
    d.rectangle((0, 0, W, H), outline="#6b4a2a", width=m)
    for _ in range(1500):
        x, y = rnd.randrange(W), rnd.randrange(H)
        d.point((x, y), fill="#3b5a49")
elif o.style == "screen":
    for y in range(0, H, 6):
        d.line([(0, y), (W, y)], fill="#151a2b")
    d.rounded_rectangle((m, m, W - m, int(H * 0.16)), m // 2, fill="#1d2440")
    d.ellipse((W - m * 3, m + 10, W - m * 2, m + 10 + m), fill=ac)
elif o.style == "banner":
    n = 14
    for k in range(n):
        x0 = k * W / n
        d.polygon([(x0, 0), (x0 + W / n, 0), (x0 + W / n / 2, H * 0.14)], fill=[ac, "#5cd1ff", "#7be36b"][k % 3])
elif o.style == "paper":
    for y in range(int(H * 0.18), H, int(H * 0.07)):
        d.line([(0, y), (W, y)], fill="#a9c6ea", width=3)
    d.line([(int(W * 0.1), 0), (int(W * 0.1), H)], fill="#e79a9a", width=4)
elif o.style == "warning":
    for k in range(-H, W + H, 160):
        d.polygon([(k, 0), (k + 80, 0), (k + 80 - H * 0.12, H * 0.12), (k - H * 0.12, H * 0.12)], fill="#111111")
        d.polygon([(k, H), (k + 80, H), (k + 80 + H * 0.12, H * 0.88), (k + H * 0.12, H * 0.88)], fill="#111111")


def fit(text, fontname, max_w, max_h):
    s = int(max_h)
    while s > 12:
        f = kit.font(fontname, s)
        b = d.textbbox((0, 0), text, font=f)
        if b[2] - b[0] <= max_w and b[3] - b[1] <= max_h:
            return f
        s = int(s * 0.92)
    return kit.font(fontname, 12)


top, bot = (0.2 if o.style in ("screen", "banner", "warning") else 0.1) * H, 0.9 * H
avail = bot - top
heads = [lines[0]] if lines else []
body = lines[1:]
hh = avail * (0.55 if body else 0.8)
bh = (avail - hh) / max(1, len(body)) if body else 0
y = top + (avail - hh - bh * len(body)) / 2
glow = o.style in ("neon", "screen")
layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ld = ImageDraw.Draw(layer)
for k, t in enumerate(heads + body):
    is_head = k == 0
    h = hh if is_head else bh
    f = fit(t, fh if is_head else fb, W - 4 * m, h * 0.82)
    col = fg if is_head or o.style in ("chalk", "paper", "warning") else ac
    stroke = max(2, int(h * 0.04)) if is_head and o.style in ("sign", "poster", "banner") else 0
    ld.text((W / 2, y + h / 2), t, font=f, fill=col, anchor="mm", stroke_width=stroke,
            stroke_fill="#1d1d2b" if o.style != "sign" else "#173a7a")
    y += h
if glow:
    g = layer.filter(ImageFilter.GaussianBlur(18))
    im.paste(g, (0, 0), g)
im.paste(layer, (0, 0), layer)
if o.style == "chalk":
    im = im.filter(ImageFilter.GaussianBlur(0.8))

out_dir = os.path.join(kit.STUDIO, "assets", "tex")
os.makedirs(out_dir, exist_ok=True)
out = os.path.join(out_dir, o.name + ".png")
im.save(out)
print(out)
