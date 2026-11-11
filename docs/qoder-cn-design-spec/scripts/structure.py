import json
from asar_lib import Asar

a = Asar()

pkg = json.loads(a.read("package.json"))
print("== package.json ==")
print(json.dumps(pkg, ensure_ascii=False, indent=2)[:4000])

print("\n== out tree (dirs) ==")
dirs = {}
for p, s, _ in a.files:
    if not p.startswith("out/"):
        continue
    parts = p.split("/")
    key = "/".join(parts[:3])
    d = dirs.setdefault(key, [0, 0])
    d[0] += 1
    d[1] += s
for k in sorted(dirs):
    print(f"{dirs[k][0]:5d} files {dirs[k][1]/1024/1024:9.1f} MB  {k}")

print("\n== out/renderer/assets js/css top 25 ==")
rows = sorted([(s, p) for p, s, _ in a.files if p.startswith("out/renderer/assets/") and p.endswith((".js", ".css"))], reverse=True)
for s, p in rows[:25]:
    print(f"{s/1024:9.1f} KB  {p}")
print("count js in renderer/assets:", sum(1 for _, p in rows if p.endswith('.js')))
