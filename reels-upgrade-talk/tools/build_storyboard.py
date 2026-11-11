import base64, io, json, html
from PIL import Image
FR="/tmp/claude-0/-home-user-Video-Editing-/340d1117-3082-5632-86b7-bfc284cb0d6e/scratchpad/dl/frames5s/f_%03d.jpg"
OUT="/home/user/Video-Editing-/reels-upgrade-talk/storyboard.html"
def still(t, w=240):
    im=Image.open(FR % (t//5+1)).convert("RGB"); im=im.resize((w, int(w*16/9)))
    b=io.BytesIO(); im.save(b,"JPEG",quality=72); return "data:image/jpeg;base64,"+base64.b64encode(b.getvalue()).decode()

reels=[
 dict(n=1, title="Kakak nak downgrade. Saya suruh upgrade.", tag="Kisah $500k", length="60–70 s", hook="Dia telefon saya nak DOWNGRADE. Saya suruh dia UPGRADE. 6 tahun kemudian…",
  why="Strongest story in the talk: a clear before/after with a number people remember. Best opener for the series.",
  scenes=[
   (51,"0:51–0:58","Lona juga ada satu kes… Kakak kata, saya selalu tengok Nona buat live, tergerak nak downgrade.","HOOK card over a fast punch-in: “Dia telefon nak DOWNGRADE” / “Saya suruh dia UPGRADE”","Hook text slams in two beats (whoosh ×2). Phone-ring sting under “telefon”.","Music starts low. Caption colour: gold keyword on DOWNGRADE / UPGRADE."),
   (58,"0:58–0:65","Umur Kakak berapa? 48. Nak downgrade rumah berapa bilik? Dari 5 bilik ke 4 bilik.","Caption only","Age badge “48” pops beside her head. Line icons: 5-room HDB → arrow → 4-room HDB, arrow pointing DOWN in red.","Soft pop SFX on badge."),
   (68,"1:08–1:20","Bila Nona tengok income keluarganya, suami bergaji besar… dia mampu pindah ke rumah private. “Kau suruh aku upgrade itu apa hal?”","Caption; the “apa hal?” line gets a bigger, playful caption","Small card: “Pendapatan keluarga: kukuh ✔” then condo icon slides in. Freeze-frame + zoom on “apa hal?” for a comedic beat.","Record-scratch-lite or subtle “huh” SFX on the freeze."),
   (81,"1:21–1:40","Abang boleh bayar habis rumah kondo bila umur 65… rumah 5 bilik di Jurong West harga $650,000. Pindah 4 bilik $500,000 memang boleh bayar habis.","Caption","Map pin “Jurong West” drops in. Two price tags animate: 5-bilik $650k · 4-bilik $500k.","Pin-drop SFX. Music lifts slightly."),
   (109,"1:49–2:00","Jadi Nona belikan mereka kondo di Jurong West pada $1.1 juta. Bulan-bulan bayar guna CPF, tak perlu top up cash.","Caption, “$1.1 JUTA” in gold","Price tag $1.1M. CPF card graphic with “Top-up cash: $0”.","Cash-register “ka-ching” (soft)."),
   (120,"2:00–2:19","6 tahun kemudian kondonya sekarang $1.6 juta… naik $500,000. Kalau Nona dengar cakap dia, dia rugi potensi.","Caption; THE money moment","Big animated counter rolls $1.1M → $1.6M, then a gold stamp “+$500,000” slams in. Hold 1.5 s. Then a faded “downgrade” path with “rugi potensi” crossed out.","Counter tick SFX, stamp thud. Music hits its peak here."),
   (139,"2:19–2:28","Kakak pun sekarang happy, hari-hari boleh pandang swimming pool. Jem dia singgah saja.","Caption","Light moment: tiny pool/sun sticker, her laugh kept in. Punch-in 112%.","Keep natural laugh, music dips for it."),
   (152,"2:32–2:42","Kalau Kakak patah balik, Kakak ada $500,000 lebih cash disebabkan capital appreciation kondo tersebut.","Caption; label “CAPITAL APPRECIATION”","Lower-third label. Final “$500k cash” tag stays on screen into the end card.","Music resolves."),
   (466,"END CARD 3 s","—","“Nak buat kira-kira dulu? DM saya / 8268 1111”","Barakah Homes logo + PropNex logo on navy, handle @nonakirana, phone number. Also her smiling frame behind it.","Outro sting."),
  ]),
 dict(n=2, title="Dua pakcik, umur sama. $30k vs $1.7 juta.", tag="Kisah dua pakcik", length="55–65 s", hook="Dua pakcik, sama-sama 77 tahun. Seorang ada $30k. Seorang ada $1.7 JUTA cash.",
  why="A head-to-head comparison is made for split-screen graphics. Strong emotional close (“MasyaAllah”).",
  scenes=[
   (359,"5:59–6:01","Saya ada kes dua pakcik ini.","HOOK card: “$30k” vs “$1.7 JUTA” side by side","Two cards slide in from left/right with a VS in the middle. Both labelled “77 tahun”.","Double whoosh. Music: slower, more cinematic than Reel 1."),
   (361,"6:01–6:20","Satu pakcik 77 tahun, rumah 4 bilik di Marsiling. Beli $38 ribu sahaja… bila nak jual, pindah 3 bilik dekat anak, keuntungan cash dia $30 ribu sahaja.","Caption","Left card fills in: “Pakcik A · Marsiling 4-bilik · Beli $38k · Untung $30k”. Map pin Marsiling.","Pop SFX per line of the card."),
   (381,"6:21–6:32","Semakin rumah berusia, rate of growth kurang sedikit… keuntungan tidak sebanyak kalau tinggal di rumah yang lebih muda.","Caption; keyword “rate of growth”","Simple curve graphic: value line flattening as the flat ages. Label “Rumah semakin tua → pertumbuhan perlahan”.","Low hum under the graphic."),
   (394,"6:34–6:46","Seorang lagi pakcik tinggal kondo, dah habis bayar. Pakcik bisnesman ke? Taklah, pakcik dulu ajar Bahasa Inggeris di sekolah.","Caption; “CIKGU” tag","Right card starts: “Pakcik B · Cikgu Bahasa Inggeris”. Breaks the ‘only rich people’ assumption.","Music lifts."),
   (406,"6:46–6:56","Bila pakcik 40-an, pakcik pinjam bank overdraft beli landed. Tinggal 5 tahun, lepas itu jual, sebab landed itu dah buat duit.","Caption","Timeline bar: 40-an → landed → +5 tahun → jual. Small house icons.","Tick SFX as timeline advances."),
   (416,"6:56–7:11","Pakcik beli kondo 2 bilik freehold $900 ribu. 20 tahun kemudian Nona jualkan kondo itu cash $1.7 juta. Pakcik 77 tahun. MasyaAllah.","Caption; $1.7 JUTA in gold","Counter $900k → $1.7M, then “CASH” stamp. Freeze on her “MasyaAllah” expression (7:11) for 1 s.","Counter + stamp SFX, music peak, then dip for the freeze."),
   (433,"7:13–7:18","Keputusan yang dia buat bila usia 40-an itu menentukan persaraan yang dia akan hadapi.","Full-width text card quoting this line","Both cards return side by side, now complete. Gold underline on “40-an”.","Music resolves."),
   (466,"END CARD 3 s","—","“Keputusan 40-an anda, persaraan anda. Jom bincang.”","Logos, handle, phone.","Outro sting."),
  ]),
 dict(n=3, title="Kenapa orang kita takut nak upgrade?", tag="Mindset + peraturan baru", length="50–60 s", hook="Kenapa orang Melayu kita takut nak upgrade? Sebab ini.",
  why="Pairs the cultural insight at the start with the ‘it’s reversible’ rule change near the middle. Good conversation-starter post.",
  scenes=[
   (20,"0:20–0:25","(Soalan dari host) Nona, kenapa masyarakat kita rata-rata takut nak upgrade atau naik taraf?","HOOK: question as a big text card. Host audio is off-mic; use it if it cleans up, else text-only hook.","Question card on navy, typewriter-style reveal.","Keys/typing SFX."),
   (26,"0:26–0:43","Memang orang Melayu kita berada, beralah, rendah diri, sopan santun… bila cakap naik taraf macam menunjuk. Show off. Takut periuk besar keraknya.","Caption; sticker “SHOW OFF?” with a question mark","Three word-tags pop in: beralah · rendah diri · sopan santun. Then a proverb card “Periuk besar, keraknya besar” in serif.","Pop SFX ×3, soft music."),
   (43,"0:43–0:51","Tapi bila kita fikir keperluan di hari tua nanti, perancangan perumahan hari ini memainkan peranan yang besar.","Caption","Timeline: “Hari ini” → “Umur 65”. House icon grows along it.","Music lifts."),
   (186,"3:06–3:18","Tak semua naik taraf tu tak baik. Dari segi size tak boleh lawan HDB, tapi dari segi asset class anda pindah ke perumahan yang lebih tinggi.","Caption; “ASSET CLASS” label","Two columns: HDB (size ✔) vs Private (asset class ✔). No winner, just the trade-off.","Pop SFX."),
   (200,"3:20–3:50","Sekarang dah tak ada cooling period… dulu 15 bulan, selepas jual private kena rehat 15 bulan sebelum masuk HDB. Sekarang tak perlu. Jual kondo, jual landed, terus pindah ke HDB dengan cash dalam bank.","Caption; “15 BULAN” struck through","“15 BULAN cooling period” card gets a red strike-through. Then arrow Condo → HDB with a cash-stack icon. ⚠ See note below before publishing this claim.","Strike SFX, ka-ching."),
   (230,"3:50–3:53","Jadi kalau kita mampu, kita boleh.","Big caption of the line","Hold frame, clean.","Music resolves."),
   (466,"END CARD 3 s","—","“Mampu ke tidak? Jom kira sama-sama.”","Logos, handle, phone.","Outro sting."),
  ]),
 dict(n=4, title="Jangan beli kondo kalau tak boleh jawab 3 soalan ni", tag="Checklist sebelum upgrade", length="55–65 s", hook="Nak beli kondo? Jawab 3 soalan ni dulu.",
  why="Turns the ‘sustainability’ and ‘buffer’ advice into a save-able checklist. Also carries the Barakah Homes planning angle.",
  scenes=[
   (233,"3:53–4:06","Anda buat perkiraan, tengok kelayakan hutang bank, pastikan boleh duduk sekurang-kurangnya 7 hingga 10 tahun. Jangan dengar cakap orang: beli kondo 2 tahun, CPF habis, kena top up cash, pening kepala.","Checklist item 1 appears: “☐ Boleh bertahan 7–10 tahun?”","Checklist panel on the left third. Then a red warning chip “CPF habis → top up cash” shakes.","Tick SFX, warning buzz."),
   (246,"4:06–4:15","Mesti ada apa yang saya panggil sustainability. Kalau anda mampu bertahan 7–10 tahun, ia pelaburan yang baik.","Item 1 gets ticked ✔; word “SUSTAINABILITY” highlighted","Tick animation.","Tick SFX."),
   (268,"4:28–4:42","Dalam tim saya, Barakah Homes, kami pastikan bila naik taraf ke rumah private, ada perancangan supaya hutang rumah habis bayar pada usia 55.","Item 2: “☐ Hutang habis umur 55?”","Barakah Homes wordmark lower-third. Age dial 55.","Pop SFX."),
   (282,"4:42–4:55","Kalau berlaku kematian, penyakit kronik, buang kerja… kita bantu pastikan ada buffer, supaya tak perlu jual rumah waktu terdesak.","Item 3: “☐ Ada buffer untuk what-ifs?”","Shield icon with three small icons: health, job, family. Tone: calm, no jokes here.","Music softens."),
   (295,"4:55–5:16","Bayangkan beli kondo 2–3 tahun, tiba-tiba seorang kena kanser… kalau ada perancangan kewangan, buffer boleh bantu bayar rumah sambil jalani rawatan. Bila masanya sesuai, jual dan patah balik ke HDB.","Caption only, slower pace, fewer cuts","No graphics over her face. Gentle 105% punch-in only.","Music very low."),
   (316,"5:16–5:27","Perancangan ini perlu kerana ramai yang ghairah, main terjun saja. Tak fikir kecemasan, what ifs.","Full checklist shown with all 3 ticked","Checklist card recap: 7–10 tahun ✔ · Habis bayar @55 ✔ · Buffer ✔. Save-this-post nudge: “Simpan untuk rujukan”.","Triple tick SFX."),
   (462,"7:42–7:49 + END CARD","Anda boleh cari saya di Facebook, Instagram, TikTok atau hubungi saya 8268 1111.","Her own CTA line used as audio","Social icons pop in as she names them; phone number card; logos.","Outro sting."),
  ]),
 dict(n=5, title="Kondo mana nak beli? Data, bukan teka.", tag="Bonus · PropNex tools", length="20–30 s", hook="Kondo ni boleh beli ke tidak? Jangan teka.",
  why="Optional short bonus cut. Short, data-driven, good for a weekday filler post.",
  scenes=[
   (164,"2:44–3:06","Kondo apa nak beli, boleh ke tidak? PropNex ada tech tools untuk forecasting: beli projek ni, berapa capital appreciation, bagus ke tidak, jual dalam 10 tahun ok ke tidak. Ada informasi dan data untuk bantu pelanggan buat keputusan lebih baik.","Caption; “DATA, BUKAN TEKA” sticker","Mock dashboard card (brand colours, no real numbers): project · forecast · 10-year outlook. PropNex logo lower-third.","UI blip SFX, upbeat music."),
   (466,"END CARD 3 s","—","“Nak tengok data projek anda? DM saya.”","Logos, handle, phone.","Outro sting."),
  ]),
]

def esc(s): return html.escape(s)
parts=[]
parts.append('''<title>Upgrade Talk Reels</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;800&family=Fraunces:opsz,wght@9..144,600;9..144,700&display=swap">
<style>
/* Layout: one column storyboard; each reel is a band with a strip of 9:16 stills and a notes table under each. Brand navy/gold from the carousel. */
:root{--bg:#f6f3ec;--fg:#1b2a3f;--muted:#5f6472;--card:#ffffff;--line:#e2dccd;--navy:#1b2a3f;--gold:#a47a3c;--gold-soft:#f1e6d2;--warn:#b4432f;--warn-soft:#fbe9e4;
 --display:'Fraunces',Georgia,serif;--body:'Inter',system-ui,sans-serif}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#141a25;--fg:#efe9dc;--muted:#a9aebb;--card:#1c2433;--line:#2c3545;--navy:#0f1520;--gold:#d2a561;--gold-soft:#3a2f1c;--warn:#ef8a74;--warn-soft:#3b1f19;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#141a25;--fg:#efe9dc;--muted:#a9aebb;--card:#1c2433;--line:#2c3545;--navy:#0f1520;--gold:#d2a561;--gold-soft:#3a2f1c;--warn:#ef8a74;--warn-soft:#3b1f19;color-scheme:dark}
body{background:var(--bg);color:var(--fg);font-family:var(--body);line-height:1.5;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:0 48px}
.wrap{max-width:1100px;margin:0 auto}
h1{font-family:var(--display);font-size:clamp(30px,5vw,48px);line-height:1.05;margin:28px 0 8px;text-wrap:balance}
h2{font-family:var(--display);font-size:clamp(22px,3.2vw,30px);margin:0;line-height:1.15;text-wrap:balance}
h3{font-size:14px;letter-spacing:.08em;text-transform:uppercase;color:var(--gold);margin:28px 0 10px}
.eyebrow{font-size:13px;letter-spacing:.1em;text-transform:uppercase;color:var(--gold);font-weight:600}
.lede{max-width:66ch;color:var(--muted);font-size:17px}
.meta{display:flex;flex-wrap:wrap;gap:10px;margin:14px 0 24px}
.chip{background:var(--card);border:1px solid var(--line);border-radius:999px;padding:6px 12px;font-size:13px}
.chip b{color:var(--gold)}
.series{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px;margin:8px 0 8px}
.series a{display:block;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px;color:inherit;text-decoration:none;min-width:0}
.series a .n{font-family:var(--display);font-size:28px;color:var(--gold);line-height:1}
.series a .t{font-weight:600;margin-top:6px;font-size:14px}
.series a .l{color:var(--muted);font-size:12px;margin-top:4px}
.reel{margin-top:44px;padding-top:28px;border-top:3px solid var(--navy)}
.reel header{display:flex;flex-wrap:wrap;align-items:flex-end;justify-content:space-between;gap:12px}
.reel .num{font-family:var(--display);font-size:64px;line-height:.9;color:var(--gold)}
.hook{margin:16px 0 6px;background:var(--navy);color:#fff;border-radius:14px;padding:16px 18px;font-family:var(--display);font-size:clamp(18px,2.4vw,24px);line-height:1.25;max-width:720px}
.hook small{display:block;font-family:var(--body);font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:#d2a561;margin-bottom:6px}
.why{color:var(--muted);max-width:70ch;margin:8px 0 18px}
.strip{display:flex;gap:10px;overflow-x:auto;padding-bottom:8px;scroll-snap-type:x proximity}
.shot{flex:0 0 150px;scroll-snap-align:start}
.shot img{width:150px;aspect-ratio:9/16;object-fit:cover;border-radius:10px;display:block;border:1px solid var(--line)}
.shot .tc{font-size:11px;color:var(--muted);margin-top:4px;font-variant-numeric:tabular-nums}
.shot .sc{font-size:12px;font-weight:600}
.tbl{overflow-x:auto;margin-top:14px}
table{border-collapse:collapse;width:100%;min-width:860px;font-size:13.5px}
th{text-align:left;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);padding:8px 10px;border-bottom:1px solid var(--line)}
td{padding:10px;border-bottom:1px solid var(--line);vertical-align:top}
td:first-child{white-space:nowrap;font-variant-numeric:tabular-nums;color:var(--muted)}
td.say{font-style:italic;max-width:300px}
td.txt{font-weight:600;max-width:220px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px 18px;min-width:0}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px}
.card h4{margin:0 0 6px;font-size:15px}
.card p,.card li{margin:0;font-size:14px;color:var(--muted)}
.card ul{margin:4px 0 0;padding-left:18px}
.note{background:var(--warn-soft);border-left:4px solid var(--warn);border-radius:8px;padding:12px 14px;margin:14px 0;font-size:14px}
.caption-demo{display:inline-block;background:#111;color:#fff;font-weight:800;font-size:22px;padding:6px 12px;border-radius:8px;letter-spacing:.01em}
.caption-demo em{font-style:normal;color:#e8b85c}
.swatches{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px}
.sw{width:44px;height:44px;border-radius:8px;border:1px solid var(--line)}
@media (prefers-reduced-motion: reduce){*{scroll-behavior:auto}}
</style>
<div class="wrap">
<div class="eyebrow">Storyboard draft · for approval</div>
<h1>Upgrade Talk Reels</h1>
<p class="lede">One 7 min 53 s talk (DJI Osmo Pocket 3, vertical, Malay) cut into a series of short Reels / TikToks. Each reel is self-contained, opens on a hook within the first second, keeps your own voice and phrasing, and adds motion graphics only where they carry a number or an idea you are saying.</p>
<div class="meta"><span class="chip"><b>Source</b> 1 video received (of 3)</span><span class="chip"><b>Output</b> 1080×1920 · 30 fps · H.264</span><span class="chip"><b>Reels</b> 4 main + 1 bonus</span><span class="chip"><b>Language</b> Malay captions, your words</span></div>
<h3>The series</h3>
<div class="series">''')
for r in reels:
    parts.append(f'<a href="#reel-{r["n"]}"><div class="n">{r["n"]:02d}</div><div class="t">{esc(r["title"])}</div><div class="l">{esc(r["tag"])} · {esc(r["length"])}</div></a>')
parts.append('</div>')
for r in reels:
    parts.append(f'<section class="reel" id="reel-{r["n"]}"><header><div><div class="eyebrow">Reel {r["n"]} · {esc(r["tag"])} · target {esc(r["length"])}</div><h2>{esc(r["title"])}</h2></div><div class="num">{r["n"]:02d}</div></header>')
    parts.append(f'<div class="hook"><small>Hook · first 1.5 s on screen</small>{esc(r["hook"])}</div><p class="why">{esc(r["why"])}</p>')
    parts.append('<div class="strip">')
    for i,(t,tc,say,txt,vis,aud) in enumerate(r["scenes"],1):
        parts.append(f'<div class="shot"><img src="{still(t)}" alt="Still at {tc}"><div class="sc">Shot {i}</div><div class="tc">{esc(tc)}</div></div>')
    parts.append('</div><div class="tbl"><table><thead><tr><th>Source</th><th>What you say (kept as audio)</th><th>On-screen text</th><th>Added visuals</th><th>Sound</th></tr></thead><tbody>')
    for (t,tc,say,txt,vis,aud) in r["scenes"]:
        parts.append(f'<tr><td>{esc(tc)}</td><td class="say">{esc(say)}</td><td class="txt">{esc(txt)}</td><td>{esc(vis)}</td><td>{esc(aud)}</td></tr>')
    parts.append('</tbody></table></div>')
    if r["n"]==3:
        parts.append('<div class="note"><b>Please confirm before we cut Shot 5.</b> The reel repeats that the 15-month wait-out period for private owners moving to HDB no longer applies. As far as I know it was still in force for buyers under 55 (seniors 55+ buying a 4-room or smaller were exempt). If the rule has since changed, say so and I will keep the line as is. If not, I suggest rewording the caption to “Kini ada pengecualian untuk 55 tahun ke atas” and trimming the audio to match, so the post is not flagged as inaccurate.</div>')
    parts.append('</section>')
parts.append('''<section class="reel" id="style"><header><div><div class="eyebrow">Applies to every reel</div><h2>Look, captions and sound</h2></div></header>
<div class="grid2" style="margin-top:18px">
<div class="card"><h4>Captions</h4><p>Burned-in, 2–4 words per line, bold sans, lower-middle of frame (clear of the TikTok/Reels UI). Key words in gold. Your Malay kept as spoken, light clean-up of fillers only.</p><p style="margin-top:10px"><span class="caption-demo">naik <em>$500,000</em></span></p></div>
<div class="card"><h4>Cuts and movement</h4><p>Every jump cut is hidden with an alternating 100% / 112% punch-in. One speed-ramp per reel at most. Freeze-frames only on the two comedic/emotional beats marked above.</p></div>
<div class="card"><h4>Colour</h4><p>The green office wall is neutralised (white balance), skin warmed slightly, highlights on the white hijab protected, light vignette. Clean, bright, not filtered.</p><div class="swatches"><div class="sw" style="background:#1b2a3f"></div><div class="sw" style="background:#a47a3c"></div><div class="sw" style="background:#f1e6d2"></div><div class="sw" style="background:#ffffff"></div></div><p style="margin-top:8px">Graphics use the Barakah Homes navy and gold from your carousel so the feed stays consistent.</p></div>
<div class="card"><h4>Sound</h4><p>Lav audio de-noised and levelled to −14 LUFS. Music bed sits well under the voice: upbeat and light for Reels 1, 4, 5; slower and more cinematic for Reel 2; soft for Reel 3. Whoosh / pop / ka-ching SFX only where a graphic lands.</p></div>
<div class="card"><h4>Graphics, not stock footage</h4><p>All added visuals are motion graphics built in-house: counters, price tags, map pins, HDB-vs-condo icons, CPF card, checklist, comparison cards. No stock footage is needed. If you want real B-roll (condo pool, HDB blocks, Jurong West), send me a few clips or photos and I will weave them in.</p></div>
<div class="card"><h4>End card (3 s, every reel)</h4><p>Your smiling frame behind a navy panel: Barakah Homes + PropNex logos, @nonakirana, the phone number you say on camera. Please confirm the number: I heard “8268 111”, which is one digit short.</p></div>
</div>
<h3>Suggested cover text and caption lines</h3>
<div class="grid2">
<div class="card"><h4>Reel 1</h4><p>Cover: “Nak DOWNGRADE → jadi +$500k”</p><p>Caption: Kakak telefon nak downgrade. Kami kira sama-sama. 6 tahun kemudian, +$500,000. Ini kisahnya. #upgradeHDB #kondoSingapura #BarakahHomes</p></div>
<div class="card"><h4>Reel 2</h4><p>Cover: “$30k vs $1.7 juta. Umur sama.”</p><p>Caption: Dua pakcik, dua keputusan di usia 40-an, dua persaraan yang sangat berbeza. #persaraan #hartanahSingapura</p></div>
<div class="card"><h4>Reel 3</h4><p>Cover: “Kenapa kita takut upgrade?”</p><p>Caption: Bukan menunjuk. Ini perancangan hari tua. Setuju? Komen di bawah. #mindset #naiktaraf</p></div>
<div class="card"><h4>Reel 4</h4><p>Cover: “3 soalan sebelum beli kondo”</p><p>Caption: Simpan ini sebelum anda tandatangan apa-apa. #checklist #belikondo #BarakahHomes</p></div>
</div>
<h3>What I need from you to proceed</h3>
<div class="card"><ul>
<li>Approve, reorder, or drop any of the 5 reels. Tell me if you want fewer (for example only Reels 1, 2 and 4).</li>
<li>Confirm the 15-month wait-out point in Reel 3 and the phone number for the end card.</li>
<li>Send the other two videos (share links, set to “Anyone with the link”). I only have this one so far.</li>
<li>Optional: your Instagram/TikTok handle exactly as you want it on screen, and any music you already license.</li>
</ul></div>
</section></div>''')
open(OUT,"w").write("\n".join(parts))
import os; print(OUT, os.path.getsize(OUT)//1024, "KB")
