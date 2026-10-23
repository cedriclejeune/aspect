"""Simple vector art for the base-set cards (tools/build_cards.py).

Each drawing is a 100 × 100 SVG body in the rulebook style: ink line art on parchment,
crimson and gold accents. art(name) returns a full <svg>, or None when a card has no drawing.
Weapons are drawn upright, then turned to a diagonal.
"""
import math

from illustrations import CRIMSON, GOLD, INK, PARCH, SHADE, MUTED, ASPECT_GREEN, CRYSTAL, gem, sym_int, sym_str, sym_dex, sym_wil

STEEL = "#d9d6cc"
WOOD = "#9a6b3a"
LEATHER = "#a8743f"
DARK = "#4a3a2c"
MOSS = "#6f8f4e"


def svg(body, label):
    return (f'<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{label}">'
            f'<g stroke="{INK}" stroke-width="2.6" stroke-linejoin="round" stroke-linecap="round">{body}</g></svg>')


def rot(body, a=45, s=1.2):
    """Turn an upright drawing; s enlarges it to fill the diagonal."""
    return f'<g transform="translate(50 50) scale({s}) rotate({a}) translate(-50 -50)">{body}</g>'


def P(d, fill="none", sw=None, extra=""):
    w = f' stroke-width="{sw}"' if sw else ""
    return f'<path d="{d}" fill="{fill}"{w}{extra}/>'


def C(x, y, r, fill="none", sw=None):
    w = f' stroke-width="{sw}"' if sw else ""
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}"{w}/>'


def R(x, y, w, h, fill="none", rx=0, sw=None):
    s = f' stroke-width="{sw}"' if sw else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"{s}/>'


def L(x1, y1, x2, y2, sw=None, color=INK):
    w = f' stroke-width="{sw}"' if sw else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}"{w}/>'


def star(cx, cy, r, n=5, inner=.45, fill=GOLD):
    pts = " ".join(f"{cx + (r if i % 2 == 0 else r * inner) * math.sin(math.pi * i / n):.1f},"
                   f"{cy - (r if i % 2 == 0 else r * inner) * math.cos(math.pi * i / n):.1f}" for i in range(2 * n))
    return f'<polygon points="{pts}" fill="{fill}"/>'


def hexa(cx, cy, r, fill):
    pts = " ".join(f"{cx + r * math.cos(math.radians(60 * i + 30)):.1f},{cy + r * math.sin(math.radians(60 * i + 30)):.1f}" for i in range(6))
    return f'<polygon points="{pts}" fill="{fill}"/>'


# ---------- weapons (upright: tip at the top) ----------
def blade(top, bottom, w, guard, grip, pommel=True, hw=None):
    hw = hw or guard * .2
    return (P(f"M50 {top} L{50 + w / 2} {top + w} L{50 + w / 2} {bottom} L{50 - w / 2} {bottom} L{50 - w / 2} {top + w} Z", STEEL)
            + L(50, top + w + 2, 50, bottom - 3, 1.2, MUTED)
            + R(50 - guard / 2, bottom, guard, 5, GOLD, 2)
            + R(50 - 3.5, bottom + 5, 7, grip, LEATHER, 1.5)
            + (C(50, bottom + 5 + grip + 4, 4.5, GOLD) if pommel else ""))


def dagger():
    return rot(blade(18, 56, 11, 26, 14))


def shortsword():
    return rot(blade(12, 60, 10, 30, 14))


def longsword():
    return rot(blade(5, 63, 9, 34, 17))


def greatsword():
    return rot(P("M50 2 L57 10 L57 62 L43 62 L43 10 Z", STEEL) + L(50, 12, 50, 58, 1.2, MUTED)
               + P("M28 62 Q50 58 72 62 L72 67 Q50 63 28 67 Z", GOLD) + R(46, 67, 8, 22, LEATHER, 1.5) + C(50, 93, 4.5, GOLD))


def rapier():
    return rot(P("M50 3 L52 8 L52 62 L48 62 L48 8 Z", STEEL) + P("M36 62 L64 62", sw=3.4)
               + P("M38 62 Q36 76 50 76 Q62 76 62 64", sw=2.2) + R(47, 64, 6, 18, LEATHER, 1.5) + C(50, 86, 4, GOLD))


def haft(top, bottom, w=6):
    return R(50 - w / 2, top, w, bottom - top, WOOD, 2)


def handaxe():
    return rot(haft(20, 92) + P("M53 18 Q76 14 80 34 Q72 44 53 38 Z", STEEL) + L(56, 24, 56, 34, 1.2, MUTED), -30)


def battleaxe():
    return rot(haft(8, 94) + P("M53 14 Q80 6 84 32 Q80 52 53 44 Z", STEEL) + P("M47 14 Q20 6 16 32 Q20 52 47 44 Z", STEEL), -30)


def glaive():
    return rot(haft(30, 97, 5) + P("M48 34 L48 6 Q66 14 60 40 Q56 44 48 40 Z", STEEL) + R(45, 36, 10, 6, GOLD, 2), 30)


