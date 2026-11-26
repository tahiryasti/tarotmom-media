import math, random, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, DUR = 1080, 1920, 30, 15.0
N = int(FPS * DUR)
OUT = sys.argv[1] if len(sys.argv) > 1 else "video_noaudio.mp4"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerifCondensed.ttf"
GOLD = (232, 196, 120)
CREAM = (250, 240, 225)

random.seed(7)

def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)

def fade(t, a, b, d=0.5):
    """1 between a and b with d-second fades."""
    if t < a or t > b:
        return 0.0
    return min(ease((t - a) / d), ease((b - t) / d))

# ---------- background ----------
bg = Image.new("RGB", (W, H))
px = bg.load()
for y in range(H):
    k = y / H
    r = int(18 + 30 * k); g = int(8 + 10 * k); b = int(45 + 35 * (1 - abs(k - 0.5) * 2))
    for x in range(W):
        px[x, y] = (r, g, b)
neb = Image.new("RGB", (W, H), (0, 0, 0))
nd = ImageDraw.Draw(neb)
for _ in range(9):
    cx, cy, rr = random.randint(0, W), random.randint(0, H), random.randint(200, 450)
    col = random.choice([(90, 40, 140), (40, 50, 140), (120, 50, 110)])
    nd.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=col)
neb = neb.filter(ImageFilter.GaussianBlur(160))
bg = Image.blend(bg, Image.eval(neb, lambda v: v), 0.35)

stars = [(random.randint(0, W), random.randint(0, H), random.uniform(1, 3.2),
          random.uniform(0, 6.28), random.uniform(0.8, 2.5)) for _ in range(170)]

# ---------- glow behind card ----------
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(glow).ellipse([W/2 - 380, 900 - 560, W/2 + 380, 900 + 560], fill=(240, 190, 110, 120))
glow = glow.filter(ImageFilter.GaussianBlur(110))

# ---------- cards ----------
CW, CH = 540, 900

def star_poly(cx, cy, r1, r2, n=8, rot=-math.pi / 2):
    pts = []
    for i in range(n * 2):
        r = r1 if i % 2 == 0 else r2
        a = rot + i * math.pi / n
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts

def card_base(fill):
    im = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, CW - 1, CH - 1], 36, fill=fill)
    d.rounded_rectangle([18, 18, CW - 19, CH - 19], 26, outline=GOLD, width=5)
    d.rounded_rectangle([32, 32, CW - 33, CH - 33], 20, outline=GOLD + (150,), width=2)
    return im, d

back, d = card_base((35, 18, 70, 255))
cx, cy = CW / 2, CH / 2
for r in (230, 190, 150):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=GOLD, width=3)
d.polygon(star_poly(cx, cy, 120, 40), fill=GOLD)
d.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=(35, 18, 70))
# crescent moons top/bottom
for my in (120, CH - 120):
    d.ellipse([cx - 45, my - 45, cx + 45, my + 45], fill=GOLD)
    d.ellipse([cx - 25, my - 55, cx + 55, my + 35], fill=(35, 18, 70))
for (sx, sy) in [(90, 90), (CW - 90, 90), (90, CH - 90), (CW - 90, CH - 90)]:
    d.polygon(star_poly(sx, sy, 18, 6, 4), fill=GOLD)

import json
SPEC = json.load(open(sys.argv[3])) if len(sys.argv) > 3 else {
    "numeral": "XVII", "name": "THE STAR", "symbol": "star",
    "hook": ["This card found you", "for a reason..."],
    "messages": [["Hope is returning to you."], ["What you thought was lost", "is finding its way back."], ["Trust the timing."]],
    "cta_top": ["Type \"I receive\"", "to claim this energy"]}

