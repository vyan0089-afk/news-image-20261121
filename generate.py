#!/usr/bin/env python3
"""Draw THE TWENTY-FIRST: a one-page newspaper front page summing up
Saturday 21 November 2026 world news. 35 stories, 7 regions, every story
verified as happened / first reported on 21 Nov 2026, each with a named
source and an uncertainty label. Stdlib + Pillow only (build-time).
Run: python3 generate.py  -> writes entry.png (1024x1024, RGB)."""

import math
import random
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
CREAM = (247, 241, 222)
PAPER2 = (242, 233, 205)
CARD = (255, 252, 240)
INK = (26, 26, 26)
RED = (176, 30, 30)
BLUE = (28, 68, 128)
GOLD = (176, 132, 20)
TEAL = (18, 110, 105)
GREEN = (46, 110, 46)
GREY = (110, 105, 90)
LINE = (90, 82, 64)
PURPLE = (120, 90, 200)
SKY = (205, 228, 240)
MAPLAND = (216, 206, 170)

FDIR = "/usr/share/fonts/truetype/dejavu/"


def font(name, size):
    return ImageFont.truetype(FDIR + name, size)


SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SERIF = lambda s: font("DejaVuSerif.ttf", s)
SERIF_I = lambda s: font("DejaVuSerif-Italic.ttf", s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)

# Regions: name, code, colour. Order matches the region strip.
REGIONS = [("EUROPE", "EU", RED), ("ASIA", "AS", BLUE),
           ("MIDDLE EAST", "ME", GOLD), ("AFRICA", "AF", GREEN),
           ("AMERICAS", "AM", TEAL), ("OCEANIA", "OC", (120, 70, 130)),
           ("GLOBAL", "GL", GREY)]
REG_COL = {c: col for _, c, col in REGIONS}
REG_NAME = {c: n for n, c, _ in REGIONS}

# (num, region, headline, summary, source, label)
# Labels: CONFIRMED verified · OFFICIAL stated by an authority ·
# REPORTED reported, not yet independently verified · CLAIM one side's
# claim · FORECAST still to happen.
HEROES = [
 (1, "EU", "COP31 IN OVERTIME: NO DEAL",
  "Antalya talks run past their Friday close into day 13; the draft drops "
  "all fossil-fuel wording and a third text is due Saturday morning.",
  "AP; Reuters", "CONFIRMED"),
 (2, "ME", "THREE MISSILES DOWN OVER RIYADH",
  "Saudi defences destroy three Houthi ballistic missiles aimed at the "
  "capital in the early hours; two more were stopped over Jizan on Friday.",
  "Saudi Press Agency", "CONFIRMED"),
 (3, "AM", "PERU SHAKEN BY 6.7 QUAKE",
  "A deep quake strikes Junin at 00:09 UTC, 108 km down, and is felt in "
  "Lima; homes damaged, power cut, but no deaths reported.",
  "USGS", "CONFIRMED"),
]

FEATURES = [
 (4, "AS", "DAVAO: 146 SAFE AFTER ENGINE SCARE",
  "Air Niugini 767 diverts to Davao on a right-engine fire warning; all "
  "137 passengers and 9 crew slide out unhurt.",
  "CAAP; AP", "CONFIRMED"),
 (5, "GL", "BITCOIN SINKS BELOW $60,000",
  "Bitcoin falls to about $58,200 at midday UTC, its lowest since September "
  "2024, as the AI sell-off spreads to crypto.",
  "Finnhub; Reuters", "CONFIRMED"),
 (6, "OC", "RAHUL 136 AS INDIA TAKE CHARGE",
  "KL Rahul's 13th Test hundred, his first in New Zealand, lifts India to "
  "486 for 4 at stumps on day three in Wellington.",
  "IANS", "CONFIRMED"),
 (7, "EU", "BEPICOLOMBO DUE AT MERCURY TONIGHT",
  "After eight years, the ESA-JAXA probe fires its thrusters at 19:24 CET "
  "for a 37-minute burn to be captured by Mercury's gravity.",
  "ESA", "FORECAST"),
 (8, "EU", "ZELENSKY: CRIMEA BRIDGE 'WILL NOT STAY'",
  "Ukraine's president says the bridge is a legitimate target and warns "
  "Russia it will not survive, in an NBC interview.",
  "NBC; United24", "REPORTED"),
 (9, "ME", "IRAN CLAIMS US DRONE DOWNED",
  "The IRGC says it shot down a US MQ-9 over the Strait of Hormuz, its "
  "58th such claim; the US has not confirmed it.",
  "Al Jazeera; IRIB", "CLAIM"),
 (10, "AM", "TRUMP VOWS 'TREMENDOUS TAX' ON AI DATA CENTRES",
  "US firms building data centres abroad face a huge tax, the president "
  "says at the White House; no rate or rule is given.",
  "Reuters; AP", "REPORTED"),
 (11, "AS", "CHINA TO JAPAN: 'CORRECT' TAIWAN WORDS",
  "Beijing demands Tokyo retract PM Takaichi's Taiwan remarks 'as soon as "
  "possible', a day after Xi snubbed her at APEC.",
  "Reuters", "REPORTED"),
 (12, "GL", "MAKE.FUN OPENS TODAY'S CONTEST",
  "This news-image contest opens 00:00 UTC; $100 in USDC is locked in "
  "escrow at 01:56:50 UTC for the 50 best entries.",
  "make.fun", "CONFIRMED"),
 (13, "EU", "DENMARK EXPELS RUSSIAN ATTACHE",
  "Copenhagen expels Moscow's defence attache, out in seven days, over a "
  "plot to kill rapper Kyivstoner near the capital.",
  "Al Jazeera; PET", "REPORTED"),
]

