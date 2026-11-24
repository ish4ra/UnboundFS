"""UnboundFS Phase 0 brand concepts: geometry and palettes.

Every symbol is drawn on a 100 x 100 unit canvas. Each symbol function
returns SVG markup and takes:
    c    -- dict of colour roles for the context (icon / light / dark / mono)
    uid  -- unique prefix for mask and clip ids, so several symbols can be
            inlined into one HTML document without id collisions
    simple -- reduced-detail variant used for the menu bar template
"""
import math

GAP = 2.6  # standard knockout gap, in symbol units


def f(v):
    """Compact number formatting for SVG output."""
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def mask_open(uid, name):
    return (f'<mask id="{uid}-{name}" maskUnits="userSpaceOnUse" x="-20" y="-20" '
            f'width="140" height="140"><rect x="-20" y="-20" width="140" height="140" fill="#fff"/>')


# --------------------------------------------------------------------------
# 01 Beyond  (the nine-dot puzzle: solvable only by leaving the box)
# --------------------------------------------------------------------------
def sym_beyond(c, uid, simple=False):
    g = 24 if not simple else 27
    o = 50 - 1.5 * g
    sw = 5.6 if not simple else 8.4
    dot = 6.3 if not simple else 6.8
    P = lambda i, j: (o + i * g, o + j * g)
    pts = [P(0, 0), P(3, 0), P(0, 3), P(0, 0), P(2, 2)]
    d = "M" + "L".join(f"{f(x)} {f(y)}" for x, y in pts)
    out = [f'<path d="{d}" fill="none" stroke="{c["line"]}" stroke-width="{f(sw)}" '
           f'stroke-linejoin="round" stroke-linecap="round"/>']
    grid = [(i, j) for i in range(3) for j in range(3)]
    if simple:  # menu bar: keep only the dots that sit off the line's corners
        grid = [(1, 1), (2, 2), (1, 0), (0, 1), (2, 0), (0, 2), (2, 1), (1, 2)]
    for i, j in grid:
        x, y = P(i, j)
        out.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(dot)}" fill="{c["dot"]}"/>')
    return "".join(out)


# --------------------------------------------------------------------------
# 02 Unfolded
# --------------------------------------------------------------------------
def sym_unfolded(c, uid, simple=False):
    s, g, r = 20, 3.4, 3.6
    w, h = 4 * s + 3 * g, 3 * s + 2 * g
    x0, y0 = (100 - w) / 2, (100 - h) / 2
    faces = [("T", 1, 0), ("L", 0, 1), ("F", 1, 1), ("R", 2, 1), ("D", 2, 2), ("B", 3, 1)]
    out = []
    for name, col, row in faces:
        x, y = x0 + col * (s + g), y0 + row * (s + g)
        tr = ""
        if name == "B" and not simple:
            # faces still folding flat: foreshortened and tilted on their hinges
            tr = (f' transform="translate({f(x)} {f(y + s)}) skewY(-16) scale(0.66 1) '
                  f'translate({f(-x)} {f(-(y + s))})"')
        if name == "T" and not simple:
            tr = (f' transform="translate({f(x)} {f(y + s)}) skewX(-18) scale(1 0.7) '
                  f'translate({f(-x)} {f(-(y + s))})"')
        out.append(f'<rect x="{f(x)}" y="{f(y)}" width="{s}" height="{s}" rx="{r}" '
                   f'fill="{c[name]}"{tr}/>')
    return "".join(out)


