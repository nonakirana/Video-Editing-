# Barakah Homes house-tour editor

One-command comedy edit for a raw walkthrough video:

- animated Barakah Homes logo intro, branded call-to-action outro
- logo badge watermark on every shot
- timed comedy captions, snap zoom punch-ins, fast-forward "skip the corridor"
  sections, freeze-frame record-scratch moments, hard cuts
- synthesised sound effects (whoosh, boing, ding, pop, scratch, drumroll, sad, honk)
- landscape (YouTube), portrait (Reels / TikTok) or square output

## Run

```bash
python3 edit_house_tour.py --video raw_tour.mp4 --gags gags.json --out tour_edit.mp4
python3 edit_house_tour.py --video raw_tour.mp4 --gags gags.json --out tour_reel.mp4 --format portrait
```

Needs `ffmpeg` and Python with Pillow and numpy. A 12-minute 1080p source renders in
roughly 10 to 15 minutes on a 4-core machine (`--preset ultrafast` for quick previews).

## Gag sheet

`gags.example.json` shows every gag type. All times are seconds into the **original**
video; the script re-maps them onto the edited timeline after cuts and speed-ups.

| type | fields | what it does |
|------|--------|--------------|
| `caption` | `start`, `end`, `text`, `style`, optional `sfx` | text on screen. Styles: `pop` (yellow comic box), `shout` (huge white outlined), `lower` (navy lower-third), `tag` (small aside, top-left), `sticker` (gold price-tag, top-right) |
| `zoom` | `start`, `end`, `factor`, `x`, `y`, optional `text`, `sfx` | snap punch-in on a point (`x`,`y` are 0..1 across the frame) |
| `speed` | `start`, `end`, `factor`, optional `label` | fast-forward with a ">> 6x" style label |
| `freeze` | `at`, `hold`, optional `text`, `sfx` | freeze frame, desaturated slow push-in, record scratch |
| `cut` | `start`, `end` | removes the range entirely |
| `sfx` | `at`, `name` | drops a sound effect |

Top-level `title`, `subtitle`, `cta` and `handle` set the intro and outro text.
Use `\n` inside `text` for a line break.
