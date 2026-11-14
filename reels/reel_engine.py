"""Barakah Homes reel renderer.

Takes a clip spec (in/out points on the source interview, hook text, pop-up words,
caption words with timings) and renders a 1080x1920 30fps branded reel:
  * sentence-safe trim with audio fades and loudness normalisation
  * punch-in zoom cuts on sentence starts + slow drift
  * hook title at the top for the first seconds
  * lower-third name plate
  * word-by-word Malay captions with the live word in gold, English line under it
  * gold / cream pop-up keyword cards with a spring animation
  * gold progress bar, small logo watermark
  * navy end card with logo and CTA
"""
import json, math, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
NAVY = (27, 42, 63)
NAVY_DEEP = (16, 27, 43)
GOLD = (164, 122, 60)
GOLD_LIGHT = (214, 176, 110)
CREAM = (246, 241, 232)
WHITE = (255, 255, 255)
MUTED = (200, 192, 178)

# Safe zone shared by Instagram Reels and TikTok on a 1080x1920 canvas:
#  - top 270px: status bar / camera / "Reels" title
#  - bottom 520px: username, caption, audio strip (TikTok captions can reach ~y1400)
#  - right 150px between y900 and y1600: like / comment / share / profile column
#  - the speaker's face sits in the top half; text starts below her chin (y>=720)
SAFE_L, SAFE_R = 64, 920
SAFE_W = SAFE_R - SAFE_L            # 856px usable width
SAFE_CX = (SAFE_L + SAFE_R) // 2    # 492: horizontal centre of the safe column
TEXT_TOP, TEXT_BOTTOM = 1000, 1400   # measured: her chin never goes below y≈950 in the chosen clips

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_IT = "/usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf"
SANS = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
SANS_B = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
SANS_XB = "/usr/share/fonts/opentype/inter/InterDisplay-ExtraBold.otf"
SANS_SB = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"

_fonts = {}
def font(path, size):
    k = (path, size)
    if k not in _fonts:
        _fonts[k] = ImageFont.truetype(path, size)
    return _fonts[k]

# ---------- easing ----------
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease_out_cubic(t): t = clamp(t); return 1 - (1 - t) ** 3
def ease_in_out(t): t = clamp(t); return t * t * (3 - 2 * t)
def spring(t):
    """overshooting pop: 0 -> ~1.12 -> 1"""
    t = clamp(t)
    return 1 - math.exp(-6.5 * t) * math.cos(10 * t) if t < 1 else 1.0

# ---------- drawing helpers ----------
def wrap(draw, text, f, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=f) <= max_w: cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def rounded(draw, box, r, fill):
    draw.rounded_rectangle(box, radius=r, fill=fill)

def shadowed(img, blur=18, offset=(0, 14), alpha=120):
    """Return a new image with a soft drop shadow under `img` (RGBA)."""
    pad = blur * 3
    canvas = Image.new("RGBA", (img.width + pad * 2, img.height + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sh.paste((10, 16, 28, alpha), (0, 0), img.split()[3])
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    canvas.alpha_composite(sh, (pad + offset[0], pad + offset[1]))
    canvas.alpha_composite(img, (pad, pad))
    return canvas

def paste_center(base, layer, cx, cy, scale=1.0, alpha=1.0, rot=0.0):
    if alpha <= 0.001 or scale <= 0.01: return
    im = layer
    if abs(scale - 1) > 0.002:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BILINEAR)
    if abs(rot) > 0.01:
        im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 0.999:
        a = im.split()[3].point(lambda v: int(v * alpha))
        im = im.copy(); im.putalpha(a)
    base.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))

# ---------- static layers ----------
def layer_bottom_gradient():
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px = ov.load()
    y0, y1 = int(H * 0.46), int(H * 0.80)
    for y in range(y0, H):
        a = int(150 * ease_in_out((min(y, y1) - y0) / (y1 - y0)))
        for x in range(W): px[x, y] = NAVY_DEEP + (a,)
    return ov

def layer_top_gradient(strength=190):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px = ov.load()
    y0, y1 = 0, int(H * 0.46)
    for y in range(y0, y1):
        a = int(strength * (1 - ease_in_out((y - y0) / (y1 - y0))))
        for x in range(W): px[x, y] = NAVY_DEEP + (a,)
    return ov

