"""Generate the 'Sell first or buy first? Wrong question.' Instagram carousel (8 slides, 1080x1350).

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
        if isinstance(ok, str):
            cx, cy = 64 + 66, y + h / 2
            d.ellipse((cx - 24, cy - 24, cx + 24, cy + 24), fill=GOLD_L)
            fnum = font(SANS_B, 26)
            d.text((cx - d.textlength(ok, font=fnum) / 2, cy - 16), ok, font=fnum, fill=NAVY)
        else:
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
    fh = ih + 44 + 56
    card = Image.new("RGBA", (pw, fh), CREAM + (255,))
    card.paste(ph, (22, 22))
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
polaroid(img, "nona-desk-consult.jpg", 800, 395, pw=340, angle=-6)
y = headline(d, 596, bold=["Sell first or", "buy first?"], italic=["Wrong question."], size=100)
d.text((64, y + 16), "Here's the question that actually matters.", font=font(SANS_SB, 31), fill=MUTED)
my_take(img, None, "Upgrading stress is rarely about price. It's about timing.")
footer(d, 1, right="Swipe  →")
save(img, 1)

# 02 — the real question: the gap
img = background(); d = ImageDraw.Draw(img); header(d, 2)
polaroid(img, "nona-walkthrough.jpg", 880, 330, pw=260, angle=5)
y = headline(d, 120, kicker="The real question:", bold=["Can you"], italic=["afford the gap?"], size=92)
y = par(d, "Three gaps open up between two homes.", font(SANS_SB, 31), 64, y + 24, 620, MUTED, lh=1.35)
y = point_cards(d, y + 36, [
    ("1", "Cash gap: new down payment due before your sale money arrives."),
    ("2", "Loan gap: months of paying two mortgages."),
    ("3", "Time gap: where you live if the keys don't line up."),
])
my_take(img, None, "Choosing the order is really choosing which gap you can live with.")
footer(d, 2)
save(img, 2)

# 03 — if you buy first
img = background(); d = ImageDraw.Draw(img); header(d, 3)
y = headline(d, 120, kicker="If you buy first", bold=["Buying first"], italic=["buys you time."], size=92)
y = point_cards(d, y + 24, [
    (True,  "You can hold two homes for a few months."),
    (True,  "No move in between. No disruption for the kids."),
    (False, "ABSD upfront. Refundable only if the first home sells in time."),
    (False, "Two mortgages until your sale completes."),
])
b = my_take(img, None, "Buy first only if a slow sale won't cost you sleep.", bottom=H - 190)
d.text((64, b + 18), "ABSD remission is subject to IRAS eligibility and conditions.", font=font(SANS, 24), fill=MUTED)
footer(d, 3)
save(img, 3)

# 04 — if you sell first
img = background(); d = ImageDraw.Draw(img); header(d, 4)
y = headline(d, 120, kicker="If you sell first", bold=["Selling first"], italic=["buys you clarity."], size=92)
y = point_cards(d, y + 24, [
    (True,  "Your sale funds the next down payment."),
    (True,  "A confirmed budget before you fall for a unit."),
    (False, "Temporary housing and two moves, unless you negotiate an extension of stay."),
    (False, "Prices may rise while you search."),
])
my_take(img, None, "The calmer route, if you've planned where to live in between.")
footer(d, 4)
save(img, 4)

# 05 — an overlap, not a gap
img = background(); d = ImageDraw.Draw(img); header(d, 5)
y = headline(d, 120, kicker="What I aim for with my clients", bold=["An overlap,"], italic=["not a gap."], size=96)
y = par(d, "Secure your buyer. Then commit to your purchase, with dates that line up.", font(SANS, 31), 64, y + 24, 600, MUTED, lh=1.35)
polaroid(img, "nona-condo-viewing.jpg", 895, 800, pw=270, angle=4)
by = y + 60
rrect(d, (64, by, 600, by + 60), 30, fill=CREAM)
d.text((96, by + 14), "SELL", font=font(SANS_B, 26), fill=NAVY)
d.text((190, by + 17), "offer  →  exercise  →  complete", font=font(SANS, 23), fill=INK)
rrect(d, (330, by + 84, 720, by + 144), 30, fill=DEEP, outline=GOLD_L, width=3)
d.text((362, by + 98), "BUY", font=font(SANS_B, 26), fill=WHITE)
d.text((446, by + 101), "exercise  →  complete", font=font(SANS, 23), fill=MUTED)
# the overlap band
d.rectangle((330, by - 12, 600, by + 156), outline=GOLD_L, width=2)
d.text((330, by + 166), "the overlap", font=font(SANS_SB, 22), fill=GOLD_L)
# milestones
ly = by + 270
xs = [100, 280, 460, 640]
d.line((xs[0], ly, xs[-1], ly), fill=WHITE, width=4)
for x, lab in zip(xs, ["Offer on\nyour sale", "Exercise\nyour purchase", "Sale\ncompletes", "Purchase\ncompletes"]):
    d.ellipse((x - 14, ly - 14, x + 14, ly + 14), fill=NAVY, outline=WHITE, width=4)
    for i, line in enumerate(lab.split("\n")):
        f = font(SANS_SB, 21)
        d.text((x - d.textlength(line, font=f) / 2, ly + 28 + i * 26), line, font=f, fill=MUTED)
my_take(img, None, "Sale money in before purchase money is due. Everything else is detail.")
footer(d, 5)
save(img, 5)

# 06 — four numbers
img = background(); d = ImageDraw.Draw(img); header(d, 6)
y = headline(d, 120, kicker="Before anyone signs", bold=["Four numbers"], italic=["I check first."], size=92)
y = point_cards(d, y + 24, [
    ("1", "Net proceeds, after the loan, CPF refund and fees."),
    ("2", "Loan room, from an actual In-Principle Approval."),
    ("3", "Cash needed: down payment, stamp duty, legal, renovation."),
    ("4", "Monthly commitment after the move, with a buffer."),
])
my_take(img, None, "If it doesn't work on paper, it won't work in real life.")
footer(d, 6)
save(img, 6)

# 07 — three mistakes
img = background(); d = ImageDraw.Draw(img); header(d, 7)
y = headline(d, 120, kicker="I see these every month", bold=["Three upgrading"], italic=["mistakes."], size=92)
y = point_cards(d, y + 24, [
    (False, "Viewing new launches before knowing what your home can fetch."),
    (False, "Assuming your home sells in a month. Plan for three."),
    (False, "Forgetting the in-between costs: rental, two moves, storage."),
])
my_take(img, None, "Not the wrong home. The wrong order.")
footer(d, 7)
save(img, 7)

# 08 — CTA
img = background(); d = ImageDraw.Draw(img); header(d, 8)
y = headline(d, 150, bold=["Plan the order,"], italic=["then the home."], size=100)
d.text((64, y + 18), "Every family's numbers are different.", font=font(SANS_SB, 31), fill=MUTED)
polaroid(img, "nona-cafe-consult.jpg", 800, 880, pw=400, angle=-4)
rrect(d, (64, 820, 520, 1080), 30, fill=CREAM)
yy = par(d, "DM me \"SEQUENCE\" and we'll map out your order together.", font(SANS_B, 30), 96, 850, 392, INK, lh=1.3)
d.line((96, yy + 26, 176, yy + 26), fill=INK, width=4)
d.polygon([(166, yy + 14), (184, yy + 26), (166, yy + 38)], fill=INK)
lg = Image.open(LG("barakah-logo.png")).convert("RGBA"); lg = lg.crop(lg.getbbox())
sc = 96 / lg.width; lg = lg.resize((96, round(lg.height * sc)), Image.LANCZOS)
a = lg.split()[3]; lw = Image.new("RGBA", lg.size, WHITE + (255,)); lw.putalpha(a)
img.alpha_composite(lw, (64, 1118))
footer(d, 8)
save(img, 8)
print("done")
