"""Build the static pixel-art SVGs for the profile README.

Usage: python scripts/build_assets.py   (writes into assets/)
"""
import html
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
from pixelfont import F, text_rects, text_width  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets")
os.makedirs(OUT, exist_ok=True)
random.seed(11)

W = 880


def save(name, parts):
    with open(os.path.join(OUT, name), "w") as f:
        f.write("\n".join(parts))


def px(x, y, s, c, extra=""):
    return f'<rect x="{x}" y="{y}" width="{s}" height="{s}" fill="{c}"{extra}/>'


def sprite(rows, palette, x, y, s):
    out = []
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch in palette:
                out.append(px(x + c * s, y + r * s, s, palette[ch]))
    return out


# ======================================================================
# HEADER — tall title screen with surface world + underground mine
# ======================================================================
def build_header():
    H = 520
    P = 8
    SURFACE = 300
    LOOP = "10s"
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}" shape-rendering="crispEdges">']

    # Cursor path: start -> START button -> grass cube -> diamond ore -> moon -> start
    stops = [  # (percent, x, y)
        (0, 830, 470), (16, 452, 226), (24, 452, 226),
        (38, 96, 176), (46, 96, 176),
        (60, 612, 446), (68, 612, 446),
        (82, 770, 58), (90, 770, 58), (100, 830, 470),
    ]
    cur_kf = "".join(f"{p}%{{transform:translate({x}px,{y}px)}}" for p, x, y in stops)

    def click_kf(name, start):
        a, b, c = start, start + 2, start + 7
        return (f"@keyframes {name}{{0%,{a - 0.1}%{{opacity:0;transform:scale(.3)}}"
                f"{a}%{{opacity:1;transform:scale(.3)}}{c}%{{opacity:0;transform:scale(1.6)}}"
                f"{c + 0.1}%,100%{{opacity:0}}}}")

    s.append("<style>"
             ".tw{animation:tw 3s steps(2) infinite}.tw2{animation:tw 2.2s steps(2) infinite .7s}"
             ".tw3{animation:tw 2.7s steps(2) infinite 1.3s}"
             "@keyframes tw{0%,100%{opacity:1}50%{opacity:.15}}"
             ".cl1{animation:drift 40s linear infinite}.cl2{animation:drift 56s linear infinite -24s}"
             ".cl3{animation:drift 70s linear infinite -45s}"
             "@keyframes drift{from{transform:translateX(-280px)}to{transform:translateX(920px)}}"
             ".bob{animation:bob 2.4s steps(4) infinite}.bob2{animation:bob 2.4s steps(4) infinite -1.2s}"
             "@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}"
             ".walk{animation:walk 16s steps(64) infinite}"
             "@keyframes walk{from{transform:translateX(-40px)}to{transform:translateX(920px)}}"
             ".spark{animation:spark 1.8s steps(2) infinite}.spark2{animation:spark 2.4s steps(2) infinite .9s}"
             "@keyframes spark{0%,100%{opacity:1}50%{opacity:.35}}"
             f".cur{{animation:cur {LOOP} ease-in-out infinite}}@keyframes cur{{{cur_kf}}}"
             f".btnup{{animation:btnup {LOOP} steps(1) infinite}}"
             "@keyframes btnup{0%,16.9%{opacity:1}17%,23%{opacity:0}23.1%,100%{opacity:1}}"
             f".btndn{{animation:btndn {LOOP} steps(1) infinite}}"
             "@keyframes btndn{0%,16.9%{opacity:0}17%,23%{opacity:1}23.1%,100%{opacity:0}}"
             f".c1{{animation:c1 {LOOP} linear infinite;transform-box:fill-box;transform-origin:center}}"
             f".c2{{animation:c2 {LOOP} linear infinite;transform-box:fill-box;transform-origin:center}}"
             f".c3{{animation:c3 {LOOP} linear infinite;transform-box:fill-box;transform-origin:center}}"
             f".c4{{animation:c4 {LOOP} linear infinite;transform-box:fill-box;transform-origin:center}}"
             + click_kf("c1", 17) + click_kf("c2", 39) + click_kf("c3", 61) + click_kf("c4", 83) +
             f".jump{{animation:jump {LOOP} steps(1) infinite}}"
             "@keyframes jump{0%,38.9%{transform:translateY(0)}39%,44%{transform:translateY(-14px)}44.1%,100%{transform:translateY(0)}}"
             f".glow{{animation:glow {LOOP} steps(1) infinite}}"
             "@keyframes glow{0%,60.9%{opacity:0}61%,67%{opacity:1}67.1%,100%{opacity:0}}"
             "</style>")

    # --- sky ------------------------------------------------------------
    bands = ["#0a0f24", "#0f1733", "#152043", "#1b2a55", "#223568", "#2b417c", "#354e90", "#405ca3"]
    s.append(f'<rect width="{W}" height="{H}" fill="{bands[-1]}"/>')
    bh = SURFACE // len(bands) + 1
    for i, c in enumerate(bands):
        s.append(f'<rect y="{i * bh}" width="{W}" height="{bh + 1}" fill="{c}"/>')

    # moon
    mx, my, mr = 770, 58, 4
    for yy in range(-mr, mr + 1):
        for xx in range(-mr, mr + 1):
            if xx * xx + yy * yy <= mr * mr + 1:
                s.append(px(mx + xx * P - 4, my + yy * P - 4, P, "#f4f1c9" if (xx * 3 + yy) % 7 else "#d9d4a3"))

    # stars
    for _ in range(46):
        sx, sy = random.randrange(0, W // 4) * 4, random.randrange(0, 200 // 4) * 4
        if abs(sx - mx) < 56 and abs(sy - my) < 56:
            continue
        s.append(f'<rect class="{random.choice(["tw", "tw2", "tw3", ""])}" x="{sx}" y="{sy}" '
                 f'width="{random.choice([3, 3, 4])}" height="{random.choice([3, 3, 4])}" fill="#fff"/>')

    # clouds
    def cloud(cls, y, shape, op):
        g = [f'<g class="{cls}">']
        for r, row in enumerate(shape):
            for c, ch in enumerate(row):
                if ch == "#":
                    g.append(px(c * P, y + r * P, P, "#e8ecff", f' opacity="{op}"'))
        return g + ["</g>"]
    s += cloud("cl1", 88, ["..####......", ".########...", "###########."], ".85")
    s += cloud("cl2", 150, ["...###....", ".#######..", "#########."], ".7")
    s += cloud("cl3", 40, ["..###...", "#######."], ".5")

    # far mountains (stepped)
    peaks = [(0, 7), (60, 11), (130, 15), (200, 10), (250, 8), (330, 13), (420, 17), (500, 12),
             (560, 9), (640, 14), (720, 18), (790, 12), (880, 9)]
    for (x0, h0), (x1, h1) in zip(peaks, peaks[1:]):
        for x in range(x0, x1, P):
            t = (x - x0) / max(1, (x1 - x0))
            h = round(h0 + (h1 - h0) * t)
            s.append(f'<rect x="{x}" y="{SURFACE - h * P}" width="{P}" height="{h * P}" fill="#1a2a52"/>')
            s.append(f'<rect x="{x}" y="{SURFACE - h * P}" width="{P}" height="{P}" fill="#dfe6ff" opacity=".55"/>' if h >= 15 else "")
    # near hills
    for i, h in enumerate([4, 5, 6, 6, 5, 4, 4, 5, 7, 8, 7, 6, 5, 5, 6, 7, 6, 5, 4, 4, 5, 6]):
        cw = W // 22 + 1
        s.append(f'<rect x="{i * cw}" y="{SURFACE - h * P}" width="{cw}" height="{h * P}" fill="#17394a"/>')

    # pixel trees on the surface
    tree = ["..LLLL..", ".LLLLLL.", "LLLLLLLL", "LLLlLLLL", ".LLLLLL.", "...TT...", "...TT...", "...TT..."]
    for tx in [24, 176, 680, 832]:
        s += sprite(tree, {"L": "#2f8f3a", "l": "#46b04f", "T": "#6b4220"}, tx - 16, SURFACE - 64, 8)

    # --- ground: grass + dirt + stone with ores -------------------------
    B = 40
    grass, dirt = ["#5fb346", "#4e9a37", "#6cc552"], ["#8b5a2b", "#7a4d24", "#9a6633", "#6b4220"]
    stone = ["#7d7d7d", "#6e6e6e", "#8a8a8a", "#747474"]
    for bx in range(0, W, B):
        for row, by in enumerate(range(SURFACE, H, B)):
            for yy in range(0, B, P):
                for xx in range(0, B, P):
                    if row == 0 and yy == 0:
                        col = random.choice(grass)
                    elif row == 0 and yy == P and random.random() < 0.5:
                        col = random.choice(grass)
                    elif row <= 1:
                        col = random.choice(dirt) if random.random() < 0.35 else dirt[0]
                    else:
                        col = random.choice(stone) if random.random() < 0.4 else stone[0]
                    s.append(px(bx + xx, by + yy, P, col))
            s.append(f'<rect x="{bx}" y="{by}" width="{B}" height="{B}" fill="none" stroke="#000" stroke-opacity=".16"/>')

    # ores (clusters of pixels inside stone)
    ores = [("#262626", ""), ("#d8af93", ""), ("#fcee4b", "spark"), ("#5decf5", "spark2"), ("#ff3b3b", "spark")]
    spots = [(64, 400), (152, 456), (248, 416), (336, 472), (424, 472), (520, 456), (612, 446),
             (704, 408), (792, 464), (856, 400), (24, 480), (300, 400)]
    for i, (ox, oy) in enumerate(spots):
        col, cls = ores[i % len(ores)]
        if (ox, oy) == (612, 446):
            col, cls = "#5decf5", "spark2"
        g = [f'<g class="{cls}">'] if cls else []
        for dx, dy in [(0, 0), (8, 0), (0, 8), (16, 8), (8, 16)]:
            g.append(px(ox + dx - 8, oy + dy - 8, 6, col))
        s += g + (["</g>"] if cls else [])
    # extra glow on the diamond the cursor clicks
    s.append('<g class="glow"><rect x="596" y="430" width="32" height="32" fill="#5decf5" opacity=".35"/></g>')

    # cave tunnel with torch
    s.append(f'<rect x="368" y="{SURFACE + 96}" width="120" height="32" fill="#2a2a2a"/>')
    s.append(f'<rect x="368" y="{SURFACE + 96}" width="120" height="6" fill="#1c1c1c"/>')
    s += sprite(["Y", "O", "T", "T"], {"Y": "#ffe066", "O": "#ff9f1a", "T": "#6b4220"}, 380, SURFACE + 100, 6)
    s.append(f'<rect class="tw2" x="372" y="{SURFACE + 96}" width="24" height="18" fill="#ffb347" opacity=".25"/>')

    # isometric floating blocks
    def iso(cx, cy, k, top, left, right, cls):
        h = k / 2
        t = f"{cx},{cy - h} {cx + k},{cy} {cx},{cy + h} {cx - k},{cy}"
        l_ = f"{cx - k},{cy} {cx},{cy + h} {cx},{cy + h + k} {cx - k},{cy + k}"
        r_ = f"{cx + k},{cy} {cx},{cy + h} {cx},{cy + h + k} {cx + k},{cy + k}"
        return [f'<g class="{cls}">', f'<polygon points="{l_}" fill="{left}"/>',
                f'<polygon points="{r_}" fill="{right}"/>', f'<polygon points="{t}" fill="{top}"/>',
                f'<polygon points="{t}" fill="none" stroke="#000" stroke-opacity=".25"/>', "</g>"]
    s.append('<g class="jump">')
    s += iso(96, 168, 26, "#6cc552", "#7a4d24", "#5e3a1b", "bob")
    s.append("</g>")
    s += iso(810, 200, 20, "#7fd8ff", "#3aa6d9", "#2a7fa8", "bob2")
    s += iso(150, 222, 13, "#ffd257", "#e0a92e", "#b8861f", "bob2")

    # --- title ------------------------------------------------------------
    title, tp = "NAHWA KAKAA", 8
    tx, ty = (W - text_width(title, tp)) // 2, 52
    for d, col in [(5, "#141428"), (4, "#1b1b2f"), (3, "#2a2a45"), (2, "#3d3d63"), (1, "#56568a")]:
        s += text_rects(title, tx + d * 2, ty + d * 2, tp, col)
    s += text_rects(title, tx, ty, tp, "#ffe066")
    s += text_rects(title, tx, ty, tp // 2 if False else tp, "#fff3b0", ' opacity="0"')

    sub, sp = "COMPUTER SCIENCE STUDENT @ UMI", 3
    sx = (W - text_width(sub, sp)) // 2
    s += text_rects(sub, sx + 2, 134, sp, "#0a0f24")
    s += text_rects(sub, sx, 132, sp, "#cfe3ff")

    # --- START button (pressed by the cursor) -------------------------
    bw, bh2, bx0, by0 = 280, 52, (W - 280) // 2, 186
    lbl, lp = "PRESS START", 3

    def button(dy, face, shadow, txt):
        g = [f'<rect x="{bx0}" y="{by0 + 6}" width="{bw}" height="{bh2}" fill="#000" opacity=".45"/>' if dy == 0 else "",
             f'<rect x="{bx0}" y="{by0 + dy}" width="{bw}" height="{bh2}" fill="{shadow}"/>',
             f'<rect x="{bx0 + 4}" y="{by0 + dy + 4}" width="{bw - 8}" height="{bh2 - 8}" fill="{face}"/>',
             f'<rect x="{bx0 + 4}" y="{by0 + dy + 4}" width="{bw - 8}" height="4" fill="#fff" opacity=".25"/>']
        lx = bx0 + (bw - text_width(lbl, lp)) // 2
        g += text_rects(lbl, lx, by0 + dy + 16, lp, txt)
        return g
    s.append('<g class="btnup">')
    s += button(0, "#3b82f6", "#1e3a8a", "#ffffff")
    s.append("</g>")
    s.append('<g class="btndn" opacity="0">')
    s += button(6, "#22c55e", "#14532d", "#ffffff")
    s.append("</g>")

    # walking explorer
    hero = ["..####..", "..#ee#..", "..####..", ".bbbbbb.", "b.bbbb.b", "..bbbb..", "..l..l..", "..l..l.."]
    s.append(f'<g class="walk"><g transform="translate(0,{SURFACE - 32})">')
    s += sprite(hero, {"#": "#f2c38b", "e": "#1b1b2f", "b": "#3b82f6", "l": "#1e3a8a"}, 0, 0, 4)
    s.append("</g></g>")

    # click rings
    for cls, (x, y) in zip(["c1", "c2", "c3", "c4"], [(452, 226), (96, 176), (612, 446), (770, 58)]):
        s.append(f'<rect class="{cls}" x="{x - 18}" y="{y - 18}" width="36" height="36" fill="none" '
                 f'stroke="#ffffff" stroke-width="4" opacity="0"/>')

    # animated pixel cursor (generic arrow pointer)
    arrow = ["K...........", "KK..........", "KWK.........", "KWWK........", "KWWWK.......",
             "KWWWWK......", "KWWWWWK.....", "KWWWWWWK....", "KWWWWWWWK...", "KWWWWWWWWK..",
             "KWWWWWKKKKK.", "KWWKWWK.....", "KWK.KWWK....", "KK..KWWK....", "K....KWWK...",
             ".....KWWK...", "......KK...."]
    s.append('<g class="cur" transform="translate(470,236)">')
    s += sprite(arrow, {"K": "#000000", "W": "#ffffff"}, 0, 0, 2)
    s.append("</g>")

    s.append("</svg>")
    save("header.svg", s)


# ======================================================================
# HOTBAR (inventory)
# ======================================================================
def build_hotbar():
    items = [("C++", "#659ad2"), ("JAVA", "#e76f00"), ("PHP", "#8892bf"), ("PY", "#ffd43b"),
             ("HTML", "#e34f26"), ("CSS", "#264de4"), ("JS", "#f7df1e"), ("LRVL", "#ff2d20"), ("TW", "#38bdf8")]
    n, gap = len(items), 6
    SW = (W - 24 - (n - 1) * gap) // n
    HH = 180
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{HH}" viewBox="0 0 {W} {HH}" shape-rendering="crispEdges">']
    kf = "".join(f"{i * 100 / n:.2f}%,{(i + 1) * 100 / n - .01:.2f}%{{transform:translateX({i * (SW + gap)}px)}}" for i in range(n))
    s.append("<style>.sel{animation:sel 9s steps(1) infinite}@keyframes sel{" + kf + "}"
             ".xp{animation:xp 4s steps(24) infinite alternate}@keyframes xp{from{width:40px}to{width:" + str(W - 150) + "px}}"
             ".hb{animation:hb 1.6s steps(1) infinite}@keyframes hb{0%,85%{transform:translateY(0)}86%,100%{transform:translateY(-3px)}}</style>")
    s.append(f'<rect width="{W}" height="{HH}" fill="#0d1117"/>')
    heart = ["0110110", "1111111", "1111111", "0111110", "0011100", "0001000"]
    for hi in range(10):
        hx, full = 12 + hi * 30, hi < 9
        s.append(f'<g class="{"hb" if hi % 3 == 0 else ""}">')
        for r, row in enumerate(heart):
            for c, ch in enumerate(row):
                if ch == "1":
                    s.append(px(hx + c * 3, 14 + r * 3, 3, "#ff3b3b" if full else "#4a1a1a"))
        s.append("</g>")
    hunger = ["0011100", "0111110", "1111111", "1111111", "0111110", "0010100"]
    for hi in range(10):
        hx = W - 12 - (hi + 1) * 30 + 9
        for r, row in enumerate(hunger):
            for c, ch in enumerate(row):
                if ch == "1":
                    s.append(px(hx + c * 3, 14 + r * 3, 3, "#c98a3a" if hi < 8 else "#3a2a1a"))
    s += text_rects("XP", 12, 50, 2, "#7CFC00")
    s.append(f'<rect x="40" y="48" width="{W - 150}" height="12" fill="#1f2a1f" stroke="#000" stroke-width="2"/>')
    s.append('<rect class="xp" x="40" y="48" width="40" height="12" fill="#7CFC00"/>')
    s += text_rects("LV UP", W - 72, 50, 2, "#7CFC00")
    by = 76
    gem = ["..####..", ".######.", "########", "########", ".######.", "..####.."]
    for i, (label, col) in enumerate(items):
        x0 = 12 + i * (SW + gap)
        s.append(f'<rect x="{x0}" y="{by}" width="{SW}" height="{SW}" fill="#8b8b8b"/>')
        s.append(f'<rect x="{x0 + 4}" y="{by + 4}" width="{SW - 8}" height="{SW - 8}" fill="#3a3a3a"/>')
        gx = x0 + (SW - 32) // 2
        for r, row in enumerate(gem):
            for c, ch in enumerate(row):
                if ch == "#":
                    shine = r < 2 and c < 4
                    s.append(px(gx + c * 4, by + 12 + r * 4, 4, "#ffffff" if shine else col, ' opacity=".55"' if shine else ""))
        lx = x0 + (SW - text_width(label, 2)) // 2
        s += text_rects(label, lx + 1, by + 49, 2, "#000")
        s += text_rects(label, lx, by + 48, 2, "#fff")
    s.append(f'<g class="sel"><rect x="9" y="{by - 3}" width="{SW + 6}" height="{SW + 6}" fill="none" stroke="#fff" stroke-width="4"/></g>')
    s.append("</svg>")
    save("hotbar.svg", s)


# ======================================================================
# Section banners (full width) + footer
# ======================================================================
def build_banners():
    def banner(name, text, color, icon):
        s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="56" viewBox="0 0 {W} 56" shape-rendering="crispEdges">',
             f'<rect y="6" width="{W}" height="44" fill="#0d1117"/>',
             f'<rect y="6" width="{W}" height="4" fill="{color}"/>',
             f'<rect y="46" width="{W}" height="4" fill="{color}" opacity=".45"/>']
        s += sprite(icon, {"#": color, "w": "#ffffff"}, 16, 16, 3)
        s += text_rects(text, 54, 19, 3, "#000")
        s += text_rects(text, 52, 17, 3, color)
        for i in range(6):  # decorative blocks on the right
            s.append(px(W - 24 - i * 18, 20 + (i % 2) * 6, 10, color, f' opacity="{0.9 - i * 0.13:.2f}"'))
        s.append("</svg>")
        save(name, s)
    star = ["...#...", "..###..", "#######", ".#####.", ".##.##.", "#.....#"]
    chest = ["#######", "#wwwww#", "###w###", "#wwwww#", "#wwwww#", "#######"]
    sword = ["......#", ".....#.", "....#..", "#..#...", ".##....", "##.#..."]
    globe = [".#####.", "#.#.#.#", "#######", "#.#.#.#", "#######", ".#####."]
    heart = [".##.##.", "#######", "#######", ".#####.", "..###..", "...#..."]
    gift = ["#######", "###w###", "#######", "#..w..#", "#..w..#", "#######"]
    banner("title-about.svg", "PLAYER INFO", "#ffe066", star)
    banner("title-inventory.svg", "INVENTORY", "#7CFC00", chest)
    banner("title-quests.svg", "QUESTS COMPLETED", "#ff7ab6", sword)
    banner("title-world.svg", "WORLD MAP", "#7fd8ff", globe)
    banner("title-stats.svg", "PLAYER STATS", "#ffa94d", heart)
    banner("title-chest.svg", "BONUS LOOT", "#c792ea", gift)

    # footer strip
    H = 110
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" shape-rendering="crispEdges">',
         "<style>.bl{animation:bl 1.2s steps(1) infinite}@keyframes bl{0%,60%{opacity:1}61%,100%{opacity:0}}</style>",
         f'<rect width="{W}" height="{H}" fill="#0d1117"/>']
    for bx in range(0, W, 8):
        s.append(px(bx, 78, 8, random.choice(["#5fb346", "#4e9a37", "#6cc552"])))
        s.append(px(bx, 86, 8, random.choice(["#8b5a2b", "#7a4d24", "#8b5a2b"])))
        s.append(px(bx, 94, 8, "#8b5a2b"))
        s.append(px(bx, 102, 8, random.choice(["#7a4d24", "#6b4220"])))
    msg = "GAME SAVED - THANKS FOR PLAYING!"
    mx = (W - text_width(msg, 3)) // 2
    s += text_rects(msg, mx + 2, 30, 3, "#000")
    s += text_rects(msg, mx, 28, 3, "#ffe066")
    s.append('<g class="bl">')
    s += text_rects("> CONTINUE", (W - text_width("> CONTINUE", 2)) // 2, 56, 2, "#cfe3ff")
    s.append("</g></svg>")
    save("footer.svg", s)


# ======================================================================
# Quest cards (one SVG per project, linked from the README)
# ======================================================================
QUESTS = [
    ("skrining-tb", "SKRINING TB WEB", "Web-based tuberculosis screening", "WEB", "#ff6b6b",
     ["...##...", "...##...", "########", "########", "...##...", "...##..."]),
    ("sar-inventory", "SAR INVENTORY", "Inventory system for SAR equipment", "WEB", "#ffa94d",
     ["########", "#..##..#", "########", "#......#", "#......#", "########"]),
    ("voting", "VOTING DISTRIBUSI", "Voting app for Distributed Systems", "DISTRIBUTED", "#7fd8ff",
     ["..####..", "..#..#..", "########", "#......#", "#......#", "########"]),
    ("smartabsen", "SMARTABSEN WEB", "Smart attendance web application", "WEB", "#7CFC00",
     [".######.", "#..#...#", "#..#...#", "#..###.#", "#......#", ".######."]),
    ("laportuntas", "LAPORTUNTAS UI/UX", "Public report platform UI (Figma)", "UI/UX", "#5b8cff",
     ["......##", "...#####", "########", "########", "...#####", "......##"]),
    ("pengenalan", "PENGENALAN PEMROGRAMAN", "C++ practicum labs & evaluations", "C++", "#ffe066",
     [".......#", "......#.", ".....#..", "#...#...", ".###....", "##.#...."]),
]


def build_cards():
    CW, CH = 430, 150
    for slug, title, desc, tag, color, icon in QUESTS:
        s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{CW}" height="{CH}" viewBox="0 0 {CW} {CH}" shape-rendering="crispEdges">',
             "<style>.sh{animation:sh 3s steps(1) infinite}@keyframes sh{0%,80%{opacity:0}81%,100%{opacity:1}}"
             ".t{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}</style>",
             f'<rect width="{CW}" height="{CH}" fill="{color}"/>',
             f'<rect x="4" y="4" width="{CW - 8}" height="{CH - 8}" fill="#0d1117"/>',
             f'<rect x="4" y="4" width="{CW - 8}" height="4" fill="#ffffff" opacity=".08"/>']
        # icon slot
        s.append('<rect x="20" y="22" width="64" height="64" fill="#3a3a3a"/>')
        s.append(f'<rect x="20" y="22" width="64" height="4" fill="{color}" opacity=".6"/>')
        s += sprite(icon, {"#": color}, 28, 36, 6)
        # title (pixel font) — shrink if long
        tp = 2 if text_width(title, 2) <= CW - 120 else 1
        s += text_rects(title, 101, 33, tp, "#000")
        s += text_rects(title, 100, 32, tp, "#ffffff")
        s.append(f'<text class="t" x="100" y="70" font-size="14" fill="#9aa4b2">{html.escape(desc)}</text>')
        # tag + status
        tw = len(tag) * 9 + 20
        s.append(f'<rect x="100" y="86" width="{tw}" height="22" fill="{color}" opacity=".18"/>')
        s.append(f'<text class="t" x="110" y="102" font-size="13" font-weight="700" fill="{color}">{tag}</text>')
        s += text_rects("QUEST COMPLETE", 100, 124, 2, "#7CFC00")
        s += text_rects("+XP", CW - 60, 124, 2, "#ffe066")
        # shine on the corner
        s.append(f'<rect class="sh" x="{CW - 30}" y="18" width="10" height="10" fill="#ffffff" opacity=".8"/>')
        s.append("</svg>")
        save(f"quest-{slug}.svg", s)


if __name__ == "__main__":
    build_header()
    build_hotbar()
    build_banners()
    build_cards()
    print("assets built")
