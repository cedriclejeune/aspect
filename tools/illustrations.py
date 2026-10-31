"""Inline SVG illustrations for the PDF rulebook.

Style: ink line art on parchment, crimson for the Calling, gold for Aspects. Cards are drawn in the printed base set's
black-and-white Ledger look (ledger_card), with the ink stat symbols from rules/symbols/ink/.
Each public function returns an <svg> string sized by its viewBox (CSS sets width).
"""
import math
from pathlib import Path

INK = "#2b1d12"
CRIMSON = "#8a1c1c"
GOLD = "#b07d2b"
PARCH = "#f6efdd"
SHADE = "#e6d8b5"
MUTED = "#7a6648"

HEAD = "font-family:Cinzel,serif;font-weight:700"
BODY = "font-family:'EB Garamond',Georgia,serif"


def _svg(w, h, body, label):
    return (
        f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" role="img" '
        f'aria-label="{label}"><defs>'
        f'<marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M0 0L10 5L0 10z" fill="{INK}"/></marker>'
        f'<marker id="arrc" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M0 0L10 5L0 10z" fill="{CRIMSON}"/></marker>'
        f"</defs>{body}</svg>"
    )


LANG = "en"  # set_lang("fr") translates every figure's text through tools/i18n_fr.py
_TR, _TR_UP = {}, {}


def set_lang(lang):
    """Draw the figures in English ("en") or French ("fr")."""
    global LANG, _TR, _TR_UP
    LANG = lang
    if lang == "fr":
        import i18n_fr
        _TR = i18n_fr.ILLUSTRATIONS
        _TR_UP = {k.upper(): v.upper() for k, v in _TR.items()}
        for d in (BRAM_CALLING, BRAM_TOTALS):
            d[9] = i18n_fr.feet(d[9])
    else:
        _TR, _TR_UP = {}, {}


def tr(s):
    """A figure's text in the current language (unchanged if it has no translation)."""
    if not _TR or not isinstance(s, str):
        return s
    return _TR.get(s) or _TR_UP.get(s) or s


def _text(x, y, s, size=14, style=BODY, fill=INK, anchor="middle", weight=None, italic=False):
    s = tr(s)
    extra = f";font-weight:{weight}" if weight else ""
    extra += ";font-style:italic" if italic else ""
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" style="{style}{extra}" font-size="{size}" fill="{fill}">{s}</text>'


def _hex(cx, cy, r, fill="none", stroke=INK, sw=2, dash=None, rot=0):
    pts = " ".join(
        f"{cx + r * math.cos(math.radians(60 * i + rot)):.1f},{cy + r * math.sin(math.radians(60 * i + rot)):.1f}"
        for i in range(6)
    )
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>'


def gem(cx, cy, r, color=CRIMSON, label=None, label_size=None):
    """Faceted hexagonal gem."""
    out = [_hex(cx, cy, r, fill=color, stroke=INK, sw=2.2, rot=30)]
    inner = r * 0.55
    out.append(_hex(cx, cy, inner, fill="none", stroke=PARCH, sw=1.2, rot=30))
    for i in range(6):
        a = math.radians(60 * i + 30)
        out.append(
            f'<line x1="{cx + inner * math.cos(a):.1f}" y1="{cy + inner * math.sin(a):.1f}" '
            f'x2="{cx + r * math.cos(a):.1f}" y2="{cy + r * math.sin(a):.1f}" stroke="{PARCH}" stroke-width="1" opacity=".7"/>'
        )
    out.append(f'<polygon points="{cx - inner * .5:.1f},{cy - inner * .7:.1f} {cx + inner * .2:.1f},{cy - inner * .85:.1f} {cx - inner * .1:.1f},{cy - inner * .2:.1f}" fill="#fff" opacity=".35"/>')
    if label:
        out.append(_text(cx, cy + (label_size or r * .5) * .35, label, label_size or r * .5, HEAD, PARCH))
    return "".join(out)


# ---------- icons (centered at cx, cy, about s px tall) ----------
def icon_sword(cx, cy, s):
    h = s / 2
    return (
        f'<g stroke="{INK}" stroke-width="2.2" fill="none" stroke-linecap="round">'
        f'<path d="M{cx} {cy - h}L{cx + h * .12} {cy + h * .35}L{cx - h * .12} {cy + h * .35}Z" fill="{SHADE}"/>'
        f'<line x1="{cx - h * .4}" y1="{cy + h * .35}" x2="{cx + h * .4}" y2="{cy + h * .35}"/>'
        f'<line x1="{cx}" y1="{cy + h * .35}" x2="{cx}" y2="{cy + h * .8}"/>'
        f'<circle cx="{cx}" cy="{cy + h * .9}" r="{h * .1}" fill="{GOLD}"/></g>'
    )


def icon_shield(cx, cy, s, bands=0):
    h = s / 2
    w = h * .8
    out = (
        f'<path d="M{cx - w} {cy - h * .8}Q{cx} {cy - h * 1.05} {cx + w} {cy - h * .8}'
        f'L{cx + w} {cy - h * .1}Q{cx + w * .9} {cy + h * .6} {cx} {cy + h}Q{cx - w * .9} {cy + h * .6} {cx - w} {cy - h * .1}Z" '
        f'fill="{SHADE}" stroke="{INK}" stroke-width="2.2"/>'
    )
    for i in range(bands):
        y = cy - h * .45 + i * h * .45
        out += f'<line x1="{cx - w * .85}" y1="{y}" x2="{cx + w * .85}" y2="{y}" stroke="{INK}" stroke-width="1.6"/>'
    if bands == 0:
        out += f'<line x1="{cx}" y1="{cy - h * .85}" x2="{cx}" y2="{cy + h * .9}" stroke="{INK}" stroke-width="1.4"/>'
    return out


def icon_book(cx, cy, s):
    h = s / 2
    w = h * .8
    return (
        f'<g stroke="{INK}" stroke-width="2" fill="{SHADE}">'
        f'<rect x="{cx - w}" y="{cy - h}" width="{2 * w}" height="{2 * h}" rx="3"/>'
        f'<line x1="{cx - w * .65}" y1="{cy - h}" x2="{cx - w * .65}" y2="{cy + h}"/>'
        f'<circle cx="{cx + w * .15}" cy="{cy - h * .1}" r="{h * .35}" fill="none" stroke="{CRIMSON}"/>'
        f'<path d="M{cx + w * .15} {cy - h * .45}L{cx + w * .15} {cy + h * .25}M{cx - w * .2} {cy - h * .1}L{cx + w * .5} {cy - h * .1}" stroke="{CRIMSON}" stroke-width="1.4"/>'
        f"</g>"
    )


def icon_bow(cx, cy, s):
    h = s / 2
    return (
        f'<g stroke="{INK}" stroke-width="2.2" fill="none" stroke-linecap="round">'
        f'<path d="M{cx - h * .2} {cy - h}Q{cx + h * .9} {cy} {cx - h * .2} {cy + h}"/>'
        f'<line x1="{cx - h * .2}" y1="{cy - h}" x2="{cx - h * .2}" y2="{cy + h}" stroke-width="1.2"/>'
        f'<line x1="{cx - h * .7}" y1="{cy}" x2="{cx + h * .7}" y2="{cy}" stroke-width="1.6" marker-end="url(#arr)"/></g>'
    )


def icon_mask(cx, cy, s):
    h = s / 2
    return (
        f'<g stroke="{INK}" stroke-width="2" fill="{SHADE}">'
        f'<path d="M{cx - h} {cy - h * .4}Q{cx} {cy - h * .9} {cx + h} {cy - h * .4}Q{cx + h * .9} {cy + h * .5} {cx} {cy + h * .3}Q{cx - h * .9} {cy + h * .5} {cx - h} {cy - h * .4}Z"/>'
        f'<ellipse cx="{cx - h * .4}" cy="{cy - h * .15}" rx="{h * .22}" ry="{h * .13}" fill="{INK}"/>'
        f'<ellipse cx="{cx + h * .4}" cy="{cy - h * .15}" rx="{h * .22}" ry="{h * .13}" fill="{INK}"/></g>'
    )


def icon_jump(cx, cy, s):
    h = s / 2
    return (
        f'<g stroke="{INK}" stroke-width="2.4" fill="none" stroke-linecap="round" stroke-linejoin="round">'
        f'<path d="M{cx - h} {cy + h * .7}Q{cx} {cy - h * 1.4} {cx + h} {cy + h * .7}" stroke-dasharray="4 4" marker-end="url(#arr)"/>'
        f'<line x1="{cx - h * 1.1}" y1="{cy + h * .95}" x2="{cx + h * 1.1}" y2="{cy + h * .95}" stroke-width="1.6"/></g>'
    )


def icon_compass(cx, cy, s):
    r = s / 2
    return (
        f'<g stroke="{INK}" stroke-width="2.2"><circle cx="{cx}" cy="{cy}" r="{r}" fill="{SHADE}"/>'
        f'<path d="M{cx} {cy - r * .8}L{cx + r * .22} {cy}L{cx} {cy + r * .8}L{cx - r * .22} {cy}Z" fill="{CRIMSON}" stroke-width="1.4"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{r * .1}" fill="{INK}"/></g>'
    )


