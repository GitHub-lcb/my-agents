import json
import os
import re
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
token_defs = json.load(open(os.path.join(HERE, "token_defs.json"), encoding="utf-8"))
class_var = json.load(open(os.path.join(HERE, "class_var.json"), encoding="utf-8"))

THEMES = ["light", "dark", "forest-light", "forest-dark", "bee-light", "bee-dark",
          "mint-light", "mint-dark", "parchment-light", "parchment-dark"]

# ---- recover full theme selector lists ----
css = open(os.path.join(HERE, "extracted/out/renderer/assets/styles-eCOZTk0p.css"), encoding="utf-8", errors="replace").read()
theme_sels = set()
for m in re.finditer(r"([^{}]{0,400}data-theme=[a-z-]+[^{}]{0,400})\{", css):
    for part in m.group(1).split(","):
        part = part.strip()
        if "data-theme=" in part:
            theme_sels.add(part)
print("== theme selectors found ==")
for s in sorted(theme_sels):
    print("  ", s)


def theme_of(sel):
    """classify a selector into base-light / base-dark / theme override / root-default"""
    if "data-theme" not in sel:
        if sel.strip() in (":root", ":root,:host", "html", "html,:host"):
            return "root-default"
        return None
    names = re.findall(r"data-theme=([a-z-]+)", sel)
    if not names:
        return None
    if len(names) > 1:
        if any(n.endswith("-light") or n == "light" for n in names):
            return "base-light"
        if any(n.endswith("-dark") or n == "dark" for n in names):
            return "base-dark"
        return "group-other"
    n = names[0]
    if n in ("light", "dark"):
        return "base-" + n
    return n  # e.g. mint-light


def resolve(var):
    vals = {}
    for sel, atc, val in token_defs.get(var, []):
        t = theme_of(sel)
        if t:
            vals[t] = val.strip()
    return vals


# ---- semantic classes -> token name ----
UTIL = ["bg", "text", "border", "ring", "outline", "divide", "fill", "stroke", "from", "via", "to",
        "shadow", "accent", "caret", "decoration", "placeholder"]
STD = re.compile(r"^(red|blue|green|yellow|purple|pink|orange|teal|cyan|indigo|violet|fuchsia|rose|sky|emerald|lime|amber|neutral|slate|gray|zinc|stone|white|black|transparent|current|inherit)(-|$)")

tokens = defaultdict(lambda: {"classes": set(), "var": None, "props": set()})
for cls, decls in class_var.items():
    m = re.match(r"^(" + "|".join(UTIL) + r")-(.+)$", cls)
    if not m:
        continue
    util, rest = m.group(1), m.group(2)
    if STD.match(rest):
        continue
    if rest.endswith(("-0", "-0.5", "-1", "-2", "-3", "-4", "-5", "-6", "-8", "-10", "-12", "-16", "-20", "-24", "-32", "-40", "-48", "-56", "-64")):
        continue
    var = None
    for prop, v in decls.items():
        var = v
        break
    if not var:
        continue
    # token name: rest may already encode utility (bg-container, text-secondary)
    tokens[rest]["classes"].add(cls)
    tokens[rest]["var"] = var
    tokens[rest]["props"].update(decls.keys())

print("\n== distinct semantic tokens:", len(tokens))
rows = []
for name in sorted(tokens):
    info = tokens[name]
    vals = resolve(info["var"])
    rows.append({
        "token": name,
        "var": info["var"],
        "classes": sorted(info["classes"])[:4],
        "props": sorted(info["props"]),
        "root_default": vals.get("root-default"),
        "light": vals.get("base-light"),
        "dark": vals.get("base-dark"),
        "overrides": {k: v for k, v in vals.items() if k not in ("root-default", "base-light", "base-dark")},
    })

with open(os.path.join(HERE, "semantic_tokens.json"), "w", encoding="utf-8") as fh:
    json.dump(rows, fh, ensure_ascii=False, indent=2)

for r in rows:
    print(f"  {r['token']:<28} {r['var']:<10} light={str(r['light'])[:24]:<26} dark={str(r['dark'])[:24]:<26} overrides={list(r['overrides'])[:4]}")
