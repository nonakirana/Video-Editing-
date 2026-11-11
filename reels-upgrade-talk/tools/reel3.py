import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reelkit import *
OUT = "/home/user/Video-Editing-/reels-upgrade-talk/reel3-kenapa-takut-upgrade.mp4"
spec = [
 dict(kind="clip", s=20.0, e=25.0, zoom=1.0, gain=5.0, text="Nona, kenapa masyarakat kita ini rata-rata takut nak upgrade ataupun nak naik taraf?"),
 dict(kind="clip", s=26.1, e=37.3, zoom=1.12, text="Memang orang Melayu kita ini berada, beralah, rendah diri, sopan santun. Jadi pada mereka ini, bila kita cakap tentang naik taraf atau upgrade, macam menunjuk. Show off."),
 dict(kind="clip", s=38.0, e=43.2, zoom=1.0, text="Itulah, dia nak lebih daripada orang lain, kan? Dan dia takut, besar periuk, besar keraknya."),
 dict(kind="clip", s=43.8, e=51.4, zoom=1.12, push=0.03, text="Tapi saya rasa, apabila kita fikir tentang keperluan kita di hari tua nanti, perancangan perumahan pada hari ini memainkan peranan yang besar."),
 dict(kind="clip", s=185.8, e=198.5, zoom=1.0, text="Jadi tak semua naik taraf itu tak baik. Memanglah dari segi size tak boleh lawan dengan HDB, tapi dari segi asset class, anda pindah ke satu kelas perumahan yang lebih tinggi daripada perumahan awam."),
 dict(kind="clip", s=199.0, e=202.0, zoom=1.12, text="Tapi bila anda patah balik, sekarang kan dah tak ada cooling period."),
 dict(kind="clip", s=211.4, e=230.1, zoom=1.0, push=0.04, text="Kerana dulu ada 15 bulan cooling period. Selepas penjualan kondo, rumah private anda, perlu rehat 15 bulan sebelum anda masuk ke perumahan awam HDB. Sekarang tak perlu. Jual kondo, jual landed, terus anda boleh pindah ke HDB dengan selonggok cash dalam bank, hasil daripada penjualan rumah private anda."),
 dict(kind="clip", s=230.2, e=233.0, zoom=1.12, text="Jadi ini yang saya rasa, kalau kita mampu, kita boleh."),
 dict(kind="still", t=466.0, dur=3.4, zoom=1.0, dark=0.5),
]
def make_els(segs, T, E, S):
    els, sfx = [], []
    els.append(Element(0.0, E(0), typewriter("Kenapa orang kita takut nak upgrade?", (90, 1040), size=60, cps=30, maxw=900, kicker="Soalan"))); sfx += [(0.1 + i * 0.25, "tick") for i in range(8)]
    # three traits
    for i, (w, t) in enumerate([("beralah", 30.4), ("rendah diri", 31.2), ("sopan santun", 32.0)]):
        els.append(Element(T(1, t), T(1, 36.6), popin(pill(w, size=42, bg=WHITE, fg=NAVY), (60, 1000 + i * 110), "lt"))); sfx.append((T(1, t) + 0.05, "pop"))
    els.append(Element(T(1, 36.7), E(1), popin(stamp("SHOW OFF?", size=84, color=RED, fg=WHITE, angle=6), (540, 1150)))); sfx.append((T(1, 36.75), "thud"))
    els.append(Element(T(2, 41.9), E(2), popin(card("“Besar periuk, besar keraknya.”", size=54, serif=True, bg=NAVY, maxw=900, kicker="Peribahasa"), (540, 1140)))); sfx.append((T(2, 41.95), "whoosh"))
    els.append(Element(T(3, 46.4), E(3), popin(timeline_img([("Hari ini", "perancangan perumahan"), ("Umur 65", "hari tua, selesa")]), (540, 1150)))); sfx += [(T(3, 46.45), "tick"), (T(3, 48.3), "tick")]
    els.append(Element(T(4, 189.8), E(4), popin(icon_card("hdb", "HDB: size menang", s=140), (250, 1130)))); sfx.append((T(4, 189.85), "pop"))
    els.append(Element(T(4, 192.5), E(4), popin(icon_card("condo", "Private: asset class", s=140), (800, 1130)))); sfx.append((T(4, 192.55), "pop"))
    els.append(Element(T(5, 200.4), E(5), strike("15 bulan cooling period", (540, 1140), at=0.5))); sfx += [(T(5, 200.45), "pop"), (T(5, 200.95), "strike")]
    els.append(Element(T(6, 212.3), T(6, 221.0), popin(card("Dulu: tunggu 15 bulan", size=52, bg=NAVY, kicker="Jual private → beli HDB"), (540, 1140)))); sfx.append((T(6, 212.35), "pop"))
    els.append(Element(T(6, 221.3), E(6), popin(pill("Dihapuskan · 28 Julai 2026", size=40, bg=GOLD, fg=INK, icon="tick"), (540, 1030)))); sfx.append((T(6, 221.35), "kaching"))
    els.append(Element(T(6, 222.7), E(6), popin(icon_card("condo", "Jual", s=110), (230, 1240), delay=0.0)))
    els.append(Element(T(6, 222.7), E(6), popin(icon_img("arrow_right", 100, GOLD), (470, 1240), delay=0.2)))
    els.append(Element(T(6, 222.7), E(6), popin(icon_card("hdb", "Terus ke HDB", s=110), (730, 1240), delay=0.35))); sfx += [(T(6, 222.75), "pop"), (T(6, 223.1), "pop")]
    els.append(Element(T(6, 226.2), E(6), popin(pill("+ cash dalam bank", size=38, icon="cash"), (1020, 880), "rt"))); sfx.append((T(6, 226.25), "kaching"))
    els.append(Element(T(7, 231.5), E(7), popin(card("Kalau mampu, kita boleh.", size=72, bg=GOLD, fg=INK, maxw=900), (540, 1140)))); sfx.append((T(7, 231.55), "whoosh"))
    ec = end_card("Mampu ke tidak? Jom kira sama-sama.", "DM saya di Instagram · TikTok · Facebook")
    els.append(Element(S(8), E(8), popin(ec, (540, 900), hold_fade=False))); sfx.append((S(8) + 0.05, "sting"))
    return els, sfx
run_reel("reel3", spec, make_els, OUT)