def icon_swords(cx, cy, s):
    h = s / 2
    out = '<g stroke="{0}" stroke-width="2.4" stroke-linecap="round">'.format(INK)
    for sgn in (1, -1):
        out += (
            f'<line x1="{cx - sgn * h}" y1="{cy - h}" x2="{cx + sgn * h * .55}" y2="{cy + h * .55}"/>'
            f'<line x1="{cx + sgn * h * .3}" y1="{cy + h * .8}" x2="{cx + sgn * h * .8}" y2="{cy + h * .3}"/>'
            f'<line x1="{cx + sgn * h * .65}" y1="{cy + h * .65}" x2="{cx + sgn * h}" y2="{cy + h}"/>'
        )
    return out + "</g>"


def icon_die(cx, cy, s):
    """A d20: any trial, not only a fight."""
    return _hex(cx, cy, s / 2, fill=PARCH, stroke=INK, sw=2.2) + _text(cx, cy + s * .15, "20", s * .42, HEAD, CRIMSON)


def icon_chest(cx, cy, s):
    h = s / 2
    w = h * 1.2
    return (
        f'<g stroke="{INK}" stroke-width="2.2">'
        f'<rect x="{cx - w}" y="{cy - h * .15}" width="{2 * w}" height="{h * 1.05}" fill="{SHADE}"/>'
        f'<path d="M{cx - w} {cy - h * .15}Q{cx - w} {cy - h} {cx} {cy - h}Q{cx + w} {cy - h} {cx + w} {cy - h * .15}Z" fill="{GOLD}"/>'
        f'<rect x="{cx - h * .18}" y="{cy - h * .3}" width="{h * .36}" height="{h * .4}" fill="{INK}"/></g>'
    )


def icon_fire(cx, cy, s):
    h = s / 2
    return (
        f'<g stroke="{INK}" stroke-width="2">'
        f'<path d="M{cx} {cy - h}Q{cx + h * .7} {cy - h * .1} {cx + h * .45} {cy + h * .45}Q{cx} {cy + h * .7} {cx - h * .45} {cy + h * .45}Q{cx - h * .7} {cy - h * .1} {cx} {cy - h}Z" fill="{CRIMSON}"/>'
        f'<path d="M{cx} {cy - h * .3}Q{cx + h * .3} {cy + h * .1} {cx} {cy + h * .45}Q{cx - h * .3} {cy + h * .1} {cx} {cy - h * .3}Z" fill="{GOLD}" stroke-width="1"/>'
        f'<line x1="{cx - h * .9}" y1="{cy + h * .95}" x2="{cx + h * .9}" y2="{cy + h * .6}" stroke-width="3"/>'
        f'<line x1="{cx + h * .9}" y1="{cy + h * .95}" x2="{cx - h * .9}" y2="{cy + h * .6}" stroke-width="3"/></g>'
    )


def card(x, y, w, h, title, rank, tag, color=GOLD):
    return (
        f'<g><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{PARCH}" stroke="{INK}" stroke-width="2"/>'
        f'<rect x="{x}" y="{y}" width="{w}" height="{h * .22}" rx="6" fill="{color}" stroke="{INK}" stroke-width="2"/>'
        + _text(x + w / 2, y + h * .15, title, h * .1, HEAD, PARCH)
        + _text(x + w / 2, y + h * .9, f"{rank} · {tag}", h * .09, BODY, MUTED, italic=True)
        + "</g>"
    )


# ---------- figures ----------
def cover_emblem():
    cx, cy, R = 200, 200, 128
    icons = [icon_sword, icon_book, icon_shield, icon_jump, None]
    body = [f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{GOLD}" stroke-width="2"/>',
            f'<circle cx="{cx}" cy="{cy}" r="{R + 14}" fill="none" stroke="{INK}" stroke-width="1" stroke-dasharray="2 6"/>']
    for i, ic in enumerate(icons):
        a = math.radians(-90 + 72 * i)
        x, y = cx + R * math.cos(a), cy + R * math.sin(a)
        body.append(f'<line x1="{cx + 52 * math.cos(a):.1f}" y1="{cy + 52 * math.sin(a):.1f}" x2="{cx + (R - 40) * math.cos(a):.1f}" y2="{cy + (R - 40) * math.sin(a):.1f}" stroke="{GOLD}" stroke-width="2"/>')
        if ic:
            body.append(_hex(x, y, 38, fill=PARCH, stroke=INK, sw=2.2))
            body.append(ic(x, y, 36))
        else:
            body.append(_hex(x, y, 38, fill="none", stroke=INK, sw=2, dash="6 5"))
            body.append(_text(x, y + 9, "+", 28, HEAD, MUTED))
    body.append(gem(cx, cy, 56, CRIMSON))
    return _svg(400, 400, "".join(body), "A Calling gem surrounded by five Slots holding cards")


def play_loop():
    ox, oy, ax, ay = 350, 200, 120, 130  # oval: Trial on top, Gather below, Rest & Rebuild on the left
    pt = lambda a: (ox + ax * math.cos(math.radians(a)), oy + ay * math.sin(math.radians(a)))

    def leave(a, step):  # angle where the oval exits a node's circle (r 34) plus a gap
        b = a
        while math.dist(pt(a), pt(b)) < 42:
            b += step
        return b

    def arc(a1, a2, extra=""):
        (x1, y1), (x2, y2) = pt(leave(a1, 1)), pt(leave(a2, -1))
        return f'<path d="M{x1:.1f} {y1:.1f} A{ax} {ay} 0 0 1 {x2:.1f} {y2:.1f}" fill="none" stroke="{INK}" stroke-width="2"{extra} marker-end="url(#arr)"/>'

    dotted = ' stroke-dasharray="6 5"'
    (cx, cy), (gx, gy), (rx, ry) = pt(-90), pt(90), pt(180)
    body = [
        arc(-90, 90),  # Trial → Gather
        arc(90, 180, dotted), arc(180, 270, dotted),  # the side path through Rest & Rebuild
        # Gather → Trial: chain trials without resting.
        f'<line x1="{gx:.1f}" y1="{gy - 42:.1f}" x2="{cx:.1f}" y2="{cy + 44:.1f}" stroke="{INK}" stroke-width="2" marker-end="url(#arr)"/>',
    ]
    for (x, y), name, ic, (dx, dy, anchor) in [
        ((cx, cy), "Trial", icon_die, (0, -44, "middle")),
        ((gx, gy), "Gather", icon_chest, (0, 56, "middle")),
        ((rx, ry), "Rest &amp; Rebuild", icon_fire, (-48, 6, "end")),
    ]:
        body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="34" fill="{PARCH}" stroke="{INK}" stroke-width="2.2"/>')
        body.append(ic(x, y, 34))
        body.append(_text(x + dx, y + dy, name, 17, HEAD, INK, anchor=anchor))
    return _svg(700, 400, "".join(body), "The play loop: face a trial and gather, again and again; rest and rebuild when needed")


def icon_ring(cx, cy, s):
    r = s / 2
    return (
        f'<g stroke="{INK}" stroke-width="2.2"><circle cx="{cx}" cy="{cy + r * .2}" r="{r * .65}" fill="none" stroke-width="3"/>'
        f'<path d="M{cx} {cy - r}L{cx + r * .3} {cy - r * .55}L{cx} {cy - r * .3}L{cx - r * .3} {cy - r * .55}Z" fill="{CRIMSON}" stroke-width="1.4"/></g>'
    )


def icon_potion(cx, cy, s):
    h = s / 2
    return (
        f'<path d="M{cx - h * .2} {cy - h}h{h * .4}v{h * .45}q{h * .6} {h * .3} {h * .6} {h * .85}v{h * .5}q0 {h * .2} -{h * .2} {h * .2}'
        f'h-{h * .8}q-{h * .2} 0 -{h * .2} -{h * .2}v-{h * .5}q0 -{h * .55} {h * .6} -{h * .85}z" fill="{CRIMSON}" stroke="{INK}" stroke-width="2"/>'
    )


# ---------- stat symbols: four abilities, their Defenses (same symbol in a shield), HP, Speed ----------
def sym_str(cx, cy, s):
    """Clenched fist."""
    h = s / 2
    out = [f'<g stroke="{INK}" stroke-width="{s * .045:.2f}" stroke-linejoin="round">',
           f'<rect x="{cx - h * .45}" y="{cy + h * .45}" width="{h * .9}" height="{h * .55}" fill="{SHADE}"/>',
           f'<rect x="{cx - h * .8}" y="{cy - h * .4}" width="{h * 1.6}" height="{h * .95}" rx="{h * .25}" fill="{SHADE}"/>']
    for i in range(4):
        out.append(f'<rect x="{cx - h * .8 + i * h * .4:.2f}" y="{cy - h * .85}" width="{h * .4:.2f}" height="{h * .75}" rx="{h * .2:.2f}" fill="{SHADE}"/>')
    out.append(f'<rect x="{cx - h * .95}" y="{cy - h * .1}" width="{h * 1.15}" height="{h * .34}" rx="{h * .17}" fill="{PARCH}"/></g>')
    return "".join(out)


