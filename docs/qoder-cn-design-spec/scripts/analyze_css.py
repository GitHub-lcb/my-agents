import os
import re
from collections import Counter, defaultdict

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extracted", "out", "renderer", "assets")

css_files = [f for f in os.listdir(BASE) if f.endswith(".css")]
print("css files:", css_files)

texts = {}
for f in css_files:
    with open(os.path.join(BASE, f), encoding="utf-8", errors="replace") as fh:
        texts[f] = fh.read()

main = texts["styles-eCOZTk0p.css"]
print("main css chars:", len(main))

# 1. custom property declarations
decls = re.findall(r"--([A-Za-z0-9_-]+)\s*:\s*([^;}]+)", main)
print("\n== custom property declarations total:", len(decls), "unique names:", len({d[0] for d in decls}))

# group by prefix pattern: --q + hex-like suffix (hashed) vs named
hashed = [n for n, _ in decls if re.fullmatch(r"q[0-9a-f]{6}", n)]
named = [n for n, _ in decls if not re.fullmatch(r"q[0-9a-f]{6}", n)]
print("hashed tokens:", len(set(hashed)), " named tokens:", len(set(named)))
print("\n== named tokens (non-hashed) sample ==")
for n in sorted(set(named))[:120]:
    print("  --" + n)

# 2. class name vocabulary: extract selectors
sels = re.findall(r"\.([a-zA-Z][A-Za-z0-9_-]*)\s*[,{:>\s\[]", main)
c = Counter(sels)
print("\n== class name count:", len(c))
prefixes = Counter()
for name, cnt in c.items():
    for pre in ["bg-", "text-", "border-", "rounded-", "shadow-", "p-", "px-", "py-", "pt-", "pb-", "pl-", "pr-",
                "m-", "mx-", "my-", "gap-", "space-", "w-", "h-", "size-", "font-", "leading-", "tracking-",
                "flex", "grid", "items-", "justify-", "z-", "duration-", "ease-", "animate-", "transition-",
                "hover:", "focus:", "disabled:", "data-", "dark:", "group", "peer", "opacity-", "ring-", "divide-"]:
        if name.startswith(pre):
            prefixes[pre] += cnt
print("\n== utility prefixes ==")
for k, v in prefixes.most_common(40):
    print(f"{v:6d}  {k}")

print("\n== top 60 classes ==")
for name, cnt in c.most_common(60):
    print(f"{cnt:5d}  .{name}")

# 3. font-family
print("\n== font-family declarations ==")
for m in set(re.findall(r"font-family\s*:\s*([^;}]+)", main)):
    print("  ", m[:160])

# 4. keyframes
kf = set(re.findall(r"@keyframes\s+([A-Za-z0-9_-]+)", main))
print("\n== keyframes:", len(kf))
print("  " + ", ".join(sorted(kf)[:80]))

# 5. media queries
mq = Counter(re.findall(r"@media[^{]+", main))
print("\n== media queries (top 25) ==")
for k, v in mq.most_common(25):
    print(f"{v:4d}  {k.strip()[:120]}")

# 6. selectors defining theme blocks
print("\n== theme-ish selectors ==")
for m in set(re.findall(r"([^{}]{0,80}(?:\.dark|data-theme|data-mode|color-scheme)[^{}]{0,80})\{", main)):
    print("  ", m.strip()[:160])
