"""Build STORYBOARD.md (clip proposal + storyboard + captions) and storyboard.png from clips.json and rendered reels."""
import json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
clips = json.load(open(os.path.join(HERE, "clips.json")))
OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "output")

def tc(s):
    m, sec = divmod(s, 60); return f"{int(m):02d}:{sec:05.2f}"

def clip_time(c, src_t):
    """source seconds -> seconds into the finished reel"""
    pre = 0.25; acc = 0.0
    for i, (a, b) in enumerate(c["segments"]):
        a2 = a - (pre if i == 0 else 0.12); b2 = b + (0.55 if i == len(c["segments"]) - 1 else 0.18)
        if a2 - 0.3 <= src_t <= b2 + 0.3: return acc + (src_t - a2)
        acc += b2 - a2
    return None

# ---------- hand-written post copy ----------
POSTS = {
"R01": dict(angle="Origin story. Warm, personal, high shareability among radio listeners who remember her voice.",
    caption="Dulu saya jual suara. Sekarang saya jual rumah. 🎙️➡️🏠\n\n13 tahun lepas saya tukar kerjaya. Kepuasan dia berbeza: dulu gembira bila pendengar happy, sekarang gembira bila pelanggan capai matlamat kehidupan mereka.\n\nTerima kasih Warna 94.2FM, Tiji & Arzak, kerana jemput saya balik ke studio. Rindu!\n\n13 years ago I swapped the mic for a licence. Different job, same purpose: helping people get to where they want to be.",
    tags="#NonaKirana #BarakahHomes #PropNex #Warna942 #EjenRumah #RealEstateSingapore #PropertyAgentSG #HDB #KerjayaBaru"),
"R02": dict(angle="Myth-buster. Reframes 'upgrade' for young HDB families; invites the DM.",
    caption="Upgrade tak semestinya pindah ke private. 🏠\n\nRamai bermula dengan 3-bilik BTO, kemudian bila anak dah ramai, mereka perlukan ruang. Soalan biasa: \"Nona, gaji seorang je, mampu tak nak upgrade ke 5-bilik?\"\n\nJawapan saya sentiasa bermula dengan kira-kira yang terperinci. Kita tak nak overstretch. Kita tak nak bayar hutang rumah lebih daripada apa yang kita mampu.\n\nUpgrading doesn't have to mean private property. It means the right-sized home for this chapter, within a budget that lets you sleep at night.\n\nNak kira your numbers? DM saya \"UPGRADE\".",
    tags="#Upgrade #HDB #BTO #RumahSG #BarakahHomes #PropNex #NonaKirana #SingaporeProperty #HDBUpgrade #PerancanganKewangan"),
"R03": dict(angle="Big-picture insight. Links housing to retirement, and introduces the Executive Maisonette as the smart middle option.",
    caption="Perumahan dan persaraan berkait rapat. 🔗\n\nKeputusan rumah yang kita buat di usia 30-an dan 40-an akan menentukan persaraan kita nanti.\n\nAda orang ada keberanian tapi tak ada kemampuan: nak beli kondo, tapi sebenarnya tak mampu. Kalau bajet hanya cukup untuk Executive Maisonette, tak payah paksa diri ke private. EM ada tangga, ada privacy macam rumah landed, dan ia satu jenis perumahan yang sangat baik.\n\nYour housing decisions in your 30s and 40s shape your retirement. Courage is not the same as affordability.",
    tags="#Persaraan #CPF #ExecutiveMaisonette #HDB #Kondo #BarakahHomes #PropNex #NonaKirana #RetirementPlanningSG #SingaporeProperty"),
"R04": dict(angle="Strategy reel for the ones who can afford private. Ends on the licensed-agent reminder.",
    caption="Bagi yang mampu dan berani: private dulu, patah balik HDB kemudian. 📈\n\nBerdasarkan pengalaman saya, mereka yang pindah ke private dan kemudian patah balik ke HDB selalunya ada lebihan cash yang lebih. Akaun persaraan dipenuhkan, dan bila 65, CPF LIFE bermula dengan selesa.\n\nTapi semua ini bermula dengan satu perkara: tengok your numbers dulu. Kira-kira, berbincang, dan dengar daripada ejen yang berkelayakan dan berlesen.\n\nFor those with the means and the appetite: private first, right-size back to HDB later, with your retirement account full. But numbers before decisions, always.",
    tags="#PrivateProperty #HDB #CPFLIFE #Persaraan #BarakahHomes #PropNex #NonaKirana #PropertyStrategy #SingaporeProperty #EjenBerlesen"),
"R05": dict(angle="Punchy advice with a memorable line in English. Strong save/share value.",
    caption="Kalau anda mampu, I always say: go for the biggest HDB. 🏢\n\nJumbo. Executive Maisonette. Executive Apartment. Kenapa? Kerana pemerintah dah tak buat lagi. EM yang terakhir yang saya tahu di Rivervale Crescent, lebih kurang 36 tahun dah.\n\nAnda beli rare item. Nanti bila dah tua, budak-budak baru akan kata: \"Eh auntie, rumahnya ada tangga!\" Dan mereka akan bayar untuk rumah yang no longer in production.\n\nIf you can afford it, buy the biggest HDB you can. They aren't making these anymore.",
    tags="#BiggestHDB #ExecutiveMaisonette #ExecutiveApartment #JumboFlat #HDB #BarakahHomes #PropNex #NonaKirana #SingaporeProperty #RareItem"),
"R06": dict(angle="Client story with a number. The most 'proof' of the set; good for carousel repurposing too.",
    caption="Kisah pakcik Tampines. 🏘️\n\nBaru kahwin: 3-bilik di Tampines. Tiga anak perempuan: pindah ke Executive Apartment, Tampines juga. Umur 68, anak-anak dah keluar: \"Rumah ni terlalu besar.\"\n\nApa yang kami buat? Jual EA, pindah ke 3-bilik sebelah Tampines Polyclinic. Dalam bank: lebih $300,000 cash. Retirement Account penuh. Bulan-bulan dapat CPF LIFE yang penuh.\n\nItu yang saya maksudkan bila saya kata perumahan dan persaraan berkait rapat.\n\n3-room, then Executive Apartment, then back to a 3-room next to the polyclinic: $300k+ in cash and a full Retirement Account. That's what a housing journey can do when it's planned.",
    tags="#KisahPelanggan #Tampines #RightSizing #CPFLIFE #RetirementAccount #HDB #BarakahHomes #PropNex #NonaKirana #SingaporeProperty"),
"R07": dict(angle="Practical warning for 30s-40s buyers. The $1,000 to $500 contrast is the hook.",
    caption="Stretch boleh. Tapi mesti ada perancangan untuk bayar habis sebelum 55. ⏳\n\nKenapa 55? Retirement Account mula, dan CPF contribution kita berkurangan. Kalau dulu ada $1,000 untuk bayar duit rumah, nanti tinggal $500. Lagi $500 kena keluar cash.\n\nItu yang kita dengar orang kata: \"Eh, rumah aku dah kena top up cash.\" Itu yang kita nak elakkan.\n\nStretching is fine in your 30s and 40s, as long as the plan is to be fully paid by 55, before your CPF contribution drops.\n\nNak buat perancangan? DM \"55\".",
    tags="#BayarHabis55 #CPF #RetirementAccount #HutangRumah #HDB #BarakahHomes #PropNex #NonaKirana #PerancanganKewangan #SingaporeProperty"),
"R08": dict(angle="Shortest reel. Positioning statement: the agent who stays for the planning.",
    caption="Biasanya ejen rumah: jual, beli, lepas tu bye-bye. 👋\n\nBagi saya, ada tanggungjawab untuk bantu pelanggan buat perancangan. Lagi-lagi kalau mereka 30-an, 40-an dan ambil hutang 25 tahun. Kemudian macam mana?\n\nPerancangannya mudah: bila 55, rumah habis bayar.\n\nMost agents close the deal and move on. I stay for the plan.",
    tags="#EjenRumah #BarakahHomes #PropNex #NonaKirana #PerancanganRumah #HDB #PropertyAgentSG #TrustedAgent #SingaporeProperty"),
"R09": dict(angle="Long-form story reel (61 s). Emotional problem, then the 'magic trick'. Best for engagement and comments about property pledging.",
    caption="Kakak 55, abang 60, hutang rumah masih ada. 😣\n\nNak downgrade, tapi anak-anak semua tengah tunggu BTO, baru balik belajar, tak nak keluar rumah. Abang dah tak bekerja. Macam mana nak bayar?\n\nKalau mereka beli awal dan rancang untuk bayar habis, tak perlu jual rumah bila terdesak. Tapi saya ada satu magic trick: property pledging. Keluarkan wang persaraan untuk bayar habis hutang rumah.\n\nIni polisi CPF. Anda perlu tahu sama ada anda layak atau tidak. Nak semak? DM saya \"PLEDGE\".\n\nA 55-year-old wife, a 60-year-old husband, a loan that's still running, and kids who can't move out yet. Property pledging is one option, if you qualify.",
    tags="#PropertyPledging #CPF #Downgrade #HDB #ExecutiveMaisonette #BarakahHomes #PropNex #NonaKirana #RetirementPlanningSG #SingaporeProperty"),
}

