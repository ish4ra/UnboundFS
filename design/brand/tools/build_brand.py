"""Build the production UnboundFS identity (Concept 05 Shear) into design/brand/.

    python3 build_brand.py assets    SVG masters + PNG render jobs
    python3 build_brand.py package   .icns, .iconset, Xcode asset catalogs (after rendering)
    python3 build_brand.py pages     previews, GitHub and promotional images (render jobs)

Run everything with ./build.sh.
"""
import html
import json
import os
import shutil
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shear  # noqa: E402
import svgkit  # noqa: E402
from shear import CTX, f  # noqa: E402
from svgkit import SQUIRCLE, svg_doc, shape_run, cap_ratio  # noqa: E402

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
BUILD = os.path.join(TOOLS, ".build")
SMALL_MAX = 32  # rasters this size or smaller use the optical small-size variant


def p(*parts):
    return os.path.join(ROOT, *parts)


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(text)


# ==========================================================================
# SVG builders
# ==========================================================================
def symbol_svg(ctx, uid, variant="full", title="UnboundFS symbol"):
    return svg_doc(shear.symbol(CTX[ctx], uid, variant), "0 0 100 100", None, None, title)


APPEARANCES = {
    # name: (background top, bottom, symbol ctx, rim colour, rim opacity)
    "default": (shear.ICON_BG[0], shear.ICON_BG[1], "light", "#000000", "0.06"),
    "dark": (shear.ICON_BG_DARK[0], shear.ICON_BG_DARK[1], "dark", "#FFFFFF", "0.10"),
    "tinted": ("#1C1C1E", "#0B0B0C", "tinted", "#FFFFFF", "0.10"),
}


def icon_inner(appearance, uid, variant="full", shadow=True):
    top, bot, ctx, rim, rim_op = APPEARANCES[appearance]
    k = shear.BRAND["icon_scale"]
    sh = (f'<filter id="{uid}-sh" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="10" '
          f'stdDeviation="12" flood-color="#000" flood-opacity="0.28"/></filter>') if shadow else ""
    return (f'<defs><linearGradient id="{uid}-bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{top}"/>'
            f'<stop offset="1" stop-color="{bot}"/></linearGradient><clipPath id="{uid}-clip"><path d="{SQUIRCLE}"/></clipPath>{sh}</defs>'
            f'<path d="{SQUIRCLE}" fill="url(#{uid}-bg)"' + (f' filter="url(#{uid}-sh)"' if shadow else "") + '/>'
            f'<path d="{SQUIRCLE}" fill="none" stroke="{rim}" stroke-opacity="{rim_op}" stroke-width="3" clip-path="url(#{uid}-clip)"/>'
            f'<g clip-path="url(#{uid}-clip)"><g transform="translate(512 512) scale({k}) translate(-50 -50)">'
            f'{shear.symbol(CTX[ctx], uid + "-s", variant)}</g></g>')


def icon_svg(appearance, uid, variant="full"):
    t = f"UnboundFS app icon ({appearance} appearance{', small-size variant' if variant == 'small' else ''})"
    return svg_doc(icon_inner(appearance, uid, variant), "0 0 1024 1024", None, None, t)


def icon_layers():
    """Separate foreground layers on the 1024 canvas, for Icon Composer."""
    k = shear.BRAND["icon_scale"]
    full = shear.symbol(dict(a="#25282E", b="#878D97", cut="#FF5A2C"), "L")
    # split the composed symbol into its three parts by re-drawing each alone
    parts = {
        "1-disc-upper": dict(a="#25282E", b="none", cut="none"),
        "2-disc-lower": dict(a="none", b="#878D97", cut="none"),
        "3-ember-cut": dict(a="none", b="none", cut="#FF5A2C"),
    }
    out = {}
    for name, c in parts.items():
        inner = f'<g transform="translate(512 512) scale({k}) translate(-50 -50)">{shear.symbol(c, "L" + name[0])}</g>'
        out[name] = svg_doc(inner, "0 0 1024 1024", None, None, f"UnboundFS icon layer {name}")
    assert full  # composed reference exists
    return out