def spear(lugs=False):
    out = haft(26, 97, 5) + P("M50 3 Q60 16 54 30 L46 30 Q40 16 50 3 Z", STEEL) + L(50, 8, 50, 27, 1.2, MUTED)
    if lugs:
        out += P("M38 34 L62 34", sw=4) + R(46, 30, 8, 7, GOLD, 2)
    return rot(out, 35)


def longbow():
    return (P("M30 6 Q82 50 30 94", sw=4.2, extra=f' stroke="{WOOD}"') + P("M30 6 Q82 50 30 94", sw=1.2, extra=f' stroke="{INK}"')
            + L(30, 6, 30, 94, 1.2) + L(16, 50, 84, 50, 2.2) + P("M84 50 L74 45 L76 50 L74 55 Z", STEEL)
            + P("M16 50 L10 45 M16 50 L10 55 M21 50 L15 45 M21 50 L15 55", sw=1.6, extra=f' stroke="{CRIMSON}"'))


def sling():
    return (P("M18 14 Q30 46 40 62", sw=2) + P("M82 14 Q70 46 60 62", sw=2) + C(18, 12, 4) + P("M38 60 Q50 80 62 60 Q50 66 38 60 Z", LEATHER)
            + C(50, 64, 6, "#9a9488"))


def javelins():
    out = ""
    for a in (-22, 0, 22):
        out += f'<g transform="rotate({a} 50 90)">' + R(48, 22, 4, 72, WOOD, 1.5) + P("M50 4 L55 22 L45 22 Z", STEEL) + "</g>"
    return out + P("M30 70 L70 70", sw=5, extra=f' stroke="{LEATHER}"')


def greatclub():
    return rot(P("M45 94 L46 44 Q38 16 50 6 Q64 14 56 44 L55 94 Z", WOOD) + C(46, 26, 2.4, DARK, 1.2) + C(55, 34, 2.4, DARK, 1.2)
               + C(50, 16, 2, DARK, 1.2) + R(44, 80, 12, 5, LEATHER, 1.5), 30)


def gladius():
    return rot(blade(14, 58, 14, 24, 13))


def pilum():
    return rot(R(47.5, 44, 5, 52, WOOD, 1.8) + R(49, 12, 2, 34, STEEL, 1.4) + P("M50 2 L54 12 L46 12 Z", STEEL) + R(45, 42, 10, 5, GOLD, 1.6), 35)


def shield_wall():
    out = ""
    for x in (12, 38, 64):
        out += R(x, 20, 24, 60, CRIMSON, 4) + C(x + 12, 50, 5, GOLD, 1.6) + L(x + 12, 24, x + 12, 44, 1.2, GOLD) + L(x + 12, 56, x + 12, 76, 1.2, GOLD)
    return out


def staff():
    return rot(haft(26, 97, 6) + C(50, 16, 11, CRYSTAL) + C(46, 12, 3, PARCH, 0) + P("M40 26 Q50 32 60 26", sw=3) + R(45, 52, 10, 6, GOLD, 2), 20)


def lute():
    return rot(P("M50 44 C28 44 22 72 34 86 C42 96 58 96 66 86 C78 72 72 44 50 44 Z", LEATHER) + C(50, 68, 7, DARK)
               + R(46, 8, 8, 38, WOOD, 2) + R(43, 2, 14, 9, DARK, 2) + L(48, 10, 48, 88, .8) + L(52, 10, 52, 88, .8) + R(42, 82, 16, 4, DARK, 1), 30)


# ---------- armor and shields ----------
TORSO = "M30 18 L42 12 Q50 18 58 12 L70 18 L84 30 L76 44 L70 40 L70 88 L30 88 L30 40 L24 44 L16 30 Z"


def leather():
    return (P(TORSO, LEATHER) + P("M42 12 Q50 30 58 12", sw=2) + L(50, 26, 50, 86, 1.4)
            + P("M34 50 L66 50 M34 66 L66 66", sw=1.4, extra=' stroke-dasharray="3 3"') + R(30, 74, 40, 6, DARK, 1, 1.6))


def mail():
    rings = "".join(C(36 + 7 * i + (3.5 if j % 2 else 0), 30 + 7 * j, 3.2, "none", 1.1) for j in range(8) for i in range(4) if 36 + 7 * i + (3.5 if j % 2 else 0) < 66)
    return P(TORSO, STEEL) + rings + P("M42 12 Q50 22 58 12", sw=2)


def plate():
    return (P("M30 24 Q50 16 70 24 L70 62 Q50 92 30 62 Z", STEEL) + L(50, 22, 50, 82, 1.6) + P("M36 40 Q50 46 64 40", sw=1.6)
            + P("M30 24 Q16 22 14 40 L28 42 Z", STEEL) + P("M70 24 Q84 22 86 40 L72 42 Z", STEEL) + C(50, 32, 3, GOLD, 1.4))


def round_shield():
    return C(50, 50, 40, LEATHER) + C(50, 50, 40, "none", 5) + C(50, 50, 12, STEEL) + C(50, 50, 4, GOLD, 1.4) + L(50, 14, 50, 36, 1.4) + L(50, 64, 50, 86, 1.4)


def heater(cx=50, cy=50, s=1, fill=STEEL):
    return f'<g transform="translate({cx} {cy}) scale({s}) translate(-50 -50)">' + P("M18 12 Q50 2 82 12 L82 44 Q78 76 50 94 Q22 76 18 44 Z", fill) + "</g>"


