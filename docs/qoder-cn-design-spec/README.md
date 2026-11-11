# Qoder CN 设计规范逆向分析

对 **Qoder CN 0.5.7**（Electron 43 + React 19 + Tailwind CSS v4 桌面应用）设计系统的逆向还原成果。

- **分析对象**：`C:\Users\<user>\AppData\Local\Qoder CN\Qoder CN Launcher\Qoder CN Launcher.exe` 引导安装的应用（`E:\develop-lcb\apps\Qoder CN\.qoder-versions\0.5.7`）
- **方法**：解包 `app.asar`（6,448 文件 / 295 MB），对 CSS 产物、React bundle 与静态资源做静态逆向。**未运行应用本体**。
- **版本**：Qoder CN 0.5.7 · build 87859884 · commit 73fe8d73 · Electron 43.8.4 · 分析于 2026-11-11

> 注：`Qoder CN Launcher.exe` 本身只有 131 KB，是一个引导器（负责安装/更新/拉起），真正的产品界面与设计系统在其拉起的 Electron 应用内。

## 目录结构

```text
.
├── Qoder-CN-设计规范逆向分析.md   # 主报告：14 章
├── design-spec.html               # 可视化规范页（单文件自包含，浏览器打开）
├── README.md                      # 本文件
├── tokens/                        # 机器可读设计 token
│   ├── design-tokens.json         #   68 语义色 + 10 主题矩阵 + 字体/间距/圆角/动效/状态契约
│   ├── semantic-tokens-raw.json   #   语义 token 原始解析（哈希变量名/工具类名/CSS 属性）
│   └── theme-matrix.json          #   10 套主题关键 token 矩阵
├── appendix/                      # 分线原始分析（逐条证据）
│   ├── components.md              #   组件库规范（806 行，27 个组件族）
│   ├── surfaces.md                #   界面与信息架构（12 个 Surface、窗口尺寸、导航、流程）
│   └── brand.md                   #   品牌视觉（Logo 逐行取证、图标取样、插画、材质）
├── assets/                        # 从应用中提取的素材
│   ├── icons/                     #   应用图标（light/dark、windows 版）
│   ├── illustrations/             #   Qoduck 吉祥物、场景贴纸、玻璃材质
│   ├── brand/                     #   启动屏 logo 源文件、托盘/应用 ico
│   └── fonts/                     #   Inter / Instrument Sans / qoder-seti 字体子集
├── preview/                       # 可视化页截图
│   ├── preview-light.png
│   ├── preview-dark.png
│   └── preview-full.png
└── scripts/                       # 逆向分析脚本（可复现用，Python 3.13）
    ├── asar_lib.py                #   轻量 asar 解析器（header 解析 / 按路径解包）
    ├── inventory.py / structure.py / designsys.py   # 文件盘点、目录结构、包结构
    ├── extract.py                 #   抽取 CSS / HTML / JS bundle / SVG
    ├── analyze_css.py             #   CSS 变量、工具类、字体、keyframes 统计
    ├── parse_tokens.py            #   CSS 块解析 + 类名 → 哈希变量映射
    ├── resolve_tokens.py          #   主题选择器归类 → 语义 token 表
    ├── theme_matrix.py            #   10 套主题色彩矩阵
    ├── scales.py                  #   字号/圆角/阴影/动效/层级等尺度
    ├── contrast.py                #   WCAG 对比度计算
    ├── motion.py                  #   从 JS bundle 提取缓动/时长/弹簧参数
    ├── deep_dive.py               #   aura 动效、间距、圆角、data-* 契约统计
    ├── dump_rules.py              #   按选择器模式导出 CSS 规则
    ├── gen_tables.py / gen_tokens_json.py  # 报告表格与 token JSON 生成
    └── gen_html.py                #   可视化规范页生成器
```

## 快速开始

- **读报告**：任意 Markdown 阅读器打开 `Qoder-CN-设计规范逆向分析.md`。
- **看可视化页**：双击 `design-spec.html`（建议 Chromium 内核浏览器，支持 `corner-shape` 等新特性）。右上角切换 light/dark；导航可跳转。
- **用 token**：直接消费 `tokens/design-tokens.json`（结构见文件内 `meta` / `color` / `typography` / `motion` / `a11y` 字段）。

## 证据等级约定

主报告中：**【实测】** = 产物中直接读到的值/选择器；**【推断】** = 由命名与用法推断；**【未确认】** = 产物中无证据，不做臆测。ASCII 布局图与语义解释属于对实测数据的整理。

## 关键结论速览

| 维度 | 结论 |
|---|---|
| 色彩 | **68 个语义 token + 10 套主题**（light/dark × forest/bee/mint/parchment）；CSS 变量哈希化（`--qXXXXXX`），但语义工具类名可读（`.bg-bg-container`） |
| 排版 | 主 UI **系统字体栈 + 12px 基准**；内容侧 `.typeset` 四模式（chat 14 / compact 13 / docs 15 / reading 16），标题 `base + 6/4/2/0` 相对计算 |
| 组件 | **153 个组件**；尺寸严格收敛 **20/28/36px**（sm/md/lg）；圆角为 `corner-shape: squircle` 超椭圆体系（控件 16px）；焦点用边框/底色变色、不画 ring |
| 界面 | 单 HTML + `?surface=` 路由出 **12 个 Surface**；主窗 1320×800，左栏 248/208、右栏 280，会话限宽 768/820/924；frameless + 40px 自绘标题栏 |
| 动效 | 主缓动 `cubic-bezier(.2,.8,.2,1)` 使用 **111 次**；UI 过渡 140–240ms；8 组弹簧；主题切换 160ms View Transition；reduced-motion 覆盖 30 处 |
| 品牌 | 启动屏 72px mask logo + 呼吸/扫光双动画（2.15s，扫光留 28% 停顿）；Qoduck 鸭子承担引导与情绪反馈；876 张 webp 中 743 张为语音 orb 序列帧 |
| 可访问性 | 主/次级文本达标；**短板**：`text-quaternary` 在 8/10 主题下 < 4.5:1、浅色 `warning` 作文字 1.9:1、`mint-light` 主按钮 2.7:1、焦点态无全局基线 |

## 复现说明（可选）

脚本按分析过程写成，含当时使用的绝对路径（`E:\develop-lcb\apps\Qoder CN\.qoder-versions\0.5.7\resources\app.asar` 等），复现时需按本机安装位置调整：

```powershell
python scripts/asar_lib.py          # 验证 asar 可解析
python scripts/inventory.py         # 文件盘点
python scripts/parse_tokens.py      # 生成 token_defs.json / class_var.json
python scripts/resolve_tokens.py    # 生成 semantic_tokens.json
python scripts/theme_matrix.py      # 生成 theme_matrix.json
python scripts/contrast.py          # 对比度报告
python scripts/gen_tokens_json.py   # 生成 tokens/design-tokens.json
python scripts/gen_html.py          # 生成 design-spec.html
```

依赖仅为 Python 3.13 标准库（`contrast.py` 纯计算，无第三方依赖；Pillow 仅用于个别取色脚本）。
