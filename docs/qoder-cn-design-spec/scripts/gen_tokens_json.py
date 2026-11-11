import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = r"E:\develop-lcb\workspace-tools\ToolCove\qoder-design-spec\tokens"
os.makedirs(OUT, exist_ok=True)

tokens = json.load(open(os.path.join(HERE, "semantic_tokens.json"), encoding="utf-8"))
matrix = json.load(open(os.path.join(HERE, "theme_matrix.json"), encoding="utf-8"))
scales = json.load(open(os.path.join(HERE, "scales.json"), encoding="utf-8"))

THEMES = ["light", "dark", "forest-light", "forest-dark", "bee-light", "bee-dark",
          "mint-light", "mint-dark", "light-parchment", "parchment-dark"]

colors = {}
for t in tokens:
    colors[t["token"]] = {
        "cssVariable": t["var"],
        "light": t.get("light"),
        "dark": t.get("dark"),
        "themeOverrides": t.get("overrides") or {},
        "utilityClasses": t.get("classes", []),
        "cssProperties": t.get("props", []),
    }

ts = scales["theme_scales"]
doc = {
    "$schema": "https://design-tokens.github.io/community-group/format/",
    "meta": {
        "product": "Qoder CN",
        "version": "0.5.7",
        "build": "87859884",
        "extractedFrom": "app.asar / out/renderer/assets/*.css",
        "method": "reverse engineering (compiled Tailwind v4 CSS + hashed CSS variables)",
        "themeCount": len(THEMES),
        "themes": THEMES,
        "note": "CSS 变量名在产物中被哈希；此文件已将哈希变量与语义工具类名交叉还原。",
    },
    "color": colors,
    "themeMatrix": matrix,
    "typography": {
        "fontFamily": {
            "ui": "-apple-system, BlinkMacSystemFont, \"Segoe UI\", sans-serif",
            "inter": "Inter, -apple-system, BlinkMacSystemFont, \"Segoe UI\", sans-serif",
            "brand": "Instrument Sans, -apple-system, BlinkMacSystemFont, \"Segoe UI\", sans-serif",
            "serif": "Crimson Pro",
            "mono": "ui-monospace, SFMono-Regular, SF Mono, Consolas, Liberation Mono, Menlo, monospace",
            "dynamicIsland": "Dynamic Island Inter",
            "fileIcon": "qoder-seti",
        },
        "fontSize": {k: v for k, v in ts.get("text", {}).items() if not k.endswith("--line-height")},
        "lineHeight": {k: v for k, v in ts.get("text", {}).items() if k.endswith("--line-height")},
        "fontWeight": {k.replace("--font-weight-", ""): v for k, v in ts.get("font-weight", {}).items()},
        "tracking": {k.replace("--tracking-", ""): v for k, v in ts.get("tracking", {}).items()},
        "leading": {k.replace("--leading-", ""): v for k, v in ts.get("leading", {}).items()},
        "baseBodyFontSize": "12px",
        "fontSizeModes": {
            "small": {"body": "13px", "code": "12px", "lineHeight": "24px"},
            "medium": {"body": "14px", "code": "13px", "lineHeight": "24px"},
            "large": {"body": "16px", "code": "14px", "lineHeight": "28px"},
        },
        "typesetModes": {
            "default": {"fontSize": "14px", "lineHeight": "24px", "blockGap": "12px", "headingGap": "20px", "codeSize": "13px", "codeLineHeight": "20px", "listIndent": "20px"},
            "chat": {"fontSize": "14px", "lineHeight": "24px", "blockGap": "12px", "headingGap": "24px", "codeSize": "13px", "codeLineHeight": "20px", "listIndent": "20px"},
            "compact": {"fontSize": "13px", "lineHeight": "22px", "blockGap": "8px", "headingGap": "16px", "codeSize": "12px", "codeLineHeight": "20px", "listIndent": "12px"},
            "docs": {"fontSize": "15px", "lineHeight": "26px", "blockGap": "16px", "headingGap": "28px", "codeSize": "13px", "codeLineHeight": "20px", "listIndent": "13px"},
            "reading": {"fontSize": "16px", "lineHeight": "30px", "blockGap": "20px", "headingGap": "32px", "codeSize": "14px", "codeLineHeight": "20px", "listIndent": "14px"},
        },
        "headingScale": {"relativeTo": "base", "h1": "+6px", "h2": "+4px", "h3": "+2px", "h4h6": "base", "weight": 600, "tracking": "0"},
    },
    "spacing": {"base": "4px", "cssVariable": "--spacing: 0.25rem", "scale": [4, 8, 12, 16, 24, 32, 40, 48, 64]},
    "radius": {k.replace("--radius-", ""): v for k, v in ts.get("radius", {}).items()},
    "blur": {k.replace("--blur-", ""): v for k, v in ts.get("blur", {}).items()},
    "motion": {
        "durations": {"instant": "90ms", "fast": "140-160ms", "base": "180-240ms", "slow": "280-420ms", "ambient": "1.05-1.8s", "breath": "2.4-6s", "boot": "2.15s", "themeTransition": "160ms"},
        "easings": {
            "primary": "cubic-bezier(.2,.8,.2,1)",
            "secondary": "cubic-bezier(.16,1,.3,1)",
            "tertiary": "cubic-bezier(.22,1,.36,1)",
            "standard": "cubic-bezier(.4,0,.2,1)",
            "springEmphasis": "cubic-bezier(.34,1.4,.64,1)",
            "linear": "linear",
            "easeInOut": "ease-in-out",
        },
        "springs": [
            {"stiffness": 360, "damping": 24, "mass": 0.45},
            {"stiffness": 420, "damping": 26, "mass": 0.75},
            {"stiffness": 260, "damping": 32, "mass": 0.55},
            {"stiffness": 180, "damping": 28, "mass": 0.5},
            {"stiffness": 170, "damping": 30, "mass": 0.6},
            {"stiffness": 105, "damping": 28, "mass": 0.9},
            {"stiffness": 100, "damping": 10, "mass": 1},
            {"stiffness": 500, "damping": 25, "mass": None},
        ],
        "reducedMotion": "prefers-reduced-motion 覆盖 30 处；data-animation-paused 可运行期暂停；data-visual-effects=off 关闭模糊/渐变/阴影",
        "keyframes": scales.get("keyframes", []),
    },
    "elevation": {
        "surfaces": ["bg-base", "bg-container", "bg-elevated", "bg-layout", "bg-spotlight", "bg-mask"],
        "borderTokenNote": "`border` 存的是 0 0 0 1px rgba 阴影（发丝描边）",
        "shadowCountNonTailwind": 13,
        "zIndex": {"local": "0-3", "float": "10-30", "overlay": "50-100", "drag": "360", "global": "1000-1200", "bootSplash": "2147483647"},
    },
    "stateContracts": {
        "data-theme": 162, "data-state": 56, "data-variant": 45, "data-slot": 22,
        "data-pointer-focus": 22, "data-part-type": 22, "data-layout-region": 16,
        "data-disabled": 14, "data-platform": 14, "data-surface": 13, "data-orientation": 10,
        "data-font-size": 24, "data-ui-scale": 6, "data-animation-paused": 7,
    },
    "accessibility": {
        "contrastFailures": [
            "text-quaternary 在 8/10 主题下 < 4.5:1（2.3-3.1）",
            "warning 作为文字色在浅色主题 1.9:1",
            "mint-light primary 作为文字色 2.8:1",
            "mint-light 主按钮 text-on-primary 2.70:1、light-parchment 3.73:1",
        ],
        "focusRing": "无全局统一；组件级 focus-visible:ring-2 + ring-primary/primary-border，或 outline 1-2px + offset 2px",
        "scrollbar": {"width": "6px", "thumbRadius": "3px", "transition": "background-color .16s"},
        "missing": ["forced-colors", "prefers-contrast"],
    },
}

path = os.path.join(OUT, "design-tokens.json")
with open(path, "w", encoding="utf-8") as fh:
    json.dump(doc, fh, ensure_ascii=False, indent=2)
print("written", path, os.path.getsize(path), "bytes")
