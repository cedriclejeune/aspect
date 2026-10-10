"""Inline SVG illustrations for the PDF rulebook.

Style: ink line art on parchment, crimson for the Core, gold for Aspects.
Each public function returns an <svg> string sized by its viewBox (CSS sets width).
"""
import math

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


def _text(x, y, s, size=14, style=BODY, fill=INK, anchor="middle", weight=None, italic=False):
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
    return _svg(400, 400, "".join(body), "A Core gem surrounded by five Slots holding Aspects")


def core_loop():
    cx, cy, R = 350, 200, 125
    steps = [("Explore", icon_compass), ("Fight", icon_swords), ("Loot", icon_chest), ("Rest &amp; Rebuild", icon_fire)]
    body = []
    for i in range(4):
        a1, a2 = math.radians(-90 + 90 * i + 22), math.radians(-90 + 90 * (i + 1) - 22)
        body.append(
            f'<path d="M{cx + R * math.cos(a1):.1f} {cy + R * math.sin(a1):.1f} A{R} {R} 0 0 1 {cx + R * math.cos(a2):.1f} {cy + R * math.sin(a2):.1f}" '
            f'fill="none" stroke="{INK}" stroke-width="2" marker-end="url(#arr)"/>'
        )
    for i, (name, ic) in enumerate(steps):
        a = math.radians(-90 + 90 * i)
        x, y = cx + R * math.cos(a), cy + R * math.sin(a)
        body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="34" fill="{PARCH}" stroke="{INK}" stroke-width="2.2"/>')
        body.append(ic(x, y, 34))
        lx = x + (62 if i == 1 else -62 if i == 3 else 0)
        ly = y + (6 if i in (1, 3) else -44 if i == 0 else 56)
        body.append(_text(lx, ly, name, 17, HEAD, INK, anchor="start" if i == 1 else "end" if i == 3 else "middle"))
    body.append(_text(cx, cy - 6, "No class.", 17, BODY, MUTED, italic=True))
    body.append(_text(cx, cy + 16, "No level.", 17, BODY, MUTED, italic=True))
    return _svg(700, 400, "".join(body), "The core loop: explore, fight, loot, rest and rebuild")


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


