import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "extracted", "out", "renderer", "assets")


def parse_decls(css):
    results = []
    stack = []
    buf = []
    for ch in css:
        if ch == "{":
            prelude = "".join(buf).strip()
            buf = []
            kind = "at" if (prelude.startswith("@") and not prelude.startswith("@font-face")) else "rule"
            stack.append({"kind": kind, "prelude": prelude, "decls": []})
        elif ch == "}":
            if stack:
                frame = stack.pop()
                if frame["kind"] == "rule":
                    tail = "".join(buf).strip()
                    if tail:
                        frame["decls"].append(tail)
                    results.append((frame["prelude"], frame["decls"], frame.get("at")))
                buf = []
        elif ch == ";":
            if stack and stack[-1]["kind"] == "rule":
                stack[-1]["decls"].append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
    return results


files = sys.argv[1].split(",") if len(sys.argv) > 1 else ["styles-eCOZTk0p.css", "index-BFGCOCH4.css"]
patterns = sys.argv[2:] or ["typeset", "markdown-body"]
for fname in files:
    css = open(os.path.join(BASE, fname), encoding="utf-8", errors="replace").read()
    rules = parse_decls(css)
    for pat in patterns:
        print("\n" + "=" * 100)
        print("FILE:", fname, "PATTERN:", pat)
        hits = [(s, d) for s, d, _ in rules if pat in s]
        print("rules:", len(hits))
        for s, d in hits[:40]:
            print("\n--- " + s[:300])
            for dd in d[:30]:
                print("    " + dd[:300])
