"""Overlay the Instagram/TikTok interface zones and the measured face band on frames from every rendered reel."""
import json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "output")
clips = json.load(open(os.path.join(HERE, "clips.json")))
F = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-SemiBold.otf", 22)
W, H = 1080, 1920
def clip_time(c, src_t):
    pre = 0.25; acc = 0.0
    for i, (a, b) in enumerate(c["segments"]):
        a2 = a - (pre if i == 0 else 0.12); b2 = b + (0.55 if i == len(c["segments"]) - 1 else 0.18)
        if a2 - 0.3 <= src_t <= b2 + 0.3: return acc + (src_t - a2)
        acc += b2 - a2
tiles = []
for c in clips:
    f = [x for x in os.listdir(OUT_DIR) if x.startswith(c["id"]) and x.endswith(".mp4")]
    if not f: continue
    path = os.path.join(OUT_DIR, f[0])
    for t, lb in [(1.5, "hook"), (clip_time(c, c["popups"][1]["t"]) + 0.8, "pop-up")]:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", path, "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "pipe:1"], capture_output=True).stdout
        im = Image.frombuffer("RGB", (W, H), raw, "raw", "RGB", 0, 1).convert("RGBA")
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        d.rectangle((0, 0, W, 270), fill=(220, 40, 40, 70)); d.rectangle((0, 1400, W, H), fill=(220, 40, 40, 70)); d.rectangle((920, 900, W, 1600), fill=(220, 40, 40, 70))
        d.rectangle((0, 270, 920, 1000), outline=(255, 215, 0, 255), width=4)
        d.text((20, 300), "face band (measured chin ≤ 962)", font=F, fill=(255, 215, 0, 255))
        d.text((20, 1410), "IG / TikTok interface zones", font=F, fill=(255, 120, 120, 255))
        im.alpha_composite(ov)
        tiles.append((f"{c['id']} {lb}", im.resize((270, 480))))
cols = 6; rows = (len(tiles) + cols - 1) // cols
board = Image.new("RGB", (16 + cols * 286, 16 + rows * 516), (246, 241, 232)); d = ImageDraw.Draw(board)
for i, (lb, im) in enumerate(tiles):
    x = 16 + (i % cols) * 286; y = 16 + (i // cols) * 516
    board.paste(im, (x, y)); d.text((x, y + 484), lb, font=F, fill=(27, 42, 63))
board.save(os.path.join(HERE, "safezone_proof.png"), optimize=True); print("safezone_proof.png", board.size)
