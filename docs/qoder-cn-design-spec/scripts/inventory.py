import sys
from collections import Counter, defaultdict
from asar_lib import Asar

a = Asar()

# top-level grouping
top = Counter()
for p, s, _ in a.files:
    top[p.split("/")[0]] += 1
print("== top-level entries ==")
for k, v in top.most_common(40):
    print(f"{v:6d}  {k}")

exts = Counter()
for p, s, _ in a.files:
    e = p.rsplit(".", 1)[-1].lower() if "." in p.split("/")[-1] else "(none)"
    exts[e] += 1
print("\n== extensions ==")
for k, v in exts.most_common(30):
    print(f"{v:6d}  .{k}")

print("\n== CSS files (top 40 by size) ==")
css = sorted([(s, p) for p, s, _ in a.files if p.endswith(".css")], reverse=True)
print("count:", len(css), "total KB:", sum(s for s, _ in css) // 1024)
for s, p in css[:40]:
    print(f"{s/1024:9.1f} KB  {p}")

print("\n== theme-ish json (top 40) ==")
th = sorted([(s, p) for p, s, _ in a.files if p.endswith(".json") and any(k in p.lower() for k in ("theme", "color", "token", "design", "style"))], reverse=True)
print("count:", len(th))
for s, p in th[:40]:
    print(f"{s/1024:9.1f} KB  {p}")

print("\n== fonts ==")
for p, s, _ in sorted(a.files, key=lambda x: -x[1]):
    if p.lower().endswith((".ttf", ".otf", ".woff", ".woff2")):
        print(f"{s/1024:9.1f} KB  {p}")
