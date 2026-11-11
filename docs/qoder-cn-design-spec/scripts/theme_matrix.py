import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
rows = json.load(open(os.path.join(HERE, "semantic_tokens.json"), encoding="utf-8"))
css = open(os.path.join(HERE, "extracted/out/renderer/assets/styles-eCOZTk0p.css"), encoding="utf-8", errors="replace").read()
ds = open(os.path.join(HERE, "extracted/out/renderer/assets/index-BFGCOCH4.css"), encoding="utf-8", errors="replace").read()

THEMES = ["light", "dark", "forest-light", "forest-dark", "bee-light", "bee-dark",
          "mint-light", "mint-dark", "light-parchment", "parchment-dark"]

FOCUS = ["bg-base", "bg-container", "bg-elevated", "bg-layout", "bg-spotlight",
         "text", "text-secondary", "text-tertiary", "text-quaternary", "text-on-primary",
         "border", "border-secondary", "border-tertiary", "border-quaternary",
         "fill", "fill-secondary", "fill-tertiary",
         "primary", "primary-hover", "primary-active", "primary-text", "primary-bg", "primary-border",
         "link", "success", "warning", "error", "info"]

by_token = {r["token"]: r for r in rows}


def value_for(token, theme):
    r = by_token.get(token)
    if not r:
        return "-"
    ov = r.get("overrides") or {}
    if theme in ov:
        return ov[theme]
    is_dark = theme.endswith("dark")
    v = r["dark"] if is_dark else r["light"]
    if not v:
        v = r["root_default"] or r["light"] or r["dark"]
    return v or "-"


print("== 主题色彩矩阵（部分关键 token）==")
header = f"{'token':<18}" + "".join(f"{t[:13]:<15}" for t in THEMES)
print(header)
for tok in FOCUS:
    line = f"{tok:<18}"
    for t in THEMES:
        v = str(value_for(tok, t))
        line += f"{v[:14]:<15}"
    print(line)

# theme transition duration
print("\n== theme transition duration var ==")
m = re.search(r"--q26f0e9:\s*([^;}]+)", css)
print("  --q26f0e9 =", m.group(1) if m else "not found")

# base body / html typography
print("\n== base html/body rules ==")
for pat in [r"body\{[^}]*\}", r"html\{[^}]*\}", r"html,body\{[^}]*\}"]:
    for mm in list(re.finditer(pat, css))[:3]:
        print("  ", mm.group(0)[:300])

print("\n== :root font settings ==")
for mm in re.finditer(r":root\{([^}]{0,600})\}", css):
    body = mm.group(1)
    if "font" in body or "color-scheme" in body:
        print("  ", body[:400])

# collect theme palette summary -> save
matrix = {tok: {t: value_for(tok, t) for t in THEMES} for tok in FOCUS}
with open(os.path.join(HERE, "theme_matrix.json"), "w", encoding="utf-8") as fh:
    json.dump(matrix, fh, ensure_ascii=False, indent=2)
print("\nsaved theme_matrix.json")
