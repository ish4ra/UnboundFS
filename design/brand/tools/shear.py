"""UnboundFS official identity: Concept 05 "Shear" (selected by the project owner).

The geometry below is copied unchanged from the Phase 0 concept
(design/archive/phase-0-branding/tools/concepts.py, sym_shear). Do not edit
the canonical numbers; any change is a change to the logo.

Symbol canvas: 100 x 100 units.
"""


def f(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


# ---- canonical geometry (Phase 0, unchanged) ------------------------------
ANGLE = -20      # rotation of the fault line, degrees
R = 37           # disc radius
SLIDE = 6.5      # each half slides this far along the fault line
SEP = 3.4        # each half moves this far away from the fault line
CUT_H = 2.4      # ember cut thickness
# menu bar template (Phase 0 "simple" variant, unchanged)
R_MENU, SEP_MENU = 38, 3.8


def symbol(c, uid, variant="full"):
    """variant: 'full' (logo, icon), 'menubar' (template glyph, no cut line),
    'small' (optional optical adjustment for 16/32 px app icon rasters)."""
    r, d, p, h = R, SLIDE, SEP, CUT_H
    line = True
    if variant == "menubar":
        r, p, line = R_MENU, SEP_MENU, False
    elif variant == "small":
        # Optical adjustment for 16 and 32 px only: a heavier cut and wider separation
        # so the ember line survives rasterisation. Same shape, angle and proportions.
        p, h = 4.6, 4.4
    cut = (f'<rect x="{f(50 - r - d)}" y="{f(50 - h / 2)}" width="{f(2 * (r + d))}" height="{f(h)}" '
           f'rx="{f(h / 2)}" fill="{c["cut"]}"/>') if line else ""
    return (f'<defs><clipPath id="{uid}-u"><rect x="0" y="0" width="100" height="50"/></clipPath>'
            f'<clipPath id="{uid}-d"><rect x="0" y="50" width="100" height="50"/></clipPath></defs>'
            f'<g transform="rotate({ANGLE} 50 50)">'
            f'<g transform="translate({f(-d)} {f(-p)})"><circle cx="50" cy="50" r="{f(r)}" fill="{c["a"]}" clip-path="url(#{uid}-u)"/></g>'
            f'<g transform="translate({f(d)} {f(p)})"><circle cx="50" cy="50" r="{f(r)}" fill="{c["b"]}" clip-path="url(#{uid}-d)"/></g>'
            f'{cut}</g>')


def _fn(c, uid, simple=False):  # adapter for svgkit (Phase 0 signature)
    return symbol(c, uid, "menubar" if simple else "full")


# ---- official palette ------------------------------------------------------
PALETTE = [
    ("Ink", "#121316"), ("Graphite", "#25282E"), ("Steel", "#878D97"),
    ("Silver", "#D3D7DD"), ("Paper", "#FBFBFC"), ("Ember", "#FF5A2C"),
]
# Tints used only inside the original reversed (dark-background) artwork.
REVERSED_TINTS = [("Reversed upper", "#F1F2F4"), ("Reversed lower", "#8C929C"), ("Reversed ember", "#FF6A3D")]
ICON_BG = ("#FBFBFC", "#D3D7DD")
ICON_BG_DARK = ("#25282E", "#121316")   # dark appearance variant (proposed)

CTX = {
    "light": dict(a="#25282E", b="#878D97", cut="#FF5A2C", text="#25282E", text2="#FF5A2C"),
    "dark": dict(a="#F1F2F4", b="#8C929C", cut="#FF6A3D", text="#F1F2F4", text2="#FF6A3D"),
    "tinted": dict(a="#FFFFFF", b="#8E8E93", cut="#D9D9DE", text="#FFFFFF", text2="#D9D9DE"),
}
CTX["icon"] = CTX["light"]
for _name, _col in (("mono-black", "#000000"), ("mono-white", "#FFFFFF")):
    CTX[_name] = {k: _col for k in CTX["light"]}

BRAND = dict(num=5, slug="shear", name="UnboundFS", fn=_fn, icon_scale=5.9, icon_tone="light",
             icon_bg=ICON_BG, ctx=CTX,
             font=[("UNBOUND", "inter600", "text"), ("FS", "inter600", "text2")], tracking=0.12)


def contexts(_concept):
    return CTX