# ---------- jewelry ----------
def ring(top=None, band=GOLD):
    return C(50, 60, 26, "none", 9) + f'<circle cx="50" cy="60" r="26" fill="none" stroke="{band}" stroke-width="5"/>' + (top or "")


def ring_of_warding():
    return ring(heater(50, 28, .34, CRIMSON))


def guild_signet():
    return ring(R(36, 18, 28, 22, GOLD, 4) + P("M44 30 a4 4 0 1 1 8 0 a4 4 0 1 1 -8 0 M52 30 L60 30 M57 30 L57 34", sw=1.8))


def ring_of_sparks():
    return ring(P("M54 6 L40 30 L50 30 L44 48 L62 22 L52 22 L58 6 Z", GOLD))


def bandolier():
    return (P("M14 20 L28 12 L88 78 L74 86 Z", LEATHER) + hexa(36, 32, 8, CRYSTAL) + hexa(51, 48, 8, CRYSTAL) + hexa(66, 64, 8, CRYSTAL)
            + R(70, 74, 12, 10, GOLD, 2))


def amulet():
    return P("M24 10 Q50 52 76 10", sw=2.2, extra=' stroke-dasharray="4 2"') + C(50, 62, 22, GOLD) + star(50, 62, 15, 8, .5, PARCH) + C(50, 62, 5, CRIMSON, 1.4)


def boots():
    return (P("M38 14 L58 14 L58 62 Q82 66 86 80 L86 88 L36 88 Z", LEATHER) + L(36, 80, 86, 80, 1.6) + P("M58 26 L38 26", sw=1.6)
            + P("M30 30 L12 24 M30 42 L8 42 M30 54 L12 60", sw=2, extra=f' stroke="{GOLD}"'))


# ---------- items ----------
def flask(liquid=CRIMSON, big=False):
    r = 30 if big else 24
    cy = 62 if big else 64
    return (R(42, 12, 16, 16, PARCH, 2) + R(40, 8, 20, 6, WOOD, 2) + C(50, cy, r, PARCH)
            + P(f"M{50 - r + 2} {cy} A{r - 2} {r - 2} 0 0 0 {50 + r - 2} {cy} Z", liquid, 0) + C(50, cy, r) + C(42, cy - 8, 3, "#fff", 0))


def pouch():
    return (P("M30 34 Q16 70 30 86 L70 86 Q84 70 70 34 Q50 28 30 34 Z", LEATHER) + P("M30 34 Q50 42 70 34", sw=2) + P("M44 26 Q50 36 56 26", sw=2)
            + C(66, 82, 10, GOLD) + C(78, 78, 8, GOLD) + star(50, 60, 7, 5, .45, GOLD))


def scroll():
    return (R(24, 18, 52, 64, PARCH, 3) + P("M24 18 Q18 18 18 24 Q18 30 24 30") + P("M76 82 Q82 82 82 76 Q82 70 76 70")
            + "".join(L(32, 32 + 8 * i, 68 - (10 if i == 3 else 0), 32 + 8 * i, 1.4) for i in range(5)) + C(64, 72, 8, CRIMSON) + star(64, 72, 5, 5, .5, PARCH))


def fire_flask():
    return flask(GOLD) + P("M50 2 Q60 14 54 22 Q50 16 46 22 Q40 14 50 2 Z", CRIMSON, 1.6)


def book(mark):
    return R(22, 14, 56, 74, CRIMSON, 4) + R(28, 14, 50, 74, "none", 2) + L(30, 14, 30, 88, 2) + mark


# ---------- Cores: the crimson gem, with the lead ability's symbol ----------
def core(sym, big=False):
    return gem(46, 46, 36 if big else 30, CRIMSON) + C(74, 74, 17, PARCH) + sym(74, 74, 22)


def balanced():
    return gem(50, 50, 22, CRIMSON) + "".join(C(x, y, 11, PARCH) + s(x, y, 14) for (x, y), s in
                                              (((50, 12), sym_str), ((88, 50), sym_dex), ((50, 88), sym_int), ((12, 50), sym_wil)))


def bandit_core():
    return core(sym_dex) + f'<g transform="translate(2 2) scale(.42)">{dagger()}</g>'


# ---------- Aspects ----------
def eye(cx=50, cy=50, s=1, iris=GOLD):
    return f'<g transform="translate({cx} {cy}) scale({s}) translate(-50 -50)">' + P("M10 50 Q50 14 90 50 Q50 86 10 50 Z", PARCH) + C(50, 50, 16, iris) + C(50, 50, 7, INK, 0) + C(54, 45, 3, "#fff", 0) + "</g>"


def springheel():
    return (P("M30 88 L42 82 L30 76 L42 70 L30 64 L42 58 L30 52", sw=3, extra=f' stroke="{MUTED}"') + boots_small(36, 30)
            + P("M48 70 Q70 10 92 52", sw=2.4, extra=' stroke-dasharray="5 4"') + P("M92 52 L86 44 M92 52 L82 52", sw=2.4))


