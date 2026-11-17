"""Generate the 'Small in a company full of champions' Instagram carousel.

Run:  python3 make_carousel.py
Output: slides/01.png ... slides/05.png  (1080x1350, IG portrait)

Layout follows the "social card" reference: profile row on top, rounded photo
card, big headline underneath with one accent line, counter pill top-right,
"Swipe" on the cover. Colours and logo are Barakah Homes Realty.
"""
from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1080, 1350
NAVY = (27, 42, 63)
GOLD = (164, 122, 60)
CREAM = (246, 241, 232)
CREAM_DEEP = (236, 228, 214)
WHITE = (255, 255, 255)
MUTED = (140, 132, 120)
HANDLE = "nonakirana"
BRAND = "Barakah Homes Realty"
N = 5

DISPLAY_B = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
DISPLAY_M = "/usr/share/fonts/opentype/inter/InterDisplay-Medium.otf"
SANS = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
SANS_B = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"

HERE = os.path.dirname(os.path.abspath(__file__))
P = lambda n: os.path.join(HERE, "photos", n)
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


def rounded_mask(size, r, scale=4):
    m = Image.new("L", (size[0] * scale, size[1] * scale), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, size[0] * scale - 1, size[1] * scale - 1), r * scale, fill=255)
    return m.resize(size, Image.LANCZOS)


def circle_mask(size, scale=4):
    m = Image.new("L", (size * scale, size * scale), 0)
    ImageDraw.Draw(m).ellipse((0, 0, size * scale - 1, size * scale - 1), fill=255)
    return m.resize((size, size), Image.LANCZOS)


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


def draw_par(draw, text, f, x, y, max_w, fill, lh=1.12):
    for line in wrap(draw, text, f, max_w):
        draw.text((x, y), line, font=f, fill=fill)
        y += round(f.size * lh)
    return y


# ---------- brand pieces ----------
_logo = Image.open(P("barakah-logo.png")).convert("RGBA")
_logo = _logo.crop(_logo.getbbox())
LOGO_MARK = _logo.crop((0, 0, _logo.width, 1191)).crop(_logo.crop((0, 0, _logo.width, 1191)).getbbox())


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
def slide(n, photo, focus, lines, accent, card_h=700, hl_size=78, footer=None, swipe=False, cta=False):
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
    # brand line with logo mark
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
    ph_img = cover_crop(Image.open(P(photo)), cw, card_h, focus).convert("RGBA")
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((M, cy + 10, M + cw, cy + card_h + 10), 28, fill=NAVY + (28,))
    img = Image.alpha_composite(img, shadow)
    card = Image.new("RGBA", (cw, card_h), (0, 0, 0, 0))
    card.paste(ph_img, (0, 0))
    card.putalpha(rounded_mask((cw, card_h), 28))
    img.alpha_composite(card, (M, cy))
    d = ImageDraw.Draw(img)

    # headline
    y = cy + card_h + 56
    f_hl = font(DISPLAY_M, hl_size)
    f_acc = font(DISPLAY_B, hl_size)
    for line in lines:
        y = draw_par(d, line, f_hl, M, y, cw, NAVY)
    y = draw_par(d, accent, f_acc, M, y, cw, GOLD)

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
        # full logo bottom-right
        lw = 150
        s = lw / _logo.width
        lg = _logo.resize((lw, round(_logo.height * s)), Image.LANCZOS)
        img.alpha_composite(lg, (W - M - lw, H - 60 - lg.height))

    img.convert("RGB").save(os.path.join(OUT, f"{n:02d}.png"), optimize=True)


# ================= SLIDES =================

slide(1, "with-leaders.jpg", (0.5, 0.42),
      ["I was a champion", "at my last agency."],
      "Here, I'm number 200.",
      card_h=660, hl_size=80,
      footer="On feeling small again.", swipe=True)

slide(2, "board-200.jpg", (0.5, 0.38),
      ["For years I was used to", "seeing my name at the top."],
      "Being a champion felt normal.",
      card_h=640, hl_size=66,
      footer="The comfortable part.")

slide(3, "trophy-stage.jpg", (0.55, 0.25),
      ["Then I joined a company", "with 500 champions."],
      "And I placed 200th.",
      card_h=660, hl_size=70,
      footer="PropNex Top 500 Producers, Q3 2026.")

slide(4, "seated.jpg", (0.5, 0.3),
      ["In a room full of champions,", "you feel small."],
      "It humbles me. And I'm grateful.",
      card_h=660, hl_size=64,
      footer="The honest part.")

slide(5, "trophy-close.jpg", (0.5, 0.3),
      ["Small keeps me hungry.", "Humble keeps me going."],
      "Not complacent. Not done.",
      card_h=640, hl_size=66,
      footer="Follow @nonakirana for the climb.", cta=True)

print("done")
