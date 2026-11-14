# Reels from the Warna 94.2FM interview

Nine branded 1080×1920 reels cut from Nona Kirana's 13-minute radio guest slot (Malay), for Instagram Reels and TikTok.

- `STORYBOARD.md` — clip proposal, brand/layout rules, measured safe zones, per-reel storyboard, spoken lines with English, post captions and hashtags.
- `storyboard.png` — thumbnail storyboard, one row per reel.
- `safezone_proof.png` — rendered frames with the Instagram/TikTok interface zones and the measured face band drawn on top.
- `output/*.mp4` — the finished reels (H.264, AAC, 30 fps, −14 LUFS).
- `build_clips.py` — the edit decision list: segments, hooks, pop-ups, English lines, transcription fixes. Writes `clips.json`.
- `reel_engine.py` — renderer (ffmpeg + Pillow): sentence-safe trims, punch-in cuts, word-by-word captions, pop-up cards, name plate, end card.
- `make_storyboard.py` — regenerates `STORYBOARD.md` and `storyboard.png`.
- `transcript_words.json` — word-level Whisper transcript of the whole recording (source seconds).
- `assets/` — Barakah Homes and PropNex logos.

## Regenerate

```bash
python3 build_clips.py                                   # clips.json
python3 reel_engine.py clips.json /path/to/source.mp4 output/   # all reels (add R01,R05 to render a subset)
python3 make_storyboard.py output/                       # docs + storyboard image
```

The source recording is not committed (3.6 GB). Rendering needs ffmpeg, Pillow and the Inter + Liberation fonts.
