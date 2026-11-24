"""Validate the production UnboundFS brand assets in design/brand/."""
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

from PIL import Image
from PIL.IcnsImagePlugin import IcnsFile

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
REPO = os.path.dirname(os.path.dirname(ROOT))
sys.path.insert(0, TOOLS)
import shear  # noqa: E402

problems, n = [], {"svg": 0, "png": 0, "links": 0}


def bad(msg):
    problems.append(msg)


# 1. Identity: production geometry must equal the approved Phase 0 concept.
sys.path.insert(0, os.path.join(REPO, "design", "archive", "phase-0-branding", "tools"))
import concepts  # noqa: E402

norm = lambda s: re.sub(r'(id="|url\(#)[^"\)]*', "", s)
for ctx in ("light", "dark", "mono-black"):
    for simple in (False, True):
        a = concepts.sym_shear(dict(concepts.contexts(concepts.CONCEPTS[4])[ctx]), "x", simple=simple)
        b = shear.symbol(shear.CTX[ctx], "x", "menubar" if simple else "full")
        if norm(a) != norm(b):
            bad(f"identity: {ctx} {'menubar' if simple else 'full'} symbol differs from approved Concept 05")
if [c[1] for c in shear.PALETTE] != ["#121316", "#25282E", "#878D97", "#D3D7DD", "#FBFBFC", "#FF5A2C"]:
    bad("palette differs from the approved palette")

# 2. Files
for dp, dirs, files in os.walk(ROOT):
    if "/tools" in dp:
        continue
    for fn in files:
        path = os.path.join(dp, fn)
        rel = os.path.relpath(path, ROOT)
        if fn.endswith(".svg"):
            n["svg"] += 1
            try:
                root = ET.parse(path).getroot()
            except ET.ParseError as e:
                bad(f"{rel}: XML error {e}")
                continue
            txt = open(path).read()
            if not root.get("viewBox"):
                bad(f"{rel}: no viewBox")
            if "<text" in txt:
                bad(f"{rel}: live text")
            ids = set(re.findall(r'id="([^"]+)"', txt))
            for r1, r2 in re.findall(r'url\(#([^)]+)\)|href="#([^"]+)"', txt):
                if (r1 or r2) not in ids:
                    bad(f"{rel}: dangling #{r1 or r2}")
        elif fn.endswith(".png"):
            n["png"] += 1
            im = Image.open(path)
            m = re.search(r"-(\d+)\.png$", fn)
            if m and ("unboundfs-symbol" in fn or "AppIcon-" in fn):
                s = int(m.group(1))
                if im.size != (s, s):
                    bad(f"{rel}: {im.size} != {s}x{s}")
            transparent = any(k in rel for k in ("logo/", "wordmark/", "menubar/", "AppIcon"))
            if transparent:
                if im.mode != "RGBA":
                    bad(f"{rel}: no alpha")
                    continue
                a = im.getchannel("A")
                w, h = im.size
                if a.getpixel((0, 0)) or a.getpixel((w - 1, h - 1)):
                    bad(f"{rel}: corners not transparent")
                if a.getextrema()[1] == 0:
                    bad(f"{rel}: empty image")
            if "menubar/" in rel:
                rgb = im.convert("RGBA")
                if any(px[3] and px[:3] != (0, 0, 0) for px in rgb.getdata()):
                    bad(f"{rel}: template image must be black + alpha only")

# 3. Icon packaging
expect = {(16, 16, 1), (16, 16, 2), (32, 32, 1), (32, 32, 2), (128, 128, 1), (128, 128, 2), (256, 256, 1),
          (256, 256, 2), (512, 512, 1), (512, 512, 2)}
with open(os.path.join(ROOT, "app-icon", "AppIcon.icns"), "rb") as fh:
    got = set(IcnsFile(fh).itersizes())
if got != expect:
    bad(f"AppIcon.icns sizes {sorted(got)}")
for setdir in ("AppIcon.iconset", "Assets.xcassets/AppIcon.appiconset"):
    d = os.path.join(ROOT, "app-icon", setdir)
    for pt, sc in [(s[0], s[2]) for s in expect]:
        f = os.path.join(d, f"icon_{pt}x{pt}{'@2x' if sc == 2 else ''}.png")
        if not os.path.exists(f):
            bad(f"{setdir}: missing {os.path.basename(f)}")
        elif Image.open(f).size != (pt * sc, pt * sc):
            bad(f"{setdir}: wrong size {os.path.basename(f)}")
cj = json.load(open(os.path.join(ROOT, "app-icon", "Assets.xcassets", "AppIcon.appiconset", "Contents.json")))
if len(cj["images"]) != 10:
    bad("AppIcon.appiconset Contents.json should list 10 images")
mj = json.load(open(os.path.join(ROOT, "menubar", "Assets.xcassets", "UnboundFSMenubar.imageset", "Contents.json")))
if mj["properties"].get("template-rendering-intent") != "template":
    bad("menu bar image set is not a template image")

# 4. Fixed-size deliverables
sizes = {"github/readme-banner-light.png": (2560, 640), "github/readme-banner-dark.png": (2560, 640),
         "github/social-preview.png": (1280, 640), "promo/unboundfs-hero-light-2560x1440.png": (2560, 1440),
         "promo/unboundfs-hero-dark-2560x1440.png": (2560, 1440), "promo/unboundfs-square-1080.png": (1080, 1080),
         "menubar/UnboundFSMenubarTemplate.png": (18, 18), "menubar/UnboundFSMenubarTemplate@2x.png": (36, 36)}
for rel, s in sizes.items():
    if Image.open(os.path.join(ROOT, rel)).size != s:
        bad(f"{rel}: expected {s}")

# 5. Links in documentation
for doc in (os.path.join(ROOT, "README.md"), os.path.join(ROOT, "GUIDELINES.md"), os.path.join(REPO, "README.md")):
    if not os.path.exists(doc):
        bad(f"missing {doc}")
        continue
    base = os.path.dirname(doc)
    for l1, l2, l3 in re.findall(r'\]\(([^)#\s]+)\)|src="([^"]+)"|srcset="([^"]+)"', open(doc).read()):
        link = l1 or l2 or l3
        if link.startswith(("http", "mailto:")):
            continue
        n["links"] += 1
        if not os.path.exists(os.path.join(base, link)):
            bad(f"{os.path.relpath(doc, REPO)}: broken link {link}")

print(f"identity checks passed: {not any(p.startswith('identity') or p.startswith('palette') for p in problems)}")
print(f"checked {n['svg']} SVG, {n['png']} PNG, ICNS + 2 icon sets, {n['links']} doc links")
print("\n".join(problems) if problems else "no problems found")
sys.exit(1 if problems else 0)
