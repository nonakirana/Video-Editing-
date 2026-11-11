from PIL import Image, ImageDraw, ImageFont
import os
HERE = os.path.dirname(os.path.abspath(__file__))
COLS, ROWS, TW = 4, 2, 500
TH = round(TW * 1350 / 1080); G, TOP = 24, 70
sheet = Image.new("RGB", (G + COLS * (TW + G), TOP + ROWS * (TH + G + 36)), (246, 241, 232))
d = ImageDraw.Draw(sheet)
f = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-SemiBold.otf", 22)
d.text((G, 22), "Storyboard: Buy first, or sell first?  (8 slides, 1080x1350)", font=f, fill=(27, 42, 63))
labels = ["Cover", "Option 1: buy first", "Option 2: sell first", "Do both", "Know your numbers", "Sell + search together", "Coordinate timeline", "CTA"]
for i in range(8):
    im = Image.open(os.path.join(HERE, "slides", f"{i+1:02d}.png")).resize((TW, TH), Image.LANCZOS)
    c, r = i % COLS, i // COLS
    x, y = G + c * (TW + G), TOP + r * (TH + G + 36)
    sheet.paste(im, (x, y)); d.text((x, y + TH + 8), f"{i+1:02d}  {labels[i]}", font=f, fill=(27, 42, 63))
sheet.save(os.path.join(HERE, "storyboard.png"), optimize=True); print(sheet.size)
