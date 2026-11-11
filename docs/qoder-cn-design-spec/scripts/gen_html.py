import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = r"E:\develop-lcb\workspace-tools\ToolCove\qoder-design-spec\design-spec.html"

tokens = {t["token"]: t for t in json.load(open(os.path.join(HERE, "semantic_tokens.json"), encoding="utf-8"))}
matrix = json.load(open(os.path.join(HERE, "theme_matrix.json"), encoding="utf-8"))
scales = json.load(open(os.path.join(HERE, "scales.json"), encoding="utf-8"))

THEMES = ["light", "dark", "forest-light", "forest-dark", "bee-light", "bee-dark",
          "mint-light", "mint-dark", "light-parchment", "parchment-dark"]


# ---------- contrast helpers ----------
def hex2rgb(h):
    if not isinstance(h, str) or not h.startswith("#"):
        return None
    h = h[1:]
    if len(h) in (3, 4):
        h = "".join(c * 2 for c in h)
    if len(h) == 8:
        h = h[:6]
    try:
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    except Exception:
        return None


def lum(h):
    rgb = hex2rgb(h)
    if not rgb:
        return None

    def f(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (f(x) for x in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(a, b):
    la, lb = lum(a), lum(b)
    if la is None or lb is None:
        return None
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def badge(r):
    if r is None:
        return ""
    if r >= 7:
        cls, txt = "pass", f"AAA {r:.1f}"
    elif r >= 4.5:
        cls, txt = "pass", f"AA {r:.1f}"
    elif r >= 3:
        cls, txt = "warn", f"AA-L {r:.1f}"
    else:
        cls, txt = "fail", f"FAIL {r:.1f}"
    return f'<span class="badge {cls}">{txt}</span>'


def swatch(name, light, dark, bg_light="#ffffff", bg_dark="#111110"):
    t = tokens.get(name, {})
    lv = t.get("light") or "-"
    dv = t.get("dark") or "-"
    TEXT_TOKENS = {"text", "text-secondary", "text-tertiary", "text-quaternary", "text-on-primary",
                   "primary", "link", "success", "warning", "error", "info"}
    if name == "text-on-primary":
        rl = ratio(lv, matrix["primary"]["light"])
        rd = ratio(dv, matrix["primary"]["dark"])
    elif name in TEXT_TOKENS:
        rl = ratio(lv, bg_light)
        rd = ratio(dv, bg_dark)
    else:
        rl = rd = None
    style_l = f"background:{lv}" if isinstance(lv, str) and lv.startswith("#") else ""
    style_d = f"background:{dv}" if isinstance(dv, str) and dv.startswith("#") else ""
    if not style_l:
        style_l = "background:repeating-linear-gradient(45deg,#eee,#eee 4px,#fff 4px,#fff 8px)"
    if not style_d:
        style_d = "background:repeating-linear-gradient(45deg,#333,#333 4px,#222 4px,#222 8px)"
    ov = t.get("overrides") or {}
    ovtxt = f"{len(ov)} 主题覆写" if ov else "全局一致"
    return f"""
    <div class="swatch">
      <div class="chip light" style="{style_l}" title="{lv}"></div>
      <div class="chip dark" style="{style_d}" title="{dv}"></div>
      <div class="swatch-meta">
        <code>{name}</code>
        <span class="hex">{lv} / {dv}</span>
        <span class="sub">{ovtxt}</span>
        <div class="badges">{badge(rl)}{badge(rd)}</div>
      </div>
    </div>"""


GROUPS = [
    ("背景与表面", ["bg-base", "bg-container", "bg-elevated", "bg-layout", "bg-spotlight", "bg-mask"]),
    ("文本", ["text", "text-secondary", "text-tertiary", "text-quaternary", "text-on-primary"]),
    ("边框与填充", ["border", "border-secondary", "border-tertiary", "border-quaternary",
                "fill", "fill-secondary", "fill-tertiary", "fill-quaternary"]),
    ("主色与链接", ["primary", "primary-hover", "primary-active", "primary-text",
                "primary-bg", "primary-bg-hover", "primary-border", "link"]),
    ("状态色", ["success", "success-bg", "success-border", "warning", "warning-bg", "warning-border",
             "error", "error-bg", "error-border", "info", "info-bg", "info-border"]),
    ("辅助色与特殊", ["mint", "mint-bg", "lavender", "lavender-bg", "mauve", "mauve-bg",
                "sage", "sage-bg", "diff-insert", "surface-floating", "surface-subtle"]),
]

color_sections = ""
for title, names in GROUPS:
    items = "".join(swatch(n, None, None) for n in names if n in tokens)
    color_sections += f'<h3 class="group-title">{title}</h3><div class="swatch-grid">{items}</div>'

# ---------- theme cards ----------
theme_cards = ""
for t in THEMES:
    bg = matrix["bg-base"][t]
    cont = matrix["bg-container"][t]
    elev = matrix["bg-elevated"][t]
    text = matrix["text"][t]
    prim = matrix["primary"][t]
    onp = matrix["text-on-primary"][t]
    name_cn = {"light": "标准浅色", "dark": "标准深色", "forest-light": "森林浅色", "forest-dark": "森林深色",
               "bee-light": "蜂黄浅色", "bee-dark": "蜂黄深色", "mint-light": "薄荷浅色", "mint-dark": "薄荷深色",
               "light-parchment": "羊皮纸浅色", "parchment-dark": "羊皮纸深色"}[t]
    theme_cards += f"""
    <div class="theme-card" data-theme="{t}" style="--tb:{bg};--tc:{cont};--te:{elev};--tt:{text};--tp:{prim};--ton:{onp}">
      <div class="theme-preview" style="background:var(--tb)">
        <div class="tp-panel" style="background:var(--tc);color:var(--tt)">
          <div class="tp-line" style="background:var(--tt);opacity:.9"></div>
          <div class="tp-line short"></div>
          <div class="tp-btn" style="background:var(--tp);color:var(--ton)">Run Agent</div>
        </div>
        <div class="tp-panel elev" style="background:var(--te);color:var(--tt)"><div class="tp-line short"></div></div>
      </div>
      <div class="theme-meta"><b>{name_cn}</b><code>data-theme="{t}"</code><span class="hex">primary {prim}</span></div>
    </div>"""

# ---------- type scale ----------
type_rows = ""
for k, v in [("--text-2xl", "24 / 32"), ("--text-xl", "20 / 28"), ("--text-lg", "18 / 28"),
             ("--text-base", "16 / 24"), ("--text-sm", "14 / 20"), ("--text-xs", "12 / 16")]:
    size = scales["theme_scales"]["text"][k]
    px = float(size.replace("rem", "")) * 16
    type_rows += f"""
    <div class="type-row">
      <div class="type-label"><code>{k.replace('--text-', '')}</code><span class="hex">{px:.0f}px · {v.split(' / ')[1]}px</span></div>
      <div class="type-sample" style="font-size:{px}px;line-height:1.35">The quick brown fox · 让 AI 与工程师并肩工作</div>
    </div>"""

# ---------- radius ----------
radii = [("xs", "2px"), ("sm", "4px"), ("md", "6px"), ("lg", "8px"), ("xl", "12px"), ("2xl", "16px")]
radius_cells = "".join(
    f'<div class="radius-cell"><div class="radius-box" style="border-radius:{px}"></div><code>{n}</code><span class="hex">{px}</span></div>'
    for n, px in radii)

# ---------- spacing ----------
sp_steps = [4, 8, 12, 16, 24, 32, 40, 48, 64]
sp_rows = "".join(
    f'<div class="sp-row"><code>{v}px</code><div class="sp-bar" style="width:{max(v*3, 4)}px"></div></div>' for v in sp_steps)

# ---------- motion ----------
easings = [
    ("主缓动", "cubic-bezier(.2,.8,.2,1)", "111 次使用 · 入场/展开/hover", 0.2, 0.8, 0.2, 1),
    ("次缓动", "cubic-bezier(.16,1,.3,1)", "28 次 · 长距离位移/揭示", 0.16, 1, 0.3, 1),
    ("第三缓动", "cubic-bezier(.22,1,.36,1)", "15 次 · 面板/抽屉", 0.22, 1, 0.36, 1),
    ("标准", "cubic-bezier(.4,0,.2,1)", "Material 标准曲线", 0.4, 0, 0.2, 1),
    ("弹性强调", "cubic-bezier(.34,1.4,.64,1)", "开关/贴纸", 0.34, 1.4, 0.64, 1),
]


def curve_svg(x1, y1, x2, y2):
    # normalize control points into 100x100 box; y inverted
    cy1 = 100 - y1 * 100
    cy2 = 100 - y2 * 100
    return f'<svg viewBox="-10 -10 120 120" class="curve"><path d="M0,100 C{x1*100:.0f},{cy1:.0f} {x2*100:.0f},{cy2:.0f} 100,0" fill="none"/><circle cx="0" cy="100" r="3"/><circle cx="100" cy="0" r="3"/></svg>'


ease_rows = "".join(
    f'<div class="ease-card">{curve_svg(*e[3:])}<div><b>{e[0]}</b><code>{e[1]}</code><span class="sub">{e[2]}</span></div></div>'
    for e in easings)

# ---------- contrast table ----------
contrast_rows = ""
for tok in ["text", "text-secondary", "text-tertiary", "text-quaternary", "primary", "link", "success", "warning", "error", "info"]:
    cells = ""
    for t in THEMES:
        bg = matrix["bg-container"][t]
        c = matrix.get(tok, {}).get(t)
        r = ratio(c, bg) if c else None
        cells += f"<td>{badge(r)}</td>"
    contrast_rows += f"<tr><td><code>{tok}</code></td>{cells}</tr>"

# ---------- token json embed ----------
embedded = {
    "metadata": {"product": "Qoder CN", "version": "0.5.7", "extracted": "2026-11-11", "themes": THEMES},
    "colors": {k: {"light": v.get("light"), "dark": v.get("dark"), "var": v.get("var")} for k, v in tokens.items()},
    "themeMatrix": matrix,
}

CSS = r"""
@font-face{font-family:"Instrument Sans";src:url("./assets/fonts/instrument-sans-400.woff2") format("woff2");font-weight:400;font-display:swap}
@font-face{font-family:"Instrument Sans";src:url("./assets/fonts/instrument-sans-500.woff2") format("woff2");font-weight:500;font-display:swap}
@font-face{font-family:"Inter";src:url("./assets/fonts/inter-400.woff2") format("woff2");font-weight:400;font-display:swap}
@font-face{font-family:"Inter";src:url("./assets/fonts/inter-500.woff2") format("woff2");font-weight:500;font-display:swap}
@font-face{font-family:"Inter";src:url("./assets/fonts/inter-600.woff2") format("woff2");font-weight:600;font-display:swap}

:root{
  --bg:#ffffff; --bg-soft:#f9f9f9; --bg-elev:#f6f6f6;
  --text:#141414; --text-2:#636261; --text-3:#838280;
  --border:#e6e6e6; --border-2:#dddddd;
  --primary:#4b6f5a; --primary-text:#4b6f5a; --primary-bg:#f2f4f2; --on-primary:#fdfdfd;
  --success:#579b6e; --warning:#d99a2b; --error:#d24b46; --info:#3b81e9;
  --mono:ui-monospace,SFMono-Regular,"SF Mono",Consolas,Menlo,monospace;
  --sans:-apple-system,BlinkMacSystemFont,"Segoe UI","Inter",sans-serif;
  --display:"Instrument Sans",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
  --radius:8px;
}
html[data-theme="dark"]{
  --bg:#0e0e0e; --bg-soft:#111110; --bg-elev:#22221f;
  --text:#eeeeeb; --text-2:#b4b4ac; --text-3:#7b7b74;
  --border:#292926; --border-2:#31312d;
  --primary:#5cb870; --primary-text:#8ee5a1; --primary-bg:#14261c; --on-primary:#080807;
  --success:#73cd94; --warning:#faad14; --error:#ff4d4f; --info:#0b83f1;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--text);font-family:var(--sans);font-size:14px;line-height:1.6;-webkit-font-smoothing:antialiased;transition:background .16s ease-out,color .16s ease-out}
code,.mono{font-family:var(--mono);font-size:11.5px}
a{color:var(--primary-text);text-decoration:none}
.wrap{max-width:1180px;margin:0 auto;padding:0 32px}
.topbar{position:sticky;top:0;z-index:50;background:color-mix(in srgb,var(--bg) 88%,transparent);backdrop-filter:blur(12px);border-bottom:1px solid var(--border)}
.topbar .wrap{display:flex;align-items:center;gap:16px;height:56px}
.brand{font-family:var(--display);font-weight:500;letter-spacing:-.01em;font-size:15px}
.brand b{font-weight:500}
.ver{font-family:var(--mono);font-size:11px;color:var(--text-2);border:1px solid var(--border);padding:2px 6px;border-radius:999px}
nav{margin-left:auto;display:flex;gap:18px;font-size:12.5px}
nav a{color:var(--text-2)}
nav a:hover{color:var(--text)}
.toggle{font-family:var(--mono);font-size:11px;border:1px solid var(--border);background:var(--bg-soft);color:var(--text);border-radius:6px;padding:5px 10px;cursor:pointer}
.toggle:hover{border-color:var(--border-2)}

.hero{padding:72px 0 40px;border-bottom:1px solid var(--border)}
.kicker{font-family:var(--mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--text-3)}
h1{font-family:var(--display);font-weight:500;font-size:clamp(34px,5vw,58px);line-height:1.06;letter-spacing:-.02em;margin:14px 0 18px}
h1 em{font-style:normal;color:var(--primary-text)}
.lede{max-width:720px;color:var(--text-2);font-size:16px;line-height:1.7}
.stats{display:flex;flex-wrap:wrap;gap:0;margin-top:36px;border-top:1px solid var(--border)}
.stat{padding:18px 28px 18px 0;margin-right:28px;border-right:1px solid var(--border)}
.stat:last-child{border-right:0}
.stat b{display:block;font-family:var(--display);font-size:26px;font-weight:500;line-height:1.1}
.stat span{font-family:var(--mono);font-size:10.5px;color:var(--text-3);letter-spacing:.04em}

section{padding:56px 0;border-bottom:1px solid var(--border)}
.sec-head{display:flex;align-items:baseline;gap:14px;margin-bottom:8px}
.sec-no{font-family:var(--mono);font-size:11px;color:var(--text-3);letter-spacing:.1em}
h2{font-family:var(--display);font-weight:500;font-size:26px;letter-spacing:-.015em;margin:0}
.sec-desc{color:var(--text-2);max-width:760px;margin:0 0 30px}
h3.group-title{font-size:12px;font-family:var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--text-3);font-weight:400;margin:34px 0 12px}

.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(252px,1fr));gap:12px;border:0;border-radius:0;overflow:visible;background:none}
.card{background:var(--bg);padding:20px;border:1px solid var(--border);border-radius:10px}
.card:hover{border-color:var(--border-2)}
.card .idx{font-family:var(--mono);font-size:10px;color:var(--text-3)}
.card h4{margin:8px 0 6px;font-size:14.5px;font-weight:600;letter-spacing:-.01em}
.card p{margin:0;color:var(--text-2);font-size:12.5px;line-height:1.65}

.surface-demo{padding:26px;border-radius:12px;background:var(--bg-soft);border:1px solid var(--border);margin-bottom:8px}
.surf{display:flex;justify-content:space-between;align-items:center;padding:14px 16px;border-radius:8px;margin-top:8px;font-family:var(--mono);font-size:11px;color:var(--text-2);border:1px solid var(--border)}
.surf b{color:var(--text);font-weight:500;font-family:var(--sans);font-size:12.5px}

.swatch-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(268px,1fr));gap:10px}
.swatch{display:flex;gap:12px;align-items:flex-start;padding:10px;border:1px solid var(--border);border-radius:8px}
.swatch:hover{border-color:var(--border-2)}
.chip{width:46px;height:46px;border-radius:6px;border:1px solid var(--border);flex:none}
.chip.light{display:none}
html[data-theme="dark"] .chip.light{display:none}
html[data-theme="dark"] .chip.dark{display:block}
.chip.dark{display:none}
html[data-theme="light"] .chip.light{display:block}
html[data-theme="light"] .chip.dark{display:none}
.swatch-meta{display:flex;flex-direction:column;gap:2px;min-width:0}
.swatch-meta code{font-size:11.5px;color:var(--text)}
.hex{font-family:var(--mono);font-size:10.5px;color:var(--text-2)}
.sub{font-size:10.5px;color:var(--text-3)}
.badges{display:flex;gap:4px;margin-top:4px;flex-wrap:wrap}
.badge{font-family:var(--mono);font-size:9.5px;padding:1px 5px;border-radius:4px;border:1px solid}
.badge.pass{color:var(--success);border-color:color-mix(in srgb,var(--success) 40%,transparent);background:color-mix(in srgb,var(--success) 8%,transparent)}
.badge.warn{color:var(--warning);border-color:color-mix(in srgb,var(--warning) 40%,transparent);background:color-mix(in srgb,var(--warning) 8%,transparent)}
.badge.fail{color:var(--error);border-color:color-mix(in srgb,var(--error) 40%,transparent);background:color-mix(in srgb,var(--error) 8%,transparent)}

.theme-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:14px}
.theme-card{border:1px solid var(--border);border-radius:10px;overflow:hidden}
.theme-preview{height:118px;padding:12px;display:flex;gap:8px;align-items:flex-start}
.tp-panel{flex:1;border-radius:7px;padding:9px;border:1px solid rgba(128,128,128,.16);display:flex;flex-direction:column;gap:5px}
.tp-panel.elev{flex:0 0 42%}
.tp-line{height:5px;border-radius:2px;background:currentColor;opacity:.5}
.tp-line.short{width:62%}
.tp-btn{margin-top:auto;font-size:9px;padding:4px 6px;border-radius:5px;text-align:center;font-weight:500}
.theme-meta{padding:10px 12px;display:flex;flex-direction:column;gap:2px;border-top:1px solid var(--border)}
.theme-meta b{font-size:12.5px;font-weight:600}
.theme-meta code{font-size:10px;color:var(--text-2)}

.type-row{display:grid;grid-template-columns:150px 1fr;gap:20px;align-items:baseline;padding:14px 0;border-bottom:1px solid var(--border)}
.type-label{display:flex;flex-direction:column;gap:2px}
.type-label code{font-size:11.5px}
.type-sample{letter-spacing:-.015em}

.tset{border:1px solid var(--border);border-radius:10px;overflow:hidden;margin-top:8px}
.tset-row{display:grid;grid-template-columns:120px 1fr;gap:18px;padding:16px;border-bottom:1px solid var(--border)}
.tset-row:last-child{border-bottom:0}
.tset-name{font-family:var(--mono);font-size:11px;color:var(--text-2)}
.tset h5{margin:0 0 4px;font-size:14px;font-weight:600}
.tset p{margin:0 0 6px;color:var(--text-2)}
.tset code{background:var(--bg-elev);padding:1px 4px;border-radius:4px}
.tset .code-block{background:var(--bg-soft);border:1px solid var(--border);border-radius:6px;padding:8px 10px;font-family:var(--mono);font-size:11px;color:var(--text-2);margin-top:6px}

.radius-row{display:flex;gap:26px;flex-wrap:wrap;margin-top:8px}
.radius-cell{display:flex;flex-direction:column;align-items:center;gap:5px}
.radius-box{width:76px;height:76px;background:var(--primary-bg);border:1px solid color-mix(in srgb,var(--primary) 40%,transparent)}
.radius-cell code{font-size:11px}

.sp-row{display:flex;align-items:center;gap:14px;padding:5px 0}
.sp-row code{width:42px;color:var(--text-2);font-size:11px}
.sp-bar{height:12px;background:color-mix(in srgb,var(--primary) 25%,transparent);border-radius:2px}

.ease-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:12px}
.ease-card{border:1px solid var(--border);border-radius:10px;padding:14px;display:flex;gap:14px}
.ease-card svg.curve{width:56px;height:56px;flex:none}
.ease-card svg.curve path{stroke:var(--primary);stroke-width:2.5}
.ease-card svg.curve circle{fill:var(--text-3)}
.ease-card div{display:flex;flex-direction:column;gap:1px;min-width:0}
.ease-card b{font-size:12px;font-weight:600}
.ease-card code{font-size:9.5px;color:var(--text-2);word-break:break-all}

.demo-row{display:flex;gap:12px;flex-wrap:wrap;margin-top:18px}
.demo{border:1px solid var(--border);border-radius:10px;padding:16px;flex:1 1 240px;background:var(--bg-soft)}
.demo h6{margin:0 0 4px;font-size:12.5px;font-weight:600;font-family:var(--mono);letter-spacing:.02em}
.demo p{margin:0 0 12px;font-size:11.5px;color:var(--text-2)}
.demo-stage{height:56px;display:flex;align-items:center;position:relative;overflow:hidden}
.demo-box{width:36px;height:36px;border-radius:8px;background:var(--primary);transition:transform .22s cubic-bezier(.2,.8,.2,1)}
.demo:hover .demo-box{transform:translateX(180px)}
.demo-box.s2{transition:transform .35s cubic-bezier(.16,1,.3,1)}
.demo:hover .demo-box.s2{transform:translateX(180px) scale(1.06)}
.demo-panel{border:1px solid var(--border);border-radius:8px;background:var(--bg);padding:8px 10px;font-size:11.5px;color:var(--text-2);transform:translateY(0);opacity:1;transition:transform .24s cubic-bezier(.22,1,.36,1),opacity .24s cubic-bezier(.22,1,.36,1)}
.demo:hover .demo-panel{transform:translateY(8px);opacity:.35}

table.contrast{border-collapse:collapse;width:100%;font-size:11px}
table.contrast th,table.contrast td{padding:7px 8px;border-bottom:1px solid var(--border);text-align:left;white-space:nowrap}
table.contrast th{font-family:var(--mono);font-size:10px;color:var(--text-3);font-weight:400;letter-spacing:.06em}
table.contrast td code{font-size:10.5px}
.scroll-x{overflow-x:auto}

table.matrix{border-collapse:collapse;width:100%;font-size:11.5px}
table.matrix th,table.matrix td{padding:8px 10px;border-bottom:1px solid var(--border);text-align:left}
table.matrix th{font-family:var(--mono);font-size:10px;color:var(--text-3);font-weight:400}

.note{border-left:2px solid var(--primary);padding:10px 14px;background:var(--primary-bg);border-radius:0 8px 8px 0;color:var(--text-2);font-size:12.5px;margin:16px 0}
footer{padding:44px 0 64px;color:var(--text-3);font-size:12px}
footer code{color:var(--text-2)}
.asset-row{display:flex;gap:18px;flex-wrap:wrap;align-items:center;margin-top:14px}
.asset{border:1px solid var(--border);border-radius:10px;padding:12px;background:var(--bg-soft);display:flex;flex-direction:column;align-items:center;gap:8px;width:120px}
.asset img{width:64px;height:64px;object-fit:contain}
.asset span{font-family:var(--mono);font-size:9.5px;color:var(--text-3);text-align:center}
.surface-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:10px;margin-top:12px}
.surface-card{border:1px solid var(--border);border-radius:9px;padding:12px;background:var(--bg)}
.surface-card b{font-size:12.5px}
.surface-card .sub{font-size:10.5px;display:block;margin-top:2px}
.surface-card code{font-size:10px;color:var(--text-2)}
.size-ladder{display:flex;gap:26px;align-items:flex-end;margin-top:6px}
.size-item{display:flex;flex-direction:column;align-items:center;gap:7px}
.size-box{display:inline-flex;align-items:center;padding:0 14px;border:1px solid var(--border-2);background:var(--bg);font-size:12px;color:var(--text-2);corner-shape:squircle}
.size-item code{font-size:10.5px;color:var(--text-2)}
.btn-demo-row{display:flex;gap:10px;flex-wrap:wrap;margin-top:6px}
.btn-demo{display:inline-flex;align-items:center;height:28px;padding:0 12px;border-radius:16px;corner-shape:squircle;font-size:13px;font-weight:500;border:1px solid transparent;line-height:1}
.squircle-pair{display:flex;gap:28px;margin-top:8px}
.sq{width:88px;height:88px;background:var(--primary-bg);border:1px solid color-mix(in srgb,var(--primary) 30%,transparent);display:flex;align-items:flex-end;justify-content:center;padding-bottom:7px;font-family:var(--mono);font-size:10px;color:var(--text-2)}
.chips{display:flex;flex-wrap:wrap;gap:6px;margin-top:10px}
.chip-tag{font-family:var(--mono);font-size:10.5px;border:1px solid var(--border);border-radius:6px;padding:3px 7px;color:var(--text-2);background:var(--bg-soft)}
.layout-diagram{border:1px solid var(--border);border-radius:12px;overflow:hidden;margin-top:12px}
.ld-title{height:40px;background:var(--bg-soft);border-bottom:1px solid var(--border);display:flex;align-items:center;gap:10px;padding:0 14px;font-family:var(--mono);font-size:10.5px;color:var(--text-2)}
.ld-dot{width:7px;height:7px;border-radius:50%;background:var(--border-2)}
.ld-body{display:flex;height:196px}
.ld-a{width:19%;min-width:118px;border-right:1px solid var(--border);padding:12px;font-family:var(--mono);font-size:10px;color:var(--text-2);background:var(--bg-soft);display:flex;flex-direction:column;gap:8px}
.ld-b{flex:1;padding:12px;display:flex;flex-direction:column;gap:8px;background:var(--bg)}
.ld-b2{width:22%;min-width:128px;border-left:1px solid var(--border);padding:12px;font-family:var(--mono);font-size:10px;color:var(--text-2);background:var(--bg-soft);display:flex;flex-direction:column;gap:8px}
.ld-line{height:7px;border-radius:3px;background:var(--border)}
.ld-line.w70{width:70%}.ld-line.w40{width:40%}
.ld-region{font-family:var(--mono);font-size:9.5px;letter-spacing:.06em;color:var(--text-3);text-transform:uppercase}
.note b{color:var(--text)}
@media(max-width:760px){nav{display:none}.type-row{grid-template-columns:1fr}.tset-row{grid-template-columns:1fr}}
"""

JS = r"""
const root=document.documentElement;
const btn=document.getElementById('themeToggle');
function setTheme(t){root.dataset.theme=t;btn.textContent=t==='dark'?'☾ Dark':'☀ Light';try{localStorage.setItem('qspec-theme',t)}catch(e){}}
btn.addEventListener('click',()=>setTheme(root.dataset.theme==='dark'?'light':'dark'));
(function(){let t='light';try{t=localStorage.getItem('qspec-theme')||'light'}catch(e){}const q=new URLSearchParams(location.search).get('theme');if(q==='dark'||q==='light')t=q;setTheme(t)})();
document.querySelectorAll('a[href^="#"]').forEach(a=>a.addEventListener('click',e=>{const el=document.querySelector(a.getAttribute('href'));if(el){e.preventDefault();el.scrollIntoView({behavior:'smooth',block:'start'})}}));
"""

HTML = f"""<!doctype html>
<html lang="zh-CN" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Qoder CN · 设计规范逆向还原 v0.5.7</title>
<style>{CSS}</style>
</head>
<body>
<header class="topbar"><div class="wrap">
  <div class="brand">Qoder <b>CN</b> · Design Spec</div>
  <span class="ver">v0.5.7 · 逆向还原</span>
  <nav>
    <a href="#principles">原则</a><a href="#color">色彩</a><a href="#theme">主题</a>
    <a href="#type">排版</a><a href="#space">间距</a><a href="#motion">动效</a>
    <a href="#components">组件</a><a href="#layout">界面</a>
    <a href="#platform">适配</a><a href="#a11y">对比度</a>
  </nav>
  <button class="toggle" id="themeToggle">☀ Light</button>
</div></header>

<div class="wrap">
  <div class="hero">
    <div class="kicker">Design System Reverse Engineering</div>
    <h1>Qoder CN 设计规范<br><em>从 app.asar 里还原出来的体系</em></h1>
    <p class="lede">解包 Electron 应用的 6,448 个文件，从 Tailwind v4 产物、哈希化 CSS 变量与 React bundle 中，还原出 68 个语义色彩 token、10 套主题、4 种内容排版模式与一套统一的动效语言。以下展示的每个数值都来自产物本身，并标注了证据等级。</p>
    <div class="stats">
      <div class="stat"><b>68</b><span>语义色彩 TOKEN</span></div>
      <div class="stat"><b>10</b><span>主题（5 家族 × 明暗）</span></div>
      <div class="stat"><b>60</b><span>KEYFRAMES</span></div>
      <div class="stat"><b>4</b><span>TYPESET 排版模式</span></div>
      <div class="stat"><b>6</b><span>字体家族</span></div>
      <div class="stat"><b>111</b><span>主缓动使用次数</span></div>
    </div>
  </div>

  <section id="principles">
    <div class="sec-head"><span class="sec-no">01</span><h2>设计原则</h2></div>
    <p class="sec-desc">从 token 结构、组件写法与动效参数中归纳出的七条稳定模式。</p>
    <div class="cards">
      <div class="card"><div class="idx">01</div><h4>系统字体 + 致密基准</h4><p>UI 默认使用系统字体栈，body 基准 12px。牺牲一点"设计感"，换取工具类产品的信息密度与原生感。</p></div>
      <div class="card"><div class="idx">02</div><h4>语义 Token 三层架构</h4><p>原始值 → 语义 token → 工具类。哈希变量名（--q71fecd）与语义类名（.bg-bg-container）并存。</p></div>
      <div class="card"><div class="idx">03</div><h4>表面分层而非阴影堆叠</h4><p>base / container / elevated / layout 四级表面 + 用 box-shadow 模拟的 1px 发丝描边，全站仅 13 条自定义阴影。</p></div>
      <div class="card"><div class="idx">04</div><h4>内容即界面</h4><p>AI 回答、文档、长文统一走 .typeset，按 chat / compact / docs / reading 四种密度切换，标题字号随基准相对计算。</p></div>
      <div class="card"><div class="idx">05</div><h4>一条主缓动统治动效</h4><p>cubic-bezier(.2,.8,.2,1) 使用 111 次，标准过渡 140–240ms，氛围动画 1.05–1.8s，弹簧参数收敛到 8 组。</p></div>
      <div class="card"><div class="idx">06</div><h4>AI 人格化视觉</h4><p>aura 光晕、语音 orb（breathing/capsule/classic 三种）、Qoduck 鸭子、Dynamic Island 胶囊，把"思考/在听/完成"做成有生命感的状态。</p></div>
      <div class="card"><div class="idx">07</div><h4>可降级的设计系统</h4><p>data-theme / data-font-size / data-ui-scale / data-visual-effects / data-platform 五个开关，让规范能适配环境与性能。</p></div>
    </div>
  </section>

  <section id="color">
    <div class="sec-head"><span class="sec-no">02</span><h2>色彩系统</h2></div>
    <p class="sec-desc">68 个语义 token，覆盖表面、文本、边框填充、主色、状态色与辅助色。切换右上角主题查看 light / dark 两套基准值；徽章为相对 bg-container 的 WCAG 对比度。</p>
    <h3 class="group-title">表面层级演示</h3>
    <div class="surface-demo">
      <div class="surf"><b>bg-layout</b><span>窗口壳底板</span></div>
      <div class="surf" style="background:var(--bg-soft)"><b>bg-base</b><span>页面最底层</span></div>
      <div class="surf" style="background:var(--bg)"><b>bg-container</b><span>卡片 / 面板 / 容器</span></div>
      <div class="surf" style="background:var(--bg-elev)"><b>bg-elevated</b><span>浮层 / 弹窗 / 悬浮面板</span></div>
    </div>
    {color_sections}
    <div class="note"><b>边框的特殊约定</b>：<code>border</code> token 存的不是颜色，而是 <code>0 0 0 1px rgba(...)</code> 的 box-shadow —— 全站发丝描边用阴影实现，避免 1px 边框在缩放下的模糊与占位差异。</div>
  </section>

  <section id="theme">
    <div class="sec-head"><span class="sec-no">03</span><h2>主题体系</h2></div>
    <p class="sec-desc">5 个色系家族 × 明暗 = 10 套主题。切换主题时背景、文本、边框、填充、主色整套重算，而非只换主色。主题切换动画走 View Transitions，160ms 淡入淡出。</p>
    <div class="theme-grid">{theme_cards}</div>
    <div class="note"><b>命名瑕疵</b>：羊皮纸家族浅色叫 <code>light-parchment</code>、深色叫 <code>parchment-dark</code>，与其他家族的 <code>xxx-light / xxx-dark</code> 不对称——复刻时建议先统一命名。</div>
  </section>

  <section id="type">
    <div class="sec-head"><span class="sec-no">04</span><h2>字体与排版</h2></div>
    <p class="sec-desc">主 UI 用系统字体栈（-apple-system / Segoe UI），Inter 用于需要跨平台一致的局部，品牌场合切 Instrument Sans；Crimson Pro 为长文衬线，KaTeX 负责公式，qoder-seti 是文件图标字体。</p>
    <h3 class="group-title">字号阶梯</h3>
    {type_rows}
    <h3 class="group-title">typeset 内容排版模式</h3>
    <p class="sec-desc" style="margin-bottom:12px">同一段内容在四种模式下的密度差异。标题不做固定字号，而是 <code>base + 6 / +4 / +2 / +0</code> 相对计算。</p>
    <div class="tset">
      <div class="tset-row"><div class="tset-name">.typeset-chat<br><span class="hex">14 / 24</span></div><div class="tset" style="border:0"><h5 style="font-size:20px">Agent 已完成 3 个任务</h5><p style="font-size:14px;line-height:24px">我检查了工作区的变更，修复了 <code>auth.ts</code> 中的类型错误，并补充了 2 个测试用例。以下是关键改动摘要。</p><div class="code-block">$ pnpm test --filter auth<br>✓ 12 passed</div></div></div>
      <div class="tset-row"><div class="tset-name">.typeset-compact<br><span class="hex">13 / 22</span></div><div class="tset" style="border:0"><h5 style="font-size:15px">Agent 已完成 3 个任务</h5><p style="font-size:13px;line-height:22px">我检查了工作区的变更，修复了 <code>auth.ts</code> 中的类型错误，并补充了 2 个测试用例。以下是关键改动摘要。</p><div class="code-block" style="font-size:12px">$ pnpm test --filter auth<br>✓ 12 passed</div></div></div>
      <div class="tset-row"><div class="tset-name">.typeset-docs<br><span class="hex">15 / 26</span></div><div class="tset" style="border:0"><h5 style="font-size:21px">Agent 已完成 3 个任务</h5><p style="font-size:15px;line-height:26px">我检查了工作区的变更，修复了 <code>auth.ts</code> 中的类型错误，并补充了 2 个测试用例。以下是关键改动摘要。</p><div class="code-block" style="font-size:13px">$ pnpm test --filter auth<br>✓ 12 passed</div></div></div>
      <div class="tset-row"><div class="tset-name">.typeset-reading<br><span class="hex">16 / 30</span></div><div class="tset" style="border:0"><h5 style="font-size:22px">Agent 已完成 3 个任务</h5><p style="font-size:16px;line-height:30px">我检查了工作区的变更，修复了 <code>auth.ts</code> 中的类型错误，并补充了 2 个测试用例。以下是关键改动摘要。</p><div class="code-block" style="font-size:14px">$ pnpm test --filter auth<br>✓ 12 passed</div></div></div>
    </div>
  </section>

  <section id="space">
    <div class="sec-head"><span class="sec-no">05</span><h2>间距与圆角</h2></div>
    <p class="sec-desc">严格 4px 网格（--spacing: 0.25rem）。圆角 6 档，实际使用还包含 3/5/10/20/24px 与胶囊；另有 30 处 <code>corner-shape: squircle</code> 超椭圆圆角，用于引导卡片等品牌化场景。</p>
    <h3 class="group-title">间距阶梯</h3>
    {sp_rows}
    <h3 class="group-title">圆角阶梯</h3>
    <div class="radius-row">{radius_cells}</div>
  </section>

  <section id="motion">
    <div class="sec-head"><span class="sec-no">06</span><h2>动效语言</h2></div>
    <p class="sec-desc">一条主缓动 + 少量时长档 + 8 组弹簧参数。UI 过渡集中在 140–240ms；氛围动画 1.05–1.8s；启动屏 2.15s。悬停下面卡片可以看到对应缓动的实际效果。</p>
    <h3 class="group-title">缓动曲线</h3>
    <div class="ease-grid">{ease_rows}</div>
    <h3 class="group-title">实测过渡</h3>
    <div class="demo-row">
      <div class="demo"><h6>.22s primary</h6><p>cubic-bezier(.2,.8,.2,1)</p><div class="demo-stage"><div class="demo-box"></div></div></div>
      <div class="demo"><h6>.35s reveal</h6><p>cubic-bezier(.16,1,.3,1)</p><div class="demo-stage"><div class="demo-box s2"></div></div></div>
      <div class="demo"><h6>.24s panel</h6><p>cubic-bezier(.22,1,.36,1)</p><div class="demo-stage"><div class="demo-panel">Panel content</div></div></div>
    </div>
    <div class="note"><b>降级策略</b>：<code>prefers-reduced-motion</code> 在产物中出现 30 次；<code>data-visual-effects=off</code> 可一键关闭模糊/渐变/阴影；<code>data-animation-paused</code> 支持运行期暂停。</div>
  </section>

  <section id="components">
    <div class="sec-head"><span class="sec-no">07</span><h2>组件规范</h2></div>
    <p class="sec-desc">设计系统有 153 个组件，其 bundle（S__Wc8-4.js）未深度混淆，<code>cva()</code> 变体表可直接读出。最强的一致性约束是尺寸阶梯与 squircle 圆角体系。</p>
    <h3 class="group-title">尺寸阶梯：20 / 28 / 36px（sm / md / lg + custom 逃生口）</h3>
    <div class="size-ladder">
      <div class="size-item"><div class="size-box" style="height:20px;border-radius:16px">sm</div><code>h-5 · 20px</code></div>
      <div class="size-item"><div class="size-box" style="height:28px;border-radius:16px">md（默认）</div><code>h-7 · 28px</code></div>
      <div class="size-item"><div class="size-box" style="height:36px;border-radius:16px">lg</div><code>h-9 · 36px</code></div>
    </div>
    <h3 class="group-title">Button 变体（12 种中节选 6 种）</h3>
    <div class="btn-demo-row">
      <button class="btn-demo" style="background:var(--primary);color:var(--on-primary)">primary</button>
      <button class="btn-demo" style="background:#080807;color:#fdfdfd">secondary</button>
      <button class="btn-demo" style="background:var(--bg-elev);color:var(--text)">tertiary</button>
      <button class="btn-demo" style="background:transparent;color:var(--text-2)">ghost（默认）</button>
      <button class="btn-demo" style="background:transparent;border-color:var(--border-2);color:var(--text)">outline</button>
      <button class="btn-demo" style="background:var(--error);color:#fff">destructive</button>
    </div>
    <h3 class="group-title">圆角：普通 16px vs squircle 16px（超椭圆）</h3>
    <div class="squircle-pair">
      <div class="sq" style="border-radius:16px">rounded 16px</div>
      <div class="sq" style="border-radius:16px;corner-shape:squircle">squircle 16px</div>
    </div>
    <p class="sec-desc" style="margin-top:10px">控件主圆角为 <code>squircle-2xl</code>(16px)、浮层 <code>squircle-xl</code>(12px)、标签 4px、胶囊 <code>squircle-full</code>。全站共 30 处 <code>corner-shape: squircle</code>，并用 <code>@supports</code> 提供普通圆角兜底。</p>
    <h3 class="group-title">27 个组件族</h3>
    <div class="chips">
      <span class="chip-tag">Button</span><span class="chip-tag">IconButton</span><span class="chip-tag">Input</span><span class="chip-tag">Textarea</span><span class="chip-tag">Field/Label</span><span class="chip-tag">Chat Composer</span><span class="chip-tag">Select</span><span class="chip-tag">DropdownMenu</span><span class="chip-tag">Dialog</span><span class="chip-tag">Drawer</span><span class="chip-tag">Tooltip/HoverCard/Popover</span><span class="chip-tag">Tabs</span><span class="chip-tag">Table</span><span class="chip-tag">Tag</span><span class="chip-tag">Avatar</span><span class="chip-tag">Toast</span><span class="chip-tag">Switch</span><span class="chip-tag">Checkbox/Radio</span><span class="chip-tag">Progress/Skeleton</span><span class="chip-tag">EmptyState</span><span class="chip-tag">Card</span><span class="chip-tag">Scrollbar</span><span class="chip-tag">Slider</span><span class="chip-tag">Kbd</span><span class="chip-tag">Segmented</span><span class="chip-tag">Breadcrumb</span><span class="chip-tag">SplitButton</span>
    </div>
    <div class="note"><b>状态规范</b>：hover 用 fill 系；focus <b>改边框/底色、不画 ring</b>；disabled 统一 <code>opacity-50 cursor-not-allowed</code>；状态型组件统一用 <code>data-state</code> 驱动；全库 <code>motion-reduce:</code> 兜底。<br><b>已知例外</b>：Toast 用 sonner 自有调色板不接 token、组件层直接写 <code>var(--qXXXXXX)</code>、Button 无 loading 态、无统一 Card 抽象、Notification 三套实现并存。</div>
  </section>

  <section id="layout">
    <div class="sec-head"><span class="sec-no">08</span><h2>界面架构</h2></div>
    <p class="sec-desc">全应用只有 3 个 HTML 入口，其余界面由 <code>index.html?surface=&lt;id&gt;</code> 路由 + 动态 import 装配。主窗为 frameless + 40px 自绘标题栏，Windows 用 <code>titleBarOverlay.height=40</code> 与系统按钮对齐。</p>
    <div class="layout-diagram">
      <div class="ld-title"><span class="ld-dot"></span><span class="ld-dot"></span><span class="ld-dot"></span>&nbsp; 自绘标题栏 40px · ← → · 侧栏开关 · 拖拽区 · 窗口控制 / 账户</div>
      <div class="ld-body">
        <div class="ld-a"><span class="ld-region">A · 左侧栏</span><div class="ld-line w70"></div><div class="ld-line"></div><div class="ld-line"></div><div class="ld-line w40"></div><span style="margin-top:auto">248 / min 208px</span></div>
        <div class="ld-b">
          <span class="ld-region">B-HEADER · 40px（工作区 Tab / 地址栏）</span>
          <div class="ld-line w70"></div><div class="ld-line"></div><div class="ld-line w40"></div>
          <div style="margin-top:auto;border:1px dashed var(--border-2);border-radius:8px;padding:8px;font-family:var(--mono);font-size:10px;color:var(--text-3)">Composer（底部固定）</div>
        </div>
        <div class="ld-b2"><span class="ld-region">B2 · 右栏</span><div class="ld-line"></div><div class="ld-line w70"></div><div class="ld-line w40"></div><span style="margin-top:auto">280px · 抽屉 620px</span></div>
      </div>
    </div>
    <div class="scroll-x" style="margin-top:16px"><table class="matrix">
      <tr><th>窗口 / 区域</th><th>尺寸</th><th>说明</th></tr>
      <tr><td>Workbench 主窗口</td><td><code>1320×800</code></td><td>min 720×540，可缩放</td></tr>
      <tr><td>登录窗口</td><td><code>690×446</code></td><td>min = max，固定不可缩放</td></tr>
      <tr><td>Quick Note</td><td><code>400×720</code></td><td>min 320×600 / max 480×800，贴光标 32px</td></tr>
      <tr><td>Desktop Pet</td><td><code>128×176</code></td><td>128px 精灵 + 48px 工具栏，可调尺寸百分比</td></tr>
      <tr><td>会话内容限宽</td><td><code>768 / 820 / 924</code></td><td>新任务 / page / 非空会话</td></tr>
      <tr><td>左侧栏</td><td><code>248 / 208</code></td><td>default / min，可折叠</td></tr>
      <tr><td>右栏 / Issue 抽屉</td><td><code>280 / 620</code></td><td>可折叠 / 覆盖式抽屉</td></tr>
    </table></div>
    <h3 class="group-title">12 个独立 Surface</h3>
    <div class="surface-grid">
      <div class="surface-card"><b>Dynamic Island</b><span class="sub">OS 级置顶悬浮条</span><code>island / notch 两模式</code></div>
      <div class="surface-card"><b>Desktop Pet</b><span class="sub">透明桌面精灵窗</span><code>128px sprite + 48px 工具栏</code></div>
      <div class="surface-card"><b>Live Voice Overlay</b><span class="sub">全屏透明浮层</span><code>aura orb 三套视觉</code></div>
      <div class="surface-card"><b>Quick Note</b><span class="sub">竖版便签窗</span><code>400×720 · 置顶</code></div>
      <div class="surface-card"><b>Companion Activity</b><span class="sub">底部气泡栈</span><code>折叠 68 / 展开 188px</code></div>
      <div class="surface-card"><b>Onboarding</b><span class="sub">首启引导浮层</span><code>信封 + 身份卡 240×280</code></div>
      <div class="surface-card"><b>Role Reveal Demo</b><span class="sub">角色动效演示</span><code>独立 chunk</code></div>
      <div class="surface-card"><b>Hosted Presentation Menu</b><span class="sub">透明菜单锚点</span><code>2×2px 锚点定位</code></div>
      <div class="surface-card"><b>Data Directory Progress</b><span class="sub">独立迁移进度窗</span><code>独立 CSP · 禁网</code></div>
      <div class="surface-card"><b>Artifact Preview</b><span class="sub">产物独立预览窗</span><code>头部 40px · 尺寸未确认</code></div>
      <div class="surface-card"><b>登录</b><span class="sub">独立窗口</span><code>690×446 固定</code></div>
      <div class="surface-card"><b>Workbench</b><span class="sub">主窗口</span><code>1320×800</code></div>
    </div>
    <div class="note"><b>设计意图</b>：左侧栏没有文件树——第一层是任务/项目/讨论（人的工作对象），文件树被降级为"任务内的工作目录 + 右栏 Tab"。Dynamic Island / Desktop Pet / Companion Activity 共用同一只鸭子人格，把 Agent 状态提升到 OS 层：人在别处也能批准权限、回答问题。</div>
  </section>

  <section id="platform">
    <div class="sec-head"><span class="sec-no">09</span><h2>主题与平台适配</h2></div>
    <p class="sec-desc">同一套 UI 通过 CSS 变量开关适配不同平台、密度与性能档位。</p>
    <div class="scroll-x"><table class="matrix">
      <tr><th>机制</th><th>开关</th><th>规范值</th><th>设计含义</th></tr>
      <tr><td>主题</td><td><code>data-theme</code></td><td>10 套</td><td>整套色彩重算，非只换主色</td></tr>
      <tr><td>主题切换</td><td><code>data-qoder-theme-transition</code></td><td>160ms fade（View Transitions）</td><td>减少切换时的视觉跳变</td></tr>
      <tr><td>平台</td><td><code>data-platform</code></td><td>win32 关闭渐变/毛玻璃改实色</td><td>换取 Windows 渲染正确性与性能</td></tr>
      <tr><td>视觉效果</td><td><code>data-visual-effects</code></td><td>off 时 blur/gradient/shadow 归零</td><td>低配机 / 远程桌面兜底</td></tr>
      <tr><td>字号</td><td><code>data-font-size</code></td><td>small 13 / medium 14 / large 16</td><td>仅聊天正文与 markdown</td></tr>
      <tr><td>界面缩放</td><td><code>data-ui-scale</code></td><td>large = zoom 1.1</td><td>只作用于侧栏/内容区，避免整窗模糊</td></tr>
      <tr><td>终端主题</td><td><code>data-terminal-theme</code></td><td>独立 light/dark</td><td>终端可独立于应用主题</td></tr>
    </table></div>
  </section>

  <section id="a11y">
    <div class="sec-head"><span class="sec-no">10</span><h2>对比度合规</h2></div>
    <p class="sec-desc">对 10 套主题逐个计算 WCAG 2.1 对比度（相对 bg-container）。主文本与次级文本表现优秀，但四级文本、浅色 warning 与部分主题的主色按钮存在硬伤。</p>
    <div class="scroll-x"><table class="contrast">
      <tr><th>Token</th>{''.join(f'<th>{t}</th>' for t in THEMES)}</tr>
      {contrast_rows}
    </table></div>
    <div class="note"><b>需要修正的 4 处</b>：① <code>text-quaternary</code> 在 8/10 主题下低于 4.5:1，应限定为非关键信息；② <code>warning</code> 作文字色在浅色主题仅 1.9:1，只应用于图标/背景；③ <code>mint-light</code> 的 <code>primary</code> 文字 2.8:1；④ <code>mint-light</code> 主按钮文字 2.7:1、<code>light-parchment</code> 3.7:1，不达 AA。</div>
  </section>

  <section id="brand">
    <div class="sec-head"><span class="sec-no">11</span><h2>品牌视觉</h2></div>
    <p class="sec-desc">启动屏 logo 是「mask + 三层叠加 + 两条 2.15s 同步动画」的合成件，而且刻意用中性灰阶（text-quaternary 72% × opacity 0.6）而非品牌绿——低存在感启动。吉祥物鸭子 Qoduck 承担引导、空状态与情绪反馈。</p>
    <div class="scroll-x"><table class="matrix">
      <tr><th>Logo 规格</th><th>值</th></tr>
      <tr><td>画布</td><td><code>72×72px</code>，mask = qoder-loading-line.svg（5 path / 3 渐变）</td></tr>
      <tr><td>本体 / 扫光</td><td>本体 <code>text-quaternary 72%</code> + <code>opacity .6</code>；扫光核心 <code>text-tertiary 54%</code></td></tr>
      <tr><td>光效</td><td>底部辉光 <code>blur(24px)</code>（=1/3 画布）opacity .58；扫光 <code>blur(10px)</code></td></tr>
      <tr><td>动画</td><td>呼吸 <code>2.15s linear</code>（62% → 0.86）；扫光 <code>2.15s cubic-bezier(.28,0,.62,1)</code>（前 72% 走完，留 28% 停顿）</td></tr>
      <tr><td>明暗</td><td>light <code>multiply</code> / dark <code>screen</code>；reduced-motion 直接移除扫光层</td></tr>
    </table></div>
    <h3 class="group-title">品牌取样色</h3>
    <div class="btn-demo-row" style="gap:14px">
      <span class="chip-tag" style="display:inline-flex;align-items:center;gap:8px"><span style="width:14px;height:14px;border-radius:4px;background:#4B6F5A;display:inline-block"></span>UI 主色 #4B6F5A</span>
      <span class="chip-tag" style="display:inline-flex;align-items:center;gap:8px"><span style="width:14px;height:14px;border-radius:4px;background:#5CB870;display:inline-block"></span>UI 主色(dark) #5CB870</span>
      <span class="chip-tag" style="display:inline-flex;align-items:center;gap:8px"><span style="width:14px;height:14px;border-radius:4px;background:#2ADB5C;display:inline-block"></span>产品 Logo 绿 #2ADB5C</span>
      <span class="chip-tag" style="display:inline-flex;align-items:center;gap:8px"><span style="width:14px;height:14px;border-radius:4px;background:#255A41;display:inline-block"></span>内联字标绿 #255A41</span>
      <span class="chip-tag" style="display:inline-flex;align-items:center;gap:8px"><span style="width:14px;height:14px;border-radius:4px;background:#FFD966;display:inline-block"></span>Qoduck 黄 #FFD966</span>
      <span class="chip-tag" style="display:inline-flex;align-items:center;gap:8px"><span style="width:14px;height:14px;border-radius:4px;background:#F87825;display:inline-block"></span>鸭喙橙 #F87825</span>
    </div>
    <p class="sec-desc" style="margin-top:12px">发现<b>三套绿未收敛</b>：UI 语义绿 <code>#4B6F5A</code>、产品 Logo 亮绿 <code>#2ADB5C</code>、内联字标深绿 <code>#255A41</code>——用途不同但缺少明文映射规则。876 个 webp 中 <b>743 个是语音 orb 序列帧</b>，first-use 贴纸 12 类，另有成长徽章（7/30/100 天、周年）。</p>
    <div class="asset-row">
      <div class="asset"><img src="./assets/icons/qoder-light.png" alt="Qoder logo light"><span>qoder-light<br>应用图标</span></div>
      <div class="asset"><img src="./assets/icons/qoder-dark.png" alt="Qoder logo dark"><span>qoder-dark<br>应用图标</span></div>
      <div class="asset"><img src="./assets/illustrations/Qoduck01-Dwn546pz.webp" alt="Qoduck"><span>Qoduck01<br>吉祥物</span></div>
      <div class="asset"><img src="./assets/illustrations/duckReading-DvaKonHI.webp" alt="duck reading"><span>duckReading<br>场景贴纸</span></div>
      <div class="asset"><img src="./assets/illustrations/glass-light-BX6cg1om.webp" alt="glass light"><span>glass-light<br>玻璃材质</span></div>
    </div>
  </section>

  <footer>
    <p><b>方法</b>：解析 app.asar 头部 → 抽取 15 个 CSS、12 个 JS bundle 与静态资源 → 自写 CSS 解析器还原「选择器/声明/变量」→ 用语义工具类名反解哈希变量 → 与主题选择器交叉还原 light/dark/主题覆写值 → 计算 WCAG 对比度。</p>
    <p><b>证据等级</b>：本页所有色值、字号、时长、缓动均来自产物实测；"推断"已在上文标注；未在产物中找到依据的项目未写入。</p>
    <p style="margin-top:14px">Qoder CN 0.5.7 · build 87859884 · commit 73fe8d73 · Electron 43.8.4 · 逆向分析于 2026-11-11</p>
  </footer>
</div>
<script>{JS}</script>
</body>
</html>
"""

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write(HTML)
print("written", OUT, os.path.getsize(OUT), "bytes")
