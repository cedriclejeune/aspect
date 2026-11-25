"""Vector animatic: Hilda tiptoes to set a stone on a cairn, wobbles, and everything falls on her. 1920x1080, 24 fps, 8 s."""
import math, random, sys
from PIL import Image, ImageDraw

W, H, SS, FPS, DUR = 1920, 1080, 2, 24, 8.0
G = 900                      # ground line
LLEG, FOOT = 95, 12
SKY, GRASS, GRASS_D = (206, 221, 226), (138, 166, 98), (108, 134, 76)
INK = (52, 44, 40)
SKIN, TUNIC, TROUS = (241, 196, 160), (96, 128, 72), (112, 82, 56)
PACK, ROCK, BEANIE = (146, 98, 58), (152, 152, 150), (184, 52, 42)
BRAID, BELT, PAN, STEEL, WOOD = (218, 112, 40), (98, 60, 34), (46, 46, 52), (170, 175, 182), (150, 105, 60)


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(a, b, t0, t1, t):
    s = clamp((t - t0) / (t1 - t0))
    s = s * s * (3 - 2 * s)
    return a + (b - a) * s


def rot(p, deg, o=(0, 0)):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    x, y = p[0] - o[0], p[1] - o[1]
    return (o[0] + x * c - y * s, o[1] + x * s + y * c)


def circ(c, r, n=28, ry=None, ang=0):
    ry = r if ry is None else ry
    return [rot((c[0] + r * math.cos(2 * math.pi * i / n), c[1] + ry * math.sin(2 * math.pi * i / n)), ang, c) for i in range(n)]


def rock_shape(seed, r, flat=1.0):
    rnd = random.Random(seed)
    return [(r * rnd.uniform(0.8, 1.1) * math.cos(2 * math.pi * i / 9), flat * r * rnd.uniform(0.8, 1.1) * math.sin(2 * math.pi * i / 9))
            for i in range(9)]


# ---------------------------------------------------------------- timeline
def rig(t):
    p = {}
    # heels: up 1.5-2.4, down as she topples
    p["heel"] = ease(0, 1, 1.5, 2.4, t) * (1 - ease(0, 1, 4.7, 5.0, t))
    # torso tilt: lean in to reach, back upright, wobble, fall back, sit
    tilt = ease(0, 14, 1.5, 2.6, t) - ease(0, 14, 3.0, 3.4, t)
    if 3.6 <= t < 4.8:
        k = (t - 3.6) / 1.2
        tilt += (3 + 14 * k) * math.sin(2 * math.pi * 2.2 * (t - 3.6)) - 6 * k
    tilt += ease(0, -40, 4.75, 5.35, t) + ease(0, 50, 5.35, 6.0, t)
    if t >= 4.8:  # the wobble value frozen where the fall takes over
        tilt += (3 + 14) * math.sin(2 * math.pi * 2.2 * 1.2) - 6
    p["tilt"] = tilt
    # arms (0 = hanging, 90 = forward, 180 = up)
    arm = ease(20, 75, 0.2, 0.9, t)                         # lifts the stone to the chest
    arm = ease(arm, 128, 1.6, 2.7, t)                       # raises it to the cairn top
    arm = ease(arm, 110, 3.1, 3.5, t)                       # proud, arms half down
    fl = ease(0, 1, 3.6, 3.9, t) * (1 - ease(0, 1, 4.7, 4.9, t))
    armF = arm + fl * 55 * math.sin(2 * math.pi * 3.1 * t)
    armB = arm + fl * 55 * math.sin(2 * math.pi * 3.1 * t + 2.4)
    up = ease(0, 1, 4.8, 5.1, t) * (1 - ease(0, 1, 6.4, 6.9, t))  # arms over the head, then rest
    rest = ease(0, 1, 6.4, 6.9, t)
    p["armF"] = armF * (1 - up - rest) + 168 * up + 70 * rest
    p["armB"] = armB * (1 - up - rest) + 158 * up + 55 * rest
    # legs: front leg kicks up on the wobble, both go forward as she sits
    kick = ease(0, 1, 4.1, 4.5, t) * (1 - ease(0, 1, 4.9, 5.2, t))
    sit = ease(0, 1, 4.85, 5.45, t)
    p["legF"] = 30 * kick + 78 * sit
    p["legB"] = -6 * kick + 70 * sit
    stand_y = G - LLEG - FOOT - 22 * p["heel"]
    p["hip"] = (900 - 45 * sit, stand_y * (1 - sit) + (G - 30) * sit)
    p["mouth"] = "smile" if t < 3.75 else ("o" if t < 6.7 else "daze")
    p["eyes"] = "open" if t < 6.65 else ("shut" if t < 7.3 else "open")
    p["stone_held"] = t < 3.0
    p["pack_full"] = t < 5.0
    return p