# --------------------------------------------------------------------------
# 03 Refract
# --------------------------------------------------------------------------
def sym_refract(c, uid, simple=False):
    sw = 10.5 if simple else 8.6
    seam = 51
    xl, xr = 17, 83
    a1, a2 = math.radians(12), math.radians(48)
    rise_l, rise_r = (seam - xl) * math.tan(a1), (xr - seam) * math.tan(a2)
    step = 17 if simple else 15
    n = 2 if simple else 3
    total = (n - 1) * step
    y0 = 50 - (total + rise_l - rise_r) / 2
    paths = []
    for i in range(n):
        y = y0 + i * step
        paths.append(f'M{f(xl)} {f(y + rise_l)}L{seam} {f(y)}L{xr} {f(y - rise_r)}')
    d = "".join(paths)
    defs = (f'<clipPath id="{uid}-l"><rect x="-10" y="-10" width="{seam + 10}" height="120"/></clipPath>'
            f'<clipPath id="{uid}-r"><rect x="{seam}" y="-10" width="70" height="120"/></clipPath>')
    st = f'fill="none" stroke-width="{f(sw)}" stroke-linecap="round" stroke-linejoin="round"'
    seam_line = "" if simple else (
        f'<line x1="{seam}" y1="5" x2="{seam}" y2="95" stroke="{c["seam"]}" stroke-width="1.6" '
        f'stroke-linecap="round"/>')
    return (f'<defs>{defs}</defs>{seam_line}'
            f'<path d="{d}" {st} stroke="{c["left"]}" clip-path="url(#{uid}-l)"/>'
            f'<path d="{d}" {st} stroke="{c["right"]}" clip-path="url(#{uid}-r)"/>')


# --------------------------------------------------------------------------
# 04 Keystone
# --------------------------------------------------------------------------
def _sector(cx, cy, R, r, a0, a1):
    p = lambda rad, a: (cx + rad * math.cos(math.radians(a)), cy + rad * math.sin(math.radians(a)))
    o0, o1, i1, i0 = p(R, a0), p(R, a1), p(r, a1), p(r, a0)
    return (f'M{f(o0[0])} {f(o0[1])}A{f(R)} {f(R)} 0 0 1 {f(o1[0])} {f(o1[1])}'
            f'L{f(i1[0])} {f(i1[1])}A{f(r)} {f(r)} 0 0 0 {f(i0[0])} {f(i0[1])}Z')


def sym_keystone(c, uid, simple=False):
    cx, cy, R, r = 50, 47, 38, 19
    top = 11
    band = (f'M{cx - R} {top + 2.5}Q{cx - R} {top} {cx - R + 2.5} {top}H{cx - r - 2.5}'
            f'Q{cx - r} {top} {cx - r} {top + 2.5}V{cy}'
            f'A{r} {r} 0 0 0 {cx + r} {cy}V{top + 2.5}Q{cx + r} {top} {cx + r + 2.5} {top}'
            f'H{cx + R - 2.5}Q{cx + R} {top} {cx + R} {top + 2.5}V{cy}'
            f'A{R} {R} 0 0 1 {cx - R} {cy}Z')
    key = _sector(cx, cy, R + 4.5, r - 3, 72, 108)
    g = GAP if not simple else 3.6
    m = mask_open(uid, "k")
    cuts = [cy]
    if not simple:
        cuts.append((top + cy) / 2)
    for y in cuts:
        m += f'<rect x="0" y="{f(y - g / 2)}" width="100" height="{f(g)}" fill="#000"/>'
    angles = [36, 144] if simple else [36, 144]
    for a in angles:
        m += (f'<rect x="{cx}" y="{f(cy - g / 2)}" width="60" height="{f(g)}" fill="#000" '
              f'transform="rotate({a} {cx} {cy})"/>')
    m += f'<path d="{key}" fill="#000" stroke="#000" stroke-width="{f(2 * g)}" stroke-linejoin="round"/></mask>'
    return (f'<defs>{m}</defs><path d="{band}" fill="{c["stone"]}" mask="url(#{uid}-k)"/>'
            f'<path d="{key}" fill="{c["key"]}"/>')


# --------------------------------------------------------------------------
# 05 Shear
# --------------------------------------------------------------------------
def sym_shear(c, uid, simple=False):
    R = 37 if not simple else 38
    d = 6.5          # slide along the fault line
    p = 3.4 if not simple else 3.8   # separation across the fault line
    line = "" if simple else (
        f'<rect x="{f(50 - R - d)}" y="48.8" width="{f(2 * (R + d))}" height="2.4" rx="1.2" fill="{c["cut"]}"/>')
    return (f'<defs><clipPath id="{uid}-u"><rect x="0" y="0" width="100" height="50"/></clipPath>'
            f'<clipPath id="{uid}-d"><rect x="0" y="50" width="100" height="50"/></clipPath></defs>'
            f'<g transform="rotate(-20 50 50)">'
            f'<g transform="translate({-d} {-p})"><circle cx="50" cy="50" r="{R}" fill="{c["a"]}" clip-path="url(#{uid}-u)"/></g>'
            f'<g transform="translate({d} {p})"><circle cx="50" cy="50" r="{R}" fill="{c["b"]}" clip-path="url(#{uid}-d)"/></g>'
            f'{line}</g>')


