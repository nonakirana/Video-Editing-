import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reelkit import *

OUT = sys.argv[1] if len(sys.argv) > 1 else "/home/user/Video-Editing-/reels-upgrade-talk/reel1-kakak-downgrade.mp4"
WD = os.path.join(SP, "work", "reel1")

spec = [
 dict(kind="clip", s=51.9, e=58.7, zoom=1.0, push=0.03, text="Kerana Nona juga ada satu kes di mana, Kakak ini comel lah. Dia kata, saya selalu tengok Nona di Facebook buat live. Jadi macam tergerak lah, Kakak nak downgrade."),
 dict(kind="clip", s=59.2, e=65.8, zoom=1.12, text="Umur Kakak berapa? 48. Oh, Kakak nak downgrade rumah berapa bilik? Oh, pindah rumah 4 bilik saja, daripada 5 bilik ke 4 bilik."),
 dict(kind="clip", s=66.2, e=74.9, zoom=1.0, text="Bila Nona tengok income, pendapatan keluarganya, suaminya bergaji besar. Dan dia mampu sebenarnya untuk pindah ke rumah private."),
 dict(kind="clip", s=75.4, e=80.4, zoom=1.12, text="Jadi dia kata tak terfikir, Kakak call kau nak downgrade, yang kau suruh aku upgrade itu apa hal?"),
 dict(kind="still", t=80.3, dur=0.9, zoom=1.2),
 dict(kind="clip", s=90.4, e=100.3, zoom=1.0, push=0.03, text="Bayangkan, pada ketika itu rumah 5 bilik di Jurong West rata-rata harganya dalam $650 ribu. Kalau Nona pindah ke rumah 4 bilik, $500 ribu memang boleh bayar habis, tak ada masalah."),
 dict(kind="clip", s=110.2, e=119.9, zoom=1.12, text="Jadi Nona belikan mereka kondo di kawasan Jurong West juga pada $1.1 juta. Bulan-bulan Abang bayar gunakan CPF, tak perlu top up sebarang cash, kerana duit CPF Abang cukup."),
 dict(kind="clip", s=120.0, e=132.5, zoom=1.0, push=0.04, text="6 tahun kemudian, kondonya sekarang nilainya $1.6 juta. $500 ribu daripada $1.1 juta. Jadi dalam masa 5 tahun, dia naik $500 ribu!"),
 dict(kind="clip", s=139.6, e=146.0, zoom=1.12, text="Jadi Kakak sekarang sangat gembira. Hari-hari boleh pandang swimming pool... Gym! Gym dia singgah saja!"),
 dict(kind="clip", s=154.8, e=162.5, zoom=1.0, push=0.03, text="Kalau Kakak patah balik, kurangnya Kakak ada $500 ribu lebih cash, disebabkan oleh capital appreciation kondo tersebut."),
 dict(kind="still", t=466.0, dur=3.4, zoom=1.0, dark=0.5),
]
def make_els(segs, T, E, S):
    els, sfxe = [], []
    # hook
    h1 = card("Dia telefon nak DOWNGRADE.", size=64, kicker="Kisah sebenar", maxw=900)
    h2 = card("Saya suruh dia UPGRADE.", size=64, bg=GOLD, fg=INK, maxw=900)
    els.append(Element(0.0, 3.4, popin(h1, (540, 1120)))); sfxe.append((0.05, "whoosh"))
    els.append(Element(0.7, 3.4, popin(h2, (540, 1290)))); sfxe.append((0.75, "whoosh"))
    # seg1: age + rooms
    els.append(Element(T(1, 60.3), E(1), popin(pill("48 tahun", size=44), (1030, 920), "rt"))); sfxe.append((T(1, 60.35), "pop"))
    els.append(Element(T(1, 64.4), E(1), popin(icon_card("hdb", "5 bilik"), (250, 1130))))
    els.append(Element(T(1, 64.4), E(1), popin(icon_img("arrow_right", 110, RED), (540, 1130), delay=0.15)))
    els.append(Element(T(1, 64.4), E(1), popin(icon_card("hdb", "4 bilik", s=130), (830, 1130), delay=0.3))); sfxe += [(T(1, 64.45), "pop"), (T(1, 64.75), "pop")]
    # seg2: income + private
    els.append(Element(T(2, 71.0), E(2), popin(pill("Pendapatan keluarga: kukuh", size=38, bg=WHITE, fg=NAVY, icon="tick"), (540, 1100)))); sfxe.append((T(2, 71.05), "pop"))
    els.append(Element(T(2, 74.1), E(2), popin(icon_card("condo", "Rumah private"), (540, 1270)))); sfxe.append((T(2, 74.15), "pop"))
    # freeze: apa hal
    els.append(Element(S(4), E(4), popin(card("APA HAL?!", size=110, bg=GOLD, fg=INK, serif=False), (540, 1100)))); sfxe.append((S(4) + 0.02, "thud"))
    # seg5: Jurong West + price tags
    els.append(Element(T(5, 93.2), E(5), popin(pill("Jurong West", icon="pin", size=42, bg=NAVY, fg=WHITE), (60, 620), "lt"))); sfxe.append((T(5, 93.25), "pop"))
    els.append(Element(T(5, 95.0), E(5), popin(tag("5 bilik HDB", "$650,000", w=440), (60, 1000), "lt"))); sfxe.append((T(5, 95.05), "blip"))
    els.append(Element(T(5, 98.2), E(5), popin(tag("4 bilik HDB", "$500,000", w=440), (1020, 1000), "rt"))); sfxe.append((T(5, 98.25), "blip"))
    # seg6: condo 1.1M + CPF
    els.append(Element(T(6, 113.0), E(6), popin(tag("Kondo · Jurong West", "$1.1 juta", w=520), (60, 1000), "lt"))); sfxe.append((T(6, 113.05), "kaching"))
    els.append(Element(T(6, 116.6), E(6), popin(icon_card("card", "CPF · top-up cash: $0", s=120), (1020, 1000), "rt"))); sfxe.append((T(6, 116.65), "pop"))
    # seg7: counter + stamp
    els.append(Element(T(7, 122.0), E(7), counter("$", 1.1, 1.6, " juta", (540, 1110), roll=1.6, size=140))); sfxe.append((T(7, 122.0), "counter"))
    els.append(Element(T(7, 125.8), E(7), popin(stamp("+$500,000"), (540, 1310)))); sfxe.append((T(7, 125.85), "thud")); sfxe.append((T(7, 126.0), "kaching"))
    # seg8: pool
    els.append(Element(T(8, 141.3), E(8), popin(icon_card("pool", "Swimming pool", s=140), (540, 1120)))); sfxe.append((T(8, 141.35), "pop"))
    # seg9: cash + lower third
    els.append(Element(T(9, 157.3), E(9), popin(pill("+$500k CASH", size=56, icon="cash"), (540, 1080)))); sfxe.append((T(9, 157.35), "kaching"))
    els.append(Element(T(9, 159.2), E(9), slide_in(lower_third("Capital appreciation", "Nilai kondo naik dalam 5–6 tahun"), (60, 1330), (-300, 0), "lt")))
    # end card
    ec = end_card("Nak buat kira-kira dulu sebelum upgrade?", "DM saya di Instagram · TikTok · Facebook")
    els.append(Element(S(10), E(10), popin(ec, (540, 900), hold_fade=False))); sfxe.append((S(10) + 0.05, "sting"))

    return els, sfxe
run_reel("reel1", spec, make_els, OUT)
