"""Reel rendering kit: segments -> base video, Pillow overlay compositor -> final reel."""
import os, sys, json, math, subprocess, re, shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SP = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(SP, "dl", "video1.mp4")
WORDS = json.load(open(os.path.join(SP, "dl", "words1.json")))
LOGO_B = Image.open("/home/user/Video-Editing-/recruitment-carousel/photos/barakah-logo.png").convert("RGBA")
LOGO_B = LOGO_B.crop(LOGO_B.getbbox())
LOGO_P = Image.open("/home/user/Video-Editing-/recruitment-carousel/photos/propnex-logo.png").convert("RGBA")
W, H, FPS = 1080, 1920, 30

NAVY = (27, 42, 63); GOLD = (212, 165, 97); GOLD_D = (164, 122, 60); CREAM = (247, 240, 226)
WHITE = (255, 255, 255); INK = (20, 24, 32); RED = (214, 72, 52); GREEN = (46, 160, 96); MUTED = (200, 192, 178)
FD = "/usr/share/fonts/opentype/inter/InterDisplay-ExtraBold.otf"
FB = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
FS = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
FM = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
FSERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
_fc = {}
def font(p, s):
    k = (p, s)
    if k not in _fc: _fc[k] = ImageFont.truetype(p, s)
    return _fc[k]

# ---------- easing ----------
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease_out(x): x = clamp(x); return 1 - (1 - x) ** 3
def ease_back(x):
    x = clamp(x); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def pop_scale(lt, dur=0.32): return ease_back(lt / dur) if lt < dur else 1.0
def fade_out(lt, end, d=0.2): return clamp((end - lt) / d)

# ---------- text helpers ----------
def tw(f, s): return f.getlength(s)
def wrap(f, text, maxw):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if tw(f, t) <= maxw or not cur: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def rrect(d, box, r, fill, outline=None, width=0):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)

