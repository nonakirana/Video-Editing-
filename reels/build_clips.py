"""Define the reels cut from the Warna 94.2FM interview and write clips.json.

Times are source-video seconds. Every segment starts on the first word of a
sentence and ends on the last word of one, so nothing is cut mid-sentence.
"""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
words = json.load(open(os.path.join(HERE, "transcript_words.json")))

# transcription fixes (speech-to-text mishears names and Singapore terms)
FIX = {
    "Nuna": "Nona", "Nuna,": "Nona,", "Nola": "Nona", "Tempenis": "Tampines", "Interchain": "Interchange",
    "poliklinik.": "poliklinik.", "Polyklinik.": "Poliklinik.", "Riverville": "Rivervale",
    "Maisonet": "Maisonette", "maisonnet": "maisonette", "maisonnet,": "maisonette,", "eksekutif": "executive",
    "apartman": "apartment", "apartemen.": "apartment.", "RM300": "$300", "RM500,000": "$500,000",
    "-penak,": "-pinak,", "bertahulian": "berkelayakan", "pesaran": "persaraan", "mengembirakan": "menggembirakan",
    "capaikan": "capai", "tanggalah": "tangga lah", "penyakit,": "penyiar,", "penyakit": "penyiar",
    "TG": "Tiji", "RZ": "Arzak", "islam": "silap", "budget": "bajet", "agent": "ejen", "government": "kerajaan",
    "Pelajir.": "pledging.",
}
DROP = {"Seperti"}  # stray fragment at 10:50.0 (speech-to-text artefact before "pledging")
FIX_SEQ = {("tak", "silap"): ("kalau tak", "silap")}

def get_words(a, b, breaks=()):
    out = []
    for w in words:
        if a - 0.05 <= w["s"] <= b + 0.05:
            t = w["w"].strip()
            t = FIX.get(t, t)
            if t in DROP and w["s"] > 649: continue
            if t.startswith("-") or t.startswith(",") or t.startswith("%"):
                if out: out[-1]["w"] += t; out[-1]["e"] = w["e"]; continue
            out.append({"w": t, "s": w["s"], "e": w["e"], "brk": any(abs(w["s"] - x) < 0.06 for x in breaks)})
    for i in range(len(out) - 1):
        k = (out[i]["w"], out[i + 1]["w"])
        if k in FIX_SEQ: out[i]["w"], out[i + 1]["w"] = FIX_SEQ[k]
    return out

def sub(s, e, en): return {"s": s, "e": e, "en": en}
def pop(t, text, style="cream", **kw): return dict(t=t, text=text, style=style, **kw)

CTA_BIG = "Perlukah anda upgrade?"
CTA_SMALL = "Kira your numbers dulu. WhatsApp Nona 8268 1111 atau DM sahaja."
COMMON = dict(name="Nona Kirana", role="Barakah Homes Realty · PropNex", handle="@nonakirana",
              cta_big=CTA_BIG, cta_small=CTA_SMALL, face=[540, 1100])

clips = []

# 1 ---------------------------------------------------------------- the pivot
clips.append(dict(COMMON, id="R01", slug="dari-dj-ke-ejen-rumah",
    title="Dulu jual suara, sekarang jual rumah",
    segments=[[168.26, 178.98], [200.25, 229.63]], breaks=[178.28, 200.25],
    kicker="13 tahun selepas radio", hook=["Dulu jual *suara*.", "Sekarang jual *rumah*."],
    popups=[pop(176.0, "Jual Suara", "navy", sub="Warna 94.2FM", dur=1.7), pop(177.9, "Jual Rumah", "gold", sub="Barakah Homes"),
            pop(215.2, "Kepuasan berbeza", "cream", size=84, sub="a different kind of fulfilment"),
            pop(228.4, "Matlamat kehidupan", "gold", size=80, sub="life goals")],
    subs=[sub(168.26, 171.2, "Good afternoon, Tiji and Arzak."),
          sub(171.7, 175.1, "No, today I'm here as a property agent."),
          sub(175.1, 178.3, "Back then I sold my voice. Now I sell homes."),
          sub(178.3, 179.0, "Masya Allah!"),
          sub(200.25, 206.0, "I never expected it. 13 years ago I changed careers."),
          sub(206.5, 214.7, "As a property agent I get to help so many people solve problems and reach their property dreams."),
          sub(215.0, 216.2, "So the fulfilment is different."),
          sub(216.25, 222.5, "On radio, our happiness came from making listeners happy."),
          sub(222.8, 229.63, "As an agent, it comes from helping my clients reach their life goals.")]))

