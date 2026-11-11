import os
from asar_lib import Asar

a = Asar()

print("== node_modules/@qoder-space/* (top-level dirs declared in header) ==")
node = a.header["files"]["node_modules"]["files"]
for name in sorted(node):
    if name.startswith("@qoder-space") or name.startswith("@ali") or name == "@qoder":
        sub = node[name]["files"]
        for pkg in sorted(sub):
            files = sub[pkg].get("files", {})
            total = sum(v.get("size", 0) for v in files.values() if "size" in v)
            print(f"  {name}/{pkg}   ({len(files)} entries, {total/1024:.0f} KB)")

print("\n== design-system files ==")
prefix = "node_modules/@qoder-space/design-system/"
rows = sorted([(p, s) for p, s, _ in a.files if p.startswith(prefix)], key=lambda x: -x[1])
print("count:", len(rows), "total KB:", sum(s for _, s in rows) // 1024)
for p, s in rows[:60]:
    print(f"{s/1024:9.1f} KB  {p[len(prefix):]}")

print("\n== markdown docs in asar ==")
for p, s, _ in sorted([(p, s) for p, s, _ in a.files if p.endswith(".md")], key=lambda x: -x[1])[:30]:
    print(f"{s/1024:9.1f} KB  {p}")