def boots_small(x, y):
    return f'<g transform="translate({x - 24} {y - 22}) scale(.5)">' + P("M38 14 L58 14 L58 62 Q82 66 86 80 L86 88 L36 88 Z", LEATHER) + "</g>"


def stone_blood():
    return P("M50 8 Q78 46 78 64 A28 28 0 0 1 22 64 Q22 46 50 8 Z", "#9a9488") + P("M40 46 L50 58 L46 70 M60 52 L56 64", sw=1.8) + P("M36 64 Q38 78 50 80", sw=2.2, extra=f' stroke="{CRIMSON}"')


def iron_will():
    return heater(50, 52, .9, "#9a9488") + sym_wil(50, 48, 40)


def clear_mind():
    return "".join(L(50 + 30 * math.cos(math.radians(a)), 50 + 30 * math.sin(math.radians(a)), 50 + 44 * math.cos(math.radians(a)), 50 + 44 * math.sin(math.radians(a)), 2.4)
                   for a in range(0, 360, 30)) + eye(50, 50, .62, "#6f9fb0")


def cleave():
    return f'<g transform="translate(-8 4) scale(.8)">{handaxe()}</g>' + P("M54 20 Q92 44 70 90", sw=3.2, extra=f' stroke="{CRIMSON}"') + P("M64 16 Q100 46 80 90", sw=1.8, extra=f' stroke="{CRIMSON}"')


def steady_aim():
    return C(50, 50, 36, PARCH) + C(50, 50, 24, "none") + C(50, 50, 11, CRIMSON) + L(50, 6, 50, 26) + L(50, 74, 50, 94) + L(6, 50, 26, 50) + L(74, 50, 94, 50)


def shield_bash():
    return heater(40, 52, .72, STEEL) + C(40, 46, 6, GOLD) + "".join(L(72, 50 + d, 92, 50 + d * 2, 3) for d in (-16, 0, 16))


def note(x, y, s=1, fill=INK):
    return f'<g transform="translate({x} {y}) scale({s})">' + f'<ellipse cx="0" cy="0" rx="7" ry="5" fill="{fill}" transform="rotate(-20)"/>' + L(6, -2, 6, -30, 2.6) + P("M6 -30 Q16 -26 16 -16", sw=2.6) + "</g>"


def battle_hymn():
    return f'<g transform="translate(-14 4) scale(.85)">{longsword()}</g>' + note(66, 46, 1.1) + note(80, 72, .8)


def banner(color=CRIMSON):
    return R(22, 8, 5, 88, WOOD, 2) + C(24.5, 8, 4, GOLD) + P(f"M27 14 L84 14 L72 32 L84 50 L27 50 Z", color) + star(50, 32, 9, 5, .45, GOLD)


def padlock():
    return P("M34 46 L34 32 A16 16 0 0 1 66 32 L66 46", sw=6, extra=f' stroke="{MUTED}"') + R(26, 44, 48, 42, GOLD, 5) + C(50, 60, 5, INK, 0) + P("M48 62 L46 74 L54 74 L52 62 Z", INK, 0) + P("M66 78 L92 92 M84 88 L88 82", sw=2.6)


def laurel():
    out = ""
    for side in (-1, 1):
        out += P(f"M50 88 Q{50 + side * 40} 70 {50 + side * 30} 16", sw=2.4)
        for k in range(5):
            t = .18 + k * .17
            x = 50 + side * (40 * 2 * t * (1 - t) + 30 * t * t) * 1
            y = 88 * (1 - t) ** 2 + 70 * 2 * t * (1 - t) + 16 * t * t
            out += f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="5" ry="10" fill="{MOSS}" transform="rotate({side * (40 - k * 12)} {x:.1f} {y:.1f})"/>'
    return out + star(50, 46, 13)


def anchor():
    return C(50, 18, 8, "none", 4) + L(50, 26, 50, 86, 5) + L(32, 36, 68, 36, 5) + P("M18 62 Q22 88 50 88 Q78 88 82 62", sw=5) + P("M12 66 L18 58 L24 66 M76 66 L82 58 L88 66", sw=4)


def street_urchin():
    return pouch() + f'<g transform="translate(54 0) scale(.46)">{dagger()}</g>'


def tracks():
    def paw(x, y, s):
        return (f'<g transform="translate({x} {y}) scale({s})">' + f'<ellipse cx="0" cy="6" rx="9" ry="8" fill="{DARK}"/>'
                + "".join(C(dx, dy, 3.6, DARK) for dx, dy in ((-10, -6), (-4, -12), (4, -12), (10, -6))) + "</g>")
    return paw(30, 74, 1) + paw(56, 56, 1) + paw(38, 34, .9) + paw(66, 18, .8)


def mortar():
    return R(46, 6, 8, 46, WOOD, 3) + P("M16 46 L84 46 Q82 82 50 86 Q18 82 16 46 Z", "#b9b2a2") + R(12, 42, 76, 8, "#b9b2a2", 3) + P("M30 60 Q50 70 70 60", sw=1.6) + P("M60 22 q8 -8 16 0 q-8 8 -16 0", MOSS, 1.6)


def tankard():
    return R(22, 26, 46, 62, STEEL, 4) + P("M68 38 Q90 38 90 56 Q90 74 68 74", sw=6) + P("M18 28 Q24 10 40 16 Q50 6 60 16 Q74 12 72 28 Z", PARCH) + L(30, 40, 30, 80, 1.4) + L(46, 40, 46, 80, 1.4)