def sym_dex(cx, cy, s):
    """Feather."""
    h = s / 2
    return (
        f'<g transform="rotate(35 {cx} {cy})" stroke="{INK}" stroke-width="{s * .045:.2f}" stroke-linecap="round">'
        f'<path d="M{cx} {cy - h}C{cx + h * .6} {cy - h * .55} {cx + h * .5} {cy + h * .3} {cx} {cy + h * .6}'
        f'C{cx - h * .5} {cy + h * .3} {cx - h * .6} {cy - h * .55} {cx} {cy - h}Z" fill="{SHADE}"/>'
        f'<path d="M{cx + h * .42} {cy - h * .3}L{cx + h * .2} {cy - h * .25}M{cx - h * .45} {cy + h * .05}L{cx - h * .2} {cy + h * .05}" fill="none"/>'
        f'<line x1="{cx}" y1="{cy - h * .75}" x2="{cx}" y2="{cy + h * 1.05}"/></g>'
    )


def sym_int(cx, cy, s):
    """Open eye."""
    h = s / 2
    return (
        f'<g stroke="{INK}" stroke-width="{s * .045:.2f}">'
        f'<path d="M{cx - h} {cy}Q{cx} {cy - h * .95} {cx + h} {cy}Q{cx} {cy + h * .95} {cx - h} {cy}Z" fill="{PARCH}"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{h * .4}" fill="{GOLD}"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{h * .17}" fill="{INK}" stroke="none"/>'
        f'<circle cx="{cx + h * .12}" cy="{cy - h * .14}" r="{h * .07}" fill="{PARCH}" stroke="none"/></g>'
    )


def sym_wil(cx, cy, s):
    """Radiant star: presence."""
    h = s / 2
    pts = " ".join(
        f"{cx + (h if i % 2 == 0 else h * .42) * math.sin(math.radians(22.5 * i)):.2f},"
        f"{cy - (h if i % 2 == 0 else h * .42) * math.cos(math.radians(22.5 * i)):.2f}"
        for i in range(16)
    )
    return (f'<polygon points="{pts}" fill="{GOLD}" stroke="{INK}" stroke-width="{s * .045:.2f}" stroke-linejoin="round"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{h * .2}" fill="{PARCH}" stroke="{INK}" stroke-width="{s * .035:.2f}"/>')


def sym_hp(cx, cy, s):
    """Heart."""
    h = s / 2
    return (
        f'<path d="M{cx} {cy + h * .85}C{cx - h * 1.35} {cy - h * .05} {cx - h * .65} {cy - h * 1.1} {cx} {cy - h * .4}'
        f'C{cx + h * .65} {cy - h * 1.1} {cx + h * 1.35} {cy - h * .05} {cx} {cy + h * .85}Z" '
        f'fill="{CRIMSON}" stroke="{INK}" stroke-width="{s * .045:.2f}" stroke-linejoin="round"/>'
        f'<path d="M{cx - h * .55} {cy - h * .35}Q{cx - h * .5} {cy - h * .6} {cx - h * .25} {cy - h * .6}" fill="none" stroke="{PARCH}" stroke-width="{s * .04:.2f}" stroke-linecap="round" opacity=".7"/>'
    )


def sym_speed(cx, cy, s):
    """Boot with motion lines."""
    h = s / 2
    bx = cx + h * .2
    return (
        f'<g stroke="{INK}" stroke-width="{s * .045:.2f}" stroke-linecap="round" stroke-linejoin="round">'
        f'<path d="M{bx - h * .35} {cy - h * .9}L{bx + h * .15} {cy - h * .9}L{bx + h * .15} {cy + h * .1}'
        f'Q{bx + h * .8} {cy + h * .2} {bx + h * .8} {cy + h * .55}L{bx + h * .8} {cy + h * .75}L{bx - h * .4} {cy + h * .75}Z" fill="{SHADE}"/>'
        f'<line x1="{bx - h * .42}" y1="{cy - h * .6}" x2="{bx + h * .22}" y2="{cy - h * .6}"/>'
        f'<path d="M{cx - h * .55} {cy - h * .5}H{cx - h * 1.05}M{cx - h * .5} {cy}H{cx - h * .9}M{cx - h * .55} {cy + h * .5}H{cx - h * 1.05}" fill="none"/></g>'
    )


def defense(sym):
    """A Defense symbol: the ability's symbol inside a shield."""
    def draw(cx, cy, s):
        h = s / 2
        w = h * .85
        return (
            f'<path d="M{cx - w} {cy - h * .85}Q{cx} {cy - h * 1.05} {cx + w} {cy - h * .85}'
            f'L{cx + w} {cy - h * .1}Q{cx + w * .9} {cy + h * .6} {cx} {cy + h}Q{cx - w * .9} {cy + h * .6} {cx - w} {cy - h * .1}Z" '
            f'fill="{PARCH}" stroke="{INK}" stroke-width="{s * .05:.2f}"/>' + sym(cx, cy - h * .1, s * .62)
        )
    return draw


STAT_SYMBOLS = {"STR": sym_str, "DEX": sym_dex, "INT": sym_int, "WIL": sym_wil, "HP": sym_hp, "SPD": sym_speed}


def stat_symbol(key, shield=False):
    """One stat symbol as a small standalone SVG, for tables. shield=True draws the Defense."""
    sym = defense(STAT_SYMBOLS[key]) if shield else STAT_SYMBOLS[key]
    label = f"{key} Defense" if shield else key
    return _svg(40, 40, sym(20, 20, 36 if shield else 32), label)


def character_anatomy():
    body = [gem(95, 200, 58, CRIMSON, "DUELIST", 13),
            _text(95, 290, "Calling: STR · DEX", 13, BODY, MUTED, italic=True),
            _text(95, 308, "HP · Speed · perk", 13, BODY, MUTED, italic=True)]
    groups = [  # (title, x0, y, [(name, icon or None)])
        ("Armor", 230, 85, [("Leather", icon_shield)]),
        ("Hands", 370, 85, [("Finesse Blade", icon_sword), ("Dagger", icon_sword)]),
        ("Jewelry", 230, 215, [("Ring of Warding", icon_ring)]),
        ("Items", 370, 215, [("Potion ×1", icon_potion), ("empty", None)]),
        ("Aspects", 230, 345, [("Cat Burglar", icon_mask), ("Springheel", icon_jump), ("Iron Will", icon_fire)]),
    ]
    for title, x0, y, slots in groups:
        body.append(_text(x0 - 34, y - 42, title.upper(), 13, HEAD, GOLD, anchor="start"))
        for i, (name, ic) in enumerate(slots):
            x = x0 + i * 110
            if ic:
                body.append(_hex(x, y, 30, fill=PARCH, stroke=INK, sw=2.2))
                body.append(ic(x, y, 28))
            else:
                body.append(_hex(x, y, 30, fill="none", stroke=INK, sw=2, dash="6 5"))
            body.append(_text(x, y + 47, name, 12, HEAD, MUTED if not ic else INK))
    body.append(f'<line x1="160" y1="40" x2="160" y2="370" stroke="{GOLD}" stroke-width="1.5"/>')
    # stash
    sx = 575
    body.append(_text(sx + 50, 175, "Stash", 18, HEAD))
    for k in range(4):
        body.append(f'<rect x="{sx + 8 + k * 9}" y="{195 + k * 9}" width="70" height="90" rx="6" fill="{PARCH}" stroke="{INK}" stroke-width="1.8"/>')
    body.append(f'<rect x="{sx + 35}" y="{222}" width="70" height="22" rx="6" fill="{GOLD}" stroke="{INK}" stroke-width="1.8"/>')
    body.append(_text(sx + 50, 335, "unequipped cards", 12, BODY, MUTED, italic=True))
    body.append(_text(sx + 50, 352, "swap at rests", 12, BODY, CRIMSON, italic=True))
    return _svg(700, 400, "".join(body), "A character: Calling, Armor, two Hands, Jewelry, two Items, three Aspects and a Stash")