# ---------------------------------------------------------------- Hilda
def hilda(p):
    """Returns draw ops [(kind, pts, fill, width)] plus key points, all in world coords."""
    hip, tilt = p["hip"], p["tilt"]
    T = lambda q: rot((hip[0] + q[0], hip[1] + q[1]), tilt, hip)
    ops, key = [], {}

    def poly(pts, fill, w=4):
        ops.append(("poly", [T(q) for q in pts], fill, w))

    def leg(angle, back):
        a = math.radians(angle)
        top = (hip[0] + (-14 if back else 14), hip[1] + 6)
        knee_len = LLEG * 0.55
        mid = (top[0] + knee_len * math.sin(a), top[1] + knee_len * math.cos(a))
        ank = (top[0] + LLEG * math.sin(a), top[1] + LLEG * math.cos(a))
        n = (math.cos(a) * 16, -math.sin(a) * 16)
        ops.append(("poly", [(top[0] - n[0], top[1] - n[1]), (top[0] + n[0], top[1] + n[1]), (mid[0] + n[0], mid[1] + n[1]),
                             (mid[0] - n[0], mid[1] - n[1])], TROUS if not back else (92, 66, 44), 4))
        m = (math.cos(a) * 12, -math.sin(a) * 12)
        ops.append(("poly", [(mid[0] - m[0], mid[1] - m[1]), (mid[0] + m[0], mid[1] + m[1]), (ank[0] + m[0], ank[1] + m[1]),
                             (ank[0] - m[0], ank[1] - m[1])], SKIN, 4))
        fa = -angle + 65 * p["heel"]   # foot along the ground, tipped down on tiptoe
        ops.append(("poly", circ(rot((ank[0] + 20, ank[1] + 4), fa + 90 - angle if False else fa, ank), 30, ry=11, ang=fa), SKIN, 4))

    def arm(angle, back):
        sh = (6 if back else 14, -104)
        a = math.radians(angle)
        hand = (sh[0] + 108 * math.sin(a), sh[1] + 108 * math.cos(a))
        n = (math.cos(a) * 13, -math.sin(a) * 13)
        poly([(sh[0] - n[0], sh[1] - n[1]), (sh[0] + n[0], sh[1] + n[1]), (hand[0] + n[0], hand[1] + n[1]),
              (hand[0] - n[0], hand[1] - n[1])], TUNIC if not back else (84, 112, 62))
        poly(circ(hand, 15), SKIN)
        return T(hand)

    leg(p["legB"], True)
    key["handB"] = arm(p["armB"], True)
    # pack, rocks and pan behind her
    poly([(-128, -158), (-30, -158), (-34, 4), (-120, 4)], PACK)
    if p["pack_full"]:
        key["pack_rocks"] = []
        for i, (x, y, r) in enumerate([(-118, -170, 24), (-80, -176, 26), (-44, -168, 22), (-100, -200, 22), (-62, -204, 24),
                                       (-82, -226, 20), (-128, -192, 16)]):
            poly([(x + q[0], y + q[1]) for q in rock_shape(100 + i, r)], ROCK)
            key["pack_rocks"].append((T((x, y)), r))
    poly(circ((-134, -70), 24), PAN)
    poly([(-140, -96), (-128, -96), (-128, -132), (-140, -132)], PAN)
    leg(p["legF"], False)
    # body: tunic, zigzag, belt, pouch, axe
    poly([(-46, 22), (50, 22), (40, -122), (-36, -122)], TUNIC)
    zz = [(-46 + 12 * i, 14 if i % 2 else 4) for i in range(9)]
    ops.append(("line", [T(q) for q in zz], (214, 170, 90), 4))
    poly([(-44, -12), (48, -12), (48, 2), (-44, 2)], BELT)
    poly([(-26, -6), (-2, -6), (-2, 26), (-26, 26)], (122, 76, 44))
    poly([(22, -8), (30, -8), (30, 52), (22, 52)], WOOD)
    poly([(14, 34), (40, 30), (44, 58), (12, 56)], STEEL)
    # head
    head = (8, -172)
    key["head_top"] = T((head[0], head[1] - 86))
    poly(circ(head, 52), SKIN)
    poly(circ((56, -166), 11), SKIN)
    if p["eyes"] == "open":
        r = 7 if p["mouth"] == "o" else 5
        poly(circ((32, -180), r), INK, 0)
    else:
        ops.append(("line", [T((24, -180)), T((40, -180))], INK, 4))
    if p["mouth"] == "smile":
        ops.append(("line", [T((30, -150)), T((38, -146)), T((46, -150))], INK, 4))
    elif p["mouth"] == "o":
        poly(circ((40, -148), 9, ry=11), INK, 0)
    else:
        ops.append(("line", [T((28, -148)), T((34, -152)), T((40, -146)), T((46, -150))], INK, 4))
    for f in [(22, -164), (30, -160), (38, -164), (14, -158)]:
        poly(circ(f, 2.2, n=8), (196, 110, 70), 0)
    poly(circ((-6, -170), 9, ry=12), SKIN)                      # ear
    # beanie and braid
    poly([(-50, -186), (60, -186), (52, -226), (22, -256), (-26, -250), (-48, -220)], BEANIE)
    poly([(-52, -200), (62, -200), (62, -184), (-52, -184)], (160, 40, 34))
    braid = [(-20, -150), (-14, -126), (-22, -104), (-14, -84)]
    ops.append(("line", [T(q) for q in braid], BRAID, 16))
    key["handF"] = arm(p["armF"], False)
    if p["stone_held"]:
        key["stone"] = (key["handF"][0] - 4, key["handF"][1] - 22)
    return ops, key


