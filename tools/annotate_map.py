"""Annotate carte.png: Nordic place names, village dots, legend (1 square = 1 day of travel = 50 km)."""
import sys
from PIL import Image, ImageDraw, ImageFont

Image.MAX_IMAGE_PIXELS = None
SRC, OUT = sys.argv[1], sys.argv[2]
im = Image.open(SRC).convert("RGBA")
W, H = im.size
GRID = 558.6  # px per grid square (measured)

F = "/usr/share/fonts/truetype/freefont/"
f_city = ImageFont.truetype(F + "FreeSerifBold.ttf", 118)
f_town = ImageFont.truetype(F + "FreeSerif.ttf", 92)
f_vill = ImageFont.truetype(F + "FreeSerifItalic.ttf", 72)
INK, HALO = (38, 30, 22, 255), (238, 232, 218, 255)

# (name, x, y, dx, dy)  x,y = icon centre; label centred at x+dx, y+dy
CITIES = [
    ("Ithilmar", 499, 1298, 0, 190),
    ("Caras Galen", 1278, 1418, 60, 190),
    ("Hrafnborg", 5671, 479, 0, 200),
    ("Vélmar", 9705, 839, 0, -200),
    ("Úlfstad", 8766, 1817, 0, 200),
    ("Hvalvík", 11303, 2696, 0, 190),
    ("Járnholt", 9885, 3135, 0, 190),
    ("Skarnholm", 2356, 4181, 0, 190),
    ("Eyrarbakki", 6610, 3742, 0, 210),
    ("Sólheim", 9106, 4561, 0, 190),
    ("Konungshöfn", 9905, 6118, 0, 190),
]
TOWNS = [
    ("Brimnes", 3754, 998, 0, 170),
    ("Djúpavík", 4893, 2996, -60, 170),
    ("Ísafell", 1737, 3235, 0, -170),
    ("Skógar", 4034, 3615, 0, 170),
    ("Fjallnes", 5152, 4381, 0, 170),
    ("Grindavík", 8667, 479, 0, 170),
    ("Selfoss", 9745, 1158, 0, 160),
    ("Vargafjörður", 9625, 1957, 0, 170),
    ("Saltvík", 11003, 2616, -60, -170),
    ("Mýrdal", 10284, 2836, 0, -170),
    ("Stormey", 2077, 6238, 0, 170),
    ("Eldey", 4473, 6857, 0, 170),
    ("Kaldbak", 8786, 5120, 0, -170),
    ("Hafnarey", 8507, 5559, 0, 170),
    ("Birkiland", 9585, 5779, 0, -165),
    ("Dalvík", 10184, 5779, 0, -170),
    ("Vatnsdal", 9286, 6138, -60, 170),
    ("Torvík", 9386, 6758, 0, 170),
]
VILLAGES = [
    ("Lundey", 3135, 2057), ("Hrísey", 3994, 1957), ("Flatey", 2616, 2616),
    ("Eryn Dúath", 1598, 1040), ("Tirnaith", 999, 1797), ("Krossnes", 5192, 2396),
    ("Sker", 5352, 3395), ("Tangi", 3714, 3115), ("Vík", 7468, 479),
    ("Langanes", 9865, 400), ("Ormsey", 7269, 1797), ("Hraun", 7828, 1578),
    ("Gnúpur", 10983, 1917), ("Dimmuborg", 11030, 1600), ("Bjarg", 7868, 3275),
    ("Austey", 11303, 3195), ("Gnípa", 1518, 3942), ("Ósar", 3994, 4301),
    ("Heiði", 5432, 4820), ("Kjalvík", 839, 4960), ("Hrútey", 4473, 6420),
    ("Nordey", 6989, 4461), ("Fold", 7349, 4621), ("Breiðavík", 7009, 5020),
    ("Akrar", 8387, 4661), ("Garðar", 7708, 6178), ("Hlíð", 7508, 6817),
    ("Strönd", 8507, 6538), ("Kirkjubær", 9665, 4900), ("Hornvík", 10584, 4141),
    ("Útey", 11902, 4820), ("Rifsnes", 11942, 6098), ("Hálsar", 9905, 5379),
]


def is_land(x, y):
    r, g, b, _ = im.getpixel((x, y))
    return abs(r - g) < 25 and abs(g - b) < 25 and r > 150


def nearest_land(x, y):
    for rad in range(0, 400, 10):
        for dx in range(-rad, rad + 1, 10):
            for dy in (-rad, rad) if abs(dx) != rad else range(-rad, rad + 1, 10):
                if is_land(x + dx, y + dy) and all(
                    is_land(x + dx + ox, y + dy + oy) for ox, oy in ((-40, 0), (40, 0), (0, -40), (0, 40))
                ):
                    return x + dx, y + dy
    print("no land near", x, y, "- kept as is")
    return x, y


# --- clip icons for the legend before drawing anything
castle_icon = im.crop((9705 - 170, 839 - 120, 9705 + 170, 839 + 110))
town_icon = im.crop((9745 - 130, 1158 - 110, 9745 + 140, 1158 + 100))

d = ImageDraw.Draw(im)


def label(text, cx, cy, font, stroke):
    d.text((cx, cy), text, font=font, fill=INK, anchor="mm", stroke_width=stroke, stroke_fill=HALO)


def dot(x, y, r=26):
    d.ellipse((x - r - 8, y - r - 8, x + r + 8, y + r + 8), fill=HALO)
    d.ellipse((x - r, y - r, x + r, y + r), fill=INK)


