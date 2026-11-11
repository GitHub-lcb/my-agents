import os
import re

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extracted", "out", "renderer", "assets")
hits = {}
for f in sorted(os.listdir(BASE)):
    if not f.endswith(".css"):
        continue
    t = open(os.path.join(BASE, f), encoding="utf-8", errors="replace").read()
    n = t.count("aura-buddy")
    if n:
        hits[f] = (n, t)

print("files containing aura-buddy:", {k: v[0] for k, v in hits.items()})
for f, (n, t) in hits.items():
    print("\n=====", f, "size", len(t))
    kfs = re.findall(r"@keyframes\s+([A-Za-z0-9_-]+)", t)
    print("keyframes:", kfs)
    # print a slice around first aura-buddy occurrence
    i = t.find("aura-buddy")
    print(t[max(0, i - 300):i + 3000][:3500])