# 2 ------------------------------------------------- upgrade does not mean private
clips.append(dict(COMMON, id="R02", slug="upgrade-tak-semestinya-private",
    title="Upgrade tak semestinya private",
    segments=[[240.72, 242.66], [244.48, 281.5]],
    kicker="Perlukah kita upgrade?", hook=["Upgrade tak semestinya", "pindah ke *private*."],
    popups=[pop(246.7, "Tak semestinya private", "cream", size=76, sub="not necessarily private"),
            pop(252.7, "3-bilik BTO", "gold", sub="where many start"),
            pop(271.3, "5-bilik?", "navy", sub="can I afford it?"),
            pop(278.1, "Jangan overstretch", "gold", size=80, sub="don't over-borrow")],
    subs=[sub(240.72, 242.66, "Why do people upgrade? What is it?"),
          sub(244.48, 249.5, "When we talk about upgrading, it doesn't have to mean moving to private property."),
          sub(250.0, 253.9, "Some people start with a 3-room BTO."),
          sub(254.2, 261.9, "Then once the kids come, they need more space and comfort for the family, and they come to see me."),
          sub(261.96, 272.4, "\"Nona, on my salary, single income, wife at home, can I get enough loan to upgrade to a 5-room?\""),
          sub(272.6, 275.5, "That's where I do a detailed calculation,"),
          sub(275.9, 281.5, "look at their budget, because we don't want them to overstretch or pay more than they can afford.")]))

# 3 ------------------------------------------------- housing and retirement are linked
clips.append(dict(COMMON, id="R03", slug="perumahan-dan-persaraan",
    title="Perumahan dan persaraan berkait rapat",
    segments=[[310.72, 348.42]],
    kicker="13 tahun bantu orang jual beli rumah", hook=["Rumah di usia *30-an*", "menentukan *persaraan*."],
    popups=[pop(314.7, "Perumahan = Persaraan", "gold", size=70, sub="housing shapes retirement"),
            pop(325.2, "Berani ≠ Mampu", "cream", size=90, sub="courage is not affordability"),
            pop(336.3, "Executive Maisonette", "navy", size=70, sub="the underrated upgrade"),
            pop(347.0, "Privacy macam landed", "cream", size=74, sub="landed-style privacy")],
    subs=[sub(310.72, 314.1, "In my opinion, after 13 years helping people buy and sell,"),
          sub(314.7, 316.7, "housing and retirement are closely linked."),
          sub(317.1, 323.5, "The decisions we make in our 30s and 40s decide what our retirement looks like."),
          sub(323.9, 327.1, "Some people have the courage but not the means."),
          sub(327.2, 329.8, "They want to buy a condo but actually can't afford it."),
          sub(330.1, 332.1, "So it's hard. What can Nona do?"),
          sub(332.1, 334.2, "Usually I look at it from the budget."),
          sub(334.9, 337.6, "Say they can only afford an Executive Maisonette."),
          sub(337.6, 339.7, "Then no need to go all the way to private."),
          sub(339.7, 346.0, "Because an Executive Maisonette is a type of housing I think is great. It has stairs."),
          sub(347.0, 348.42, "Privacy like a landed home.")]))

