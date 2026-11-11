import os
import re
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "extracted", "out", "renderer", "assets")
s = open(os.path.join(BASE, "styles-eCOZTk0p.css"), encoding="utf-8", errors="replace").read()
ds = open(os.path.join(BASE, "index-BFGCOCH4.css"), encoding="utf-8", errors="replace").read()
allcss = s + ds

print("===== aura-buddy: keyframes (durations/easing) =====")
for m in re.finditer(r"@keyframes\s+(aura-buddy-[A-Za-z0-9_-]+)\s*\{(?:[^{}]|\{[^{}]*\})*\}", allcss):
    name = m.group(1)
    body = m.group(0)
    anims = re.findall(r"animation:\s*([^;{}]+)", body)
    tf = len(re.findall(r"\d+%\{", body))
    print(f"  {name:<42} keyframe steps={tf:<3} inner animations={anims[:3]}")

print("\n===== aura-buddy: class rules (count) =====")
ab = re.findall(r"\.[\w-]*aura-buddy[\w-]*(?:[^{]*?)\{[^}]*\}", allcss)
print("rules:", len(ab))
for r in ab[:12]:
    print("  ", r[:180])

print("\n===== spacing utility usage (gap/p/m) =====")
for pref in ["gap", "p", "px", "py", "pt", "pb", "pl", "pr", "m", "mx", "my", "space-y", "rounded", "h", "w", "size"]:
    pat = re.compile(r"\." + pref + r"-(\d+(?:\.\d+)?|px|\[[^\]]+\])(?![0-9])\b")
    c = Counter(pat.findall(s))
    total = sum(c.values())
    print(f"{pref:<8} total={total:<5} top: " + ", ".join(f"{k}×{v}" for k, v in c.most_common(8)))

print("\n===== raw border-radius values =====")
br = Counter(re.findall(r"border-radius:\s*([^;}]*)", allcss))
for k, v in br.most_common(20):
    print(f"{v:5d}  {k[:80]}")

print("\n===== raw box-shadow (non tw-var) values =====")
sh = [x for x in re.findall(r"box-shadow:\s*([^;}]*)", allcss) if "var(--tw-inset-shadow)" not in x]
print("count non-tw:", len(sh))
c = Counter(sh)
for k, v in c.most_common(20):
    print(f"{v:5d}  {k[:120]}")

print("\n===== backdrop-filter usage =====")
bf = Counter(re.findall(r"backdrop-filter:\s*([^;}]*)", allcss))
for k, v in bf.most_common(15):
    print(f"{v:5d}  {k[:100]}")

print("\n===== data-attribute design contracts =====")
attrs = Counter(re.findall(r"\[(data-[a-z-]+)[\]=]", allcss))
for k, v in attrs.most_common(40):
    print(f"{v:5d}  [{k}]")
