import sys, os, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reelkit import *
OUTD = "/home/user/Video-Editing-/reels-upgrade-talk/covers"; os.makedirs(OUTD, exist_ok=True)
CAND = os.path.join(SP, "covers", "cand")
def still(t): return Image.open(os.path.join(CAND, f"f_{t:06.1f}.png")).convert("RGBA")
def gradient(img, y0=700, strength=190):
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); px = g.load()
    for y in range(y0, H):
        a = int(strength * ((y - y0) / (H - y0)) ** 0.9)
        for x in range(0, W, 1): px[x, y] = (10, 14, 22, a)
    return Image.alpha_composite(img, g)
def logo_strip(img, light=True):
    lb = LOGO_B.resize((170, int(170 * LOGO_B.height / LOGO_B.width)), Image.LANCZOS)
    if light:  # white version for dark background: use alpha as mask
        a = lb.split()[3]; lb = Image.new("RGBA", lb.size, (255, 255, 255, 0)); lb.putalpha(a)
    img.alpha_composite(lb, ((W - lb.width) // 2, H - 150 - lb.height))
    f = font(FM, 26); d = ImageDraw.Draw(img); t = "Nona Kirana · Barakah Homes Realty"
    d.text(((W - tw(f, t)) / 2, H - 130), t, font=f, fill=(255, 255, 255, 230) if light else NAVY + (255,))
    return img
def center(img, el, y): img.alpha_composite(el, ((W - el.width) // 2, y))

def style_bold(t, kicker, lines, gold_idx, y=940):
    img = gradient(still(t), 800); d = ImageDraw.Draw(img)
    f = font(FD, 112); fk = font(FS, 34)
    d.text(((W - tw(fk, kicker)) / 2, y), kicker.upper(), font=fk, fill=GOLD + (255,))
    yy = y + 60
    for i, l in enumerate(lines):
        fz = f if tw(f, l) <= 960 else font(FD, int(112 * 960 / tw(f, l)))
        d.text(((W - tw(fz, l)) / 2, yy), l, font=fz, fill=(GOLD if i in gold_idx else WHITE) + (255,), stroke_width=4, stroke_fill=INK + (255,))
        yy += int(fz.size * 1.08)
    return logo_strip(img)
def style_card(t, kicker, text, size=76, y=860):
    img = still(t); c = card(text, size=size, kicker=kicker, maxw=940, bg=NAVY); center(img, c, y); return logo_strip(img)
def style_number(t, big, sub, y=900, big_size=230):
    img = gradient(still(t), 760, 210); d = ImageDraw.Draw(img)
    f = font(FD, big_size)
    if tw(f, big) > 980: f = font(FD, int(big_size * 980 / tw(f, big)))
    d.text(((W - tw(f, big)) / 2, y), big, font=f, fill=GOLD + (255,), stroke_width=8, stroke_fill=INK + (255,))
    fs = font(FD, 60); yy = y + int(f.size * 1.05)
    for l in wrap(fs, sub, 940):
        d.text(((W - tw(fs, l)) / 2, yy), l, font=fs, fill=WHITE + (255,), stroke_width=4, stroke_fill=INK + (255,)); yy += 70
    return logo_strip(img)
def style_quote(t, text, kicker="Nona Kirana", y=840):
    img = still(t); f = font(FSERIF, 72); lines = wrap(f, text, 860)
    h = 60 + 40 + len(lines) * 84 + 50
    band = Image.new("RGBA", (W - 100, h), CREAM + (255,)); d = ImageDraw.Draw(band)
    d.rectangle((0, 0, W - 100, 12), fill=GOLD + (255,))
    fk = font(FS, 28); d.text((50, 44), kicker.upper(), font=fk, fill=GOLD_D + (255,))
    yy = 100
    for l in lines: d.text((50, yy), l, font=f, fill=NAVY + (255,)); yy += 84
    sh, pad = shadowed(band, blur=24, alpha=130); img.alpha_composite(sh, (50 - pad, y - pad)); return logo_strip(img)
def style_band(t, text, sub=None, y=880):
    img = still(t); f = font(FD, 84); lines = wrap(f, text, 940)
    h = 50 + len(lines) * 94 + (60 if sub else 0) + 40
    band = Image.new("RGBA", (W, h), GOLD + (255,)); d = ImageDraw.Draw(band)
    yy = 40
    for l in lines: d.text(((W - tw(f, l)) / 2, yy), l, font=f, fill=NAVY + (255,)); yy += 94
    if sub:
        fs = font(FS, 36); d.text(((W - tw(fs, sub)) / 2, yy + 8), sub, font=fs, fill=NAVY + (230,))
    img.alpha_composite(band, (0, y)); return logo_strip(img)

covers = {
 1: [("bold", 146.5, dict(kicker="Kisah sebenar", lines=["Nak", "DOWNGRADE…", "jadi +$500k"], gold_idx=[2])),
     ("card", 125.4, dict(kicker="Kisah sebenar", text="Dia telefon nak downgrade. Saya suruh dia upgrade.")),
     ("number", 460.6, dict(big="+$500,000", sub="dalam 5 tahun, tanpa top-up cash")),
     ("quote", 139.9, dict(text="“Jangan downgrade sebelum kita kira dulu.”")),
     ("band", 86.5, dict(text="Downgrade → Upgrade", sub="Kakak 48 tahun · Jurong West"))],
 2: [("bold", 426.3, dict(kicker="Dua pakcik, 77 tahun", lines=["$30k", "vs", "$1.7 JUTA"], gold_idx=[2])),
     ("card", 431.9, dict(kicker="Persaraan", text="Dua pakcik, umur sama. Persaraan sangat berbeza.")),
     ("number", 362.6, dict(big="$1.7 JUTA", sub="cash pada usia 77 tahun")),
     ("quote", 399.5, dict(text="“Keputusan di usia 40-an menentukan persaraan anda.”")),
     ("band", 470.5, dict(text="Cikgu pun boleh.", sub="Landed → kondo freehold → $1.7 juta cash"))],
 3: [("bold", 36.9, dict(kicker="Mindset", lines=["Kenapa kita", "TAKUT nak", "upgrade?"], gold_idx=[1])),
     ("card", 28.2, dict(kicker="Soalan", text="Upgrade rumah = menunjuk?")),
     ("number", 231.6, dict(big="15 BULAN", sub="cooling period, dihapuskan 28 Julai 2026", big_size=200)),
     ("quote", 458.5, dict(text="“Besar periuk, besar keraknya?” Belum tentu.")),
     ("band", 43.0, dict(text="Kalau mampu, kita boleh.", sub="HDB → private → balik HDB dengan cash"))],
 4: [("bold", 246.9, dict(kicker="Checklist", lines=["3 SOALAN", "sebelum", "beli kondo"], gold_idx=[0])),
     ("card", 320.5, dict(kicker="Sebelum tandatangan", text="Jangan beli kondo kalau tak boleh jawab 3 soalan ini.")),
     ("number", 468.5, dict(big="7–10 TAHUN", sub="boleh bertahan ke tidak?", big_size=200)),
     ("quote", 181.6, dict(text="“Ramai yang ghairah, main terjun saja.”")),
     ("band", 461.3, dict(text="Checklist sebelum upgrade", sub="Bertahan 7–10 tahun · habis bayar @55 · ada buffer"))],
 5: [("bold", 172.0, dict(kicker="PropNex tech tools", lines=["Kondo ni", "boleh beli", "ke tidak?"], gold_idx=[2])),
     ("card", 142.2, dict(kicker="Sebelum beli", text="Jangan teka. Tengok data.")),
     ("number", 466.0, dict(big="DATA", sub="bukan teka", big_size=260)),
     ("quote", 60.5, dict(text="“Data untuk keputusan yang lebih baik.”")),
     ("band", 12.0, dict(text="Forecast 10 tahun", sub="Capital appreciation · projek ni bagus ke tidak"))],
}
FN = {"bold": style_bold, "card": style_card, "number": style_number, "quote": style_quote, "band": style_band}
names = {1: "reel1-kakak-downgrade", 2: "reel2-dua-pakcik", 3: "reel3-kenapa-takut-upgrade", 4: "reel4-3-soalan-sebelum-beli-kondo", 5: "reel5-data-bukan-teka"}
zf = zipfile.ZipFile(os.path.join(OUTD, "all-covers.zip"), "w", zipfile.ZIP_DEFLATED)
for r, items in covers.items():
    tiles = []
    for i, (sty, t, kw) in enumerate(items, 1):
        img = FN[sty](t, **kw).convert("RGB")
        fn = os.path.join(OUTD, f"{names[r]}-cover{i}.jpg"); img.save(fn, quality=92); zf.write(fn, os.path.basename(fn))
        tiles.append(img.resize((324, 576)))
    sheet = Image.new("RGB", (5 * 324 + 4 * 10, 576), (20, 20, 20))
    for i, im in enumerate(tiles): sheet.paste(im, (i * 334, 0))
    sheet.save(os.path.join(OUTD, f"{names[r]}-covers-sheet.jpg"), quality=88)
zf.close(); print("done", sorted(os.listdir(OUTD)))
