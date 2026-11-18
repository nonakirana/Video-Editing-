"""Generate the 'What's your purpose?' Instagram carousel (Top New Achiever story).

Run:  python3 make_carousel.py
Output: slides/01.png ... slides/06.png  (1080x1350, IG portrait)

Layout follows the "social card" reference: profile row on top, rounded photo
card, big headline underneath with one accent line, counter pill top-right,
"Swipe" on the cover. Colours and logo are Barakah Homes Realty.

Headline markup:  *word*  -> cursive (Dancing Script),  \\n -> forced line break
                  **word** -> bold (Inter Display Bold)
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, re

W, H = 1080, 1350
NAVY = (27, 42, 63)
GOLD = (164, 122, 60)
CREAM = (246, 241, 232)
WHITE = (255, 255, 255)
MUTED = (140, 132, 120)
HANDLE = "nonakirana"
BRAND = "Barakah Homes Realty"
N = 6

HERE = os.path.dirname(os.path.abspath(__file__))
DISPLAY_B = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
DISPLAY_M = "/usr/share/fonts/opentype/inter/InterDisplay-Medium.otf"
SANS = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
SANS_B = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
CURSIVE = os.path.join(HERE, "fonts", "DancingScript.ttf")
CURSIVE_SCALE = 1.32   # cursive is drawn larger so its x-height matches Inter

P = lambda n: os.path.join(HERE, "photos", n)
OUT = os.path.join(HERE, "slides")
os.makedirs(OUT, exist_ok=True)


def font(path, size, variation=None):
    f = ImageFont.truetype(path, size)
    if variation:
        f.set_variation_by_name(variation)
    return f


def cover_crop(img, w, h, focus=(0.5, 0.5)):
    img = img.convert("RGB")
    s = max(w / img.width, h / img.height)
    img = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    x = round((img.width - w) * focus[0]); y = round((img.height - h) * focus[1])
    return img.crop((x, y, x + w, y + h))


def contain(img, w, h):
    img = img.convert("RGB")
    s = min(w / img.width, h / img.height)
    return img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)


def rounded_mask(size, r, scale=4):
    m = Image.new("L", (size[0] * scale, size[1] * scale), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, size[0] * scale - 1, size[1] * scale - 1), r * scale, fill=255)
    return m.resize(size, Image.LANCZOS)


def circle_mask(size, scale=4):
    m = Image.new("L", (size * scale, size * scale), 0)
    ImageDraw.Draw(m).ellipse((0, 0, size * scale - 1, size * scale - 1), fill=255)
    return m.resize((size, size), Image.LANCZOS)


# ---------- rich text: regular / **bold** / *cursive* ----------
TOKEN = re.compile(r"\*\*(.+?)\*\*|\*(.+?)\*|([^*]+)")


def tokens(text):
    """Split markup into (word, style) pairs, style in {'r','b','c'}."""
    out = []
    for m in TOKEN.finditer(text):
        if m.group(1) is not None: style, s = "b", m.group(1)
        elif m.group(2) is not None: style, s = "c", m.group(2)
        else: style, s = "r", m.group(3)
        for w in s.split():
            out.append((w, style))
    return out


def rich_fonts(size, base="r"):
    fr = font(DISPLAY_M if base == "r" else DISPLAY_B, size)
    fb = font(DISPLAY_B, size)
    fc = font(CURSIVE, round(size * CURSIVE_SCALE), "Bold")
    return {"r": fr, "b": fb, "c": fc}


def rich_lines(draw, text, fonts, max_w):
    """Greedy wrap of styled words; returns list of lines, each a list of (word, style)."""
    space = draw.textlength(" ", font=fonts["r"])
    lines, cur, cur_w = [], [], 0
    for w, st in tokens(text):
        ww = draw.textlength(w, font=fonts[st])
        add = ww if not cur else space + ww
        if cur and cur_w + add > max_w:
            lines.append(cur); cur, cur_w = [(w, st)], ww
        else:
            cur.append((w, st)); cur_w += add
    if cur: lines.append(cur)
    return lines


def draw_rich(draw, text, size, x, y, max_w, fill, base="r", lh=1.14, cursive_fill=None):
    """Draw markup text; words share one baseline per line. Returns y after the block."""
    fonts = rich_fonts(size, base)
    space = draw.textlength(" ", font=fonts["r"])
    asc = fonts["r"].getmetrics()[0]
    line_h = round(size * lh)
    for seg in text.split("\n"):
      for line in rich_lines(draw, seg, fonts, max_w):
        cx = x
        base_y = y + asc
        for w, st in line:
            col = cursive_fill if (st == "c" and cursive_fill) else fill
            draw.text((cx, base_y), w, font=fonts[st], fill=col, anchor="ls")
            cx += draw.textlength(w, font=fonts[st]) + space
        y += line_h
    return y


# ---------- brand pieces ----------
_logo = Image.open(P("barakah-logo.png")).convert("RGBA")
_logo = _logo.crop(_logo.getbbox())
LOGO_MARK = _logo.crop((0, 0, _logo.width, 1191))
LOGO_MARK = LOGO_MARK.crop(LOGO_MARK.getbbox())


def paste_scaled(img, src, x, y, width):
    s = width / src.width
    src = src.resize((round(src.width * s), round(src.height * s)), Image.LANCZOS)
    img.alpha_composite(src, (x, y))
    return src.size


def ig_glyph(size, color, stroke=None):
    """Instagram camera glyph, drawn at 4x and downsampled."""
    s = 4
    g = Image.new("RGBA", (size * s, size * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(g)
    st = (stroke or max(2, size // 11)) * s
    pad = st // 2 + s
    d.rounded_rectangle((pad, pad, size * s - pad, size * s - pad), radius=int(size * s * 0.27), outline=color, width=st)
    c = size * s / 2; r = size * s * 0.21
    d.ellipse((c - r, c - r, c + r, c + r), outline=color, width=st)
    dr = size * s * 0.055; dx = size * s * 0.735; dy = size * s * 0.265
    d.ellipse((dx - dr, dy - dr, dx + dr, dy + dr), fill=color)
    return g.resize((size, size), Image.LANCZOS)


def avatar(size):
    src = Image.open(P("portrait.jpg")).convert("RGB").crop((310, 70, 650, 410))
    src = src.resize((size, size), Image.LANCZOS).convert("RGBA")
    src.putalpha(circle_mask(size))
    return src


# ---------- slide template ----------
def slide(n, photo, focus, headline, accent, card_h=700, hl_size=78, footer=None, swipe=False, cta=False, fit=False, precrop=None, blur=None):
    """fit=True shows the whole photo (no crop) scaled down inside the card over a blurred fill."""
    img = Image.new("RGBA", (W, H), CREAM + (255,))
    d = ImageDraw.Draw(img)
    M = 64

    # profile row
    av = 92
    ay = 70
    img.alpha_composite(avatar(av), (M, ay))
    fh = font(SANS_B, 34)
    hx = M + av + 26
    d.text((hx, ay + 2), HANDLE, font=fh, fill=NAVY)
    gx = hx + int(d.textlength(HANDLE, font=fh)) + 14
    img.alpha_composite(ig_glyph(34, GOLD + (255,)), (gx, ay + 6))
    mw, mh = paste_scaled(img, LOGO_MARK, hx, ay + 52, 26)
    d.text((hx + mw + 10, ay + 50), BRAND, font=font(SANS, 26), fill=MUTED)

    # counter pill
    pill = font(SANS_B, 26)
    t = f"{n}/{N}"
    tw = d.textlength(t, font=pill)
    pw, ph = int(tw + 44), 50
    d.rounded_rectangle((W - M - pw, 70, W - M, 70 + ph), ph // 2, fill=NAVY)
    d.text((W - M - pw + 22, 70 + 10), t, font=pill, fill=WHITE)

    # photo card
    cy = 210
    cw = W - 2 * M
    src = Image.open(P(photo)).convert("RGB")
    if blur:   # hide logos: heavy blur + pixelate inside each box
        for box in blur:
            block = box[4] if len(box) > 4 else 18
            box = box[:4]
            region = src.crop(box)
            small = region.resize((max(1, region.width // block), max(1, region.height // block)), Image.BILINEAR)
            region = small.resize(region.size, Image.BILINEAR).filter(ImageFilter.GaussianBlur(6))
            src.paste(region, box[:2])
    if precrop:
        src = src.crop(precrop)
    if fit:
        bg = cover_crop(src, cw, card_h, (0.5, 0.3)).filter(ImageFilter.GaussianBlur(28))
        bg = Image.blend(bg, Image.new("RGB", bg.size, NAVY), 0.35).convert("RGBA")
        fg = contain(src, cw - 48, card_h - 48).convert("RGBA")
        fg.putalpha(rounded_mask(fg.size, 18))
        ph_img = bg
        fx, fy = (cw - fg.width) // 2, (card_h - fg.height) // 2
        sh = Image.new("RGBA", bg.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle((fx, fy + 8, fx + fg.width, fy + fg.height + 8), 18, fill=(0, 0, 0, 90))
        ph_img = Image.alpha_composite(ph_img, sh.filter(ImageFilter.GaussianBlur(10)))
        ph_img.alpha_composite(fg, (fx, fy))
    else:
        ph_img = cover_crop(src, cw, card_h, focus).convert("RGBA")
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((M, cy + 10, M + cw, cy + card_h + 10), 28, fill=NAVY + (28,))
    img = Image.alpha_composite(img, shadow)
    card = Image.new("RGBA", (cw, card_h), (0, 0, 0, 0))
    card.paste(ph_img, (0, 0))
    card.putalpha(rounded_mask((cw, card_h), 28))
    img.alpha_composite(card, (M, cy))
    d = ImageDraw.Draw(img)

    # headline (navy, cursive words in gold) + accent line (gold bold)
    y = cy + card_h + 56
    y = draw_rich(d, headline, hl_size, M, y, cw, NAVY, base="r", cursive_fill=GOLD)
    y = draw_rich(d, accent, hl_size, M, y, cw, GOLD, base="b")

    # footer
    fy = H - 92
    ff = font(SANS, 26)
    if footer:
        d.text((M, fy), footer, font=ff, fill=MUTED)
    if swipe:
        fs = font(SANS_B, 30)
        t = "Swipe  →"
        d.text((W - M - d.textlength(t, font=fs), fy - 4), t, font=fs, fill=NAVY)
    if cta:
        lw = 150
        s = lw / _logo.width
        lg = _logo.resize((lw, round(_logo.height * s)), Image.LANCZOS)
        img.alpha_composite(lg, (W - M - lw, H - 60 - lg.height))

    img.convert("RGB").save(os.path.join(OUT, f"{n:02d}.png"), optimize=True)


# ================= SLIDES =================
ERA_LOGO = [(80, 5, 196, 160),          # top-left agency logo on the 2016 award photo
            (890, 88, 952, 122, 6),     # "ERA" in "ERA Top New Achiever 2015"
            (900, 122, 962, 156, 6)]    # "ERA" in "ERA Top 18th Achiever 2015"

slide(1, "award-2016.jpg", (0.5, 0.5),
      "I was the *Top New Achiever*\nin my company.",
      "This is **why** I did it.",
      card_h=600, hl_size=70, blur=ERA_LOGO,
      footer="My purpose.", swipe=True)

slide(2, "family-birthday.jpg", (0.5, 0.45),
      "I came from a simple,\npoor and *broken* family.\nYour typical sad story.",
      "But I wanted to **break the cycle** and change our lives.",
      card_h=560, hl_size=58,
      footer="Where it started.")

slide(3, "family-trip.jpg", (0.5, 0.5),
      "I borrowed money from\nmy *mother* to pay for\nmy RES course.",
      "She is **my purpose** to do well.",
      card_h=600, hl_size=62,
      footer="Where my purpose began.")

slide(4, "family-hotel.jpg", (0.5, 0.0),
      "I do this for my *children.*",
      "So they never know **the struggle.**",
      card_h=760, hl_size=56,
      footer="The reason I keep going.")

slide(5, "award-2016.jpg", (0.5, 0.45),
      "I was *hungry* then.",
      "I'm **still hungry** now.",
      card_h=680, hl_size=78, precrop=(400, 200, 1000, 728), blur=ERA_LOGO,
      footer="Same fire, bigger why.")

slide(6, "family-trip.jpg", (0.5, 0.5),
      "What's *your* purpose?",
      "Tell me **in the comments.**",
      card_h=620, hl_size=78, precrop=(120, 100, 1200, 739),
      footer="Follow @nonakirana for more.", cta=True)

print("done")
