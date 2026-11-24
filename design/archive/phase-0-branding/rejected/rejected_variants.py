"""Rejected and experimental Phase 0 variants, preserved for reference.

These designs were explored during Phase 0 and replaced before the concepts were
presented. They were never committed at the time; this script reconstructs them
from the exact geometry used during the session so they are not lost.

    python3 rejected_variants.py   (writes SVGs + sheet.html next to this file)
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
from concepts import f, mask_open, GAP, LEAF  # noqa: E402
import svgkit  # noqa: E402


# ---------------- 01 Trackway v1: concentric rings with an aligned channel
def trackway_v1(c, uid, simple=False):
    radii, sw, core, ch, dot = [40, 27.5, 15], 8.5, 5.4, 13.5, 4.7
    m = mask_open(uid, "ch") + (f'<rect x="50" y="{f(50 - ch / 2)}" width="70" height="{f(ch)}" '
                                f'transform="rotate(-45 50 50)" fill="#000"/></mask>')
    rings = "".join(f'<circle cx="50" cy="50" r="{r}" fill="none" stroke="{c[k]}" stroke-width="{sw}"/>'
                    for r, k in zip(radii, ["r1", "r2", "r3"]))
    dx, dy = 50 + 40 * math.cos(math.radians(45)), 50 - 40 * math.sin(math.radians(45))
    return (f'<defs>{m}</defs><g mask="url(#{uid}-ch)">{rings}</g><circle cx="50" cy="50" r="{core}" fill="{c["core"]}"/>'
            f'<circle cx="{f(dx)}" cy="{f(dy)}" r="{dot}" fill="{c["dot"]}"/>')


# ---------------- 01 Trackway v2: eccentric "ripple gate"
def trackway_v2(c, uid, simple=False):
    radii, offs, sw, ch, dot = [40, 27, 14], [0, 4.6, 9.2], 7.6, 12.5, 4.9
    ux, uy = math.cos(math.radians(45)), -math.sin(math.radians(45))
    cx0, cy0 = 50 + 2.2 * ux, 50 + 2.2 * uy
    centers = [(cx0 - o * ux, cy0 - o * uy) for o in offs]
    ix, iy = centers[-1]
    m = mask_open(uid, "ch") + (f'<rect x="{f(ix)}" y="{f(iy - ch / 2)}" width="80" height="{f(ch)}" '
                                f'transform="rotate(-45 {f(ix)} {f(iy)})" fill="#000"/></mask>')
    rings = "".join(f'<circle cx="{f(x)}" cy="{f(y)}" r="{r}" fill="none" stroke="{c[k]}" stroke-width="{sw}"/>'
                    for (x, y), r, k in zip(centers, radii, ["r1", "r2", "r3"]))
    return (f'<defs>{m}</defs><g mask="url(#{uid}-ch)">{rings}</g>'
            f'<circle cx="{f(ix)}" cy="{f(iy)}" r="{f((14 - sw / 2) * 0.52)}" fill="{c["core"]}"/>'
            f'<circle cx="{f(cx0 + 40 * ux)}" cy="{f(cy0 + 40 * uy)}" r="{dot}" fill="{c["dot"]}"/>')


# ---------------- 01 Beyond v1: nine dots with the box drawn
def beyond_boxed(c, uid, simple=False):
    g, o, sw, dot, pad = 25, 14.5, 5.4, 6.2, 10.5
    P = lambda i, j: (o + i * g, o + j * g)
    d = "M" + "L".join(f"{f(x)} {f(y)}" for x, y in [P(0, 0), P(3, 0), P(0, 3), P(0, 0), P(2, 2)])
    x0, x1 = o - pad, o + 2 * g + pad
    m = mask_open(uid, "bx") + (f'<path d="{d}" fill="none" stroke="#000" stroke-width="{f(sw + 2 * GAP)}" '
                                f'stroke-linejoin="round" stroke-linecap="round"/></mask>')
    out = (f'<defs>{m}</defs><rect x="{f(x0)}" y="{f(x0)}" width="{f(x1 - x0)}" height="{f(x1 - x0)}" rx="9" '
           f'fill="none" stroke="{c["box"]}" stroke-width="2.2" mask="url(#{uid}-bx)"/>'
           f'<path d="{d}" fill="none" stroke="{c["line"]}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"/>')
    return out + "".join(f'<circle cx="{f(P(i, j)[0])}" cy="{f(P(i, j)[1])}" r="{dot}" fill="{c["dot"]}"/>'
                         for i in range(3) for j in range(3))


# ---------------- 01 Beyond v2: rotated 45 degrees (read as a tree / arrow)
def beyond_rotated(c, uid, simple=False):
    g, sw, dot, a = 19.5, 5.6, 6.3, math.radians(45)
    pts = [(0, 0), (3 * g, 0), (0, 3 * g), (0, 0), (2 * g, 2 * g)]
    R = lambda x, y: (x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a))
    rp = [R(*p) for p in pts]
    xs, ys = [p[0] for p in rp], [p[1] for p in rp]
    ox, oy = 50 - (min(xs) + max(xs)) / 2, 50 - (min(ys) + max(ys)) / 2
    d = "M" + "L".join(f"{f(x + ox)} {f(y + oy)}" for x, y in rp)
    dots = [R(i * g, j * g) for i in range(3) for j in range(3)]
    return (f'<path d="{d}" fill="none" stroke="{c["line"]}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"/>'
            + "".join(f'<circle cx="{f(x + ox)}" cy="{f(y + oy)}" r="{dot}" fill="{c["dot"]}"/>' for x, y in dots))


# ---------------- 02 Unfolded v1: only one face folding
def unfolded_v1(c, uid, simple=False):
    s, g, r = 20, 3.4, 3.6
    x0, y0 = (100 - (4 * s + 3 * g)) / 2, (100 - (3 * s + 2 * g)) / 2
    out = []
    for name, col, row in [("T", 1, 0), ("L", 0, 1), ("F", 1, 1), ("R", 2, 1), ("D", 2, 2), ("B", 3, 1)]:
        x, y = x0 + col * (s + g), y0 + row * (s + g)
        tr = (f' transform="translate({f(x)} {f(y + s)}) skewY(-13) scale(0.74 1) translate({f(-x)} {f(-(y + s))})"'
              if name == "B" else "")
        out.append(f'<rect x="{f(x)}" y="{f(y)}" width="{s}" height="{s}" rx="{r}" fill="{c[name]}"{tr}/>')
    return "".join(out)


# ---------------- 05 Shear v1: cut line overshooting the disc (read as a planet ring)
def shear_v1(c, uid, simple=False):
    R, d, p = 37, 5.5, 3.4
    return (f'<defs><clipPath id="{uid}-u"><rect width="100" height="50"/></clipPath>'
            f'<clipPath id="{uid}-d"><rect y="50" width="100" height="50"/></clipPath></defs>'
            f'<g transform="rotate(-20 50 50)"><g transform="translate({-d} {-p})"><circle cx="50" cy="50" r="{R}" fill="{c["a"]}" clip-path="url(#{uid}-u)"/></g>'
            f'<g transform="translate({d} {p})"><circle cx="50" cy="50" r="{R}" fill="{c["b"]}" clip-path="url(#{uid}-d)"/></g>'
            f'<rect x="4" y="48.8" width="92" height="2.4" rx="1.2" fill="{c["cut"]}"/></g>')


# ---------------- 06 Loose Leaf v1: dog-eared sheets (read as a generic documents icon)
DOG = "M5 0H33Q38 0 38 -5V-42L26 -54H5Q0 -54 0 -49V-5Q0 0 5 0Z"
FLAP = "M26 -54V-45.5Q26 -42 29.5 -42H38Z"


def leaf_v1(c, uid, simple=False):
    px, py, rots, roles = 47, 83, [-34, -17, 0], ["s3", "s2", "s1"]
    out, defs = [], []
    for i, (rot, role) in enumerate(zip(rots, roles)):
        m = mask_open(uid, f"s{i}")
        for fr in rots[i + 1:]:
            m += (f'<path d="{DOG}" transform="translate({px} {py}) rotate({fr})" fill="#000" stroke="#000" '
                  f'stroke-width="{2 * GAP}" stroke-linejoin="round"/>')
        defs.append(m + "</mask>")
        flap = f'<path d="{FLAP}" fill="{c["flap"]}"/>' if i == 2 else ""
        out.append(f'<g mask="url(#{uid}-s{i})"><g transform="translate({px} {py}) rotate({rot})">'
                   f'<path d="{DOG}" fill="{c[role]}"/>{flap}</g></g>')
    return f'<defs>{"".join(defs)}</defs>' + "".join(out)


# ---------------- 08 Interlink v1: narrow links (read as a psi / bars)
def interlink_v1(c, uid, simple=False):
    sw = 11
    m_n = mask_open(uid, "n") + f'<line x1="58" y1="12" x2="58" y2="32" stroke="#000" stroke-width="{sw + 2 * GAP}"/></mask>'
    m_u = mask_open(uid, "u") + f'<line x1="42" y1="68" x2="42" y2="88" stroke="#000" stroke-width="{sw + 2 * GAP}"/></mask>'
    return (f'<defs>{m_n}{m_u}</defs>'
            f'<path d="M22 8V60A18 18 0 0 0 58 60V8" fill="none" stroke-width="{sw}" stroke="{c["u"]}" mask="url(#{uid}-u)"/>'
            f'<path d="M42 92V40A18 18 0 0 1 78 40V92" fill="none" stroke-width="{sw}" stroke="{c["n"]}" mask="url(#{uid}-n)"/>')


GRAPHITE = ("#2C3338", "#16191C")
VARIANTS = [
    ("01-trackway-v1", "Trackway v1", "Concept 01 (first idea)", trackway_v1, GRAPHITE,
     dict(r1="#EEF3F1", r2="#A3B1AD", r3="#5E6B69", core="#5FE3B0", dot="#5FE3B0"),
     "Concentric rings with a channel cut through them. Read as a target or radar icon, so the idea was replaced."),
    ("01-trackway-v2", "Trackway v2", "Concept 01 (second attempt)", trackway_v2, GRAPHITE,
     dict(r1="#EEF3F1", r2="#A3B1AD", r3="#5E6B69", core="#5FE3B0", dot="#5FE3B0"),
     "Eccentric 'ripple gate' rings. Still read as a target; replaced by the nine-dot Beyond concept."),
    ("01-beyond-boxed", "Beyond, boxed", "Concept 01 exploration", beyond_boxed, ("#2C3338", "#15181B"),
     dict(line="#EEF3F1", dot="#5FE3B0", box="#55615F"),
     "Nine-dot solution with the box drawn. The box knockouts left fragments and the drawing was too busy."),
    ("01-beyond-rotated", "Beyond, rotated", "Concept 01 exploration", beyond_rotated, ("#2C3338", "#15181B"),
     dict(line="#5FE3B0", dot="#EEF3F1"),
     "Same solution rotated 45 degrees. Symmetric, but read as a tree or an arrow."),
    ("02-unfolded-v1", "Unfolded v1", "Concept 02 (first version)", unfolded_v1, ("#1C3060", "#0A1530"),
     dict(T="#6F8CCB", L="#33528F", F="#3DD6EB", R="#33528F", D="#6F8CCB", B="#D3F4FA"),
     "Only one face folding. Read as a plus sign or a game piece; a second folding face was added."),
    ("05-shear-v1", "Shear v1", "Concept 05 (first version)", shear_v1, ("#FBFBFC", "#D3D7DD"),
     dict(a="#25282E", b="#878D97", cut="#FF5A2C"),
     "Cut line overshooting the disc. Read as a planet ring; the line was trimmed flush with the halves."),
    ("06-loose-leaf-v1", "Loose Leaf v1", "Concept 06 (first version)", leaf_v1, ("#2D2846", "#141220"),
     dict(s1="#EEE9FF", s2="#B3A0FF", s3="#7B5CF5", flap="#B3A0FF"),
     "Dog-eared pages. Read as a generic documents icon; replaced with punched binder paper."),
    ("08-interlink-v1", "Interlink v1", "Concept 08 (first version)", interlink_v1, ("#F8F8F6", "#DFE2E0"),
     dict(u="#0B9A8A", n="#FF6B4A"),
     "Narrow, tall links. Read as a psi or two bars rather than 'un'; widened in the final concept."),
]


def main():
    cards, jobs = [], []
    for slug, name, origin, fn, bg, colors, why in VARIANTS:
        concept = dict(num=0, name=name, fn=fn, icon_scale=5.7, icon_tone="dark" if bg[0] < "#8" else "light",
                       icon_bg=bg, ctx=dict(icon=colors))
        d = os.path.join(HERE, slug)
        os.makedirs(d, exist_ok=True)
        icon = svgkit.app_icon_svg(concept, "rj" + slug.replace("-", ""))
        sym = svgkit.svg_doc(fn(colors, "rs" + slug.replace("-", "")), "0 0 100 100", None, None, name)
        for fn_, svg in (("app-icon.svg", icon), ("symbol.svg", sym)):
            with open(os.path.join(d, fn_), "w") as fh:
                fh.write(svg + "\n")
        cards.append(f'<div class="c">{svgkit.app_icon_svg(concept, "rc" + slug.replace("-", ""), size=220)}'
                     f'<b>{name}</b><span>{origin}</span><p>{why}</p></div>')
    html = ('<!doctype html><html><head><meta charset="utf-8"><style>'
            'body{margin:0;background:#E7E8EA;font-family:Inter,system-ui,sans-serif;color:#16181B}'
            '.s{width:2000px;padding:48px}h1{margin:0 0 6px;font-size:40px}.s>p{margin:0 0 28px;color:#5C6169;font-size:18px}'
            '.g{display:grid;grid-template-columns:repeat(4,1fr);gap:20px}.c{background:#fff;border-radius:18px;padding:22px;'
            'display:flex;flex-direction:column;align-items:center;gap:6px;text-align:center}.c b{font-size:22px}'
            '.c span{color:#5C6169;font-size:14px}.c p{font-size:15px;line-height:1.45;margin:6px 0 0}</style></head><body>'
            '<div class="s"><h1>Phase 0 — rejected and experimental variants</h1>'
            '<p>Explored during Phase 0 and replaced before presentation. Preserved for reference only; not part of the UnboundFS identity.</p>'
            f'<div class="g">{"".join(cards)}</div></div></body></html>')
    os.makedirs(os.path.join(HERE, ".build"), exist_ok=True)
    hp = os.path.join(HERE, ".build", "sheet.html")
    with open(hp, "w") as fh:
        fh.write(html)
    jobs.append(dict(html=hp, out=os.path.join(HERE, "rejected-variants.png"), w=2000, h=900, fullPage=True))
    with open(os.path.join(HERE, ".build", "jobs.json"), "w") as fh:
        json.dump(jobs, fh)
    print(f"{len(VARIANTS)} variants written")


if __name__ == "__main__":
    main()
