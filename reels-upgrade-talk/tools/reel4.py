import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reelkit import *
OUT = "/home/user/Video-Editing-/reels-upgrade-talk/reel4-3-soalan-sebelum-beli-kondo.mp4"
ITEMS = ["Boleh bertahan 7–10 tahun?", "Hutang habis bayar umur 55?", "Ada buffer untuk what-ifs?"]
spec = [
 dict(kind="clip", s=233.1, e=236.5, zoom=1.0, text="Anda buat perkiraan, tengok hutang bank, kelayakan anda,"),
 dict(kind="clip", s=236.6, e=246.2, zoom=1.12, text="dan pastikan anda boleh duduk sekurang-kurangnya 7 hingga 10 tahun. Jangan dengar cakap orang: beli kondo 2 tahun, CPF dah habis, kena top up cash, pening kepala."),
 dict(kind="clip", s=246.6, e=255.2, zoom=1.0, push=0.03, text="Mesti ada apa yang saya panggil sustainability. Kalau saya rasa anda mampu untuk bertahan di kondo itu 7 hingga 10 tahun, saya rasa ia merupakan satu pelaburan yang baik."),
 dict(kind="clip", s=272.6, e=282.7, zoom=1.12, text="Dalam tim saya, namanya Barakah Homes. Dan kami pastikan apabila mereka naik taraf ke rumah private, ada perancangan untuk memastikan hutang rumah habis bayar pada usia 55 tahun."),
 dict(kind="clip", s=283.1, e=295.9, zoom=1.0, text="Kalau tidak, berlaku kematian, penyakit-penyakit kronik, ataupun mereka jadi vegetable, buang kerja pun. Jadi kita akan bantu mereka untuk pastikan ada buffer. Jadi mereka tak perlu jual rumah waktu terdesak."),
 dict(kind="clip", s=296.1, e=300.4, zoom=1.05, text="Bayangkan anda beli rumah kondo itu 2–3 tahun, tiba-tiba satu orang kena penyakit kanser."),
 dict(kind="clip", s=305.3, e=317.0, zoom=1.05, push=0.02, text="Tapi kalau kita ada perancangan kewangan yang baik, kita ada buffer. Buffer itu boleh bantu untuk bayar duit rumah sambil kita jalani rawatan. Dan bila-bila masanya yang sesuai untuk kita jual, kita jual dan patah balik ke rumah HDB."),
 dict(kind="clip", s=317.3, e=324.0, zoom=1.12, text="Jadi perancangan ini perlu, kerana ramai yang ghairah, mereka main terjun saja, masuk beli, tapi mereka tak fikir tentang kecemasan."),
 dict(kind="clip", s=462.6, e=468.4, zoom=1.0, text="Okey, anda boleh cari saya di Facebook, Instagram, TikTok, atau hubungi saya terus."),
 dict(kind="still", t=466.0, dur=3.4, zoom=1.0, dark=0.5),
]
def make_els(segs, T, E, S):
    els, sfx = [], []
    els.append(Element(0.0, E(0), popin(card("3 soalan sebelum beli kondo", size=66, bg=NAVY, kicker="Checklist", maxw=900), (540, 1120)))); sfx.append((0.05, "whoosh"))
    # checklist phase 1
    els.append(Element(T(1, 238.9), E(2), checklist(ITEMS, [T(2, 247.9) - T(1, 238.9)], (60, 1000), "lt"))); sfx += [(T(1, 238.95), "pop"), (T(2, 247.95), "ding")]
    els.append(Element(T(1, 243.4), E(1), popin(pill("CPF habis → top-up cash", size=36, bg=RED, fg=WHITE), (1020, 860), "rt"))); sfx.append((T(1, 243.45), "buzz"))
    els.append(Element(T(2, 247.9), E(2), popin(pill("SUSTAINABILITY", size=38), (1020, 860), "rt")))
    # Barakah lower third + checklist phase 2
    els.append(Element(T(3, 273.4), E(3), slide_in(lower_third("Barakah Homes Realty", "Perancangan sebelum naik taraf"), (60, 1330), (-300, 0), "lt")))
    els.append(Element(T(3, 279.5), E(4), checklist(ITEMS, [-1, T(3, 282.0) - T(3, 279.5), T(4, 292.3) - T(3, 279.5)], (60, 1000), "lt"))); sfx += [(T(3, 282.05), "ding"), (T(4, 292.35), "ding")]
    els.append(Element(T(4, 284.2), T(4, 291.5), popin(icon_card("shield", "Buffer kecemasan", s=120), (1020, 780), "rt"))); sfx.append((T(4, 284.25), "pop"))
    # recap + save
    els.append(Element(T(7, 318.4), E(7), checklist(ITEMS, [-1, -1, -1], (60, 1000), "lt"))); sfx.append((T(7, 318.45), "ding"))
    els.append(Element(T(7, 321.5), E(7), popin(pill("Simpan post ini", size=38, bg=GOLD, fg=INK), (1020, 880), "rt"))); sfx.append((T(7, 321.55), "pop"))
    for i, (ic, t) in enumerate([("fb", 464.1), ("ig", 464.6), ("tt", 465.2)]):
        els.append(Element(T(8, t), E(8), popin(icon_img(ic, 130), (330 + i * 210, 1150)))); sfx.append((T(8, t) + 0.05, "pop"))
    ec = end_card("Simpan checklist ini sebelum tandatangan apa-apa.", "DM saya di Instagram · TikTok · Facebook")
    els.append(Element(S(9), E(9), popin(ec, (540, 900), hold_fade=False))); sfx.append((S(9) + 0.05, "sting"))
    return els, sfx
run_reel("reel4", spec, make_els, OUT)