def smith():
    return (P("M14 70 L86 70 L76 80 L60 80 L64 92 L36 92 L40 80 L24 80 Z", DARK)
            + rot(R(46, 26, 8, 52, WOOD, 2) + R(32, 14, 36, 16, STEEL, 2), -40, 1) + P("M70 54 l6 -6 M78 60 l8 -2 M66 48 l2 -8", sw=2, extra=f' stroke="{GOLD}"'))


def mountains():
    return P("M4 88 L36 30 L52 56 L66 36 L96 88 Z", "#a39d8f") + P("M28 44 L36 30 L44 44 L40 40 L36 46 L32 40 Z", PARCH, 1.6) + L(66, 36, 66, 10, 2.4) + P("M66 10 L84 16 L66 22 Z", CRIMSON)


def crossed_swords():
    return (f'<g transform="translate(0 4) scale(.85) translate(9 0)">{rot(blade(5, 63, 9, 34, 17), 45)}</g>'
            + f'<g transform="translate(0 4) scale(.85) translate(9 0)">{rot(blade(5, 63, 9, 34, 17), -45)}</g>')


def heart(cx=50, cy=52, s=1, fill=CRIMSON):
    return f'<g transform="translate({cx} {cy}) scale({s}) translate(-50 -52)">' + P("M50 86 C14 62 12 30 32 22 C42 18 48 24 50 32 C52 24 58 18 68 22 C88 30 86 62 50 86 Z", fill) + "</g>"


def second_wind():
    return heart(46, 54, .8) + P("M10 30 Q40 22 60 30 Q76 36 86 26", sw=2.4, extra=f' stroke="{MUTED}"') + P("M18 84 Q48 76 70 82 Q84 86 92 76", sw=2.4, extra=f' stroke="{MUTED}"')


def wiry():
    return "".join(f'<ellipse cx="50" cy="{30 + 8 * k}" rx="{30 - k * 2}" ry="10" fill="none" stroke="{WOOD}" stroke-width="5"/>' for k in range(6)) + P("M80 30 Q92 20 86 8", sw=4, extra=f' stroke="{WOOD}"')


def night_eyes():
    return P("M60 8 A30 30 0 1 0 92 48 A24 24 0 1 1 60 8 Z", GOLD) + eye(44, 62, .62, "#6f9fb0")


def sellsword():
    return f'<g transform="translate(-14 -6) scale(.85)">{longsword()}</g>' + C(70, 74, 12, GOLD) + C(80, 62, 10, GOLD) + C(58, 84, 9, GOLD)


def acrobat():
    return P("M14 82 Q50 -6 86 82", sw=2, extra=' stroke-dasharray="4 4"') + C(20, 64, 9, CRIMSON) + C(50, 22, 9, GOLD) + C(80, 64, 9, ASPECT_GREEN)


def cauldron():
    return (P("M18 44 L82 44 Q86 84 50 88 Q14 84 18 44 Z", DARK) + R(14, 40, 72, 8, DARK, 3) + C(36, 30, 6, MOSS) + C(54, 22, 8, MOSS) + C(66, 34, 5, MOSS)
            + L(24, 88, 18, 96, 4) + L(76, 88, 82, 96, 4))


# ---------- spells ----------
def fire_bolt():
    trail = "".join(L(x, y, x + 30, y - 30, 3, c) for x, y, c in ((8, 80, GOLD), (16, 92, CRIMSON), (6, 64, CRIMSON)))
    return trail + C(64, 38, 22, CRIMSON) + P("M64 22 Q78 30 74 44 Q68 56 56 50 Q48 42 56 34 Q60 30 64 22 Z", GOLD, 1.6) + C(64, 42, 5, PARCH, 0)


def hand(fill=PARCH, extra=""):
    return P("M36 90 L34 52 Q32 42 38 42 Q42 42 42 50 L42 22 Q42 16 47 16 Q52 16 52 22 L52 46 L52 16 Q52 10 57 10 Q62 10 62 16 L62 46 L62 22 Q62 16 67 16 Q72 16 72 22 L72 62 Q72 82 62 90 Z", fill, extra=extra)


def mage_hand():
    return hand("#e4ecef", ' stroke-dasharray="5 3"') + "".join(C(x, y, 2.4, CRYSTAL, 0) for x, y in ((20, 20), (86, 30), (16, 60), (88, 72)))


def magic_missile():
    out = ""
    for k, y in enumerate((24, 50, 76)):
        out += P(f"M12 {y + 8} Q40 {y + 4} 70 {y}", sw=2, extra=f' stroke="{CRYSTAL}" stroke-dasharray="4 3"') + star(78, y, 10, 4, .35, GOLD)
    return out


def shield_spell():
    return hexa(50, 50, 42, "#dbe8ec") + hexa(50, 50, 30, "none") + star(50, 50, 12, 4, .35, CRYSTAL)