# 4 ------------------------------------------------- private then back to HDB
clips.append(dict(COMMON, id="R04", slug="strategi-private-ke-hdb",
    title="Strategi: private dulu, patah balik HDB",
    segments=[[356.54, 390.14]],
    kicker="Bagi yang mampu & berani", hook=["Private dulu,", "patah balik *HDB*."],
    popups=[pop(364.2, "Patah balik HDB", "cream", size=84, sub="right-size later"),
            pop(369.4, "Akaun persaraan penuh", "gold", size=68, sub="retirement account topped up"),
            pop(375.4, "Your numbers dulu", "navy", size=80, sub="numbers before decisions"),
            pop(386.4, "Ejen berlesen", "gold", size=86, sub="licensed & qualified")],
    subs=[sub(356.54, 359.4, "I do recommend they move to private property,"),
          sub(359.44, 365.8, "because from experience, those who go private and later downsize back to HDB"),
          sub(366.2, 368.8, "end up with more cash left over,"),
          sub(368.8, 371.2, "so we top up the retirement account too."),
          sub(371.2, 373.7, "Then at 65, CPF LIFE starts."),
          sub(374.0, 377.5, "All of this I help with. We look at your numbers first,"),
          sub(377.5, 381.6, "before deciding which upgrade suits you and your family."),
          sub(382.2, 386.2, "Before making this decision, do the sums and discuss first."),
          sub(386.4, 390.14, "Listen to a qualified, licensed agent.")]))

# 5 ------------------------------------------------- go for the biggest HDB
clips.append(dict(COMMON, id="R05", slug="go-for-the-biggest-hdb",
    title="Go for the biggest HDB",
    segments=[[423.02, 465.14]],
    kicker="Nasihat Nona", hook=["Kalau mampu,", "go for the *biggest HDB*."],
    popups=[pop(426.3, "Biggest HDB", "gold", size=96, sub="jumbo · EM · EA"),
            pop(435.5, "Dah tak buat lagi", "cream", size=80, sub="no longer built"),
            pop(447.9, "Rare item", "navy", size=96, sub="scarcity = value"),
            pop(457.8, "No longer in production", "gold", size=64, sub="the last EMs are ~36 years old")],
    subs=[sub(423.02, 427.7, "Like I said, if you can afford it, I always say go for the biggest HDB."),
          sub(427.8, 434.0, "Meaning, if you can buy the biggest, buy a jumbo, an Executive Maisonette, an Executive Apartment. Why?"),
          sub(434.18, 437.1, "The government no longer builds these."),
          sub(437.68, 443.1, "The last Executive Maisonettes I know of are at Rivervale Crescent, about 36 years old now."),
          sub(443.6, 445.5, "Since then they haven't built any."),
          sub(445.54, 448.9, "So if you buy one, people say you're buying a rare item."),
          sub(449.6, 455.6, "Because when we're old, the young ones will say: \"Eh auntie, your house has stairs! So unique.\""),
          sub(455.6, 459.5, "And they'll pay for a home that's no longer in production."),
          sub(459.5, 461.6, "If you want one, the government isn't building more."),
          sub(461.56, 465.14, "So for those who can afford it, I'd say buy the biggest.")]))

