"""SVG building blocks shared by the UnboundFS brand-concept build:
macOS-style app icon container, outlined wordmarks, standalone files."""
import math
import os
from functools import lru_cache

import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

from shear import f, contexts

FONT_DIR = os.environ.get("UNBOUND_FONT_DIR", "")
INTER_DIR = "/usr/share/fonts/opentype/inter"
FONTS = {
    "manrope700": "manrope-latin-700-normal.ttf",
    "manrope500": "manrope-latin-500-normal.ttf",
    "sg700": "space-grotesk-latin-700-normal.ttf",
    "sg500": "space-grotesk-latin-500-normal.ttf",
    "interd600": os.path.join(INTER_DIR, "InterDisplay-SemiBold.otf"),
    "inter600": os.path.join(INTER_DIR, "Inter-SemiBold.otf"),
    "outfit600": "outfit-latin-600-normal.ttf",
    "outfit400": "outfit-latin-400-normal.ttf",
    "fraunces600": "fraunces-latin-600-normal.ttf",
    "fraunces400": "fraunces-latin-400-normal.ttf",
    "jbm700": "jetbrains-mono-latin-700-normal.ttf",
    "jbm500": "jetbrains-mono-latin-500-normal.ttf",
    "sora600": "sora-latin-600-normal.ttf",
}
FONT_NAMES = {
    "manrope": "Manrope", "sg": "Space Grotesk", "interd": "Inter Display", "inter": "Inter",
    "outfit": "Outfit", "fraunces": "Fraunces", "jbm": "JetBrains Mono", "sora": "Sora",
}


def font_label(key):
    fam = key.rstrip("0123456789")
    return f"{FONT_NAMES[fam]} {key[len(fam):]}"


@lru_cache(None)
def _font(key):
    path = FONTS[key]
    if not os.path.isabs(path):
        path = os.path.join(FONT_DIR, path)
    tt = TTFont(path)
    face = hb.Face(hb.Blob.from_file_path(path))
    return tt, hb.Font(face)


def cap_ratio(key):
    tt, _ = _font(key)
    return tt["OS/2"].sCapHeight / tt["head"].unitsPerEm


def shape_run(key, text, size, x0, baseline, tracking_em):
    """Return (svg path d, advance) for text outlined with harfbuzz shaping."""
    tt, font = _font(key)
    upem = tt["head"].unitsPerEm
    scale = size / upem
    gs, order = tt.getGlyphSet(), tt.getGlyphOrder()
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf, {"kern": True, "liga": True})
    pen = SVGPathPen(gs, ntos=lambda v: f(v))
    x = 0.0
    n = len(buf.glyph_infos)
    for i, (info, pos) in enumerate(zip(buf.glyph_infos, buf.glyph_positions)):
        name = order[info.codepoint]
        tp = TransformPen(pen, (scale, 0, 0, -scale, x0 + (x + pos.x_offset) * scale,
                                baseline - pos.y_offset * scale))
        gs[name].draw(tp)
        x += pos.x_advance
        if i < n - 1:
            x += tracking_em * upem
    return pen.getCommands(), x * scale


# --------------------------------------------------------------------------
def squircle_path(cx=512, cy=512, a=412, n=5.0, steps=480):
    pts = []
    for i in range(steps):
        t = 2 * math.pi * i / steps
        c, s = math.cos(t), math.sin(t)
        x = cx + a * math.copysign(abs(c) ** (2 / n), c)
        y = cy + a * math.copysign(abs(s) ** (2 / n), s)
        pts.append(f"{x:.1f} {y:.1f}")
    return "M" + "L".join(pts) + "Z"


SQUIRCLE = squircle_path()


def symbol_markup(concept, ctx_name, uid, simple=False):
    return concept["fn"](contexts(concept)[ctx_name], uid, simple=simple)


SQ_REF = None  # when set to an element id, icons reference one shared squircle path


def app_icon_inner(concept, uid, shadow=True):
    top, bot = concept["icon_bg"]
    k = concept["icon_scale"]
    dark = concept["icon_tone"] == "dark"
    rim = "#FFFFFF" if dark else "#000000"
    rim_op = "0.10" if dark else "0.06"
    shadow_defs = (f'<filter id="{uid}-sh" x="-20%" y="-20%" width="140%" height="140%">'
                   f'<feDropShadow dx="0" dy="10" stdDeviation="12" flood-color="#000" flood-opacity="0.28"/></filter>'
                   if shadow else "")
    shape = (lambda attrs: f'<use href="#{SQ_REF}" {attrs}/>') if SQ_REF else \
        (lambda attrs: f'<path d="{SQUIRCLE}" {attrs}/>')
    return (f'<defs><linearGradient id="{uid}-bg" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bot}"/></linearGradient>'
            f'<clipPath id="{uid}-clip">{shape("")}</clipPath>{shadow_defs}</defs>'
            + shape(f'fill="url(#{uid}-bg)"' + (f' filter="url(#{uid}-sh)"' if shadow else ""))
            + shape(f'fill="none" stroke="{rim}" stroke-opacity="{rim_op}" stroke-width="3" clip-path="url(#{uid}-clip)"')
            + f'<g clip-path="url(#{uid}-clip)"><g transform="translate(512 512) scale({k}) translate(-50 -50)">'
            f'{symbol_markup(concept, "icon", uid + "-s")}</g></g>')


def svg_doc(inner, vb, w=None, h=None, title=None):
    wh = f' width="{w}" height="{h}"' if w else ""
    t = f"<title>{title}</title>" if title else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}"{wh}>{t}{inner}</svg>')


def app_icon_svg(concept, uid, shadow=True, size=None):
    return svg_doc(app_icon_inner(concept, uid, shadow), "0 0 1024 1024", size, size,
                   f"UnboundFS concept {concept['num']:02d} {concept['name']} app icon")


def symbol_svg(concept, ctx_name, uid, simple=False, size=None):
    return svg_doc(symbol_markup(concept, ctx_name, uid, simple), "0 0 100 100", size, size,
                   f"UnboundFS concept {concept['num']:02d} {concept['name']} symbol")


WM_CAP = 31.0


def wordmark_parts(concept, ctx_name, uid):
    """Returns (inner markup, width, height) for symbol + outlined wordmark."""
    c = contexts(concept)[ctx_name]
    runs = concept["font"]
    size = WM_CAP / cap_ratio(runs[0][1])
    baseline = 50 + WM_CAP / 2
    x = 112.0
    paths = []
    for i, (text, key, role) in enumerate(runs):
        d, adv = shape_run(key, text, size, x, baseline, concept["tracking"])
        paths.append(f'<path d="{d}" fill="{c[role]}"/>')
        x += adv
        if i < len(runs) - 1:
            x += concept["tracking"] * size  # tracking between runs too
    width = math.ceil(x + 6)
    inner = f'<g>{symbol_markup(concept, ctx_name, uid)}</g>' + "".join(paths)
    return inner, width, 100


def wordmark_svg(concept, ctx_name, uid):
    inner, w, h = wordmark_parts(concept, ctx_name, uid)
    return svg_doc(inner, f"0 0 {w} {h}", None, None,
                   f"UnboundFS concept {concept['num']:02d} {concept['name']} wordmark")
