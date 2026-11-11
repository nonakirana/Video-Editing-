"""Generate the 'Behind the team photo' Instagram carousel.

Run:  python3 make_carousel.py
Output: slides/01.png ... slides/10.png  (1080x1350, IG portrait)
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
TOTAL = 10

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_IT = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
SANS_B = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"

HERE = os.path.dirname(os.path.abspath(__file__))
P = lambda n: os.path.join(HERE, "..", "recruitment-carousel", "photos", n)
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
    draw.text((64, H - 70), f"{n:02d} / {TOTAL}", font=font(SANS, 22), fill=col)
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

# ---------- story slide: framed photo on top, "what you see / what you don't" below ----------
def story_slide(n, photo, kicker, see, dont, bg=NAVY, strip_h=600, focus=(0.5, 0.35)):
    img = Image.new("RGBA", (W, H), bg + (255,))
    d = ImageDraw.Draw(img)
    dark = bg == NAVY
    ph = cover_crop(load(photo), W - 128, strip_h, focus)
    img.paste(ph, (64, 100))
    d.rectangle((64, 100, W - 64, 100 + strip_h), outline=GOLD, width=4)
    y = 100 + strip_h + 60
    d.text((64, y), kicker.upper(), font=font(SANS_B, 26), fill=GOLD); y += 40
    gold_rule(d, 64, y); y += 34
    d.text((64, y), "WHAT YOU SEE", font=font(SANS_B, 22), fill=MUTED if dark else (140, 130, 115)); y += 34
    y = draw_par(d, see, font(SERIF, 62), 64, y, W - 128, WHITE if dark else NAVY, lh=1.08)
    y += 28
    d.text((64, y), "WHAT YOU DON'T", font=font(SANS_B, 22), fill=GOLD); y += 34
    draw_par(d, dont, font(SANS, 30), 64, y, W - 128, MUTED if dark else (90, 90, 90), lh=1.38)
    footer(d, n, dark)
    save(img, n)

# ================= SLIDES =================

# 01 — cover: studio photo full width, fading into navy
img = Image.new("RGBA", (W, H), NAVY + (255,))
ph = load("studio-clapper.jpg").convert("RGB")
ph = cover_crop(ph, W, 700, (0.5, 0.55))
PH = ph.height
img.paste(ph, (0, 0))
fade = Image.new("RGBA", (W, H), NAVY + (0,))
fd = ImageDraw.Draw(fade)
fd.rectangle((0, 0, W, PH), fill=NAVY + (40,))
for i in range(170):
    fd.line((0, PH - 170 + i, W, PH - 170 + i), fill=NAVY + (40 + int(215 * (i / 170) ** 1.3),))
img = Image.alpha_composite(img, fade)
d = ImageDraw.Draw(img)
logo(img, "barakah-logo.png", 64, 60, 140, white=True)
y = PH - 40
fk = font(SANS_B, 26)
d.text((64, y), "BEHIND THE TEAM PHOTO", font=fk, fill=GOLD)
sw = "SWIPE  →"
d.text((W - 64 - d.textlength(sw, font=fk), y), sw, font=fk, fill=GOLD); y += 40
gold_rule(d, 64, y); y += 32
for line in ["Every team photo", "has a story", "you don't see."]:
    d.text((64, y), line, font=font(SERIF, 92), fill=WHITE); y += round(92 * 1.04)
y += 26
draw_par(d, "8 photos from 12 years of building a team, and what was really happening when the camera clicked.",
         font(SANS, 30), 64, y, W - 128, MUTED, lh=1.35)
footer(d, 1)
save(img, 1)

# 02–09 — the photos
story_slide(2, "teamnona-lunch.jpg", "Where it started",
    "A lunch.",
    "No office, no system. Just a few of us agreeing to help each other win. That table was #TeamNona's first boardroom.",
    focus=(0.5, 0.3))

story_slide(3, "era-days.jpg", "The ERA days",
    "A big, happy group.",
    "Half of these faces have moved on since. I still celebrate every one of them. Growth was never meant to keep everyone in one frame.",
    bg=CREAM, focus=(0.5, 0.4))

story_slide(4, "team-masks.jpg", "The pandemic years",
    "Masks and smiles.",
    "Viewings cancelled, deals slow, and nobody knew when it would end. Nobody left either. That's when I knew what we had.",
    focus=(0.5, 0.45))

story_slide(5, "team-studio-shoot.jpg", "The first studio shoot",
    "Everyone looking polished.",
    "The group chat hunting for one date that worked for all of us, and the nerves of people who had never stood under a studio light.",
    bg=CREAM, focus=(0.5, 0.6))

story_slide(6, "team-dinner.jpg", "Closing dinners",
    "A nice dinner.",
    "The months of rejections each person at this table pushed through to earn their seat. We don't celebrate the deal. We celebrate the person.",
    focus=(0.5, 0.2))

story_slide(7, "gathering.jpg", "Raya with the extended family",
    "A very full living room.",
    "Spouses, kids and parents who held the fort through late nights and weekend viewings. A team is never just the agents.",
    bg=CREAM, focus=(0.5, 0.75))

story_slide(8, "propnex-office.jpg", "The move to PropNex",
    "A new office.",
    "The hard conversations before it, and the same people choosing to walk through the new door together.",
    focus=(0.5, 0.5))

story_slide(9, "barakah-team.jpg", "Barakah Homes, today",
    "The team photo.",
    "12 years, five names, hundreds of goodbyes, and a team that still shows up for each other every single morning. Alhamdulillah.",
    bg=CREAM, focus=(0.5, 0.5))

# 10 — CTA
img = Image.new("RGBA", (W, H), NAVY + (255,))
d = ImageDraw.Draw(img)
ph = cover_crop(load("team-studio-wide.jpg"), W - 128, 520, (0.5, 0.5))
img.paste(ph, (64, 90))
d.rectangle((64, 90, W - 64, 610), outline=GOLD, width=4)
y = 680
d.text((64, y), "NEXT YEAR'S PHOTO", font=font(SANS_B, 26), fill=GOLD); y += 40
gold_rule(d, 64, y); y += 34
y = draw_par(d, "There's a seat in the next one.", font(SERIF, 76), 64, y, W - 128, WHITE, lh=1.08)
y += 26
y = draw_par(d, "If you're a realtor who wants to grow steadily, surrounded by people who genuinely want you to win, DM me \"PHOTO\". I'll reply personally.",
             font(SANS, 31), 64, y, W - 128, MUTED, lh=1.35)
lh = logo(img, "barakah-logo.png", 64, H - 215, 110, white=True)
logo(img, "propnex-logo.png", 64 + 110 + 36, H - 215 + lh // 2 - 20, 190, white=True)
footer(d, 10)
save(img, 10)
print("done")