def draw_symbol(d, sym, cx, cy):
    Y, L, P = (255, 214, 120), (255, 245, 210), (200, 170, 255)
    if sym == "star":
        d.polygon(star_poly(cx, cy, 120, 42, 8), fill=Y)
        d.polygon(star_poly(cx, cy, 70, 26, 8, rot=-math.pi / 2 + math.pi / 8), fill=L)
    elif sym == "sun":
        for k in range(16):
            a = k * math.pi / 8
            r2 = 135 if k % 2 == 0 else 110
            d.polygon([(cx + 70 * math.cos(a - .18), cy + 70 * math.sin(a - .18)), (cx + r2 * math.cos(a), cy + r2 * math.sin(a)), (cx + 70 * math.cos(a + .18), cy + 70 * math.sin(a + .18))], fill=Y)
        d.ellipse([cx - 75, cy - 75, cx + 75, cy + 75], fill=Y); d.ellipse([cx - 55, cy - 55, cx + 55, cy + 55], fill=L)
    elif sym == "moon":
        d.ellipse([cx - 100, cy - 100, cx + 100, cy + 100], fill=L)
        d.ellipse([cx - 55, cy - 125, cx + 135, cy + 65], fill=(30, 28, 80))
    elif sym == "heart":
        d.ellipse([cx - 100, cy - 80, cx, cy + 20], fill=(235, 110, 140)); d.ellipse([cx, cy - 80, cx + 100, cy + 20], fill=(235, 110, 140))
        d.polygon([(cx - 97, cy - 15), (cx + 97, cy - 15), (cx, cy + 110)], fill=(235, 110, 140))
    elif sym == "crown":
        d.polygon([(cx - 110, cy + 60), (cx - 110, cy - 50), (cx - 55, cy), (cx, cy - 80), (cx + 55, cy), (cx + 110, cy - 50), (cx + 110, cy + 60)], fill=Y)
        for x in (-110, 0, 110):
            yy = -50 if x else -80
            d.ellipse([cx + x - 14, cy + yy - 14, cx + x + 14, cy + yy + 14], fill=L)
    elif sym == "eye":
        d.polygon([(cx - 130, cy), (cx, cy - 70), (cx + 130, cy), (cx, cy + 70)], fill=L)
        d.ellipse([cx - 50, cy - 50, cx + 50, cy + 50], fill=P); d.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=(30, 28, 80))
    elif sym == "wheel":
        d.ellipse([cx - 120, cy - 120, cx + 120, cy + 120], outline=Y, width=12)
        d.ellipse([cx - 30, cy - 30, cx + 30, cy + 30], fill=Y)
        for k in range(8):
            a = k * math.pi / 4
            d.line([(cx, cy), (cx + 115 * math.cos(a), cy + 115 * math.sin(a))], fill=Y, width=8)
    elif sym == "lightning":
        d.polygon([(cx + 20, cy - 140), (cx - 60, cy + 10), (cx - 5, cy + 10), (cx - 30, cy + 140), (cx + 60, cy - 20), (cx + 5, cy - 20)], fill=Y)
    elif sym == "infinity":
        for sgn in (-1, 1):
            d.ellipse([cx + sgn * 62 - 60, cy - 50, cx + sgn * 62 + 60, cy + 50], outline=Y, width=14)
    elif sym == "cup":
        d.chord([cx - 90, cy - 120, cx + 90, cy + 40], 0, 180, fill=Y)
        d.rectangle([cx - 10, cy - 40, cx + 10, cy + 90], fill=Y); d.ellipse([cx - 60, cy + 75, cx + 60, cy + 105], fill=Y)
    elif sym == "sword":
        d.polygon([(cx, cy - 150), (cx - 16, cy - 120), (cx - 16, cy + 60), (cx + 16, cy + 60), (cx + 16, cy - 120)], fill=L)
        d.rectangle([cx - 70, cy + 60, cx + 70, cy + 80], fill=Y); d.rectangle([cx - 12, cy + 80, cx + 12, cy + 140], fill=Y)
    else:
        draw_symbol(d, "star", cx, cy)

front, d = card_base((245, 232, 205, 255))
navy = (40, 30, 85)
d.rectangle([50, 140, CW - 50, CH - 170], fill=(30, 28, 80))
for (sx, sy, s) in [(110, 190, 14), (430, 180, 16), (100, 470, 12), (445, 460, 14), (150, 560, 9), (395, 560, 9)]:
    d.polygon(star_poly(sx, sy, s, s * 0.35, 8), fill=(255, 240, 200))
draw_symbol(d, SPEC["symbol"], CW / 2, 360)
for i, wy in enumerate(range(620, CH - 180, 26)):
    pts = [(x, wy + 7 * math.sin(x / 38 + i)) for x in range(52, CW - 50, 6)]
    d.line(pts, fill=(110, 150, 220) if i % 2 == 0 else (80, 110, 190), width=4)
f_num = ImageFont.truetype(SERIF_B, 54)
name = SPEC["name"]
fs = 56
while True:
    f_name = ImageFont.truetype(SERIF_B, fs)
    if d.textlength(name, font=f_name) <= CW - 90 or fs <= 30: break
    fs -= 2
d.text((CW / 2, 88), SPEC["numeral"], font=f_num, fill=navy, anchor="mm")
d.text((CW / 2, CH - 100), name, font=f_name, fill=navy, anchor="mm")