# (num, region, one-line text, source, label)
BRIEFS = [
 (14, "ME", "Houthis threaten Jeddah and Red Sea ports.", "Al Jazeera", "CLAIM"),
 (15, "ME", "Iran keeps its 60% uranium; IAEA counts 440.9 kg.", "Al Jazeera", "REPORTED"),
 (16, "AM", "Panama vows to block a COP31 deal with no fossil fuels.", "UN News", "REPORTED"),
 (17, "AM", "Vance will not say he would have ordered Iran strikes.", "Reuters", "REPORTED"),
 (18, "AM", "SpaceX closes a new funding round, reports say.", "Reuters", "REPORTED"),
 (19, "AM", "Texas carries out an execution after a final appeal fails.", "AP", "REPORTED"),
 (20, "AM", "Man convicted over the Los Angeles Palisades fire.", "AP", "REPORTED"),
 (21, "AM", "Missouri jury awards $7.25bn in a Roundup cancer case.", "Reuters", "REPORTED"),
 (22, "AM", "A youth climate trial opens in a Canadian court.", "CBC", "REPORTED"),
 (23, "AM", "George Russell fastest in Las Vegas Grand Prix practice.", "F1", "REPORTED"),
 (24, "AM", "Verstappen faces the stewards after Las Vegas practice.", "F1", "REPORTED"),
 (25, "EU", "Zelensky: Starshield faltered in Ukraine; Musk disputes it.", "h.ua", "REPORTED"),
 (26, "OC", "Australia and China hold AI talks, officials say.", "Reuters", "REPORTED"),
 (27, "OC", "Pat Cummins strikes in Melbourne as Australia press on.", "AAP", "REPORTED"),
 (28, "AS", "Kim Jong-un tours factories in Pyongyang, state media say.", "KCNA", "REPORTED"),
 (29, "AS", "A freight train derails near Sejong; no deaths reported.", "Yonhap", "REPORTED"),
 (30, "AS", "Taipei passes its city budget after a long debate.", "CNA", "REPORTED"),
 (31, "AS", "Bangkok unveils an arsenic clean-up plan for its water.", "Bangkok Post", "REPORTED"),
 (32, "AS", "Pakistan joins a SCO forum in New Delhi.", "PTI", "REPORTED"),
 (33, "AS", "Rain alerts go up across eastern India.", "IMD", "REPORTED"),
 (34, "AS", "New sanctions target Myanmar's junta and its arms trade.", "Reuters", "REPORTED"),
 (35, "AF", "Next year's climate summit is set for Addis Ababa.", "UN News", "REPORTED"),
]

STATS = [("DAY 13", "COP31 overtime"), ("3", "missiles down over Riyadh"),
         ("6.7", "Peru quake, Junin"), ("146", "safe in Davao"),
         ("$58,214", "Bitcoin, midday UTC"), ("136", "Rahul, Wellington")]

DATE_CHECK = ("NOT 21 NOV: Wall St correction; Kyiv bridges barrage; Poland "
              "missile; UK-EU deal; Cyclone Akvan; ICJ Myanmar ruling (all 20 "
              "Nov); Voyager 1 light-day (18 Nov). NOT YET: COP31 final text; "
              "BepiColombo capture (burn 19:24 CET).")

# ---------------------------------------------------------------- helpers