ORDER = ["R01", "R05", "R06", "R02", "R07", "R03", "R09", "R04", "R08"]

md = []
md.append("# Barakah Homes reels from the Warna 94.2FM interview\n")
md.append("Source: 13 min 14 s vertical phone recording (1080×1920, 60 fps) of Nona Kirana's guest slot on Warna 94.2FM with hosts Tiji and Arzak, in Malay. Topic: *Perlukah kita upgrade?* (Should we upgrade?). The first 2 min 40 s is pre-show audio (traffic, weather, ads) and is not used.\n")
md.append("## 1. Proposal: nine reels, one interview\n")
md.append("Every clip starts on the first word of a sentence and ends on the last word of one, with 0.25 s of breathing room before and 0.55 s after. Where a clip skips studio banter, the join lands on a sentence boundary and is covered by a punch-in cut and a cream flash.\n")
md.append("| # | Reel | Source timecodes | Length | Why this moment |\n|---|------|------------------|--------|-----------------|")
for c in clips:
    segs = " + ".join(f"{tc(a)}–{tc(b)}" for a, b in c["segments"])
    md.append(f"| {c['id']} | **{c['title']}** | {segs} | {c['duration']:.0f} s | {POSTS[c['id']]['angle']} |")
md.append("\n**Suggested posting order** (alternate story, advice and positioning): " + " → ".join(ORDER) + ". Three per week gives a three-week run from one recording.\n")