def grease():
    return P("M4 70 Q16 50 44 58 Q72 46 96 66 Q90 92 50 90 Q8 94 4 70 Z", "#6b5a2c") + C(36, 72, 3, "#c9b97a", 0) + C(64, 70, 4, "#c9b97a", 0) + P("M40 48 Q50 20 66 40", sw=2.4, extra=' stroke-dasharray="4 3"') + boots_small(70, 30)


def misty_step():
    def foot(x, y):
        return f'<ellipse cx="{x}" cy="{y}" rx="6" ry="10" fill="{DARK}"/>'
    return foot(20, 80) + foot(32, 66) + "".join(C(x, y, r, "#e4ecef") for x, y, r in ((52, 50, 12), (64, 42, 10), (60, 58, 9))) + foot(76, 28) + foot(88, 14)


def web():
    out = "".join(L(50, 50, 50 + 46 * math.cos(math.radians(a)), 50 + 46 * math.sin(math.radians(a)), 1.6) for a in range(0, 360, 45))
    for r in (12, 24, 36):
        pts = " ".join(f"{50 + r * math.cos(math.radians(a)):.1f},{50 + r * math.sin(math.radians(a)):.1f}" for a in range(0, 360, 45))
        out += f'<polygon points="{pts}" fill="none" stroke-width="1.6"/>'
    return out + C(64, 34, 5, INK) + L(64, 34, 64, 12, 1)


# ---------- Glamour, Divine, Nature ----------
def comedy_mask():
    return P("M16 22 Q50 10 84 22 Q86 70 50 86 Q14 70 16 22 Z", PARCH) + P("M28 40 Q36 32 44 40 M56 40 Q64 32 72 40", sw=3) + P("M32 58 Q50 76 68 58 Q50 66 32 58 Z", CRIMSON)


def horn():
    return P("M12 40 L22 40 Q60 36 88 14 L88 86 Q60 64 22 60 L12 60 Z", GOLD) + L(40, 38, 40, 62, 2) + L(60, 32, 60, 70, 2) + note(82, 92, .6)


def hold_the_line():
    return heater(24, 50, .42) + heater(50, 50, .42, GOLD) + heater(76, 50, .42) + P("M10 80 L90 80", sw=3)


def cutting_words():
    return (P("M10 16 L76 16 Q84 16 84 24 L84 54 Q84 62 76 62 L36 62 L22 76 L24 62 L18 62 Q10 62 10 54 Z", PARCH)
            + f'<g transform="translate(16 12) scale(.62)">{rot(blade(18, 56, 11, 26, 14), 70)}</g>')


def steady_now():
    return hand() + P("M14 44 Q8 50 14 56 M86 44 Q92 50 86 56", sw=2.4, extra=f' stroke="{GOLD}"')


def skull():
    return (P("M22 46 Q22 12 50 12 Q78 12 78 46 Q78 60 68 64 L68 80 L32 80 L32 64 Q22 60 22 46 Z", PARCH)
            + C(38, 44, 8, INK, 0) + C(62, 44, 8, INK, 0) + P("M50 54 L45 64 L55 64 Z", INK, 0) + L(42, 72, 42, 80, 2) + L(50, 72, 50, 80, 2) + L(58, 72, 58, 80, 2))


def sun(fill=GOLD):
    rays = "".join(L(50 + 26 * math.cos(math.radians(a)), 50 + 26 * math.sin(math.radians(a)), 50 + 42 * math.cos(math.radians(a)), 50 + 42 * math.sin(math.radians(a)), 3, GOLD) for a in range(0, 360, 30))
    return rays + C(50, 50, 20, fill)


def bane():
    return sun("#8a8270") + P("M10 74 Q16 58 32 62 Q38 46 56 52 Q72 44 80 60 Q94 62 90 76 Z", DARK)


def compass():
    return C(50, 50, 40, PARCH) + C(50, 50, 32, "none", 1.4) + P("M50 14 L58 50 L50 86 L42 50 Z", CRIMSON, 1.6) + P("M50 50 L58 50 L50 86 Z", PARCH, 1.6) + C(50, 50, 4, GOLD)


def twist_fate():
    return hexa(50, 52, 30, PARCH) + f'<text x="50" y="61" text-anchor="middle" font-size="24" fill="{CRIMSON}" stroke="none" style="font-family:Cinzel,serif;font-weight:700">20</text>' + P("M14 30 A42 42 0 0 1 86 30", sw=3) + P("M86 30 L76 26 M86 30 L84 20", sw=3)


def healing_word():
    return P("M10 14 L90 14 L90 62 L44 62 L28 80 L30 62 L10 62 Z", PARCH) + R(43, 22, 14, 34, CRIMSON, 2, 1.6) + R(33, 32, 34, 14, CRIMSON, 2, 1.6)


def cure_wounds():
    return hand() + heart(57, 54, .36)


def hawk():
    return (P("M50 30 Q30 12 6 22 Q24 30 30 40 Q14 44 10 58 Q32 50 44 52 L40 82 L50 74 L60 82 L56 52 Q68 50 90 58 Q86 44 70 40 Q76 30 94 22 Q70 12 50 30 Z", "#8a6a44")
            + C(50, 32, 7, "#8a6a44") + P("M50 36 L54 42 L50 40 Z", GOLD, 1))