def wrap(draw, text, fnt, width):
    """Greedy word wrap to a pixel width; returns list of lines."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= width:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_font(draw, text, fname, size, width):
    """Largest font size <= size that fits text in width (min 8)."""
    s = size
    while s > 8 and draw.textlength(text, font=font(fname, s)) > width:
        s -= 1
    return font(fname, s)


def label_chip(d, x, y, label):
    """Small outlined label chip with a solid paper fill so it stays
    readable over illustration art; returns its width."""
    f = SANS_B(8)
    w = int(d.textlength(label, font=f)) + 10
    col = {"CONFIRMED": GREEN, "OFFICIAL": BLUE, "REPORTED": GOLD,
           "CLAIM": RED, "FORECAST": PURPLE}.get(label, GREY)
    d.rounded_rectangle([x, y, x + w, y + 11], radius=3, outline=col, width=1,
                        fill=CARD)
    d.text((x + 5, y + 1), label, font=f, fill=col)
    return w


# ---------------------------------------------------------------- map data
# Simplified continent outlines in lon/lat, drawn by hand from an atlas.
CONTINENTS = [
    # North America
    [(-168, 66), (-150, 70), (-135, 69), (-125, 71), (-110, 68), (-95, 69),
     (-85, 66), (-80, 62), (-76, 62), (-70, 58), (-65, 60), (-60, 55),
     (-55, 52), (-60, 47), (-65, 44), (-70, 42), (-74, 39), (-76, 35),
     (-80, 32), (-81, 26), (-84, 30), (-89, 29), (-93, 29), (-97, 26),
     (-101, 24), (-105, 20), (-105, 24), (-110, 24), (-114, 28),
     (-117, 33), (-122, 37), (-124, 42), (-124, 48), (-130, 55),
     (-140, 60), (-152, 58), (-162, 58), (-166, 60), (-168, 66)],
    # Greenland
    [(-58, 64), (-52, 60), (-44, 60), (-40, 64), (-32, 68), (-25, 70),
     (-22, 74), (-30, 76), (-45, 76), (-58, 74), (-60, 70), (-58, 64)],
    # South America
    [(-79, 9), (-77, 8), (-72, 12), (-64, 10), (-60, 8), (-54, 6),
     (-51, 4), (-50, 0), (-44, -3), (-38, -5), (-35, -8), (-38, -15),
     (-40, -20), (-46, -24), (-48, -28), (-54, -34), (-58, -38),
     (-62, -41), (-65, -45), (-68, -50), (-70, -54), (-74, -53),
     (-73, -45), (-73, -37), (-71, -30), (-70, -20), (-75, -15),
     (-79, -8), (-81, -4), (-80, 1), (-79, 9)],
    # Europe
    [(-10, 36), (-9, 38), (-9, 43), (-2, 44), (-1, 46), (-4, 48),
     (0, 50), (2, 51), (5, 53), (8, 55), (8, 57), (10, 59),
     (13, 56), (18, 56), (21, 55), (24, 58), (26, 59), (28, 60),
     (30, 61), (28, 64), (25, 66), (22, 68), (18, 69), (14, 67),
     (12, 65), (10, 62), (6, 58), (5, 60), (2, 58), (-2, 57),
     (-5, 50), (-5, 48), (-2, 44), (-9, 37), (-10, 36)],
    # United Kingdom
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53),
     (1, 51), (-3, 50), (-5, 50)],
    # Africa
    [(-6, 35), (-10, 31), (-15, 27), (-17, 21), (-17, 15), (-15, 11),
     (-12, 8), (-8, 5), (-4, 5), (2, 6), (6, 4), (9, 4), (9, 0),
     (12, -4), (13, -10), (12, -15), (13, -20), (12, -26), (15, -27),
     (17, -29), (19, -34), (25, -34), (28, -33), (32, -29), (35, -24),
     (36, -20), (40, -15), (40, -10), (42, -4), (46, -1), (48, 2),
     (51, 10), (48, 11), (44, 11), (43, 12), (40, 15), (38, 18),
     (37, 22), (35, 24), (34, 28), (32, 31), (30, 31), (25, 32),
     (20, 32), (15, 32), (11, 34), (10, 37), (5, 37), (0, 36),
     (-6, 35)],
    # Asia
    [(30, 36), (33, 36), (36, 36), (39, 38), (42, 38), (44, 39),
     (47, 38), (49, 37), (52, 37), (54, 37), (56, 38), (58, 39),
     (60, 40), (63, 42), (66, 44), (68, 45), (71, 45), (74, 46),
     (77, 48), (80, 50), (83, 53), (86, 55), (90, 58), (95, 60),
     (100, 62), (105, 64), (110, 66), (115, 68), (120, 70), (125, 71),
     (130, 71), (135, 71), (140, 72), (145, 72), (150, 71), (155, 69),
     (160, 67), (165, 66), (170, 66), (178, 65), (173, 64), (170, 60),
     (163, 60), (160, 55), (158, 52), (156, 50), (150, 48), (144, 44),
     (142, 40), (140, 38), (138, 35), (135, 34), (132, 33), (130, 31),
     (128, 34), (126, 38), (124, 40), (122, 38), (121, 33), (120, 28),
     (118, 25), (114, 22), (110, 20), (108, 18), (106, 12), (105, 9),
     (103, 8), (101, 7), (99, 10), (98, 13), (97, 16), (94, 17),
     (92, 21), (90, 22), (88, 22), (86, 20), (84, 19), (81, 16),
     (80, 13), (78, 8), (76, 10), (74, 13), (73, 18), (71, 20),
     (69, 22), (67, 24), (65, 25), (62, 25), (60, 25), (58, 25),
     (56, 26), (54, 26), (52, 27), (50, 29), (48, 30), (46, 29),
     (44, 29), (42, 30), (40, 31), (38, 32), (36, 34), (33, 35),
     (30, 36)],
    # Japan
    [(130, 31), (132, 33), (134, 34), (137, 35), (139, 35), (140, 37),
     (141, 40), (141, 43), (143, 44), (144, 42), (142, 40), (140, 36),
     (137, 34), (134, 33), (131, 32), (130, 31)],
    # Indonesia (west + east blobs)
    [(95, 5), (98, 4), (100, 0), (103, -2), (106, -6), (110, -7),
     (112, -7), (114, -8), (111, -7), (107, -7), (104, -5), (101, 1),
     (98, 4), (95, 5)],
    [(119, -1), (122, 0), (125, 1), (128, -1), (131, -1), (132, -3),
     (129, -4), (125, -3), (121, -3), (119, -1)],
    # Australia
    [(114, -22), (113, -25), (114, -30), (115, -33), (116, -35),
     (119, -34), (122, -33), (126, -32), (129, -32), (132, -32),
     (135, -35), (137, -35), (140, -38), (143, -39), (146, -39),
     (149, -37), (151, -34), (153, -32), (153, -28), (151, -24),
     (149, -20), (146, -19), (143, -17), (142, -14), (142, -11),
     (140, -12), (137, -12), (135, -13), (133, -12), (131, -12),
     (129, -13), (127, -14), (125, -15), (122, -17), (120, -19),
     (117, -20), (114, -22)],
    # New Zealand
    [(167, -45), (169, -43), (171, -42), (173, -41), (175, -38),
     (176, -38), (174, -40), (172, -41), (170, -43), (168, -45),
     (167, -45)],
]

# (story num, lon, lat) for the geographically located stories.
PINS = {1: (30.7, 36.9), 2: (46.7, 24.6), 3: (-75.2, -11.2), 4: (125.6, 7.1),
        6: (174.8, -41.3), 7: (8.7, 49.9), 8: (30.5, 50.5), 9: (56.5, 26.6),
        10: (-77.0, 38.9), 11: (139.7, 35.7), 13: (12.6, 55.7)}


def project(lon, lat, x0, y0, w, h):
    """Equirectangular projection into the map box."""
    px = x0 + (lon + 170.0) / 360.0 * w
    py = y0 + (75.0 - lat) / 130.0 * h
    return px, py

# ---------------------------------------------------------------- illustrations
# Every illustration is drawn from scratch with vector shapes. `big` is
# True in the hero slots (wide box, caption line) and False in the small
# feature slots.

def illus_cop31(d, x, y, w, h, big):
    cx, cy = x + w // 2, y + h // 2
    # sky bands
    for i in range(4):
        d.rectangle([x, y + i * h // 4, x + w, y + (i + 1) * h // 4],
                    fill=(225 + i * 4, 235 - i * 3, 240 - i * 4))
    # globe
    r = h // 2 - 10 if big else min(w, h) // 2 - 2
    gx = cx - (w // 6 if big else 0)
    gy = cy - 6 if big else cy - 2
    d.ellipse([gx - r, gy - r, gx + r, gy + r], fill=(190, 220, 235),
              outline=TEAL, width=3)
    d.ellipse([gx - r + 5, gy - r + 7, gx - 4, gy - 2], fill=(120, 170, 110))
    d.ellipse([gx + 2, gy + 2, gx + r - 5, gy + r - 7], fill=(120, 170, 110))
    d.ellipse([gx - r + 8, gy + r - 12, gx + 2, gy + r - 4], fill=(140, 185, 125))
    d.line([gx - r, gy, gx + r, gy], fill=TEAL, width=2)
    d.arc([gx - r // 2, gy - r, gx + r // 2, gy + r], 270, 90, fill=TEAL, width=1)
    # thermometer
    tx = x + w - 20
    d.rounded_rectangle([tx, y + 6, tx + 9, y + h - 18], radius=4,
                        fill=(255, 255, 255), outline=RED, width=2)
    d.rectangle([tx + 2, y + 16, tx + 7, y + h - 20], fill=RED)
    d.ellipse([tx - 3, y + h - 26, tx + 12, y + h - 11], fill=RED)
    for ty in (y + 12, y + 22, y + 32):
        d.line([tx - 3, ty, tx, ty], fill=RED, width=1)
    # day counter
    if big:
        d.rectangle([x + 6, y + 6, x + 52, y + 22], fill=RED)
        d.text((x + 29, y + 8), "DAY 13", font=SANS_B(11), fill=(255, 255, 255),
               anchor="ma")


def illus_missiles(d, x, y, w, h, big):
    cx, cy = x + w // 2, y + h // 2
    # night sky
    rng = random.Random(21)
    d.rectangle([x, y, x + w, y + h], fill=(30, 40, 70))
    for _ in range(26 if big else 10):
        sx = x + rng.randint(2, w - 3)
        sy = y + rng.randint(2, h // 2)
        d.ellipse([sx, sy, sx + 2, sy + 2], fill=(255, 240, 180))
    # city skyline
    base = y + h - 12
    for i, bh in enumerate((14, 26, 18, 32, 22, 16)):
        bx = x + 4 + i * (w - 8) // 6
        bw = (w - 8) // 6 - 3
        d.rectangle([bx, base - bh, bx + bw, base], fill=(60, 65, 90))
        for wy in range(base - bh + 3, base - 2, 6):
            d.rectangle([bx + 2, wy, bx + 4, wy + 2], fill=(255, 220, 120))
    # shield dome
    d.arc([x + 6, y + 4, x + w - 6, y + h + 6], 180, 360, fill=(140, 200, 255),
          width=2)
    d.arc([x + 14, y + 10, x + w - 14, y + h + 2], 180, 360,
          fill=(140, 200, 255), width=1)
    # three missile trails with bursts
    for i, mx in enumerate((0.22, 0.5, 0.78)):
        tx = x + int(w * mx)
        ty = y + 12 + i * 4
        d.line([tx - 14, ty + 16, tx, ty], fill=(255, 200, 90), width=3)
        d.polygon([(tx, ty - 4), (tx + 5, ty + 3), (tx - 5, ty + 3)], fill=RED)
        bx2, by2 = tx - 20, ty + 22
        for a in range(0, 360, 45):
            rr = math.radians(a)
            d.line([bx2, by2, bx2 + 7 * math.cos(rr), by2 + 7 * math.sin(rr)],
                   fill=(255, 170, 60), width=2)
        d.ellipse([bx2 - 3, by2 - 3, bx2 + 3, by2 + 3], fill=(255, 220, 100))


def illus_quake(d, x, y, w, h, big):
    cx, cy = x + w // 2, y + h // 2
    # Andes mountains
    d.rectangle([x, y, x + w, y + h], fill=(235, 225, 200))
    d.polygon([(x, y + h), (x + w * 0.18, y + 10), (x + w * 0.38, y + h)],
              fill=(150, 140, 120))
    d.polygon([(x + w * 0.3, y + h), (x + w * 0.55, y + 4), (x + w * 0.8, y + h)],
              fill=(120, 110, 95))
    d.polygon([(x + w * 0.62, y + h), (x + w * 0.85, y + 14), (x + w, y + h)],
              fill=(150, 140, 120))
    d.polygon([(x + w * 0.5, y + 4), (x + w * 0.55, y + 4), (x + w * 0.58, y + 14),
               (x + w * 0.52, y + 14)], fill=(255, 255, 255))
    # shaking buildings
    base = y + h - 10
    for i, (bx, bw, bh, tilt) in enumerate(((6, 16, 22, -2), (26, 14, 30, 2),
                                            (46, 18, 18, -3), (68, 14, 26, 2))):
        px = x + bx * w // 100
        pw = bw * w // 100
        ph = bh * h // 100
        d.polygon([(px, base), (px + tilt, base - ph), (px + pw + tilt, base - ph),
                   (px + pw, base)], fill=(90, 80, 70))
        for wy in range(base - ph + 4, base - 3, 7):
            d.rectangle([px + 3, wy, px + 6, wy + 3], fill=(255, 220, 120))
    # ground cracks
    d.line([x + 4, base, x + w * 0.3, base + 4, x + w * 0.55, base - 2,
            x + w - 4, base + 3], fill=INK, width=2)


def illus_davao(d, x, y, w, h, big):
    cx, cy = x + w // 2, y + h // 2
    # sky + sun
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    d.ellipse([x + w - 24, y + 4, x + w - 8, y + 20], fill=(255, 220, 100),
              outline=GOLD, width=2)
    for i in range(3):
        d.line([x + 4 + i * 10, y + 8 + i * 4, x + 30 + i * 10, y + 8 + i * 4],
               fill=(255, 255, 255), width=2)
    # runway
    base = y + h - 12
    d.rectangle([x, base, x + w, base + 4], fill=(70, 70, 70))
    for dx in range(6, w - 6, 14):
        d.line([x + dx, base + 2, x + dx + 7, base + 2], fill=(255, 255, 255),
               width=1)
    # plane body
    py = cy - 4
    d.polygon([(x + 6, py), (x + w - 22, py - 8), (x + w - 8, py - 2),
               (x + w - 22, py + 6), (x + 6, py + 6)], fill=(245, 245, 245),
              outline=INK, width=2)
    d.polygon([(x + w // 2, py - 6), (x + w // 2 + 12, py - 20),
               (x + w // 2 + 18, py - 6)], fill=(200, 210, 220), outline=INK, width=1)
    d.polygon([(x + 12, py + 4), (x + 22, py + 16), (x + 28, py + 4)],
              fill=(200, 210, 220), outline=INK, width=1)
    for wx in range(x + 14, x + w - 30, 9):
        d.ellipse([wx, py - 3, wx + 3, py], fill=BLUE)
    # right engine with smoke puffs
    ex, ey = x + w - 34, py + 8
    d.ellipse([ex, ey, ex + 10, ey + 6], fill=(90, 90, 90))
    for i, (sx, sy, sr) in enumerate(((ex + 12, ey - 6, 4), (ex + 20, ey - 12, 6),
                                      (ex + 30, ey - 18, 8))):
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(200, 200, 200),
                  outline=(160, 160, 160), width=1)
    # evacuation slide
    d.polygon([(x + w - 30, py + 6), (x + w - 14, py + 6), (x + w - 6, base),
               (x + w - 16, base)], fill=GOLD, outline=(150, 110, 10), width=1)


def illus_bitcoin(d, x, y, w, h, big):
    cx, cy = x + w // 2, y + h // 2
    # chart grid
    for gy in (y + 10, y + 22, y + 34):
        d.line([x + 6, gy, x + w - 8, gy], fill=(220, 212, 190), width=1)
    # candles falling
    cw = 10 if big else 5
    vals = (12, 18, 14, 26, 22, 34) if big else (14, 24, 18, 32)
    for i, v in enumerate(vals):
        bx = x + 8 + i * (cw + 4) if big else x + 5 + i * (cw + 3)
        by = y + 10 + v * (h - 30) // 40
        d.rectangle([bx, by, bx + cw, y + h - 16], fill=RED if i % 2 else (200, 80, 70))
        d.line([bx + cw // 2, by - 4, bx + cw // 2, by], fill=INK, width=1)
    # big coin
    r = 20 if big else 13
    ccx = cx + (w // 4 if big else 0)
    ccy = cy - 4
    d.ellipse([ccx - r, ccy - r, ccx + r, ccy + r], fill=(255, 200, 60),
              outline=GOLD, width=3)
    d.ellipse([ccx - r + 4, ccy - r + 4, ccx + r - 4, ccy + r - 4],
              outline=(200, 150, 30), width=1)
    d.text((ccx, ccy - 1), "B", font=SANS_B(22 if big else 14), fill=(150, 100, 10),
           anchor="mm")
    # down arrow
    d.line([x + w - 26, y + 8, x + w - 8, y + h - 22], fill=RED, width=3)
    d.polygon([(x + w - 8, y + h - 22), (x + w - 20, y + h - 24),
               (x + w - 10, y + h - 12)], fill=RED)


def illus_rahul(d, x, y, w, h, big):
    cx, cy = x + w // 2, y + h // 2
    # outfield
    d.rectangle([x, y, x + w, y + h], fill=(190, 220, 170))
    d.ellipse([x + 6, y + 6, x + w - 6, y + h - 6], outline=(150, 190, 130),
              width=2)
    # pitch
    d.rectangle([cx - 12, y + 6, cx + 12, y + h - 8], fill=(235, 220, 175))
    # stumps
    for sx in (cx - 8, cx - 3, cx + 2):
        d.line([sx, y + h - 24, sx, y + h - 12], fill=GOLD, width=2)
    d.line([cx - 9, y + h - 25, cx + 4, y + h - 25], fill=GOLD, width=2)
    # bat + ball
    d.line([cx - 20, cy + 14, cx - 2, cy - 12], fill=(190, 150, 90), width=5)
    d.rectangle([cx - 6, cy - 16, cx + 2, cy - 6], fill=(200, 160, 100),
                outline=(150, 110, 60), width=1)
    d.ellipse([cx + 14, cy - 20, cx + 22, cy - 12], fill=RED)
    d.arc([cx + 14, cy - 20, cx + 22, cy - 12], 200, 340, fill=(255, 255, 255),
          width=1)
    # scoreboard
    if big:
        d.rectangle([x + 4, y + 4, x + 62, y + 20], fill=INK)
        d.text((x + 33, y + 6), "124*", font=SANS_B(12), fill=(255, 255, 255),
               anchor="ma")
    else:
        d.rectangle([x + 2, y + 2, x + 34, y + 14], fill=INK)
        d.text((x + 18, y + 3), "124*", font=SANS_B(9), fill=(255, 255, 255),
               anchor="ma")


def illus_bepi(d, x, y, w, h, big):
    cx, cy = x + w // 2, y + h // 2
    rng = random.Random(77)
    d.rectangle([x, y, x + w, y + h], fill=(20, 24, 48))
    for _ in range(30 if big else 12):
        sx = x + rng.randint(2, w - 3)
        sy = y + rng.randint(2, h - 3)
        d.ellipse([sx, sy, sx + 2, sy + 2], fill=(255, 255, 255))
    # sun rays
    sx, sy = x + 12, y + 10
    for a in range(0, 360, 30):
        rr = math.radians(a)
        d.line([sx, sy, sx + 12 * math.cos(rr), sy + 12 * math.sin(rr)],
               fill=(255, 200, 60), width=2)
    d.ellipse([sx - 6, sy - 6, sx + 6, sy + 6], fill=(255, 220, 90))
    # Mercury
    mx, my = cx + w // 6, cy + h // 8
    mr = 16 if big else 10
    d.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(170, 160, 150),
              outline=(120, 110, 100), width=2)
    for (ccx, ccy, cr) in ((mx - 5, my - 3, 3), (mx + 4, my + 2, 2),
                           (mx + 1, my - 7, 2), (mx - 2, my + 6, 2)):
        d.ellipse([ccx - cr, ccy - cr, ccx + cr, ccy + cr], fill=(140, 130, 120))
    # orbit ellipse
    d.ellipse([x + 8, y + h // 2 - 6, x + w - 8, y + h - 4], outline=TEAL,
              width=1)
    # spacecraft
    px, py = cx - w // 4, cy + h // 6
    d.rectangle([px - 14, py - 3, px - 4, py + 3], fill=(60, 90, 160))
    d.rectangle([px + 4, py - 3, px + 14, py + 3], fill=(60, 90, 160))
    d.rectangle([px - 4, py - 6, px + 4, py + 6], fill=(220, 220, 220),
                outline=INK, width=1)
    d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=GOLD)
    # thruster flame
    d.polygon([(px - 4, py + 6), (px + 4, py + 6), (px, py + 16)],
              fill=(255, 170, 40))
    d.polygon([(px - 2, py + 6), (px + 2, py + 6), (px, py + 12)],
              fill=(255, 230, 120))


def illus_bridge(d, x, y, w, h, big):
    cx, cy = x + w // 2, y + h // 2
    # sky + sea
    d.rectangle([x, y, x + w, y + h // 2], fill=(200, 225, 240))
    d.rectangle([x, y + h // 2, x + w, y + h], fill=(120, 170, 210))
    for wy in range(y + h // 2 + 4, y + h - 2, 7):
        d.arc([x + 4, wy - 4, x + w - 4, wy + 4], 0, 180, fill=(90, 140, 190),
              width=1)
    # bridge deck with a broken span
    deck = y + h // 2 - 8
    d.line([x + 4, deck, x + w - 4, deck], fill=INK, width=3)
    gap = (cx - 12, cx + 12)
    d.line([gap[0], deck, gap[0], deck + 10], fill=INK, width=2)
    d.line([gap[1], deck, gap[1], deck + 10], fill=INK, width=2)
    d.polygon([(gap[0], deck), (gap[0] + 5, deck + 12), (gap[0] + 10, deck)],
              fill=(150, 140, 120))
    # arch
    ar = 34 if big else 16
    d.arc([cx - ar, deck - 26, cx + ar, deck + 8], 180, 360, fill=INK, width=3)
    d.arc([cx - ar, deck - 26, cx + ar, deck + 8], 200, 340, fill=RED, width=1)
    # fallen span in the water
    d.polygon([(gap[0] + 2, deck + 14), (gap[1] - 2, deck + 14),
               (gap[1] - 6, deck + 22), (gap[0] + 6, deck + 22)], fill=(120, 110, 100))
    # flags
    d.rectangle([x + 6, y + 6, x + 22, y + 16], fill=BLUE)
    d.rectangle([x + 6, y + 16, x + 22, y + 26], fill=GOLD)


def illus_drone(d, x, y, w, h, big):
    cx, cy = x + w // 2, y + h // 2
    # dusk sky over the strait
    for i in range(4):
        d.rectangle([x, y + i * h // 4, x + w, y + (i + 1) * h // 4],
                    fill=(250 - i * 18, 200 - i * 25, 130 - i * 15))
    d.ellipse([x + w - 26, y + 6, x + w - 10, y + 22], fill=(255, 220, 120))
    # sea
    d.rectangle([x, y + h * 2 // 3, x + w, y + h], fill=(70, 120, 170))
    for wy in range(y + h * 2 // 3 + 3, y + h - 2, 6):
        d.line([x + 4, wy, x + w - 4, wy], fill=(140, 190, 220), width=1)
    # tanker
    d.rectangle([x + 8, y + h - 20, x + w - 8, y + h - 12], fill=(120, 40, 40))
    d.rectangle([x + w - 26, y + h - 30, x + w - 12, y + h - 20],
                fill=(240, 240, 240))
    # drone
    dx, dy = cx, y + h // 3
    d.ellipse([dx - 12, dy - 3, dx + 12, dy + 3], fill=(60, 60, 60))
    d.rectangle([dx - 2, dy - 8, dx + 2, dy + 2], fill=(60, 60, 60))
    d.line([dx - 16, dy - 8, dx + 16, dy - 8], fill=(40, 40, 40), width=2)
    d.ellipse([dx - 20, dy - 11, dx - 12, dy - 5], fill=(120, 120, 120))
    d.ellipse([dx + 12, dy - 11, dx + 20, dy - 5], fill=(120, 120, 120))
    # radar arcs from a ship
    for r in (8, 14, 20):
        d.arc([x + w - 30 - r, y + h - 30 - r, x + w - 30 + r, y + h - 30 + r],
              270, 360, fill=(255, 255, 255), width=1)


def illus_datacentre(d, x, y, w, h, big):
    cx, cy = x + w // 2, y + h // 2
    d.rectangle([x, y, x + w, y + h], fill=(235, 238, 245))
    # server racks
    for i in range(3):
        rx = x + 6 + i * (w - 12) // 3
        rw = (w - 12) // 3 - 4
        d.rectangle([rx, y + 8, rx + rw, y + h - 16], fill=(50, 55, 70),
                    outline=INK, width=1)
        for ry in range(y + 12, y + h - 20, 9):
            d.rectangle([rx + 3, ry, rx + rw - 3, ry + 5], fill=(90, 120, 180))
            d.ellipse([rx + rw - 6, ry + 1, rx + rw - 3, ry + 4],
                      fill=(120, 220, 120))
    # tax document with dollar sign
    dx = cx + w // 4
    d.rectangle([dx - 12, y + h - 26, dx + 12, y + h - 8], fill=(255, 255, 255),
                outline=INK, width=1)
    d.text((dx, y + h - 24), "$", font=SANS_B(13), fill=RED, anchor="ma")
    # lightning bolt
    d.polygon([(cx - w // 4, y + 6), (cx - w // 4 - 6, y + 18),
               (cx - w // 4 - 1, y + 18), (cx - w // 4 - 6, y + 30),
               (cx - w // 4 + 4, y + 16), (cx - w // 4 - 1, y + 16)],
              fill=(255, 200, 40), outline=GOLD, width=1)


def illus_flags(d, x, y, w, h, big):
    cx, cy = x + w // 2, y + h // 2
    d.rectangle([x, y, x + w, y + h], fill=(245, 240, 225))
    # China flag
    fx = x + 6
    d.rectangle([fx, y + 10, fx + w // 2 - 10, y + h - 22], fill=RED)
    d.ellipse([fx + 6, y + 16, fx + 14, y + 24], fill=(255, 220, 60))
    for (sx, sy) in ((fx + 18, y + 14), (fx + 22, y + 20), (fx + 18, y + 26),
                      (fx + 14, y + 22)):
        d.ellipse([sx, sy, sx + 3, sy + 3], fill=(255, 220, 60))
    # Japan flag
    jx = x + w // 2 + 4
    d.rectangle([jx, y + 10, jx + w // 2 - 10, y + h - 22], fill=(255, 255, 255),
                outline=INK, width=1)
    d.ellipse([jx + w // 4 - 9, cy - 9, jx + w // 4 + 9, cy + 9], fill=RED)
    # speech lines between
    for i, sy in enumerate((y + 14, y + 22, y + 30)):
        d.line([fx + w // 2 - 6, sy, jx - 2, sy], fill=GREY, width=1)


def illus_makefun(d, x, y, w, h, big):
    cx, cy = x + w // 2, y + h // 2
    d.rectangle([x, y, x + w, y + h], fill=(238, 230, 250))
    # ghost mascot
    r = 20 if big else 12
    gx, gy = cx, cy - 4
    d.ellipse([gx - r - 4, gy - r - 4, gx + r + 4, gy + r + 4],
              fill=(225, 210, 245))
    d.ellipse([gx - r + 2, gy - r + 2, gx + r - 2, gy + r - 6], fill=PURPLE)
    d.rectangle([gx - r + 2, gy - 2, gx + r - 2, gy + r - 6], fill=PURPLE)
    tw = 10 if big else 7
    for gxx in (gx - r + 2, gx - tw // 2, gx + r - 2 - tw):
        d.polygon([(gxx, gy + r - 6), (gxx + tw // 2, gy + r + 3),
                   (gxx + tw, gy + r - 6)], fill=PURPLE)
    d.ellipse([gx - 10, gy - 10, gx - 4, gy - 2], fill=INK)
    d.ellipse([gx + 4, gy - 10, gx + 10, gy - 2], fill=INK)
    d.ellipse([gx - 8, gy - 8, gx - 6, gy - 6], fill=(255, 255, 255))
    d.ellipse([gx + 6, gy - 8, gx + 8, gy - 6], fill=(255, 255, 255))
    d.arc([gx - 6, gy - 2, gx + 6, gy + 6], 0, 180, fill=INK, width=2)
    # gold coin
    d.ellipse([x + w - 30, y + 8, x + w - 12, y + 26], fill=(255, 210, 80),
              outline=GOLD, width=2)
    d.text((x + w - 21, y + 11), "$", font=SANS_B(11), fill=GOLD, anchor="ma")
    # confetti
    rng = random.Random(31)
    for _ in range(14 if big else 7):
        px = x + rng.randint(2, w - 4)
        py = y + rng.randint(2, h - 4)
        d.rectangle([px, py, px + 3, py + 2],
                    fill=rng.choice([RED, GOLD, TEAL, PURPLE]))


def illus_denmark(d, x, y, w, h, big):
    cx, cy = x + w // 2, y + h // 2
    d.rectangle([x, y, x + w, y + h], fill=(240, 235, 220))
    # Danish flag
    fx, fy = x + 6, y + 8
    fw, fh = w // 2 - 8, h // 2 - 6
    d.rectangle([fx, fy, fx + fw, fy + fh], fill=RED)
    d.rectangle([fx + fw // 3, fy, fx + fw // 3 + 6, fy + fh],
                fill=(255, 255, 255))
    d.rectangle([fx, fy + fh // 2 - 3, fx + fw, fy + fh // 2 + 3],
                fill=(255, 255, 255))
    # shield
    sh = 18 if big else 11
    sx, sy = cx + w // 5, cy + 2
    d.polygon([(sx, sy - sh), (sx + sh, sy - sh + 6), (sx + sh, sy + 4),
               (sx, sy + sh + 6), (sx - sh, sy + 4), (sx - sh, sy - sh + 6)],
              fill=(250, 225, 220), outline=RED, width=3)
    d.text((sx, sy - 6), "!", font=SANS_B(14 if big else 10), fill=RED,
           anchor="ma")
    # scales of justice
    bx = x + w - 26
    d.line([bx, y + h - 24, bx, y + h - 8], fill=INK, width=2)
    d.line([bx - 10, y + h - 24, bx + 10, y + h - 24], fill=INK, width=2)
    d.polygon([(bx - 12, y + h - 22), (bx - 6, y + h - 22), (bx - 9, y + h - 14)],
              fill=GOLD)
    d.polygon([(bx + 6, y + h - 22), (bx + 12, y + h - 22), (bx + 9, y + h - 14)],
              fill=GOLD)


ILLUS = {1: illus_cop31, 2: illus_missiles, 3: illus_quake, 4: illus_davao,
         5: illus_bitcoin, 6: illus_rahul, 7: illus_bepi, 8: illus_bridge,
         9: illus_drone, 10: illus_datacentre, 11: illus_flags,
         12: illus_makefun, 13: illus_denmark}

# ---------------------------------------------------------------- page

def draw_illus_layer(img, num, x, y, w, h, big):
    """Draw one illustration onto its own layer and paste it, so no stroke
    can spill past the illustration box onto neighbouring text."""
    layer = Image.new("RGB", (w, h), CARD)
    ld = ImageDraw.Draw(layer)
    ILLUS[num](ld, 0, 0, w, h, big)
    img.paste(layer, (x, y))

def draw_paper(d):
    """Subtle vertical gradient + deterministic speckle, for a printed feel
    and a denser PNG."""
    for yy in range(H):
        t = yy / H
        c = (247 - int(6 * t), 241 - int(7 * t), 222 - int(9 * t))
        d.line([0, yy, W, yy], fill=c)
    rng = random.Random(20261121)
    for _ in range(90000):
        px = rng.randint(0, W - 1)
        py = rng.randint(0, H - 1)
        shade = rng.choice([(238, 230, 205), (250, 246, 232), (235, 226, 198),
                            (252, 248, 236)])
        d.point((px, py), fill=shade)
    # faint diagonal hatch, like newsprint grain
    for xx in range(-H, W, 7):
        d.line([xx, 0, xx + H, H], fill=(244, 237, 216), width=1)
    # faint column rules, like newsprint
    for xx in range(0, W, 7):
        if xx % 49 == 0:
            d.line([xx, 0, xx, H], fill=(243, 236, 214), width=1)


def main():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    draw_paper(d)
    M = 16

    # --- top strip ---
    d.rectangle([0, 0, W, 24], fill=INK)
    d.text((M, 4), "THE WORLD IN ONE DAY", font=SANS_B(13),
           fill=(255, 255, 255))
    d.text((W - M, 4), "35 STORIES  ·  7 REGIONS  ·  EVERY ONE DATED",
           font=SANS_B(12), fill=(255, 220, 120), anchor="ra")

    # --- masthead ---
    d.text((W // 2, 30), "THE TWENTY-FIRST", font=SERIF_B(56), fill=INK,
           anchor="ma")
    d.line([M, 94, W - M, 94], fill=INK, width=2)
    d.text((W // 2, 100), "SATURDAY 21 NOVEMBER 2026", font=SANS_B(22),
           fill=RED, anchor="ma")
    d.text((W // 2, 126),
           "COP31 in overtime  •  Three missiles down over Riyadh  •  "
           "Peru shaken by a 6.7 quake",
           font=SERIF(15), fill=INK, anchor="ma")

    # --- region strip: equal cells, counts sum to 35 ---
    # (Proportional widths made the AFRICA cell unreadable, so the strip
    # uses equal cells and the counts carry the breakdown.)
    counts = {}
    for _, r, *_ in HEROES + FEATURES:
        counts[r] = counts.get(r, 0) + 1
    for _, r, *_ in BRIEFS:
        counts[r] = counts.get(r, 0) + 1
    assert sum(counts.values()) == 35, counts
    y = 148
    x = M
    total_w = W - 2 * M
    cw_strip = total_w // 7
    for i, (name, code, col) in enumerate(REGIONS):
        n = counts[code]
        seg = cw_strip if i < 6 else total_w - 6 * cw_strip
        d.rectangle([x, y, x + seg - 2, y + 20], fill=col)
        d.text((x + seg // 2 - 1, y + 3), f"{name} {n}", font=SANS_B(11),
               fill=(255, 255, 255), anchor="ma")
        x += seg

    # --- stat strip: 6 numbers ---
    y = 174
    bw = (W - 2 * M) // 6
    for i, (num, lab) in enumerate(STATS):
        bx = M + i * bw
        d.rectangle([bx + 2, y, bx + bw - 2, y + 34], outline=LINE, width=1,
                    fill=PAPER2)
        d.text((bx + bw // 2, y + 2), num, font=SANS_B(15), fill=RED,
               anchor="ma")
        d.text((bx + bw // 2, y + 19), lab, font=SANS(10), fill=INK,
               anchor="ma")

    # --- 3 heroes ---
    y0 = 216
    cw = (W - 2 * M - 2 * 10) // 3
    for i, (num, reg, head, summ, src, lab) in enumerate(HEROES):
        x = M + i * (cw + 10)
        col = REG_COL[reg]
        d.rectangle([x, y0, x + cw, y0 + 178], outline=LINE, width=1,
                    fill=CARD)
        d.rectangle([x, y0, x + cw, y0 + 20], fill=col)
        d.text((x + 6, y0 + 2), f"{num:02d}", font=SANS_B(13),
               fill=(255, 255, 255))
        d.text((x + cw - 6, y0 + 3), REG_NAME[reg], font=SANS_B(11),
               fill=(255, 255, 255), anchor="ra")
        draw_illus_layer(img, num, x + 4, y0 + 24, cw - 8, 62, big=True)
        lines = wrap(d, head, SERIF_B(14), cw - 10)
        yy = y0 + 90
        for ln in lines[:2]:
            d.text((x + 5, yy), ln, font=SERIF_B(14), fill=INK)
            yy += 17
        lines = wrap(d, summ, SANS(11), cw - 10)
        for ln in lines[:3]:
            d.text((x + 5, yy), ln, font=SANS(11), fill=INK)
            yy += 13
        d.text((x + 5, y0 + 178 - 13), f"({src})", font=SANS(9), fill=GREY)
        label_chip(d, x + cw - 62, y0 + 178 - 14, lab)

    # --- features 04-13: 2 cols x 5 rows ---
    fy = 400
    rh = 50
    fw = (W - 2 * M - 10) // 2
    for i, (num, reg, head, summ, src, lab) in enumerate(FEATURES):
        col_i, row_i = i % 2, i // 2
        x = M + col_i * (fw + 10)
        y = fy + row_i * rh
        col = REG_COL[reg]
        d.rectangle([x, y, x + fw, y + rh - 4], outline=LINE, width=1,
                    fill=CARD)
        d.rectangle([x, y, x + 30, y + rh - 4], fill=col)
        d.text((x + 15, y + 5), f"{num:02d}", font=SANS_B(12),
               fill=(255, 255, 255), anchor="ma")
        d.text((x + 15, y + 24), reg, font=SANS_B(9),
               fill=(255, 255, 255), anchor="ma")
        d.text((x + 36, y + 2), head, font=SANS_B(12), fill=INK)
        lines = wrap(d, summ, SANS(11), fw - 36 - 52)
        yy = y + 17
        for ln in lines[:2]:
            d.text((x + 36, yy), ln, font=SANS(11), fill=INK)
            yy += 13
        draw_illus_layer(img, num, x + fw - 48, y + 3, 44, 40, big=False)
        d.text((x + 36, y + rh - 13), f"({src})", font=SANS(9), fill=GREY)
        label_chip(d, x + fw - 66, y + rh - 14, lab)

    # --- map band + DATE CHECK ---
    my0 = 656
    d.rectangle([M, my0, 700, my0 + 78], outline=LINE, width=1,
                fill=(238, 232, 205))
    d.text((M + 6, my0 + 4),
           "WHERE IT HAPPENED — the 11 located stories, numbered",
           font=SANS_B(11), fill=INK)
    mx0, my1, mw, mh = M + 8, my0 + 18, 668, 54
    # graticule
    for gx in range(mx0, mx0 + mw, 55):
        d.line([gx, my1, gx, my1 + mh], fill=(225, 218, 190), width=1)
    for gy in range(my1, my1 + mh, 13):
        d.line([mx0, gy, mx0 + mw, gy], fill=(225, 218, 190), width=1)
    # ocean stipple
    rng = random.Random(1121)
    for _ in range(1500):
        px = rng.randint(mx0, mx0 + mw - 1)
        py = rng.randint(my1, my1 + mh - 1)
        d.point((px, py), fill=(200, 192, 160))
    for poly in CONTINENTS:
        pts = [project(lon, lat, mx0, my1, mw, mh) for lon, lat in poly]
        d.polygon(pts, fill=MAPLAND, outline=(150, 140, 110), width=1)
    for n, (lon, lat) in PINS.items():
        px, py = project(lon, lat, mx0, my1, mw, mh)
        d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=RED,
                  outline=(255, 255, 255), width=1)
        d.text((px, py - 5), str(n), font=SANS_B(8), fill=(255, 255, 255),
               anchor="ma")
    # DATE CHECK box
    dx0 = 710
    d.rectangle([dx0, my0, W - M, my0 + 78], outline=RED, width=2,
                fill=(255, 240, 235))
    d.text((dx0 + 6, my0 + 3), "DATE CHECK — NOT 21 NOVEMBER",
           font=SANS_B(11), fill=RED)
    for j, ln in enumerate(wrap(d, DATE_CHECK, SANS(10), W - M - dx0 - 12)):
        d.text((dx0 + 6, my0 + 18 + j * 11), ln, font=SANS(10), fill=INK)

    # --- how we checked ---
    d.text((M, 738),
           "HOW WE CHECKED:  CONFIRMED verified  ·  OFFICIAL stated by an "
           "authority  ·  REPORTED not yet verified  ·  CLAIM one side's "
           "claim  ·  FORECAST still to happen",
           font=SANS(10), fill=GREY)

    # --- briefs 14-35: 2 cols x 11 rows ---
    by = 756
    d.text((M, by), "THE REST OF THE DAY — briefs 14–35", font=SANS_B(12),
           fill=INK)
    by += 16
    brh = 17
    bw2 = (W - 2 * M - 10) // 2
    for i, (num, reg, text, src, lab) in enumerate(BRIEFS):
        col_i, row_i = i % 2, i // 2
        x = M + col_i * (bw2 + 10)
        y = by + row_i * brh
        d.text((x, y), f"{num}.", font=SANS_B(11), fill=REG_COL[reg])
        full = f"{text} ({src}) [{lab}]"
        fnt = fit_font(d, full, "DejaVuSans.ttf", 11, bw2 - 26)
        d.text((x + 24, y), full, font=fnt, fill=INK)

    # --- footer ---
    fy2 = by + 11 * brh + 6
    d.line([M, fy2, W - M, fy2], fill=LINE, width=1)
    d.text((M, fy2 + 4),
           "Sources: AP, Reuters, USGS, CAAP, Finnhub, IANS, ESA, NBC, "
           "Al Jazeera, IRIB, Saudi Press Agency, UN News, F1, KCNA, Yonhap, "
           "CNA, PTI, IMD, CBC, AAP, h.ua, make.fun — named per story.",
           font=SANS(9), fill=GREY)
    d.text((M, fy2 + 16),
           "All 35 stories happened or were first reported on Saturday 21 "
           "November 2026. Story 7 is a scheduled event; story 9 and story 14 "
           "are claims, not confirmed facts.",
           font=SANS(9), fill=GREY)
    img.save("entry.png", optimize=True)


if __name__ == "__main__":
    main()
    print("wrote entry.png")
