import os
import re
import json
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "extracted", "out", "renderer", "assets")


def parse_blocks(css):
    """Return list of (chain, decls) where chain is selector/at-rule stack."""
    out = []
    stack = []  # list of (kind, text)  kind in {'at','rule'}
    buf = []
    i = 0
    n = len(css)
    while i < n:
        ch = css[i]
        if ch == "{":
            prelude = "".join(buf).strip()
            buf = []
            if prelude.startswith("@") and not prelude.startswith("@keyframes") or prelude.startswith("@media") or prelude.startswith("@supports") or prelude.startswith("@layer") or prelude.startswith("@container"):
                stack.append(("at", prelude))
            else:
                stack.append(("rule", prelude))
        elif ch == "}":
            if stack:
                kind, text = stack.pop()
                if kind == "rule":
                    pass
            # when closing a rule, its decls were already captured? need different approach
            buf = []
        i += 1
    return out


def parse_decls(css):
    """Yield (chain_str, decls) for each leaf rule block, handling nesting."""
    results = []
    stack = []  # frames: dict(kind, prelude, decls)
    buf = []
    i = 0
    n = len(css)
    while i < n:
        ch = css[i]
        if ch == "{":
            prelude = "".join(buf).strip()
            buf = []
            if prelude.startswith("@") and not prelude.startswith("@font-face") and not prelude.startswith("@page"):
                stack.append({"kind": "at", "prelude": prelude, "decls": []})
            else:
                stack.append({"kind": "rule", "prelude": prelude, "decls": []})
        elif ch == "}":
            if stack:
                frame = stack.pop()
                chain = " | ".join(f["prelude"] for f in stack if f["kind"] == "at")
                if frame["kind"] == "rule":
                    tail = "".join(buf).strip()
                    if tail:
                        frame["decls"].append(tail)
                    results.append((chain, frame["prelude"], frame["decls"]))
                else:
                    attext = frame["prelude"]
                    # block content for @font-face etc is in decls? we didn't collect
            buf = []
        elif ch == ";":
            if stack and stack[-1]["kind"] == "rule":
                stack[-1]["decls"].append("".join(buf).strip())
            elif stack and stack[-1]["kind"] == "at":
                # inside at-rule directly (rare)
                pass
            buf = []
        else:
            buf.append(ch)
        i += 1
    return results


def split_decl(d):
    if ":" in d:
        k, v = d.split(":", 1)
        return k.strip(), v.strip()
    return None, None


files = ["styles-eCOZTk0p.css", "index-BFGCOCH4.css"]
var_defs = defaultdict(list)  # var -> list of (selector, atchain, value)
class_var = {}  # class -> set of vars used in its decls
class_decls = defaultdict(dict)

for fname in files:
    css = open(os.path.join(BASE, fname), encoding="utf-8", errors="replace").read()
    rules = parse_decls(css)
    print(fname, "rules:", len(rules))
    for atchain, sel, decls_list in rules:
        for d in decls_list:
            k, v = split_decl(d)
            if not k:
                continue
            if k.startswith("--"):
                var_defs[k].append((sel, atchain, v))
        # map classes in selector -> vars used
        sels = [s.strip() for s in sel.split(",")]
        for s in sels:
            if s.startswith(".") and len(s) < 120:
                m = re.match(r"^\.([A-Za-z][\w-]*)", s)
                if m:
                    cls = m.group(1)
                    for d in decls_list:
                        k, v = split_decl(d)
                        if k and v and "var(--q" in v:
                            mm = re.search(r"var\((--q[0-9a-f]{6})", v)
                            if mm:
                                class_decls[cls][k] = mm.group(1)

print("vars defined:", len(var_defs))

# find var defining for a few semantic classes
for cls in ["bg-bg-container", "bg-bg-base", "text-primary", "text-secondary", "border-border", "bg-bg-elevated"]:
    print(cls, "->", class_decls.get(cls))

# which selectors define vars (top)
selc = defaultdict(int)
for var, lst in var_defs.items():
    for sel, atc, v in lst:
        selc[(atc, sel)] += 1
print("\n== top selector/at contexts defining vars ==")
for (atc, sel), cnt in sorted(selc.items(), key=lambda x: -x[1])[:20]:
    print(f"{cnt:5d}  at={atc[:60]!r} sel={sel[:80]!r}")

with open(os.path.join(HERE, "token_defs.json"), "w", encoding="utf-8") as fh:
    json.dump({k: v for k, v in var_defs.items()}, fh, ensure_ascii=False, indent=2)
with open(os.path.join(HERE, "class_var.json"), "w", encoding="utf-8") as fh:
    json.dump({k: v for k, v in class_decls.items()}, fh, ensure_ascii=False, indent=2)
print("\nsaved token_defs.json / class_var.json")