# 6 ------------------------------------------------- the Tampines uncle story
clips.append(dict(COMMON, id="R06", slug="kisah-pakcik-tampines",
    title="Kisah pakcik Tampines: $300k cash & CPF LIFE penuh",
    segments=[[465.64, 476.20], [487.10, 520.90]],
    kicker="Kisah benar pelanggan", hook=["3-bilik → EA → 3-bilik.", "Lebih *$300k* cash di bank."],
    popups=[pop(469.8, "3-bilik Tampines", "cream", size=80, sub="chapter 1: newlyweds"),
            pop(473.8, "Executive Apartment", "gold", size=70, sub="chapter 2: three daughters"),
            pop(497.9, "Right-size", "navy", size=96, sub="chapter 3: near the polyclinic"),
            pop(514.4, "$300,000 cash", "gold", size=90, sub="plus full retirement account"),
            pop(519.5, "CPF LIFE penuh", "cream", size=84, sub="full monthly payout for life", dur=1.5)],
    subs=[sub(465.64, 467.6, "I have a case. This uncle,"),
          sub(467.66, 470.9, "when he was newly married, bought a 3-room in Tampines."),
          sub(470.94, 476.2, "When he had three daughters, he moved to an Executive Apartment, also in Tampines."),
          sub(487.1, 490.6, "When he reached his 60s, 68 if I'm not mistaken,"),
          sub(490.78, 493.9, "he said: it's just auntie and me now. The kids have all moved out."),
          sub(493.96, 496.1, "This Executive Apartment is too big."),
          sub(496.5, 497.5, "So what did he want?"),
          sub(497.56, 501.9, "A 3-room near Tampines Interchange, near the polyclinic."),
          sub(502.3, 505.0, "Because when you're older, collecting medicine nearby is easier."),
          sub(505.16, 508.1, "So what did Nona do? I sold the Executive Apartment."),
          sub(508.3, 512.3, "We moved to a 3-room right next to Tampines Polyclinic."),
          sub(512.48, 515.7, "And in the bank he had over $300,000 cash."),
          sub(516.0, 517.7, "His Retirement Account was full too."),
          sub(517.9, 520.9, "Meaning every month he gets the full CPF LIFE payout.")]))

# 7 ------------------------------------------------- pay it off before 55
clips.append(dict(COMMON, id="R07", slug="bayar-habis-sebelum-55",
    title="Bayar habis sebelum 55",
    segments=[[528.52, 562.68]],
    kicker="Untuk anda yang 30-an, 40-an", hook=["Stretch boleh. Tapi", "*bayar habis* sebelum *55*."],
    popups=[pop(535.4, "Bayar habis sebelum 55", "gold", size=66, sub="clear it before 55"),
            pop(547.3, "CPF contribution ↓", "cream", size=80, sub="drops after 55"),
            pop(553.0, "$1,000 → $500", "navy", size=90, sub="the other half comes from cash"),
            pop(559.6, "Top up cash", "gold", size=90, sub="what we want to avoid")],
    subs=[sub(528.52, 531.6, "For those of you who may have the means, in your 30s and 40s,"),
          sub(531.7, 533.9, "and feel you can stretch a little,"),
          sub(533.9, 537.3, "you must have a plan to pay it off before 55."),
          sub(538.2, 538.8, "Why?"),
          sub(538.98, 543.2, "At 55 our Retirement Account kicks in."),
          sub(543.2, 546.8, "Some don't meet the Full Retirement Sum, so all sorts of problems."),
          sub(546.8, 549.6, "And our CPF contribution also drops."),
          sub(549.54, 552.1, "If you used to have $1,000 to pay the home loan,"),
          sub(552.1, 556.1, "later it drops by 50% to only $500."),
          sub(556.06, 557.4, "So $500 has to come out in cash."),
          sub(557.4, 560.6, "That's when you hear people say: eh, I have to top up cash for my house."),
          sub(561.2, 562.68, "That's what we want to avoid.")]))

