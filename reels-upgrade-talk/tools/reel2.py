import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reelkit import *
OUT = "/home/user/Video-Editing-/reels-upgrade-talk/reel2-dua-pakcik.mp4"
spec = [
 dict(kind="clip", s=360.2, e=361.9, zoom=1.0, text="Saya ada kes dua pakcik ini."),
 dict(kind="clip", s=362.0, e=370.5, zoom=1.12, text="Satu pakcik 77 tahun, tinggal di rumah 4 bilik di Marsiling. Dari hari pertama, katanya dia beli rumah itu $38 ribu sahaja. Mana dah dapat 4 bilik, $38 ribu."),
 dict(kind="clip", s=370.8, e=380.0, zoom=1.0, push=0.03, text="Tapi bila tiba masanya dia nak jual, nak pindah rumah 3 bilik dekat dengan anak, keuntungan cash dia $30 ribu sahaja. Jadi pakcik kata, eh, susah payah jaga rumah, $30 ribu cash sahaja."),
 dict(kind="clip", s=380.8, e=386.6, zoom=1.12, text="Kerana apa? Semakin rumah itu berusia, rate of growth dia kurang sedikit."),
 dict(kind="clip", s=393.3, e=403.4, zoom=1.0, text="Berbanding dengan seorang lagi pakcik. Nona jumpa dia, pakcik itu tinggal kondo. Rumah kondo dah habis bayar. Saya tanya lah, pakcik bisnesman ke? Dia kata taklah, pakcik dulu ajar English saja dekat sekolah."),
 dict(kind="clip", s=403.5, e=415.4, zoom=1.12, text="Oh ya? Macam mana pakcik boleh beli kondo 2 bilik bayar habis? Oh, dulu bila pakcik 40-an, pakcik nak tinggal landed. Pakcik pinjam bank overdraft, beli landed. Tapi pakcik tinggal 5 tahun, lepas itu pakcik jual, kerana landed itu dah buat duit."),
 dict(kind="clip", s=415.7, e=432.3, zoom=1.0, push=0.04, text="Jadi dia jual, pakcik ini beli kondo 2 bilik freehold, $900 ribu sahaja. 20 tahun kemudian, Nona jualkan kondo itu, cash $1.7 juta! Pakcik... pakcik dua orang, oh! $1.7 juta dolar cash, 77 tahun. MasyaAllah."),
 dict(kind="still", t=432.1, dur=0.8, zoom=1.2),
 dict(kind="clip", s=432.4, e=439.0, zoom=1.12, text="Jadi, keputusan yang dia buat bila usia 40-an itu, menentukan persaraan yang dia akan hadapi."),
 dict(kind="still", t=466.0, dur=3.4, zoom=1.0, dark=0.5),
]
def make_els(segs, T, E, S):
    els, sfx = [], []
    # hook: two cards + VS
    a = card("$30k", size=96, bg=NAVY, kicker="Pakcik A · 77 tahun"); b = card("$1.7 JUTA", size=96, bg=GOLD, fg=INK, kicker="Pakcik B · 77 tahun", kicker_fg=NAVY)
    els.append(Element(0.0, T(1, 362.6), slide_in(a, (60, 1100), (-500, 0), "lt"))); sfx.append((0.05, "whoosh"))
    els.append(Element(0.3, T(1, 362.6), slide_in(b, (1020, 1100), (500, 0), "rt"))); sfx.append((0.35, "whoosh"))
    els.append(Element(0.7, T(1, 362.6), popin(pill("VS", size=40, bg=RED, fg=WHITE), (540, 1390)))); sfx.append((0.75, "thud"))
    # pakcik A card progressive
    rowsA = lambda n: compare_card("PAKCIK A", ["77 tahun", "Marsiling · 4 bilik HDB", "Beli: $38,000", "Untung cash: $30,000"][:n], highlight=3 if n >= 4 else None)
    els.append(Element(T(1, 362.8), E(2), progressive(rowsA, [(0, (1,)), (T(1, 365.1) - T(1, 362.8), (2,)), (T(1, 367.6) - T(1, 362.8), (3,)), (T(2, 375.6) - T(1, 362.8), (4,))], (60, 980), "lt")))
    sfx += [(T(1, 362.85), "pop"), (T(1, 365.15), "pop"), (T(1, 367.65), "pop"), (T(2, 375.65), "buzz")]
    # curve
    els.append(Element(T(3, 382.0), E(3), popin(curve_img(), (540, 1180)))); sfx.append((T(3, 382.05), "pop"))
    # pakcik B card progressive
    rowsB = lambda n: compare_card("PAKCIK B", ["77 tahun", "Kondo · dah habis bayar", "Cikgu Bahasa Inggeris", "Jual: $1.7 juta cash"][:n], title_bg=GOLD_D, highlight=3 if n >= 4 else None)
    els.append(Element(T(4, 395.5), E(4), progressive(rowsB, [(0, (1,)), (T(4, 396.5) - T(4, 395.5), (2,)), (T(4, 400.9) - T(4, 395.5), (3,))], (1020, 980), "rt")))
    sfx += [(T(4, 395.55), "pop"), (T(4, 396.55), "pop"), (T(4, 400.95), "pop")]
    # timeline
    tl = timeline_img([("40-an", "beli landed"), ("+5 tahun", "jual, untung"), ("Kondo", "freehold, $900k")])
    els.append(Element(T(5, 407.3), E(5), popin(tl, (540, 1150)))); sfx += [(T(5, 407.35), "tick"), (T(5, 412.5), "tick"), (T(5, 414.5), "tick")]
    # counter + stamp
    els.append(Element(T(6, 418.6), T(6, 423.2), popin(tag("Kondo 2 bilik freehold", "$900,000", w=520), (540, 1100)))); sfx.append((T(6, 418.65), "blip"))
    els.append(Element(T(6, 423.3), E(6), counter("$", 0.9, 1.7, " juta", (540, 1110), roll=1.6, size=140))); sfx.append((T(6, 423.3), "counter"))
    els.append(Element(T(6, 425.6), E(6), popin(stamp("CASH · 77 TAHUN"), (540, 1310)))); sfx += [(T(6, 425.65), "thud"), (T(6, 425.8), "kaching")]
    # freeze still: nothing (her reaction)
    # quote
    q = card("Keputusan di usia 40-an menentukan persaraan anda.", size=56, serif=True, bg=NAVY, maxw=900)
    els.append(Element(T(8, 433.2), E(8), popin(q, (540, 1140)))); sfx.append((T(8, 433.25), "whoosh"))
    # end
    ec = end_card("Keputusan 40-an anda, persaraan anda.", "Jom bincang. DM saya di Instagram · TikTok · Facebook")
    els.append(Element(S(9), E(9), popin(ec, (540, 900), hold_fade=False))); sfx.append((S(9) + 0.05, "sting"))
    return els, sfx
run_reel("reel2", spec, make_els, OUT)