def character_anatomy():
    body = [gem(95, 200, 58, CRIMSON, "CORE", 16),
            _text(95, 290, "STR · DEX · INT · CHA", 13, BODY, MUTED, italic=True),
            _text(95, 308, "HP · Speed", 13, BODY, MUTED, italic=True)]
    groups = [  # (title, x0, y, [(name, icon or None)])
        ("Armor", 230, 85, [("Light Armor", icon_shield)]),
        ("Hands", 370, 85, [("Finesse Blade", icon_sword), ("Light Blade", icon_sword)]),
        ("Jewelry", 230, 215, [("Ring of Warding", icon_ring)]),
        ("Items", 370, 215, [("Potion ×1", icon_potion), ("empty", None)]),
        ("Attributes", 230, 345, [("Cat Burglar", icon_mask), ("Springheel", icon_jump), ("Iron Will", icon_fire)]),
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
    body.append(_text(sx + 50, 335, "unequipped Aspects", 12, BODY, MUTED, italic=True))
    body.append(_text(sx + 50, 352, "swap at rests", 12, BODY, CRIMSON, italic=True))
    return _svg(700, 400, "".join(body), "A character: Core, Armor, two Hands, Jewelry, two Items, three Attributes and a Stash")


def aspect_card_anatomy():
    x, y, w, h = 40, 20, 270, 380
    sw, top = 50, y + 56  # bonus strip, right edge
    sx = x + w - sw
    row = (h - 56 - 40) / 10
    body = [f'<rect x="{x + 6}" y="{y + 6}" width="{w}" height="{h}" rx="12" fill="{SHADE}"/>',
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{PARCH}" stroke="{INK}" stroke-width="2.5"/>',
            f'<rect x="{x}" y="{y}" width="{w}" height="56" rx="12" fill="{GOLD}" stroke="{INK}" stroke-width="2.5"/>',
            _text(x + 16, y + 36, "HEAVY ARMOR", 19, HEAD, PARCH, anchor="start"),
            gem(x + w - 28, y + 28, 18, CRIMSON, "II", 13),
            f'<rect x="{sx}" y="{top}" width="{sw}" height="{row * 10}" fill="{SHADE}" stroke="{INK}" stroke-width="1"/>']
    labels = ["STR", "DEX", "INT", "CHA", "STR", "DEX", "INT", "CHA", "HP", "SPD"]
    values = {4: "+4", 9: "−10"}
    for i, lab in enumerate(labels):
        cy = top + row * i + row / 2
        if i:
            body.append(f'<line x1="{sx}" y1="{top + row * i}" x2="{sx + sw}" y2="{top + row * i}" stroke="{MUTED}" stroke-width="0.5"/>')
        faded = "" if i in values else ' opacity="0.3"'
        if 4 <= i <= 7:
            body.append(f'<path d="M{sx + 5},{cy - 10} h22 v8 c0,7 -5,11 -11,13 c-6,-2 -11,-6 -11,-13 z" fill="none" stroke="{GOLD}" stroke-width="1.3"{faded}/>')
        body.append(f'<g{faded}>' + _text(sx + 16, cy + 3.5, lab, 8.5, HEAD, INK) + '</g>')
        if i in values:
            body.append(_text(sx + sw - 3, cy + 5, values[i], 13, HEAD, CRIMSON, anchor="end"))
    cx = x + (w - sw) / 2
    body += [icon_shield(cx, y + 150, 90),
             _text(cx, y + 250, "Plate, scarred by", 14, BODY, MUTED, italic=True),
             _text(cx, y + 268, "a hundred blades.", 14, BODY, MUTED, italic=True),
             f'<line x1="{x + 14}" y1="{y + h - 40}" x2="{x + w - 14}" y2="{y + h - 40}" stroke="{GOLD}" stroke-width="1.5"/>',
             _text(x + w / 2, y + h - 16, "Armor · Noisy · Req STR +2", 14, BODY, INK, italic=True)]
    callouts = [  # (point y, point x, label y, label)
        (y + 36, x + 150, y + 10, "Name"),
        (y + 28, x + w - 10, y + 52, "Rank"),
        (top + row * 4.5, sx + sw - 6, y + 130, "Bonus strip"),
        (y + 210, cx + 40, y + 215, "Effect / art"),
        (y + h - 20, x + w - 30, y + h - 20, "Keywords"),
    ]
    for py, px, ly, label in callouts:
        body.append(f'<polyline points="{px},{py} {x + w + 30},{ly} {x + w + 50},{ly}" fill="none" stroke="{INK}" stroke-width="1" stroke-dasharray="3 3"/>')
        body.append(f'<circle cx="{px}" cy="{py}" r="3" fill="{CRIMSON}"/>')
        body.append(_text(x + w + 58, ly + 5, label, 16, HEAD, INK, anchor="start"))
    return _svg(620, 420, "".join(body), "Anatomy of an Aspect card")


STRIP_LABELS = ["STR", "DEX", "INT", "CHA", "STR", "DEX", "INT", "CHA", "HP", "SPD"]


def strip_card(x, y, w, h, name, vals, kw, art=None, core=None):
    """An Aspect card with its bonus strip on the right. vals: {row: "+3"}. core: {row: (own, total)}."""
    th, kh = h * .13, h * .1
    sw = w * .2
    sx = x + w - (2 * sw if core else sw)
    rh = (h - th - kh) / 10
    fs = rh * .42
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="{PARCH}" stroke="{INK}" stroke-width="1.6"/>',
           f'<rect x="{x}" y="{y}" width="{w}" height="{th}" rx="7" fill="{GOLD}" stroke="{INK}" stroke-width="1.6"/>',
           _text(x + 6, y + th * .68, name, min(th * .5, (w - (2 * sw if core else 0) - 12) / (len(name) * .66)), HEAD, PARCH, anchor="start"),
           f'<rect x="{sx}" y="{y + th}" width="{x + w - sx}" height="{rh * 10}" fill="{SHADE}" stroke="{INK}" stroke-width=".8"/>',
           f'<line x1="{x}" y1="{y + h - kh}" x2="{x + w}" y2="{y + h - kh}" stroke="{GOLD}" stroke-width="1"/>',
           _text(x + w / 2, y + h - kh * .32, kw, kh * .5, BODY, INK, italic=True)]
    if core:
        out.append(f'<line x1="{sx + sw}" y1="{y + th}" x2="{sx + sw}" y2="{y + th + rh * 10}" stroke="{INK}" stroke-width=".8"/>')
    for i, lab in enumerate(STRIP_LABELS):
        cy = y + th + rh * (i + .5)
        if i:
            out.append(f'<line x1="{sx}" y1="{y + th + rh * i}" x2="{x + w}" y2="{y + th + rh * i}" stroke="{MUTED}" stroke-width=".4"/>')
        shown = i in vals or core
        op = "" if shown else ' opacity="0.3"'
        if 4 <= i <= 7:
            out.append(f'<rect x="{sx + 1.5}" y="{cy - rh * .38}" width="{fs * 2.1}" height="{rh * .76}" rx="{rh * .3}" fill="none" stroke="{GOLD}" stroke-width=".8"{op}/>')
        out.append(f'<g{op}>' + _text(sx + 2.5 + fs * 1.05, cy + fs * .35, lab, fs * .8, HEAD, INK) + '</g>')
        if core:
            own, tot = core[i]
            out.append(_text(sx + sw - 2, cy + fs * .4, own, fs * 1.15, HEAD, INK, anchor="end"))
            out.append(f'<rect x="{sx + sw + 2}" y="{cy - rh * .4}" width="{sw - 4}" height="{rh * .8}" rx="2" fill="{PARCH}" stroke="{MUTED}" stroke-width=".7" stroke-dasharray="2 1.5"/>')
            out.append(_text(sx + sw * 1.5, cy + fs * .45, tot, fs * 1.35, BODY, CRIMSON, italic=True, weight=600))
        elif i in vals:
            out.append(_text(sx + sw - 2, cy + fs * .4, vals[i], fs * 1.15, HEAD, CRIMSON, anchor="end"))
    if core:
        out.append(_text(sx + sw * .5, y + th * .7, "own", th * .36, BODY, PARCH, italic=True))
        out.append(_text(sx + sw * 1.5, y + th * .7, "total", th * .36, BODY, PARCH, italic=True))
    if art:
        out.append(art((x + sx) / 2, y + th + (h - th - kh) * .45, (sx - x) * .5))
    return "".join(out)