def lockup_parts(ctx, uid):
    return svgkit.wordmark_parts(shear.BRAND, ctx, uid)


def lockup_svg(ctx, uid):
    inner, w, h = lockup_parts(ctx, uid)
    return svg_doc(inner, f"0 0 {w} {h}", None, None, "UnboundFS wordmark")


def logotype_svg(ctx):
    """Lettering only, same setting as the lockup."""
    c = CTX[ctx]
    runs, tr = shear.BRAND["font"], shear.BRAND["tracking"]
    size = svgkit.WM_CAP / cap_ratio(runs[0][1])
    x, paths = 0.0, []
    for i, (text, key, role) in enumerate(runs):
        d, adv = shape_run(key, text, size, x, svgkit.WM_CAP, tr)
        paths.append(f'<path d="{d}" fill="{c[role]}"/>')
        x += adv + (tr * size if i < len(runs) - 1 else 0)
    w = round(x + 1, 2)
    return svg_doc("".join(paths), f"0 0 {f(w)} {f(svgkit.WM_CAP)}", None, None, "UnboundFS logotype"), w


# ==========================================================================
# Phase: assets
# ==========================================================================
ICONSET = [(16, 1), (16, 2), (32, 1), (32, 2), (128, 1), (128, 2), (256, 1), (256, 2), (512, 1), (512, 2)]


def build_assets():
    jobs = []

    def job(svg, out, w, h=None):
        jobs.append(dict(svg=svg, out=out, w=w, h=h or w))

    # logo
    for name, ctx in [("symbol", "light"), ("symbol-reversed", "dark"), ("symbol-mono-black", "mono-black"),
                      ("symbol-mono-white", "mono-white")]:
        fp = p("logo", f"unboundfs-{name}.svg")
        write(fp, symbol_svg(ctx, "s" + ctx.replace("-", "")) + "\n")
        for s in ((256, 512, 1024, 2048) if name in ("symbol", "symbol-reversed") else (1024,)):
            job(fp, p("logo", "png", f"unboundfs-{name}-{s}.png"), s)
    # wordmark
    for name, ctx in [("wordmark", "light"), ("wordmark-reversed", "dark"), ("wordmark-mono-black", "mono-black"),
                      ("wordmark-mono-white", "mono-white")]:
        fp = p("wordmark", f"unboundfs-{name}.svg")
        write(fp, lockup_svg(ctx, "w" + ctx.replace("-", "")) + "\n")
        _, w, h = lockup_parts(ctx, "x")
        for scale in (2, 4):
            job(fp, p("wordmark", "png", f"unboundfs-{name}@{scale}x.png"), round(w * 2.4 * scale / 2),
                round(h * 2.4 * scale / 2))
    for name, ctx in [("logotype", "light"), ("logotype-reversed", "dark")]:
        svg, w = logotype_svg(ctx)
        fp = p("wordmark", f"unboundfs-{name}.svg")
        write(fp, svg + "\n")
        job(fp, p("wordmark", "png", f"unboundfs-{name}@4x.png"), round(w * 4 * 2.4 / 2), round(svgkit.WM_CAP * 4 * 2.4 / 2))
    # app icon masters
    for ap in APPEARANCES:
        fp = p("app-icon", f"AppIcon-{ap}.svg" if ap != "default" else "AppIcon.svg")
        write(fp, icon_svg(ap, "i" + ap) + "\n")
        job(fp, p("app-icon", "png", f"AppIcon-{ap}-1024.png"), 1024)
    write(p("app-icon", "AppIcon-small.svg"), icon_svg("default", "ismall", "small") + "\n")
    for name, svg in icon_layers().items():
        write(p("app-icon", "icon-composer-layers", f"{name}.svg"), svg + "\n")
    # iconset rasters
    for pt, sc in ICONSET:
        px = pt * sc
        src = p("app-icon", "AppIcon-small.svg") if px <= SMALL_MAX else p("app-icon", "AppIcon.svg")
        job(src, os.path.join(BUILD, "iconset", f"{px}.png"), px)
    # menu bar
    fp = p("menubar", "UnboundFSMenubarTemplate.svg")
    write(fp, symbol_svg("mono-black", "mb", "menubar", "UnboundFS menu bar template") + "\n")
    job(fp, p("menubar", "UnboundFSMenubarTemplate.png"), 18)
    job(fp, p("menubar", "UnboundFSMenubarTemplate@2x.png"), 36)
    # palette
    pal = {
        "name": "UnboundFS — Shear (Silver & Ember)",
        "status": "approved by the project owner",
        "colors": [{"name": n, "hex": h} for n, h in shear.PALETTE],
        "app_icon_background": {"top": shear.ICON_BG[0], "bottom": shear.ICON_BG[1]},
        "reversed_artwork_tints": [{"name": n, "hex": h} for n, h in shear.REVERSED_TINTS],
        "primary_accent": "Ember",
        "typeface": {"wordmark": "Inter SemiBold, uppercase, tracking +0.12 em", "ui": "System font (SF Pro)"},
    }
    write(p("palette", "palette.json"), json.dumps(pal, indent=2) + "\n")
    css = ":root {\n" + "".join(f"  --ubfs-{n.lower()}: {h};\n" for n, h in shear.PALETTE) + "}\n"
    write(p("palette", "colors.css"), "/* UnboundFS official palette (Concept 05 Shear). */\n" + css)
    os.makedirs(BUILD, exist_ok=True)
    write(os.path.join(BUILD, "jobs-assets.json"), json.dumps(jobs, indent=1))
    print(f"assets: {len(jobs)} render jobs")


