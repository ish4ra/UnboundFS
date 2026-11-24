"""Build every UnboundFS Phase 0 brand-concept deliverable.

    python3 build.py assets   -> SVG sources + PNG render jobs
    python3 build.py pages    -> boards, comparison sheet, previews, gallery, README

See tools/README.md (run via ./build.sh).
"""
import base64
import html
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from concepts import CONCEPTS, contexts  # noqa: E402
from svgkit import (app_icon_svg, app_icon_inner, symbol_svg, symbol_markup, wordmark_svg,  # noqa: E402
                    wordmark_parts, font_label, SQUIRCLE)

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
BUILD = os.environ.get("UNBOUND_BUILD_DIR", os.path.join(TOOLS, ".build"))
ICON_SIZES = [16, 32, 64, 128, 256, 512, 1024]


def cdir(c):
    return os.path.join(ROOT, "concepts", f"concept-{c['num']:02d}-{c['slug']}")


def rel(path):
    return os.path.relpath(path, ROOT)


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(text)


def label(c):
    return f"Concept {c['num']:02d}"


# ==========================================================================
# Phase 1: SVG sources and PNG jobs
# ==========================================================================
def build_assets():
    jobs = []
    for c in CONCEPTS:
        d = cdir(c)
        u = f"ub{c['num']}"
        files = {
            "app-icon.svg": app_icon_svg(c, u + "i"),
            "symbol.svg": symbol_svg(c, "light", u + "l"),
            "symbol-reversed.svg": symbol_svg(c, "dark", u + "d"),
            "symbol-mono-black.svg": symbol_svg(c, "mono-black", u + "mb"),
            "symbol-mono-white.svg": symbol_svg(c, "mono-white", u + "mw"),
            "menubar-template.svg": symbol_svg(c, "mono-black", u + "mt", simple=True),
            "wordmark.svg": wordmark_svg(c, "light", u + "wl"),
            "wordmark-reversed.svg": wordmark_svg(c, "dark", u + "wd"),
            "wordmark-mono-black.svg": wordmark_svg(c, "mono-black", u + "wmb"),
            "wordmark-mono-white.svg": wordmark_svg(c, "mono-white", u + "wmw"),
        }
        for name, svg in files.items():
            write(os.path.join(d, name), svg + "\n")
        pal = {
            "concept": label(c), "name": c["name"], "palette": c["palette_name"],
            "colors": [{"name": n, "hex": h} for n, h in c["palette"]],
            "app_icon_background": {"top": c["icon_bg"][0], "bottom": c["icon_bg"][1]},
            "wordmark_typeface": sorted({font_label(k) for _, k, _ in c["font"]}),
        }
        write(os.path.join(d, "palette.json"), json.dumps(pal, indent=2) + "\n")

        p = os.path.join(d, "png")
        for s in ICON_SIZES:
            jobs.append(dict(svg=os.path.join(d, "app-icon.svg"), out=os.path.join(p, f"app-icon-{s}.png"), w=s, h=s))
        for name in ["symbol", "symbol-reversed", "symbol-mono-black", "symbol-mono-white"]:
            jobs.append(dict(svg=os.path.join(d, f"{name}.svg"), out=os.path.join(p, f"{name}-1024.png"), w=1024, h=1024))
        for s in (18, 36):
            jobs.append(dict(svg=os.path.join(d, "menubar-template.svg"),
                             out=os.path.join(p, f"menubar-template-{s}.png"), w=s, h=s))
        for name in ["wordmark", "wordmark-reversed"]:
            _, w, h = wordmark_parts(c, "light", "x")
            jobs.append(dict(svg=os.path.join(d, f"{name}.svg"), out=os.path.join(p, f"{name}@2x.png"),
                             w=round(w * 2.4), h=round(h * 2.4)))
    os.makedirs(BUILD, exist_ok=True)
    write(os.path.join(BUILD, "jobs-assets.json"), json.dumps(jobs, indent=1))
    print(f"assets: {len(CONCEPTS)} concepts, {len(jobs)} PNG jobs")


# ==========================================================================
# Shared HTML pieces
# ==========================================================================
FONT_STACK = '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif'


def file_url(path):
    return "file://" + os.path.abspath(path)


def data_uri(path):
    with open(path, "rb") as fh:
        return "data:image/png;base64," + base64.b64encode(fh.read()).decode()


def inline_symbol(c, ctx, uid, size, simple=False):
    return (f'<svg viewBox="0 0 100 100" width="{size}" height="{size}" role="img" '
            f'aria-label="{label(c)} {c["name"]} symbol">{symbol_markup(c, ctx, uid, simple)}</svg>')


def inline_icon(c, uid, size, shadow=True):
    return (f'<svg viewBox="0 0 1024 1024" width="{size}" height="{size}" role="img" '
            f'aria-label="{label(c)} {c["name"]} app icon">{app_icon_inner(c, uid, shadow)}</svg>')


def inline_wordmark(c, ctx, uid, height):
    inner, w, h = wordmark_parts(c, ctx, uid)
    return (f'<svg viewBox="0 0 {w} {h}" height="{height}" width="{round(w * height / h)}" role="img" '
            f'aria-label="UnboundFS wordmark, {label(c)}">{inner}</svg>')


def battery_svg(color, h):
    return (f'<svg viewBox="0 0 26 13" height="{h}" width="{round(h * 2)}" aria-hidden="true">'
            f'<rect x="0.75" y="0.75" width="21.5" height="11.5" rx="3.2" fill="none" stroke="{color}" '
            f'stroke-opacity="0.45" stroke-width="1.2"/><rect x="2.5" y="2.5" width="15" height="8" rx="1.8" fill="{color}"/>'
            f'<rect x="23.3" y="4.4" width="1.6" height="4.2" rx="0.8" fill="{color}" fill-opacity="0.45"/></svg>')


