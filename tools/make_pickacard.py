"""Pick-a-card video (3 piles) for @tarotmomdaily.
Usage: python3 tools/make_pickacard.py out.mp4 render specs/<date>-pick.json
       python3 tools/make_pickacard.py out.mp4 stills specs/<date>-pick.json
Spec:
{"type": "pickacard",
 "hook": ["Pick a card.", "Your message is waiting."],
 "piles": [{"numeral": "VI", "name": "THE LOVERS", "symbol": "heart",
            "messages": [["Line one."], ["Line two a", "line two b"]]}, ... 3 piles],
 "cta": ["Which one did you pick?", "Comment 1, 2 or 3"]}
"""
import json, math, os, subprocess, sys

SPEC_PATH = sys.argv[3]
MODE = sys.argv[2] if len(sys.argv) > 2 else "render"
OUT = sys.argv[1]
SPEC = json.load(open(SPEC_PATH))

# Reuse the look of the daily video (background, stars, card back, symbols, fonts).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
_argv = sys.argv
sys.argv = [_argv[0], OUT]
import make_video as mv  # noqa: E402
sys.argv = _argv
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

W, H, FPS = mv.W, mv.H, mv.FPS
DUR = 26.0
N = int(FPS * DUR)
CW, CH = mv.CW, mv.CH
GOLD, CREAM = mv.GOLD, mv.CREAM
ease, fade, draw_lines = mv.ease, mv.fade, mv.draw_lines
navy = (40, 30, 85)


def make_front(p):
    im, d = mv.card_base((245, 232, 205, 255))
    d.rectangle([50, 140, CW - 50, CH - 170], fill=(30, 28, 80))
    for (sx, sy, s) in [(110, 190, 14), (430, 180, 16), (100, 470, 12), (445, 460, 14), (150, 560, 9), (395, 560, 9)]:
        d.polygon(mv.star_poly(sx, sy, s, s * 0.35, 8), fill=(255, 240, 200))
    mv.draw_symbol(d, p["symbol"], CW / 2, 360)
    for i, wy in enumerate(range(620, CH - 180, 26)):
        pts = [(x, wy + 7 * math.sin(x / 38 + i)) for x in range(52, CW - 50, 6)]
        d.line(pts, fill=(110, 150, 220) if i % 2 == 0 else (80, 110, 190), width=4)
    f_num = ImageFont.truetype(mv.SERIF_B, 54)
    fs = 56
    while True:
        f_name = ImageFont.truetype(mv.SERIF_B, fs)
        if d.textlength(p["name"], font=f_name) <= CW - 90 or fs <= 30:
            break
        fs -= 2
    d.text((CW / 2, 88), p["numeral"], font=f_num, fill=navy, anchor="mm")
    d.text((CW / 2, CH - 100), p["name"], font=f_name, fill=navy, anchor="mm")
    return im


fronts = [make_front(p) for p in SPEC["piles"]]
f_num_big = ImageFont.truetype(mv.SERIF_B, 120)


def numbered_back(n, s):
    im = mv.back.copy()
    d = ImageDraw.Draw(im)
    d.ellipse([CW / 2 - 85, CH / 2 - 85, CW / 2 + 85, CH / 2 + 85], fill=(35, 18, 70), outline=GOLD, width=6)
    d.text((CW / 2, CH / 2 + 4), str(n), font=f_num_big, fill=GOLD, anchor="mm")
    return im.resize((int(CW * s), int(CH * s)), Image.LANCZOS)


SMALL = 0.52
backs_small = [numbered_back(i + 1, SMALL) for i in range(3)]
shadow_small = mv.shadow.resize((int((CW + 120) * SMALL), int((CH + 120) * SMALL)))

# Timeline (seconds)
T_HOOK = (0.2, 3.4)
T_CHOOSE = (3.6, 6.6)
REVEAL = [(6.8, 12.2), (12.4, 17.8), (18.0, 23.4)]
T_CTA = (23.6, DUR)

f_hook = ImageFont.truetype(mv.SERIF_B, 64)
f_title = ImageFont.truetype(mv.SERIF_B, 58)
f_msg = ImageFont.truetype(mv.SERIF_I, 56)
f_cta = ImageFont.truetype(mv.SERIF_B, 56)
f_label = ImageFont.truetype(mv.SERIF_B, 60)


def base(t):
    im = mv.bg.copy().convert("RGBA")
    d = ImageDraw.Draw(im)
    for (sx, sy, s, ph, sp) in mv.stars:
        a = 0.45 + 0.55 * (0.5 + 0.5 * math.sin(t * sp + ph))
        c = int(255 * a)
        yy = (sy - t * 6 * s) % H
        d.ellipse([sx - s, yy - s, sx + s, yy + s], fill=(c, c, int(c * 0.92), 255))
    return im


