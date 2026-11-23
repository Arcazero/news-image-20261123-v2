#!/usr/bin/env python3
"""Draw 'The World Today — 23 November 2026': a 1024x1024 newspaper sheet
summing up Monday 23 November 2026 in six illustrated story cards.

Reads the six verified illustrations from assets/*.webp, lays them out under a
masthead and a five-city weather strip, and writes entry.png (PNG, <= 1 MiB).
Run:  python3 draw.py
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
OUT = os.path.join(HERE, "entry.png")

W = H = 1024
PAPER = (253, 252, 247)      # warm newsprint
INK = (18, 18, 18)
MUTED = (90, 86, 78)
RULE = (150, 145, 132)
CHIP_BG = (18, 18, 18)
CHIP_FG = (253, 252, 247)
CARD_BG = (255, 255, 255)
CARD_LINE = (205, 200, 188)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


F_SERIF_BIG = font("DejaVuSerif-Bold.ttf", 64)
F_SERIF = font("DejaVuSerif-Bold.ttf", 26)
F_SANS_B = font("DejaVuSans-Bold.ttf", 21)
F_SANS = font("DejaVuSans.ttf", 19)
F_SANS_SM = font("DejaVuSans.ttf", 16)
F_CHIP = font("DejaVuSans-Bold.ttf", 15)
F_WEATHER = font("DejaVuSans-Bold.ttf", 17)
F_WEATHER_SM = font("DejaVuSans.ttf", 15)
F_FOOT = font("DejaVuSans.ttf", 14)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap returning a list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_photo(path, w, h):
    """Open a photo, centre-crop to w:h, quantise to 256 colours."""
    img = Image.open(path).convert("RGB")
    iw, ih = img.size
    scale = max(w / iw, h / ih)
    img = img.resize((int(iw * scale + 0.5), int(ih * scale + 0.5)),
                     Image.LANCZOS)
    x = (img.width - w) // 2
    y = (img.height - h) // 2
    img = img.crop((x, y, x + w, y + h))
    img = img.convert("P", palette=Image.ADAPTIVE, colors=256).convert("RGB")
    return img


STORIES = [
    ("COP31", "assets/cop31.webp",
     "COP31 collapses with no deal after fossil-fuel row",
     "Two weeks of talks in Antalya end without agreement as oil states "
     "block a phase-out text, leaving the summit to close empty-handed."),
    ("WEATHER", "assets/storms.webp",
     "Thanksgiving storms batter both US coasts",
     "Heavy rain and snow disrupt the busiest travel week of the year, "
     "with floods in the west and a nor'easter gathering off the east."),
    ("USA", "assets/delta.webp",
     "Delta outage delays 1,600 flights on Sunday",
     "An automation failure grounds planes across the network on the "
     "weekend before Thanksgiving, stranding thousands of passengers."),
    ("GULF", "assets/rabigh.webp",
     "Houthis claim strike on Saudi Rabigh refinery",
     "The group says it hit the Red Sea plant with drones, the latest "
     "attack on Gulf energy sites as regional tensions keep climbing."),
    ("BALTIC", "assets/sparta.webp",
     "Russian ship Sparta II still burns off Finland",
     "The sanctioned cargo vessel has smouldered for days in the Gulf "
     "of Finland as tugs stand by and crews fight the fire at sea."),
    ("UKRAINE", "assets/kyiv.webp",
     "Drone strike traps 14 in the Kyiv region",
     "Rescuers dig through rubble after an overnight attack hits a "
     "residential block, as air defences report a record drone wave."),
]

WEATHER = [
    ("Antalya", "21° / 12°", "overcast", "13 km/h"),
    ("New York", "19° / 6°", "overcast", "19 km/h"),
    ("Atlanta", "18° / 9°", "overcast", "16 km/h"),
    ("Rabigh", "34° / 23°", "clear", "22 km/h"),
    ("Kyiv", "2° / 0°", "snow grains", "10 km/h"),
]

FOOT = ("Sources: Reuters, CNN, UN News, WSJ, ISW  •  Weather: Open-Meteo  •  "
        "Illustrations generated for this entry")


def main():
    sheet = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(sheet)
    mx = 36                      # side margin
    cx = W - 2 * mx              # content width

    # --- masthead ------------------------------------------------------
    y = 30
    title = "THE WORLD TODAY"
    d.text(((W - d.textlength(title, font=F_SERIF_BIG)) / 2, y),
           title, font=F_SERIF_BIG, fill=INK)
    y += 78
    date = "Monday, 23 November 2026"
    d.text(((W - d.textlength(date, font=F_SERIF)) / 2, y),
           date, font=F_SERIF, fill=MUTED)
    y += 40
    d.line([(mx, y), (W - mx, y)], fill=RULE, width=2)
    y += 12

    # --- weather strip -------------------------------------------------
    cell_w = cx // 5
    for i, (city, temp, cond, wind) in enumerate(WEATHER):
        x0 = mx + i * cell_w
        d.text((x0 + 4, y), city, font=F_WEATHER, fill=INK)
        d.text((x0 + 4, y + 22), temp, font=F_WEATHER_SM, fill=MUTED)
        d.text((x0 + 4, y + 42), f"{cond} · {wind}",
               font=F_WEATHER_SM, fill=MUTED)
        if i:
            d.line([(x0 - 6, y + 2), (x0 - 6, y + 58)], fill=RULE, width=1)
    y += 66
    d.line([(mx, y), (W - mx, y)], fill=RULE, width=2)
    y += 14

    # --- story grid: 2 columns x 3 rows -------------------------------
    gap = 18
    card_w = (cx - gap) // 2
    foot_h = 34
    grid_top = y
    grid_h = H - 30 - foot_h - grid_top
    card_h = (grid_h - 2 * gap) // 3
    photo_h = 104
    pad = 12

    for idx, (tag, asset, headline, body) in enumerate(STORIES):
        row, col = divmod(idx, 2)
        x0 = mx + col * (card_w + gap)
        y0 = grid_top + row * (card_h + gap)

        d.rectangle([x0, y0, x0 + card_w, y0 + card_h],
                    fill=CARD_BG, outline=CARD_LINE, width=1)
        photo = fit_photo(os.path.join(HERE, asset), card_w, photo_h)
        sheet.paste(photo, (x0, y0))
        # tag chip over the photo's bottom-left corner
        chip_w = d.textlength(tag, font=F_CHIP) + 18
        chip_y = y0 + photo_h - 30
        d.rectangle([x0 + 8, chip_y, x0 + 8 + chip_w, chip_y + 22],
                    fill=CHIP_BG)
        d.text((x0 + 17, chip_y + 3), tag, font=F_CHIP, fill=CHIP_FG)

        tx = x0 + pad
        ty = y0 + photo_h + 8
        text_w = card_w - 2 * pad
        for line in wrap(d, headline, F_SANS_B, text_w)[:2]:
            d.text((tx, ty), line, font=F_SANS_B, fill=INK)
            ty += 24
        ty += 2
        for line in wrap(d, body, F_SANS, text_w)[:3]:
            d.text((tx, ty), line, font=F_SANS, fill=MUTED)
            ty += 21

    # --- footer --------------------------------------------------------
    fy = H - 30 - 14
    d.line([(mx, fy), (W - mx, fy)], fill=RULE, width=1)
    d.text((mx, fy + 8), FOOT, font=F_FOOT, fill=MUTED)

    sheet.save(OUT, "PNG", optimize=True)
    print(f"wrote {OUT}: {os.path.getsize(OUT)} bytes")


if __name__ == "__main__":
    main()