# --------------------------------------------------------------------------
# 06 Loose Leaf
# --------------------------------------------------------------------------
LEAF_W, LEAF_H, LEAF_R = 38, 56, 5


def _leaf_path():
    w, h, r = LEAF_W, LEAF_H, LEAF_R
    return (f"M{r} 0H{w - r}Q{w} 0 {w} {-r}V{-(h - r)}Q{w} {-h} {w - r} {-h}"
            f"H{r}Q0 {-h} 0 {-(h - r)}V{-r}Q0 0 {r} 0Z")


LEAF = _leaf_path()


def sym_leaf(c, uid, simple=False):
    """Loose-leaf binder sheets, punched holes and all, fanning free."""
    px, py = 46, 84
    rots = [-40, -20, 0] if not simple else [-34, 0]
    roles = ["s3", "s2", "s1"] if not simple else ["s2", "s1"]
    holes = [] if simple else [-13, -28, -43]
    out, defs = [], []
    for i, (rot, role) in enumerate(zip(rots, roles)):
        front_rots = rots[i + 1:]
        is_front = i == len(rots) - 1
        m = mask_open(uid, f"s{i}")
        for fr in front_rots:
            m += (f'<path d="{LEAF}" transform="translate({px} {py}) rotate({fr})" fill="#000" '
                  f'stroke="#000" stroke-width="{f(2 * GAP)}" stroke-linejoin="round"/>')
        if is_front:
            for hy in holes:
                m += f'<circle cx="{px + 6.5}" cy="{py + hy}" r="2.7" fill="#000"/>'
        m += "</mask>"
        defs.append(m)
        out.append(f'<g mask="url(#{uid}-s{i})"><path d="{LEAF}" transform="translate({px} {py}) '
                   f'rotate({rot})" fill="{c[role]}"/></g>')
    return f'<defs>{"".join(defs)}</defs>' + "".join(out)


# --------------------------------------------------------------------------
# 07 Pathfinder
# --------------------------------------------------------------------------
def rounded_poly(pts, rad):
    d = f"M{f(pts[0][0])} {f(pts[0][1])}"
    for i in range(1, len(pts) - 1):
        (x0, y0), (x1, y1), (x2, y2) = pts[i - 1], pts[i], pts[i + 1]
        l1 = math.hypot(x1 - x0, y1 - y0)
        l2 = math.hypot(x2 - x1, y2 - y1)
        rr = min(rad, l1 / 2, l2 / 2)
        ax, ay = x1 - (x1 - x0) / l1 * rr, y1 - (y1 - y0) / l1 * rr
        bx, by = x1 + (x2 - x1) / l2 * rr, y1 + (y2 - y1) / l2 * rr
        d += f"L{f(ax)} {f(ay)}Q{f(x1)} {f(y1)} {f(bx)} {f(by)}"
    d += f"L{f(pts[-1][0])} {f(pts[-1][1])}"
    return d


