# Carousel: "What's your purpose?"

6-slide Instagram carousel for Nona Kirana / Barakah Homes Realty: Top New Achiever at her first agency, and the purpose behind it (a poor broken family, the mother she borrowed from to pay her RES fees, her children, and staying hungry).

Same social-card design as `humble-carousel/` in Barakah Homes navy, gold and cream: profile row with Instagram glyph and the Barakah Homes logo mark, rounded photo card, headline mixing Inter Display with gold cursive words (Dancing Script), counter pill, Swipe arrow on the cover and the full logo on the last slide.

- `slides/01.png` … `slides/06.png` — ready to upload, 1080×1350.
- `caption.md` — caption, hashtags and posting notes.
- `make_carousel.py` — regenerates the slides from `photos/` (`python3 make_carousel.py`).
- `photos/` — the source photos, the studio portrait used for the avatar, and the Barakah Homes logo.
- `fonts/` — Dancing Script and Great Vibes (SIL Open Font License).
- `storyboard.png` — contact sheet of all six slides.
- `barakah-purpose-carousel.zip` — the six slides zipped.

On the 2016 award photo, the previous agency's logo and the two "ERA" words in the congratulations text are pixelated and blurred before cropping (`ERA_LOGO` boxes, `blur=` argument). The tiny ERA marks on the sash and lapel pins are not blurred.

## Slide order

| # | Headline | Accent line | Photo |
|---|----------|-------------|-------|
| 01 | I was the *Top New Achiever* in my company. | This is **why** I did it. | 2016 award stage, logo and ERA words blurred |
| 02 | I came from a simple, poor and *broken* family. Your typical sad story. | But I wanted to **break the cycle** and change our lives. | Family birthday |
| 03 | I borrowed money from my *mother* to pay for my RES course. | She is **my purpose** to do well. | Family trip |
| 04 | I do this for my *children.* | So they never know **the struggle.** | Family photo with the children |
| 05 | I was *hungry* then. | I'm **still hungry** now. | Award stage, cropped to Nona |
| 06 | What's *your* purpose? | Tell me **in the comments.** | Family trip, with Barakah Homes logo |

Markup in the headline strings: `*word*` = cursive, `**word**` = bold, `\n` = forced line break.