def menubar_html(c, uid, mode, scale=1):
    fg = "#000000" if mode == "light" else "#FFFFFF"
    ctx = "mono-black" if mode == "light" else "mono-white"
    bar_bg = "rgba(246,246,246,0.92)" if mode == "light" else "rgba(30,30,32,0.92)"
    h = 24 * scale
    g = 16 * scale
    fs = 13 * scale
    return (f'<div class="mbar" style="height:{h}px;background:{bar_bg};color:{fg};font-size:{fs}px;'
            f'gap:{14 * scale}px;padding:0 {12 * scale}px">'
            f'<span class="mb-glyph" style="padding:{2 * scale}px {5 * scale}px;border-radius:{4 * scale}px;'
            f'background:{"rgba(0,0,0,0.08)" if mode == "light" else "rgba(255,255,255,0.14)"}">'
            f'{inline_symbol(c, ctx, uid, g, simple=True)}</span>'
            f'{battery_svg(fg, 11 * scale)}<span class="mb-time">Tue 24 Nov&nbsp;&nbsp;9:41</span></div>')


def swatches(c, size=56, text=True):
    out = []
    for n, h in c["palette"]:
        cap = f'<span class="sw-name">{html.escape(n)}</span><span class="sw-hex">{h}</span>' if text else ""
        out.append(f'<div class="sw"><span class="sw-chip" style="background:{h};width:{size}px;height:{size}px"></span>{cap}</div>')
    return '<div class="swatches">' + "".join(out) + "</div>"


# ==========================================================================
# Phase 2a: per-concept presentation boards (PNG)
# ==========================================================================
BOARD_CSS = f"""
*{{box-sizing:border-box}}
html,body{{margin:0;background:#E9EAEC;font-family:{FONT_STACK};color:#16181B}}
.board{{width:2000px;padding:56px 64px 60px;display:flex;flex-direction:column;gap:28px}}
.head{{display:flex;justify-content:space-between;align-items:flex-end}}
.eyebrow{{font-size:17px;letter-spacing:.14em;text-transform:uppercase;color:#5C6169;font-weight:600}}
.title{{font-size:64px;font-weight:700;letter-spacing:-.02em;margin:6px 0 0;line-height:1}}
.pal{{font-size:22px;color:#5C6169;margin-top:10px}}
.note{{text-align:right;font-size:16px;color:#5C6169;line-height:1.5}}
.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:20px}}
.tile{{border-radius:18px;padding:22px;display:flex;flex-direction:column;gap:14px;position:relative}}
.tile .lab{{font-size:14px;letter-spacing:.12em;text-transform:uppercase;font-weight:600;opacity:.62}}
.light{{background:#FFFFFF}} .dark{{background:#111214;color:#F2F3F5}} .mid{{background:#D6D8DC}}
.center{{flex:1;display:flex;align-items:center;justify-content:center}}
.span2{{grid-column:span 2}} .row2{{grid-row:span 2}}
.iconstage{{background:linear-gradient(160deg,#F7F7F8,#D9DBDF)}}
.sizes{{display:flex;align-items:flex-end;gap:26px}} .sizes figure{{justify-content:flex-end}}
.sizes figure{{margin:0;display:flex;flex-direction:column;align-items:center;gap:8px;font-size:13px;color:inherit}}
.sizes figcaption{{opacity:.6;font-variant-numeric:tabular-nums}}
.px{{image-rendering:pixelated}}
.swatches{{display:flex;gap:14px;flex-wrap:wrap}}
.sw{{display:flex;flex-direction:column;gap:6px;font-size:13px}}
.sw-chip{{border-radius:12px;box-shadow:inset 0 0 0 1px rgba(0,0,0,.08)}}
.sw-name{{font-weight:600}} .sw-hex{{font-family:ui-monospace,"DejaVu Sans Mono",monospace;opacity:.7}}
.sym{{font-size:21px;line-height:1.55;max-width:60ch}}
.mbar{{display:flex;align-items:center;justify-content:flex-end;border-radius:8px}}
.mb-glyph{{display:inline-flex}} .mb-time{{font-weight:500;font-variant-numeric:tabular-nums}}
.mbwrap{{border-radius:12px;padding:16px;display:flex;flex-direction:column;gap:12px}}
.wall-l{{background:linear-gradient(120deg,#C9D6E8,#EAD9CF)}} .wall-d{{background:linear-gradient(120deg,#1B2433,#2B1F2E)}}
.meta{{font-size:15px;opacity:.7;line-height:1.5}}
"""


