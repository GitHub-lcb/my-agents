import os
import shutil
from asar_lib import Asar

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = r"E:\develop-lcb\workspace-tools\ToolCove\qoder-design-spec\assets"
os.makedirs(OUT, exist_ok=True)

a = Asar()
# exact asset names discovered earlier
want = {}
for p, s, _ in a.files:
    base = p.rsplit("/", 1)[-1]
    if p.startswith("out/renderer/application-icons/"):
        want[p] = "icons/" + base
    elif base.startswith("qoder-loading-line-") and base.endswith(".svg"):
        want[p] = "brand/" + base
    elif base in ("Qoduck01-Dwn546pz.webp", "glass-light-BX6cg1om.webp", "glass-dark-Bl3KGVjk.webp",
                  "beeDoodle-CFIaPhTT.webp", "Qoduck03-CaD-CBFW.webp", "empty-DCjnVihL.webp"):
        want[p] = "illustrations/" + base
    elif base.startswith("qoder-loading-line") or base in ("app-icon.ico",):
        want[p] = "brand/" + base

# also grab first few duck / sticker examples by pattern
picked = 0
for p, s, _ in a.files:
    base = p.rsplit("/", 1)[-1]
    if picked >= 8:
        break
    if p.startswith("out/renderer/assets/") and base.endswith(".webp") and any(
            k in base for k in ("Qoduck", "duck", "glass", "first-use", "empty", "failed")):
        if p not in want:
            want[p] = "illustrations/" + base
            picked += 1

for src, rel in want.items():
    dest = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    try:
        a.extract(src, os.path.join(OUT, ".."))  # extract keeps path structure
        real = os.path.join(OUT, "..", src)
        shutil.move(real, dest)
    except Exception as e:
        print("skip", src, e)

# install-dir icons (larger)
res = r"E:\develop-lcb\apps\Qoder CN\.qoder-versions\0.5.7\resources"
for f in os.listdir(os.path.join(res, "application-icons")):
    shutil.copy2(os.path.join(res, "application-icons", f), os.path.join(OUT, "icons", f))
for f in ("app-icon.ico",):
    p = os.path.join(res, f)
    if os.path.exists(p):
        shutil.copy2(p, os.path.join(OUT, "brand", f))
p = os.path.join(res, "tray", "tray.ico")
if os.path.exists(p):
    shutil.copy2(p, os.path.join(OUT, "brand", "tray.ico"))

for root, dirs, files in os.walk(OUT):
    for f in files:
        p = os.path.join(root, f)
        print(f"{os.path.getsize(p)/1024:8.1f} KB  {p.replace(OUT, '')}")
