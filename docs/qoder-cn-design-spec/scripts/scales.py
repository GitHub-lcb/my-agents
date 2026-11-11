import json
import os
import re
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "extracted", "out", "renderer", "assets")
files = [f for f in os.listdir(BASE) if f.endswith(".css")]
texts = {f: open(os.path.join(BASE, f), encoding="utf-8", errors="replace").read() for f in files}
main = texts["styles-eCOZTk0p.css"]
allcss = "\n".join(texts.values())

report = {}

# ---------- 1. theme-layer scales ----------
print("===== @layer theme tokens =====")
theme_match = re.search(r"@layer theme\{(.*?)@layer", main, re.S)
theme = theme_match.group(1) if theme_match else ""
named = dict(re.findall(r"(--[A-Za-z0-9-]+)\s*:\s*([^;{}]+)", theme))
scale_groups = defaultdict(dict)
for k, v in named.items():
    m = re.match(r"--(text|radius|font-weight|leading|tracking|spacing|container|blur|shadow|ease|animate|font|color|breakpoint|perspective|aspect|drop-shadow)", k)
    if m:
        scale_groups[m.group(1)][k] = v.strip()
for g in sorted(scale_groups):
    print(f"\n[{g}]")
    for k in sorted(scale_groups[g]):
        print(f"  {k}: {scale_groups[g][k][:120]}")
report["theme_scales"] = {g: dict(v) for g, v in scale_groups.items()}

# ---------- 2. keyframes + animations ----------
print("\n\n===== keyframes =====")
kf = []
for f, t in texts.items():
    for m in re.finditer(r"@keyframes\s+([A-Za-z0-9_-]+)\s*\{", t):
        kf.append((m.group(1), f))
print("count:", len(kf), "unique:", len({k for k, _ in kf}))
print(", ".join(sorted({k for k, _ in kf})))
report["keyframes"] = sorted({k for k, _ in kf})

# animation shorthand usages
anims = re.findall(r"animation:\s*([^;{}]+)", allcss)
durs = Counter()
eases = Counter()
for a in anims:
    for d in re.findall(r"(?<![\w.-])(\d+(?:\.\d+)?)(m?s)\b", a):
        durs[d[0] + d[1]] += 1
    for e in re.findall(r"(cubic-bezier\([^)]*\)|linear|ease-in-out|ease-out|ease-in|ease|steps\([^)]*\)|spring)", a):
        eases[e] += 1
print("\n== animation durations (top 25) ==")
for k, v in durs.most_common(25):
    print(f"{v:5d}  {k}")
print("\n== animation easings (top 20) ==")
for k, v in eases.most_common(20):
    print(f"{v:5d}  {k}")

# transition durations/easings
td = Counter(re.findall(r"transition(?:-duration)?:\s*([^;{}]+)", allcss))
trans_vals = Counter()
for t in td:
    for m in re.findall(r"(?<![\w.-])(\d+(?:\.\d+)?)(m?s)\b", t):
        trans_vals[m[0] + m[1]] += 1
print("\n== transition durations (top 25) ==")
for k, v in trans_vals.most_common(25):
    print(f"{v:5d}  {k}")

# cubic-bezier frequency
cb = Counter(re.findall(r"cubic-bezier\([^)]*\)", allcss))
print("\n== cubic-bezier frequency (top 25) ==")
for k, v in cb.most_common(25):
    print(f"{v:5d}  {k}")

report["animation_durations"] = dict(durs.most_common(40))
report["transition_durations"] = dict(trans_vals.most_common(40))
report["easings"] = dict(cb.most_common(40))

# ---------- 3. z-index ----------
zi = Counter(re.findall(r"z-index:\s*(-?\d+)", allcss))
print("\n== z-index values ==")
for k, v in sorted(zi.items(), key=lambda x: int(x[0])):
    print(f"  z={k}: {v}")

# ---------- 4. breakpoints ----------
bp = Counter()
for m in re.finditer(r"@media[^{]*?\(min-width:\s*([\d.]+)(px|rem|em)\)", allcss):
    bp[m.group(1) + m.group(2)] += 1
for m in re.finditer(r"@media[^{]*?\(max-width:\s*([\d.]+)(px|rem|em)\)", allcss):
    bp["max-" + m.group(1) + m.group(2)] += 1
print("\n== breakpoints ==")
for k, v in bp.most_common(20):
    print(f"  {k}: {v}")

# ---------- 5. common utility values (design scale usage) ----------
def top_values(prefix, n=15, lim=6):
    pat = re.compile(r"\." + prefix + r"([\w\\./\[\]-]+)\s*\{")
    c = Counter()
    for name in pat.findall(main):
        if len(name) <= lim:
            c[name.replace("\\", "")] += 1
    return c.most_common(n)

print("\n== rounded-* values in use ==")
rad = Counter(re.findall(r"\.[\w-]*rounded(?:-[a-z0-9]+)?\{[^}]*border-radius:\s*([^;}]*)", main))
for k, v in rad.most_common(20):
    print(f"{v:4d}  {k[:60]}")
print("\n== shadow values in use ==")
sh = Counter(re.findall(r"box-shadow:\s*([^;}]*)", main))
for k, v in sh.most_common(18):
    print(f"{v:4d}  {k[:110]}")
print("\n== font-size values in use ==")
fs = Counter(re.findall(r"font-size:\s*([^;}]*)", main))
for k, v in fs.most_common(18):
    print(f"{v:4d}  {k[:80]}")
print("\n== line-height values in use ==")
lh = Counter(re.findall(r"line-height:\s*([^;}]*)", main))
for k, v in lh.most_common(14):
    print(f"{v:4d}  {k[:60]}")
print("\n== font-weight values ==")
fw = Counter(re.findall(r"font-weight:\s*([^;}]*)", allcss))
for k, v in fw.most_common(12):
    print(f"{v:4d}  {k[:40]}")

# ---------- 6. reduced motion ----------
rm = allcss.count("prefers-reduced-motion")
print("\nprefers-reduced-motion occurrences:", rm)
with open(os.path.join(HERE, "scales.json"), "w", encoding="utf-8") as fh:
    json.dump(report, fh, ensure_ascii=False, indent=2)
print("\nsaved scales.json")