md.append("## 2. Brand and layout rules (Barakah Homes corporate colours)\n")
md.append("""| Token | Value | Used for |
|-------|-------|----------|
| Navy | `#1B2A3F` | caption pills, navy pop-up cards, end card background, name plate |
| Deep navy | `#101B2B` | gradient behind the text band, shadows |
| Gold | `#A47A3C` | live caption word, kicker pill, gold pop-up cards, progress bar, rules |
| Light gold | `#D6B06E` | highlighted words in the hook, English line |
| Cream | `#F6F1E8` | cream pop-up cards, hook text, logo word mark on dark |
| Muted | `#C8C0B2` | upcoming caption words, end-card body |

Type: Liberation Serif Bold for hooks, pop-ups and the name (matches the recruitment carousel), Inter ExtraBold for the word-by-word captions, Inter SemiBold for the English line and kickers.

### Face clearance and platform safe zones (measured)

The speaker's face was located with a face detector every 0.5 s across all nine clip ranges. Her chin never drops below **y = 962 px** in the chosen ranges (lowest at 10:37 in R09), and her face sits right of centre (mean centre x ≈ 770). The punch-in zoom is anchored to the bottom of the frame, so zooming in lifts her face rather than lowering it.

| Zone | Pixels on the 1080×1920 canvas | Reason |
|------|-------------------------------|--------|
| Top, kept clear of text | y 0–270 | Instagram status bar and Reels title, TikTok top tabs |
| Face, kept clear of text | y 0–1000 (full width) | measured chin ≤ 962 plus margin |
| Right column, kept clear | x 920–1080 between y 900 and 1600 | like / comment / share / profile buttons on both apps |
| Bottom, kept clear | y 1400–1920 | username, caption, audio strip (TikTok captions can reach ≈ y 1430) |
| **Text band** | **x 64–920, y 1000–1400** | every hook, pop-up, caption and English line lives here |

Vertical stack inside the band: pop-up card centred at y 1085 (or the hook block from y 1000 while it is on screen) → Malay caption pill centred at y 1250 (pushed down automatically while the hook is visible, measured from the hook layer) → English line from y 1320. The English line waits until the hook leaves so the stack never spills past y 1400. The small logo mark sits top-left at (64, 290), the one place her face never reaches.

## 3. Edit language ("fancy edits")

- **Hook block** (0–3.2 s): gold kicker pill + two-line serif statement with gold emphasis words, scales in from 94 % and fades out.
- **Punch-in cuts**: alternate 1.00× and 1.08× on sentence starts (at least 3.5 s apart) with a slow 2.5 % push-in inside each shot. Hard joins between segments get a cream flash.
- **Word-by-word captions**: Malay, max four words per pill, the live word sits on a gold chip and the pill pops 6 % on each new word. English line underneath in light gold.
- **Pop-up words**: cream, gold or navy cards with a serif keyword and a small English sub-label, spring in with a −3° settle, hold ≈ 2 s, shrink-fade out.
- **Name plate**: "Nona Kirana · Barakah Homes Realty · PropNex" slides in after the hook and leaves before the first pop-up.
- **Progress bar**: gold, bottom edge. **End card** (2.4 s): navy, arch logo, CTA, handle pill, PropNex chip.
- **Audio**: EBU R128 loudness to −14 LUFS, high-pass at 70 Hz, 0.15 s fade in, 0.45 s fade out.

## 4. Storyboards

Frame thumbnails are in `storyboard.png` (one row per reel: hook, name plate, pop-ups, closing line, end card). Times below are seconds into the finished reel; source timecodes in brackets.
""")
for c in clips:
    md.append(f"\n### {c['id']} — {c['title']}  ({c['duration']:.0f} s)\n")
    md.append(f"**Hook (0–3.2 s):** kicker `{c['kicker']}` · " + " / ".join(l.replace("*", "**") for l in c["hook"]))
    md.append("\n| Reel time | Source | Beat | On screen |\n|---|---|---|---|")
    md.append(f"| 0.0 s | {tc(c['segments'][0][0])} | Open | Hook block over the first sentence; captions start immediately |")
    md.append(f"| 3.4 s | | Name plate | Nona Kirana · Barakah Homes Realty · PropNex slides in (leaves before first pop-up) |")
    beats = []
    for p in c["popups"]:
        ct = clip_time(c, p["t"])
        beats.append((ct, f"| {ct:.1f} s | {tc(p['t'])} | Pop-up ({p['style']}) | **{p['text']}**" + (f" · _{p['sub']}_" if p.get("sub") else "") + " |"))
    for i in range(1, len(c["segments"])):
        ct = clip_time(c, c["segments"][i][0])
        beats.append((ct, f"| {ct:.1f} s | {tc(c['segments'][i][0])} | Join | Cream flash + punch-in; skips banter {tc(c['segments'][i-1][1])}–{tc(c['segments'][i][0])} |"))
    for _, row in sorted(beats): md.append(row)
    md.append(f"| {c['duration'] + 0.8:.1f} s | {tc(c['segments'][-1][1])} | Close | Last sentence ends, 0.55 s breath, audio fades |")
    md.append(f"| {c['duration'] + 0.8:.1f}–{c['duration'] + 3.2:.1f} s | | End card | *{c['cta_big']}* · {c['cta_small']} · {c['handle']} |")
    md.append("\n**Spoken (Malay) and English line:**\n")
    for s_ in c["subs"]:
        ws = " ".join(w["w"] for w in c["words"] if s_["s"] - 0.05 <= w["s"] < s_["e"] - 0.03)
        md.append(f"- `{tc(s_['s'])}` {ws}  \n  _{s_['en']}_")
    md.append(f"\n**Caption:**\n\n```\n{POSTS[c['id']]['caption']}\n\n{POSTS[c['id']]['tags']}\n```")

