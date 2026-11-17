# Carousel: "Small in a company full of champions"

5-slide Instagram carousel for Nona Kirana / Barakah Homes Realty, on being a former champion who now feels small at PropNex, and why that keeps her from being complacent.

Design follows the "social card" reference (profile row, rounded photo card, big headline with one accent line, counter pill, Swipe arrow) recoloured in Barakah Homes navy, gold and cream, with the Barakah Homes logo mark and an Instagram glyph next to the handle. Headlines mix Inter Display (regular and bold) with gold cursive words in Dancing Script; mark them in `make_carousel.py` as `*cursive*` and `**bold**`. Slide 1 is cropped to the four faces on stage (`precrop` in the slide call).

- `slides/01.png` … `slides/05.png` — ready to upload, 1080×1350.
- `caption.md` — caption, hashtags and posting notes.
- `make_carousel.py` — regenerates the slides from `photos/` (`python3 make_carousel.py`).
- `photos/` — source photos, the studio portrait used for the avatar, and the Barakah Homes logo.
- `fonts/` — Dancing Script (cursive accent words) and Great Vibes, both SIL Open Font License.
- `storyboard.png` — contact sheet of all five slides.

## Slide order

| # | Headline | Accent line | Photo |
|---|----------|-------------|-------|
| 01 | I was a champion at my last agency. | Here, I'm number 200. | On stage with PropNex leaders |
| 02 | For years I was used to seeing my name at the top. | Being a champion felt normal. | Name on the 200 board |
| 03 | Then I joined a company with 500 champions. | And I placed 200th. | Trophy in front of the stage |
| 04 | In a room full of champions, you feel small. | It humbles me. And I'm grateful. | Seated portrait |
| 05 | Small keeps me hungry. Humble keeps me going. | Not complacent. Not done. | Trophy close-up, with Barakah Homes logo |

To change wording, edit the `slide(...)` calls at the bottom of `make_carousel.py` and re-run it.