def layer_logo_mark(size=150):
    lg = Image.open(os.path.join(ASSETS, "barakah-logo.png")).convert("RGBA")
    lg = lg.crop(lg.getbbox())
    lg.thumbnail((size, size), Image.LANCZOS)
    # the logo is gold+navy; on dark video we lift the navy word mark to cream
    r, g, b, a = lg.split()
    px = lg.load()
    for y in range(lg.height):
        for x in range(lg.width):
            R, G, B, A = px[x, y]
            if A and R < 90 and B < 110:  # navy pixels -> cream
                px[x, y] = CREAM + (A,)
    return lg

def layer_lower_third(name, role):
    f1, f2 = font(SERIF, 46), font(SANS_SB, 24)
    tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    w = int(max(tmp.textlength(name, font=f1), tmp.textlength(role.upper(), font=f2)) + 96)
    h = 128
    im = Image.new("RGBA", (w + 14, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rounded(d, (14, 0, w + 14, h), 16, NAVY + (225,))
    d.rectangle((14, 0, 22, h), fill=GOLD)
    d.text((48, 22), name, font=f1, fill=CREAM)
    d.text((50, 84), role.upper(), font=f2, fill=GOLD_LIGHT)
    return im

def layer_hook(kicker, lines, size=52):
    f_k = font(SANS_B, 24)
    tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    while size > 40 and max(tmp.textlength(l.replace("*", ""), font=font(SERIF, size)) for l in lines) > SAFE_W:
        size -= 2
    f_h = font(SERIF, size)
    im = Image.new("RGBA", (W, 560), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    y = 0
    if kicker:
        f_k = font(SANS_B, 22)
        pill_w = int(d.textlength(kicker.upper(), font=f_k) + 36)
        rounded(d, (64, y, 64 + pill_w, y + 38), 19, GOLD + (255,))
        d.text((82, y + 7), kicker.upper(), font=f_k, fill=NAVY)
        y += 50
    for ln in lines:
        # highlight words wrapped in *asterisks* in gold
        x = 64
        for tok in ln.split(" "):
            gold = "*" in tok
            t = tok.replace("*", "")
            d.text((x + 3, y + 4), t, font=f_h, fill=(0, 0, 0, 110))
            d.text((x, y), t, font=f_h, fill=GOLD_LIGHT if gold else CREAM)
            x += d.textlength(t + " ", font=f_h)
        y += int(size * 1.02)
    return im.crop((0, 0, SAFE_R + 20, y + 14))

def layer_caption(words, hi, f_size=58, max_w=SAFE_W):
    """One caption chunk. words: list of str; hi: index of live word (-1 none)."""
    f = font(SANS_XB, f_size)
    tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    sp = tmp.textlength(" ", font=f)
    # layout into lines
    lines, cur, cur_w = [], [], 0
    for i, w in enumerate(words):
        ww = tmp.textlength(w, font=f)
        if cur and cur_w + sp + ww > max_w:
            lines.append(cur); cur, cur_w = [], 0
        cur.append((i, w, ww)); cur_w += ww + (sp if len(cur) > 1 else 0)
    if cur: lines.append(cur)
    lh = int(f_size * 1.32)
    pad_x, pad_y = 34, 22
    widths = [sum(ww for _, _, ww in ln) + sp * (len(ln) - 1) for ln in lines]
    bw = int(max(widths) + pad_x * 2)
    bh = lh * len(lines) + pad_y * 2 - 8
    im = Image.new("RGBA", (bw + 40, bh + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rounded(d, (20, 20, 20 + bw, 20 + bh), 22, NAVY + (215,))
    y = 20 + pad_y - 4
    for ln, lw in zip(lines, widths):
        x = 20 + (bw - lw) / 2
        for i, w, ww in ln:
            if i == hi:
                rounded(d, (x - 10, y - 2, x + ww + 10, y + lh - 10), 12, GOLD + (255,))
                d.text((x, y), w, font=f, fill=NAVY_DEEP)
            elif i < hi:
                d.text((x, y), w, font=f, fill=CREAM)
            else:
                d.text((x, y), w, font=f, fill=MUTED)
            x += ww + sp
        y += lh
    return im

def layer_subtitle(text, f_size=34):
    f = font(SANS_SB, f_size)
    tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    lines = wrap(tmp, text, f, SAFE_W - 40)
    lh = int(f_size * 1.25)
    im = Image.new("RGBA", (SAFE_W, lh * len(lines) + 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    y = 4
    for ln in lines:
        x = (SAFE_W - d.textlength(ln, font=f)) / 2
        d.text((x + 2, y + 2), ln, font=f, fill=(0, 0, 0, 160))
        d.text((x, y), ln, font=f, fill=GOLD_LIGHT)
        y += lh
    return im

def layer_popup(text, style="cream", size=80, sub=None):
    size = min(size, 74)
    """Big pop-up word card."""
    f = font(SERIF if style != "sans" else SANS_XB, size)
    tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    lines = wrap(tmp, text, f, SAFE_W - 120)
    lh = int(size * 1.06)
    tw = max(tmp.textlength(l, font=f) for l in lines)
    pad_x, pad_y = 48, 28
    bw, bh = int(tw + pad_x * 2), lh * len(lines) + pad_y * 2
    if sub: bh += 40
    im = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if style == "cream":
        rounded(d, (0, 0, bw, bh), 26, CREAM + (255,)); fg = NAVY; rule = GOLD
    elif style == "gold":
        rounded(d, (0, 0, bw, bh), 26, GOLD + (255,)); fg = NAVY_DEEP; rule = CREAM
    else:  # navy
        rounded(d, (0, 0, bw, bh), 26, NAVY + (245,)); fg = CREAM; rule = GOLD
    d.rectangle((pad_x, pad_y - 14, pad_x + 70, pad_y - 8), fill=rule)
    y = pad_y
    for l in lines:
        d.text((pad_x, y), l, font=f, fill=fg); y += lh
    if sub:
        d.text((pad_x, y + 2), sub.upper(), font=font(SANS_B, 24), fill=rule if style != "gold" else NAVY)
    return shadowed(im, blur=22, offset=(0, 18), alpha=140)

def layer_endcard(cta_big, cta_small, handle):
    im = Image.new("RGBA", (W, H), NAVY + (255,))
    d = ImageDraw.Draw(im)
    # subtle arch motif: faint gold rounded rectangle frame
    d.rounded_rectangle((70, 70, W - 70, H - 70), radius=40, outline=GOLD + (90,), width=3)
    lg = Image.open(os.path.join(ASSETS, "barakah-logo.png")).convert("RGBA")
    lg = lg.crop(lg.getbbox()); lg.thumbnail((520, 520), Image.LANCZOS)
    # recolour navy word mark to cream
    px = lg.load()
    for y in range(lg.height):
        for x in range(lg.width):
            R, G, B, A = px[x, y]
            if A and R < 90 and B < 110: px[x, y] = CREAM + (A,)
    im.alpha_composite(lg, ((W - lg.width) // 2, 420))
    y = 420 + lg.height + 90
    d.rectangle(((W - 90) // 2, y, (W + 90) // 2, y + 6), fill=GOLD); y += 46
    f = font(SERIF, 76)
    for ln in wrap(d, cta_big, f, W - 200):
        d.text(((W - d.textlength(ln, font=f)) / 2, y), ln, font=f, fill=CREAM); y += 84
    y += 20
    f2 = font(SANS, 34)
    for ln in wrap(d, cta_small, f2, W - 220):
        d.text(((W - d.textlength(ln, font=f2)) / 2, y), ln, font=f2, fill=MUTED); y += 48
    # handle pill
    f3 = font(SANS_B, 32)
    pw = int(d.textlength(handle, font=f3) + 72)
    rounded(d, ((W - pw) // 2, H - 420, (W + pw) // 2, H - 352), 34, GOLD + (255,))
    d.text(((W - d.textlength(handle, font=f3)) / 2, H - 405), handle, font=f3, fill=NAVY_DEEP)
    pn = Image.open(os.path.join(ASSETS, "propnex-logo.png")).convert("RGBA")
    pn = pn.crop(pn.getbbox()); pn.thumbnail((220, 80), Image.LANCZOS)
    f4 = font(SANS_SB, 24)
    t = "BARAKAH HOMES @"
    tw = d.textlength(t, font=f4)
    x0 = (W - (tw + 18 + pn.width)) / 2
    d.text((x0, H - 250 + (pn.height - 28) / 2), t, font=f4, fill=MUTED)
    # PropNex logo has dark text; place on a cream chip for legibility
    chip = Image.new("RGBA", (pn.width + 28, pn.height + 20), CREAM + (255,))
    chip.alpha_composite(pn, (14, 10))
    im.alpha_composite(chip, (int(x0 + tw + 18), H - 260))
    return im

# ---------- caption chunking ----------
def chunk_words(words, max_words=4, max_dur=2.2):
    """words: [{'w','s','e'}] -> list of chunks [{'words':[...], 's','e'}]
    Breaks on punctuation, long gaps, max_words."""
    chunks, cur = [], []
    def flush():
        if cur: chunks.append({"words": list(cur), "s": cur[0]["s"], "e": cur[-1]["e"]})
        cur.clear()
    for i, w in enumerate(words):
        if cur and (w.get("brk") or w["s"] - cur[-1]["e"] > 0.7 or len(cur) >= max_words or w["s"] - cur[0]["s"] > max_dur):
            flush()
        cur.append(w)
        if w["w"].rstrip()[-1:] in ".?!," and len(cur) >= 2:
            flush()
    flush()
    return chunks

# ---------- main render ----------
def render(spec, src, out_path, workdir):
    os.makedirs(workdir, exist_ok=True)
    pre, post = spec.get("pre", 0.25), spec.get("post", 0.55)
    segs = spec.get("segments") or [[spec["in"], spec["out"]]]
    # expand first/last with breathing room; inner joins get a small pad each side
    ranges = []
    for i, (a, b) in enumerate(segs):
        a2 = max(0, a - (pre if i == 0 else 0.12))
        b2 = b + (post if i == len(segs) - 1 else 0.18)
        ranges.append((a2, b2))
    t_in = ranges[0][0] + pre
    body = sum(b - a for a, b in ranges)
    # map source time -> clip time
    offs, acc = [], 0.0
    for a, b in ranges:
        offs.append((a, b, acc)); acc += b - a
    def to_clip(ts):
        for a, b, o in offs:
            if a - 0.3 <= ts <= b + 0.3: return o + (min(max(ts, a), b) - a)
        return None
    start = ranges[0][0]
    end_len = spec.get("endcard", 2.4)
    total = body + end_len
    n_frames = int(round(total * FPS))
    body_frames = int(round(body * FPS))
    if os.environ.get("PREVIEW"):
        n_frames = min(n_frames, int(float(os.environ["PREVIEW"]) * FPS))

    # audio: trim, normalise, fade, pad for end card
    aud = os.path.join(workdir, "audio.wav")
    parts = []
    for i, (a, b) in enumerate(ranges):
        pth = os.path.join(workdir, f"a{i}.wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-t", f"{b-a:.3f}", "-i", src, "-vn", "-ac", "2", "-ar", "48000",
                        "-af", "afade=t=in:d=0.04,afade=t=out:st=%.3f:d=0.04" % (b - a - 0.04), pth], check=True)
        parts.append(pth)
    lst = os.path.join(workdir, "alist.txt")
    open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst,
                    "-af", f"highpass=f=70,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000,afade=t=in:d=0.15,afade=t=out:st={body-0.45:.3f}:d=0.45,apad=whole_dur={total:.3f}",
                    "-ar", "48000", aud], check=True)

    # layers
    L_bot = layer_bottom_gradient()
    L_top = layer_top_gradient()
    L_logo = layer_logo_mark(spec.get("logo_size", 120))
    L_lt = layer_lower_third(spec.get("name", "Nona Kirana"), spec.get("role", "Barakah Homes Realty · PropNex"))
    L_hook = layer_hook(spec.get("kicker"), spec["hook"], spec.get("hook_size", 78))
    L_end = layer_endcard(spec.get("cta_big", "Still growing. Still recruiting."),
                          spec.get("cta_small", "Realtors who want to grow steadily, with people who want to see you win: DM “GROW”."),
                          spec.get("handle", "@nonakirana"))
    hook_dur = spec.get("hook_dur", 3.2)

    # captions relative to clip start
    words = [{"w": w["w"].strip(), "s": to_clip(w["s"]), "e": to_clip(w["e"]), "brk": w.get("brk", False)} for w in spec["words"]]
    words = [w for w in words if w["s"] is not None and w["e"] is not None]
    join_times = [o for _, _, o in offs][1:]
    for w in words:
        if any(abs(w["s"] - j) < 0.3 for j in join_times): w["brk"] = True
    chunks = chunk_words(words, spec.get("max_words", 4))
    cap_cache = {}
    subs = [{"s": to_clip(s["s"]), "e": to_clip(s["e"]), "text": s["en"]} for s in spec.get("subs", [])]
    subs = [s for s in subs if s["s"] is not None and s["e"] is not None]
    sub_cache = {}
    popups = [dict(p, layer=layer_popup(p["text"], p.get("style", "cream"), p.get("size", 92), p.get("sub"))) for p in spec.get("popups", [])]
    for p in popups: p["t"] = to_clip(p["t"])  # popup times are given in source seconds
    popups = [p for p in popups if p["t"] is not None]
    seg_starts = [o for _, _, o in offs][1:]
    zoom_cuts = sorted(set([0.0] + seg_starts + [c["s"] for c in chunks if c["words"][0]["w"][:1].isupper()]))
    # alternate 1.0 / 1.14 scale on sentence starts, at most one cut per 3.5s
    cuts, last = [], -10
    for t in zoom_cuts:
        if t - last >= 3.5 or t in seg_starts: cuts.append(t); last = t
    face_cx, face_cy = spec.get("face", (540, 1100))  # anchor crop to the bottom: zoom lifts the face, never lowers it

    busy = sorted((p["t"] - 0.3, p["t"] + p.get("dur", 2.0) + 0.2) for p in popups)
    cur = hook_dur + 0.2; lt_window = (cur, cur + 4.5)
    for b0, b1 in busy + [(body - 0.6, body)]:
        if b0 - cur >= 3.0: lt_window = (cur, min(cur + 4.5, b0)); break
        cur = max(cur, b1)

    def zoom_at(t):
        idx = max(i for i, c in enumerate(cuts) if c <= t)
        base = 1.0 if idx % 2 == 0 else 1.08
        drift = 0.025 * clamp((t - cuts[idx]) / 6.0)   # slow push-in
        return base + drift

    dcmd = ["ffmpeg", "-v", "error"]
    for a, b in ranges: dcmd += ["-ss", f"{a:.3f}", "-t", f"{b-a:.3f}", "-i", src]
    fc = "".join(f"[{i}:v]fps={FPS},scale={W}:{H},setpts=PTS-STARTPTS[v{i}];" for i in range(len(ranges)))
    fc += "".join(f"[v{i}]" for i in range(len(ranges))) + f"concat=n={len(ranges)}:v=1:a=0[out]"
    dcmd += ["-filter_complex", fc, "-map", "[out]", "-f", "rawvideo", "-pix_fmt", "rgb24", "pipe:1"]
    dec = subprocess.Popen(dcmd, stdout=subprocess.PIPE, bufsize=W * H * 3 * 4)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "pipe:0",
                            "-i", aud, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                            "-pix_fmt", "yuv420p", "-profile:v", "high", "-movflags", "+faststart",
                            "-c:a", "aac", "-b:a", "192k", "-shortest", out_path], stdin=subprocess.PIPE)
    frame_bytes = W * H * 3
    last_frame = None
    for fi in range(n_frames):
        t = fi / FPS
        if fi < body_frames:
            raw = dec.stdout.read(frame_bytes)
            if len(raw) < frame_bytes: raw = last_frame_raw
            last_frame_raw = raw
            fr = Image.frombuffer("RGB", (W, H), raw, "raw", "RGB", 0, 1)
            z = zoom_at(t)
            if z > 1.001:
                cw, ch = W / z, H / z
                cx = clamp(face_cx, cw / 2, W - cw / 2); cy = clamp(face_cy, ch / 2, H - ch / 2)
                fr = fr.crop((int(cx - cw / 2), int(cy - ch / 2), int(cx + cw / 2), int(cy + ch / 2))).resize((W, H), Image.BICUBIC)
            frame = fr.convert("RGBA")
            frame.alpha_composite(L_bot)
            # hook (top) with gradient
            if t < hook_dur:
                a = ease_out_cubic(t / 0.35) if t < 0.35 else (1 - ease_in_out((t - (hook_dur - 0.4)) / 0.4) if t > hook_dur - 0.4 else 1)
                pass
                sc = 0.94 + 0.06 * ease_out_cubic(t / 0.45)
                hook_y = spec.get("hook_y", TEXT_TOP)
                paste_center(frame, L_hook, L_hook.width / 2, hook_y + L_hook.height / 2 + (1 - ease_out_cubic(t / 0.45)) * 30, scale=sc, alpha=a)
            # lower third: first window of at least 3 s after the hook in which no pop-up is on screen
            lt0, lt1 = lt_window
            if lt0 <= t < lt1:
                k = ease_out_cubic((t - lt0) / 0.5)
                a = k if t < lt1 - 0.4 else 1 - ease_in_out((t - (lt1 - 0.4)) / 0.4)
                x = 64 - (1 - k) * 80
                im = L_lt.copy(); im.putalpha(im.split()[3].point(lambda v: int(v * a)))
                frame.alpha_composite(im, (int(x), spec.get("lt_y", TEXT_TOP + 30)))
            # logo watermark (top right, below status bar)
            frame.alpha_composite(L_logo, (64, 290)) if t >= hook_dur else None
            # captions (pushed below the hook block while it is on screen, measured from the layer itself)
            cap_y = spec.get("cap_y", 1250)
            hook_bottom = spec.get("hook_y", TEXT_TOP) + L_hook.height
            hook_vis = 1.0 if t < hook_dur - 0.4 else 1 - ease_in_out((t - (hook_dur - 0.4)) / 0.4)
            for ci, c in enumerate(chunks):
                if c["s"] - 0.05 <= t <= c["e"] + 0.25:
                    hi = -1
                    for wi, w in enumerate(c["words"]):
                        if w["s"] <= t: hi = wi
                    key = (ci, hi)
                    if key not in cap_cache: cap_cache[key] = layer_caption([w["w"] for w in c["words"]], hi, spec.get("cap_size", 54))
                    im = cap_cache[key]
                    need = hook_bottom + 22 + (im.height / 2 - 20) - cap_y   # 20 = transparent margin of the pill image
                    if need > 0 and hook_vis > 0: cap_y = cap_y + need * hook_vis
                    # pop on each new word
                    tw = c["words"][hi]["s"] if hi >= 0 else c["s"]
                    sc = 1 + 0.06 * (1 - ease_out_cubic((t - tw) / 0.16))
                    paste_center(frame, im, SAFE_CX, cap_y, scale=sc)
                    break
            # english subtitle
            for si, s in enumerate(subs):
                if s["s"] <= t <= s["e"] + 0.3:
                    if si not in sub_cache: sub_cache[si] = layer_subtitle(s["text"], spec.get("sub_size", 32))
                    a = ease_out_cubic((t - s["s"]) / 0.25) * (1 - hook_vis)   # English line waits until the hook leaves
                    paste_center(frame, sub_cache[si], SAFE_CX, cap_y + 70 + sub_cache[si].height / 2, alpha=a)
                    break
            # popups
            for p in popups:
                dur = p.get("dur", 2.0)
                if p["t"] <= t <= p["t"] + dur:
                    k = (t - p["t"])
                    sc = spring(k / 0.55) if k < 0.55 else 1.0
                    a = 1.0 if k < dur - 0.3 else 1 - ease_in_out((k - (dur - 0.3)) / 0.3)
                    rot = p.get("rot", -3) * (1 - ease_out_cubic(k / 0.6)) + p.get("rest_rot", -2)
                    paste_center(frame, p["layer"], p.get("x", SAFE_CX), p.get("y", 1085), scale=sc * (1 if k < dur - 0.3 else 1 - 0.1 * (1 - a)), alpha=a, rot=rot)
            # quick cream flash on hard joins between segments
            for ss in seg_starts:
                if 0 <= t - ss < 0.2:
                    fl = Image.new("RGBA", (W, H), CREAM + (int(200 * (1 - (t - ss) / 0.2)),))
                    frame.alpha_composite(fl)
            # progress bar
            d = ImageDraw.Draw(frame)
            d.rectangle((0, H - 10, W, H), fill=NAVY_DEEP + (160,))
            d.rectangle((0, H - 10, int(W * t / body), H), fill=GOLD + (255,))
            last_frame = frame
        else:
            k = (fi - body_frames) / FPS
            a = ease_in_out(k / 0.5)
            frame = last_frame.copy() if a < 1 else L_end.copy()
            if a < 1:
                ec = L_end.copy(); ec.putalpha(ec.split()[3].point(lambda v: int(v * a)))
                frame.alpha_composite(ec)
            else:
                frame = L_end.copy()
            # gentle rise of the end card content is skipped for simplicity; add a fade-in of the CTA pill
        enc.stdin.write(frame.convert("RGB").tobytes())
        if fi % 150 == 0: print(f"  {spec['id']}: frame {fi}/{n_frames}", flush=True)
    dec.stdout.close(); dec.wait()
    enc.stdin.close(); enc.wait()
    return out_path

if __name__ == "__main__":
    spec_path, src, out_dir = sys.argv[1], sys.argv[2], sys.argv[3]
    only = sys.argv[4].split(",") if len(sys.argv) > 4 else None
    specs = json.load(open(spec_path))
    os.makedirs(out_dir, exist_ok=True)
    for s in specs:
        if only and s["id"] not in only: continue
        out = os.path.join(out_dir, f"{s['id']}_{s['slug']}.mp4")
        print("rendering", out, flush=True)
        render(s, src, out, os.path.join(out_dir, "_work", s["id"]))
        print("done", out, flush=True)