md.append("""
## 5. Notes for review

- The WhatsApp number on the end card (8268 1111) is the one Nona gives on air at 11:03. Replace it in `build_clips.py` if a different line should be used.
- Transcription was automatic (Whisper, Malay). Names and Singapore terms were corrected by hand (Nona, Tampines, Rivervale Crescent, Executive Maisonette, S$ figures). Please skim the captions in section 4 once more; `FIX` in `build_clips.py` holds the correction table.
- One figure was left out on purpose: the monthly CPF LIFE amount she quotes at 08:41 could not be transcribed with confidence, so R06 ends one sentence earlier on "CPF LIFE yang penuh".
- To change any wording, time or pop-up: edit `build_clips.py`, run `python3 build_clips.py`, then `python3 reel_engine.py clips.json <source.mp4> output/`.
""")
open(os.path.join(HERE, "STORYBOARD.md"), "w").write("\n".join(md))
print("STORYBOARD.md written")

# ---------- storyboard.png from rendered reels ----------
if os.path.isdir(OUT_DIR):
    F = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-SemiBold.otf", 22)
    FB = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf", 30)
    tw, th = 216, 384; cols = 6; pad = 16; label_h = 70
    rows = []
    for c in clips:
        f = [x for x in os.listdir(OUT_DIR) if x.startswith(c["id"]) and x.endswith(".mp4")]
        if not f: continue
        path = os.path.join(OUT_DIR, f[0])
        # name-plate time: same rule as the engine (first >=3 s gap after the hook with no pop-up)
        hook_dur = 3.2; body = c["duration"] + 0.8
        busy = sorted((clip_time(c, p["t"]) - 0.3, clip_time(c, p["t"]) + p.get("dur", 2.0) + 0.2) for p in c["popups"])
        cur = hook_dur + 0.2; lt0 = cur
        for b0, b1 in busy + [(body - 0.6, body)]:
            if b0 - cur >= 3.0: lt0 = cur; break
            cur = max(cur, b1)
        times = [1.2, lt0 + 0.7] + [clip_time(c, p["t"]) + 0.7 for p in c["popups"][:3]] + [c["duration"] + 2.6]
        labels = ["Hook", "Name plate"] + [f"Pop-up: {p['text']}" for p in c["popups"][:3]] + ["End card"]
        thumbs = []
        for t in times:
            raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", path, "-frames:v", "1", "-vf", f"scale={tw}:{th}", "-f", "rawvideo", "-pix_fmt", "rgb24", "pipe:1"], capture_output=True).stdout
            thumbs.append(Image.frombuffer("RGB", (tw, th), raw, "raw", "RGB", 0, 1).copy() if len(raw) == tw * th * 3 else Image.new("RGB", (tw, th), (40, 40, 40)))
        rows.append((c, thumbs, labels))
    Wd = pad + cols * (tw + pad); Hd = pad + len(rows) * (th + label_h + pad) + 90
    board = Image.new("RGB", (Wd, Hd), (246, 241, 232)); d = ImageDraw.Draw(board)
    d.text((pad, 18), "Barakah Homes × Warna 94.2FM — reel storyboard", font=ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf", 40), fill=(27, 42, 63))
    d.rectangle((pad, 70, pad + 90, 75), fill=(164, 122, 60))
    y = 90 + pad
    for c, thumbs, labels in rows:
        d.text((pad, y), f"{c['id']}  {c['title']}  ·  {c['duration']:.0f} s", font=FB, fill=(27, 42, 63))
        for i, (im, lb) in enumerate(zip(thumbs, labels)):
            x = pad + i * (tw + pad)
            board.paste(im, (x, y + 40))
            d.text((x, y + 40 + th + 6), lb[:22], font=F, fill=(90, 90, 90))
        y += th + label_h + pad
    board.save(os.path.join(HERE, "storyboard.png"), optimize=True)
    print("storyboard.png written", board.size)
