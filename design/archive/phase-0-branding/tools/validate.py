"""Validate the generated brand-concept deliverables."""
import os, re, sys, xml.etree.ElementTree as ET
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
problems, counts = [], {"svg": 0, "png": 0, "links": 0}

for dp, _, files in os.walk(ROOT):
    if "/tools" in dp:
        continue
    for fn in files:
        p = os.path.join(dp, fn)
        r = os.path.relpath(p, ROOT)
        if fn.endswith(".svg"):
            counts["svg"] += 1
            try:
                root = ET.parse(p).getroot()
            except ET.ParseError as e:
                problems.append(f"{r}: XML error {e}"); continue
            if not root.get("viewBox"):
                problems.append(f"{r}: missing viewBox")
            txt = open(p).read()
            if "<text" in txt:
                problems.append(f"{r}: live <text> (should be outlined)")
            ids = set(re.findall(r'id="([^"]+)"', txt))
            for ref in re.findall(r'url\(#([^)]+)\)|href="#([^"]+)"', txt):
                ref = ref[0] or ref[1]
                if ref not in ids:
                    problems.append(f"{r}: dangling reference #{ref}")
            if re.search(r"nan|inf", " ".join(re.findall(r'd="([^"]+)"', txt))):
                problems.append(f"{r}: invalid path data")
        elif fn.endswith(".png"):
            counts["png"] += 1
            im = Image.open(p)
            m = re.search(r"-(\d+)\.png$", fn)
            s = int(m.group(1)) if m else 0
            if m and ("app-icon" in fn or "symbol" in fn or "menubar" in fn):
                if im.size != (s, s):
                    problems.append(f"{r}: size {im.size}, expected {s}x{s}")
            if dp.endswith("/png"):
                if im.mode != "RGBA":
                    problems.append(f"{r}: no alpha channel"); continue
                a = im.getchannel("A")
                w, h = im.size
                if a.getpixel((0, 0)) != 0 or a.getpixel((w - 1, h - 1)) != 0:
                    problems.append(f"{r}: corner not transparent")
                if a.getextrema()[1] == 0:
                    problems.append(f"{r}: image is empty")
                if "app-icon" in fn and s >= 256:
                    # nothing may touch the canvas edge except shadow; body is 824/1024
                    bbox = a.point(lambda v: 255 if v > 200 else 0).getbbox()
                    lo, hi = s * 0.09, s * 0.91
                    if bbox[0] < lo or bbox[1] < lo or bbox[2] > hi + s * 0.02 or bbox[3] > hi + s * 0.03:
                        problems.append(f"{r}: icon body outside grid {bbox}")
            elif "comparison" in fn or "previews" in dp:
                if im.size[0] < 1400:
                    problems.append(f"{r}: preview too small {im.size}")

for doc in ["README.md"]:
    txt = open(os.path.join(ROOT, doc)).read()
    for link in re.findall(r'\]\(([^)#]+)\)|src="([^"]+)"', txt):
        link = link[0] or link[1]
        if link.startswith("http"):
            continue
        counts["links"] += 1
        if not os.path.exists(os.path.join(ROOT, link)):
            problems.append(f"{doc}: broken link {link}")

print(f"checked {counts['svg']} SVG, {counts['png']} PNG, {counts['links']} README links")
print("\n".join(problems) if problems else "no problems found")
sys.exit(1 if problems else 0)
