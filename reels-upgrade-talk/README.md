# Upgrade Talk Reels

Short-form series cut from one 7 min 53 s vertical talk (Malay, DJI Osmo Pocket 3) on upgrading from HDB to private property.

## Finished reels (1080×1920, 30 fps, H.264, burned-in Malay captions, −14 LUFS audio)

| # | File | Length | Hook |
|---|------|--------|------|
| 1 | `reel1-kakak-downgrade.mp4` | 82 s | Dia telefon nak DOWNGRADE. Saya suruh dia UPGRADE. |
| 2 | `reel2-dua-pakcik.mp4` | 77 s | $30k vs $1.7 juta. Dua pakcik, umur sama. |
| 3 | `reel3-kenapa-takut-upgrade.mp4` | 73 s | Kenapa orang kita takut nak upgrade? |
| 4 | `reel4-3-soalan-sebelum-beli-kondo.mp4` | 81 s | 3 soalan sebelum beli kondo. |
| 5 | `reel5-data-bukan-teka.mp4` | 25 s | Kondo ni boleh beli ke tidak? Jangan teka. (bonus) |

Every cut is placed inside a real pause detected in the audio (`tools/pauses-video1.txt`), after the sentence has finished, and cuts that fell inside continuous speech are merged into one take.

No music bed is baked in, so you can add a trending track in Instagram or TikTok at upload time. Sound effects (whooshes, pops, ka-ching, counter ticks, outro sting) are included.

## Other files

- `storyboard.html` — the approved storyboard draft.
- `transcript-video1.txt` / `.json` — timestamped transcript of the source video.
- `tools/` — the Pillow + ffmpeg compositor (`reelkit.py`) and one script per reel. Each script re-renders its reel from the source video (`python3 reelN.py`; set `PREVIEW="t1,t2,…"` to render a contact sheet instead).

The source video is not committed (2.1 GB). It is the Google Drive file shared in the session.
