"""Generate the '12 Years of Building Teams' Instagram carousel.

Run:  python3 make_carousel.py
Output: slides/01.png ... slides/12.png  (1080x1350, IG portrait)
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

W, H = 1080, 1350
NAVY = (27, 42, 63)
GOLD = (164, 122, 60)
CREAM = (246, 241, 232)
WHITE = (255, 255, 255)
MUTED = (200, 192, 178)
HANDLE = "@nonakirana"

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_IT = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
SANS_B = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"

HERE = os.path.dirname(os.path.abspath(__file__))
P = lambda n: os.path.join(HERE, "photos", n)
# Pre-crop boxes: these photos carry baked-in story text/bands we don't want on a slide.
PRECROP = {"teamnona-lunch.jpg": (0, 123, 1440, 1110),
           "era-days.jpg": (0, 161, 1440, 833),
           "team-dinner.jpg": (0, 0, 1440, 700)}
def load(n):
    im = Image.open(P(n))
    return im.crop(PRECROP[n]) if n in PRECROP else im
OUT = os.path.join(HERE, "slides")
os.makedirs(OUT, exist_ok=True)

def font(path, size):
    return ImageFont.truetype(path, size)

def cover_crop(img, w, h, focus=(0.5, 0.5)):
    img = img.convert("RGB")
    s = max(w / img.width, h / img.height)
    img = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    x = round((img.width - w) * focus[0]); y = round((img.height - h) * focus[1])
    return img.crop((x, y, x + w, y + h))

def wrap(draw, text, f, max_w):
    lines, cur = [], ""
    for word in text.split():
        t = (cur + " " + word).strip()
        if draw.textlength(t, font=f) <= max_w:
            cur = t
        else:
            lines.append(cur); cur = word
    if cur: lines.append(cur)
    return lines

def draw_par(draw, text, f, x, y, max_w, fill, lh=1.18, align="left"):
    for line in wrap(draw, text, f, max_w):
        lx = x if align == "left" else x + (max_w - draw.textlength(line, font=f)) / 2
        draw.text((lx, y), line, font=f, fill=fill)
        y += round(f.size * lh)
    return y

def gradient_overlay(base, top_alpha=40, bottom_alpha=235, start=0.25, color=NAVY):
    """Darken photo from `start` (fraction of height) to bottom."""
    ov = Image.new("RGBA", (W, H), color + (0,))
    px = ov.load()
    y0 = int(H * start)
    for y in range(H):
        if y < y0:
            a = top_alpha
        else:
            t = (y - y0) / (H - y0)
            a = int(top_alpha + (bottom_alpha - top_alpha) * (t ** 1.4))
        for x in range(W):
            px[x, y] = color + (a,)
    return Image.alpha_composite(base.convert("RGBA"), ov)

def logo(img, which, x, y, width, white=False):
    lg = Image.open(P(which)).convert("RGBA")
    if which == "barakah-logo.png":
        lg = lg.crop(lg.getbbox())
    s = width / lg.width
    lg = lg.resize((round(lg.width * s), round(lg.height * s)), Image.LANCZOS)
    if white:
        a = lg.split()[3]
        lg = Image.new("RGBA", lg.size, WHITE + (255,)); lg.putalpha(a)
    img.alpha_composite(lg, (x, y))
    return lg.height

def footer(draw, n, dark_bg=True):
    col = MUTED if dark_bg else GOLD
    draw.text((64, H - 70), f"{n:02d} / 12", font=font(SANS, 22), fill=col)
    t = HANDLE
    draw.text((W - 64 - draw.textlength(t, font=font(SANS, 22)), H - 70), t, font=font(SANS, 22), fill=col)

def gold_rule(draw, x, y, w=90, t=5):
    draw.rectangle((x, y, x + w, y + t), fill=GOLD)

def save(img, n):
    img.convert("RGB").save(os.path.join(OUT, f"{n:02d}.png"), optimize=True)

# ---------- photo slide: photo bg, text block at bottom ----------
def photo_slide(n, photo, kicker, headline, body=None, focus=(0.5, 0.4), hl_size=74, body_size=32):
    base = cover_crop(load(photo), W, H, focus)
    img = gradient_overlay(base, start=0.3)
    d = ImageDraw.Draw(img)
    fk, fh, fb = font(SANS_B, 26), font(SERIF, hl_size), font(SANS, body_size)
    # measure block from the bottom up
    hl_lines = wrap(d, headline, fh, W - 128)
    body_lines = wrap(d, body, fb, W - 128) if body else []
    block = 30 + 40 + len(hl_lines) * round(hl_size * 1.1) + (24 + len(body_lines) * round(body_size * 1.35) if body else 0)
    y = H - 130 - block
    d.text((64, y), kicker.upper(), font=fk, fill=GOLD, spacing=4); y += 40
    gold_rule(d, 64, y); y += 30
    y = draw_par(d, headline, fh, 64, y, W - 128, WHITE, lh=1.1)
    if body:
        y += 24
        draw_par(d, body, fb, 64, y, W - 128, MUTED, lh=1.35)
    footer(d, n)
    save(img, n)

# ---------- text slide: solid bg, big statement ----------
def text_slide(n, kicker, headline, body=None, bg=NAVY, hl_size=84, photo_strip=None, strip_h=440, focus=(0.5, 0.35)):
    img = Image.new("RGBA", (W, H), bg + (255,))
    d = ImageDraw.Draw(img)
    dark = bg == NAVY
    fk, fh, fb = font(SANS_B, 26), font(SERIF, hl_size), font(SANS, 32)
    y = 150
    if photo_strip:
        ph = cover_crop(load(photo_strip), W - 128, strip_h, focus)
        img.paste(ph, (64, 110))
        d.rectangle((64, 110, W - 64, 110 + strip_h), outline=GOLD, width=4)
        y = 110 + strip_h + 70
    d.text((64, y), kicker.upper(), font=fk, fill=GOLD); y += 40
    gold_rule(d, 64, y); y += 36
    y = draw_par(d, headline, fh, 64, y, W - 128, WHITE if dark else NAVY, lh=1.1)
    if body:
        y += 30
        draw_par(d, body, fb, 64, y, W - 128, MUTED if dark else (90, 90, 90), lh=1.4)
    footer(d, n, dark)
    save(img, n)

# ================= SLIDES =================

# 01 — cover
base = cover_crop(load("studio-clapper.jpg"), W, H, (0.5, 0.45))
img = gradient_overlay(base, top_alpha=110, bottom_alpha=250, start=0.3)
# soft navy band behind the text block (fades in over 90px above y=660)
band = Image.new("RGBA", (W, H), NAVY + (0,))
bd = ImageDraw.Draw(band)
for i in range(90):
    bd.line((0, 570 + i, W, 570 + i), fill=NAVY + (int(130 * i / 90),))
bd.rectangle((0, 660, W, H), fill=NAVY + (130,))
img = Image.alpha_composite(img, band)
d = ImageDraw.Draw(img)
logo(img, "barakah-logo.png", 64, 70, 150, white=True)
fh = font(SERIF, 84)
y = 690
fk = font(SANS_B, 26)
d.text((64, y), "12 YEARS OF BUILDING TEAMS", font=fk, fill=GOLD)
sw = "SWIPE  →"
d.text((W - 64 - d.textlength(sw, font=fk), y), sw, font=fk, fill=GOLD); y += 40
gold_rule(d, 64, y); y += 32
for line in ["Still growing.", "Still recruiting.", "Still just", "getting started."]:
    d.text((64, y), line, font=fh, fill=WHITE); y += round(84 * 1.04)
y += 24
draw_par(d, "12 years of building teams, and what they taught me about leading people forward.", font(SANS, 30), 64, y, W - 128, MUTED, lh=1.35)
footer(d, 1)
save(img, 1)

# 02 — how it started
text_slide(2, "How it started", "12 years ago I recruited my first agent.",
    "No system, no playbook. Just a belief that if I helped people win, we would all win together. That was the start of #TeamNona.",
    photo_strip="teamnona-lunch.jpg", strip_h=600, focus=(0.5, 0.3), hl_size=68)

# 03 — the journey (timeline over studio-wide photo)
base = cover_crop(load("team-studio-shoot.jpg"), W, H, (0.5, 0.5))
img = gradient_overlay(base, top_alpha=160, bottom_alpha=245, start=0.15)
d = ImageDraw.Draw(img)
y = 120
d.text((64, y), "THE JOURNEY", font=font(SANS_B, 26), fill=GOLD); y += 40
gold_rule(d, 64, y); y += 34
y = draw_par(d, "One team. Five names. Same heart.", font(SERIF, 74), 64, y, W - 128, WHITE, lh=1.08)
y += 50
steps = [("TeamNona", "Where it all began"),
         ("Nona Kirana & Associates", "First time putting my name on the door"),
         ("NKD · Nona Kirana Division", "From a team to a division"),
         ("Nona Kirana District", "Bigger reach, bigger responsibility"),
         ("Barakah Homes", "Where we are today, Alhamdulillah")]
ft, fs = font(SERIF, 44), font(SANS, 26)
lx = 90
d.line((lx, y + 10, lx, y + len(steps) * 118 - 60), fill=GOLD, width=3)
for i, (t, s) in enumerate(steps):
    cy = y + i * 118
    r = 13 if i < len(steps) - 1 else 18
    d.ellipse((lx - r, cy + 14 - r, lx + r, cy + 14 + r), fill=GOLD if i == len(steps) - 1 else NAVY, outline=GOLD, width=3)
    d.text((lx + 44, cy - 6), t, font=ft, fill=WHITE)
    d.text((lx + 44, cy + 48), s, font=fs, fill=MUTED)
footer(d, 3)
save(img, 3)

# 04 — people come and go
text_slide(4, "The honest part", "People come and people go.",
    "Some stayed a season. Some stayed a decade. Some left and came back. Every single one taught me something, and I am grateful for all of them.",
    photo_strip="era-days.jpg", bg=CREAM, hl_size=76)

# 05–10 — lessons
text_slide(5, "Lesson 01", "Manage expectations early.",
    "Theirs and mine. Most disappointment in a team comes from things that were never said out loud. Say them.",
    photo_strip="team-masks.jpg", hl_size=76)

text_slide(6, "Lesson 02", "Listen. Take feedback constructively.",
    "Not every piece of feedback is comfortable. But the team that tells you the truth is a team that still cares.",
    bg=CREAM, hl_size=76)

text_slide(7, "Lesson 03", "Know when to empathise, and when to be firm.",
    "Both are love. Kindness without standards builds comfort, not growth.",
    photo_strip="team-studio-wide.jpg", hl_size=70)

text_slide(8, "Lesson 04", "Make the decision that won't please everyone.",
    "If it is for the betterment of the team, make it. Then stand by it, and explain it with respect.",
    bg=CREAM, hl_size=72)

text_slide(9, "Lesson 05", "Be willing to listen and agree, even before you fully understand.",
    "Trust is built in the moments you choose to back your people first and ask your questions after.",
    photo_strip="propnex-lobby.jpg", focus=(0.5, 0.3), hl_size=62)

text_slide(10, "Lesson 06", "Lead by example, and with integrity.",
    "Your team will never do what you say. They will do what you do. Especially when you think nobody is watching.",
    bg=CREAM, hl_size=76)

# 11 — today: Barakah Homes
base = cover_crop(load("propnex-office.jpg"), W, H, (0.55, 0.5))
img = gradient_overlay(base, top_alpha=60, bottom_alpha=240, start=0.3)
d = ImageDraw.Draw(img)
y = 760
d.text((64, y), "TODAY", font=font(SANS_B, 26), fill=GOLD); y += 40
gold_rule(d, 64, y); y += 30
y = draw_par(d, "Barakah Homes, at PropNex.", font(SERIF, 76), 64, y, W - 128, WHITE, lh=1.1)
y += 24
y = draw_par(d, "A new name, the same mission: build a team where people grow, earn well, and do this business with barakah.",
             font(SANS, 32), 64, y, W - 128, MUTED, lh=1.35)
y += 40
h = logo(img, "barakah-logo.png", 64, y, 120, white=True)
logo(img, "propnex-logo.png", 64 + 120 + 40, y + h // 2 - 22, 210, white=True)
footer(d, 11)
save(img, 11)

# 12 — CTA
img = Image.new("RGBA", (W, H), CREAM + (255,))
d = ImageDraw.Draw(img)
ph = cover_crop(load("barakah-team.jpg"), W - 128, 520, (0.5, 0.5))
img.paste(ph, (64, 90))
d.rectangle((64, 90, W - 64, 610), outline=GOLD, width=4)
y = 680
d.text((64, y), "I AM STILL RECRUITING", font=font(SANS_B, 26), fill=GOLD); y += 40
gold_rule(d, 64, y); y += 34
y = draw_par(d, "12 years in, I still want to see people grow.", font(SERIF, 74), 64, y, W - 128, NAVY, lh=1.08)
y += 26
y = draw_par(d, "If you are a salesperson looking for a team that will push you, back you and tell you the truth, let's talk. DM me \"GROW\" and I'll reach out.",
             font(SANS, 32), 64, y, W - 128, (90, 90, 90), lh=1.35)
lh = logo(img, "barakah-logo.png", 64, H - 215, 110)
logo(img, "propnex-logo.png", 64 + 110 + 36, H - 215 + lh // 2 - 20, 190)
footer(d, 12, dark_bg=False)
save(img, 12)
print("done")