def shadowed(img, blur=18, off=(0, 10), alpha=110):
    """Return img with a soft drop shadow behind it (bigger canvas)."""
    pad = blur * 2 + max(off)
    can = Image.new("RGBA", (img.width + pad * 2, img.height + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", can.size, (0, 0, 0, 0))
    a = img.split()[3].point(lambda v: v * alpha // 255)
    sh.paste((0, 0, 0, 255), (pad + off[0], pad + off[1]), a)
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    can.alpha_composite(sh); can.alpha_composite(img, (pad, pad))
    return can, pad

def paste_scaled(frame, img, anchor, scale=1.0, alpha=1.0, align="center"):
    """Paste img onto frame with scale about anchor (x,y). align: center|lt|rt|lb|rb (anchor relative)."""
    if scale <= 0.01 or alpha <= 0: return
    w, h = max(1, int(img.width * scale)), max(1, int(img.height * scale))
    im = img.resize((w, h), Image.LANCZOS) if scale != 1.0 else img
    if alpha < 1.0:
        a = im.split()[3].point(lambda v: int(v * alpha)); im = im.copy(); im.putalpha(a)
    x, y = anchor
    if align == "center": pos = (int(x - w / 2), int(y - h / 2))
    elif align == "lt": pos = (int(x), int(y))
    elif align == "rt": pos = (int(x - w), int(y))
    elif align == "lb": pos = (int(x), int(y - h))
    elif align == "rb": pos = (int(x - w), int(y - h))
    elif align == "ct": pos = (int(x - w / 2), int(y))
    elif align == "cb": pos = (int(x - w / 2), int(y - h))
    frame.alpha_composite(im, pos)

# ---------- element renderers (each returns an RGBA image, built once and cached) ----------
def text_block(lines, fpath, size, fill, maxw=None, align="center", spacing=1.1, stroke=0, stroke_fill=INK):
    f = font(fpath, size)
    if isinstance(lines, str): lines = wrap(f, lines, maxw) if maxw else [lines]
    lh = int(size * spacing)
    w = int(max(tw(f, l) for l in lines)) + stroke * 2 + 4
    img = Image.new("RGBA", (w, lh * len(lines) + stroke * 2 + 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, l in enumerate(lines):
        x = stroke + 2 if align == "left" else (w - tw(f, l)) / 2
        d.text((x, i * lh + stroke), l, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    return img

def card(lines, size=56, fpath=FD, bg=NAVY, fg=WHITE, pad=(44, 34), maxw=820, radius=28, accent=None, kicker=None, kicker_fg=GOLD, align="center", serif=False):
    f = font(FSERIF if serif else fpath, size)
    if isinstance(lines, str): lines = wrap(f, lines, maxw - pad[0] * 2)
    lh = int(size * 1.12)
    kf = font(FS, 26)
    kh = 40 if kicker else 0
    w = int(max([tw(f, l) for l in lines] + ([tw(kf, kicker)] if kicker else [0]))) + pad[0] * 2
    h = lh * len(lines) + pad[1] * 2 + kh
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    rrect(d, (0, 0, w - 1, h - 1), radius, bg + (255,))
    if accent: d.rounded_rectangle((0, 0, 14, h - 1), radius=7, fill=accent + (255,))
    y = pad[1]
    if kicker:
        d.text((pad[0] if align == "left" else (w - tw(kf, kicker)) / 2, y - 6), kicker.upper(), font=kf, fill=kicker_fg + (255,)); y += kh
    for l in lines:
        x = pad[0] if align == "left" else (w - tw(f, l)) / 2
        d.text((x, y), l, font=f, fill=fg + (255,)); y += lh
    return shadowed(img)[0]

def pill(text, size=40, bg=GOLD, fg=INK, fpath=FD, pad=(30, 16), icon=None):
    f = font(fpath, size)
    iw = (size + 16) if icon else 0
    w = int(tw(f, text)) + pad[0] * 2 + iw; h = size + pad[1] * 2
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    rrect(d, (0, 0, w - 1, h - 1), h // 2, bg + (255,))
    if icon:
        ic = icon_img(icon, size + 4, fg); img.alpha_composite(ic, (pad[0] - 6, (h - ic.height) // 2))
    d.text((pad[0] + iw, pad[1] - size * 0.08), text, font=f, fill=fg + (255,))
    return shadowed(img, blur=10, off=(0, 6), alpha=90)[0]

def tag(label, value, bg=WHITE, fg=INK, vfg=GOLD_D, w=None):
    fl, fv = font(FS, 28), font(FD, 54)
    w = w or int(max(tw(fl, label), tw(fv, value))) + 64
    h = 150
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    rrect(d, (0, 0, w - 1, h - 1), 22, bg + (255,))
    d.rounded_rectangle((0, 0, w - 1, 10), radius=5, fill=GOLD + (255,))
    d.text((32, 30), label.upper(), font=fl, fill=(110, 110, 120, 255))
    d.text((32, 66), value, font=fv, fill=vfg + (255,))
    return shadowed(img)[0]

def icon_img(name, s=120, color=NAVY):
    """Simple vector icons drawn with Pillow. Returns RGBA s x s."""
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(img); c = color + (255,)
    u = s / 100
    if name == "hdb":  # wide block with windows
        d.rounded_rectangle((8 * u, 22 * u, 92 * u, 92 * u), radius=int(6 * u), fill=c)
        for r in range(4):
            for col in range(5):
                d.rectangle((16 * u + col * 15 * u, 30 * u + r * 15 * u, 24 * u + col * 15 * u, 38 * u + r * 15 * u), fill=(255, 255, 255, 230))
    elif name == "condo":  # tall tower + pool
        d.rounded_rectangle((28 * u, 6 * u, 72 * u, 82 * u), radius=int(6 * u), fill=c)
        for r in range(6):
            for col in range(2):
                d.rectangle((36 * u + col * 16 * u, 14 * u + r * 11 * u, 46 * u + col * 16 * u, 20 * u + r * 11 * u), fill=(255, 255, 255, 230))
        d.rounded_rectangle((8 * u, 84 * u, 92 * u, 94 * u), radius=int(5 * u), fill=(90, 190, 230, 255))
    elif name == "landed":
        d.polygon([(50 * u, 10 * u), (92 * u, 44 * u), (8 * u, 44 * u)], fill=c)
        d.rectangle((18 * u, 44 * u, 82 * u, 90 * u), fill=c)
        d.rectangle((42 * u, 60 * u, 58 * u, 90 * u), fill=(255, 255, 255, 230))
    elif name == "arrow_down":
        d.line([(50 * u, 10 * u), (50 * u, 80 * u)], fill=c, width=int(14 * u))
        d.polygon([(20 * u, 60 * u), (80 * u, 60 * u), (50 * u, 94 * u)], fill=c)
    elif name == "arrow_up":
        d.line([(50 * u, 90 * u), (50 * u, 20 * u)], fill=c, width=int(14 * u))
        d.polygon([(20 * u, 40 * u), (80 * u, 40 * u), (50 * u, 6 * u)], fill=c)
    elif name == "arrow_right":
        d.line([(8 * u, 50 * u), (70 * u, 50 * u)], fill=c, width=int(14 * u))
        d.polygon([(60 * u, 20 * u), (60 * u, 80 * u), (94 * u, 50 * u)], fill=c)
    elif name == "pin":
        d.ellipse((22 * u, 6 * u, 78 * u, 62 * u), fill=c)
        d.polygon([(26 * u, 50 * u), (74 * u, 50 * u), (50 * u, 94 * u)], fill=c)
        d.ellipse((38 * u, 22 * u, 62 * u, 46 * u), fill=(255, 255, 255, 255))
    elif name == "card":  # CPF card
        d.rounded_rectangle((6 * u, 22 * u, 94 * u, 78 * u), radius=int(8 * u), fill=c)
        d.rectangle((6 * u, 34 * u, 94 * u, 44 * u), fill=(255, 255, 255, 200))
        d.rounded_rectangle((16 * u, 54 * u, 46 * u, 66 * u), radius=int(3 * u), fill=GOLD + (255,))
    elif name == "shield":
        d.polygon([(50 * u, 6 * u), (90 * u, 20 * u), (84 * u, 60 * u), (50 * u, 94 * u), (16 * u, 60 * u), (10 * u, 20 * u)], fill=c)
        d.line([(34 * u, 50 * u), (46 * u, 62 * u), (68 * u, 36 * u)], fill=(255, 255, 255, 255), width=int(9 * u), joint="curve")
    elif name == "tick":
        d.line([(16 * u, 52 * u), (40 * u, 76 * u), (86 * u, 26 * u)], fill=c, width=int(14 * u), joint="curve")
    elif name == "cross":
        d.line([(20 * u, 20 * u), (80 * u, 80 * u)], fill=c, width=int(14 * u))
        d.line([(80 * u, 20 * u), (20 * u, 80 * u)], fill=c, width=int(14 * u))
    elif name == "cash":
        for i in range(3):
            d.rounded_rectangle((10 * u, (62 - i * 14) * u, 90 * u, (80 - i * 14) * u), radius=int(5 * u), fill=c, outline=(255, 255, 255, 255), width=int(3 * u))
        d.ellipse((42 * u, 42 * u, 58 * u, 58 * u), fill=(255, 255, 255, 255))
    elif name == "phone":
        d.rounded_rectangle((30 * u, 6 * u, 70 * u, 94 * u), radius=int(10 * u), fill=c)
        d.rounded_rectangle((36 * u, 16 * u, 64 * u, 78 * u), radius=int(4 * u), fill=(255, 255, 255, 230))
    elif name == "pool":
        d.rounded_rectangle((8 * u, 40 * u, 92 * u, 90 * u), radius=int(12 * u), fill=(90, 190, 230, 255))
        for i in range(3):
            d.arc((14 * u + i * 26 * u, 56 * u, 40 * u + i * 26 * u, 76 * u), 180, 360, fill=(255, 255, 255, 255), width=int(5 * u))
        d.ellipse((60 * u, 8 * u, 90 * u, 38 * u), fill=GOLD + (255,))
    elif name == "heart":
        d.ellipse((12 * u, 18 * u, 52 * u, 58 * u), fill=c); d.ellipse((48 * u, 18 * u, 88 * u, 58 * u), fill=c)
        d.polygon([(14 * u, 46 * u), (86 * u, 46 * u), (50 * u, 90 * u)], fill=c)
    elif name == "briefcase":
        d.rounded_rectangle((8 * u, 30 * u, 92 * u, 86 * u), radius=int(8 * u), fill=c)
        d.rectangle((36 * u, 16 * u, 64 * u, 30 * u), fill=c); d.rectangle((8 * u, 50 * u, 92 * u, 56 * u), fill=(255, 255, 255, 200))
    elif name == "fb":
        d.ellipse((4 * u, 4 * u, 96 * u, 96 * u), fill=(24, 119, 242, 255))
        d.text((38 * u, 14 * u), "f", font=font(FD, int(62 * u)), fill=(255, 255, 255, 255))
    elif name == "ig":
        d.rounded_rectangle((8 * u, 8 * u, 92 * u, 92 * u), radius=int(26 * u), fill=(214, 60, 130, 255))
        d.ellipse((30 * u, 30 * u, 70 * u, 70 * u), outline=(255, 255, 255, 255), width=int(8 * u))
        d.ellipse((70 * u, 20 * u, 80 * u, 30 * u), fill=(255, 255, 255, 255))
    elif name == "tt":
        d.rounded_rectangle((8 * u, 8 * u, 92 * u, 92 * u), radius=int(26 * u), fill=(16, 16, 20, 255))
        d.text((30 * u, 12 * u), "♪", font=font("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(60 * u)), fill=(105, 201, 208, 255))
    return img

def icon_card(name, label=None, s=170, bg=WHITE, color=NAVY, label_fg=INK):
    f = font(FS, 30)
    w = max(s + 40, int(tw(f, label)) + 48 if label else 0); h = s + 40 + (46 if label else 0)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    rrect(d, (0, 0, w - 1, h - 1), 26, bg + (255,))
    img.alpha_composite(icon_img(name, s, color), ((w - s) // 2, 20))
    if label: d.text(((w - tw(f, label)) / 2, s + 26), label, font=f, fill=label_fg + (255,))
    return shadowed(img)[0]

def stamp(text, size=92, color=GOLD, fg=INK, angle=-8):
    f = font(FD, size)
    w = int(tw(f, text)) + 80; h = size + 60
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    rrect(d, (0, 0, w - 1, h - 1), 20, color + (255,))
    d.text((40, 24), text, font=f, fill=fg + (255,))
    img = img.rotate(angle, expand=True, resample=Image.BICUBIC)
    return shadowed(img)[0]

def counter_img(prefix, value, suffix, size=150):
    f = font(FD, size); s = f"{prefix}{value}{suffix}"
    return text_block([s], FD, size, GOLD + (255,), stroke=8, stroke_fill=INK + (255,))

def checklist_img(items, ticked, w=800):
    f = font(FB, 38); lh = 92; pad = 34
    h = pad * 2 + lh * len(items)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    rrect(d, (0, 0, w - 1, h - 1), 28, WHITE + (255,))
    for i, it in enumerate(items):
        y = pad + i * lh
        box = (pad, y + 14, pad + 52, y + 66)
        if i < ticked:
            d.rounded_rectangle(box, radius=12, fill=GREEN + (255,)); img.alpha_composite(icon_img("tick", 44, WHITE), (pad + 4, y + 18))
        else:
            d.rounded_rectangle(box, radius=12, outline=NAVY + (255,), width=4)
        for j, l in enumerate(wrap(f, it, w - pad * 2 - 80)[:2]):
            d.text((pad + 76, y + 16 + j * 40), l, font=f, fill=NAVY + (255,))
    return shadowed(img)[0]

def compare_card(title, rows, bg=WHITE, title_bg=NAVY, w=470, highlight=None):
    ft, fr = font(FD, 36), font(FS, 31); lh = 50
    h = 90 + 24 + lh * len(rows) + 24
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    rrect(d, (0, 0, w - 1, h - 1), 26, bg + (255,))
    d.rounded_rectangle((0, 0, w - 1, 90), radius=26, fill=title_bg + (255,)); d.rectangle((0, 50, w - 1, 90), fill=title_bg + (255,))
    d.text(((w - tw(ft, title)) / 2, 24), title, font=ft, fill=WHITE + (255,))
    for i, r in enumerate(rows):
        col = (GOLD_D if (highlight is not None and i == highlight) else INK) + (255,)
        fnt = font(FD, 34) if (highlight is not None and i == highlight) else fr
        d.text((28, 104 + i * lh), r, font=fnt, fill=col)
    return shadowed(img)[0]

def lower_third(label, sub=None):
    f, fs = font(FD, 34), font(FS, 26)
    w = int(max(tw(f, label), tw(fs, sub) if sub else 0)) + 70; h = 64 + (34 if sub else 0)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    rrect(d, (0, 0, w - 1, h - 1), 14, NAVY + (235,))
    d.rectangle((0, 0, 12, h - 1), fill=GOLD + (255,))
    d.text((36, 14), label.upper(), font=f, fill=WHITE + (255,))
    if sub: d.text((36, 52), sub, font=fs, fill=GOLD + (255,))
    return img

def timeline_img(points, w=880):
    """points: list of (label_top, label_bottom). Draws dots along a bar."""
    f, fs = font(FD, 30), font(FS, 24)
    h = 190
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    rrect(d, (0, 0, w - 1, h - 1), 26, WHITE + (255,))
    n = len(points); xs = [60 + i * (w - 120) / (n - 1) for i in range(n)]
    d.line([(xs[0], 100), (xs[-1], 100)], fill=MUTED + (255,), width=8)
    for (x, (a, b)) in zip(xs, points):
        d.ellipse((x - 16, 84, x + 16, 116), fill=GOLD + (255,), outline=NAVY + (255,), width=4)
        ax = min(max(16, x - tw(f, a) / 2), w - 16 - tw(f, a)); bx = min(max(16, x - tw(fs, b) / 2), w - 16 - tw(fs, b))
        d.text((ax, 36), a, font=f, fill=NAVY + (255,))
        d.text((bx, 128), b, font=fs, fill=(110, 110, 120, 255))
    return shadowed(img)[0]

def curve_img(w=760, h=360, label_top="Nilai rumah", label_bottom="Rumah semakin tua → pertumbuhan perlahan"):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    rrect(d, (0, 0, w - 1, h - 1), 26, WHITE + (255,))
    d.text((34, 24), label_top.upper(), font=font(FS, 26), fill=(110, 110, 120, 255))
    pts = []
    for i in range(0, 101):
        x = 60 + i * (w - 120) / 100; y = 290 - 200 * (1 - math.exp(-i / 28))
        pts.append((x, y))
    d.line(pts, fill=NAVY + (255,), width=10, joint="curve")
    d.line([(60, 290), (w - 60, 290)], fill=MUTED + (255,), width=4)
    d.text((34, h - 54), label_bottom, font=font(FS, 26), fill=GOLD_D + (255,))
    return shadowed(img)[0]

def strike_card(text, progress):
    """Card with red strike-through animated by progress 0..1."""
    f = font(FD, 60)
    w = int(tw(f, text)) + 100; h = 150
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    rrect(d, (0, 0, w - 1, h - 1), 26, WHITE + (255,))
    d.text((50, 38), text, font=f, fill=NAVY + (255,))
    if progress > 0:
        d.line([(40, h // 2 + 4), (40 + (w - 80) * clamp(progress), h // 2 - 10)], fill=RED + (255,), width=16)
    return shadowed(img)[0]

def end_card(title, sub, handle="Nona Kirana · Barakah Homes Realty"):
    w, h = 940, 720
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    rrect(d, (0, 0, w - 1, h - 1), 36, CREAM + (255,))
    lb = LOGO_B.resize((300, int(300 * LOGO_B.height / LOGO_B.width)), Image.LANCZOS)
    img.alpha_composite(lb, ((w - lb.width) // 2, 40))
    y = 40 + lb.height + 10
    ft = font(FSERIF, 54)
    for l in wrap(ft, title, w - 120):
        d.text(((w - tw(ft, l)) / 2, y), l, font=ft, fill=NAVY + (255,)); y += 62
    fs = font(FS, 32); y += 10
    for l in wrap(fs, sub, w - 120):
        d.text(((w - tw(fs, l)) / 2, y), l, font=fs, fill=GOLD_D + (255,)); y += 42
    lp = LOGO_P.resize((230, int(230 * LOGO_P.height / LOGO_P.width)), Image.LANCZOS)
    img.alpha_composite(lp, ((w - lp.width) // 2, h - 70 - lp.height))
    fh = font(FM, 26); d.text(((w - tw(fh, handle)) / 2, h - 52), handle, font=fh, fill=(90, 90, 100, 255))
    return shadowed(img, blur=26, alpha=140)[0]

# ---------- captions ----------
FIX = {"lona": "Nona", "nuna": "Nona", "abderi": "upgrade", "tarab": "taraf", "jurung": "Jurong", "promnex": "PropNex", "kondor": "kondo",
       "freehost": "freehold", "siming": "swimming", "kapital": "capital", "hartaanah": "hartanah", "rp650,000": "$650,000", "rp650.000": "$650,000",
       "rp650,000.": "$650,000.", "kondor.": "kondo.", "kondor,": "kondo,", "abderi,": "upgrade,", "lona,": "Nona,", "nuna,": "Nona,", "lona.": "Nona.",
       "tarab?": "taraf?", "tarab,": "taraf,", "tarab.": "taraf.", "dolar": "dolar", "jem": "jem", "mas": "Marsiling", "ling": "", "ling.": "", "ling,": ""}
NUMLIKE = re.compile(r"[\$\d]|juta|ribu|upgrade|downgrade|cash|cpf|hdb|kondo|private|sustainab|buffer|freehold|landed", re.I)

def words_in(a, b):
    return [w for w in WORDS if w["start"] >= a - 0.05 and w["end"] <= b + 0.05 and w["word"]]

def align_words(seg):
    """Map seg['text'] (clean) onto whisper word timings within the clip; returns [{s,e,w}] on output timeline."""
    ws = words_in(seg["s"], seg["e"])
    clean = seg["text"].split()
    if not ws:
        n = len(clean); d = (seg["e"] - seg["s"]) / max(1, n)
        return [{"s": seg["off"] + i * d, "e": seg["off"] + (i + 1) * d, "w": c} for i, c in enumerate(clean)]
    starts = [max(seg["s"], w["start"]) for w in ws]; ends = [min(seg["e"], w["end"]) for w in ws]
    out = []
    nc, nw = len(clean), len(ws)
    for i, c in enumerate(clean):
        a = i * nw / nc; b = (i + 1) * nw / nc
        ja, jb = int(a), min(nw - 1, int(b - 1e-6))
        fa = a - ja; fb = b - jb
        st = starts[ja] + (ends[ja] - starts[ja]) * fa
        en = starts[jb] + (ends[jb] - starts[jb]) * min(1.0, fb)
        if en <= st: en = st + 0.15
        out.append({"s": seg["off"] + (st - seg["s"]), "e": seg["off"] + (en - seg["s"]), "w": c})
    return out

def make_captions(segments, max_words=4, max_dur=1.9):
    chunks = []
    for seg in segments:
        if seg["kind"] != "clip" or not seg.get("text"): continue
        ws = align_words(seg)
        cur = []
        for w in ws:
            if cur and (len(cur) >= max_words or w["s"] - cur[-1]["e"] > 0.7 or w["s"] - cur[0]["s"] > max_dur or cur[-1]["w"][-1] in ".?!" or (cur[-1]["w"][-1] == "," and len(cur) >= 3)):
                chunks.append(cur); cur = []
            cur.append(w)
        if cur: chunks.append(cur)
    for i, c in enumerate(chunks):
        c_start = c[0]["s"] - 0.08; c_end = c[-1]["e"] + 0.3
        if i + 1 < len(chunks): c_end = min(c_end, chunks[i + 1][0]["s"] - 0.04)
        for w in c: w["cs"], w["ce"] = c_start, c_end
    return chunks

CAP_Y = 1500
def draw_caption(frame, chunk, t, y=CAP_Y, size=66):
    f = font(FD, size); fa = font(FD, int(size * 1.1))
    words = [w["w"] for w in chunk]
    act = [(w["s"] - 0.03 <= t <= w["e"] + 0.08) for w in chunk]
    gap = 22
    widths = [tw(fa if a else f, wd) for wd, a in zip(words, act)]
    total = sum(widths) + gap * (len(words) - 1)
    if total > 960:
        size = int(size * 960 / total); f = font(FD, size); fa = font(FD, int(size * 1.1))
        widths = [tw(fa if a else f, wd) for wd, a in zip(words, act)]; total = sum(widths) + gap * (len(words) - 1)
    x = (W - total) / 2
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    rrect(d, (x - 30, y - 18, x + total + 30, y + size + 26), 22, (0, 0, 0, 150))
    for wi, wd, a in zip(words, widths, act):
        col = GOLD if (a or NUMLIKE.search(wi)) else WHITE
        if a: d.text((x, y - size * 0.06), wi, font=fa, fill=col + (255,), stroke_width=7, stroke_fill=INK + (255,))
        else: d.text((x, y), wi, font=f, fill=col + (255,), stroke_width=6, stroke_fill=INK + (255,))
        x += wd + gap
    frame.alpha_composite(layer)

# ---------- SFX ----------
SR = 48000
def _env(n, a=0.005, r=0.2):
    t = np.arange(n) / SR; e = np.minimum(1, t / a) * np.exp(-t / r); return e
def sfx(name):
    if name == "whoosh":
        n = int(SR * 0.45); x = np.random.randn(n)
        from numpy.fft import rfft, irfft
        X = rfft(x); fr = np.fft.rfftfreq(n, 1 / SR); X *= np.exp(-((np.log(fr + 1) - np.log(1800)) ** 2) / 0.6); x = irfft(X)
        t = np.arange(n) / SR; e = np.sin(np.pi * t / 0.45) ** 2; return x / np.max(np.abs(x)) * e * 0.5
    if name == "pop":
        n = int(SR * 0.12); t = np.arange(n) / SR; return np.sin(2 * np.pi * (520 - 300 * t / 0.12) * t) * _env(n, 0.002, 0.04) * 0.6
    if name == "ding":
        n = int(SR * 0.9); t = np.arange(n) / SR
        return (np.sin(2 * np.pi * 1760 * t) + 0.5 * np.sin(2 * np.pi * 2637 * t) + 0.3 * np.sin(2 * np.pi * 3520 * t)) * _env(n, 0.002, 0.25) * 0.35
    if name == "kaching":
        a = np.concatenate([sfx("ding")[: int(SR * 0.08)], sfx("ding")]); return a * 0.9
    if name == "tick":
        n = int(SR * 0.05); return np.random.randn(n) * _env(n, 0.001, 0.008) * 0.5
    if name == "thud":
        n = int(SR * 0.5); t = np.arange(n) / SR; return np.sin(2 * np.pi * (90 - 50 * t) * t) * _env(n, 0.002, 0.12) * 0.9
    if name == "buzz":
        n = int(SR * 0.35); t = np.arange(n) / SR; return np.sign(np.sin(2 * np.pi * 180 * t)) * (np.sin(2 * np.pi * 7 * t) > 0) * _env(n, 0.005, 0.3) * 0.25
    if name == "strike":
        n = int(SR * 0.25); x = np.random.randn(n); return x * _env(n, 0.002, 0.05) * 0.5
    if name == "blip":
        n = int(SR * 0.09); t = np.arange(n) / SR; return np.sin(2 * np.pi * 1200 * t) * _env(n, 0.002, 0.03) * 0.4
    if name == "sting":
        n = int(SR * 1.4); t = np.arange(n) / SR
        return (np.sin(2 * np.pi * 523 * t) + 0.6 * np.sin(2 * np.pi * 659 * t) + 0.5 * np.sin(2 * np.pi * 784 * t)) * _env(n, 0.01, 0.5) * 0.3
    if name == "ring":
        n = int(SR * 0.6); t = np.arange(n) / SR; return np.sin(2 * np.pi * 1000 * t) * (np.sin(2 * np.pi * 25 * t) > 0) * _env(n, 0.005, 0.5) * 0.3
    if name == "counter":  # rapid ticks over 1.4 s
        n = int(SR * 1.4); out = np.zeros(n); tk = sfx("tick")
        for i in range(28):
            p = int(i * SR * 0.05); out[p:p + len(tk)] += tk * (0.6 + 0.4 * i / 28)
        return out
    raise KeyError(name)

def mix_sfx(events, dur, out_wav, gain_db=-16):
    n = int(SR * (dur + 2)); out = np.zeros(n)
    for (t, name) in events:
        s = sfx(name); p = int(t * SR); out[p:p + len(s)] += s[: n - p]
    out *= 10 ** (gain_db / 20); out = np.clip(out, -1, 1)
    import wave
    w = wave.open(out_wav, "w"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out * 32767).astype(np.int16).tobytes()); w.close()


PAUSES = [tuple(map(float, l.split())) for l in open(os.path.join(SP, "dl", "sil_-27.txt")) if l.strip()]
def _fix_word(t):
    key = t.lower()
    return FIX.get(key, t)

def snap_segments(spec):
    """Snap clip boundaries into real pauses, merge clips separated by <1 s of source, keep an index map."""
    snapped = []
    for s in spec:
        if s["kind"] != "clip": snapped.append(dict(s)); continue
        a, b = s["s"], s["e"]
        cand = [p for p in PAUSES if a - 0.8 <= p[1] <= a + 0.25]
        a2 = (max(cand, key=lambda p: p[1])[1] - 0.10) if cand else a - 0.15
        cand = [p for p in PAUSES if b - 0.25 <= p[0] <= b + 1.2]
        text = s.get("text", "")
        if cand:
            p = min(cand, key=lambda p: p[0]); b2 = p[0] + min(0.30, 0.6 * (p[1] - p[0]))
            if p[0] > b + 0.4:  # words were spoken between the old end and the pause: add them to the caption text
                extra = [_fix_word(w["word"]) for w in WORDS if b - 0.05 < w["start"] < p[0] and w["word"]]
                extra = [w for w in extra if w]
                if extra: text = (text + " " + " ".join(extra)).strip()
        else:
            b2 = b + 0.3
        snapped.append(dict(s, s=round(a2, 3), e=round(b2, 3), text=text, orig_s=a, orig_e=b))
    merged, index_map = [], []
    for i, s in enumerate(snapped):
        if merged and s["kind"] == "clip" and merged[-1]["kind"] == "clip" and -1.0 <= s["s"] - merged[-1]["e"] < 1.0:
            m = merged[-1]
            m["e"] = s["e"]; m["text"] = (m.get("text", "") + " " + s.get("text", "")).strip(); m["push"] = max(m.get("push", 0), s.get("push", 0))
            index_map.append((len(merged) - 1, s["s"], s["e"]))
        else:
            merged.append(dict(s)); index_map.append((len(merged) - 1, s.get("s", 0), s.get("e", 0)))
    return merged, index_map

# ---------- base video ----------
GRADE = "colorbalance=gm=-0.12:gs=-0.06:gh=-0.04:rm=0.03,eq=contrast=1.06:saturation=1.02:brightness=0.01,vignette=PI/5"
def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0: print(r.stderr[-3000:]); raise SystemExit("ffmpeg failed")

def build_segments(spec, workdir):
    """spec: list of dicts kind=clip(s,e,zoom,push) | still(t,dur,zoom,dark). Returns segments with offsets, total dur."""
    os.makedirs(workdir, exist_ok=True)
    spec, index_map = snap_segments(spec)
    segs, off, files = [], 0.0, []
    for i, s in enumerate(spec):
        fn = os.path.join(workdir, f"seg{i:02d}.mov")
        z = s.get("zoom", 1.0); push = s.get("push", 0.0)
        key = json.dumps({k: v for k, v in s.items() if k != "text"}, sort_keys=True) + GRADE
        keyf = fn + ".key"
        if os.path.exists(fn) and os.path.exists(keyf) and open(keyf).read() == key:
            dur = s["e"] - s["s"] if s["kind"] == "clip" else s["dur"]
            segs.append(dict(s, off=off, dur=dur)); off += dur; files.append(fn); continue
        if s["kind"] == "clip":
            dur = s["e"] - s["s"]
            zoomexpr = f"{z}+{push}*t/{dur:.3f}"
            vf = (f"fps={FPS},scale=w='trunc(iw*({zoomexpr})/2)*2':h='trunc(ih*({zoomexpr})/2)*2':eval=frame,"
                  f"crop={W}:{H}:(iw-{W})/2:(ih-{H})*0.35,{GRADE},format=yuv420p")
            af = f"volume={s.get('gain', 1.0)},afade=t=in:d=0.05,afade=t=out:st={max(0, dur - 0.08):.3f}:d=0.08"
            run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s['s']:.3f}", "-i", SRC, "-t", f"{dur:.3f}", "-vf", vf, "-af", af,
                 "-c:v", "libx264", "-preset", "fast", "-crf", "15", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", fn])
        else:
            dur = s["dur"]; dark = s.get("dark", 0.0)
            png = os.path.join(workdir, f"still{i:02d}.png")
            vf0 = f"scale=w='trunc(iw*{z}/2)*2':h='trunc(ih*{z}/2)*2',crop={W}:{H}:(iw-{W})/2:(ih-{H})*0.35,{GRADE}"
            if dark: vf0 += f",eq=brightness=-{dark * 0.5:.2f}:saturation={1 - dark * 0.6:.2f}"
            run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s['t']:.3f}", "-i", SRC, "-frames:v", "1", "-vf", vf0, png])
            run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-framerate", str(FPS), "-i", png, "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                 "-t", f"{dur:.3f}", "-vf", "format=yuv420p", "-c:v", "libx264", "-preset", "fast", "-crf", "15", "-c:a", "pcm_s16le", "-shortest", fn])
        open(keyf, "w").write(key)
        segs.append(dict(s, off=off, dur=dur)); off += dur; files.append(fn)
    lst = os.path.join(workdir, "list.txt")
    open(lst, "w").write("".join(f"file '{f}'\n" for f in files))
    base = os.path.join(workdir, "base.mov")
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", base])
    for i, (ni, a, b) in enumerate(index_map):
        sg = segs[ni]
        print(f"  seg{i:02d} -> part {ni}  {sg['kind']} {sg.get('s', sg.get('t', 0)):.2f}-{sg.get('e', 0):.2f}  own {a:.2f}-{b:.2f}  out {sg['off']:.1f}", flush=True)
    return segs, off, base, index_map

def finish(base, overlay_gen, total, sfx_events, out_mp4, workdir, music=None):
    """overlay_gen(t) -> RGBA frame. Pipes frames to ffmpeg, overlays, processes audio, muxes."""
    sfxw = os.path.join(workdir, "sfx.wav"); mix_sfx(sfx_events, total, sfxw)
    aud = os.path.join(workdir, "audio.wav"); voice = os.path.join(workdir, "voice.wav")
    run(["ffmpeg", "-v", "error", "-y", "-i", base, "-af", "afftdn=nf=-28:nr=12,highpass=f=80,loudnorm=I=-15:TP=-1.5:LRA=11,aresample=48000", "-ar", "48000", "-ac", "2", voice])
    run(["ffmpeg", "-v", "error", "-y", "-i", voice, "-i", sfxw, "-filter_complex",
         "[1:a]aformat=sample_rates=48000:channel_layouts=stereo[s];[0:a][s]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]",
         "-map", "[a]", "-ar", "48000", "-ac", "2", aud])
    vd = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", aud], capture_output=True, text=True).stdout.strip())
    print(f"  audio {vd:.2f}s vs video {total:.2f}s", flush=True)
    assert abs(vd - total) < 0.3, "audio/video length mismatch"
    vid = os.path.join(workdir, "video.mp4")
    nframes = int(round(total * FPS))
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-i", base, "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "pipe:0",
                          "-filter_complex", "[0:v][1:v]overlay=format=auto:shortest=1,format=yuv420p[v]", "-map", "[v]", "-an",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-r", str(FPS), vid], stdin=subprocess.PIPE)
    for i in range(nframes):
        fr = overlay_gen(i / FPS); p.stdin.write(fr.tobytes())
        if i % 300 == 0: print(f"  frame {i}/{nframes}", flush=True)
    p.stdin.close(); p.wait()
    if p.returncode != 0: raise SystemExit("overlay encode failed")
    run(["ffmpeg", "-v", "error", "-y", "-i", vid, "-i", aud, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", out_mp4])
    print("wrote", out_mp4)

# ---------- element scheduler ----------
class Element:
    def __init__(self, t0, t1, draw): self.t0, self.t1, self.draw = t0, t1, draw
def schedule(elements, captions, t):
    frame = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for e in elements:
        if e.t0 <= t < e.t1: e.draw(frame, t - e.t0, e.t1 - e.t0)
    for c in captions:
        if c[0]["cs"] <= t < c[0]["ce"]: draw_caption(frame, c, t); break
    return frame

# convenience: static image with pop-in and fade-out
def popin(img, anchor, align="center", hold_fade=True, delay=0.0):
    def draw(frame, lt, dur):
        if lt < delay: return
        lt2 = lt - delay
        sc = pop_scale(lt2); al = fade_out(lt, dur) if hold_fade else 1.0
        paste_scaled(frame, img, anchor, sc, al, align)
    return draw

def slide_in(img, anchor, frm=(-400, 0), align="center", hold_fade=True, delay=0.0):
    def draw(frame, lt, dur):
        if lt < delay: return
        k = ease_out((lt - delay) / 0.4); al = fade_out(lt, dur) if hold_fade else 1.0
        paste_scaled(frame, img, (anchor[0] + frm[0] * (1 - k), anchor[1] + frm[1] * (1 - k)), 1.0, al, align)
    return draw

def counter(prefix, a, b, suffix, anchor, roll=1.4, size=150, fmt="{:.1f}"):
    cache = {}
    def draw(frame, lt, dur):
        k = ease_out(lt / roll); v = a + (b - a) * k
        s = fmt.format(v)
        if s not in cache: cache[s] = counter_img(prefix, s, suffix, size)
        sc = 1.0 + 0.12 * (1 - ease_out(lt / 0.3)) if lt < 0.3 else 1.0
        paste_scaled(frame, cache[s], anchor, sc, fade_out(lt, dur))
    return draw

def checklist(items, tick_times, anchor, align="lt"):
    cache = {}
    def draw(frame, lt, dur):
        n = sum(1 for tt in tick_times if lt >= tt)
        if n not in cache: cache[n] = checklist_img(items, n)
        paste_scaled(frame, cache[n], anchor, pop_scale(lt), fade_out(lt, dur), align)
    return draw

def strike(text, anchor, at=0.6):
    cache = {}
    def draw(frame, lt, dur):
        pr = round(clamp((lt - at) / 0.35), 2)
        if pr not in cache: cache[pr] = strike_card(text, pr)
        paste_scaled(frame, cache[pr], anchor, pop_scale(lt), fade_out(lt, dur))
    return draw

def typewriter(text, anchor, size=58, cps=28, maxw=860, bg=NAVY, kicker=None):
    cache = {}
    def draw(frame, lt, dur):
        n = min(len(text), int(lt * cps) + 1)
        if n not in cache: cache[n] = card(text[:n] + ("|" if n < len(text) and int(lt * 6) % 2 == 0 else ""), size=size, maxw=maxw, bg=bg, kicker=kicker, align="left")
        paste_scaled(frame, cache[n], anchor, 1.0, fade_out(lt, dur), "lt")
    return draw

def dim(amount=0.45):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, int(255 * amount)))
    def draw(frame, lt, dur):
        k = ease_out(lt / 0.4) * fade_out(lt, dur, 0.4)
        if k > 0: paste_scaled(frame, layer, (0, 0), 1.0, k, "lt")
    return draw

def preview(base, overlay_gen, times, out_jpg, cols=5):
    tiles=[]
    for t in times:
        png=out_jpg+".tmp.png"
        run(["ffmpeg","-v","error","-y","-ss",f"{t:.3f}","-i",base,"-frames:v","1",png])
        fr=Image.open(png).convert("RGBA"); fr.alpha_composite(overlay_gen(t))
        d=ImageDraw.Draw(fr); d.rectangle((0,0,160,50),fill=(0,0,0,255)); d.text((8,6),f"{t:.1f}s",font=font(FS,34),fill=(255,255,255,255))
        tiles.append(fr.convert("RGB").resize((360,640)))
    rows=(len(tiles)+cols-1)//cols
    sheet=Image.new("RGB",(cols*360,rows*640),"black")
    for i,im in enumerate(tiles): sheet.paste(im,((i%cols)*360,(i//cols)*640))
    sheet.save(out_jpg,quality=88); print("preview",out_jpg)

def progressive(build, states, anchor, align="center", hold_fade=True):
    """build(*args)->img; states=[(t_rel, args)] reveals successive versions at t_rel."""
    cache = {}
    def draw(frame, lt, dur):
        idx = max([i for i, (tt, _) in enumerate(states) if lt >= tt] or [-1])
        if idx < 0: return
        if idx not in cache: cache[idx] = build(*states[idx][1])
        first = states[0][0]
        paste_scaled(frame, cache[idx], anchor, pop_scale(lt - first), fade_out(lt, dur) if hold_fade else 1.0, align)
    return draw

def run_reel(name, spec, make_els, out):
    wd = os.path.join(SP, "work", name)
    segs, total, base, imap = build_segments(spec, wd)
    def T(i, src):
        ni = imap[i][0]; return segs[ni]["off"] + (src - segs[ni]["s"])
    def S(i):
        ni, a, b = imap[i]; return segs[ni]["off"] + ((a - segs[ni]["s"]) if segs[ni]["kind"] == "clip" else 0)
    def E(i):
        ni, a, b = imap[i]; return segs[ni]["off"] + ((b - segs[ni]["s"]) if segs[ni]["kind"] == "clip" else segs[ni]["dur"])
    print("total", round(total, 1), flush=True)
    els, sfxe = make_els(segs, T, E, S)
    caps = make_captions(segs)
    gen = lambda t: schedule(els, caps, t)
    if os.environ.get("PREVIEW"):
        ts = [float(x) for x in os.environ["PREVIEW"].split(",")]
        preview(base, gen, ts, os.path.join(wd, "preview.jpg"))
    else:
        finish(base, gen, total, sfxe, out, wd)