# ==========================================================================
# Phase: package (ICNS, iconset, asset catalogs)
# ==========================================================================
ICNS_TYPES = {16: b"icp4", 32: b"icp5", 64: b"ic12", 128: b"ic07", 256: b"ic08", 512: b"ic09", 1024: b"ic10"}
RETINA_TYPES = {32: b"ic11", 64: b"ic12", 256: b"ic13", 512: b"ic14", 1024: b"ic10"}


def iconset_name(pt, sc):
    return f"icon_{pt}x{pt}{'@2x' if sc == 2 else ''}.png"


def build_package():
    src = os.path.join(BUILD, "iconset")
    iconset = p("app-icon", "AppIcon.iconset")
    appiconset = p("app-icon", "Assets.xcassets", "AppIcon.appiconset")
    for d in (iconset, appiconset):
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d)
    images = []
    for pt, sc in ICONSET:
        name = iconset_name(pt, sc)
        for d in (iconset, appiconset):
            shutil.copy(os.path.join(src, f"{pt * sc}.png"), os.path.join(d, name))
        images.append({"filename": name, "idiom": "mac", "scale": f"{sc}x", "size": f"{pt}x{pt}"})
    write(os.path.join(appiconset, "Contents.json"),
          json.dumps({"images": images, "info": {"author": "xcode", "version": 1}}, indent=2) + "\n")
    write(p("app-icon", "Assets.xcassets", "Contents.json"),
          json.dumps({"info": {"author": "xcode", "version": 1}}, indent=2) + "\n")
    # ICNS: PNG-payload entries as written by iconutil (1x and 2x types)
    entries = []
    for pt, sc in ICONSET:
        px = pt * sc
        typ = (RETINA_TYPES if sc == 2 else ICNS_TYPES)[px]
        if any(t == typ for t, _ in entries):
            continue
        with open(os.path.join(src, f"{px}.png"), "rb") as fh:
            entries.append((typ, fh.read()))
    body = b"".join(t + struct.pack(">I", len(d) + 8) + d for t, d in entries)
    with open(p("app-icon", "AppIcon.icns"), "wb") as fh:
        fh.write(b"icns" + struct.pack(">I", len(body) + 8) + body)
    # menu bar image set (vector, template rendering)
    mb = p("menubar", "Assets.xcassets", "UnboundFSMenubar.imageset")
    shutil.rmtree(mb, ignore_errors=True)
    os.makedirs(mb)
    shutil.copy(p("menubar", "UnboundFSMenubarTemplate.svg"), os.path.join(mb, "UnboundFSMenubarTemplate.svg"))
    write(os.path.join(mb, "Contents.json"), json.dumps({
        "images": [{"filename": "UnboundFSMenubarTemplate.svg", "idiom": "universal"}],
        "info": {"author": "xcode", "version": 1},
        "properties": {"preserves-vector-representation": True, "template-rendering-intent": "template"}}, indent=2) + "\n")
    write(p("menubar", "Assets.xcassets", "Contents.json"), json.dumps({"info": {"author": "xcode", "version": 1}}, indent=2) + "\n")
    print(f"package: AppIcon.icns ({len(entries)} entries), iconset, asset catalogs")


