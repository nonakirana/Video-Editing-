import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reelkit import *
OUT = "/home/user/Video-Editing-/reels-upgrade-talk/reel5-data-bukan-teka.mp4"
spec = [
 dict(kind="clip", s=164.2, e=165.9, zoom=1.12, text="Kondo apa nak beli, boleh ke tidak?"),
 dict(kind="clip", s=166.4, e=179.3, zoom=1.0, push=0.04, text="PropNex saya rasa ada tools, PropNex tech tools yang boleh bantu kita buat forecasting. Bila kita beli projek ni, berapakah capital appreciation? Projek ni bagus untuk kita beli ke tidak? Bila nak jual dalam masa 10 tahun, okay ke tidak?"),
 dict(kind="clip", s=179.6, e=185.4, zoom=1.12, text="Jadi mereka ada informasi dan data untuk bantu saya dan para pelanggan saya buat keputusan yang lebih baik lagi."),
 dict(kind="still", t=466.0, dur=3.4, zoom=1.0, dark=0.5),
]
def make_els(segs, T, E, S):
    els, sfx = [], []
    els.append(Element(0.0, 3.0, popin(card("Kondo ni boleh beli ke tidak? Jangan teka.", size=60, bg=NAVY, maxw=900), (540, 1120)))); sfx.append((0.05, "whoosh"))
    els.append(Element(T(1, 168.8), E(1), popin(pill("PropNex tech tools", size=40, bg=NAVY, fg=WHITE), (60, 880), "lt"))); sfx.append((T(1, 168.85), "blip"))
    rows = lambda n: compare_card("FORECAST", ["Capital appreciation: ↑ ?", "Projek ni bagus ke tidak?", "Jual dalam 10 tahun: OK?"][:n], w=640, title_bg=GOLD_D)
    els.append(Element(T(1, 174.2), E(1), progressive(rows, [(0, (1,)), (T(1, 175.7) - T(1, 174.2), (2,)), (T(1, 177.4) - T(1, 174.2), (3,))], (540, 1140))))
    sfx += [(T(1, 174.25), "blip"), (T(1, 175.75), "blip"), (T(1, 177.45), "blip")]
    els.append(Element(T(2, 181.4), E(2), popin(stamp("DATA, BUKAN TEKA", size=72), (540, 1140)))); sfx.append((T(2, 181.45), "thud"))
    ec = end_card("Nak tengok data projek yang anda minat?", "DM saya di Instagram · TikTok · Facebook")
    els.append(Element(S(3), E(3), popin(ec, (540, 900), hold_fade=False))); sfx.append((S(3) + 0.05, "sting"))
    return els, sfx
run_reel("reel5", spec, make_els, OUT)