# ---------------------------------------------------------------- the cairn and the falling stones
P30 = hilda(rig(2.99))[1]
TOP = P30["stone"]                    # where the stone is set down
N, CS_H = 10, (G - (TOP[1] + 14)) / 10
BASE_X = TOP[0] + 110
CAIRN = []                             # (centre, half-width, half-height, seed)
for i in range(N):
    k = i / (N - 1)
    y = G - CS_H * (i + 0.5)
    CAIRN.append(((BASE_X + (TOP[0] - BASE_X) * k + random.Random(i).uniform(-8, 8), y), 100 - 52 * k, CS_H / 2 + 2, i))
PLACED = (TOP, 52, 13, 99)
FALL_FROM = 5                          # stones 5.. fall, plus the placed one

END = hilda(rig(DUR))[1]
endhip = rig(DUR)["hip"]
HEAP = []
for row, (n, y) in enumerate([(5, G - 16), (4, G - 42), (3, G - 68)]):
    for j in range(n):
        HEAP.append((endhip[0] - 40 + row * 30 + j * 62 + random.Random(row * 10 + j).uniform(-10, 10), y))

FLYERS = []   # dict(start time, start pos fn, end, dur, bump, shape, fill, spin)
P49 = hilda(rig(4.99))[1]
slots = iter(HEAP)
for i in range(FALL_FROM, N):
    c, hw, hh, sd = CAIRN[i]
    FLYERS.append(dict(t0=4.62 + 0.06 * (i - FALL_FROM), src=("cairn", i), end=next(slots), dur=0.55, bump=30,
                       shape=circ((0, 0), hw * 0.6, ry=hh), spin=random.Random(sd).uniform(-200, 200)))
for j, (pt, r) in enumerate(P49["pack_rocks"]):
    FLYERS.append(dict(t0=5.0 + 0.04 * j, src=("pt", pt), end=next(slots), dur=0.7, bump=140,
                       shape=rock_shape(100 + j, r), spin=random.Random(j).uniform(-300, 300)))
FLYERS.append(dict(t0=5.1, src=("placed",), end=(END["head_top"][0], END["head_top"][1] + 4), dur=1.5, bump=260,
                   shape=circ((0, 0), 52, ry=13), spin=360))


def sway(t, i):
    """The cairn's top stones lean with Hilda's wobble."""
    if t < 3.6 or i < 3:
        return 0.0
    k = clamp((t - 3.6) / 1.0)
    return (i - 2) * 2.2 * k * math.sin(2 * math.pi * 2.2 * (t - 3.6) - 0.6)


def cairn_pos(t, i):
    c, hw, hh, sd = CAIRN[i]
    return (c[0] + sway(t, i) * 3, c[1]), sway(t, i)