shadow = Image.new("RGBA", (CW + 120, CH + 120), (0, 0, 0, 0))
ImageDraw.Draw(shadow).rounded_rectangle([60, 70, CW + 60, CH + 70], 36, fill=(0, 0, 0, 150))
shadow = shadow.filter(ImageFilter.GaussianBlur(28))

# ---------- text ----------
f_hook = ImageFont.truetype(SERIF_B, 64)
f_title = ImageFont.truetype(SERIF_B, 58)
f_msg = ImageFont.truetype(SERIF_I, 58)
f_cta = ImageFont.truetype(SERIF_B, 56)
f_small = ImageFont.truetype(SERIF, 40)

def draw_lines(layer, lines, y, font, fill, alpha, spacing=1.25, stroke=3):
    if alpha <= 0:
        return
    d = ImageDraw.Draw(layer)
    a = int(255 * alpha)
    lh = font.size * spacing
    for i, ln in enumerate(lines):
        d.text((W / 2, y + i * lh), ln, font=font, fill=fill + (a,), anchor="mm",
               stroke_width=stroke, stroke_fill=(15, 5, 35, int(a * 0.8)))

_MSG = [(4.4, ["Hope is returning to you."]),
       (6.4, ["What you thought was lost", "is finding its way back."]),
       (8.8, ["Trust the timing."])]

CARD_Y = 880  # card centre

def frame(i):
    t = i / FPS
    im = bg.copy().convert("RGBA")
    d = ImageDraw.Draw(im)
    for (sx, sy, s, ph, sp) in stars:
        a = 0.45 + 0.55 * (0.5 + 0.5 * math.sin(t * sp + ph))
        c = int(255 * a)
        yy = (sy - t * 6 * s) % H
        d.ellipse([sx - s, yy - s, sx + s, yy + s], fill=(c, c, int(c * 0.92), 255))
    # glow grows after reveal
    g = 0.35 + 0.65 * ease((t - 3.0) / 1.2)
    gl = glow.copy()
    gl.putalpha(gl.getchannel("A").point(lambda v: int(v * g)))
    im.alpha_composite(gl)

    # card: float + flip between 2.4s and 3.4s
    fy = CARD_Y + 14 * math.sin(t * 1.6)
    p = (t - 2.4) / 1.0
    p = ease(p)
    scale_in = 0.86 + 0.14 * ease(t / 1.2)
    sx = abs(math.cos(math.pi * p))
    face = back if p < 0.5 else front
    cw = max(2, int(CW * sx * scale_in)); ch = int(CH * scale_in)
    card = face.resize((cw, ch), Image.LANCZOS)
    sh = shadow.resize((max(2, int((CW + 120) * sx * scale_in)), int((CH + 120) * scale_in)))
    im.alpha_composite(sh, (int(W / 2 - sh.width / 2), int(fy - sh.height / 2)))
    im.alpha_composite(card, (int(W / 2 - cw / 2), int(fy - ch / 2)))

    txt = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_lines(txt, SPEC["hook"], 230, f_hook, CREAM, fade(t, 0.2, 3.3, 0.4))
    draw_lines(txt, ["Today's card:", name], 230, f_title, GOLD, fade(t, 3.5, 11.6, 0.5))
    m = SPEC["messages"]
    ys = [1420]
    for k in range(1, len(m)):
        ys.append(ys[-1] + int(len(m[k - 1]) * f_msg.size * 1.25) + 20)
    for k, (lines, st) in enumerate(zip(m, (4.4, 6.4, 8.8))):
        draw_lines(txt, lines, ys[k], f_msg, GOLD if k == len(m) - 1 else CREAM, fade(t, st, 11.6, 0.5))
    draw_lines(txt, SPEC["cta_top"], 210, f_cta, GOLD, fade(t, 11.9, 16, 0.5))
    draw_lines(txt, ["Follow @tarotmomdaily", "for your daily card"], 1460, f_cta, CREAM, fade(t, 12.3, 16, 0.5))
    im.alpha_composite(txt)

    # fade in/out from black
    k = min(ease(t / 0.6), ease((DUR - t) / 0.5))
    out = im.convert("RGB")
    if k < 1:
        out = Image.blend(Image.new("RGB", (W, H)), out, k)
    return out

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[2] == "stills":
        for tt in (1.5, 2.9, 7.5, 10.5, 13.5):
            frame(int(tt * FPS)).save(f"still_{tt}.png")
        sys.exit(0)
    tmp = OUT.replace(".mp4", ".part.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast",
                          "-crf", "19", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for i in range(N):
        p.stdin.write(frame(i).tobytes())
    p.stdin.close()
    if p.wait() == 0:
        import os; os.replace(tmp, OUT)
        print("ok")
