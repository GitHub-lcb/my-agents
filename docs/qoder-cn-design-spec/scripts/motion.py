import os
import re
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "extracted", "out", "renderer", "assets")
js_files = [f for f in os.listdir(BASE) if f.endswith(".js")]
print("js files:", len(js_files))

# pick main bundles only (>100KB) to keep it fast
big = [f for f in js_files if os.path.getsize(os.path.join(BASE, f)) > 100_000]
print("big js:", len(big))

fonts = Counter()
springs = Counter()
tweens = Counter()
easings = Counter()
durations = Counter()
layout_ids = Counter()

for f in big:
    t = open(os.path.join(BASE, f), encoding="utf-8", errors="replace").read()
    for fam in ["Instrument Sans", "Crimson Pro", "Dynamic Island Inter", "Inter", "qoder-seti"]:
        if fam in t:
            fonts[fam] += t.count(fam)
    for m in re.finditer(r"stiffness:\s*([\d.]+)\s*,\s*damping:\s*([\d.]+)\s*,\s*mass:\s*([\d.]+)", t):
        springs[m.groups()] += 1
    for m in re.finditer(r"damping:\s*([\d.]+)\s*,\s*stiffness:\s*([\d.]+)", t):
        springs[(m.group(2), m.group(1), "?")] += 1
    for m in re.finditer(r'type:\s*"spring"\s*,\s*stiffness:\s*([\d.]+)\s*,\s*damping:\s*([\d.]+)', t):
        springs[(m.group(1), m.group(2), "?")] += 1
    for m in re.finditer(r"duration:\s*(0?\.\d+|\d+(?:\.\d+)?)", t):
        durations[m.group(1)] += 1
    for m in re.finditer(r"ease:\s*\[([^\]]{3,60})\]", t):
        easings["[" + m.group(1).replace(" ", "") + "]"] += 1
    for m in re.finditer(r'ease:\s*"([a-zA-Z.]+)"', t):
        easings[m.group(1)] += 1
    for m in re.finditer(r'ease:\s*"(power\d?\.(?:in|out|inOut)|back\.(?:in|out)|circ\.(?:in|out)|expo\.(?:in|out))"', t):
        easings["gsap:" + m.group(1)] += 1

print("\n== font family mentions in JS ==")
for k, v in fonts.most_common():
    print(f"{v:6d}  {k}")

print("\n== framer-motion spring configs (stiffness,damping,mass) ==")
for k, v in springs.most_common(20):
    print(f"{v:5d}  {k}")

print("\n== tween durations ==")
for k, v in sorted(durations.items(), key=lambda x: -x[1])[:25]:
    print(f"{v:5d}  {k}s")

print("\n== ease values ==")
for k, v in easings.most_common(25):
    print(f"{v:5d}  {k}")