def flyer_pos(f, t):
    s = clamp((t - f["t0"]) / f["dur"])
    if f["src"][0] == "cairn":
        (x0, y0), a0 = cairn_pos(f["t0"], f["src"][1])
    elif f["src"][0] == "placed":
        x0, y0 = PLACED[0][0] + sway(f["t0"], N) * 3, PLACED[0][1]
        a0 = sway(f["t0"], N)
    else:
        (x0, y0), a0 = f["src"][1], 0
    x1, y1 = f["end"]
    x = x0 + (x1 - x0) * s
    y = y0 + (y1 - y0) * s * s - f["bump"] * 4 * s * (1 - s)
    return (x, y), a0 + f["spin"] * s


# ---------------------------------------------------------------- frames
def frame(t):
    im = Image.new("RGB", (W * SS, H * SS), SKY)
    d = ImageDraw.Draw(im)

    CX, CY, Z = 1010, 690, 2.0
    cam = lambda x, y: (((x - CX) * Z + W / 2) * SS, ((y - CY) * Z + H / 2) * SS)

    def poly(pts, fill, w=4, screen=False):
        d.polygon([(x * SS, y * SS) if screen else cam(x, y) for x, y in pts], fill=fill, outline=INK if w else None, width=w * SS if w else 0)

    def line(pts, col, w):
        d.line([cam(x, y) for x, y in pts], fill=col, width=w * SS, joint="curve")

    # hills and ground
    poly([(0, 760)] + [(x, 760 - 60 * math.sin(x / 300) - 30 * math.sin(x / 130)) for x in range(0, W + 1, 40)] + [(W, H), (0, H)], (176, 192, 170), 0, True)
    poly([(0, 956), (W, 962), (W, H), (0, H)], GRASS, 0, True)
    p = rig(t)
    falling = {f["src"][1] for f in FLYERS if f["src"][0] == "cairn" and t >= f["t0"]}
    for i in range(N):
        if i in falling:
            continue
        (x, y), a = cairn_pos(t, i)
        poly(circ((x, y), CAIRN[i][1], ry=CAIRN[i][2], ang=a), (128 + (i * 37) % 30, 126 + (i * 23) % 26, 122))
    placed_flying = any(f["src"][0] == "placed" and t >= f["t0"] for f in FLYERS)
    if t >= 3.0 and not placed_flying:
        a = sway(t, N)
        poly(circ((PLACED[0][0] + a * 3, PLACED[0][1]), 52, ry=13, ang=a), (140, 138, 132))
    ops, key = hilda(p)
    for kind, pts, fill, w in ops:
        poly(pts, fill, w) if kind == "poly" else line(pts, fill, w)
    if p["stone_held"]:
        poly(circ(key["stone"], 52, ry=13, ang=-6), (140, 138, 132))
    for f in FLYERS:
        if t >= f["t0"]:
            (x, y), a = flyer_pos(f, t)
            fill = (140, 138, 132) if f["src"][0] == "placed" else ROCK
            poly([rot((x + q[0], y + q[1]), a, (x, y)) for q in f["shape"]], fill)
    if False:  # dust puffs
        k = (t - 5.4) / 1.5
        for j in range(6):
            r = 10 + 26 * k
            cx = endhip[0] - 40 + j * 55
            poly(circ((cx, G - 30 - 40 * k + 10 * (j % 2)), r), (228, 222, 206) if k < 0.7 else (214, 224, 222), 0)
    return im.resize((W, H), Image.LANCZOS)


if __name__ == "__main__":
    out = sys.argv[1]
    if out.endswith(".png"):   # one still per second, for checking
        sheet = Image.new("RGB", (W // 4 * 3, H // 4 * 3), "white")
        for k, t in enumerate([0.5, 2.0, 2.9, 4.0, 4.4, 5.0, 5.4, 6.2, 7.6]):
            sheet.paste(frame(t).resize((W // 4, H // 4)), ((k % 3) * W // 4, (k // 3) * H // 4))
        sheet.save(out)
    else:
        import imageio.v2 as imageio
        with imageio.get_writer(out, fps=FPS, codec="libx264", quality=8, macro_block_size=8) as w:
            for n in range(int(DUR * FPS)):
                w.append_data(__import__("numpy").asarray(frame(n / FPS)))
        print("Saved", out)