def board_html(c):
    d = cdir(c)
    p = os.path.join(d, "png")
    u = f"bd{c['num']}"
    sizes_l = "".join(
        f'<figure><img src="{file_url(os.path.join(p, f"app-icon-{s}.png"))}" width="{s}" height="{s}" alt="">'
        f'<figcaption>{s} px</figcaption></figure>' for s in (128, 64, 32, 16))
    zoom = "".join(
        f'<figure><img class="px" src="{file_url(os.path.join(p, f"app-icon-{s}.png"))}" width="{s * z}" height="{s * z}" alt="">'
        f'<figcaption>{s} px &times;{z}</figcaption></figure>' for s, z in ((32, 3), (16, 5)))
    fonts = ", ".join(sorted({font_label(k) for _, k, _ in c["font"]}))
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{BOARD_CSS}</style></head><body>
<div class="board">
 <div class="head">
  <div><div class="eyebrow">UnboundFS &middot; Phase 0 brand exploration &middot; {label(c)}</div>
   <div class="title">{label(c)} &mdash; {html.escape(c['name'])}</div>
   <div class="pal">{html.escape(c['palette_name'])} &middot; wordmark in {fonts} (outlined)</div></div>
  <div class="note">Concept for owner review<br>Not selected &middot; not final</div>
 </div>
 <div class="grid">
  <div class="tile iconstage span2 row2"><div class="lab">macOS app icon &middot; 1024 master</div>
   <div class="center">{inline_icon(c, u + "ic", 560)}</div></div>
  <div class="tile light"><div class="lab">Symbol &middot; light background</div><div class="center">{inline_symbol(c, "light", u + "sl", 230)}</div></div>
  <div class="tile dark"><div class="lab">Symbol &middot; dark background</div><div class="center">{inline_symbol(c, "dark", u + "sd", 230)}</div></div>
  <div class="tile light"><div class="lab">Monochrome &middot; black</div><div class="center">{inline_symbol(c, "mono-black", u + "mb", 200)}</div></div>
  <div class="tile dark"><div class="lab">Monochrome &middot; white</div><div class="center">{inline_symbol(c, "mono-white", u + "mw", 200)}</div></div>
  <div class="tile light span2"><div class="lab">Wordmark &middot; light</div><div class="center" style="padding:18px 0">{inline_wordmark(c, "light", u + "wl", 110)}</div></div>
  <div class="tile dark span2"><div class="lab">Wordmark &middot; dark</div><div class="center" style="padding:18px 0">{inline_wordmark(c, "dark", u + "wd", 110)}</div></div>
  <div class="tile mid span2"><div class="lab">Menu bar template &middot; 1&times; and Retina 2&times;</div>
   <div class="mbwrap wall-l">{menubar_html(c, u + "m1", "light")}{menubar_html(c, u + "m2", "light", 2)}</div>
   <div class="mbwrap wall-d">{menubar_html(c, u + "m3", "dark")}{menubar_html(c, u + "m4", "dark", 2)}</div></div>
  <div class="tile light span2"><div class="lab">Small sizes &middot; actual pixels, then magnified</div>
   <div class="sizes" style="flex:1;align-items:center">{sizes_l}<span style="width:24px"></span>{zoom}</div></div>
  <div class="tile light span2"><div class="lab">Palette</div>{swatches(c, 74)}
   <div class="meta">App icon background gradient {c['icon_bg'][0]} &rarr; {c['icon_bg'][1]}</div></div>
  <div class="tile light span2"><div class="lab">Symbolism</div><div class="sym">{html.escape(c['symbolism'])}</div></div>
 </div>
</div></body></html>"""


# ==========================================================================
# Phase 2b: comparison sheet, dock, menu bar, small sizes (PNG)
# ==========================================================================
def comparison_html():
    cards = []
    for c in CONCEPTS:
        u = f"cp{c['num']}"
        p = os.path.join(cdir(c), "png")
        small = "".join(f'<img src="{file_url(os.path.join(p, f"app-icon-{s}.png"))}" width="{s}" height="{s}" alt="">'
                        for s in (64, 32, 16))
        chips = "".join(f'<span style="background:{h}" title="{h}"></span>' for _, h in c["palette"])
        cards.append(f"""<div class="card">
  <div class="ch"><span class="num">{c['num']:02d}</span><span class="nm">{html.escape(c['name'])}</span><span class="pn">{html.escape(c['palette_name'])}</span></div>
  <div class="ic">{inline_icon(c, u + "i", 300)}</div>
  <div class="pair"><div class="pl">{inline_symbol(c, "light", u + "l", 96)}</div><div class="pd">{inline_symbol(c, "dark", u + "d", 96)}</div><div class="pl">{inline_symbol(c, "mono-black", u + "m", 96)}</div></div>
  <div class="wm">{inline_wordmark(c, "light", u + "w", 48)}</div>
  <div class="foot"><div class="small">{small}</div><div class="chips">{chips}</div></div>