# ==========================================================================
# Colour contrast
# ==========================================================================
def _lin(c):
    c = c / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(hexv):
    r, g, b = (int(hexv[i:i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def ember_text_proposal(bg="#FBFBFC", target=4.5):
    """Darken Ember (same hue) until it reaches the target contrast on bg."""
    import colorsys
    r, g, b = (int(shear.PALETTE[5][1][i:i + 2], 16) / 255 for i in (1, 3, 5))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    while l > 0:
        rr, gg, bb = colorsys.hls_to_rgb(h, l, s)
        hx = "#%02X%02X%02X" % (round(rr * 255), round(gg * 255), round(bb * 255))
        if contrast(hx, bg) >= target:
            return hx
        l -= 0.005
    return None


def contrast_table():
    pairs = [("Ember", "Paper"), ("Ember", "Silver"), ("Ember", "Ink"), ("Ember", "Graphite"),
             ("Graphite", "Paper"), ("Ink", "Paper"), ("Steel", "Paper"), ("Steel", "Ink"), ("Paper", "Ink"),
             ("Silver", "Ink"), ("Ink", "Ember")]
    pal = dict(shear.PALETTE)
    rows = []
    for fg, bg in pairs:
        r = contrast(pal[fg], pal[bg])
        verdict = ("AA text" if r >= 4.5 else "AA large text / UI graphics only" if r >= 3 else "decorative only")
        rows.append((fg, bg, r, verdict))
    return rows


# ==========================================================================
# Phase: pages (previews, GitHub, promo, guidelines board)
# ==========================================================================
FONT = '"Inter", -apple-system, BlinkMacSystemFont, system-ui, sans-serif'


def fu(path):
    return "file://" + os.path.abspath(path)


def inline_symbol(ctx, uid, size, variant="full", extra=""):
    return f'<svg viewBox="0 0 100 100" width="{size}" height="{size}"{extra}>{shear.symbol(CTX[ctx], uid, variant)}</svg>'


def inline_icon(ap, uid, size, shadow=True):
    return f'<svg viewBox="0 0 1024 1024" width="{size}" height="{size}">{icon_inner(ap, uid, "full", shadow)}</svg>'


def inline_lockup(ctx, uid, height):
    inner, w, h = lockup_parts(ctx, uid)
    return f'<svg viewBox="0 0 {w} {h}" height="{height}" width="{round(w * height / h)}">{inner}</svg>'


def page(css, body, width):
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>*{{box-sizing:border-box}}'
            f'html,body{{margin:0;font-family:{FONT}}}{css}</style></head><body style="width:{width}px">{body}</body></html>')


def banner_html(mode):
    bg = "linear-gradient(180deg,#FBFBFC,#E9EBEE)" if mode == "light" else "linear-gradient(180deg,#25282E,#121316)"
    fg = "#25282E" if mode == "light" else "#F1F2F4"
    sub = "#5F656F" if mode == "light" else "#A9AEB6"
    ctx = "light" if mode == "light" else "dark"
    body = (f'<div style="width:2560px;height:640px;background:{bg};display:flex;align-items:center;justify-content:center;flex-direction:column;gap:34px">'
            f'{inline_lockup(ctx, "bn" + mode, 230)}'
            f'<div style="font-size:52px;font-weight:500;letter-spacing:-.01em;color:{sub}">Storage without boundaries.</div></div>')
    return page("", body, 2560)


def social_html():
    body = ('<div style="width:1280px;height:640px;background:linear-gradient(160deg,#FBFBFC,#D3D7DD);display:flex;align-items:center;gap:64px;padding:0 96px">'
            f'{inline_icon("default", "so", 360)}<div style="display:flex;flex-direction:column;gap:22px">'
            f'{inline_lockup("light", "sol", 92).replace("<svg", "<svg style=margin-left:-4px", 1)}'
            '<div style="font-size:36px;font-weight:600;color:#25282E;letter-spacing:-.01em">Storage without boundaries.</div>'
            '<div style="font-size:24px;color:#5F656F;line-height:1.4;max-width:620px">A free and open-source macOS filesystem utility. Early development: not yet usable.</div>'
            '</div></div>')
    return page("", body, 1280)


def hero_html(mode):
    dark = mode == "dark"
    bg = ("radial-gradient(1200px 900px at 30% 40%,#2E3239,#121316)" if dark
          else "radial-gradient(1200px 900px at 30% 40%,#FFFFFF,#D3D7DD)")
    fg, sub = ("#F1F2F4", "#A9AEB6") if dark else ("#25282E", "#5F656F")
    icon = inline_icon("dark" if dark else "default", "hero" + mode, 760)
    body = (f'<div style="width:2560px;height:1440px;background:{bg};display:flex;align-items:center;gap:150px;padding:0 220px">'
            f'{icon}<div style="display:flex;flex-direction:column;gap:46px">'
            f'{inline_lockup("dark" if dark else "light", "hl" + mode, 190)}'
            f'<div style="font-size:84px;font-weight:600;letter-spacing:-.02em;color:{fg}">Storage without boundaries.</div>'
            f'<div style="font-size:40px;color:{sub};line-height:1.45;max-width:1000px">Free and open-source. No subscriptions, no accounts, no telemetry.</div>'
            '</div></div>')
    return page("", body, 2560)


def square_html():
    body = ('<div style="width:1080px;height:1080px;background:linear-gradient(160deg,#25282E,#121316);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:60px">'
            f'{inline_icon("default", "sq", 520)}'
            f'{inline_lockup("dark", "sql", 96)}'
            '<div style="font-size:40px;font-weight:500;color:#A9AEB6">Storage without boundaries.</div></div>')
    return page("", body, 1080)


BOARD_CSS = """
.b{width:2000px;padding:56px 64px 60px;background:#E9EAEC;color:#16181B;display:flex;flex-direction:column;gap:24px}
.h{display:flex;justify-content:space-between;align-items:flex-end}
.ey{font-size:17px;letter-spacing:.14em;text-transform:uppercase;color:#5C6169;font-weight:600}
.t{font-size:60px;font-weight:700;letter-spacing:-.02em;line-height:1;margin-top:8px}
.nt{text-align:right;color:#5C6169;font-size:16px;line-height:1.5}
.g{display:grid;grid-template-columns:repeat(4,1fr);gap:18px}
.tile{border-radius:18px;padding:22px;display:flex;flex-direction:column;gap:12px}
.lab{font-size:14px;letter-spacing:.12em;text-transform:uppercase;font-weight:600;opacity:.62}
.L{background:#fff}.D{background:#121316;color:#F1F2F4}.S{background:linear-gradient(160deg,#F7F7F8,#D9DBDF)}
.c{flex:1;display:flex;align-items:center;justify-content:center;gap:28px;flex-wrap:wrap}
.s2{grid-column:span 2}.r2{grid-row:span 2}
.cap{font-size:14px;opacity:.65;text-align:center}
.px{image-rendering:pixelated}
.sw{display:flex;gap:12px;flex-wrap:wrap}.sw div{display:flex;flex-direction:column;gap:5px;font-size:13px}
.sw span{width:96px;height:72px;border-radius:12px;box-shadow:inset 0 0 0 1px rgba(0,0,0,.08)}
.mono{font-family:ui-monospace,"DejaVu Sans Mono",monospace;opacity:.75}
"""


def overview_html():
    iconset = os.path.join(BUILD, "iconset")
    sizes = "".join(f'<figure style="margin:0;display:flex;flex-direction:column;align-items:center;gap:6px">'
                    f'<img src="{fu(os.path.join(iconset, f"{s}.png"))}" width="{s}" height="{s}"><span class="cap">{s} px</span></figure>'
                    for s in (128, 64, 32, 16))
    zoom = "".join(f'<figure style="margin:0;display:flex;flex-direction:column;align-items:center;gap:6px">'
                   f'<img class="px" src="{fu(os.path.join(iconset, f"{s}.png"))}" width="{s * z}" height="{s * z}"><span class="cap">{s} px ×{z}</span></figure>'
                   for s, z in ((32, 3), (16, 5)))
    sw = "".join(f'<div><span style="background:{h}"></span><b>{n}</b><span class="mono" style="all:unset;font-family:ui-monospace,monospace;opacity:.75">{h}</span></div>'
                 for n, h in shear.PALETTE)
    menubar = "".join(
        f'<div style="background:{bg};border-radius:10px;height:48px;display:flex;align-items:center;justify-content:flex-end;gap:26px;padding:0 22px;color:{fg};font-size:26px;font-weight:500">'
        f'<span style="display:inline-flex;padding:4px 10px;border-radius:8px;background:{hl}">{inline_symbol(ctx, "mb" + ctx, 32, "menubar")}</span>'
        f'<span>Tue 24 Nov&nbsp;&nbsp;9:41</span></div>'
        for bg, fg, hl, ctx in (("rgba(246,246,246,.95)", "#000", "rgba(0,0,0,.08)", "mono-black"),
                                ("rgba(30,30,32,.95)", "#fff", "rgba(255,255,255,.14)", "mono-white")))
    body = f"""<div class="b">
<div class="h"><div><div class="ey">UnboundFS &middot; official visual identity</div><div class="t">Shear &mdash; Silver &amp; Ember</div></div>
<div class="nt">Approved by the project owner<br>Concept 05 from Phase 0, geometry unchanged</div></div>
<div class="g">
 <div class="tile S s2 r2"><div class="lab">App icon &middot; default appearance</div><div class="c">{inline_icon("default", "ov1", 520)}</div></div>
 <div class="tile L"><div class="lab">Symbol &middot; light</div><div class="c">{inline_symbol("light", "ov2", 210)}</div></div>
 <div class="tile D"><div class="lab">Symbol &middot; dark</div><div class="c">{inline_symbol("dark", "ov3", 210)}</div></div>
 <div class="tile L"><div class="lab">Monochrome</div><div class="c">{inline_symbol("mono-black", "ov4", 150)}</div></div>
 <div class="tile D"><div class="lab">Monochrome reversed</div><div class="c">{inline_symbol("mono-white", "ov5", 150)}</div></div>
 <div class="tile L s2"><div class="lab">Wordmark &middot; light</div><div class="c" style="padding:20px 0">{inline_lockup("light", "ov6", 110)}</div></div>
 <div class="tile D s2"><div class="lab">Wordmark &middot; dark</div><div class="c" style="padding:20px 0">{inline_lockup("dark", "ov7", 110)}</div></div>
 <div class="tile S s2"><div class="lab">macOS 26 appearance variants (proposed)</div><div class="c">
  <figure style="margin:0;text-align:center">{inline_icon("default", "ap1", 190)}<div class="cap">Default</div></figure>
  <figure style="margin:0;text-align:center">{inline_icon("dark", "ap2", 190)}<div class="cap">Dark</div></figure>
  <figure style="margin:0;text-align:center">{inline_icon("tinted", "ap3", 190)}<div class="cap">Tinted source</div></figure></div></div>
 <div class="tile L s2"><div class="lab">App icon rasters &middot; actual pixels, then magnified</div><div class="c" style="align-items:flex-end">{sizes}{zoom}</div>
  <div class="cap">16 and 32 px use the small-size optical variant (heavier cut, wider gap).</div></div>
 <div class="tile L s2"><div class="lab">Menu bar template &middot; Retina 2&times;</div><div style="display:flex;flex-direction:column;gap:12px;flex:1;justify-content:center">{menubar}</div></div>
 <div class="tile L s2"><div class="lab">Official palette</div><div class="sw">{sw}</div>
  <div class="cap" style="text-align:left">App icon background {shear.ICON_BG[0]} &rarr; {shear.ICON_BG[1]} &middot; Ember is the primary accent</div></div>
</div></div>"""
    return page(BOARD_CSS, body, 2000)


# Measured artwork box of the symbol (from the 1024 px render): units on the 100-unit canvas.
BX0, BY0, BX1, BY1 = 5.7, 12.0, 94.3, 88.0


def guidelines_html():
    pal = dict(shear.PALETTE)
    rows = "".join(f'<tr><td><span class="chip" style="background:{pal[fg]}"></span>{fg}</td><td><span class="chip" style="background:{pal[bg]}"></span>{bg}</td>'
                   f'<td class="num">{r:.2f}:1</td><td>{v}</td></tr>' for fg, bg, r, v in contrast_table())
    x = shear.R / 2  # clear-space unit
    # construction: symbol with fault-line angle and clear space
    cons = (f'<svg viewBox="-30 -30 160 160" width="520" height="520"><rect x="-30" y="-30" width="160" height="160" fill="#fff"/>'
            f'<rect x="{f(BX0 - x)}" y="{f(BY0 - x)}" width="{f(BX1 - BX0 + 2 * x)}" height="{f(BY1 - BY0 + 2 * x)}" fill="none" stroke="#FF5A2C" stroke-width=".6" stroke-dasharray="2 2"/>'
            f'<rect x="{BX0}" y="{BY0}" width="{f(BX1 - BX0)}" height="{f(BY1 - BY0)}" fill="none" stroke="#878D97" stroke-width=".4"/>'
            f'{shear.symbol(CTX["light"], "cons")}'
            f'<line x1="-10" y1="{f(50 + 60 * 0.364)}" x2="110" y2="{f(50 - 60 * 0.364)}" stroke="#878D97" stroke-width=".4" stroke-dasharray="1.5 1.5"/>'
            f'<text x="98" y="22" font-size="6" fill="#5C6169" font-family="Inter">20&#176;</text>'
            f'<text x="{f(BX0 - x + 2)}" y="{f(BY0 - x - 3)}" font-size="5.5" fill="#FF5A2C" font-family="Inter">clear space = x = &#189; disc radius</text></svg>')
    donts = []
    for label, tr in [("Don't recolour", 'style="filter:hue-rotate(160deg)"'),
                      ("Don't rotate", 'style="transform:rotate(35deg)"'),
                      ("Don't stretch", 'style="transform:scaleX(1.45)"'),
                      ("Don't add effects", 'style="filter:drop-shadow(6px 8px 0 #878D97)"')]:
        donts.append(f'<figure><div class="dn">{inline_symbol("light", "dn" + str(len(donts)), 120, extra=" " + tr)}</div><figcaption>{label}</figcaption></figure>')
    donts.append('<figure><div class="dn"><svg viewBox="0 0 100 100" width="120" height="120"><circle cx="50" cy="50" r="37" fill="#25282E"/>'
                 '<rect x="10" y="48.8" width="80" height="2.4" fill="#FF5A2C" transform="rotate(-20 50 50)"/></svg></div><figcaption>Don\'t close the gap</figcaption></figure>')
    donts.append(f'<figure><div class="dn" style="background:#FF5A2C">{inline_symbol("light", "dn9", 120)}</div><figcaption>Don\'t place on Ember</figcaption></figure>')
    css = BOARD_CSS + """
table{border-collapse:collapse;width:100%;font-size:15px}td{padding:7px 8px;border-bottom:1px solid #E6E7EA}
.num{font-variant-numeric:tabular-nums;font-weight:600}.chip{display:inline-block;width:16px;height:16px;border-radius:4px;vertical-align:-3px;margin-right:8px;box-shadow:inset 0 0 0 1px rgba(0,0,0,.12)}
figure{margin:0;display:flex;flex-direction:column;align-items:center;gap:8px}figcaption{font-size:14px;color:#5C6169}
.dn{width:180px;height:160px;border-radius:14px;background:#F4F5F6;display:flex;align-items:center;justify-content:center;overflow:hidden;position:relative}
.dn::after{content:"";position:absolute;inset:0;background:linear-gradient(to top right,transparent calc(50% - 2px),#C3291B calc(50% - 2px),#C3291B calc(50% + 2px),transparent calc(50% + 2px))}
.do{width:180px;height:160px;border-radius:14px;display:flex;align-items:center;justify-content:center}
p{margin:0;font-size:16px;line-height:1.55;max-width:70ch}"""
    proposal = ember_text_proposal()
    body = f"""<div class="b">
<div class="h"><div><div class="ey">UnboundFS &middot; brand guidelines</div><div class="t">Using the Shear identity</div></div>
<div class="nt">Full text: design/brand/GUIDELINES.md</div></div>
<div class="g">
 <div class="tile L s2 r2"><div class="lab">Construction and clear space</div><div class="c">{cons}</div>
  <p>The symbol is a disc of radius 37 units on a 100-unit canvas, cut along a line at &minus;20&deg;. Each half slides 6.5 units along the cut and 3.4 units away from it; the Ember cut is 2.4 units thick. Keep a clear space of <b>x = &#189; disc radius</b> around the symbol's artwork box.</p></div>
 <div class="tile L s2"><div class="lab">Minimum sizes</div><div class="c" style="justify-content:space-around">
  <figure>{inline_symbol("light", "mn1", 16)}<figcaption>Symbol 16 px</figcaption></figure>
  <figure>{inline_lockup("light", "mn2", 24)}<figcaption>Wordmark 24 px tall (&asymp;100 px wide)</figcaption></figure>
  <figure>{inline_symbol("mono-black", "mn3", 16, "menubar")}<figcaption>Menu bar 16&ndash;18 pt template</figcaption></figure></div></div>
 <div class="tile L s2"><div class="lab">Correct backgrounds</div><div class="c">
  <div class="do" style="background:#FBFBFC;box-shadow:inset 0 0 0 1px #E1E3E6">{inline_symbol("light", "ok1", 110)}</div>
  <div class="do" style="background:#D3D7DD">{inline_symbol("light", "ok2", 110)}</div>
  <div class="do" style="background:#121316">{inline_symbol("dark", "ok3", 110)}</div>
  <div class="do" style="background:#25282E">{inline_symbol("mono-white", "ok4", 110)}</div></div></div>
 <div class="tile L s2"><div class="lab">Colour contrast (WCAG 2.x)</div><table>{rows}</table>
  <p style="font-size:14px;margin-top:8px">Ember on light surfaces is for icons, fills and large text only. For small Ember-coloured text on Paper, a darker <b>proposed</b> tone {proposal} reaches 4.5:1; it is not part of the approved palette until the owner accepts it.</p></div>
 <div class="tile L s2"><div class="lab">Incorrect use</div><div class="c" style="gap:16px">{"".join(donts)}</div></div>
</div></div>"""
    return page(css, body, 2000)


def build_pages():
    pages = {
        "overview": (overview_html(), p("previews", "brand-overview.png"), 2000),
        "guidelines": (guidelines_html(), p("previews", "brand-guidelines.png"), 2000),
        "banner-light": (banner_html("light"), p("github", "readme-banner-light.png"), 2560),
        "banner-dark": (banner_html("dark"), p("github", "readme-banner-dark.png"), 2560),
        "social": (social_html(), p("github", "social-preview.png"), 1280),
        "hero-light": (hero_html("light"), p("promo", "unboundfs-hero-light-2560x1440.png"), 2560),
        "hero-dark": (hero_html("dark"), p("promo", "unboundfs-hero-dark-2560x1440.png"), 2560),
        "square": (square_html(), p("promo", "unboundfs-square-1080.png"), 1080),
    }
    jobs = []
    for key, (doc, out, w) in pages.items():
        hp = os.path.join(BUILD, f"{key}.html")
        write(hp, doc)
        jobs.append(dict(html=hp, out=out, w=w, h=100, fullPage=True))
    write(os.path.join(BUILD, "jobs-pages.json"), json.dumps(jobs, indent=1))
    print(f"pages: {len(jobs)} render jobs; ember text proposal {ember_text_proposal()}")
    for fg, bg, r, v in contrast_table():
        print(f"  {fg:9s} on {bg:9s} {r:5.2f}:1  {v}")


if __name__ == "__main__":
    {"assets": build_assets, "package": build_package, "pages": build_pages}[sys.argv[1]]()
