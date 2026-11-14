#!/usr/bin/env python3
"""
Barakah Homes house-tour editor.

Takes a raw walkthrough video plus a small JSON "gag sheet" and produces a
branded, comedy-cut tour:

  * animated Barakah Homes logo intro and a call-to-action outro
  * logo badge watermark throughout
  * timed comedy captions (pop, lower-third, tag styles) with slide/fade-in
  * snap zoom punch-ins, fast-forward "skip the boring bit" sections,
    freeze frames with a record-scratch, hard cuts
  * synthesised sound effects (whoosh, boing, ding, pop, scratch, drumroll)

Usage:
    python3 edit_house_tour.py --video raw.mp4 --gags gags.json --out tour.mp4

All times in the gag sheet are seconds into the ORIGINAL video; the script maps
them onto the edited timeline for you.  See gags.example.json.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOGO = HERE.parent / "recruitment-carousel" / "photos" / "barakah-logo.png"

FONT_BOLD = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
FONT_SEMI = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
if not os.path.exists(FONT_BOLD):
    FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
if not os.path.exists(FONT_SEMI):
    FONT_SEMI = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

NAVY = "0x15233B"
GOLD = "0xA67C3D"
CREAM = "0xF6F1E7"
YELLOW = "0xFFD23F"

W, H, FPS = 1920, 1080, 30   # overwritten by --format
SC = 1.0                     # ui scale (1.0 at 1080p landscape)


def fs(n: int) -> int:
    """Scale a font size / pixel offset for the chosen output format."""
    return int(round(n * SC))
AR = 48000

INTRO_LEN = 3.2
OUTRO_LEN = 4.5


# --------------------------------------------------------------------------- utils
def run(cmd: list[str], quiet: bool = True) -> None:
    if not quiet:
        print(" ".join(shlex.quote(c) for c in cmd))
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        sys.stderr.write(res.stderr[-4000:])
        raise SystemExit(f"command failed: {cmd[0]} ... (exit {res.returncode})")


def ffprobe(path: str) -> dict:
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", path],
        text=True,
    )
    return json.loads(out)


def esc(text: str) -> str:
    """Escape text for drawtext."""
    return (
        text.replace("\\", "\\\\")
        .replace(":", "\\:")
        .replace("'", "’")
        .replace("%", "\\%")
        .replace(",", "\\,")
        .replace("[", "\\[")
        .replace("]", "\\]")
        .replace(";", "\\;")
    )


def fmt(x: float) -> str:
    return f"{x:.3f}"


# --------------------------------------------------------------------------- assets
def build_logo_assets(tmp: Path) -> tuple[Path, Path, Path]:
    """Return (big logo, light logo for dark backgrounds, watermark badge) PNG paths."""
    from PIL import Image, ImageDraw, ImageFilter

    logo = Image.open(LOGO).convert("RGBA")
    bbox = logo.getchannel("A").getbbox()
    logo = logo.crop(bbox)

    big = logo.copy()
    big.thumbnail((720, 720), Image.LANCZOS)
    big_path = tmp / "logo_big.png"
    big.save(big_path)

    # Light variant: navy pixels -> cream, gold stays, for the dark outro card.
    import numpy as np
    arr = np.array(big).astype(int)
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    dark = (r + g + b) < 330
    arr[dark, 0], arr[dark, 1], arr[dark, 2] = 246, 241, 231
    light_path = tmp / "logo_light.png"
    Image.fromarray(arr.astype("uint8"), "RGBA").save(light_path)

    # Watermark: logo on a soft cream rounded badge with a faint shadow.
    size = fs(190)
    pad = fs(18)
    inner = logo.copy()
    inner.thumbnail((size - 2 * pad, size - 2 * pad), Image.LANCZOS)
    badge = Image.new("RGBA", (size + 12, size + 12), (0, 0, 0, 0))
    shadow = Image.new("RGBA", badge.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((8, 10, size + 8, size + 10), fs(28), fill=(0, 0, 0, 90))
    shadow = shadow.filter(ImageFilter.GaussianBlur(6))
    badge.alpha_composite(shadow)
    card = Image.new("RGBA", badge.size, (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle((4, 4, size + 4, size + 4), fs(28), fill=(246, 241, 231, 225))
    badge.alpha_composite(card)
    ox = 4 + (size - inner.width) // 2
    oy = 4 + (size - inner.height) // 2
    badge.alpha_composite(inner, (ox, oy))
    badge_path = tmp / "logo_badge.png"
    badge.save(badge_path)
    return big_path, light_path, badge_path


# --------------------------------------------------------------------------- sfx
SFX_EXPR = {
    # name: (duration, aevalsrc expression)
    "whoosh": (0.55, "0.5*random(0)*sin(2*PI*t*2)*exp(-4*t)*min(1,t*30)"),
    "boing": (0.7, "0.6*sin(2*PI*(260+220*exp(-9*t))*t+0.6*sin(2*PI*22*t)*exp(-6*t))*exp(-4*t)"),
    "ding": (1.0, "0.45*(sin(2*PI*1318*t)+0.5*sin(2*PI*2637*t))*exp(-5*t)"),
    "pop": (0.18, "0.7*sin(2*PI*(420+600*exp(-30*t))*t)*exp(-18*t)"),
    "scratch": (0.6, "0.7*random(0)*(0.5+0.5*sin(2*PI*(9+40*t)*t))*exp(-3.5*t)"),
    "drumroll": (1.5, "0.5*random(0)*exp(-60*mod(t,0.06))*min(1,t*8)*(if(lt(t,1.45),1,0))"),
    "sad": (1.6, "0.4*(sin(2*PI*(392-50*floor(t*2.2))*t))*exp(-1.2*t)"),
    "honk": (0.45, "0.5*(sin(2*PI*180*t)+0.5*sin(2*PI*360*t)+0.3*sin(2*PI*540*t))*min(1,t*40)*exp(-3*t)"),
}


def render_sfx(tmp: Path) -> dict[str, Path]:
    out = {}
    for name, (dur, expr) in SFX_EXPR.items():
        p = tmp / f"sfx_{name}.wav"
        run([
            "ffmpeg", "-y", "-v", "error", "-f", "lavfi",
            "-i", f"aevalsrc=exprs='{expr}':s={AR}:d={dur}",
            "-af", "lowpass=f=9000,alimiter=limit=0.9", "-ac", "2", str(p),
        ])
        out[name] = p
    return out


# --------------------------------------------------------------------------- timeline
@dataclass
class Seg:
    kind: str            # "src" | "freeze" | "intro" | "outro"
    src_start: float = 0.0
    src_end: float = 0.0
    speed: float = 1.0
    zoom: float = 1.0
    zoom_x: float = 0.5
    zoom_y: float = 0.5
    freeze_at: float = 0.0
    duration: float = 0.0    # output seconds (filled in)
    out_start: float = 0.0
    label: str | None = None  # e.g. ">> 6x"

    @property
    def out_end(self) -> float:
        return self.out_start + self.duration


def build_segments(total: float, gags: list[dict]) -> list[Seg]:
    """Turn cut/speed/freeze/zoom gags into a flat list of output segments."""
    # Collect boundaries in source time.
    marks = {0.0, total}
    for g in gags:
        if g["type"] in ("cut", "speed", "zoom"):
            marks.add(max(0.0, g["start"]))
            marks.add(min(total, g["end"]))
        elif g["type"] == "freeze":
            marks.add(min(total, g["at"]))
    pts = sorted(marks)

    segs: list[Seg] = [Seg("intro", duration=INTRO_LEN)]
    for a, b in zip(pts, pts[1:]):
        if b - a < 1e-3:
            continue
        mid = (a + b) / 2
        s = Seg("src", src_start=a, src_end=b)
        skip = False
        for g in gags:
            if g["type"] == "cut" and g["start"] <= mid <= g["end"]:
                skip = True
            elif g["type"] == "speed" and g["start"] <= mid <= g["end"]:
                s.speed = float(g.get("factor", 6))
                s.label = g.get("label", f">> {s.speed:g}x")
            elif g["type"] == "zoom" and g["start"] <= mid <= g["end"]:
                s.zoom = float(g.get("factor", 1.6))
                s.zoom_x = float(g.get("x", 0.5))
                s.zoom_y = float(g.get("y", 0.5))
        if skip:
            continue
        s.duration = (b - a) / s.speed
        # freeze frame gag sits at the START of the segment that begins at g["at"]
        for g in gags:
            if g["type"] == "freeze" and abs(g["at"] - a) < 1e-3:
                segs.append(Seg("freeze", freeze_at=a, duration=float(g.get("hold", 2.0)),
                                zoom=s.zoom, zoom_x=s.zoom_x, zoom_y=s.zoom_y))
        segs.append(s)
    segs.append(Seg("outro", duration=OUTRO_LEN))

    t = 0.0
    for s in segs:
        s.out_start = t
        t += s.duration
    return segs


def src_to_out(segs: list[Seg], t_src: float) -> float | None:
    """Map a source timestamp onto the output timeline (None if it was cut)."""
    for s in segs:
        if s.kind == "src" and s.src_start - 1e-6 <= t_src <= s.src_end + 1e-6:
            return s.out_start + (t_src - s.src_start) / s.speed
    for s in segs:  # fell on a freeze boundary
        if s.kind == "freeze" and abs(s.freeze_at - t_src) < 1e-3:
            return s.out_start
    return None


# --------------------------------------------------------------------------- filters
def zoom_filter(z: float, cx: float, cy: float) -> str:
    if z <= 1.001:
        return ""
    cw, ch = f"iw/{z:.4f}", f"ih/{z:.4f}"
    x = f"(iw-{cw})*{cx:.3f}"
    y = f"(ih-{ch})*{cy:.3f}"
    return f"crop={cw}:{ch}:{x}:{y},"


def base_video_chain(zoom: str = "") -> str:
    # Fit any input (vertical phone footage included) into 1920x1080 with a
    # blurred copy of itself behind it, keep 30fps.
    return (
        f"[0:v]{zoom}scale={W}:{H}:force_original_aspect_ratio=decrease,"
        f"setsar=1,fps={FPS},format=yuv420p,split=2[fg][bgsrc];"
        f"[bgsrc]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
        f"gblur=sigma=40,eq=brightness=-0.15[bg];"
        f"[bg][fg]overlay=(W-w)/2:(H-h)/2"
    )


def speed_label(label: str) -> str:
    return (
        f",drawtext=fontfile={FONT_BOLD}:text='{esc(label)}':fontsize={fs(54)}:fontcolor=white:"
        f"borderw=4:bordercolor=black:x={fs(70)}:y={fs(70)}:"
        f"box=1:boxcolor={NAVY}@0.75:boxborderw={fs(22)}"
    )


def render_src_segment(video: str, s: Seg, out: Path, has_audio: bool) -> None:
    vchain = base_video_chain(zoom_filter(s.zoom, s.zoom_x, s.zoom_y))
    if s.speed != 1.0:
        vchain += f",setpts=PTS/{s.speed:.4f}"
        if s.label:
            vchain += speed_label(s.label)
    vchain += "[v]"

    cmd = ["ffmpeg", "-y", "-v", "error", "-ss", fmt(s.src_start), "-to", fmt(s.src_end), "-i", video]
    if has_audio:
        a = "[0:a]"
        if s.speed != 1.0:
            # atempo only accepts 0.5..100 per stage, chain for safety
            factor = s.speed
            stages = []
            while factor > 100:
                stages.append("atempo=100")
                factor /= 100
            stages.append(f"atempo={factor:.4f}")
            a += ",".join(stages) + ","
            a += "volume=0.5,"
        a += f"aresample={AR},aformat=channel_layouts=stereo[a]"
        fc = vchain + ";" + a
        cmd += ["-filter_complex", fc, "-map", "[v]", "-map", "[a]"]
    else:
        cmd += ["-f", "lavfi", "-i", f"anullsrc=r={AR}:cl=stereo", "-filter_complex", vchain,
                "-map", "[v]", "-map", "1:a", "-shortest"]
    cmd += encode_args() + [str(out)]
    run(cmd)


def render_freeze_segment(video: str, s: Seg, out: Path) -> None:
    vchain = base_video_chain(zoom_filter(s.zoom, s.zoom_x, s.zoom_y))
    # slow dramatic push-in on the frozen frame
    vchain += (f",loop=loop={int(s.duration * FPS)}:size=1:start=0,"
               f"zoompan=z='min(1+0.002*on,1.25)':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS},"
               f"trim=duration={fmt(s.duration)},setpts=PTS-STARTPTS,"
               f"eq=saturation=0.35:contrast=1.1[v]")
    cmd = ["ffmpeg", "-y", "-v", "error", "-ss", fmt(s.freeze_at), "-i", video,
           "-f", "lavfi", "-t", fmt(s.duration), "-i", f"anullsrc=r={AR}:cl=stereo",
           "-frames:v", str(int(s.duration * FPS)),
           "-filter_complex", vchain, "-map", "[v]", "-map", "1:a", "-t", fmt(s.duration)]
    cmd += encode_args() + [str(out)]
    run(cmd)


def render_intro(logo_big: Path, out: Path, title: str, subtitle: str) -> None:
    d = INTRO_LEN
    # logo pops in with an overshoot bounce, title slides up underneath
    bounce = "(1-0.35*exp(-5*t)*cos(11*t))"
    fc = (
        f"color=c={CREAM}:s={W}x{H}:r={FPS}:d={d}[bg];"
        f"[1:v]scale=w='{fs(520)}*{bounce}':h=-1:eval=frame[lg];"
        f"[bg][lg]overlay=x=(W-w)/2:y=(H-h)/2-{fs(130)}:shortest=1,"
        f"drawtext=fontfile={FONT_BOLD}:text='{esc(title)}':fontsize={fs(78)}:fontcolor={NAVY}:"
        f"x=(w-text_w)/2:y=H*0.68+{fs(40)}*max(0\\,1-(t-0.5)*4):alpha='clip((t-0.5)*3,0,1)',"
        f"drawtext=fontfile={FONT_SEMI}:text='{esc(subtitle)}':fontsize={fs(40)}:fontcolor={GOLD}:"
        f"x=(w-text_w)/2:y=H*0.68+{fs(100)}+{fs(40)}*max(0\\,1-(t-0.9)*4):alpha='clip((t-0.9)*3,0,1)',"
        f"fade=t=out:st={d-0.35}:d=0.35,format=yuv420p[v]"
    )
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"color=c={CREAM}:s=16x16:r={FPS}:d={d}",
           "-loop", "1", "-t", fmt(d), "-i", str(logo_big),
           "-f", "lavfi", "-t", fmt(d), "-i", f"anullsrc=r={AR}:cl=stereo",
           "-filter_complex", fc, "-map", "[v]", "-map", "2:a", "-t", fmt(d)]
    cmd += encode_args() + [str(out)]
    run(cmd)


def render_outro(logo_big: Path, out: Path, cta: str, handle: str) -> None:
    d = OUTRO_LEN
    fc = (
        f"color=c={NAVY}:s={W}x{H}:r={FPS}:d={d}[bg];"
        f"[1:v]scale=w='{fs(420)}*(1-0.3*exp(-5*t)*cos(11*t))':h=-1:eval=frame[lgc];"
        f"[bg][lgc]overlay=x=(W-w)/2:y=(H-h)/2-{fs(180)}:shortest=1,"
        f"drawtext=fontfile={FONT_BOLD}:text='{esc(cta)}':fontsize={fs(64)}:fontcolor={CREAM}:"
        f"x=(w-text_w)/2:y=H*0.66+{fs(40)}*max(0\\,1-(t-0.6)*4):alpha='clip((t-0.6)*3,0,1)',"
        f"drawtext=fontfile={FONT_SEMI}:text='{esc(handle)}':fontsize={fs(40)}:fontcolor={GOLD}:"
        f"x=(w-text_w)/2:y=H*0.66+{fs(95)}+{fs(40)}*max(0\\,1-(t-1.0)*4):alpha='clip((t-1.0)*3,0,1)',"
        f"fade=t=in:st=0:d=0.3,fade=t=out:st={d-0.6}:d=0.6,format=yuv420p[v]"
    )
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"color=c={NAVY}:s=16x16:r={FPS}:d={d}",
           "-loop", "1", "-t", fmt(d), "-i", str(logo_big),
           "-f", "lavfi", "-t", fmt(d), "-i", f"anullsrc=r={AR}:cl=stereo",
           "-filter_complex", fc, "-map", "[v]", "-map", "2:a", "-t", fmt(d)]
    cmd += encode_args() + [str(out)]
    run(cmd)


def encode_args(crf: int = 20, preset: str = "veryfast") -> list[str]:
    return ["-c:v", "libx264", "-preset", preset, "-crf", str(crf), "-pix_fmt", "yuv420p",
            "-r", str(FPS), "-c:a", "aac", "-b:a", "160k", "-ar", str(AR), "-ac", "2",
            "-movflags", "+faststart"]


# --------------------------------------------------------------------------- captions
def caption_filter(c: dict, start: float, end: float) -> str:
    """drawtext for a caption shown between output times start..end."""
    text = esc(c["text"])
    style = c.get("style", "pop")
    s, e = fmt(start), fmt(end)
    # pop-in: slide up 30px and fade over 0.25s; fade out over 0.2s
    slide = f"30*max(0\\,1-(t-{s})*4)"
    alpha = f"'clip((t-{s})*5,0,1)*clip(({e}-t)*6,0,1)'"
    enable = f"enable='between(t,{s},{e})'"

    if style == "pop":          # big yellow comic caption, centre-bottom
        lines = text.count("\\n") + 1
        return (f"drawtext=fontfile={FONT_BOLD}:text='{text}':fontsize={fs(72)}:fontcolor=black:"
                f"line_spacing=10:box=1:boxcolor={YELLOW}@0.95:boxborderw={fs(26)}:"
                f"x=(w-text_w)/2:y=h*0.74-{fs((lines-1)*45)}+{slide}:alpha={alpha}:{enable}")
    if style == "shout":        # huge white text with thick black outline, centre
        return (f"drawtext=fontfile={FONT_BOLD}:text='{text}':fontsize={fs(120)}:fontcolor=white:"
                f"borderw=10:bordercolor=black:line_spacing=12:"
                f"x=(w-text_w)/2:y=(h-text_h)/2+{slide}:alpha={alpha}:{enable}")
    if style == "lower":        # branded lower-third
        return (f"drawtext=fontfile={FONT_BOLD}:text='{text}':fontsize={fs(52)}:fontcolor={CREAM}:"
                f"box=1:boxcolor={NAVY}@0.9:boxborderw={fs(24)}:"
                f"x={fs(80)}:y=h-{fs(240)}+{slide}:alpha={alpha}:{enable}")
    if style == "tag":          # small italic-ish aside, top-left
        return (f"drawtext=fontfile={FONT_SEMI}:text='{text}':fontsize={fs(44)}:fontcolor=white:"
                f"box=1:boxcolor=black@0.7:boxborderw={fs(16)}:"
                f"x={fs(70)}:y={fs(70)}+{slide}:alpha={alpha}:{enable}")
    if style == "sticker":      # gold price-tag style, top-right under nothing
        return (f"drawtext=fontfile={FONT_BOLD}:text='{text}':fontsize={fs(56)}:fontcolor={NAVY}:"
                f"box=1:boxcolor={GOLD}@0.95:boxborderw={fs(22)}:"
                f"x=w-text_w-{fs(90)}:y={fs(90)}+{slide}:alpha={alpha}:{enable}")
    raise SystemExit(f"unknown caption style {style!r}")


# --------------------------------------------------------------------------- main
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--video", required=True)
    ap.add_argument("--gags", required=True, help="JSON gag sheet")
    ap.add_argument("--out", required=True)
    ap.add_argument("--crf", type=int, default=20)
    ap.add_argument("--preset", default="veryfast")
    ap.add_argument("--format", choices=["landscape", "portrait", "square"], default="landscape",
                    help="landscape 1920x1080 (YouTube), portrait 1080x1920 (Reels/TikTok), square 1080x1080")
    ap.add_argument("--keep-temp", action="store_true")
    args = ap.parse_args()

    global W, H, SC
    W, H = {"landscape": (1920, 1080), "portrait": (1080, 1920), "square": (1080, 1080)}[args.format]
    SC = 1.0 if args.format == "landscape" else 0.85

    sheet = json.load(open(args.gags))
    gags: list[dict] = sheet.get("gags", [])
    meta = ffprobe(args.video)
    vstream = next(s for s in meta["streams"] if s["codec_type"] == "video")
    has_audio = any(s["codec_type"] == "audio" for s in meta["streams"])
    total = float(meta["format"]["duration"])
    print(f"source: {vstream['width']}x{vstream['height']}  {total:.1f}s  audio={has_audio}")

    tmpdir = Path(tempfile.mkdtemp(prefix="tour_", dir=os.environ.get("TMPDIR") or None))
    try:
        logo_big, logo_light, badge = build_logo_assets(tmpdir)
        sfx = render_sfx(tmpdir)
        segs = build_segments(total, gags)
        out_total = segs[-1].out_end
        print(f"timeline: {len(segs)} segments, {out_total:.1f}s output")

        # ---- render segments
        parts = []
        for i, s in enumerate(segs):
            p = tmpdir / f"seg_{i:03d}.mp4"
            if s.kind == "intro":
                render_intro(logo_big, p, sheet.get("title", "The House Tour"),
                             sheet.get("subtitle", "presented by Barakah Homes Realty"))
            elif s.kind == "outro":
                render_outro(logo_light, p, sheet.get("cta", "DM 'TOUR' to view this home"),
                             sheet.get("handle", "Barakah Homes Realty"))
            elif s.kind == "freeze":
                render_freeze_segment(args.video, s, p)
            else:
                render_src_segment(args.video, s, p, has_audio)
            parts.append(p)
            print(f"  seg {i:03d} {s.kind:6s} {s.duration:6.2f}s  (out {s.out_start:7.2f})", flush=True)

        concat_list = tmpdir / "concat.txt"
        concat_list.write_text("".join(f"file '{p}'\n" for p in parts))
        joined = tmpdir / "joined.mp4"
        run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(concat_list),
             "-c", "copy", str(joined)])

        # ---- captions + watermark + sfx in one final pass
        vf = []
        main_start = INTRO_LEN
        main_end = out_total - OUTRO_LEN
        vf.append(f"[1:v]format=rgba,colorchannelmixer=aa=0.92[wm]")
        vf.append(f"[0:v][wm]overlay=x=W-w-{fs(50)}:y=H-h-{fs(50)}:"
                  f"enable='between(t,{fmt(main_start)},{fmt(main_end)})'[v0]")

        draw = []
        auto_sfx: list[tuple[str, float]] = []
        for g in gags:
            if g["type"] == "caption":
                a = src_to_out(segs, g["start"])
                b = src_to_out(segs, g["end"])
                if a is None or b is None:
                    print(f"  ! caption '{g['text'][:30]}' falls in a cut; skipped")
                    continue
                draw.append(caption_filter(g, a, b))
                if g.get("sfx"):
                    auto_sfx.append((g["sfx"], a))
            elif g["type"] == "freeze":
                a = src_to_out(segs, g["at"])
                hold = float(g.get("hold", 2.0))
                auto_sfx.append((g.get("sfx", "scratch"), a))
                if g.get("text"):
                    draw.append(caption_filter({"text": g["text"], "style": g.get("style", "shout")},
                                               a + 0.15, a + hold))
            elif g["type"] == "zoom":
                a = src_to_out(segs, g["start"])
                if a is not None:
                    auto_sfx.append((g.get("sfx", "pop"), a))
                if g.get("text"):
                    b = src_to_out(segs, g["end"])
                    draw.append(caption_filter({"text": g["text"], "style": g.get("style", "pop")}, a, b))
            elif g["type"] == "speed":
                a = src_to_out(segs, g["start"])
                if a is not None:
                    auto_sfx.append((g.get("sfx", "whoosh"), a))
            elif g["type"] == "sfx":
                a = src_to_out(segs, g["at"])
                if a is not None:
                    auto_sfx.append((g["name"], a))
        # intro / outro stingers
        auto_sfx.append(("whoosh", 0.05))
        auto_sfx.append(("ding", 0.6))
        auto_sfx.append(("ding", out_total - OUTRO_LEN + 0.4))

        if draw:
            vf.append("[v0]" + ",".join(draw) + "[vout]")
        else:
            vf.append("[v0]null[vout]")

        # audio: original + sfx (each padded with adelay) mixed, mildly normalised
        inputs = ["-i", str(joined), "-i", str(badge)]
        amix_labels = ["[0:a]"]
        for k, (name, at) in enumerate(auto_sfx):
            if name not in sfx:
                print(f"  ! unknown sfx {name!r}; skipped")
                continue
            inputs += ["-i", str(sfx[name])]
            idx = 2 + len(amix_labels) - 1
            ms = int(max(0.0, at) * 1000)
            vf.append(f"[{idx}:a]adelay={ms}|{ms},volume=1.6[s{k}]")
            amix_labels.append(f"[s{k}]")
        n = len(amix_labels)
        vf.append("".join(amix_labels) + f"amix=inputs={n}:duration=first:normalize=0,"
                  f"alimiter=limit=0.95[aout]")

        cmd = ["ffmpeg", "-y", "-v", "error", "-stats"] + inputs + [
            "-filter_complex", ";".join(vf), "-map", "[vout]", "-map", "[aout]",
            "-t", fmt(out_total)] + encode_args(args.crf, args.preset) + [args.out]
        print("final render ...", flush=True)
        run(cmd)
        print(f"done: {args.out}  ({out_total:.1f}s)")
    finally:
        if args.keep_temp:
            print(f"temp kept at {tmpdir}")
        else:
            shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    main()