def wolf():
    return (P("M24 12 L36 34 L64 34 L76 12 L80 44 Q78 58 64 66 L58 82 Q50 90 42 82 L36 66 Q22 58 20 44 Z", "#8e8a80")
            + C(40, 46, 3.6, GOLD) + C(60, 46, 3.6, GOLD) + P("M44 78 L50 84 L56 78 Z", INK, 0) + P("M30 24 L36 32 M70 24 L64 32", sw=1.6))


def bear():
    return (C(28, 24, 11, "#7a5a3c") + C(72, 24, 11, "#7a5a3c") + C(50, 54, 34, "#7a5a3c") + P("M36 62 Q50 50 64 62 Q64 82 50 84 Q36 82 36 62 Z", "#b08a62")
            + C(38, 46, 4, INK, 0) + C(62, 46, 4, INK, 0) + P("M44 64 L56 64 L50 72 Z", INK, 0))


def leaf(fill=MOSS):
    return P("M50 90 L50 54 M50 54 Q16 50 22 14 Q60 10 70 40 Q72 56 50 54 Z", fill) + P("M50 54 Q42 36 34 22", sw=1.6)


def mossbalm():
    return leaf() + P("M74 54 Q84 68 76 76 Q68 80 66 72 Q66 64 74 54 Z", "#9fc4d6", 1.8)


def remembrance():
    return leaf() + f'<g transform="translate(46 44) scale(.5)">{wolf()}</g>'


def pocket_sand():
    grains = "".join(C(60 + 6 * math.cos(a), 20 + 5 * math.sin(a * 1.7), 1.6, "#c9a86a", 0) + C(74 + 8 * math.sin(a), 14 + 6 * math.cos(a), 1.3, "#c9a86a", 0)
                     for a in range(6))
    return (P("M24 44 Q12 74 26 88 L62 88 Q76 74 64 44 Q44 38 24 44 Z", LEATHER) + P("M24 44 Q44 52 64 44", sw=2)
            + P("M58 40 Q66 30 72 22", sw=2.2, extra=f' stroke="#c9a86a"') + grains)


def pack_hunter():
    return (f'<g transform="translate(-6 18) scale(.62)">{wolf()}</g>' + f'<g transform="translate(44 18) scale(.62)">{wolf()}</g>'
            + f'<g transform="translate(19 -4) scale(.7)">{wolf()}</g>')


def slippery():
    return (boots_small(62, 52) + P("M14 40 L34 40 M8 54 L32 54 M16 68 L36 68", sw=2.2, extra=f' stroke="{GOLD}"')
            + P("M20 86 Q50 78 80 86", sw=2, extra=f' stroke="{MUTED}"'))


# ---------- foes: drawn for the left half of a foe card ----------
SKIN = "#d8b48a"


def eyes(y=50, dx=10, fill=INK, r=3):
    return C(50 - dx, y, r, fill, 0) + C(50 + dx, y, r, fill, 0)


def bandit():
    return (P("M16 60 Q14 14 50 12 Q86 14 84 60 Z", DARK) + C(50, 56, 26, SKIN) + R(22, 44, 56, 12, DARK, 5) + eyes(50, 11, PARCH, 3.4)
            + P("M24 62 Q50 92 76 62 L76 70 Q50 98 24 70 Z", CRIMSON))


def archer():
    return (longbow() + P("M50 10 L80 82 L20 82 Z", MOSS) + C(50, 58, 15, SKIN) + P("M35 50 Q50 40 65 50", sw=2) + eyes(58, 6, INK, 2.4))


def goblin():
    ear = "#7a9a4a"
    return (P("M30 46 L2 28 L28 60 Z", ear) + P("M70 46 L98 28 L72 60 Z", ear) + P("M28 40 Q28 18 50 18 Q72 18 72 40 Q76 78 50 84 Q24 78 28 40 Z", ear)
            + eyes(48, 10, GOLD, 4) + C(40, 48, 1.4, INK, 0) + C(60, 48, 1.4, INK, 0)
            + P("M36 64 Q50 74 64 64", sw=2) + P("M42 66 L44 71 L46 67 M54 67 L56 71 L58 66", sw=1.4, extra=f' fill="{PARCH}"'))


def cultist():
    return (P("M50 6 Q86 20 84 92 L16 92 Q14 20 50 6 Z", "#5a1e1e") + P("M50 22 Q70 30 68 62 Q50 72 32 62 Q30 30 50 22 Z", INK)
            + eyes(46, 8, GOLD, 2.6) + star(50, 82, 7, 5, .45, GOLD))


def legionary():
    return (R(32, 4, 36, 14, CRIMSON, 6) + P("M22 56 Q22 18 50 18 Q78 18 78 56 Z", STEEL) + P("M26 54 L30 84 L42 84 L40 54 Z", STEEL)
            + P("M74 54 L70 84 L58 84 L60 54 Z", STEEL) + R(40, 52, 20, 30, SKIN, 3) + eyes(62, 5, INK, 2.2) + P("M18 54 L82 54", sw=3.4)
            + C(50, 32, 3, GOLD, 1.4))