BRAM_CORE = {0: ("+3", "+3"), 1: ("+1", "+1"), 2: ("+0", "+0"), 3: ("+0", "+0"), 4: ("13", "18"),
             5: ("11", "13"), 6: ("10", "10"), 7: ("10", "10"), 8: ("14", "14"), 9: ("30", "30")}


def keeping_totals():
    body = []
    # Panel 1: in play
    body.append(_text(10, 22, "IN PLAY: SPREAD OUT BY SLOT", 15, HEAD, CRIMSON, anchor="start"))
    w, h, gap = 104, 146, 14
    row1 = [("CORE", "Brute I", {}, "Core · Medium", None, BRAM_CORE),
            ("ARMOR", "Medium Armor I", {4: "+3"}, "Armor · Req STR +1", icon_shield, None),
            ("HANDS", "Shield I", {4: "+2", 5: "+2"}, "Shield", lambda cx, cy, s: icon_shield(cx, cy, s, 2), None),
            ("", "Versatile Weapon I", {}, "Weapon · Versatile", icon_sword, None),
            ("JEWELRY", "Ring of Warding I", {}, "Jewelry · Reaction", None, None)]
    row2 = [("ITEM", "Potion of Healing", {}, "Consumable", None, None),
            ("ATTRIBUTES", "Stone Blood I", {}, "Trait · Resist Poison", None, None),
            ("", "Iron Will I", {}, "Trait", None, None),
            ("", "Cat Burglar I", {}, "Knack", None, None)]
    for r, cards in enumerate([row1, row2]):
        y = 52 + r * (h + 34)
        for i, (slot, name, vals, kw, art, core) in enumerate(cards):
            x = 12 + i * (w + gap)
            if slot:
                body.append(_text(x, y - 7, slot, 10, HEAD, GOLD, anchor="start"))
            body.append(strip_card(x, y, w, h, name, vals, kw, art, core))
    # Panel 2: adding up
    top = 52 + 2 * (h + 34) + 14
    body.append(f'<line x1="10" y1="{top - 22}" x2="610" y2="{top - 22}" stroke="{GOLD}" stroke-width="1"/>')
    body.append(_text(10, top, "ADDING UP: CORE FIRST, EACH CARD ON TOP", 15, HEAD, CRIMSON, anchor="start"))
    W, H = 150, 210
    dx, dy = W * .2, H * .13
    x0, y0 = 12, top + 16
    stack = [("Medium Armor I", {4: "+3"}, "Armor · Req STR +1"), ("Shield I", {4: "+2", 5: "+2"}, "Shield")]
    m = len(stack)
    cxs = x0 + m * dx + dx
    body.append(strip_card(cxs, y0, W, H, "Brute I", {}, "Core · Medium", None, BRAM_CORE))
    rh = (H - H * .13 - H * .1) / 10
    for j, (name, vals, kw) in enumerate(stack):
        cx, cy = x0 + (m - 1 - j) * dx, y0
        body.append(strip_card(cx, cy, W, H, name, vals, kw))
    ry = y0 + H * .13 + rh * 4
    body.append(f'<rect x="{x0 + W - dx}" y="{ry:.1f}" width="{cxs + W - (x0 + W - dx):.1f}" height="{rh:.1f}" fill="{CRIMSON}" fill-opacity=".12" stroke="{CRIMSON}" stroke-width="1.6"/>')
    names = ["Shield", "Armor", "Core", "Total"]
    for k, nm in enumerate(names):
        body.append(_text(x0 + W - dx / 2 + k * dx, y0 + H + 16, nm, 9, BODY, MUTED, italic=True))
    tx = cxs + W + 26
    lines = [("Each row reads left to right,", BODY, INK, False),
             ("like a written sum:", BODY, INK, False),
             ("", BODY, INK, False),
             ("STR Defense", HEAD, CRIMSON, False),
             ("+2 Shield + 3 Armor", BODY, INK, False),
             ("+ 13 Core = 18", BODY, INK, False),
             ("", BODY, INK, False),
             ("DEX Defense", HEAD, CRIMSON, False),
             ("+2 Shield + 11 Core = 13", BODY, INK, False),
             ("", BODY, INK, False),
             ("Cards with an empty strip", BODY, MUTED, True),
             ("stay out of the stack.", BODY, MUTED, True)]
    for k, (t, st, col, it) in enumerate(lines):
        if t:
            body.append(_text(tx, y0 + 30 + k * 19, t, 15, st, col, anchor="start", italic=it))
    return _svg(620, max(y0 + H + 26, y0 + 30 + 12 * 19), "".join(body), "Cards spread out by Slot in play, and stacked to add up the bonus strips into the Core card's Total column")