def _callout(px, py, lx, ly, label, sub=None, side=1):
    """Dotted leader from a point on a card to a label beside it (side 1 = right, -1 = left)."""
    ex = lx + 16 * side
    out = [f'<polyline points="{px:.1f},{py:.1f} {lx:.1f},{ly:.1f} {ex:.1f},{ly:.1f}" fill="none" stroke="{INK}" stroke-width="1" stroke-dasharray="3 3"/>',
           f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3" fill="{CRIMSON}"/>']
    anchor = "start" if side > 0 else "end"
    tx = ex + 6 * side
    if label:
        out.append(_text(tx, ly + 5, label, 16, HEAD, INK, anchor=anchor))
        if sub:
            out.append(_text(tx, ly + 22, sub, 13, BODY, MUTED, anchor=anchor, italic=True))
    else:
        out.append(_text(tx, ly + 5, sub, 13, BODY, MUTED, anchor=anchor, italic=True))
    return "".join(out)


# ---------- Ledger cards (P 3.1): the printed base set's black-and-white look, laid out in mm of a 63 × 88 mm card ----------
INK_SYMBOLS = Path(__file__).resolve().parent.parent / "rules" / "symbols" / "ink"
LEDGER_ROWS = ["str", "dex", "int", "wil", "str-def", "dex-def", "int-def", "wil-def", "hp", "spd"]
LEDGER_TYPES = {"Trait": "trait", "Technique": "technique", "Knack": "knack"}  # Aspect types with a symbol
ALL4 = ["STR", "DEX", "INT", "WIL"]
PT = .3528  # mm per point


def ink_symbol(name, cx, cy, s, op=1):
    """An ink stat symbol (rules/symbols/ink/<name>.png), s px square, centered at (cx, cy)."""
    fade = f' opacity="{op}"' if op < 1 else ""
    return (f'<image href="{(INK_SYMBOLS / f"{name}.png").as_uri()}" x="{cx - s / 2:.2f}" y="{cy - s / 2:.2f}" '
            f'width="{s:.2f}" height="{s:.2f}"{fade}/>')


def _bw(svg):
    """A parchment icon in black and white."""
    for c, bw in ((INK, "#000"), (SHADE, "#fff"), (PARCH, "#fff"), (GOLD, "#000"), (CRIMSON, "#000"), (MUTED, "#555")):
        svg = svg.replace(c, bw)
    return svg


def sym4(x, y, size, lit):
    """The four ability symbols in a 2 × 2 grid, top left at (x, y), size px apart; those not in lit faded (P 3.1)."""
    return "".join(ink_symbol(key.lower(), x + (k % 2 + .5) * size, y + (k // 2 + .5) * size, size * .92, 1 if key in lit else .18)
                   for k, key in enumerate(ALL4))


def _line(x1, y1, x2, y2, sw, col="#000"):
    return f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{col}" stroke-width="{sw:.2f}"/>'


def ledger_card(x, y, w, h, name, vals=None, kw="", rank=None, lit=None, own=None, art=None, text=(), tid="", size=9.4):
    """A card in the Ledger look, w × h px at (x, y): name, symbols (lit) and Rank in the title band (no Rank: symbols
    flush right), the bonus strip (vals: {row: "+3"}; own: all ten values, a Calling's), an art icon over effect lines
    (**bold**; size in pt on the printed card), the keyword line (kw=None: none) with an Aspect's type symbol, the ID."""
    u = w / 63  # px per mm
    th, kh, sw = h * .13, h * .1, w * .2
    sx, row, my = x + w - sw, (h - th - kh) / 10, y + (th - .7 * u) / 2
    vals = own or vals or {}
    name, kw = tr(name), tr(kw)
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h:.2f}" rx="{3 * u:.2f}" fill="#fff" stroke="#000" stroke-width="{.35 * u:.2f}"/>',
           _line(x, y + th - .35 * u, x + w, y + th - .35 * u, .7 * u)]
    pt = 9.2 if len(name) <= 14 else 8 if len(name) <= 18 else 7
    if lit:
        pt = min(pt, 8.4 if len(name) <= 12 else 7.4 if len(name) <= 16 else 6.6)
    fs = pt * PT * u
    out.append(_text(f"{x + 2.4 * u:.2f}", f"{my + fs * .36:.2f}", name.upper(), round(fs, 2), HEAD + ";letter-spacing:.04em", "#000", anchor="start"))
    if lit:
        out.append(sym4(x + w - (10 if rank else 2) * u - 7.6 * u, my - 3.8 * u, 3.8 * u, lit))
    if rank:
        rs = 8 * PT * u
        out += [f'<circle cx="{x + w - 5.4 * u:.2f}" cy="{my:.2f}" r="{3.63 * u:.2f}" fill="#fff" stroke="#000" stroke-width="{.35 * u:.2f}"/>',
                _text(f"{x + w - 5.4 * u:.2f}", f"{my + rs * .36:.2f}", rank, round(rs, 2), HEAD, "#000")]
    # bonus strip: heavier rules before the Defenses and before HP, unused rows faded
    out.append(_line(sx, y + th, sx, y + h - kh, .3 * u))
    s, vs = min(4.8 * u, row * .72), 7.4 * PT * u
    for i, key in enumerate(LEDGER_ROWS):
        ry = y + th + row * i
        if i:
            out.append(_line(sx, ry, x + w, ry, .3 * u) if i in (4, 8) else _line(sx, ry, x + w, ry, .12 * u, "#b5b5b5"))
        out.append(ink_symbol(key, sx + .7 * u + s / 2, ry + row / 2, s, 1 if i in vals or own else .28))
        if i in vals:
            out.append(_text(f"{x + w - .7 * u:.2f}", f"{ry + row / 2 + vs * .36:.2f}", vals[i], round(vs, 2), HEAD, "#000", anchor="end"))
    # effect: the art icon over the text, centered in the body
    fs, cx = size * PT * u, (x + sx) / 2
    ah = min((sx - x) * .45, (h - th - kh) * .4) if art else 0
    gap = 3 * u if art and text else 0
    top = y + th + (h - th - kh - ah - gap - len(text) * fs * 1.2) / 2
    if art:
        out.append(_bw(art(cx, top + ah / 2, ah)))
    for k, line in enumerate(text):
        out.append(_text(f"{cx:.2f}", f"{top + ah + gap + fs * (1.2 * k + .9):.2f}", _md_tspans(line), round(fs, 2), BODY, "#000"))
    if kw is not None:
        out.append(_line(x, y + h - kh, x + w, y + h - kh, .3 * u))
        tx, ks = x + 2.4 * u, 7.6 * PT * u
        sym = LEDGER_TYPES.get(kw.split(" · ")[0])
        if sym:
            out.append(ink_symbol(sym, tx + 2.2 * u, y + h - kh / 2, 4.4 * u))
            tx += 5.8 * u
        out.append(_text(f"{tx:.2f}", f"{y + h - kh / 2 + ks * .32:.2f}", kw, round(ks, 2), BODY, "#000", anchor="start", italic=True))
    else:  # no keyword line (the tally card): close the strip
        out.append(_line(sx, y + h - kh, x + w, y + h - kh, .3 * u))
    if tid:
        out.append(_text(f"{x + w - 2 * u:.2f}", f"{y + h - 3.7 * u:.2f}", tid, round(4.6 * PT * u, 2), "font-family:Cinzel,serif;letter-spacing:.05em", "#777", anchor="end"))
    return "".join(out)


def calling_card():
    """A Calling card: its own ten values in the strip, its two ability symbols lit, and its perk."""
    x, y, w = 150, 20, 300
    h, u = w * 88 / 63, w / 63
    th, kh = h * .13, h * .1
    top, row, my = y + th, (h - th - kh) / 10, y + (th - .7 * u) / 2
    own = dict(enumerate(["+2", "+2", "+0", "+0", "12", "12", "10", "10", "12", "10,5" if LANG == "fr" else "35"]))
    body = [ledger_card(x, y, w, h, "Duelist", kw="Calling", lit=["STR", "DEX"], own=own,
                        text=["**Footwork:** after a", "melee hit, move 5 ft"], tid="STARTER · L-01")]
    # brackets beside the card group the own values: modifiers, Defenses, HP and Speed
    bx = x + w + 12
    for r0, r1 in ((0, 4), (4, 8), (8, 10)):
        y0, y1 = top + row * r0 + 4, top + row * r1 - 4
        body.append(f'<path d="M{bx - 5} {y0:.1f}H{bx}V{y1:.1f}H{bx - 5}" fill="none" stroke="{INK}" stroke-width="1.2"/>')
    R = x + w + 40
    mid = y + (th + h - kh) / 2
    body += [_callout(x + w - 1.5 * u, my, R, y + 30, "Symbols", "its two abilities"),
             _callout(bx, top + row * 2, R, top + row * 2, "Own values", "+2 in its two abilities"),
             _callout(bx, top + row * 6, R, top + row * 6, "", "four Defenses (10 + modifier)"),
             _callout(bx, top + row * 9, R, top + row * 9, "", "HP, Speed"),
             _callout(x + 1.2 * u, y + h - kh / 2, x - 34, y + h - kh / 2, "Keyword", "Calling", side=-1),
             _callout(x + 1.2 * u, my, x - 34, my, "Name", side=-1),
             _callout(x + 8 * u, mid, x - 34, mid, "Perk", side=-1)]
    return _svg(710, round(h + 30), "".join(body), "A Calling card: its own values beside the symbols, its two ability symbols lit, and its perk")


def card_elements():
    """A sample card with every element of 3.1 called out; the bonus strip uses the stat symbols."""
    x, y, w = 120, 20, 300
    h, u = w * 88 / 63, w / 63
    th, kh, sw = h * .13, h * .1, w * .2
    sx, top, row, my = x + w - sw, y + th, (h - th - kh) / 10, y + (th - .7 * u) / 2
    text = ["**Reaction (1/S.R.)**,", "when an attack hits you:", "reduce its damage by 5."]
    body = [ledger_card(x, y, w, h, "Warden's Plate", {4: "+4", 8: "+12", 9: "−10"}, "", "II", ["STR"], art=icon_shield, text=text)]
    # keywords, laid out by estimated width so each one can be pointed at
    kws = [("Armor", "Type"), ("Noisy 3", "Property")]
    fs = 7.6 * PT * u
    def width(t):  # rough italic Garamond advance widths
        return sum(fs * (.24 if c in " ,.1il" else .36 if c in "rt" else .62 if c.isupper() or c == "+" else .46) for c in t)
    kx, ky = x + 2.4 * u, y + h - kh / 2 + fs * .32
    body.append(_text(f"{kx:.2f}", f"{ky:.2f}", " · ".join(t for t, _ in kws), round(fs, 2), BODY, "#000", anchor="start", italic=True))
    for k, (t, lab) in enumerate(kws):
        mid = kx + width(t) / 2
        lx = x + 40 + k * 110  # labels spread wider than the keywords so they never touch
        body.append(f'<line x1="{mid:.1f}" y1="{ky + 5:.1f}" x2="{lx:.1f}" y2="{y + h + 28:.1f}" stroke="{INK}" stroke-width="1" stroke-dasharray="3 3"/>')
        body.append(f'<circle cx="{mid:.1f}" cy="{ky + 5:.1f}" r="2.5" fill="{CRIMSON}"/>')
        body.append(_text(lx, f"{y + h + 44:.1f}", lab, 13, HEAD, INK))
        kx += width(t + " · ")
    right = [  # (point x, point y, label y, label, sub)
        (x + w - 1.6 * u, my, y + 26, "Rank", "I to V"),
        (x + w - 13.8 * u, y + 9.9 * u, y + 64, "Symbols", "who can equip it"),
        (x + w, top + row * 2, top + row * 2.3, "Bonus strip", "abilities"),
        (x + w, top + row * 6, top + row * 6, "", "Defenses (in a shield)"),
        (x + w, top + row * 8.5, top + row * 8.5, "", "HP, Speed"),
        (x + w - 6, y + h - kh / 2, y + h - 10, "Keywords", "type first"),
    ]
    for px, py, ly, lab, sub in right:
        body.append(f'<polyline points="{px:.1f},{py:.1f} {x + w + 34},{ly:.1f} {x + w + 50},{ly:.1f}" fill="none" stroke="{INK}" stroke-width="1" stroke-dasharray="3 3"/>')
        body.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3" fill="{CRIMSON}"/>')
        if lab:
            body.append(_text(x + w + 56, f"{ly + 5:.1f}", lab, 16, HEAD, INK, anchor="start"))
            body.append(_text(x + w + 56, f"{ly + 22:.1f}", sub, 13, BODY, MUTED, anchor="start", italic=True))
        else:
            body.append(_text(x + w + 56, f"{ly + 5:.1f}", sub, 13, BODY, MUTED, anchor="start", italic=True))
    fx = 9.4 * PT * u  # the effect's first line, under the icon (ledger_card's layout)
    ah = min((sx - x) * .45, (h - th - kh) * .4)
    ey = top + (h - th - kh - ah - 3 * u - len(text) * fx * 1.2) / 2 + ah + 3 * u + fx * 1.2
    left = [(x + 1.2 * u, my, my, "Name"), (x + 6 * u, ey, ey, "Effect")]
    for px, py, ly, lab in left:
        body.append(f'<polyline points="{px:.1f},{py:.1f} {x - 34},{ly:.1f} {x - 50},{ly:.1f}" fill="none" stroke="{INK}" stroke-width="1" stroke-dasharray="3 3"/>')
        body.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3" fill="{CRIMSON}"/>')
        body.append(_text(x - 56, f"{ly + 5:.1f}", lab, 16, HEAD, INK, anchor="end"))
    return _svg(680, round(h + 70), "".join(body), "A card: name, symbols and Rank on top, bonus strip on the right, effect in the center, keywords at the bottom")


STRIP_LABELS = ["STR", "DEX", "INT", "WIL", "STR", "DEX", "INT", "WIL", "HP", "SPD"]


def _strip_label(out, sx, cy, rh, fs, i, op=""):
    if 4 <= i <= 7:
        out.append(f'<rect x="{sx + 1.5}" y="{cy - rh * .38}" width="{fs * 2.1}" height="{rh * .76}" rx="{rh * .3}" fill="none" stroke="{GOLD}" stroke-width=".8"{op}/>')
    out.append(f'<g{op}>' + _text(sx + 2.5 + fs * 1.05, cy + fs * .35, STRIP_LABELS[i], fs * .8, HEAD, INK) + '</g>')


def tally_small(x, y, w, h, totals, hp=None, paper="#fffaf0", band=INK, ledger=False):
    """The tally card at card size: written totals in the strip, current HP, temp HP and death saves beside it.
    paper and band: the card's colours (the printed base set is white, title band included).
    ledger: the rulebook's Ledger look instead (ink symbols in the strip, black pen)."""
    th, kh = h * .13, h * .1
    sw = w * .2
    sx = x + w - sw
    rh = (h - th - kh) / 10
    fs = rh * .42
    pen, faint, ok, ko = ("#000", "#555", "#000", "#000") if ledger else (CRIMSON, MUTED, GOLD, CRIMSON)
    if ledger:
        out = [ledger_card(x, y, w, h, "Tally", kw=None)]
    else:
        out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="{paper}" stroke="{INK}" stroke-width="1.6"/>',
               f'<rect x="{x}" y="{y}" width="{w}" height="{th}" rx="7" fill="{band}" stroke="{INK}" stroke-width="1.6"/>'
               if band == INK else f'<line x1="{x}" y1="{y + th}" x2="{x + w}" y2="{y + th}" stroke="{INK}" stroke-width="1.6"/>',
               _text(x + 6, y + th * .68, "TALLY", th * .5, HEAD, PARCH if band == INK else INK, anchor="start"),
               f'<rect x="{sx}" y="{y + th}" width="{sw}" height="{rh * 10}" fill="{paper}" stroke="{INK}" stroke-width=".8"/>']
    for i in range(10):
        cy = y + th + rh * (i + .5)
        if not ledger:
            if i:
                out.append(f'<line x1="{sx}" y1="{y + th + rh * i}" x2="{x + w}" y2="{y + th + rh * i}" stroke="{MUTED}" stroke-width=".4"/>')
            _strip_label(out, sx, cy, rh, fs, i, ' opacity="0.45"')
        if i in totals:
            out.append(_text(sx + sw - 2, cy + fs * .45, totals[i], fs * 1.35, BODY, pen, anchor="end", italic=True, weight=600))
    # left area: current HP, temp HP, death saves
    lx, lw = x + w * .06, sx - x - w * .12
    by = y + th + rh * .6
    lab = rh * .36
    out += [_text(lx, by, "CURRENT HP", lab, HEAD, faint, anchor="start"),
            f'<rect x="{lx}" y="{by + rh * .2}" width="{lw}" height="{rh * 3.2}" rx="3" fill="none" stroke="{faint}" stroke-width=".7" stroke-dasharray="2 1.5"/>']
    if hp:
        for k, v in enumerate(hp):
            last = k == len(hp) - 1
            tx = lx + lw * (.2 + .3 * k)
            out.append(_text(tx, by + rh * 2.1, v, fs * 1.5, BODY, pen if last else faint, italic=True, weight=600))
            if not last:
                out.append(f'<line x1="{tx - fs * .8}" y1="{by + rh * 1.9}" x2="{tx + fs * .8}" y2="{by + rh * 1.5}" stroke="{faint}" stroke-width=".9"/>')
    by += rh * 4.2
    out += [_text(lx, by, "TEMP HP", lab, HEAD, faint, anchor="start"),
            f'<rect x="{lx}" y="{by + rh * .2}" width="{lw * .55}" height="{rh * 1.3}" rx="3" fill="none" stroke="{faint}" stroke-width=".7" stroke-dasharray="2 1.5"/>']
    by += rh * 2.4
    out.append(_text(lx, by, "DEATH SAVES", lab, HEAD, faint, anchor="start"))
    for r, (mark, col) in enumerate((("✓", ok), ("✗", ko))):
        yy = by + rh * (.8 + r * .95)
        out.append(_text(lx + lab * .5, yy + lab * .4, mark, lab * 1.2, BODY, col))
        for k in range(3):
            out.append(f'<rect x="{lx + lab * 1.6 + k * rh * .9}" y="{yy - rh * .3}" width="{rh * .6}" height="{rh * .6}" rx="1.5" fill="none" stroke="{INK}" stroke-width=".7"/>')
    return "".join(out)