def sym_path(c, uid, simple=False):
    if simple:
        u, sw, exit_x = 17, 10, 40
        rel = [(0, 0), (u, 0), (u, u), (-u, u), (-u, -u), (exit_x, -u)]
        ext = u
    else:
        u, sw, exit_x = 12.6, 7.6, 44
        rel = [(0, 0), (u, 0), (u, u), (-u, u), (-u, -u), (2 * u, -u), (2 * u, 2 * u),
               (-2 * u, 2 * u), (-2 * u, -2 * u), (exit_x, -2 * u)]
        ext = 2 * u
    minx, maxx = -ext - sw / 2, exit_x + sw / 2
    ox = 50 - (minx + maxx) / 2
    pts = [(ox + x, 50 + y) for x, y in rel]
    d = rounded_poly(pts, sw * 0.75)
    hx0 = ox + ext + sw * 0.9
    head = (f'<line x1="{f(hx0)}" y1="{f(pts[-1][1])}" x2="{f(pts[-1][0])}" y2="{f(pts[-1][1])}" '
            f'stroke="{c["head"]}" stroke-width="{f(sw)}" stroke-linecap="round"/>')
    start = f'<circle cx="{f(pts[0][0])}" cy="{f(pts[0][1])}" r="{f(sw * 0.78)}" fill="{c["head"]}"/>'
    return (f'<path d="{d}" fill="none" stroke="{c["path"]}" stroke-width="{f(sw)}" '
            f'stroke-linecap="round" stroke-linejoin="round"/>{head}{start}')


# --------------------------------------------------------------------------
# 08 Interlink
# --------------------------------------------------------------------------
def sym_interlink(c, uid, simple=False):
    sw = 11 if not simple else 12.5
    g = GAP if not simple else 3.2
    u = "M20 10V58A20 20 0 0 0 60 58V10"
    n = "M40 90V42A20 20 0 0 1 80 42V90"
    m_n = mask_open(uid, "n") + (
        f'<line x1="60" y1="10" x2="60" y2="32" stroke="#000" stroke-width="{f(sw + 2 * g)}"/></mask>')
    m_u = mask_open(uid, "u") + (
        f'<line x1="40" y1="68" x2="40" y2="90" stroke="#000" stroke-width="{f(sw + 2 * g)}"/></mask>')
    st = f'fill="none" stroke-width="{f(sw)}"'
    return (f'<defs>{m_n}{m_u}</defs>'
            f'<path d="{u}" {st} stroke="{c["u"]}" mask="url(#{uid}-u)"/>'
            f'<path d="{n}" {st} stroke="{c["n"]}" mask="url(#{uid}-n)"/>')