def rank_ladder():
    body = []
    data = [("I", "Small edge"), ("II", "Defining"), ("III", "Strong"), ("IV", "Bends rules"), ("V", "Breaks rules")]
    colors = ["#9a8a6a", GOLD, CRIMSON, "#4b2a6b", INK]
    for i, (r, label) in enumerate(data):
        x = 64 + i * 118
        size = 20 + i * 6
        base = 150
        body.append(f'<line x1="{x}" y1="{base + 4}" x2="{x}" y2="{base + 26}" stroke="{GOLD}" stroke-width="1.5"/>')
        body.append(gem(x, base - size, size, colors[i], r, 13 + i * 2))
        body.append(_text(x, base + 50, label, 15, HEAD))
    body.append(f'<line x1="20" y1="{176}" x2="580" y2="{176}" stroke="{INK}" stroke-width="1.5" marker-end="url(#arr)"/>')
    body.append(_text(300, 230, "Higher Ranks print bigger numbers", 14, BODY, MUTED, italic=True))
    return _svg(600, 245, "".join(body), "The five Ranks, from a small edge to rule-breaking")


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
        body.append(f'<circle cx="{bx + 2 * colw + 5}" cy="113" r="12" fill="#4b2a6b" stroke="{INK}" stroke-width="1.5"/>')
        body.append(_text(bx + 2 * colw + 5, 118, "B", 13, HEAD, PARCH))
    body.append(f'<circle cx="160" cy="205" r="10" fill="#4b2a6b" stroke="{INK}" stroke-width="1.5"/>')
    body.append(_text(178, 211, "Boss: second full turn at the end of each round", 18, BODY, INK, anchor="start"))
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
    body.append(_text(ox2 + 4 * s, oy + 6 * s + 22, "T behind the wall's edge: cover, +2 AC.", 13, BODY, MUTED, italic=True))
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
    data = [("Light", "12 + DEX", 0, "—"), ("Medium", "14 + DEX (max +2)", 1, "STR +1 or DEX +1"), ("Heavy", "17", 2, "STR +2"), ("Shield", "+2", 0, "one hand")]
    for i, (name, ac, bands, req) in enumerate(data):
        x = 90 + i * 150
        body.append(icon_shield(x, 70, 70 + bands * 10, bands=bands if name != "Shield" else 0))
        body.append(_text(x, 140, name, 16, HEAD))
        body.append(_text(x, 162, f"AC {ac}", 14, BODY, INK, weight=600))
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
