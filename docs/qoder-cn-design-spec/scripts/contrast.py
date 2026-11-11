import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
matrix = json.load(open(os.path.join(HERE, "theme_matrix.json"), encoding="utf-8"))

def hex2rgb(h):
    h = h.strip()
    if not h.startswith("#"):
        return None
    h = h[1:]
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) == 8:
        h = h[:6]
    if len(h) != 6:
        return None
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def lum(h):
    rgb = hex2rgb(h)
    if not rgb:
        return None
    def f(c):
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (f(x) for x in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def contrast(a, b):
    la, lb = lum(a), lum(b)
    if la is None or lb is None:
        return None
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)

def grade(c):
    if c is None:
        return "n/a"
    if c >= 7:
        return "AAA"
    if c >= 4.5:
        return "AA"
    if c >= 3:
        return "AA-large"
    return "FAIL"

themes = ["light", "dark", "forest-light", "forest-dark", "bee-light", "bee-dark",
          "mint-light", "mint-dark", "light-parchment", "parchment-dark"]
fg = ["text", "text-secondary", "text-tertiary", "text-quaternary", "primary", "primary-text",
      "link", "success", "warning", "error", "info"]

print("== 对比度检查（文字色 vs bg-container）==")
print(f"{'token':<16}" + "".join(f"{t[:12]:<14}" for t in themes))
fail_count = 0
for tok in fg:
    line = f"{tok:<16}"
    for t in themes:
        bg = matrix["bg-container"][t]
        c = matrix.get(tok, {}).get(t)
        r = contrast(c, bg) if c and bg else None
        g = grade(r)
        if g in ("FAIL", "AA-large"):
            fail_count += 1
        line += f"{g}({r:.1f})".ljust(14) if r else "-".ljust(14)
    print(line)

print("\n== 对比度检查（text vs bg-base）==")
for tok in ["text", "text-secondary", "text-tertiary", "text-quaternary"]:
    line = f"{tok:<16}"
    for t in themes:
        bg = matrix["bg-base"][t]
        c = matrix.get(tok, {}).get(t)
        r = contrast(c, bg) if c and bg else None
        line += f"{grade(r)}({r:.1f})".ljust(14) if r else "-".ljust(14)
    print(line)

print("\n== text-on-primary vs primary 按钮对比度 ==")
for t in themes:
    p = matrix["primary"][t]
    f = matrix["text-on-primary"][t]
    r = contrast(f, p)
    print(f"  {t:<16} {grade(r):<9} {r:.2f}   (fg={f} bg={p})")

print("\n== 关键结论 ==")
print("统计：文字 token 在各主题下未达 AA(4.5) 的数量 =", fail_count)

# find theme transition duration across all extracted css
BASE = os.path.join(HERE, "extracted", "out", "renderer", "assets")
for f in os.listdir(BASE):
    if not f.endswith(".css"):
        continue
    t = open(os.path.join(BASE, f), encoding="utf-8", errors="replace").read()
    m = re.search(r"--q26f0e9:\s*([^;}]+)", t)
    if m:
        print(f"\ntheme transition duration --q26f0e9 found in {f}: {m.group(1)}")
for f in os.listdir(BASE):
    if not f.endswith(".js"):
        continue
    t = open(os.path.join(BASE, f), encoding="utf-8", errors="replace").read()
    for mm in re.finditer(r"--q26f0e9", t):
        print(f"  in {f}: ...{t[max(0,mm.start()-160):mm.start()+80]}...")
        break