def tally_card():
    """The tally card, called out: the one card you write on."""
    x, y, w = 200, 20, 300
    h = w * 88 / 63
    body = [tally_small(x, y, w, h, {0: "+3", 1: "+1", 2: "+0", 3: "+0", 4: "18", 5: "13", 6: "10", 7: "10", 8: "14", 9: "30"}, ["14", "9", "11"], ledger=True)]
    th, kh = h * .13, h * .1
    rh = (h - th - kh) / 10
    top = y + th
    R = x + w + 40
    bx = x + w + 12
    for r0, r1 in ((0, 4), (4, 8), (8, 10)):
        y0, y1 = top + rh * r0 + 4, top + rh * r1 - 4
        body.append(f'<path d="M{bx - 5} {y0:.1f}H{bx}V{y1:.1f}H{bx - 5}" fill="none" stroke="{INK}" stroke-width="1.2"/>')
    body += [_callout(bx, top + rh * 2, R, top + rh * 2, "Totals", "four modifiers"),
             _callout(bx, top + rh * 6, R, top + rh * 6, "", "four Defenses"),
             _callout(bx, top + rh * 9, R, top + rh * 9, "", "HP maximum, Speed"),
             _callout(x + 20, top + rh * 2, x - 34, top + rh * 2, "Current HP", "cross out, rewrite", side=-1),
             _callout(x + 20, top + rh * 5, x - 34, top + rh * 5.2, "Temp HP", side=-1),
             _callout(x + 20, top + rh * 7.6, x - 34, top + rh * 8, "Death saves", "successes, failures", side=-1)]
    return _svg(740, round(h + 30), "".join(body), "The tally card: ten totals lined up with the bonus strip, current HP, temporary HP and death saves")