# 8 ------------------------------------------------- not a jual-beli-bye-bye agent
clips.append(dict(COMMON, id="R08", slug="bukan-ejen-jual-beli-bye-bye",
    title="Bukan ejen jual, beli, bye-bye",
    segments=[[566.50, 588.76]],
    kicker="Cara Nona bekerja", hook=["Bukan ejen", "jual, beli, *bye-bye*."],
    popups=[pop(570.2, "Jual. Beli. Bye-bye.", "navy", size=76, sub="the usual way"),
            pop(577.1, "Tanggungjawab", "gold", size=86, sub="responsibility"),
            pop(585.7, "55 = rumah habis bayar", "cream", size=66, sub="the plan")],
    subs=[sub(566.5, 568.0, "All of this, Nona will help with,"),
          sub(568.0, 571.4, "because usually a property agent does the sale and then it's bye-bye."),
          sub(571.66, 575.3, "Bye, see you around. Usually that's the job."),
          sub(575.58, 579.8, "But for me, I have a responsibility to help them plan."),
          sub(580.0, 584.1, "Especially if they're in their 30s or 40s: yes, take the 25-year loan."),
          sub(584.3, 585.0, "Then what?"),
          sub(585.66, 588.76, "The plan is: by 55, the house is fully paid.")]))

# 9 ------------------------------------------------- kakak 55 abang 60 + property pledging
clips.append(dict(COMMON, id="R09", slug="kakak-55-abang-60-property-pledging",
    title="Kakak 55, Abang 60, dan magic trick CPF",
    segments=[[589.14, 650.78]],
    kicker="Kisah benar pelanggan", hook=["Nak *downgrade*, tapi", "anak-anak tak nak keluar."],
    popups=[pop(592.1, "Kakak 55 · Abang 60", "cream", size=74, sub="still paying the loan"),
            pop(598.6, "Anak tunggu BTO", "navy", size=80, sub="nobody can move out"),
            pop(616.1, "Terperangkap", "gold", size=90, sub="can't downgrade, loan still running"),
            pop(631.2, "Magic trick", "cream", size=96, sub="property pledging"),
            pop(636.9, "Property pledging", "gold", size=74, sub="use retirement savings to clear the loan"),
            pop(644.5, "Polisi CPF", "navy", size=90, sub="check if you qualify")],
    subs=[sub(589.14, 592.1, "I once visited a home where the wife was fussing with her husband."),
          sub(592.06, 593.7, "She's 55, he's 60."),
          sub(593.72, 595.1, "Why was she fussing?"),
          sub(595.2, 596.8, "\"We actually want to downgrade,"),
          sub(596.8, 602.4, "but look at these kids, all waiting for BTO, just back from studies, nobody wants to move out."),
          sub(602.38, 603.8, "How can we downgrade?\""),
          sub(604.04, 607.7, "They live in an Executive Maisonette: four bedrooms, comfortable."),
          sub(607.9, 609.4, "But the loan is still there."),
          sub(609.4, 612.2, "\"How do we pay? My husband no longer works.\""),
          sub(612.18, 615.4, "Logically they should downgrade: move to a 3-room, pay it off."),
          sub(615.42, 619.2, "But their life situation doesn't allow them to downgrade,"),
          sub(620.18, 622.7, "because the kids won't leave, and you love your kids."),
          sub(622.88, 627.2, "That's why: imagine if they'd bought early and planned to pay it off,"),
          sub(627.2, 629.9, "they wouldn't need to sell under pressure."),
          sub(629.9, 632.0, "But Nona had a magic trick."),
          sub(632.0, 635.2, "What I told them then: do property pledging."),
          sub(635.89, 640.3, "Property pledging: take money from your retirement savings to pay off the loan."),
          sub(640.95, 643.7, "This is one option we can take,"),
          sub(643.7, 645.8, "but it's a CPF policy."),
          sub(645.8, 650.78, "You need to know whether or not you qualify for property pledging.")]))

for c in clips:
    c["words"] = sum((get_words(a, b, c.get("breaks", ())) for a, b in c["segments"]), [])
    c["in"], c["out"] = c["segments"][0][0], c["segments"][-1][1]
    c["duration"] = round(sum(b - a for a, b in c["segments"]), 1)
json.dump(clips, open(os.path.join(HERE, "clips.json"), "w"), indent=1, ensure_ascii=False)
for c in clips:
    print(c["id"], f'{c["duration"]:5.1f}s', c["title"], "|", " ".join(w["w"] for w in c["words"])[:110], "...")