for n, x, y, dx, dy in CITIES:
    label(n, x + dx, y + dy, f_city, 10)
for n, x, y, dx, dy in TOWNS:
    label(n, x + dx, y + dy, f_town, 8)
for n, x, y in VILLAGES:
    x, y = nearest_land(x, y)
    dot(x, y)
    label(n, x, y + 85, f_vill, 7)

# regions, large islands, seas (letter-spaced)
REG_INK, SEA_INK = (70, 52, 36, 255), (28, 48, 92, 255)
f_reg = ImageFont.truetype(F + "FreeSerifBold.ttf", 150)
f_sea = ImageFont.truetype(F + "FreeSerifItalic.ttf", 170)
REGIONS = [
    ("ROYAUME ELFE", 1358, 680), ("ÎLES NAINES", 6400, 5440),
    ("NORÐLAND", 10310, 1080), ("ÚLFMÖRK", 10200, 2400),
    ("JÁRNSEY", 10150, 3680), ("KONUNGSLAND", 9350, 5195),
    ("SKÓGEY", 7670, 5750), ("LANGEY", 5430, 2117),
]
SEAS = [
    ("Mer d'Ordhaf", 6390, 1340), ("Mer des Brumes", 3595, 5513),
    ("Mer des Baleines", 6250, 6050), ("Mer de Givre", 11660, 440),
]


def spaced(text, cx, cy, font, fill, gap, stroke=0):
    ws = [font.getlength(c) for c in text]
    x = cx - (sum(ws) + gap * (len(text) - 1)) / 2
    for c, w in zip(text, ws):
        d.text((x, cy), c, font=font, fill=fill, anchor="lm", stroke_width=stroke, stroke_fill=HALO)
        x += w + gap


for n, x, y in REGIONS:
    spaced(n, x, y, f_reg, REG_INK, 40, 9)
for n, x, y in SEAS:
    spaced(n, x, y, f_sea, SEA_INK, 30)

# small unnamed icons: label only
for n, x, y in [("Hof", 9106, 2277), ("Galathil", 1173, 1215), ("Amon Thrain", 1733, 1197), ("Nesbúð", 5312, 2856), ("Bær", 1438, 3355)]:
    label(n, x, y + 110, f_vill, 7)

# --- legend, bottom-left ocean
L, T = 330, 5470
R, B = L + 1260, T + 1470
panel = Image.new("RGBA", (R - L, B - T), (238, 232, 218, 235))
im.alpha_composite(panel, (L, T))
d.rectangle((L, T, R, B), outline=INK, width=10)
d.rectangle((L + 22, T + 22, R - 22, B - 22), outline=INK, width=3)
f_head = ImageFont.truetype(F + "FreeSerifBold.ttf", 120)
f_leg = ImageFont.truetype(F + "FreeSerif.ttf", 90)
d.text(((L + R) / 2, T + 130), "Légende", font=f_head, fill=INK, anchor="mm")
d.line((L + 150, T + 215, R - 150, T + 215), fill=INK, width=4)

sx, tx = L + 230, L + 440
rows = [T + 340, T + 520, T + 680, T + 850]
ci = castle_icon.resize((230, 156))
im.alpha_composite(ci, (sx - 115, rows[0] - 78))
d.text((tx, rows[0]), "Cité", font=f_leg, fill=INK, anchor="lm")
ti = town_icon.resize((180, 140))
im.alpha_composite(ti, (sx - 90, rows[1] - 70))
d.text((tx, rows[1]), "Bourg", font=f_leg, fill=INK, anchor="lm")
dot(sx, rows[2])
d.text((tx, rows[2]), "Village", font=f_leg, fill=INK, anchor="lm")
q = 70
d.rectangle((sx - q, rows[3] - q, sx + q, rows[3] + q), outline=(60, 80, 110, 255), width=6)
d.text((tx, rows[3] - 40), "1 carré = 1 journée", font=f_leg, fill=INK, anchor="lm")
d.text((tx, rows[3] + 60), "≈ 50 km en drakkar", font=ImageFont.truetype(F + "FreeSerifItalic.ttf", 76), fill=INK, anchor="lm")

# scale bar: two squares = 2 days = 100 km
bx0 = int((L + R) / 2 - GRID)
by = T + 1160
seg = GRID / 2
for i in range(4):
    x0 = bx0 + i * seg
    d.rectangle((x0, by, x0 + seg, by + 50), fill=INK if i % 2 == 0 else HALO, outline=INK, width=5)
f_tick = ImageFont.truetype(F + "FreeSerif.ttf", 76)
for i, t, a in ((0, "0", "mm"), (2, "1", "mm"), (4, "2 jours", "rm")):
    d.text((bx0 + i * seg, by - 80), t, font=f_tick, fill=INK, anchor=a)
for i, t, a in ((0, "0", "mm"), (2, "50", "mm"), (4, "100 km", "rm")):
    d.text((bx0 + i * seg, by + 130), t, font=f_tick, fill=INK, anchor=a)
for i in (0, 2, 4):
    d.line((bx0 + i * seg, by - 15, bx0 + i * seg, by + 65), fill=INK, width=6)

im.save(OUT, optimize=False, compress_level=6)
im.convert("RGB").resize((1600, int(1600 * H / W))).save(OUT.replace(".png", "-apercu.jpg"), quality=88)
print("ok")