BRAM_CALLING = {0: "+2", 1: "+0", 2: "+0", 3: "+2", 4: "12", 5: "10", 6: "10", 7: "12", 8: "14", 9: "30"}  # Templar
BRAM_TOTALS = {0: "+2", 1: "+0", 2: "+0", 3: "+2", 4: "17", 5: "12", 6: "10", 7: "12", 8: "22", 9: "30"}


def keeping_totals():
    body = []
    # Panel 1: in play
    body.append(_text(10, 22, "IN PLAY: SPREAD OUT BY SLOT", 15, HEAD, CRIMSON, anchor="start"))
    w, h, gap = 104, 146, 14
    sw, si = ["STR", "WIL"], ["STR", "DEX"]
    row1 = [("CALLING", "Templar", {}, "Calling", None, BRAM_CALLING, sw),
            ("ARMOR", "Mail", {4: "+3", 8: "+4"}, "Armor", icon_shield, None, si),
            ("HANDS", "Shield", {4: "+2", 5: "+2"}, "Shield", lambda cx, cy, s: icon_shield(cx, cy, s, 2), None, sw),
            ("", "Versatile Weapon", {}, "Weapon · Versatile", icon_sword, None, sw),
            ("JEWELRY", "Ring of Warding", {}, "Jewelry · Reaction", None, None, ALL4)]
    row2 = [("ITEM", "Potion of Healing", {}, "Consumable", None, None, ALL4),
            ("ASPECTS", "Springheel", {8: "+2"}, "Trait", None, None, si),
            ("", "Iron Will", {8: "+2"}, "Trait", None, None, sw),
            ("", "Barkeep", {}, "Knack", None, None, sw)]
    for r, cards in enumerate([row1, row2]):
        y = 52 + r * (h + 34)
        for i, (slot, name, vals, kw, art, own, lit) in enumerate(cards):
            x = 12 + i * (w + gap)
            if slot:
                body.append(_text(x, y - 7, slot, 10, HEAD, GOLD, anchor="start"))
            body.append(ledger_card(x, y, w, h, name, vals, kw, None if own else "I", lit, own, art))
    x = 12 + 4 * (w + gap)
    y = 52 + h + 34
    body.append(_text(x, y - 7, "TALLY", 10, HEAD, INK, anchor="start"))
    body.append(tally_small(x, y, w, h, BRAM_TOTALS, ["22", "9"], ledger=True))
    # Panel 2: adding up
    top = 52 + 2 * (h + 34) + 14
    body.append(f'<line x1="10" y1="{top - 22}" x2="610" y2="{top - 22}" stroke="{GOLD}" stroke-width="1"/>')
    body.append(_text(10, top, "ADDING UP: TALLY, CALLING, THEN EACH CARD ON TOP", 15, HEAD, CRIMSON, anchor="start"))
    W, H = 150, 210
    dx = W * .2
    x0, y0 = 12, top + 16
    stack = [("Mail", {4: "+3", 8: "+4"}, "Armor", si), ("Shield", {4: "+2", 5: "+2"}, "Shield", sw),
             ("Springheel", {8: "+2"}, "Trait", si), ("Iron Will", {8: "+2"}, "Trait", sw)]
    m = len(stack)
    cxs = x0 + m * dx  # the Calling, one strip left of the tally
    body.append(tally_small(cxs + dx, y0, W, H, BRAM_TOTALS, ledger=True))
    body.append(ledger_card(cxs, y0, W, H, "Templar", kw="Calling", lit=sw, own=BRAM_CALLING))
    rh = (H - H * .13 - H * .1) / 10
    for j, (name, vals, kw, lit) in enumerate(stack):
        body.append(ledger_card(x0 + (m - 1 - j) * dx, y0, W, H, name, vals, kw, "I", lit))
    ry = y0 + H * .13 + rh * 4
    body.append(f'<rect x="{x0 + W - dx}" y="{ry:.1f}" width="{cxs + dx + W - (x0 + W - dx):.1f}" height="{rh:.1f}" fill="{CRIMSON}" fill-opacity=".12" stroke="{CRIMSON}" stroke-width="1.6"/>')
    names = [n for n, *_ in reversed(stack)] + ["Calling", "Tally"]
    names = [{"Mail": "Armor", "Springheel": "Spring."}.get(n, n) for n in names]
    if LANG == "fr":  # French names are longer: abbreviate so the labels don't run together
        names = [{"Iron Will": "Vol.", "Spring.": "Saut.", "Shield": "Boucl.", "Armor": "Arm.", "Calling": "Voc.",
                  "Tally": "Déc."}.get(n, n) for n in names]
    for k, nm in enumerate(names):
        body.append(_text(x0 + W - dx / 2 + k * dx, y0 + H + 16, nm, 9, BODY, MUTED, italic=True))
    tx = cxs + dx + W + 22
    lines = [("Each row reads left to right,", BODY, INK, False),
             ("like a written sum:", BODY, INK, False),
             ("", BODY, INK, False),
             ("STR Defense", HEAD, CRIMSON, False),
             ("+2 Shield + 3 Armor", BODY, INK, False),
             ("+ 12 Calling = 17", BODY, INK, False),
             ("", BODY, INK, False),
             ("HP", HEAD, CRIMSON, False),
             ("+2 + 2 Traits + 4 Armor + 14 = 22", BODY, INK, False),
             ("", BODY, INK, False),
             ("Cards with an empty strip", BODY, MUTED, True),
             ("stay out of the stack.", BODY, MUTED, True)]
    for k, (t, st, col, it) in enumerate(lines):
        if t:
            body.append(_text(tx, y0 + 30 + k * 19, t, 14, st, col, anchor="start", italic=it))
    return _svg(620, max(y0 + H + 26, y0 + 30 + 12 * 19), "".join(body), "Cards spread out by Slot in play beside the tally card, and stacked on the tally card to add up the bonus strips into its totals")


# ---------- Slot frames (P 12.2): drawn at 10 units per mm, 67 × 98 mm ----------
ASPECT_GREEN = "#3f6b4f"
CRYSTAL = "#3d6b7a"
FRAME_W, FRAME_H = 670, 980
FRAME_CARD = (25, 80, 655, 960)  # where the 63 × 88 mm card sits: flush with the right border's inside edge
FRAME_BAND = {"armor": INK, "hand": INK, "jewelry": INK, "item": INK, "aspect": ASPECT_GREEN, "shard": CRYSTAL}


def _frame_icon(key, cx, cy, s):
    if key == "armor":
        return icon_shield(cx, cy, s, bands=2)
    if key == "hand":
        return icon_sword(cx, cy, s)
    if key == "jewelry":
        return icon_ring(cx, cy, s)
    if key == "item":
        return icon_potion(cx, cy, s)
    return gem(cx, cy, s * .5, ASPECT_GREEN if key == "aspect" else CRYSTAL)


def _md_tspans(s):
    """**bold** inside SVG text."""
    parts = s.split("**")
    return "".join(f'<tspan font-weight="700">{p}</tspan>' if i % 2 else p for i, p in enumerate(parts))


def _wrap(s, n):
    words, lines, cur = s.split(), [], ""
    for w in words:
        if len((cur + " " + w).replace("**", "")) > n and cur:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    return lines + [cur]


def frame_body(key, name, swap, reminder, slits=True):
    """One Slot frame (or Shard frame) as SVG elements in 0.1 mm units."""
    x0, y0, x1, y1 = FRAME_CARD
    band = FRAME_BAND[key]
    name, swap, reminder = tr(name), tr(swap), [tr(p) for p in reminder]
    out = [f'<rect x="0" y="0" width="{FRAME_W}" height="{FRAME_H}" fill="{PARCH}" stroke="{INK}" stroke-width="4"/>',
           f'<rect x="0" y="0" width="{FRAME_W}" height="{y0}" fill="{band}"/>',
           f'<circle cx="52" cy="{y0 / 2}" r="31" fill="{PARCH}" stroke="{GOLD}" stroke-width="3"/>',
           _frame_icon(key, 52, y0 / 2, 40),
           _text(98, y0 / 2 + 12, name.upper(), 34, HEAD, PARCH, anchor="start"),
           _text(FRAME_W - 24, y0 / 2 + 9, swap, 24, BODY, SHADE, anchor="end", italic=True),
           # the card's place: visible only when the Slot is empty
           f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="30" fill="#fbf6e9" stroke="{MUTED}" stroke-width="2.5" stroke-dasharray="14 9"/>',
           f'<g opacity=".16">{_frame_icon(key, (x0 + x1) / 2, y0 + 330, 300)}</g>']
    ty = y0 + 600
    for para in reminder:
        for line in _wrap(para, 38):
            out.append(_text((x0 + x1) / 2, ty, _md_tspans(line), 30, BODY, INK))
            ty += 38
        ty += 16
    if key == "armor":  # an empty Armor Slot adds +10 Speed: the frame's own strip, under the card's strip
        sw, top, rh = 126, y0 + 114.4, 67.76
        out.append(f'<rect x="{x1 - sw}" y="{top}" width="{sw}" height="{rh * 10}" fill="{SHADE}" stroke="{MUTED}" stroke-width="1.5"/>')
        cy = top + rh * 9.5
        out.append(f'<line x1="{x1 - sw}" y1="{top + rh * 9}" x2="{x1}" y2="{top + rh * 9}" stroke="{MUTED}" stroke-width="1.5"/>')
        out.append(sym_speed(x1 - sw + 30, cy, 44))
        out.append(_text(x1 - 10, cy + 12, "+10", 34, HEAD, CRIMSON, anchor="end"))
    if slits:  # photo-corner slits at the top-right and bottom-left corners of the card
        for (ax, ay), (bx, by) in (((x1 - 105, y0 - 12), (x1 + 12, y0 + 105)), ((x0 - 12, y1 - 105), (x0 + 105, y1 + 12))):
            out.append(f'<line x1="{ax}" y1="{ay}" x2="{bx}" y2="{by}" stroke="{CRIMSON}" stroke-width="7" stroke-linecap="round"/>')
        out.append(_text(x1 - 70, y0 + 90, "cut", 20, BODY, CRIMSON, italic=True))
        out.append(_text(x0 + 66, y1 - 66, "cut", 20, BODY, CRIMSON, italic=True))
    return "".join(out)


