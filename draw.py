#!/usr/bin/env python3
"""Render the 23 November 2026 front page for news-image-20261123.

A 1024x1024 newspaper sheet: masthead, a five-city weather strip built
from real Open-Meteo figures for 23 Nov, six illustrated story cards in
a 2x3 grid, and a source credit at the foot.

Stories (all checked against reporting dated 22-23 Nov 2026):
  * COP31 collapses with no deal after the fossil-fuel row (Antalya)
  * Thanksgiving storms batter both US coasts (weather)
  * Delta automation outage delays 1,600+ flights (US local)
  * Houthis claim a strike on Saudi Arabia's Rabigh refinery
  * Russian cargo ship Sparta II still burns off Finland
  * Russian drone strike traps 14 in the Kyiv region

The pictures in assets/ were generated for this entry and carry no
lettering; every word on the page is typeset here in DejaVu.

    python3 draw.py        # writes entry.png (PNG under 1 MiB)
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

W, H = 1024, 1024
OUT = Path("entry.png")
ART = Path("assets")
DEJAVU = Path("/usr/share/fonts/truetype/dejavu")

INK = (15, 42, 67)        # deep navy for masthead and chips
GOLD = (184, 124, 22)     # rule under the masthead
PAPER = (247, 245, 240)   # page background
TEXT = (26, 26, 26)       # headlines
BODY = (60, 60, 60)       # card body copy
MUTED = (92, 92, 92)      # captions and credits
CARD = (255, 255, 255)    # card background
RULE = (208, 203, 193)    # hairlines
STRIP = (228, 237, 243)   # weather strip background

SIZES = {
    "masthead": 50, "dateline": 17, "small_caps": 13, "figure": 12,
    "chip": 12, "headline": 20, "copy": 14, "credit": 12,
}

STORIES = [
    dict(tag="COP31", art="cop31.webp",
         title="COP31 collapses with no deal after fossil-fuel row",
         body="The longest climate summit in history ended in Antalya with "
              "no pact: the EU, UK and others rejected a draft that never "
              "mentioned fossil fuels. Guterres called it deeply "
              "disappointing."),
    dict(tag="WEATHER", art="storms.webp",
         title="Thanksgiving storms batter both US coasts",
         body="A coastal storm soaked New York with 1-3 inches of rain and "
              "gusts to 40 mph, delaying LaGuardia flights. More storms are "
              "lined up for Tuesday in the West and Thanksgiving Day."),
    dict(tag="USA", art="delta.webp",
         title="Delta outage delays 1,600 flights on Sunday",
         body="A failure in Delta's weight-and-balance system delayed more "
              "than 1,600 flights, about half its schedule. Crews counted "
              "bags by hand; the system was fixed by the afternoon."),
    dict(tag="GULF", art="rabigh.webp",
         title="Houthis claim strike on Saudi Rabigh refinery",
         body="Yemen's Houthis said they hit the Petro Rabigh refinery on "
              "the Red Sea coast on Sunday, claiming a direct hit. Riyadh "
              "did not confirm damage; a missile was intercepted."),
    dict(tag="BALTIC", art="sparta.webp",
         title="Russian ship Sparta II still burns off Finland",
         body="The sanctioned cargo ship, hit by drones on Saturday, drifted "
              "into Finnish waters still on fire. All 16 crew were "
              "evacuated; Finland says Ukraine was likely behind it."),
    dict(tag="UKRAINE", art="kyiv.webp",
         title="Drone strike traps 14 in the Kyiv region",
         body="A Russian drone partly collapsed a five-storey apartment "
              "block near Kyiv early on Sunday. Nine people were evacuated; "
              "rescuers kept digging for those feared trapped."),
]

# Open-Meteo daily forecast for Monday 23 November 2026.
FORECAST = [
    dict(city="Antalya", hi="21\u00b0", lo="12\u00b0",
         rain="overcast", wind="13 km/h"),
    dict(city="New York", hi="19\u00b0", lo="6\u00b0",
         rain="overcast", wind="19 km/h"),
    dict(city="Atlanta", hi="18\u00b0", lo="9\u00b0",
         rain="overcast", wind="16 km/h"),
    dict(city="Rabigh", hi="34\u00b0", lo="23\u00b0",
         rain="clear", wind="22 km/h"),
    dict(city="Kyiv", hi="2\u00b0", lo="0\u00b0",
         rain="snow grains", wind="10 km/h"),
]


def make_fonts():
    """Load the DejaVu faces this page uses, serif for the masthead."""
    faces = {}
    for name, size in SIZES.items():
        family = "DejaVuSerif-Bold.ttf" if name == "masthead" \
            else "DejaVuSans-Bold.ttf"
        if name in ("figure", "copy", "credit"):
            family = "DejaVuSans.ttf"
        faces[name] = ImageFont.truetype(str(DEJAVU / family), size)
    return faces


def wrap(draw, text, font, width):
    """Greedy word wrap: lines that fit inside `width` pixels."""
    lines, line = [], ""
    for word in text.split(" "):
        trial = f"{line} {word}".strip()
        if draw.textlength(trial, font=font) <= width:
            line = trial
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def fit(draw, text, font, width, cap):
    """Wrap to at most `cap` lines, trimming the last with an ellipsis."""
    lines = wrap(draw, text, font, width)
    if len(lines) <= cap:
        return lines
    lines = lines[:cap]
    while lines and draw.textlength(lines[-1] + " ...", font=font) > width:
        head, _, _ = lines[-1].rpartition(" ")
        lines[-1] = head
    lines[-1] = f"{lines[-1]} ...".strip()
    return lines


def picture(name, width, height):
    """Crop an illustration to a box, then quantise it to keep size down."""
    img = Image.open(ART / name).convert("RGB")
    img = ImageOps.fit(img, (width, height), Image.LANCZOS)
    return img.convert("P", palette=Image.ADAPTIVE, colors=256).convert("RGB")


def masthead(draw, fonts):
    draw.text((W // 2, 6), "THE WORLD TODAY", font=fonts["masthead"],
              fill=INK, anchor="mt")
    draw.line([(14, 58), (W - 14, 58)], fill=GOLD, width=3)
    draw.text((W // 2, 74), "Monday, 23 November 2026",
              font=fonts["dateline"], fill=TEXT, anchor="ma")


def forecast_strip(draw, fonts):
    """The weather strip: label block on the left, five cities across."""
    top, height = 112, 58
    draw.rectangle([14, top, W - 14, top + height], fill=STRIP,
                   outline=RULE, width=1)
    draw.text((26, top + 8), "WEATHER", font=fonts["small_caps"], fill=INK)
    draw.text((26, top + 28), "23 NOV 2026", font=fonts["small_caps"],
              fill=INK)
    draw.text((26, top + 43), "OPEN-METEO", font=fonts["figure"],
              fill=MUTED)
    first, slot = 190, (W - 14 - 190) // len(FORECAST)
    for i, day in enumerate(FORECAST):
        left = first + i * slot
        if i:
            draw.line([(left, top + 8), (left, top + height - 8)],
                      fill=RULE, width=1)
        draw.text((left + 10, top + 6), day["city"],
                  font=fonts["small_caps"], fill=TEXT)
        draw.text((left + 10, top + 24),
                  f"{day['hi']} / {day['lo']}", font=fonts["figure"],
                  fill=TEXT)
        draw.text((left + 10, top + 40),
                  f"{day['rain']} \u00b7 {day['wind']}",
                  font=fonts["figure"], fill=MUTED)
    return top + height + 12


def story_card(page, draw, fonts, story, x, y, w, h):
    """One card: illustration on top, tag chip, headline, three lines."""
    draw.rectangle([x, y, x + w, y + h], fill=CARD, outline=RULE, width=1)
    photo_h = 140
    page.paste(picture(story["art"], w - 2, photo_h), (x + 1, y + 1))
    chip = draw.textlength(story["tag"], font=fonts["chip"]) + 16
    chip_y = y + 1 + photo_h - 24
    draw.rectangle([x + 1, chip_y, x + 1 + chip, chip_y + 23], fill=INK)
    draw.text((x + 9, chip_y + 4), story["tag"], font=fonts["chip"],
              fill=CARD)
    tx, tw = x + 12, w - 24
    hy = y + photo_h + 12
    heads = fit(draw, story["title"], fonts["headline"], tw, 2)
    for n, line in enumerate(heads):
        draw.text((tx, hy + n * 22), line, font=fonts["headline"],
                  fill=TEXT)
    by = hy + len(heads) * 22 + 4
    paras = fit(draw, story["body"], fonts["copy"], tw, 3)
    for n, line in enumerate(paras):
        draw.text((tx, by + n * 17), line, font=fonts["copy"], fill=BODY)
    assert by + len(paras) * 17 <= y + h - 6, f"{story['tag']} overflows"


def grid(page, draw, fonts, top):
    """Lay the six cards out two across, three down."""
    margin, gap = 14, 12
    cw = (W - 2 * margin - gap) // 2
    ch = (H - top - 34) // 3 - 10
    for i, story in enumerate(STORIES):
        cx = margin + (i % 2) * (cw + gap)
        cy = top + (i // 2) * (ch + 10)
        story_card(page, draw, fonts, story, cx, cy, cw, ch)


def credits(draw, fonts):
    base = H - 26
    draw.line([(14, base - 8), (W - 14, base - 8)], fill=RULE, width=1)
    line = ("Sources: Reuters \u00b7 CNN \u00b7 UN News \u00b7 WSJ \u00b7 "
            "ISW \u00b7 Open-Meteo \u2014 "
            "six stories verified 23 November 2026")
    draw.text((W // 2, base), line, font=fonts["credit"], fill=MUTED,
              anchor="ma")


def main():
    page = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(page)
    fonts = make_fonts()
    masthead(draw, fonts)
    top = forecast_strip(draw, fonts)
    grid(page, draw, fonts, top)
    credits(draw, fonts)
    page.save(OUT, "PNG", optimize=True)
    size = OUT.stat().st_size
    print(f"saved {OUT}: {page.size}, {size} bytes")
    if size > 1_048_576:
        page.save(OUT, "JPEG", quality=88)
        print(f"over 1 MiB, saved as JPEG: {OUT.stat().st_size} bytes")


if __name__ == "__main__":
    main()
