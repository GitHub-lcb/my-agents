import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
tokens = json.load(open(os.path.join(HERE, "semantic_tokens.json"), encoding="utf-8"))
matrix = json.load(open(os.path.join(HERE, "theme_matrix.json"), encoding="utf-8"))
scales = json.load(open(os.path.join(HERE, "scales.json"), encoding="utf-8"))

OUT = os.path.join(HERE, "findings")
os.makedirs(OUT, exist_ok=True)
lines = []


def w(s=""):
    lines.append(s)


# ---------- color token table ----------
w("## 色彩 Token 全表（light / dark 基准值）")
w()
w("| Token | CSS 变量 | Light 基准 | Dark 基准 | 主题覆写 | 语义推断 |")
w("|---|---|---|---|---|---|")
sem = {
    "bg-base": "页面/窗口最底层背景",
    "bg-container": "容器/卡片/面板背景",
    "bg-elevated": "浮起层（弹层/悬浮面板）",
    "bg-layout": "布局底板（窗口壳）",
    "bg-highlight": "高亮反色块（深色文字承载）",
    "bg-mask": "遮罩层",
    "bg-spotlight": "聚光/强调背景",
    "text": "主文本",
    "text-secondary": "次级文本",
    "text-tertiary": "三级文本/说明",
    "text-quaternary": "四级文本/弱提示（占位、元信息）",
    "text-on-primary": "主色上的文字",
    "border": "默认描边（1px 阴影模拟）",
    "border-secondary": "次级描边",
    "border-tertiary": "三级描边",
    "border-quaternary": "最弱描边/分隔",
    "fill": "填充（hover 背景、滑块）",
    "fill-secondary": "次级填充",
    "fill-tertiary": "三级填充",
    "primary": "品牌主色",
    "primary-hover": "主色 hover",
    "primary-active": "主色 active",
    "primary-text": "主色文字（链接/强调）",
    "primary-bg": "主色浅背景",
    "primary-border": "主色描边",
    "link": "链接色",
    "success": "成功",
    "warning": "警告",
    "error": "错误",
    "info": "信息",
    "mint": "辅助色：薄荷",
    "lavender": "辅助色：薰衣草",
    "mauve": "辅助色：藕紫",
    "sage": "辅助色：鼠尾草绿",
    "diff-insert": "Diff 新增",
    "surface-floating": "悬浮表面叠加色",
    "surface-subtle": "微弱表面叠加色",
    "natural-sm": "自然阴影小",
}
for t in tokens:
    name = t["token"]
    if name not in sem:
        continue
    ov = t.get("overrides") or {}
    ovs = ", ".join(sorted(ov.keys()))[:60] if ov else "-"
    w(f"| `{name}` | `{t['var']}` | `{t.get('light') or '-'}` | `{t.get('dark') or '-'}` | {ovs} | {sem[name]} |")
w()

# ---------- theme matrix ----------
themes = ["light", "dark", "forest-light", "forest-dark", "bee-light", "bee-dark",
          "mint-light", "mint-dark", "light-parchment", "parchment-dark"]
show = ["bg-base", "bg-container", "bg-elevated", "text", "text-secondary", "border-secondary",
        "primary", "primary-hover", "primary-text", "text-on-primary"]
w("## 10 套主题关键 Token 矩阵")
w()
w("| Token | " + " | ".join(themes) + " |")
w("|---" * (len(themes) + 1) + "|")
for tok in show:
    row = [f"`{matrix[tok][t]}`" for t in themes]
    w(f"| `{tok}` | " + " | ".join(row) + " |")
w()

# ---------- typography scale ----------
w("## 字号与行高阶梯（@layer theme）")
w()
w("| Token | 字号 | 行高 | 说明 |")
w("|---|---|---|---|")
for k in ["--text-xs", "--text-sm", "--text-base", "--text-lg", "--text-xl", "--text-2xl"]:
    v = scales["theme_scales"]["text"].get(k, "")
    lh = scales["theme_scales"]["text"].get(k + "--line-height", "")
    w(f"| `{k}` | {v} | {lh} | |")
w()

# ---------- radii ----------
w("## 圆角阶梯")
w()
w("| Token | 值 | px |")
w("|---|---|---|")
for k in ["--radius-xs", "--radius-sm", "--radius-md", "--radius-lg", "--radius-xl", "--radius-2xl"]:
    v = scales["theme_scales"]["radius"].get(k, "")
    rem = v.replace("rem", "").strip()
    px = f"{float(rem)*16:.0f}px" if rem else ""
    w(f"| `{k}` | {v} | {px} |")
w()

# ---------- motion ----------
w("## 动效参数")
w()
w("### 缓动曲线使用频次（CSS + JS 合并）")
w()
w("| 曲线 | 用途判定 |")
w("|---|---|")
w("| `cubic-bezier(.2,.8,.2,1)` | **主缓动**（约 111 次），用于入场/展开/hover 过渡 |")
w("| `cubic-bezier(.16,1,.3,1)` | 次缓动（约 28 次），长距离位移/揭示 |")
w("| `cubic-bezier(.22,1,.36,1)` | 第三缓动（约 15 次），面板进出 |")
w("| `linear` / `ease-in-out` | 循环氛围动画（呼吸/旋转/扫光） |")
w("| `cubic-bezier(.34,1.4,.64,1)` / `(.34,1.35,.64,1)` | 弹性强调（开关、贴纸） |")
w()
w("### 时长分布")
w()
w("| 区间 | 时长 | 用途 |")
w("|---|---|---|")
w("| 即时反馈 | 90–160ms | hover、滚动条淡入、主题切换（160ms） |")
w("| 标准过渡 | 180–240ms | 面板/抽屉/菜单进出 |")
w("| 强调过渡 | 280–420ms | 大面板、揭示式动画 |")
w("| 氛围循环 | 1.05–1.8s | AI 思考、aura 光晕、idle 动画 |")
w("| 长时间循环 | 2.4–6s | 呼吸、背景流动 |")
w("| 启动屏 | 2.15s | logo 呼吸 + 扫光 |")
w()
w("### framer-motion 弹簧参数（全部 5 组）")
w()
w("| stiffness | damping | mass | 推断用途 |")
w("|---|---|---|---|")
for s in [("360", "24", ".45"), ("420", "26", ".75"), ("260", "32", ".55"), ("180", "28", ".5"), ("100", "10", "1")]:
    w(f"| {s[0]} | {s[1]} | {s[2]} | - |")
w()

with open(os.path.join(OUT, "lead-tokens-tables.md"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
print("written", os.path.join(OUT, "lead-tokens-tables.md"), len(lines), "lines")
