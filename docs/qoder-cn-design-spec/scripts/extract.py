import os
from asar_lib import Asar

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extracted")
a = Asar()

want = []
for p, s, _ in a.files:
    if p == "out/renderer/index.html":
        want.append(p)
    elif p.startswith("out/renderer/assets/") and p.endswith(".css"):
        want.append(p)
    elif p.startswith("out/renderer/assets/") and p.endswith(".svg"):
        want.append(p)
    elif p.startswith("out/renderer/application-icons/"):
        want.append(p)
    elif p in ("out/main/index.js",):
        want.append(p)

# top JS bundles (renderer UI logic)
js = sorted([(s, p) for p, s, _ in a.files if p.startswith("out/renderer/assets/") and p.endswith(".js")], reverse=True)
for s, p in js[:12]:
    want.append(p)

total = 0
for p in want:
    dest = a.extract(p, OUT)
    total += os.path.getsize(dest)
print(f"extracted {len(want)} files, {total/1024/1024:.1f} MB -> {OUT}")

# asset name inventory (no extraction) for icons/webp
names = [p.rsplit("/", 1)[-1] for p, s, _ in a.files if p.startswith("out/renderer/assets/") and p.endswith(".webp")]
print("webp assets:", len(names))
print("\n".join("  " + n for n in sorted(names)[:60]))