def three_backs(im, t, alpha, highlight=None):
    if alpha <= 0:
        return
    xs = [W / 2 - 340, W / 2, W / 2 + 340]
    for k in range(3):
        fy = 900 + 14 * math.sin(t * 1.6 + k * 1.3)
        card = backs_small[k].copy()
        sh = shadow_small.copy()
        a = alpha * (0.35 if (highlight is not None and highlight != k) else 1.0)
        card.putalpha(card.getchannel("A").point(lambda v: int(v * a)))
        sh.putalpha(sh.getchannel("A").point(lambda v: int(v * a)))
        im.alpha_composite(sh, (int(xs[k] - sh.width / 2), int(fy - sh.height / 2)))
        im.alpha_composite(card, (int(xs[k] - card.width / 2), int(fy - card.height / 2)))


def reveal_card(im, t, k, a0, a1):
    """Card k flips from its numbered back to its face, centred."""
    if t < a0 or t > a1:
        return
    p = ease((t - a0 - 0.3) / 0.9)
    vis = min(ease((t - a0) / 0.4), ease((a1 - t) / 0.4))
    s = 0.62 + 0.1 * ease((t - a0) / 0.6)
    sx = abs(math.cos(math.pi * p))
    face = numbered_back(k + 1, 1.0) if p < 0.5 else fronts[k]
    cw, ch = max(2, int(CW * s * sx)), int(CH * s)
    card = face.resize((cw, ch), Image.LANCZOS)
    card.putalpha(card.getchannel("A").point(lambda v: int(v * vis)))
    g = mv.glow.copy()
    g.putalpha(g.getchannel("A").point(lambda v: int(v * vis * (0.4 + 0.6 * p))))
    im.alpha_composite(g, (0, -80))
    fy = 800 + 10 * math.sin(t * 1.6)
    im.alpha_composite(card, (int(W / 2 - cw / 2), int(fy - ch / 2)))


def frame(i):
    t = i / FPS
    im = base(t)
    # piles visible during hook + choose
    three_backs(im, t, fade(t, 0.0, T_CHOOSE[1], 0.5))
    for k, (a0, a1) in enumerate(REVEAL):
        reveal_card(im, t, k, a0, a1)
    txt = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_lines(txt, SPEC["hook"], 260, f_hook, CREAM, fade(t, *T_HOOK, 0.4))
    draw_lines(txt, ["Pause the video.", "Breathe... and choose."], 260, f_title, GOLD, fade(t, *T_CHOOSE, 0.4))
    la = fade(t, 0.6, T_CHOOSE[1], 0.4)
    if la > 0:
        dd = ImageDraw.Draw(txt)
        for k, x in enumerate((W / 2 - 340, W / 2, W / 2 + 340)):
            dd.text((x, 1240), str(k + 1), font=f_label, fill=CREAM + (int(255 * la),), anchor="mm",
                    stroke_width=3, stroke_fill=(15, 5, 35, int(204 * la)))
    for k, (a0, a1) in enumerate(REVEAL):
        p = SPEC["piles"][k]
        draw_lines(txt, [f"Card {k + 1}:", p["name"]], 210, f_title, GOLD, fade(t, a0 + 0.8, a1, 0.4))
        y = 1360
        for j, lines in enumerate(p["messages"][:2]):
            draw_lines(txt, lines, y, f_msg, GOLD if j == 1 else CREAM, fade(t, a0 + 1.4 + j * 1.2, a1, 0.4))
            y += int(len(lines) * f_msg.size * 1.25) + 24
    draw_lines(txt, SPEC["cta"], 760, f_cta, GOLD, fade(t, T_CTA[0], DUR + 1, 0.5))
    draw_lines(txt, ["Follow @tarotmomdaily", "for a new reading every week"], 1160, f_cta, CREAM,
               fade(t, T_CTA[0] + 0.4, DUR + 1, 0.5))
    im.alpha_composite(txt)
    k = min(ease(t / 0.6), ease((DUR - t) / 0.5))
    out = im.convert("RGB")
    if k < 1:
        out = Image.blend(Image.new("RGB", (W, H)), out, k)
    return out


if __name__ == "__main__":
    if MODE == "stills":
        for tt in (1.5, 5.0, 9.5, 15.0, 21.0, 25.0):
            frame(int(tt * FPS)).save(f"pick_still_{tt}.png")
        sys.exit(0)
    tmp = OUT.replace(".mp4", ".part.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast",
                          "-crf", "19", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for i in range(N):
        p.stdin.write(frame(i).tobytes())
    p.stdin.close()
    if p.wait() == 0:
        os.replace(tmp, OUT)
        print("ok")
