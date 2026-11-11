import os
import shutil
from asar_lib import Asar

HERE = os.path.dirname(os.path.abspath(__file__))
DST = r"E:\develop-lcb\workspace-tools\ToolCove\qoder-design-spec\assets\fonts"
os.makedirs(DST, exist_ok=True)

a = Asar()
want = {
    "instrument-sans-latin-400-normal-DRC__1Mx.woff2": "instrument-sans-400.woff2",
    "instrument-sans-latin-500-normal-Dk9ku72i.woff2": "instrument-sans-500.woff2",
    "inter-latin-400-normal-C38fXH4l.woff2": "inter-400.woff2",
    "inter-latin-500-normal-Cerq10X2.woff2": "inter-500.woff2",
    "inter-latin-600-normal-LgqL8muc.woff2": "inter-600.woff2",
    "qoder-seti-De-nE9UX.woff": "qoder-seti.woff",
}
found = 0
for p, s, _ in a.files:
    base = p.rsplit("/", 1)[-1]
    if base in want:
        dest = os.path.join(DST, want[base])
        with open(dest, "wb") as fh:
            fh.write(a.read(p))
        found += 1
        print(f"{s/1024:8.1f} KB -> {want[base]}")
print("copied", found)