</div>""")
    css = f"""*{{box-sizing:border-box}}html,body{{margin:0;background:#E7E8EA;font-family:{FONT_STACK};color:#16181B}}
.sheet{{width:2400px;padding:60px 64px 56px}}
.top{{display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:34px}}
.top h1{{font-size:58px;letter-spacing:-.02em;margin:0;line-height:1}} .top p{{margin:10px 0 0;font-size:22px;color:#5C6169}}
.top .r{{text-align:right;font-size:17px;color:#5C6169;line-height:1.5}}
.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:24px}}
.card{{background:#fff;border-radius:22px;padding:24px;display:flex;flex-direction:column;gap:18px}}
.ch{{display:flex;align-items:baseline;gap:12px}} .num{{font-size:15px;font-weight:700;letter-spacing:.1em;color:#5C6169}}
.nm{{font-size:30px;font-weight:700;letter-spacing:-.01em}} .pn{{margin-left:auto;font-size:15px;color:#5C6169}}
.ic{{display:flex;justify-content:center;background:linear-gradient(160deg,#F7F7F8,#DCDEE2);border-radius:16px;padding:14px 0}}
.pair{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}} .pair>div{{border-radius:12px;display:flex;justify-content:center;padding:12px 0}}
.pl{{background:#F4F5F6}} .pd{{background:#121315}}
.wm{{display:flex;justify-content:center;padding:6px 0}}
.foot{{display:flex;justify-content:space-between;align-items:flex-end}}
.small{{display:flex;gap:12px;align-items:flex-end}}
.chips{{display:flex}} .chips span{{width:26px;height:26px;border-radius:50%;margin-left:-6px;box-shadow:0 0 0 2px #fff}}
.bottom{{margin-top:30px;font-size:17px;color:#5C6169;display:flex;justify-content:space-between}}"""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body><div class="sheet">
<div class="top"><div><h1>UnboundFS &mdash; brand concepts</h1><p>Phase 0 &middot; eight logo and app icon directions &middot; Storage without boundaries.</p></div>
<div class="r">Each card: app icon &middot; symbol on light, dark, mono &middot; wordmark &middot; 64/32/16 px &middot; palette</div></div>
<div class="grid">{"".join(cards)}</div>
<div class="bottom"><span>Exploration only. No concept has been selected; the final logo, icon and colour theme await the owner's decision.</span><span>github.com/ish4ra/UnboundFS &middot; design/branding</span></div>
</div></body></html>"""


def dock_html():
    def dock(mode):
        wall = ("linear-gradient(135deg,#BFD3EA 0%,#E6D6E6 45%,#F3DCC9 100%)" if mode == "light"
                else "linear-gradient(135deg,#0E1626 0%,#24182E 55%,#2E1B1B 100%)")
        dock_bg = "rgba(255,255,255,0.38)" if mode == "light" else "rgba(30,30,34,0.45)"
        border = "rgba(255,255,255,0.55)" if mode == "light" else "rgba(255,255,255,0.14)"
        fg = "#1C1D20" if mode == "light" else "#ECEDEF"
        icons = "".join(
            f'<div class="di"><span class="tag" style="color:{fg}">{c["num"]:02d}</span>{inline_icon(c, f"dk{mode}{c["num"]}", 112)}</div>'
            for c in CONCEPTS)
        return (f'<div class="wall" style="background:{wall}"><div class="cap" style="color:{fg}">Dock preview &middot; '
                f'{mode} appearance</div><div class="dock" style="background:{dock_bg};border-color:{border}">{icons}</div></div>')
    css = f"""*{{box-sizing:border-box}}html,body{{margin:0;font-family:{FONT_STACK}}}
.wall{{width:1600px;height:300px;position:relative;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;padding-bottom:22px}}
.cap{{position:absolute;top:26px;left:32px;font-size:17px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;opacity:.75}}
.dock{{display:flex;gap:6px;padding:10px 12px;border-radius:30px;border:1px solid;backdrop-filter:blur(20px)}}
.di{{position:relative;display:flex;flex-direction:column;align-items:center;margin:-10px 0}}
.tag{{position:absolute;top:-24px;font-size:15px;font-weight:700;letter-spacing:.06em;opacity:.8}}"""
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{dock("light")}{dock("dark")}</body></html>'


def menubar_sheet_html():
    rows = []
    for c in CONCEPTS:
        rows.append(f'<div class="row"><div class="n"><b>{c["num"]:02d}</b> {html.escape(c["name"])}</div>'
                    f'<div class="wall-l mbw">{menubar_html(c, f"ms{c["num"]}l", "light", 2)}</div>'
                    f'<div class="wall-d mbw">{menubar_html(c, f"ms{c["num"]}d", "dark", 2)}</div></div>')
    css = f"""*{{box-sizing:border-box}}html,body{{margin:0;background:#E7E8EA;font-family:{FONT_STACK};color:#16181B}}
.sheet{{width:1600px;padding:40px 48px;display:flex;flex-direction:column;gap:14px}}
h1{{margin:0 0 10px;font-size:34px}} p{{margin:0 0 14px;color:#5C6169;font-size:17px}}
.row{{display:grid;grid-template-columns:200px 1fr 1fr;gap:16px;align-items:center}}
.n{{font-size:19px}} .mbw{{border-radius:12px;padding:12px}}
.wall-l{{background:linear-gradient(120deg,#C9D6E8,#EAD9CF)}} .wall-d{{background:linear-gradient(120deg,#1B2433,#2B1F2E)}}
.mbar{{display:flex;align-items:center;justify-content:flex-end;border-radius:8px}} .mb-glyph{{display:inline-flex}}
.mb-time{{font-weight:500;font-variant-numeric:tabular-nums}}"""
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body><div class="sheet">'
            f'<h1>Menu bar template icons</h1><p>Single-colour template glyphs (simplified where needed), shown at Retina 2&times; '
            f'on light and dark menu bars. Status items beside them are generic placeholders.</p>{"".join(rows)}</div></body></html>')


def small_sizes_html():
    rows = []
    for c in CONCEPTS:
        p = os.path.join(cdir(c), "png")
        act = "".join(f'<td><img src="{file_url(os.path.join(p, f"app-icon-{s}.png"))}" width="{s}" height="{s}" alt=""></td>'
                      for s in (128, 64, 32, 16))
        zoom = "".join(f'<td><img class="px" src="{file_url(os.path.join(p, f"app-icon-{s}.png"))}" width="{s * 4}" height="{s * 4}" alt=""></td>'
                       for s in (32, 16))
        mono = (f'<td><img class="px" src="{file_url(os.path.join(p, "menubar-template-18.png"))}" width="72" height="72" alt=""></td>')
        rows.append(f'<tr><th><b>{c["num"]:02d}</b> {html.escape(c["name"])}</th>{act}{zoom}{mono}</tr>')
    css = f"""*{{box-sizing:border-box}}html,body{{margin:0;background:#fff;font-family:{FONT_STACK};color:#16181B}}
.sheet{{width:1500px;padding:40px 48px}} h1{{margin:0 0 8px;font-size:34px}} p{{margin:0 0 20px;color:#5C6169;font-size:17px}}
table{{border-collapse:collapse;width:100%}} th,td{{padding:12px 10px;text-align:center;vertical-align:middle;border-bottom:1px solid #E6E7EA}}
th{{text-align:left;font-weight:500;font-size:18px;white-space:nowrap}} thead th{{font-size:14px;letter-spacing:.08em;text-transform:uppercase;color:#5C6169;text-align:center}}
.px{{image-rendering:pixelated}}"""
    head = ("<tr><th></th><th>128 px</th><th>64 px</th><th>32 px</th><th>16 px</th>"
            "<th>32 px &times;4</th><th>16 px &times;4</th><th>Menu bar 18 px &times;4</th></tr>")
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body><div class="sheet">'
            f'<h1>Small-size legibility</h1><p>App icons rasterised directly at each size (no hand hinting yet). '
            f'Magnified columns show the real pixels.</p><table><thead>{head}</thead><tbody>{"".join(rows)}</tbody></table>'
            f'</div></body></html>')


# ==========================================================================
# Phase 2c: gallery (self-contained HTML)
# ==========================================================================
SHORTLIST = [
    (4, "Keystone", "Most ownable. A true lettermark with a story about structural integrity, crisp at every size, "
                    "and the warm light icon stands apart from the usual dark utility icons."),
    (8, "Interlink", "The cleverest idea in the set: u and n, the same glyph rotated, physically linked. "
                     "Distinctive silhouette, strong two-colour system, works in one colour."),
    (1, "Beyond", "The most precise expression of the name: the nine-dot puzzle is solved only by leaving the box. "
                  "Calm, technical and very recognisable once seen."),
]


def gallery_body():
    pngs = {}
    for c in CONCEPTS:
        p = os.path.join(cdir(c), "png")
        pngs[c["num"]] = {s: data_uri(os.path.join(p, f"app-icon-{s}.png")) for s in (16, 32)}

    overview = "".join(
        f'<a class="ov" href="#c{c["num"]:02d}"><span class="ov-num">{c["num"]:02d}</span>'
        f'{inline_icon(c, f"g-ov{c["num"]}", 168)}<span class="ov-name">{html.escape(c["name"])}</span>'
        f'<span class="ov-pal">{html.escape(c["palette_name"])}</span></a>' for c in CONCEPTS)

    dock_icons = "".join(f'<div class="dk-i" title="{label(c)} {html.escape(c["name"])}">{inline_icon(c, f"g-dk{c["num"]}", 76)}'
                         f'<span>{c["num"]:02d}</span></div>' for c in CONCEPTS)

    menubars = "".join(
        f'<div class="mb-row"><span class="mb-n">{c["num"]:02d} {html.escape(c["name"])}</span>'
        f'<div class="mb-wall l">{menubar_html(c, f"g-mbl{c["num"]}", "light", 2)}</div>'
        f'<div class="mb-wall d">{menubar_html(c, f"g-mbd{c["num"]}", "dark", 2)}</div></div>' for c in CONCEPTS)

    details = []
    for c in CONCEPTS:
        u = f"g-d{c['num']}"
        sizes = "".join(f'<figure>{inline_icon(c, f"{u}s{s}", s, shadow=s >= 64)}<figcaption>{s}</figcaption></figure>'
                        for s in (128, 64, 32, 16))
        px = "".join(f'<figure><img class="px" src="{pngs[c["num"]][s]}" width="{s * 4}" height="{s * 4}" '
                     f'alt="{s} pixel raster of the {html.escape(c["name"])} icon, magnified"><figcaption>{s} px &times;4</figcaption></figure>'
                     for s in (32, 16))
        fonts = ", ".join(sorted({font_label(k) for _, k, _ in c["font"]}))
        details.append(f"""
<section class="concept" id="c{c['num']:02d}">
 <header class="c-head"><span class="c-num">Concept {c['num']:02d}</span><h2>{html.escape(c['name'])}</h2>
  <span class="c-pal">{html.escape(c['palette_name'])}</span></header>
 <p class="c-sym">{html.escape(c['symbolism'])}</p>
 <div class="c-grid">
  <div class="t t-icon"><span class="t-lab">App icon</span>{inline_icon(c, u + "ic", 300)}</div>
  <div class="t t-light"><span class="t-lab">Symbol, light</span>{inline_symbol(c, "light", u + "sl", 150)}</div>
  <div class="t t-dark"><span class="t-lab">Symbol, dark</span>{inline_symbol(c, "dark", u + "sd", 150)}</div>
  <div class="t t-light"><span class="t-lab">Mono black</span>{inline_symbol(c, "mono-black", u + "mb", 130)}</div>
  <div class="t t-dark"><span class="t-lab">Mono white</span>{inline_symbol(c, "mono-white", u + "mw", 130)}</div>
  <div class="t t-light t-wide"><span class="t-lab">Wordmark, light &middot; {html.escape(fonts)}</span>{inline_wordmark(c, "light", u + "wl", 64)}</div>
  <div class="t t-dark t-wide"><span class="t-lab">Wordmark, dark</span>{inline_wordmark(c, "dark", u + "wd", 64)}</div>
  <div class="t t-plain t-wide"><span class="t-lab">Small sizes (vector, then real pixels)</span><div class="sizes">{sizes}{px}</div></div>
  <div class="t t-plain t-wide"><span class="t-lab">Palette</span>{swatches(c, 44)}</div>
 </div>
</section>""")

    pal_rows = "".join(
        f'<div class="pr"><span class="pr-n">{c["num"]:02d} {html.escape(c["name"])}</span><div class="pr-chips">' +
        "".join(f'<span class="pr-c" style="background:{h}"><em>{h}</em></span>' for _, h in c["palette"]) +
        "</div></div>" for c in CONCEPTS)

    wms = "".join(
        f'<div class="wmr"><span class="pr-n">{c["num"]:02d}</span><div class="wm-l">{inline_wordmark(c, "light", f"g-wl{c["num"]}", 44)}</div>'
        f'<div class="wm-d">{inline_wordmark(c, "dark", f"g-wd{c["num"]}", 44)}</div></div>' for c in CONCEPTS)

    shortlist = "".join(
        f'<li><a href="#c{n:02d}">{inline_icon(next(c for c in CONCEPTS if c["num"] == n), f"g-sl{n}", 56, False)}</a>'
        f'<div><b>Concept {n:02d} &middot; {nm}</b><p>{html.escape(why)}</p></div></li>' for n, nm, why in SHORTLIST)

    return f"""
<header class="hero"><div class="wrap">
 <p class="eyebrow">UnboundFS &middot; Phase 0 &middot; Brand identity review</p>
 <h1>Eight directions for a filesystem utility that crosses platforms.</h1>
 <p class="lede">Each concept has an app icon, a standalone symbol, light, dark and monochrome versions, a menu bar template,
 a wordmark and its own palette. Nothing here is final: the owner picks the direction, and refinements follow from that choice.</p>
 <div class="hero-actions"><button id="themeBtn" type="button" class="btn">Switch to dark</button>
 <a class="btn ghost" href="#overview">Overview</a><a class="btn ghost" href="#dock">Dock</a><a class="btn ghost" href="#menubar">Menu bar</a>
 <a class="btn ghost" href="#palettes">Palettes</a><a class="btn ghost" href="#wordmarks">Wordmarks</a></div>
</div></header>
<main class="wrap">
 <section id="overview"><h3 class="sec">Overview</h3><div class="ov-grid">{overview}</div></section>
 <section id="dock"><h3 class="sec">In the Dock</h3>
  <div class="dk-wall"><div class="dk">{dock_icons}</div></div>
  <p class="cap">All eight icons side by side on a desktop. The wallpaper and dock follow the page theme.</p></section>
 <section id="menubar"><h3 class="sec">Menu bar</h3>
  <p class="cap">Template glyphs at Retina 2&times;, simplified where the full symbol is too detailed for 16 pt. The status items beside them are placeholders.</p>
  <div class="mb-list">{menubars}</div></section>
 {"".join(details)}
 <section id="palettes"><h3 class="sec">Palettes compared</h3><div class="pr-list">{pal_rows}</div>
  <p class="cap">Palettes belong to their concept. The application colour theme is decided only after a concept is approved.</p></section>
 <section id="wordmarks"><h3 class="sec">Wordmarks compared</h3><div class="wm-list">{wms}</div>
  <p class="cap">All lettering is converted to outlines from SIL Open Font License typefaces, so it renders the same everywhere.</p></section>
 <section id="shortlist"><h3 class="sec">Reviewer shortlist (advisory)</h3>
  <ol class="sl">{shortlist}</ol>
  <p class="cap">A suggestion only. All eight concepts stay open, and the decision belongs to the project owner.</p></section>
</main>
<footer class="wrap foot">UnboundFS brand concepts &middot; Phase 0 &middot; awaiting owner selection. Application development has not started.</footer>
"""


GALLERY_CSS = """
/* Layout: one centred column; concept sections are a dense tile grid that stacks at phone width. */
:root{--bg:#F3F4F5;--fg:#15171A;--muted:#5D636B;--card:#FFFFFF;--line:#E1E3E6;--ink:#111214;--paper:#FFFFFF;--stage:#E6E8EB;
 --wall:linear-gradient(135deg,#BFD3EA 0%,#E6D6E6 45%,#F3DCC9 100%);--dock:rgba(255,255,255,.4);--dockline:rgba(255,255,255,.6);
 --font:"Inter",-apple-system,BlinkMacSystemFont,"Segoe UI",system-ui,sans-serif;--mono:ui-monospace,"SF Mono",Menlo,monospace}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#0F1113;--fg:#ECEEF0;--muted:#9AA1AA;--card:#181B1F;--line:#2A2E33;--stage:#1F2328;
 --wall:linear-gradient(135deg,#0E1626 0%,#24182E 55%,#2E1B1B 100%);--dock:rgba(40,40,46,.5);--dockline:rgba(255,255,255,.14);color-scheme:dark}}
:root[data-theme="dark"]{--bg:#0F1113;--fg:#ECEEF0;--muted:#9AA1AA;--card:#181B1F;--line:#2A2E33;--stage:#1F2328;
 --wall:linear-gradient(135deg,#0E1626 0%,#24182E 55%,#2E1B1B 100%);--dock:rgba(40,40,46,.5);--dockline:rgba(255,255,255,.14);color-scheme:dark}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--fg);font-family:var(--font);font-size:15px;line-height:1.5;margin:0}
.wrap{max-width:1180px;margin:0 auto;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
.hero{padding-block:56px 28px}
.eyebrow{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);font-weight:600;margin:0 0 12px}
.hero h1{font-size:clamp(28px,4.4vw,46px);line-height:1.08;letter-spacing:-.02em;margin:0;max-width:20ch;text-wrap:balance}
.lede{color:var(--muted);max-width:64ch;font-size:16px;margin:16px 0 0}
.hero-actions{display:flex;flex-wrap:wrap;gap:8px;margin-top:22px}
.btn{font:inherit;font-size:13px;font-weight:600;padding:8px 14px;border-radius:999px;border:1px solid var(--fg);background:var(--fg);color:var(--bg);cursor:pointer;text-decoration:none}
.btn.ghost{background:transparent;color:var(--fg);border-color:var(--line)}
.btn:focus-visible,a:focus-visible{outline:2px solid var(--fg);outline-offset:2px}
section{padding-block:28px}
.sec{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);font-weight:700;margin:0 0 16px}
.cap{color:var(--muted);font-size:13px;margin:12px 0 0}
.ov-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px}
.ov{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:16px 12px 16px;display:flex;flex-direction:column;align-items:center;gap:4px;color:inherit;text-decoration:none;position:relative}
.ov svg{max-width:100%;height:auto}
.ov-num{position:absolute;top:12px;left:14px;font-size:12px;font-weight:700;color:var(--muted);font-variant-numeric:tabular-nums}
.ov-name{font-weight:700;font-size:17px} .ov-pal{color:var(--muted);font-size:12px}
.dk-wall{background:var(--wall);border-radius:18px;padding:90px 12px 18px;display:flex;justify-content:center;overflow-x:auto}
.dk{display:flex;gap:4px;padding:8px 10px;border-radius:24px;background:var(--dock);border:1px solid var(--dockline);backdrop-filter:blur(18px)}
.dk-i{display:flex;flex-direction:column;align-items:center;margin:-8px 0 -4px}
.dk-i svg{width:clamp(34px,7vw,76px);height:auto} .dk-i span{font-size:10px;font-weight:700;opacity:.7}
.mb-list{display:flex;flex-direction:column;gap:10px}
.mb-row{display:grid;grid-template-columns:150px minmax(0,1fr) minmax(0,1fr);gap:10px;align-items:center}
.mb-n{font-size:13px;font-weight:600}
.mb-wall{border-radius:12px;padding:10px;overflow:hidden} .mb-wall.l{background:linear-gradient(120deg,#C9D6E8,#EAD9CF)} .mb-wall.d{background:linear-gradient(120deg,#1B2433,#2B1F2E)}
.mbar{display:flex;align-items:center;justify-content:flex-end;border-radius:8px;white-space:nowrap}
.mb-glyph{display:inline-flex} .mb-time{font-weight:500;font-variant-numeric:tabular-nums}
.concept{border-top:1px solid var(--line);padding-block:40px}
.c-head{display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 14px}
.c-num{font-size:12px;letter-spacing:.14em;text-transform:uppercase;font-weight:700;color:var(--muted)}
.c-head h2{margin:0;font-size:clamp(26px,3.4vw,36px);letter-spacing:-.02em}
.c-pal{color:var(--muted);font-size:14px}
.c-sym{max-width:68ch;font-size:16px;margin:10px 0 22px}
.c-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}
.t{border-radius:16px;padding:14px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;min-width:0;position:relative;min-height:190px}
.t svg{max-width:100%;height:auto}
.t-lab{align-self:flex-start;font-size:11px;letter-spacing:.1em;text-transform:uppercase;font-weight:600;opacity:.62}
.t-icon{grid-column:span 2;grid-row:span 2;background:var(--stage)}
.t-light{background:var(--paper);color:#15171A;border:1px solid var(--line)} .t-dark{background:var(--ink);color:#ECEEF0;border:1px solid var(--line)}
.t-plain{background:var(--card);border:1px solid var(--line)}
.t-wide{grid-column:span 2}
.sizes{display:flex;flex-wrap:wrap;align-items:flex-end;gap:16px}
.sizes figure{margin:0;display:flex;flex-direction:column;align-items:center;gap:4px}
.sizes figcaption{font-size:11px;color:var(--muted);font-variant-numeric:tabular-nums}
.px{image-rendering:pixelated}
.swatches{display:flex;flex-wrap:wrap;gap:10px;align-self:stretch}
.sw{display:flex;flex-direction:column;gap:3px;font-size:11px}
.sw-chip{border-radius:10px;box-shadow:inset 0 0 0 1px rgba(127,127,127,.25)}
.sw-name{font-weight:600} .sw-hex{font-family:var(--mono);color:var(--muted)}
.pr-list,.wm-list{display:flex;flex-direction:column;gap:8px}
.pr{display:grid;grid-template-columns:150px minmax(0,1fr);gap:10px;align-items:center}
.pr-n{font-size:13px;font-weight:600}
.pr-chips{display:flex;border-radius:10px;overflow:hidden;min-width:0}
.pr-c{flex:1;height:44px;display:flex;align-items:flex-end;padding:4px;min-width:0}
.pr-c em{font-style:normal;font-family:var(--mono);font-size:10px;background:rgba(0,0,0,.45);color:#fff;border-radius:4px;padding:0 4px;white-space:nowrap;overflow:hidden}
.wmr{display:grid;grid-template-columns:40px minmax(0,1fr) minmax(0,1fr);gap:10px;align-items:center}
.wm-l,.wm-d{border-radius:12px;padding:14px;display:flex;justify-content:center;min-width:0}
.wm-l{background:var(--paper);border:1px solid var(--line)} .wm-d{background:var(--ink);border:1px solid var(--line)}
.wm-l svg,.wm-d svg{max-width:100%;height:auto}
.sl{list-style:none;padding:0;margin:0;display:grid;gap:12px}
.sl li{display:flex;gap:14px;align-items:flex-start;background:var(--card);border:1px solid var(--line);border-radius:16px;padding:14px}
.sl p{margin:4px 0 0;color:var(--muted);max-width:70ch}
.foot{color:var(--muted);font-size:13px;padding-block:28px 48px;border-top:1px solid var(--line)}
@media (max-width:820px){.ov-grid,.c-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.mb-row{grid-template-columns:minmax(0,1fr)}
 .pr{grid-template-columns:minmax(0,1fr)} .wmr{grid-template-columns:30px minmax(0,1fr)} .wm-d{grid-column:2}}
@media (max-width:480px){.t-icon,.t-wide{grid-column:span 2}.pr-c em{display:none}}
@media (prefers-reduced-motion:no-preference){.ov{transition:transform .15s ease}.ov:hover{transform:translateY(-2px)}}
"""

GALLERY_JS = """
(function(){var b=document.getElementById('themeBtn');var r=document.documentElement;
function cur(){var t=r.getAttribute('data-theme');if(t)return t;return matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light'}
function sync(){b.textContent=cur()==='dark'?'Switch to light':'Switch to dark'}
b.addEventListener('click',function(){var n=cur()==='dark'?'light':'dark';r.setAttribute('data-theme',n);try{localStorage.setItem('ubfs-theme',n)}catch(e){}sync()});
try{var s=localStorage.getItem('ubfs-theme');if(s)r.setAttribute('data-theme',s)}catch(e){}
sync();matchMedia('(prefers-color-scheme: dark)').addEventListener('change',sync)})();
"""


def build_gallery():
    import svgkit
    title = "UnboundFS Brand Concepts"
    svgkit.SQ_REF = "ubfs-squircle"
    body = (f'<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>'
            f'<path id="ubfs-squircle" d="{SQUIRCLE}"/></defs></svg>') + gallery_body()
    svgkit.SQ_REF = None
    full = (f'<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
            f'<title>{title}</title><style>{GALLERY_CSS}</style></head><body>{body}<script>{GALLERY_JS}</script></body></html>\n')
    write(os.path.join(ROOT, "gallery.html"), full)
    # Artifact flavour: the viewer supplies the document skeleton.
    frag = (f'<title>{title}</title><meta name="claude:viewport-fit-sides" content="cover">'
            f'<style>{GALLERY_CSS}</style>{body}<script>{GALLERY_JS}</script>\n')
    write(os.path.join(BUILD, "gallery-artifact.html"), frag)


# ==========================================================================
# README
# ==========================================================================
GH = "https://github.com/ish4ra/UnboundFS/blob/{branch}/design/branding/"


def build_readme():
    rows = []
    for c in CONCEPTS:
        d = rel(cdir(c))
        prev = f"previews/concept-{c['num']:02d}-{c['slug']}.png"
        hexes = ", ".join(f"`{h}`" for _, h in c["palette"])
        rows.append(f"| {c['num']:02d} | **{c['name']}** | {c['palette_name']} | [board]({prev}) · [files]({d}/) | {hexes} |")
    sections = []
    for c in CONCEPTS:
        d = rel(cdir(c))
        prev = f"previews/concept-{c['num']:02d}-{c['slug']}.png"
        pal = "\n".join(f"| {n} | `{h}` |" for n, h in c["palette"])
        fonts = ", ".join(sorted({font_label(k) for _, k, _ in c["font"]}))
        sections.append(f"""### Concept {c['num']:02d} — {c['name']}

<img src="{d}/png/app-icon-256.png" width="128" alt="{c['name']} app icon"> <img src="{d}/png/symbol-1024.png" width="128" alt="{c['name']} symbol">

{c['symbolism']}

![Concept {c['num']:02d} board]({prev})

| Colour | HEX |
|---|---|
{pal}

App icon background: `{c['icon_bg'][0]}` → `{c['icon_bg'][1]}` · Wordmark: {fonts} (outlined)

Files: [`{d}/`]({d}/)
""")
    text = f"""# UnboundFS — Phase 0 brand concepts

> **Status: exploration only. No concept has been selected.** The final logo, app icon and
> application colour theme are waiting on the project owner's decision. Application development
> has not started.

Eight original logo and app icon directions for **UnboundFS**, *Storage without boundaries.*

## Quick view

- **[comparison.png](comparison.png)**: all eight concepts on one sheet
- **[gallery.html](gallery.html)**: interactive, self-contained gallery with light and dark modes (download and open locally; GitHub shows HTML as source)
- **[previews/](previews/)**: one presentation board per concept, plus Dock, menu bar and small-size sheets

![All eight concepts](comparison.png)

| # | Concept | Palette | Preview | HEX |
|---|---|---|---|---|
{chr(10).join(rows)}

## Shared previews

| Sheet | What it shows |
|---|---|
| [previews/dock.png](previews/dock.png) | All icons in a Dock, light and dark desktops |
| [previews/menubar.png](previews/menubar.png) | Monochrome template glyphs in light and dark menu bars (Retina 2×) |
| [previews/small-sizes.png](previews/small-sizes.png) | 128/64/32/16 px rasters, magnified to show real pixels |

## The concepts

{chr(10).join(sections)}

## What is in each concept folder

| File | Purpose |
|---|---|
| `app-icon.svg` | macOS app icon master, 1024 × 1024 canvas, 824 px rounded-square body |
| `symbol.svg` | Standalone symbol, transparent, for light backgrounds |
| `symbol-reversed.svg` | Standalone symbol, transparent, for dark backgrounds |
| `symbol-mono-black.svg` / `symbol-mono-white.svg` | Single-colour versions |
| `menubar-template.svg` | Black-only template glyph (simplified when needed) for the menu bar |
| `wordmark*.svg` | Symbol + UnboundFS lettering (outlined), colour, reversed and mono |
| `palette.json` | Exact palette, icon background and typeface |
| `png/app-icon-{{16…1024}}.png` | App icon rendered at 16, 32, 64, 128, 256, 512 and 1024 px |
| `png/symbol*-1024.png` | Transparent 1024 px symbol renders |
| `png/wordmark*@2x.png`, `png/menubar-template-{{18,36}}.png` | Raster wordmarks and menu bar glyphs |

## Notes and limitations

- **Typefaces.** Wordmarks use Manrope, Space Grotesk, Inter Display, Inter, Outfit, Fraunces,
  JetBrains Mono and Sora, all under the SIL Open Font License 1.1. Text is converted to vector outlines,
  so no fonts need to be installed or shipped to view the assets.
- **App icon shape.** The icon body is a superellipse approximating the macOS continuous-corner shape on
  Apple's 1024 px grid. Before release, the chosen icon should be checked against Apple's current macOS
  icon template, including the layered Icon Composer format introduced with macOS Tahoe 26.
- **Small sizes.** The 16 and 32 px images are straight rasterisations. A finished icon set would get
  hand-tuned small sizes.
- **Originality.** The designs were made from scratch for this project. A preliminary web search found no
  product called "UnboundFS". This is not a trademark search or legal clearance; see the review notes in the
  phase report before adopting a mark.
- **Rebuilding.** Everything here is generated by [`tools/`](tools/) (Python + headless Chromium). See
  [`tools/README.md`](tools/README.md).
"""
    write(os.path.join(ROOT, "README.md"), text)


def build_pages():
    os.makedirs(BUILD, exist_ok=True)
    jobs = []
    pages = {"comparison": (comparison_html(), os.path.join(ROOT, "comparison.png"), 2400),
             "dock": (dock_html(), os.path.join(ROOT, "previews", "dock.png"), 1600),
             "menubar": (menubar_sheet_html(), os.path.join(ROOT, "previews", "menubar.png"), 1600),
             "small": (small_sizes_html(), os.path.join(ROOT, "previews", "small-sizes.png"), 1500)}
    for c in CONCEPTS:
        pages[f"board{c['num']}"] = (board_html(c), os.path.join(ROOT, "previews", f"concept-{c['num']:02d}-{c['slug']}.png"), 2000)
    for key, (doc, out, w) in pages.items():
        hp = os.path.join(BUILD, f"{key}.html")
        write(hp, doc)
        jobs.append(dict(html=hp, out=out, w=w, h=800, fullPage=True))
    write(os.path.join(BUILD, "jobs-pages.json"), json.dumps(jobs, indent=1))
    build_gallery()
    build_readme()
    print(f"pages: {len(jobs)} PNG jobs, gallery.html, README.md")


if __name__ == "__main__":
    {"assets": build_assets, "pages": build_pages}[sys.argv[1]]()