def slot_frame(key, name, swap, reminder):
    """A printable Slot frame, sized 67 × 98 mm by its viewBox."""
    return _svg(FRAME_W, FRAME_H, frame_body(key, name, swap, reminder), f"{name} Slot frame")


def frame_figure():
    """P 12.2: an empty Armor frame beside a Hand frame holding a weapon, parts called out."""
    s = .34  # figure scale: 0.34 px per 0.1 mm
    W, H = FRAME_W * s, FRAME_H * s
    ax, hx, y = 20, 330, 20
    x0, y0, x1, y1 = FRAME_CARD
    body = [f'<g transform="translate({ax} {y}) scale({s})">{frame_body("armor", "Armor", "Swap: 10 minutes", ["Empty: **+10 ft Speed**."], slits=False)}</g>',
            f'<g transform="translate({hx} {y}) scale({s})">{frame_body("hand", "Hand", "Swap: free interaction", [], slits=False)}</g>']
    # the tucked card, its corners under the slits
    cw, ch = (x1 - x0) * s, (y1 - y0) * s
    cx, cy = hx + x0 * s, y + y0 * s
    body.append(ledger_card(cx, cy, cw, ch, "Finesse Blade", {}, "Weapon", "I", ["DEX", "WIL"], art=icon_sword))
    for (px, py), (qx, qy) in (((x1 - 105, y0 - 12), (x1 + 12, y0 + 105)), ((x0 - 12, y1 - 105), (x0 + 105, y1 + 12))):
        P, Q = (hx + px * s, y + py * s), (hx + qx * s, y + qy * s)
        tri = (f"{P[0]:.1f},{P[1]:.1f} {Q[0]:.1f},{Q[1]:.1f} {hx + (x1 if px > x0 else x0) * s:.1f},{y + (y0 if py < y0 + 50 else y1) * s:.1f}")
        body.append(f'<polygon points="{tri}" fill="{PARCH}" stroke="{INK}" stroke-width="1"/>')
        body.append(f'<line x1="{P[0]:.1f}" y1="{P[1]:.1f}" x2="{Q[0]:.1f}" y2="{Q[1]:.1f}" stroke="{CRIMSON}" stroke-width="2.2"/>')
    R = hx + W + 30
    body += [_callout(hx + 200 * s, y + 40 * s, R, y + 14, "Slot", "symbol and name"),
             _callout(hx + 600 * s, y + 40 * s, R, y + 58, "Swap time", "3.5"),
             _callout(hx + (x1 - 8) * s, y + (y0 + 85) * s, R, y + 112, "Slit", "the card's corner tucks under it"),
             _callout(hx + (x1 - 20) * s, y + (y0 + 400) * s, R, y + 190, "Bonus strip", "on the frame's edge"),
             _callout(hx + (x0 + 105) * s, y + (y1 + 12) * s, R, y + (y1 + 12) * s, "Slit", "opposite corner"),
             _text(ax + W / 2, y + H + 24, "Empty: it shows what the Slot does", 14, BODY, MUTED, italic=True),
             _text(hx + W / 2, y + H + 24, "Framed: the card is equipped", 14, BODY, MUTED, italic=True)]
    return _svg(R + 230, H + 56, "".join(body), "An empty Armor Slot frame showing +10 ft Speed, and a Hand Slot frame holding a weapon card by two corner slits")


def rank_ladder():
    """Vertical ladder, Rank I at the bottom to V at the top, sized to sit beside a list."""
    body = []
    data = [("I", "Small edge"), ("II", "Defining"), ("III", "Strong"), ("IV", "Bends rules"), ("V", "Breaks rules")]
    colors = ["#9a8a6a", GOLD, CRIMSON, "#4b2a6b", INK]
    step, gx = 62, 52
    for i, (r, label) in enumerate(data):
        cy = 40 + (4 - i) * step
        size = 16 + i * 3.5
        body.append(f'<line x1="18" y1="{cy}" x2="{gx - size - 4:.1f}" y2="{cy}" stroke="{GOLD}" stroke-width="1.5"/>')
        body.append(gem(gx, cy, size, colors[i], r, 11 + i * 1.5))
        body.append(_text(gx + 40, cy + 5, label, 15, HEAD, anchor="start"))
    body.append(f'<line x1="14" y1="{40 + 4 * step + 24}" x2="14" y2="14" stroke="{INK}" stroke-width="1.5" marker-end="url(#arr)"/>')
    return _svg(215, 40 + 4 * step + 34, "".join(body), "The five Ranks, from a small edge at the bottom to rule-breaking at the top")


def initiative_timeline():
    body = []
    x0, colw = 150, 135
    rows = [("Side A", "won initiative", 60), ("Side B", "", 130)]
    phases = ["Round 1", "Round 2", "Round 3"]
    for j, ph in enumerate(phases):
        body.append(_text(x0 + j * (2 * colw + 20) + colw, 30, ph, 19, HEAD))
    for name, sub, y in rows:
        body.append(_text(20, y + 22, name, 19, HEAD, anchor="start"))
        if sub:
            body.append(_text(20, y + 44, sub, 15, BODY, MUTED, anchor="start", italic=True))
    order = 0
    for j in range(3):
        bx = x0 + j * (2 * colw + 20)
        # Side A bar
        if j == 0:
            body.append(f'<rect x="{bx}" y="60" width="{colw - 10}" height="36" rx="6" fill="{SHADE}" stroke="{INK}" stroke-width="1.8" stroke-dasharray="5 4"/>')
            body.append(_text(bx + (colw - 10) / 2, 84, "Move OR Action", 15, BODY, INK, weight=600))
        else:
            body.append(f'<rect x="{bx}" y="60" width="{colw - 10}" height="36" rx="6" fill="{GOLD}" stroke="{INK}" stroke-width="1.8"/>')
            body.append(_text(bx + (colw - 10) / 2, 84, "Full turns", 15, BODY, PARCH, weight=600))
        body.append(f'<rect x="{bx + colw}" y="130" width="{colw - 10}" height="36" rx="6" fill="{CRIMSON}" stroke="{INK}" stroke-width="1.8"/>')
        body.append(_text(bx + colw + (colw - 10) / 2, 154, "Full turns", 15, BODY, PARCH, weight=600))
        body.append(f'<path d="M{bx + colw - 10} 78 Q{bx + colw} 78 {bx + colw + 2} 128" fill="none" stroke="{INK}" stroke-width="1.4" marker-end="url(#arr)"/>')
        # the Boss's half turn: one action somewhere inside the characters' side (P 6.1, GM 3)
        body.append(f'<circle cx="{bx + colw + (colw - 10) / 2}" cy="130" r="12" fill="#4b2a6b" stroke="{INK}" stroke-width="1.5"/>')
        body.append(_text(bx + colw + (colw - 10) / 2, 135, "B", 13, HEAD, PARCH))
    body.append(f'<circle cx="160" cy="205" r="10" fill="#4b2a6b" stroke="{INK}" stroke-width="1.5"/>')
    body.append(_text(178, 211, "A Boss on Side A also takes a half turn (one action) during Side B, the characters' side.", 18, BODY, INK, anchor="start"))
    body.append(_text(178, 238, "Within a side, creatures act in any order they agree on.", 18, BODY, MUTED, anchor="start", italic=True))
    body.append(_text(178, 265, "Ambush: if the other side is surprised, Side A takes full turns in round 1.", 18, BODY, MUTED, anchor="start", italic=True))
    return _svg(1050, 280, "".join(body), "Side initiative timeline")