# --------------------------------------------------------------------------
# Concept table
# --------------------------------------------------------------------------
CONCEPTS = [
    dict(
        num=1, slug="beyond", name="Beyond", palette_name="Graphite & Mint",
        fn=sym_beyond, icon_scale=5.6, icon_tone="dark",
        icon_bg=("#2C3338", "#15181B"),
        ctx=dict(
            icon=dict(line="#5FE3B0", dot="#EEF3F1", text="#EEF3F1", text2="#5FE3B0"),
            light=dict(line="#13A673", dot="#1E2326", text="#1E2326", text2="#13A673"),
        ),
        palette=[("Graphite", "#15181B"), ("Graphite 2", "#2C3338"), ("Slate", "#55615F"),
                 ("Mist", "#B9C3C0"), ("Frost", "#EEF3F1"), ("Mint", "#5FE3B0"), ("Mint Deep", "#13A673")],
        font=[("Unbound", "manrope700", "text"), ("FS", "manrope500", "text2")], tracking=-0.01,
        symbolism=("The nine-dot puzzle: join all nine points with four straight lines without lifting "
                   "the pen. It can only be solved by drawing past the edge of the box. Nine blocks of "
                   "storage, one continuous mint line through every one of them, and two corners that sit "
                   "deliberately outside the boundary."),
    ),
    dict(
        num=2, slug="unfolded", name="Unfolded", palette_name="Midnight & Cyan",
        fn=sym_unfolded, icon_scale=5.9, icon_tone="dark",
        icon_bg=("#1C3060", "#0A1530"),
        ctx=dict(
            icon=dict(T="#6F8CCB", L="#33528F", F="#3DD6EB", R="#33528F", D="#6F8CCB", B="#D3F4FA",
                      text="#EAF2FF", text2="#3DD6EB"),
            light=dict(T="#2E4A85", L="#15264D", F="#0BA3BF", R="#15264D", D="#2E4A85", B="#8FA8DD",
                       text="#0B1630", text2="#0BA3BF"),
        ),
        palette=[("Midnight", "#0A1530"), ("Navy", "#15264D"), ("Steel", "#33528F"),
                 ("Periwinkle", "#6F8CCB"), ("Cyan", "#3DD6EB"), ("Cyan Deep", "#0BA3BF"), ("Ice", "#D3F4FA")],
        font=[("Unbound", "sg700", "text"), ("FS", "sg500", "text2")], tracking=-0.015,
        symbolism=("A cube is the usual picture of a volume. Here it is laid open as its six-face net, "
                   "with the last face still folding flat. A sealed container turns into a surface you "
                   "can see and use: the drive opened up, no matter how its box was built."),
    ),
    dict(
        num=3, slug="refract", name="Refract", palette_name="Charcoal & Electric Blue",
        fn=sym_refract, icon_scale=5.6, icon_tone="dark",
        icon_bg=("#272A32", "#111216"),
        ctx=dict(
            icon=dict(left="#E8EBF0", right="#4A86FF", seam="#4A4F5A", text="#E8EBF0", text2="#4A86FF"),
            light=dict(left="#1C1E23", right="#2F6BF0", seam="#C3C8D1", text="#141518", text2="#2F6BF0"),
        ),
        palette=[("Charcoal", "#111216"), ("Carbon", "#272A32"), ("Seam", "#4A4F5A"), ("Ash", "#C3C8D1"),
                 ("Frost", "#E8EBF0"), ("Electric", "#4A86FF"), ("Electric Deep", "#2F6BF0")],
        font=[("Unbound", "interd600", "text"), ("FS", "interd600", "text2")], tracking=-0.02,
        symbolism=("Light bends when it crosses from one medium into another, but it is still the same "
                   "light. Three data lanes cross a hairline boundary and change angle without breaking. "
                   "Different filesystems on either side, one continuous passage through."),
    ),
    dict(
        num=4, slug="keystone", name="Keystone", palette_name="Basalt & Copper",
        fn=sym_keystone, icon_scale=5.7, icon_tone="light",
        icon_bg=("#F4EFE7", "#DED3C3"),
        ctx=dict(
            icon=dict(stone="#2C2724", key="#C4643A", text="#2C2724", text2="#C4643A"),
            dark=dict(stone="#EFE8DE", key="#E08657", text="#EFE8DE", text2="#E08657"),
        ),
        palette=[("Basalt", "#2C2724"), ("Umber", "#5A4F48"), ("Clay", "#DED3C3"), ("Sandstone", "#F4EFE7"),
                 ("Copper", "#C4643A"), ("Copper Light", "#E08657")],
        font=[("Unbound", "outfit600", "text"), ("FS", "outfit400", "text2")], tracking=0.0,
        symbolism=("A U assembled the way stone bridges are: separate voussoir blocks locked in place by a "
                   "keystone. The blocks are storage, the arch is the bridge between platforms, and the "
                   "copper keystone is the piece UnboundFS supplies, the one that makes the whole "
                   "structure hold. A lettermark that carries a story about integrity."),
    ),
    dict(
        num=5, slug="shear", name="Shear", palette_name="Silver & Ember",
        fn=sym_shear, icon_scale=5.9, icon_tone="light",
        icon_bg=("#FBFBFC", "#D3D7DD"),
        ctx=dict(
            icon=dict(a="#25282E", b="#878D97", cut="#FF5A2C", text="#25282E", text2="#FF5A2C"),
            dark=dict(a="#F1F2F4", b="#8C929C", cut="#FF6A3D", text="#F1F2F4", text2="#FF6A3D"),
        ),
        palette=[("Ink", "#121316"), ("Graphite", "#25282E"), ("Steel", "#878D97"), ("Silver", "#D3D7DD"),
                 ("Paper", "#FBFBFC"), ("Ember", "#FF5A2C")],
        font=[("UNBOUND", "inter600", "text"), ("FS", "inter600", "text2")], tracking=0.12,
        symbolism=("A disc, the oldest shorthand for storage, split cleanly along a fault line with its "
                   "two halves slipping past each other. The ember line is the boundary itself, exposed. "
                   "A bold two-piece silhouette that holds up all the way down to 16 px."),
    ),
    dict(
        num=6, slug="loose-leaf", name="Loose Leaf", palette_name="Ink Violet & Vellum",
        fn=sym_leaf, icon_scale=5.7, icon_tone="dark",
        icon_bg=("#2D2846", "#141220"),
        ctx=dict(
            icon=dict(s1="#EEE9FF", s2="#B3A0FF", s3="#7B5CF5", flap="#B3A0FF", text="#EEE9FF", text2="#B3A0FF"),
            light=dict(s1="#232036", s2="#6A50E6", s3="#B9A9FF", flap="#6A50E6", text="#1C1A2B", text2="#6A50E6"),
        ),
        palette=[("Ink Violet", "#141220"), ("Dusk", "#2D2846"), ("Violet", "#7B5CF5"), ("Violet Deep", "#6A50E6"),
                 ("Lilac", "#B3A0FF"), ("Vellum", "#EEE9FF")],
        font=[("Unbound", "fraunces600", "text"), ("FS", "fraunces400", "text2")], tracking=-0.005,
        symbolism=("'Unbound' is a bookbinding word: pages that have left the spine. Three dog-eared leaves "
                   "fan out from one pivot, files released from the format that held them while still "
                   "sharing a single origin. Quiet, literate, and tied directly to the name."),
    ),
    dict(
        num=7, slug="pathfinder", name="Pathfinder", palette_name="Forest & Saffron",
        fn=sym_path, icon_scale=5.7, icon_tone="dark",
        icon_bg=("#184A3E", "#0A1F1A"),
        ctx=dict(
            icon=dict(path="#E6F0EB", head="#F4B637", text="#E6F0EB", text2="#F4B637"),
            light=dict(path="#123A31", head="#D9900F", text="#0E2B24", text2="#D9900F"),
        ),
        palette=[("Forest Ink", "#0A1F1A"), ("Forest", "#123A31"), ("Pine", "#184A3E"), ("Sage", "#9DBDB1"),
                 ("Fog", "#E6F0EB"), ("Saffron", "#F4B637"), ("Saffron Deep", "#D9900F")],
        font=[("Unbound", "jbm700", "text"), ("FS", "jbm500", "text2")], tracking=-0.02,
        symbolism=("A squared spiral is a maze path, and a filesystem is a maze of paths. The line starts "
                   "at a saffron core, winds through every layer and leaves the structure without being "
                   "stopped. A wayfinding mark: from a closed format to an open route."),
    ),
    dict(
        num=8, slug="interlink", name="Interlink", palette_name="Lagoon & Coral",
        fn=sym_interlink, icon_scale=5.7, icon_tone="light",
        icon_bg=("#F8F8F6", "#DFE2E0"),
        ctx=dict(
            icon=dict(u="#0B9A8A", n="#FF6B4A", text="#1D2326", text2="#0B9A8A"),
            dark=dict(u="#2CC7B3", n="#FF7D5E", text="#EEF2F1", text2="#2CC7B3"),
        ),
        palette=[("Ink", "#1D2326"), ("Lagoon Deep", "#087567"), ("Lagoon", "#0B9A8A"), ("Lagoon Light", "#2CC7B3"),
                 ("Coral", "#FF6B4A"), ("Porcelain", "#F8F8F6"), ("Fog", "#DFE2E0")],
        font=[("Un", "sora600", "text2"), ("boundFS", "sora600", "text")], tracking=-0.01,
        symbolism=("A lowercase u and n, the same letterform turned half a revolution, linked like chain "
                   "links with real over-and-under crossings. It spells the 'un' in UnboundFS and shows two "
                   "equal systems holding on to each other: two colours for two platforms, one connection."),
    ),
]


def contexts(concept):
    """Return colour dicts for icon / light / dark / mono-black / mono-white."""
    ctx = dict(concept["ctx"])
    if concept["icon_tone"] == "dark":
        ctx["dark"] = ctx["icon"]
    else:
        ctx["light"] = ctx["icon"]
    roles = set(ctx["icon"]) - {"text", "text2"}
    ctx["mono-black"] = {k: "#000000" for k in list(roles) + ["text", "text2"]}
    ctx["mono-white"] = {k: "#FFFFFF" for k in list(roles) + ["text", "text2"]}
    return ctx