def bandit_captain():
    return (C(50, 62, 24, SKIN) + P("M10 46 Q50 22 90 46 Q50 36 10 46 Z", DARK) + P("M28 42 Q50 4 72 42 Z", DARK) + P("M28 42 Q50 34 72 42", sw=2, extra=f' stroke="{GOLD}"')
            + C(59, 60, 3, INK, 0) + C(41, 60, 5.5, INK, 0) + P("M30 52 L66 70", sw=1.4) + P("M40 74 Q50 80 60 74", sw=2))


def ogre_face(skin="#9a8f6a"):
    return (C(50, 56, 36, skin) + P("M26 44 Q38 36 46 44 M54 44 Q62 36 74 44", sw=3.2) + eyes(50, 12, INK, 3.2)
            + P("M30 72 Q50 82 70 72", sw=2.6) + P("M34 74 L32 60 L40 74 Z", PARCH, 1.6) + P("M66 74 L68 60 L60 74 Z", PARCH, 1.6))


def ogre():
    return ogre_face()


def ogre_chieftain():
    return (ogre_face("#8a7f58")
            + P("M30 26 L30 8 L40 18 L50 4 L60 18 L70 8 L70 26 Z", GOLD) + C(50, 20, 3, CRIMSON, 1.2))


FOE_ART = {
    "Bandit": bandit, "Archer": archer, "Goblin": goblin, "Wolf": wolf, "Cultist": cultist, "Legionary": legionary,
    "Bandit Captain": bandit_captain, "Ogre": ogre, "Ogre Chieftain": ogre_chieftain,
}


def foe_art(name):
    fn = FOE_ART.get(name)
    return svg(fn(), name) if fn else None


ART = {
    # Cores
    "Brute": lambda: core(sym_str), "Nimble": lambda: core(sym_dex), "Scholar": lambda: core(sym_int), "Envoy": lambda: core(sym_wil),
    "Balanced": balanced, "Ogre": lambda: core(sym_str, big=True) + R(6, 6, 10, 30, WOOD, 4), "Bandit Captain": bandit_core,
    # armor and Hands
    "Leather": leather, "Mail": mail, "Plate": plate, "Shield": round_shield,
    "Dagger": dagger, "Shortsword": shortsword, "Handaxe": handaxe, "Finesse Blade": rapier, "Longsword": longsword, "Battleaxe": battleaxe,
    "Greatsword": greatsword, "Glaive": glaive, "Longbow": longbow, "Sling": sling, "Javelins": javelins, "Spellguard Staff": staff,
    "Traveler's Lute": lute, "Boarspear": lambda: spear(lugs=True),
    "Greatclub": greatclub, "Gladius": gladius, "Pilum": pilum,
    # Jewelry and Items
    "Ring of Warding": ring_of_warding, "Guild Signet": guild_signet, "Shard Bandolier": bandolier, "Holy Amulet": amulet,
    "Boots of the Long Stride": boots, "Ring of Sparks": ring_of_sparks,
    "Potion of Healing": flask, "Greater Potion of Healing": lambda: flask(CRIMSON, big=True) + star(50, 62, 10, 5, .45, GOLD),
    "Coin Pouch": pouch, "Pocket Sand": pocket_sand, "Writ of Favor": scroll, "Alchemist's Fire Recipe": fire_flask,
    # Aspects
    "Springheel": springheel, "Stone Blood": stone_blood, "Iron Will": iron_will, "Clear Mind": clear_mind, "Cleave": cleave,
    "Steady Aim": steady_aim, "Shield Bash": shield_bash, "Battle Hymn": battle_hymn, "Rallying Cry": banner, "Shield Wall": shield_wall, "Pack Hunter": pack_hunter, "Slippery": slippery,
    "Cat Burglar": padlock, "Renowned": laurel, "Sailor": anchor, "Street Urchin": street_urchin, "Hunter": tracks,
    "Physician": mortar, "Barkeep": tankard, "Smith": smith, "Mountaineer": mountains, "Twin Strike": crossed_swords,
    "Second Wind": second_wind, "Wiry": wiry, "Night Eyes": night_eyes, "Sellsword": sellsword, "Acrobat": acrobat, "Hedge Witch": cauldron,
    # deck covers
    "Conjurer's Book": lambda: book(star(53, 50, 14, 5, .45, GOLD)), "Wanderer's Repertoire": lambda: lute(),
    "Acolyte's Litany": lambda: book(f'<g transform="translate(53 50) scale(.5) translate(-50 -50)">{sun()}</g>'),
    "Wildheart's Remembrance": remembrance,
}

DECK_ART = {
    "Fire Bolt": fire_bolt, "Mage Hand": mage_hand, "Magic Missile": magic_missile, "Shield": shield_spell, "Grease": grease,
    "Misty Step": misty_step, "Web": web,
    "Jeer": comedy_mask, "Rally": horn, "Hold the Line": hold_the_line, "Cutting Words": cutting_words, "Steady Now": steady_now, "Dread": skull,
    "Guidance": compass, "Bless": sun, "Bane": bane, "Twist Fate": twist_fate, "Healing Word": healing_word, "Cure Wounds": cure_wounds,
    "Hawk": hawk, "Wolf": wolf, "Mossbalm": mossbalm, "Bear": bear,
}


def art(name, deck=False):
    fn = (DECK_ART if deck else ART).get(name)
    return svg(fn(), name) if fn else None