def combat_grid():
    s = 32
    body = []

    def grid(ox, oy, cols, rows):
        g = [f'<rect x="{ox}" y="{oy}" width="{cols * s}" height="{rows * s}" fill="{PARCH}" stroke="{INK}" stroke-width="1.5"/>']
        for c in range(1, cols):
            g.append(f'<line x1="{ox + c * s}" y1="{oy}" x2="{ox + c * s}" y2="{oy + rows * s}" stroke="{SHADE}" stroke-width="1"/>')
        for r in range(1, rows):
            g.append(f'<line x1="{ox}" y1="{oy + r * s}" x2="{ox + cols * s}" y2="{oy + r * s}" stroke="{SHADE}" stroke-width="1"/>')
        return "".join(g)

    def token(ox, oy, c, r, letter, fill):
        x, y = ox + c * s + s / 2, oy + r * s + s / 2
        return f'<circle cx="{x}" cy="{y}" r="{s * .38}" fill="{fill}" stroke="{INK}" stroke-width="1.8"/>' + _text(x, y + 5, letter, 14, HEAD, PARCH)

    # Panel 1: reach & opportunity attack
    ox, oy = 20, 40
    body.append(_text(ox + 4 * s, 26, "Opportunity attack", 16, HEAD))
    body.append(grid(ox, oy, 8, 6))
    for dc in (-1, 0, 1):
        for dr in (-1, 0, 1):
            body.append(f'<rect x="{ox + (2 + dc) * s}" y="{oy + (3 + dr) * s}" width="{s}" height="{s}" fill="{GOLD}" opacity=".35"/>')
    body.append(token(ox, oy, 2, 3, "F", GOLD))
    body.append(token(ox, oy, 3, 2, "E", CRIMSON))
    body.append(f'<path d="M{ox + 3.5 * s} {oy + 2.5 * s} L{ox + 6.5 * s} {oy + 1.5 * s}" stroke="{CRIMSON}" stroke-width="2.2" stroke-dasharray="5 4" marker-end="url(#arrc)"/>')
    body.append(_text(ox + 4 * s, oy + 6 * s + 22, "E leaves F's reach (gold): F may use", 13, BODY, MUTED, italic=True))
    body.append(_text(ox + 4 * s, oy + 6 * s + 40, "its reaction to make one melee attack.", 13, BODY, MUTED, italic=True))

    # Panel 2: cover
    ox2 = ox + 8 * s + 50
    body.append(_text(ox2 + 4 * s, 26, "Cover", 16, HEAD))
    body.append(grid(ox2, oy, 8, 6))
    body.append(f'<rect x="{ox2 + 5 * s}" y="{oy + 1 * s}" width="{s * .35}" height="{s * 2}" fill="{INK}"/>')
    body.append(f'<rect x="{ox2 + 5 * s}" y="{oy + 4 * s}" width="{s * .35}" height="{s * 2}" fill="{INK}"/>')
    body.append(token(ox2, oy, 1, 3, "A", GOLD))
    body.append(token(ox2, oy, 6, 2, "T", CRIMSON))
    body.append(token(ox2, oy, 6, 5, "H", CRIMSON))
    body.append(f'<line x1="{ox2 + 1.5 * s}" y1="{oy + 3.5 * s}" x2="{ox2 + 6.5 * s}" y2="{oy + 2.5 * s}" stroke="{INK}" stroke-width="1.6" stroke-dasharray="4 3"/>')
    body.append(f'<line x1="{ox2 + 1.5 * s}" y1="{oy + 3.5 * s}" x2="{ox2 + 6.5 * s}" y2="{oy + 5.5 * s}" stroke="{INK}" stroke-width="1.6" stroke-dasharray="4 3"/>')
    body.append(_text(ox2 + 4 * s, oy + 6 * s + 22, "T behind the wall's edge: cover, +2 STR and DEX Defense.", 13, BODY, MUTED, italic=True))
    body.append(_text(ox2 + 4 * s, oy + 6 * s + 40, "H fully hidden by the wall: can't be targeted.", 13, BODY, MUTED, italic=True))
    return _svg(ox2 + 8 * s + 20, oy + 6 * s + 56, "".join(body), "Opportunity attack and cover on a grid")


def death_saves():
    body = [_text(30, 46, "Successes", 16, HEAD, anchor="start"), _text(30, 116, "Failures", 16, HEAD, anchor="start")]
    for i in range(3):
        x = 190 + i * 60
        body.append(f'<circle cx="{x}" cy="40" r="20" fill="{GOLD if i < 2 else PARCH}" stroke="{INK}" stroke-width="2"/>')
        body.append(f'<circle cx="{x}" cy="110" r="20" fill="{CRIMSON if i < 1 else PARCH}" stroke="{INK}" stroke-width="2"/>')
        if i < 1:
            body.append(f'<path d="M{x - 8} 102l16 16M{x + 8} 102l-16 16" stroke="{PARCH}" stroke-width="3"/>')
    body.append(_text(390, 46, "3 = stable", 15, BODY, INK, anchor="start", weight=600))
    body.append(_text(390, 116, "3 = death", 15, BODY, CRIMSON, anchor="start", weight=600))
    notes = ["d20, no modifiers, at the start of each turn at 0 HP: 10+ succeeds.",
             "Natural 20: regain 1 HP. Natural 1: two failures.",
             "Damage at 0 HP: one failure (two on a critical hit). Any healing: back up."]
    for k, n in enumerate(notes):
        body.append(_text(30, 172 + k * 24, n, 16, BODY, MUTED, anchor="start", italic=True))
    return _svg(620, 230, "".join(body), "The death save track")


def armor_tiers():
    body = []
    data = [("Leather", "+2 STR · +1 DEX", 0, "+2 HP · +5 ft"), ("Mail", "+3 STR", 1, "+4 HP"), ("Plate", "+4 STR", 2, "+12 HP · −10 ft"), ("Shield", "+2 STR · +2 DEX", 0, "one Hand")]
    for i, (name, bonus, bands, req) in enumerate(data):
        x = 90 + i * 150
        body.append(icon_shield(x, 70, 70 + bands * 10, bands=bands if name != "Shield" else 0))
        body.append(_text(x, 140, name, 16, HEAD))
        body.append(_text(x, 162, bonus, 13.5, BODY, INK, weight=600))
        body.append(_text(x, 182, req, 13, BODY, MUTED, italic=True))
    return _svg(620, 200, "".join(body), "Armor tiers")


def areas_of_effect():
    body = []
    panels = ["Cone", "Cube", "Cylinder", "Emanation", "Line", "Sphere"]
    pw = 150
    for i, name in enumerate(panels):
        x = 10 + (i % 3) * (pw + 20)
        y = 10 + (i // 3) * 170
        cx, cy = x + pw / 2, y + 70
        body.append(f'<rect x="{x}" y="{y}" width="{pw}" height="140" rx="8" fill="{PARCH}" stroke="{SHADE}" stroke-width="1.5"/>')
        fill = f'fill="{CRIMSON}" fill-opacity=".25" stroke="{CRIMSON}" stroke-width="2"'
        origin = f'<circle cx="{{0}}" cy="{{1}}" r="5" fill="{INK}"/>'
        if name == "Cone":
            body.append(f'<path d="M{x + 25} {cy} L{x + 130} {cy - 52} L{x + 130} {cy + 52} Z" {fill}/>' + origin.format(x + 25, cy))
        elif name == "Cube":
            body.append(f'<rect x="{cx - 35}" y="{cy - 40}" width="70" height="70" {fill}/>' + f'<path d="M{cx - 35} {cy - 40}l18 -14h70l-18 14M{cx + 35} {cy - 40}l18 -14v70l-18 14" fill="none" stroke="{CRIMSON}" stroke-width="2"/>' + origin.format(cx - 35, cy + 30))
        elif name == "Cylinder":
            body.append(f'<path d="M{cx - 42} {cy - 30}v55a42 14 0 0 0 84 0v-55" {fill}/><ellipse cx="{cx}" cy="{cy - 30}" rx="42" ry="14" {fill}/>' + origin.format(cx, cy + 25))
        elif name == "Emanation":
            body.append(f'<circle cx="{cx}" cy="{cy}" r="48" {fill} stroke-dasharray="6 4"/>' + f'<circle cx="{cx}" cy="{cy}" r="12" fill="{GOLD}" stroke="{INK}" stroke-width="1.8"/>')
            body.append(f'<path d="M{cx + 54} {cy + 30} l22 0" stroke="{INK}" stroke-width="1.5" marker-end="url(#arr)"/>')
        elif name == "Line":
            body.append(f'<rect x="{x + 22}" y="{cy - 9}" width="110" height="18" {fill}/>' + origin.format(x + 22, cy))
        elif name == "Sphere":
            body.append(f'<circle cx="{cx}" cy="{cy}" r="48" {fill}/><ellipse cx="{cx}" cy="{cy}" rx="48" ry="15" fill="none" stroke="{CRIMSON}" stroke-width="1.2"/>' + origin.format(cx, cy))
        body.append(_text(cx, y + 132, name, 15, HEAD))
    return _svg(3 * (pw + 20), 345, "".join(body), "The six areas of effect")


def ornament():
    """Small divider used under chapter titles."""
    return _svg(
        300, 24,
        f'<line x1="10" y1="12" x2="125" y2="12" stroke="{GOLD}" stroke-width="1.5"/>'
        f'<line x1="175" y1="12" x2="290" y2="12" stroke="{GOLD}" stroke-width="1.5"/>'
        + _hex(150, 12, 9, fill=CRIMSON, stroke=INK, sw=1.5, rot=30)
        + _hex(132, 12, 4, fill=GOLD, stroke="none", sw=0, rot=30)
        + _hex(168, 12, 4, fill=GOLD, stroke="none", sw=0, rot=30),
        "",
    )
