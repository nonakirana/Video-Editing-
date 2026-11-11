"""Generate the 'Buy first, or sell first?' Instagram carousel (8 slides, 1080x1350).

Run:  python3 make_carousel.py
Photos: photos/nona-*.jpg (portrait crops; swap for your own portraits, 3:4 works best)
Logos:  ../recruitment-carousel/photos/barakah-logo.png, propnex-logo.png
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, math, random

W, H = 1080, 1350
NAVY = (27, 42, 63)
DEEP = (16, 26, 41)
GOLD = (164, 122, 60)
GOLD_L = (214, 178, 112)
CREAM = (246, 241, 232)
WHITE = (255, 255, 255)
MUTED = (200, 192, 178)
INK = (40, 40, 44)
HANDLE = "@nonakirana"
NAME = "NONA KIRANA  ·  Barakah Homes @ PropNex"
TOTAL = 8

F = "/usr/share/fonts/opentype/inter/"
SANS = F + "Inter-Medium.otf"
SANS_SB = F + "Inter-SemiBold.otf"
SANS_B = F + "Inter-Bold.otf"
DISPLAY = F + "InterDisplay-ExtraBold.otf"
SERIF_IT = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"

HERE = os.path.dirname(os.path.abspath(__file__))
PH = lambda n: os.path.join(HERE, "photos", n)
LG = lambda n: os.path.join(HERE, "..", "recruitment-carousel", "photos", n)
OUT = os.path.join(HERE, "slides"); os.makedirs(OUT, exist_ok=True)

def font(p, s): return ImageFont.truetype(p, s)

def wrap(d, text, f, max_w):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= max_w: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def par(d, text, f, x, y, max_w, fill, lh=1.3):
    for line in wrap(d, text, f, max_w):
        d.text((x, y), line, font=f, fill=fill); y += round(f.size * lh)
    return y

# ---------- background: navy with a soft gold halftone, echoing the reference ----------
def background():
    img = Image.new("RGBA", (W, H), NAVY + (255,))
    # soft light from top-right
    glow = Image.new("L", (W, H), 0)
    gd = ImageDraw.Draw(glow)
    gd.ellipse((W - 700, -500, W + 500, 700), fill=70)
    glow = glow.filter(ImageFilter.GaussianBlur(220))
    img = Image.composite(Image.new("RGBA", (W, H), (46, 66, 96, 255)), img, glow)
    # halftone dots, denser/larger toward the top-right
    dots = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(dots)
    step = 16
    for y in range(8, H, step):
        for x in range(8, W, step):
            t = max(0.0, 1 - math.hypot(x - W, y) / 1300)   # 1 at top-right corner, 0 far away
            r = 1.0 + 3.2 * t
            a = int(22 + 50 * t)
            dd.ellipse((x - r, y - r, x + r, y + r), fill=GOLD_L + (a,))
    img = Image.alpha_composite(img, dots)
    return img

def rrect(d, box, r, fill=None, outline=None, width=1):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)

def header(d, n):
    d.text((64, 62), NAME, font=font(SANS_SB, 24), fill=GOLD_L)
    t = f"{n}/{TOTAL}"
    d.text((W - 64 - d.textlength(t, font=font(SANS_SB, 24)), 62), t, font=font(SANS_SB, 24), fill=GOLD_L)

def ig_icon(d, x, y, s=34, col=WHITE):
    rrect(d, (x, y, x + s, y + s), s * 0.28, outline=col, width=3)
    c = s / 2; r = s * 0.22
    d.ellipse((x + c - r, y + c - r, x + c + r, y + c + r), outline=col, width=3)
    d.ellipse((x + s * 0.72 - 2, y + s * 0.26 - 2, x + s * 0.72 + 2, y + s * 0.26 + 2), fill=col)

def bookmark(d, x, y, col=WHITE):
    d.polygon([(x, y), (x + 22, y), (x + 22, y + 30), (x + 11, y + 21), (x, y + 30)], outline=col, width=3)

def footer(d, n, right="Save for later"):
    y = H - 92
    ig_icon(d, 64, y - 2)
    d.text((112, y + 1), HANDLE, font=font(SANS_SB, 26), fill=WHITE)
    f = font(SANS_SB, 26)
    tw = d.textlength(right, font=f)
    d.text((W - 64 - tw, y + 1), right, font=f, fill=WHITE)
    if right == "Save for later":
        bookmark(d, W - 64 - tw - 40, y + 2)

def headline(d, y, bold=None, italic=None, bold2=None, size=104, iszie=None, kicker=None):
    """Bold sans line(s), then a serif italic line, optional bold line after. Returns next y."""
    if kicker:
        d.text((64, y), kicker, font=font(SANS_SB, 40), fill=GOLD_L); y += 60
    fb = font(DISPLAY, size); fi = font(SERIF_IT, iszie or int(size * 1.06))
    for line in (bold or []):
        d.text((64, y), line, font=fb, fill=WHITE); y += round(size * 1.02)
    for line in (italic or []):
        d.text((64, y + size * 0.04), line, font=fi, fill=CREAM); y += round(size * 1.02)
    for line in (bold2 or []):
        d.text((64, y), line, font=fb, fill=WHITE); y += round(size * 1.02)
    return y

def my_take(img, y, text, h=None, bottom=H - 150):
    """Gold 'My take' pill over a deep-navy card. y=None anchors the card above the footer. Returns bottom y."""
    d = ImageDraw.Draw(img)
    f = font(SANS_SB, 31)
    lines = wrap(d, text, f, W - 128 - 64)
    card_h = h or (72 + len(lines) * 42 + 36)
    if y is None: y = bottom - card_h - 26
    top = y + 26
    rrect(d, (64, top, W - 64, top + card_h), 30, fill=DEEP, outline=GOLD, width=2)
    rrect(d, (98, y, 98 + 190, y + 54), 27, fill=GOLD_L)
    d.text((98 + 95 - d.textlength("My take", font=font(SANS_B, 26)) / 2, y + 13), "My take", font=font(SANS_B, 26), fill=NAVY)
    ty = top + 52
    for line in lines:
        d.text((104, ty), line, font=f, fill=WHITE); ty += 42
    return top + card_h

def check_icon(d, cx, cy):
    d.ellipse((cx - 24, cy - 24, cx + 24, cy + 24), fill=NAVY)
    d.line([(cx - 11, cy + 1), (cx - 3, cy + 9), (cx + 12, cy - 9)], fill=GOLD_L, width=5, joint="curve")

def cross_icon(d, cx, cy):
    d.ellipse((cx - 24, cy - 24, cx + 24, cy + 24), outline=NAVY, width=4)
    d.line([(cx - 9, cy - 9), (cx + 9, cy + 9)], fill=NAVY, width=4)
    d.line([(cx - 9, cy + 9), (cx + 9, cy - 9)], fill=NAVY, width=4)

def point_cards(d, y, items, gap=16):
    """items: list of (ok: bool, text). Cream cards with icon. Returns next y."""
    f = font(SANS_SB, 31)
    for ok, text in items:
        lines = wrap(d, text, f, W - 128 - 150)
        h = 40 + len(lines) * 42
        rrect(d, (64, y, W - 64, y + h), 32, fill=CREAM)
        (check_icon if ok else cross_icon)(d, 64 + 66, y + h / 2)
        ty = y + 20
        for line in lines:
            d.text((64 + 128, ty), line, font=f, fill=INK); ty += 42
        y += h + gap
    return y

def polaroid(img, photo, x, y, pw=430, angle=-5, caption="Nona"):
    """Cream polaroid with a photo, tilted, with shadow. (x, y) is the centre."""
    ph = Image.open(PH(photo)).convert("RGB")
    iw = pw - 44; ih = round(iw * 4 / 3)
    s = max(iw / ph.width, ih / ph.height)
    ph = ph.resize((round(ph.width * s), round(ph.height * s)), Image.LANCZOS)
    ph = ph.crop(((ph.width - iw) // 2, (ph.height - ih) // 2, (ph.width - iw) // 2 + iw, (ph.height - ih) // 2 + ih))
    fh = ih + 44 + 92
    card = Image.new("RGBA", (pw, fh), CREAM + (255,))
    card.paste(ph, (22, 22))
    cd = ImageDraw.Draw(card)
    cf = font(SERIF, 40)
    cd.text(((pw - cd.textlength(caption, font=cf)) / 2, ih + 22 + 22), caption, font=cf, fill=INK)
    card = card.rotate(angle, expand=True, resample=Image.BICUBIC)
    shadow = Image.new("RGBA", card.size, (0, 0, 0, 0))
    shadow.paste((0, 0, 0, 120), (0, 0), card.split()[3])
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    px, py = round(x - card.width / 2), round(y - card.height / 2)
    img.alpha_composite(shadow, (px + 10, py + 18))
    img.alpha_composite(card, (px, py))

def save(img, n):
    img.convert("RGB").save(os.path.join(OUT, f"{n:02d}.png"), optimize=True)

# ================= SLIDES =================

# 01 — cover
img = background(); d = ImageDraw.Draw(img); header(d, 1)
polaroid(img, "nona-clapper.jpg", 810, 380, pw=400, angle=-6)
y = headline(d, 660, bold=["Buy first,"], italic=["or sell first?"], size=118)
d.text((64, y + 18), "Read this before you decide on your next move.", font=font(SANS_SB, 31), fill=MUTED)
my_take(img, None, "Get the sequence wrong and you put pressure on both your finances and your decisions.")
footer(d, 1, right="Swipe  →")
save(img, 1)

# 02 — option 1
img = background(); d = ImageDraw.Draw(img); header(d, 2)
y = headline(d, 120, kicker="Option 1:", bold=["Buy first,"], italic=["sell later"], size=92)
y = point_cards(d, y + 24, [
    (True,  "Take your time to search, renovate and move in. No rush."),
    (False, "You service two housing loans until the first home is sold."),
    (False, "You need a substantial down payment for the second property."),
    (False, "You pay the Additional Buyer's Stamp Duty upfront, and claim it back later only if you qualify."),
])
b = my_take(img, None, "Before you buy, ask yourself honestly: if my current home takes longer to sell, can I comfortably carry both?", bottom=H - 190)
d.text((64, b + 18), "ABSD remission is subject to eligibility and conditions.", font=font(SANS, 24), fill=MUTED)
footer(d, 2)
save(img, 2)

# 03 — option 2
img = background(); d = ImageDraw.Draw(img); header(d, 3)
y = headline(d, 120, kicker="Option 2:", bold=["Sell first,"], italic=["buy later"], size=92)
y = point_cards(d, y + 24, [
    (True,  "Sell calmly, at the price you actually want."),
    (False, "You may need to rent in between if the right home doesn't show up in time."),
    (False, "Prices can move up while you are still searching."),
])
# +$30,000 vs +$50,000 tiles
ty = y + 10
rrect(d, (64, ty, 500, ty + 120), 26, fill=CREAM)
rrect(d, (580, ty, W - 64, ty + 120), 26, fill=DEEP, outline=WHITE, width=3)
fbig = font(DISPLAY, 60)
d.text((64 + (436 - d.textlength("+$30,000", font=fbig)) / 2, ty + 28), "+$30,000", font=fbig, fill=NAVY)
d.text((580 + (436 - d.textlength("+$50,000", font=fbig)) / 2, ty + 28), "+$50,000", font=fbig, fill=WHITE)
d.text((540 - d.textlength("vs", font=font(SANS_B, 28)) / 2, ty + 46), "vs", font=font(SANS_B, 28), fill=GOLD_L)
d.text((64, ty + 132), "Gained on your sale", font=font(SANS, 22), fill=MUTED)
d.text((580, ty + 132), "Added to your next home", font=font(SANS, 22), fill=MUTED)
my_take(img, None, "An extra $30,000 on your sale means little if your next home now costs $50,000 more.")
footer(d, 3)
save(img, 3)

# 04 — what I usually advise
img = background(); d = ImageDraw.Draw(img); header(d, 4)
d.text((64, 150), "What I usually advise", font=font(SERIF_IT, 72), fill=GOLD_L)
y = headline(d, 250, bold=["Do both"], italic=["almost at the same time,"], bold2=["if possible."], size=96, iszie=92)
polaroid(img, "nona-pink.jpg", 820, 715, pw=330, angle=4)
# sell / buy timelines
ty = 690
for i, (lab, dashed) in enumerate([("Sell", False), ("Buy", True)]):
    yy = ty + i * 150
    d.text((64, yy), lab, font=font(SANS_SB, 30), fill=MUTED)
    ly = yy + 70
    d.ellipse((64, ly - 12, 88, ly + 12), fill=WHITE)
    if dashed:
        for x in range(96, 520, 26): d.ellipse((x, ly - 4, x + 8, ly + 4), fill=WHITE)
    else:
        d.line((88, ly, 520, ly), fill=WHITE, width=6)
    d.polygon([(520, ly - 16), (552, ly), (520, ly + 16)], fill=WHITE)
    cx = 300 if not dashed else 400
    d.ellipse((cx - 26, ly - 26, cx + 26, ly + 26), fill=WHITE)
    d.text((cx - d.textlength(str(i + 1), font=font(SANS_B, 30)) / 2, ly - 20), str(i + 1), font=font(SANS_B, 30), fill=NAVY)
my_take(img, None, "Start both processes together, but commit to each in a carefully planned order.")
footer(d, 4)
save(img, 4)

# 05 — know your numbers (reconstructed: slide 5 of the reference was not provided)
img = background(); d = ImageDraw.Draw(img); header(d, 5)
y = headline(d, 130, bold=["Know your numbers"], italic=["before you commit"], size=92)
d.text((64, y + 14), "Your sequence should follow your finances, not your feelings.", font=font(SANS_SB, 31), fill=MUTED)
y = point_cards(d, y + 90, [
    (True, "Loan eligibility: get your In-Principle Approval before you view."),
    (True, "CPF: how much goes back to your account after the sale, with accrued interest."),
    (True, "Cash on hand for the down payment, stamp duties and renovation."),
    (True, "A time buffer, in case either side takes longer than planned."),
])
my_take(img, None, "Your numbers decide your sequence. Not the other way around.")
footer(d, 5)
save(img, 5)

# 06 — start selling and searching together
img = background(); d = ImageDraw.Draw(img); header(d, 6)
y = headline(d, 130, bold=["Start selling and"], italic=["searching together"], size=90)
y = par(d, "Market your current home while you view your next one.", font(SANS_SB, 36), 64, y + 40, W - 128, WHITE, lh=1.3)
y = par(d, "You'll learn what your home can really fetch, and what your budget can really buy.", font(SANS, 31), 64, y + 18, W - 128, MUTED, lh=1.35)
# balance scale
cx, top = W // 2, 650
d.ellipse((cx - 12, top - 12, cx + 12, top + 12), fill=WHITE)
d.line((cx, top, cx, top + 220), fill=WHITE, width=6)
d.line((cx - 140, top + 220, cx + 140, top + 220), fill=WHITE, width=6)
lx, rx = cx - 330, cx + 330
d.line((lx, top + 60, cx, top, rx, top - 30), fill=WHITE, width=6, joint="curve")   # slightly tipped
for px, py in ((lx, top + 60), (rx, top - 30)):
    d.line((px, py, px, py + 60), fill=WHITE, width=6)
    d.line((px - 90, py + 60, px + 90, py + 60), fill=WHITE, width=6)
    d.chord((px - 90, py + 10, px + 90, py + 110), 0, 180, outline=WHITE, width=6)
d.text((lx - 90, top + 180), "Selling price", font=font(SANS_SB, 28), fill=MUTED)
d.text((rx - 150, top + 180), "Next home price", font=font(SANS_SB, 28), fill=MUTED)
my_take(img, None, "Balance your realistic selling price against your next home's price and growth potential. Count the cost of waiting, too.")
footer(d, 6)
save(img, 6)

# 07 — coordinate your timeline
img = background(); d = ImageDraw.Draw(img); header(d, 7)
y = headline(d, 130, bold=["Coordinate your"], italic=["timeline carefully"], size=90)
y = par(d, "It's not only about selling and buying.", font(SANS_SB, 36), 64, y + 40, W - 128, WHITE, lh=1.3)
y = par(d, "Plan when your sale proceeds come in, when you collect keys, when you renovate, and when you move.", font(SANS, 31), 64, y + 18, W - 128, MUTED, lh=1.35)
steps = ["Sale proceeds", "Keys", "Renovate", "Move in"]
pills = ["Money in", "Payment", "Payment", None]
ly = 850; xs = [150, 410, 670, 930]
d.line((xs[0], ly, xs[-1], ly), fill=WHITE, width=6)
for x, s, p in zip(xs, steps, pills):
    d.ellipse((x - 24, ly - 24, x + 24, ly + 24), fill=NAVY, outline=WHITE, width=6)
    f = font(SANS_SB, 28)
    d.text((x - d.textlength(s, font=f) / 2, ly - 80), s, font=f, fill=WHITE)
    if p:
        fp = font(SANS_B, 26); tw = d.textlength(p, font=fp)
        box = (x - tw / 2 - 26, ly + 56, x + tw / 2 + 26, ly + 112)
        if p == "Money in": rrect(d, box, 28, fill=CREAM); col = NAVY
        else: rrect(d, box, 28, fill=DEEP, outline=WHITE, width=3); col = WHITE
        d.text((x - tw / 2, ly + 70), p, font=fp, fill=col)
my_take(img, None, "You may have enough money overall. But will it be in your hands when each payment is due?")
footer(d, 7)
save(img, 7)

# 08 — CTA
img = background(); d = ImageDraw.Draw(img); header(d, 8)
y = headline(d, 150, bold=["Plan your", "next move with"], italic=["confidence."], size=104)
d.text((64, y + 18), "Every family's situation is different.", font=font(SANS_SB, 31), fill=MUTED)
polaroid(img, "nona-white.jpg", 800, 900, pw=400, angle=-4)
rrect(d, (64, 860, 520, 1080), 30, fill=CREAM)
yy = par(d, "DM me \"MOVE\" and I'll map out your sequence with you.", font(SANS_B, 31), 96, 892, 392, INK, lh=1.3)
d.line((96, yy + 30, 176, yy + 30), fill=INK, width=4)
d.polygon([(166, yy + 18), (184, yy + 30), (166, yy + 42)], fill=INK)
# logos, bottom-left above footer
lg = Image.open(LG("barakah-logo.png")).convert("RGBA"); lg = lg.crop(lg.getbbox())
s = 96 / lg.width; lg = lg.resize((96, round(lg.height * s)), Image.LANCZOS)
a = lg.split()[3]; lw = Image.new("RGBA", lg.size, WHITE + (255,)); lw.putalpha(a)
img.alpha_composite(lw, (64, 1118))
footer(d, 8)
save(img, 8)
print("done")
