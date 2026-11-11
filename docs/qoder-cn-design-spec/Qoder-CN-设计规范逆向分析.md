# Qoder CN 桌面端设计规范逆向分析报告

> 分析对象：`C:\Users\chenbo.li\AppData\Local\Qoder CN\Qoder CN Launcher\Qoder CN Launcher.exe`
> 实际应用：`E:\develop-lcb\apps\Qoder CN\.qoder-versions\0.5.7`（Qoder CN 0.5.7，Electron 43.8.4）
> 分析方式：解包 `app.asar`（6,448 个文件 / 295 MB），逆向其 CSS 产物、React bundle 与静态资源
> 证据等级：**【实测】**= 产物中直接读到的值；**【推断】**= 由命名/用法推断；**【未确认】**= 产物中无证据

---

## 0. 结论摘要

Qoder CN 是一个以 **"Agent workbench for human and AI software teams"** 为定位的 Electron + React 19 桌面应用，但它并不是 VS Code 套壳：它自带一套**自研设计系统**（`@qoder-space/design-system`），构建在 **Tailwind CSS v4** 之上，并做了相当程度的规范化建设：

| 维度 | 规范成熟度 | 关键证据 |
|---|---|---|
| 色彩系统 | ★★★★★ 68 个语义 token + 10 套主题 | 499 个 CSS 变量，`--q` 前缀哈希化，工具类名保留语义 |
| 排版系统 | ★★★★★ 4 套内容排版模式（typeset） | `.typeset-chat/-compact/-docs/-reading` 全套规则 |
| 动效系统 | ★★★★☆ 收束到 1 条主缓动 + 8 组弹簧 | `cubic-bezier(.2,.8,.2,1)` 出现 111 次 |
| 组件规范 | ★★★★☆ 组件层 + 变体/状态契约 | `data-variant` 45 处、`data-state` 56 处、`data-slot` 22 处 |
| 可访问性 | ★★★☆☆ 有 reduced-motion 与缩放，但对比度有硬伤 | 30 处 `prefers-reduced-motion`；四级文本在 8/10 主题下不达 WCAG AA |
| 主题工程 | ★★★★☆ 10 套主题 × 平台差异 | light/dark × forest/bee/mint/parchment，Windows 关闭毛玻璃 |

**一句话总结**：这是一套"**克制的系统字体 + 12px 致密布局 + 语义化色彩分层 + 内容排版模式化 + 统一动效曲线 + 人格化 AI 视觉**"的桌面设计语言。它的 token 架构可以直接借鉴，但对比度与焦点态是明显短板。

**关键数字**：68 个语义色 token · 10 套主题 · 60 个 keyframes · 4 种内容排版模式 · 8 组弹簧参数 · 6 种字体 · 876 张 webp 插画 · 197 个 svg 图标。

---

## 1. 分析方法与证据链

```
Qoder CN Launcher.exe (131 KB，引导器)
  └─ state.ini  →  installDir=E:\develop-lcb\apps\Qoder CN, targetVersion=0.5.7
       └─ .qoder-versions\0.5.7\resources\app.asar (200 MB)
            ├─ package.json        → 技术栈与依赖
            ├─ out\main\           → Electron 主进程 (electronMain.js 20 MB)
            ├─ out\preload\        → 预加载脚本
            ├─ out\renderer\       → React UI（Vite 构建产物）
            │    ├─ index.html     → 启动壳 + 启动屏 + CSP
            │    └─ assets\        → 15 个 CSS、1652 个资源（svg/webp/js/字体）
            └─ node_modules\       → 运行期依赖
```

- 解析工具：自写 asar header 解析器（`asar_lib.py`），按需抽取文件，**未运行应用本体**。
- CSS 逆向：写了一个轻量 CSS 解析器，把 Tailwind v4 产物还原成「选择器 → 声明 → 变量」结构，再与语义工具类名交叉映射，破解了哈希变量（如 `--q71fecd` = `bg-container`）。
- 版本信息【实测】：`buildTime=2026-11-09`、`commit=73fe8d73`、`electronVersion=43.8.4`、`buildNumber=87859884`。

---

## 2. 产品与技术底座

| 项 | 值 |
|---|---|
| 产品定位 | Agent workbench for human and AI software teams |
| 桌面框架 | Electron 43.8.4（Chromium 内核，支持 View Transitions、`corner-shape` 等新特性） |
| UI 框架 | React 19 + `react-i18next` + framer-motion 12 + GSAP |
| 样式方案 | Tailwind CSS v4（`@layer theme/components/utilities`）+ CSS 变量 |
| 自研设计系统 | `@qoder-space/design-system`（编译进产物，无独立源码） |
| 代码高亮 | Shiki 4（内置多套主题，CSS 里可见 catppuccin / github / nord 等 id） |
| 目录结构 | `out/main`（主进程）、`out/preload`（桥接）、`out/renderer`（UI）、`resources/extensions`（10 个内置扩展） |
| 安装形态 | 用户级安装 + 版本化目录 `.qoder-versions\<ver>` + 独立 Launcher 引导器 |

**产品形态**：从资源命名可断定它不是单一 IDE 窗口，而是一个**多 Surface 的 Agent 工作台**——主窗口之外还有 Dynamic Island 面板、桌面宠物、语音悬浮 orb、快捷笔记、协作者活动、首次引导等独立界面（见第 8 章）。

---

## 3. 设计语言总览（7 条原则）

1. **系统字体优先、致密布局**：`font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`，`body` 基准字号 `12px`（`--text-xs`），以换取"专业工具"的信息密度【实测】。
2. **语义 token 三层架构**：原始值 → 语义 token（68 个色 + 尺度）→ 工具类（`.bg-bg-container`、`.text-primary`）。业务代码只允许用语义层【实测 + 推断】。
3. **表面分层**：`bg-base → bg-container → bg-elevated` 三级纵深厚度的背景体系，配合 `bg-spotlight`/`bg-mask` 修饰，而不是靠阴影堆叠【实测】。
4. **内容即界面**：`.typeset` 为 AI 回答、文档、阅读三种场景提供四套排版模式，排版规则集中在设计系统层【实测】。
5. **一条主缓动统治动效**：`cubic-bezier(.2,.8,.2,1)` 贯穿 111 次使用，时长集中 140–240ms，界面动效高度统一【实测】。
6. **AI 人格化**：aura 光晕、语音 orb（3 种视觉主题）、Qoduck 鸭子吉祥物、Dynamic Island 状态胶囊，把"AI 在思考/在听/在忙"做成有生命感的视觉语言【实测】。
7. **自适应**：`data-theme`（10 主题）、`data-font-size`（3 档）、`data-ui-scale`（1.1 缩放）、`data-platform`（Windows 去特效）、`data-visual-effects`（一键关闭模糊/阴影）——同一套 UI 适配不同环境【实测】。

---

## 4. 色彩规范

### 4.1 架构

```
原始色值（按主题定义）
   ↓  每套主题各定义一份
语义 Token（68 个）  例：bg-container / text-secondary / primary-hover / success-bg
   ↓  Tailwind @theme 生成工具类
工具类            例：.bg-bg-container / .text-text-secondary / .border-primary-border
   ↓
组件与页面
```

关键设计：CSS 变量名被**哈希化**（`--q4fa275` 等），但工具类保留语义（`.bg-bg-container`），既防抄袭又不损失可读性【实测】。

### 4.2 语义 Token 全表

**背景表面（4 级纵向层次 + 2 个修饰）**

| Token | Light | Dark | 用途 |
|---|---|---|---|
| `bg-base` | `#fff` | `#0e0e0e` | 页面/窗口最底层 |
| `bg-container` | `#fff` | `#111110` | 容器/卡片/面板 |
| `bg-elevated` | `#f9f9f9` | `#22221f` | 浮起层（弹层、悬浮面板） |
| `bg-layout` | `#fff` | `#111110` | 窗口壳底板 |
| `bg-spotlight` | `#fafafa` | `#22221f` | 聚光/强调背景 |
| `bg-mask` | `#95959466` | `#242421` | 遮罩 |

**文本（5 级）**

| Token | Light | Dark | 对比度（vs `bg-container`） |
|---|---|---|---|
| `text` | `#141414` | `#eeeeeb` | AAA（18.4 / 16.3） |
| `text-secondary` | `#636261` | `#b4b4ac` | AA（6.1）/ AAA（9.1） |
| `text-tertiary` | `#838280` | `#7b7b74` | 3.8–4.4（仅大字达标） |
| `text-quaternary` | `#aaa9a8` | `#585853` | **2.3–2.6（不达 AA）** |
| `text-on-primary` | `#fdfdfd` | `#080807` | 随主色变化，见 4.5 |

**边框 / 填充（层级递减）**

| Token | Light | Dark |
|---|---|---|
| `border-secondary` / `border-tertiary` / `border-quaternary` | `#ddd` / `#e6e6e6` / `#eee` | `#31312d` / `#292926` / `#20201e` |
| `fill` / `fill-secondary` / `fill-tertiary` | `#dfdfdf` / `#efefef` / `#f6f6f6` | `#31312d` / `#292926` / `#22221f` |

> 注意 `border` 这个 token 存的不是颜色，而是 `0 0 0 1px #0000000f`（浅色）/ `0 0 0 1px #ffffff14`（深色）——**1px 发丝描边用 box-shadow 实现**，属于刻意的细节规范【实测】。

**主色（品牌色）与状态色**

| 组 | Token | Light | Dark |
|---|---|---|---|
| 主色 | `primary` | `#4b6f5a`（鼠尾草绿） | `#5cb870` |
| | `primary-hover` / `primary-active` | `#436651` / `#3a5747` | `#9be6b3` / `#73cd94` |
| | `primary-text` / `link` | `#4b6f5a` / `#4d9868` | `#8ee5a1` |
| | `primary-bg` / `primary-border` | `#f2f4f2` / `#d5dbd8` | `#14261c` / `#335942` |
| 状态 | `success` / `warning` / `error` / `info` | `#579b6e` / `#efb041` / `#ec5b56` / `#3b81e9` | `#73cd94` / `#faad14` / `#ff4d4f` / `#0b83f1` |
| | `*-bg` / `*-border` | 极浅同色系 | 极深同色系 |
| 辅助 | `mint` / `lavender` / `mauve` / `sage` | `#7fbb7a` / `#b49ef9` / `#8e8c98` / `#7cb196` | 同色相提亮 |
| 特殊 | `diff-insert` | `#aec8ba` | `#73cd94` |

### 4.3 主题体系（10 套）

主题 = 5 个色系家族 × 明暗：

| 家族 | Light | Dark | 气质 |
|---|---|---|---|
| 标准 | `light` | `dark` | 中性灰绿，默认 |
| forest | `forest-light` | `forest-dark` | 森林绿，中性偏绿 |
| bee | `bee-light` | `bee-dark` | 蜂黄，暖橄榄 |
| mint | `mint-light` | `mint-dark` | 薄荷青，冷绿 |
| parchment | `light-parchment` | `parchment-dark` | 羊皮纸暖棕（`#c96442` 陶土色） |

关键 Token 矩阵（节选）：

| Token | light | dark | bee-light | bee-dark | mint-light | mint-dark | light-parchment | parchment-dark |
|---|---|---|---|---|---|---|---|---|
| `bg-container` | `#fff` | `#111110` | `#fff` | `#12130f` | `#fff` | `#0e1411` | `#fff` | `#171512` |
| `bg-elevated` | `#f9f9f9` | `#22221f` | `#f9f9f9` | `#20221d` | `#f9f9f9` | `#1a2420` | `#f6f5f3` | `#26221d` |
| `text` | `#141414` | `#eeeeeb` | `#141414` | `#f2f1e8` | `#2f4b2d` | `#eaf3ef` | `#202116` | `#f1ece5` |
| `primary` | `#4b6f5a` | `#5cb870` | `#0d0d0d` | `#e0c65c` | `#4fa98f` | `#62c9a8` | `#c96442` | `#e08a68` |
| `text-on-primary` | `#fdfdfd` | `#080807` | `#fdfdfd` | `#171407` | `#f7faf8` | `#07130f` | `#fff9f4` | `#1b0e09` |

**主题工程观察**
- 主题切换会**同时重算背景、文本、边框、填充、主色全套**，而不是只换主色；每个主题有 20–160 个 token 级覆写【实测】。
- 切换动画走 **View Transitions API**：`data-qoder-theme-transition="fade"`，`--q26f0e9 = 160ms`，`ease-out`，且 `prefers-reduced-motion` 时直接跳变【实测】。
- 命名有不对称：`light-parchment` 对 `parchment-dark`（其他家族都是 `xxx-light` 对 `xxx-dark`），属于产物中的命名瑕疵【实测】。
- 平台差异：Windows 下 `forest-light`/`mint-light` 用实色背景覆盖半透明（如 mint `#c9e8dd`），并关闭渐变与毛玻璃【实测】。

### 4.4 用法规则（从产物归纳）

1. **表面层级选型**：页面底 → `bg-base`；卡片/面板 → `bg-container`；弹层/悬浮 → `bg-elevated`；窗口壳 → `bg-layout`。
2. **透明度修饰**：直接用类名后缀表达 `/95`、`/10` 等，如 `.bg-bg-container\/95`、`.border-bg-base\/10`，对应 `color-mix(in oklab, var(...) 95%, transparent)`【实测】。
3. **发丝描边**：优先 `border` token（box-shadow 模拟 1px），不用 `1px solid` 直接写。
4. **状态色永远成组使用**：`success` + `success-bg` + `success-border`，禁止只取单色【推断】。
5. **反色块**用 `bg-highlight` + `text-on-primary` 组合，保证深浅主题下都成立【实测】。

### 4.5 对比度合规检查（WCAG 2.1）

对 10 套主题 × 关键文字 token 计算对比度：

| Token | light | dark | mint-light | light-parchment | 判定 |
|---|---|---|---|---|---|
| `text` | 18.4 AAA | 16.3 AAA | 9.7 AAA | 16.3 AAA | ✅ 全通过 |
| `text-secondary` | 6.1 AA | 9.1 AAA | 6.5 AA | 9.4 AAA | ✅ 全通过 |
| `text-tertiary` | 3.8 | 4.4 | 4.2 | 5.7 | ⚠️ 仅大字达标（浅色系） |
| `text-quaternary` | 2.3 | 2.6 | 2.6 | 2.5 | ❌ **8/10 主题不达 AA** |
| `primary`（作文字） | 5.6 AA | 7.7 AAA | **2.8 FAIL** | 3.9 | ❌ mint-light 失败 |
| `warning`（作文字） | **1.9 FAIL** | 9.9 AAA | 1.9 FAIL | 5.9 AA | ❌ 浅色全败 |
| `text-on-primary` 按钮 | 5.55 AA | 8.15 AAA | **2.70 FAIL** | 3.73 | ❌ 2 套主题不达标 |

**结论**：主文本与次级文本的对比度体系是可靠的；问题集中在三处——
- `text-quaternary` 作为正文级颜色使用会不达标，应限定在"装饰性/非关键"场景；
- 浅色主题的 `warning`（`#efb041` on `#fff`）和 `mint-light` 的 `primary` 作为文字色必须加粗/放大或换色；
- `mint-light` 与 `light-parchment` 的**主按钮文字**不达 AA，属于主题设计缺陷。

---

## 5. 字体与排版规范

### 5.1 字体角色矩阵【实测】

| 字体 | 声明/作用域 | 角色 | 字重 | 证据 |
|---|---|---|---|---|
| 系统字体栈 | `:root` 默认 | 全局 UI 正文 | — | `-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif` |
| **Inter** | 预加载 + `.font-['Inter']`、用户卡姓名 | 需要跨平台一致性的文本 | 400/500/600（含斜体） | 60 个 woff/woff2 子集 |
| **Instrument Sans** | Dynamic Island 品牌字、Onboarding 贴纸品牌字、用户卡邮箱 | 品牌/营销/HUD | 400/500 | `font-family: Instrument Sans, ...` |
| **Crimson Pro** | 仅 @font-face，CSS 中无直接引用 | 长文/编辑感阅读（推断：阅读模式或 AI 文案） | 400/600 | 6 个子集文件 |
| **Dynamic Island Inter** | 仅 Dynamic Island 面板 | 灵动岛专用（等宽数字/紧凑排版） | 100–900 可变 | 2 个子集 |
| **qoder-seti** | 文件树图标字体 | 文件类型图标（Seti 风格） | — | `qoder-seti-*.woff` |
| **KaTeX 系列** | 公式渲染 | 数学公式 | — | 21 个字体文件 |

**要点**：主 UI 用**系统字体**（性能/原生感优先），Inter 只在需要"设计一致性"的局部出现，品牌场合才切 Instrument Sans——这是很克制的字体策略。

### 5.2 字号阶梯

Tailwind 主题层给出标准阶梯，实际使用更细（存在 `11px/13px` 等硬编码）：

| Token | 字号 | 行高 | 实际使用 |
|---|---|---|---|
| `--text-xs` | 12px | 16px | **body 基准**、辅助信息 |
| `--text-sm` | 14px | 20px | 正文/聊天内容 |
| `--text-base` | 16px | 24px | 大正文 |
| `--text-lg` | 18px | 28px | 小标题 |
| `--text-xl` | 20px | 28px | 标题 |
| `--text-2xl` | 24px | 32px | 大标题 |
| 硬编码 | 11px / 13px / 14px / 16px | 18/20/22/24px | 徽标、按钮、表格 |

字重使用：400（正文）34 次、500（强调）32 次、600（标题/按钮）21 次、700（大标题）11 次【实测】。

### 5.3 基准与缩放

- **全局基准 12px**：`body { font-size: var(--text-xs) !important }`——比常规 Web 应用小 2–4px，符合"专业工具型"密度【实测】。
- **用户字号三档**（仅作用于聊天正文与 markdown）【实测】：

| 档位 | 正文 | 代码 | 行高 |
|---|---|---|---|
| `data-font-size=small` | 13px | 12px | 24px |
| `data-font-size=medium` | 14px | 13px | 24px |
| `data-font-size=large` | 16px | 14px | 28px |

- **UI 缩放**：`data-ui-scale=large` 时对侧栏、内容区、B 站式区域设 `zoom: 1.1`，且只作用于带 `data-qoder-ui-scale-sidebar` / `[data-chat-session-region=B1-CONTENT]` 等标记的区域，避免整窗模糊【实测】。

### 5.4 `.typeset` 内容排版系统

这是 Qoder 最有价值的一套规范：AI 输出/文档/阅读都用同一套排版内核，通过模式变量切换密度。

| 模式 | 基准字号 | 行高 | 段间距 | 标题间距 | 列表缩进 |
|---|---|---|---|---|---|
| `.typeset`（默认） | 14px | 24px | 12px | 20px | 20px |
| `.typeset-chat` | 14px | 24px | 12px | 24px | 20px |
| `.typeset-compact` | 13px | 22px | 8px | 16px | 12px |
| `.typeset-docs` | 15px | 26px | 16px | 28px | 13px |
| `.typeset-reading` | 16px | 30px | 20px | 32px | 14px |

**标题阶梯采用相对计算**（不以固定 px 写死）：`h1 = base + 6px`、`h2 = base + 4px`、`h3 = base + 2px`、`h4-h6 = base`；`h6` 大写（`text-transform: uppercase`）+ 三级文本色。**所有标题字重统一 600**，`letter-spacing: 0`【实测】。

**其他规则**【实测】：
- 段/列表/表格统一 `font-size: base`、`line-height: lh`；
- 行内代码：`border-radius: 4px`、背景 `fill-tertiary`、字号 `base - 1px`、`padding: 2px 4px`；
- 代码块（pre）：字号取 `--q265d82`（12/13px）、行高 20px；
- 引用：`border-inline-start: 2px solid primary`、`padding-inline-start: 16px`、斜体、三级文本色；
- 表格：`border-collapse: collapse`，表头 `fill-tertiary` 背景 + 600 字重，单元格 `padding: 8px 12px`，行分隔 `border-tertiary`；
- `strong` 600 字重、`em` 斜体，都不换色（继承正文 `text`）。

### 5.5 排版规则小结

1. 标题、正文、代码的字号必须从 typeset 模式派生，**不要单点写死**。
2. 强调只用字重（500/600），不靠变色——颜色留给语义状态。
3. 行内代码与正文差 1px，代码块与正文差 1–2px，保持"同族不同级"。
4. 表格一律无外框、有行线、表头有底色。

---

## 6. 间距、圆角、阴影与层级

### 6.1 间距：严格 4px 网格

`--spacing: 0.25rem`（4px），所有间距/尺寸用 `calc(var(--spacing) * n)` 表达。产物中高频档位：**4 / 8 / 12 / 16 / 24px**；组件内边距多为 8/12px，区块间距 16/24px，页面级 32px+【实测 + 推断】。

### 6.2 圆角阶梯

| Token | 值 | px |
|---|---|---|
| `--radius-xs` | `.125rem` | 2px |
| `--radius-sm` | `.25rem` | 4px |
| `--radius-md` | `.375rem` | 6px |
| `--radius-lg` | `.5rem` | 8px |
| `--radius-xl` | `.75rem` | 12px |
| `--radius-2xl` | `1rem` | 16px |

实际使用还包括 `3/5/10/20/24px`、`50%`、`9999px`（胶囊）。**特色**：30 处使用 `corner-shape: squircle`（超椭圆圆角）——主要出现在 Onboarding 卡片（20px 圆角 + squircle）与数据目录进度界面，属于品牌化的圆角处理【实测】。

### 6.3 阴影：刻意克制

全量 CSS 中**只有 13 条非 Tailwind 的 box-shadow**，且多为变量化的一次性阴影（如 `0 60px 120px`、`0 12px 25px`）【实测】。说明层级区分**主要靠表面色 + 1px 描边**，阴影只用于真正的浮层（弹层/拖拽/悬浮 HUD）。

### 6.4 层级（z-index）分布

实际取值从 `-10` 到 `1200`，常见档位：`0/1/2/3`（局部堆叠）、`10/20/30`（浮层）、`50/60/80/100`（弹层/遮罩）、`360`（拖拽层）、`1000/1100/1200`（全局/启动屏）。启动屏用 `2147483647`（最大值）保证首屏覆盖【实测】。

---

## 7. 组件规范

### 7.1 组件体系：三层混合结构

| 层 | 形态 | 代表 | 规模 |
|---|---|---|---|
| L1 设计系统组件 | `S__Wc8-4.js`（3.2 MB，**未深度混淆**）中 Radix primitive + `cva()`/`clsx()` | Button、Input、Select、Tabs、Switch | **153 个组件**、56 个 `data-slot`、32 种 role |
| L2 CSS 自研组件类 | `index-BFGCOCH4.css` 中手写 `.qoder-*` 类 + `data-state` 选择器 | `.qoder-drawer-*`、`.qoder-empty-state-*`、`.qoder-user-card` | 570 条规则、12 个 keyframes |
| L3 应用层组合 | `gtdG4YpP.js` 中用 L1 + 工具类 + `data-*` 拼装 | Chat Composer、侧边栏、上下文菜单 | 主渲染 bundle |

组件基座依赖：**Radix UI**（浮层/选择/滑块/进度等全部继承）、**CVA**（变体管理）、**Framer Motion**（浮层进退场）、**sonner**（Toast）、**streamdown**（Markdown 渲染）。

### 7.2 跨组件基础约定（规范核心）

**① 尺寸阶梯：20 / 28 / 36（sm/md/lg + custom 逃生口）**

| 档位 | 高度 | 典型组件 |
|---|---|---|
| `sm` | `h-5` = **20px** | Button(sm)、Input(sm)、Select(sm)、IconButton(sm) |
| `md`（默认） | `h-7` = **28px** | Button(md)、Input(md)、Select(md)、SendButton |
| `lg` | `h-9` = **36px** | Button(lg)、Input(lg)、Select(lg) |
| `custom` | — | 类名为空串，交给调用方 |

> **这是全库最强的一致性约束**：按钮、输入、选择、图标按钮四类控件在 sm/md/lg 完全对齐；图标按钮另有 `size-5/7/9` 与高度一致。

**② 圆角：`corner-shape: squircle` 超椭圆体系（不是普通 rounded）**

| 语义档 | 类 | 半径 | 使用者 |
|---|---|---|---|
| 控件标准 | `squircle-2xl` | **16px** | Button(square)、Input、Textarea、SelectTrigger |
| 浮层/容器 | `squircle-xl` | **12px** | ChatInput 外壳、建议面板、TabsList(segmented) |
| 标签 | `squircle-4` | 4px | Tag(sm)、SourcePreviewSwitch |
| 胶囊 | `squircle-full` | 9999px | Button(`rounded="pill"`) |

产物在 `.qoder-user-card` 等处以 `@supports (corner-shape: squircle)` 包裹并提供 `border-radius` 兜底——**这是调研中最有辨识度的视觉规范**（全站 30 处 squircle）。

**③ 字号**：按钮/输入/菜单/标签页默认 **13px**（"主 UI 字号"），sm 用 12px、lg 用 14px，标签最小 10–11px。12/13/14 三个近邻字号大量并用，属"事实标准"而非 token 标准。

**④ 状态表达**：

| 状态 | 统一做法 |
|---|---|
| hover | `hover:bg-fill-secondary/tertiary` 或 `hover:text-text` |
| focus | **不画 ring**：`focus:outline-none focus:ring-0`，改用边框变色/底色变化（Input `focus:border-border`） |
| focus-visible | 键盘焦点才变色（Button `focus-visible:bg-primary-active`） |
| active | `active:` 变体；raised 按钮有 `active:scale-[0.96]` 按压反馈 |
| disabled | 统一 `opacity-50 cursor-not-allowed`，**无独立 disabled 色 token** |
| 状态型 | `data-state` / `data-[state=checked]` 等 Radix 约定驱动 |
| 减少动效 | 全库 `motion-reduce:` 兜底 |

**⑤ 动效**：组件默认 `duration-150` + `ease-out`；强调控件 120ms；浮层 `opacity 0→1 + scale .95→1 + 位移 4px`、150ms；抽屉 进入 .24s / 退出 .2s / reveal .35s。

**⑥ 图标**：菜单 `size-3`(12px)、标签/面包屑 `size-3.5`(14px)、输入/按钮 `size-4`(16px)、IconButton sm `size-5`(20px)。

### 7.3 27 个组件族速查

| 组件族 | 关键规范 |
|---|---|
| Button | **12 种变体**（primary/secondary/tertiary/tertiaryDestructive/ghost(默认)/text/textPrimary/textSuccess/link/outline/raised/destructive）× 3 尺寸；`squircle-2xl`；无 loading 态 |
| IconButton | 5 变体（primary/secondary(默认)/tertiaryDestructive/ghost/toolbar 玻璃拟态）；`aria-pressed` 支持切换态 |
| Input / Textarea | outline/filled；focus 有 `border`/`shadow` 两种反馈；error 走 `aria-invalid` |
| Field / Label / InputGroup | `@container` 响应式两列（min-width 400px）；`has-aria-invalid` 联动错误态 |
| Chat Composer | 旗舰复合组件：外壳 `squircle-xl` + `focus-within:border-primary-border`；min-h 44px；Enter 发送 / Shift+Enter 换行 / 中文输入法保护；自动增高上限 6 行 |
| Select / MultiSelect | default/inline(虚线下划线)/inlineContinuation 变体；浮层 `max-h-96`、`rounded-lg`、150ms 进出场 |
| DropdownMenu | Radix 菜单；`data-[highlighted]` 键盘高亮 |
| Dialog / AlertDialog | `max-h-[90vh] + w-[calc(100%-2rem)]`；无 sm/md/lg 尺寸档 |
| Drawer | slide（.24/.2s）与 reveal（.35s，位移 94px + blur 2px）两种运动 |
| Tooltip / HoverCard / Popover | 浮层三件套；150ms + 4px 位移 |
| Tabs | density(default/compact) × motion(none/sliding/crossfade/overlap) 双轴 |
| Table | 以 Markdown 展示为主，无数据表格交互规范（未确认） |
| Tag / Badge | appearance(filled/outline/subtle/plain/solid) × 17 色 × 3 尺寸；sm+subtle 例外压到 16px 高 |
| Avatar | compact/sm/md…；`text-[10px]` 小字 |
| Toast | **sonner 实现，完全脱离 token 体系**（例外 E1） |
| Switch | 宽度三段式"吸引"动画；`data-switch-motion` |
| Checkbox / Radio | `data-state=checked` 驱动；选中 `bg-primary` |
| Progress / Skeleton | `indeterminate` / `animate-pulse` |
| Empty State | `.qoder-empty-state-stacked*` 堆叠卡形态 |
| Card | 无统一抽象，6+ 种定制卡（例外 E5） |
| Scrollbar / ScrollFade | 6px 细滚动条 + mask 边缘渐隐 + 滚动驱动动画 |
| Slider | sm/md；emphasis default/subtle；track `h-1/h-2` |
| Kbd | 三变体；**硬编码 Geist 字体**（例外） |
| SegmentedControl | `role=radiogroup` + 滑块 thumb 位移 26/52px |
| Breadcrumb | `nav aria-label=breadcrumb` + `aria-current=page` |
| SplitButton | 仅容器结构有规范，子件视觉由调用方传入（未确认） |

### 7.4 变体命名规律

设计系统把组件 API 归纳为 **8 个正交轴**：`variant`（语义角色）、`size`（sm/md/lg/custom）、`appearance`（filled/outline/subtle/plain/solid）、`color`（17 语义色）、`rounded`（square/pill）、`density`（default/compact）、`motion`（none/sliding/crossfade/overlap）、结构轴（shape/orientation/emphasis...）。缺省值几乎都是 `size="md"` + 最中性变体。

### 7.5 组件一致性短板（复刻时注意）

| # | 问题 | 影响 |
|---|---|---|
| E1 | Toast 用 sonner 自有 HSL 调色板，不接 token | 深浅主题/品牌色不一致 |
| E2 | `squircle-*` 与 `rounded-*` 混用 | 圆角语义不统一 |
| E3 | 组件层直接写 `var(--qXXXXXX)`（Switch/Radio/Alert） | token 语义丢失、暗色适配风险 |
| E4 | 字号大量 `text-[13px]` 任意值 | 排版阶梯漂移 |
| E5 | 无统一 Card 抽象（6+ 种定制卡） | 间距/圆角碎片化 |
| E6 | Button 无 loading 态 | 业务各自实现转圈 |
| E9 | Notification 三套实现（sonner / UpdateNotificationCard / Alert） | 使用边界不清 |

> 完整 27 个组件族的逐条取证（anatomy、变体表、token、a11y、证据原文）见随附的 `components.md` 原始分析（806 行）。

## 8. 布局与信息架构

### 8.1 窗口壳架构：单 HTML + 多 Surface 路由

全应用**只有 3 个 HTML 入口**：`index.html`（主壳 + 所有 Surface）、`dataDirectoryProgress.html`（迁移进度）、`hostedPresentationMenu.html`（演示菜单）。其余界面通过 `index.html?surface=<id>` 路由，入口读取 query 后设置 `document.documentElement.dataset.surface`，再动态 import 对应 chunk【实测】。

**主窗为 frameless + 自绘标题栏**：
- 标题栏高 **40px**（`h-10`）；`index.html` **刻意不写 `<title>`**（注释说明：带标题会让 Electron 忽略各窗口 title）；
- Windows：`titleBarStyle:hidden + frame:false + thickFrame:true + titleBarOverlay{height:40}`，窗口按钮由系统绘制在同一 40px 带内；
- macOS：`vibrancy + visualEffectState`，红绿灯位置 `{x:16,y:12}`；Linux：仅 `titleBarStyle`。

### 8.2 主窗口布局与尺寸

```
┌──────────────────────────────────────────────────────────────────────┐
│ 自绘标题栏 40px：[← →] [侧栏开关] …… 拖拽区 …… [窗口控制 / 账户菜单]   │
├───────────────┬──────────────────────────────────┬───────────────────┤
│ 区 A（aside） │ 区 B（main）                      │ 区 B2（右栏）      │
│ 左侧栏        │ ┌ B-HEADER 40px（工作区 Tab/地址栏）┐ │ 可折叠            │
│ 默认 248px    │ │ 会话时间线（限宽 768/820/924）  │ │ 默认 280px        │
│ 最小 208px    │ │ 产物预览 / 浏览器 / Review / 终端│ │ Issue 抽屉 620px  │
│ 可拖拽/折叠   │ └ Composer（底部固定）           ┘ │                   │
└───────────────┴──────────────────────────────────┴───────────────────┘
```

布局区域有显式命名常量：`A1-HEADER`、`A1-CONTENT`、`B-HEADER`、`B-CONTENT`，DOM 上对应 `data-layout-region="a"/"b"`【实测】。

| 区域 | 尺寸/规则 |
|---|---|
| 主窗口 | **1320×800**，最小 **720×540** |
| 登录窗口 | **690×446**（min = max，固定） |
| 视图独立窗 | 900×700（min 320×400） |
| 左侧栏 | 默认 **248px**，最小 **208px**，可折叠（collapsedSize 0，`preserve-pixel-size`） |
| 会话内容 | 限宽 `max-w-[768px]`（新任务）/ `820px`（page）/ `924px`（非空会话）——长行可读性约束 |
| 右栏 B2 | **280px**；Issue 抽屉 **620px** |
| 标题栏 | 40px；窗口控制区预留 72px；macOS 左预留 88、Linux 右预留 104 |
| Quick Note | **400×720**（min 320×600 / max 480×800），距屏 32px 贴边，头部 40px 自绘拖拽区 |

### 8.3 Surface 清单（12 项）

| # | Surface | 形态 | 尺寸/关键规范 |
|---|---|---|---|
| 1 | Workbench 主窗口 | 主窗口（frameless） | 1320×800 / min 720×540 |
| 2 | 登录 | 独立窗口 | 690×446 固定 |
| 3 | Dynamic Island | OS 级置顶悬浮条（透明无边框） | `island` / `notch` 两模式（notch 中留 192px 刘海位）；badge 高 22px；选项最小高 48px；回答框高 32px |
| 4 | Desktop Pet | OS 级桌面精灵窗（透明、可拖、不可聚焦） | 精灵基准 **128px** × 尺寸百分比 + 48px 工具栏 = 128×176；默认贴右下 `(屏宽-120, 屏高-48)`；语音时 `scale(.72)` 让位 |
| 5 | Live Voice Overlay | 全屏透明浮层 | 覆盖整屏；aura orb 三套视觉主题 |
| 6 | Quick Note | 竖版便签窗 | 400×720（min 320×600 / max 480×800） |
| 7 | Companion Activity | 屏幕底部气泡栈 | 折叠 **68px** / 展开 **188px**，`gap:8px`，内嵌回复输入 |
| 8 | First-launch Onboarding | 覆盖主窗的引导浮层 | 信封/身份卡：卡 240×280、场景卡 430×180；跳过按钮 `top:60px` |
| 9 | Onboarding Role Reveal Demo | 动效演示 Surface | 同信封/卡片动效 |
| 10 | Hosted Presentation Menu | 透明菜单锚点 | 2×2px 锚点定位 |
| 11 | Data Directory Progress | 独立 HTML 迁移进度窗 | 独立 CSP（`connect-src 'none'`） |
| 12 | Artifact Preview | 独立预览窗（推断） | 尺寸未确认；头部 40px |

### 8.4 导航模型

**左侧栏 8 项固定顺序 + 可自定义**：新的任务 / 任务 / 需要我 / 项目 / 讨论 / 搜索 / 自动化 / 扩展（+ 设置）。入口按 `primary / secondary / more` 三档可拖拽重排，部分项锁定位置；可见性由功能开关控制（`requiresIssues`、`requiresDiscussions`、`requiresExperimentalAgentChat` 等）【实测】。

**三种壳层**：`framed`（带 A/B 布局）、`standalone`（设置类，无左栏）、`chatSession`（会话，framed 的子类）。

**层级深度**：
- L1 左侧栏入口 → L2 列表页 → L3 详情（会话/项目/Issue/讨论）→ L4 右栏 Tab（文件/浏览器/Review/终端）+ 抽屉；
- **导航靠"后退/前进 + 路由持久化"，没有传统多级面包屑**（会话头部只有地址栏 + 工作区 Tab）；
- 命令模型 `workbench.action.*`（newWindow / toggleLeftSidebar / openTerminal / openQuickNote 等），有对应全局快捷键。

### 8.5 关键流程界面

| 流程 | 设计要点 |
|---|---|
| 首次启动 Onboarding | 全链路：浏览器 OAuth 登录 → 「演示场景」（GitHub/Figma/Plan/生成表格 5 张卡 + 音效）→ 角色选择 → 数据导入（任务/定时任务/Skill/MCP/记忆）→ **限定身份卡**（WELCOME QODER / BOARDING PASS / JOINED TIME）；可跳过、可重放 |
| 登录 | 独立 690×446 窗口；状态文案完整（正在恢复 / 等待浏览器确认 / 复制登录链接）；账号入口在标题栏最右 |
| 数据目录迁移 | 确认弹窗（560px，说明"原位置保留恢复副本"）→ **独立进度窗**（分阶段：准备/停止任务/复制校验/完成）→ 自动重启；异常态覆盖"上次迁移未完成" |
| 更新 | 主进程有完整增量更新链路（NSIS 缓存 + fast-update 归档）；标题栏有更新按钮；更新页布局未确认 |
| 空状态/错误态 | 系统性插画化：`EmptyState` 组件 + 876 个 webp（空态、失败、首次使用贴纸）；错误文案最高频是「重试」（111 次） |

### 8.6 设计意图观察

1. **这是"Agent 工作台"而非 IDE**：左侧栏没有文件树，第一层是任务/项目/讨论（人的工作对象），文件树被降级为"任务内的工作目录 + 右栏 Tab"。
2. **把 Agent 状态提升到 OS 层**：Dynamic Island 用徽章色编码状态（橙=待批/等待、红=失败、蓝=完成、青=提问、绿=工作中），并可直接在岛内回答/批准——人在别处也能处理 Agent 请求。
3. **"岛—桌面—主窗"三层同一人格**：Desktop Pet 的鸭子会缩小成岛内 20px 头像复用，语音时让位；Companion Activity 把通知升级成可回复的对话。
4. **Quick Note 是打断成本最低的入口**：竖版便签、置顶、贴光标，服务"随手记"而非长文。
5. **布局规范稳定在「208/248 + 内容限宽 + 280 右栏」**，只允许左右栏拖拽，内容区用限宽保证可读性。
6. **安全边界按 Surface 收敛**：独立 Surface 用更严 CSP（迁移窗甚至禁网），按最小权限单独构建。

## 9. 动效规范

### 9.1 时间与曲线

| 参数 | 值 | 使用量 | 用途 |
|---|---|---|---|
| **主缓动** | `cubic-bezier(.2,.8,.2,1)` | 111 次 | 入场、展开、hover、Tab 切换 |
| 次缓动 | `cubic-bezier(.16,1,.3,1)` | 28 次 | 长距离位移、揭示式动画 |
| 第三缓动 | `cubic-bezier(.22,1,.36,1)` | 15 次 | 面板/抽屉进出 |
| 循环 | `linear` / `ease-in-out` | 22 / 24 次 | 呼吸、旋转、扫光、流光 |
| 弹性 | `cubic-bezier(.34,1.4,.64,1)` | 2–4 次 | 开关、贴纸等"有弹性"的强调 |

**时长分布**（JS tween + CSS）：`90ms`（即时反馈）→ `140–240ms`（标准过渡，最高频为 150/220/200ms）→ `280–420ms`（强调过渡）→ `1.05–1.8s`（氛围循环）→ `2.4–6s`（呼吸/流动）。

**弹簧参数**（framer-motion，共 8 组）：`stiffness 360/damping 24/mass .45`、`420/26/.75`、`260/32/.55`、`180/28/.5`、`170/30/.6`、`105/28/.9`、`100/10/1`、`500/25`。整体是"**中高刚度 + 中低阻尼**"的手感，短促、有回弹但不晃【实测】。

### 9.2 关键动效清单

| 动效 | 规格 | 证据 |
|---|---|---|
| 启动屏 Logo | 72px mask logo；呼吸 `2.15s linear`（opacity 1→0.86）；扫光 `2.15s cubic-bezier(.28,0,.62,1)`，`translateY(-120%→120%) rotate(-24deg) scale(1.18)`；底部辉光 `blur(24px)` + `mask-composite` | `index.html` |
| 主题切换 | View Transitions 淡入淡出 `160ms ease-out`；reduced-motion 直接跳变 | `--q26f0e9=160ms` |
| AI 思考 aura | 光晕/胶囊/经典三套视觉（`data-visual-theme=breathing/capsule/classic`），核心呼吸 + 光斑漂移 + 上下波动，周期 1.05–3.6s | `LiveVoiceOverlay.css`（30 个 `aura-buddy-*` keyframes） |
| 语音 orb | 120px 光晕 `blur(8px)`、108px 核心、28px 旋转 loading、鸭子 voice frame/glass | 同上 |
| Dynamic Island | 状态胶囊切换 + 旋转 loading（`dynamicIslandSpin`），宽度弹性过渡 | `DynamicIslandPanel.css` |
| AI 流式输出 | Markdown 块进入 `opacity .85→1`；文本 shimmer `background-position` 扫过 | `qoder-markdown-stream-block-enter` / `qoder-text-shimmer` |
| 消息头像生成中 | 旋转 0→155°→360°，分段 `cubic-bezier(.2,.8,.2,1)` + `(.16,1,.3,1)` | `chat-assistant-avatar-generating` |
| Composer 占位提示 | `translateY(100%)→0` + 淡入 | `chat-composer-placeholder-*` |
| Switch 吸引 | 宽度三段式回弹（`qoder-switch-attract-width-on`），用于"提示用户可点击" | `index.css` |
| 滚动边缘渐隐 | `mask-image` 线性渐变，默认 `min(12%, 40px)`，方向可单边控制，滚动时用注册变量做 0→1 过渡 | `.scroll-fade*` |
| 侧栏滑动高亮 | 共享背景元素在各菜单项间滑动（`data-sidebar-motion-background`） | `styles.css` |
| 贴纸/引导 | `sd-fadeIn` / `sd-slideUp` / `sd-blurIn`（4px 位移 + 4px 模糊） | `index.css` |

### 9.3 动效降级策略

- `prefers-reduced-motion: reduce` 在产物中出现 **30 次**，覆盖启动屏、抽屉、滚动条、AI 动效、贴纸等【实测】。
- `data-visual-effects=off` 把所有模糊/渐变/阴影变量置为 `none/0px`（性能兜底）【实测】。
- `data-animation-paused` 可在运行期暂停动画（如后台/失焦）【实测】。
- `data-pointer-focus` 用于区分"鼠标焦点"与"键盘焦点"，避免鼠标点击时出现 focus ring【实测】。

---

## 10. 交互状态与可访问性

### 10.1 状态契约（data-* 属性）

产物里有一套清晰的组件状态协议【实测】：

| 属性 | 使用量 | 含义 |
|---|---|---|
| `data-theme` | 162 | 主题（10 套） |
| `data-state` | 56 | 开合/选中状态（`open/closed/active`） |
| `data-variant` | 45 | 组件变体（primary/secondary/ghost/danger…） |
| `data-slot` | 22 | 组件内部插槽（Radix 风格） |
| `data-pointer-focus` | 22 | 鼠标焦点 vs 键盘焦点 |
| `data-part-type` | 22 | 消息分片类型（text/tool…） |
| `data-layout-region` | 16 | 布局区域划分（a/b） |
| `data-disabled` | 14 | 禁用 |
| `data-platform` | 14 | 平台（win32/darwin） |
| `data-surface` | 13 | 独立 Surface 标识 |
| `data-orientation` | 10 | 水平/垂直 |
| `data-size` | 4 | 尺寸档位 |

### 10.2 焦点与滚动

- **焦点环**：**设计系统组件的统一做法是"边框/底色变色"，不画 ring**（Input `focus:border-border`、Button `focus-visible:bg-primary-active`、IconButton `focus-visible:bg-fill-tertiary`，并在 Input/Textarea 明确写 `focus:ring-0`）；工具类层存在 `focus-visible:ring-2` + `ring-primary` 的能力，但组件未采用；少量应用层元素用 `outline 1–2px + outline-offset:2px`。整体仍**没有全局 `:focus-visible` 基线**——规范上的缺口【实测】。
- **滚动条**：`::-webkit-scrollbar { width/height: 6px }`，轨道透明，滑块透明圆角 3px，hover/focus 时显示 `fill` 色，过渡 `.16s`；reduced-motion 时取消过渡【实测】。
- **选区**：选中文本用主色的 18% 透明叠加（`color-mix(in srgb, primary 18%, transparent)`）【实测】。

### 10.3 可访问性评估

**做得好的**：reduced-motion 覆盖广；支持字号三档与 UI 缩放；用 `data-pointer-focus` 区分输入方式；`role`/`aria-*` 在 bundle 中大量出现；强制色彩对比在部分组件上有保证。

**短板**：
1. 四级文本（`text-quaternary`）在 8/10 主题下低于 AA；
2. `mint-light`、`light-parchment` 的主按钮文字对比度不足；
3. `warning` 作为文字色在浅色主题全部不达标（应只用于图标/背景）；
4. 焦点环没有全局基线，组件间可能不一致；
5. 没有 `forced-colors` / `prefers-contrast` 适配（产物中 0 处）。

---

## 11. 主题与平台适配规范

| 机制 | 开关 | 规范值 |
|---|---|---|
| 主题 | `html[data-theme]` / `:root[data-theme]` | 10 套：light/dark/forest/bee/mint/parchment × 明暗 |
| 主题切换动画 | `data-qoder-theme-transition="fade"` | 160ms fade（View Transitions），reduced-motion 跳过 |
| 平台 | `data-platform=win32\|darwin` | **Windows：关闭半透明渐变、rgba 毛玻璃、部分 blur 置 0，改用实色背景**；macOS：`linear-gradient(180deg, bg-base, bg-elevated)` + `blur(40px) saturate(150%)` 的 vibrancy |
| 视觉效果开关 | `data-visual-effects=off` | 所有 blur/gradient/shadow 变量归零 |
| 字号 | `data-font-size=small\|medium\|large` | 13/14/16px（聊天正文） |
| UI 缩放 | `data-ui-scale=large` | `zoom: 1.1`，仅作用于标记区域 |
| 终端主题 | `data-terminal-theme=light\|dark` | 独立于应用主题，21 套变量 |
| 独立 Surface 主题 | `data-surface` | Surface 内不继承窗口背景，单独控制 |

**Windows 适配的完整规则**【实测】：
```css
:root:not([data-platform=win32]) {          /* macOS */
  --window-bg: linear-gradient(180deg, bg-base 0%, bg-elevated 100%);
  --window-blur: blur(40px) saturate(150%);
}
:root[data-platform=win32] {
  --window-bg: none;                         /* 实色 */
  --window-blur: 0;
}
```
> 设计含义：**Windows 上放弃"通透玻璃"美学，换取渲染正确性与性能**；这是跨平台设计规范里最容易被忽略、但必须写进规范的一条。

---

## 12. 品牌视觉语言

### 12.1 Logo 规范（启动屏三层结构）

启动屏 logo 不是一张图，而是 **mask + 三层叠加 + 两条同步动画** 的合成件【实测】：

| 图层 | 作用 | 关键属性 |
|---|---|---|
| 容器 | 尺寸与遮罩源 | `72×72px`；mask = `qoder-loading-line.svg`（5 path / 3 渐变）；`opacity: 0.6` |
| ① 本体 | 实心线稿 | `text-quaternary` **72% 透明**；`blur(0.18px)` 抗锯齿级微糊；呼吸动画 |
| ② 底部辉光 | 向下扩散光晕 | `blur(24px)`（= 画布 1/3）、`opacity: 0.58`；双层 mask 交集（logo × 向下渐变） |
| ③ 扫光层 | 自上而下高光 | 光带 `blur(10px)`；核心 `text-tertiary` **54%**、中段 38%、边缘 18%；`translateY(-120%)→120% rotate(-24deg) scale(1.18)` |

**动画节奏**（两条动画同周期 2.15s）：
- 呼吸 `linear`：`0/100%` opacity 1 → `62%` 0.86（后 38% 缓慢回弹）；
- 扫光 `cubic-bezier(0.28,0,0.62,1)`：前 **72%** 走完全程，后 28% **静止留一拍**（刻意避免循环感）。

**light / dark 差异**：只切换混合模式与 token —— light 用 `mix-blend-mode: multiply`（压暗叠色），dark 用 `screen`（提亮叠色），保证两种背景下光感方向一致。

**降级**：`prefers-reduced-motion` 下关闭两条动画并**直接 `display:none` 移除扫光层**，保留静态线稿 + 辉光，品牌识别不丢。

**启动屏退出**：`data-hidden` 后 `opacity 0`，`120ms ease-out` 淡出；容器 `role="status"`、logo `aria-hidden`、整屏 `-webkit-app-region: drag`（启动期可拖动窗口）。

**同语言的 React loader**：应用内 loading 是同一 logo 语言的参数化版本——尺寸/时长按比例派生（辉光 `blur(0.34×size)`、扫光 `blur(0.14×size)`、周期 `2.15×基准`），并提供 8 种变体（qoder-logo / ascii-line / ascii-bounce / percent / scramble / music / bird / fish）。

### 12.2 应用图标体系

| 资产 | 尺寸 | 规范 |
|---|---|---|
| `qoder-light/dark.png` | renderer 192²，OS 1024² | **黑白单色**（`#0F0D0C` / `#FFF`），无彩色 |
| `qoduck-light/dark.png` | 同上 | 黄鸭：`#FFD966`（67.8%）、橙喙 `#F87926`（16%） |
| `-windows` 版 | 1024² | **满版方形**（不透明像素 990,607），mac 版保留留白（592,629）——Windows 图标需铺满格子 |
| `tray.ico` / `app-icon.ico` | 多尺寸 | 单色，适配系统托盘深浅 |

### 12.3 字体角色分工

| 字体 | 角色 | 证据 |
|---|---|---|
| 系统字体栈 | 全局 UI | `-apple-system, BlinkMacSystemFont, "Segoe UI"` |
| **Inter** (400/500/600) | 需要跨平台一致的 UI 局部 | 60 个 woff 子集；用户卡姓名 |
| **Instrument Sans** (400/500) | **品牌字**：Dynamic Island 字标、Onboarding 品牌贴纸、用户卡邮箱 | `.dynamicIslandQoderWord` |
| **Crimson Pro** (400/600) | 衬线阅读模式（仅 @font-face，未检出直接引用） | 6 个子集 |
| **qoder-seti** | 文件树图标字体 | `qoder-seti-*.woff` |
| **KaTeX** | 数学公式 | 21 个字体文件 |

实测最常用字号配对是 **12 / 13 / 11px + 18px 行高**，与 token 层 12/16 的规范略有漂移。

### 12.4 插画与吉祥物系统

- **Qoduck（鸭子吉祥物）**：主色 `#FEDA6E` / `#FFD966`，橙喙 `#F87825`；`Qoduck01–04` 用于邀请场景；`duck*` 系列（duckReading/duckPainter/duckTerminal/duckSupport/duckMegaphone）作为用户头像/场景插画。
- **语音序列帧占大头**：876 个 webp 中 **743 个是语音 orb 序列帧**（idle / listening / normal / speaking / thinking），说明语音交互是产品的核心视觉资产。
- **first-use 贴纸 12 类**：首次使用引导（创建 Agent、桌面宠物、Computer Use、数据导入、讨论、分叉、目标等）各配一张贴纸，形成"**每进入一个新能力，就有一只鸭子出现**"的陪伴式引导语言。
- 动物 SVG（jest/kubernetes/github 等）用作资料卡贴纸；另有 6 帧灰调未引用资源（未确认用途）。

### 12.5 品牌配色（真实取样）

| 项 | 值 | 来源 |
|---|---|---|
| UI 主色（light） | `#4B6F5A` | `primary` token |
| UI 主色（dark） | `#5CB870` | `primary` token |
| **产品 Logo 绿** | `#2ADB5C` | `qoderIdeLogo.svg` / `qoderCnIdeLogo.svg` / `qoderworkLogo*.svg` |
| **内联字标绿** | `#255A41` | 金属/内联字标 SVG |
| Qoduck 黄 / 橙喙 | `#FEDA6E`、`#FFD966` / `#F87825` | 鸭子图标与插画 |
| 主题主色 | mint `#4FA98F`/`#62C9A8`、parchment `#C96442`/`#E08A68`、bee `#0D0D0D`/`#E0C65C` | 主题矩阵 |

> **品牌一致性风险**：存在**三套绿未收敛**——UI 语义绿（`#4B6F5A`）、产品 Logo 亮绿（`#2ADB5C`）、内联字标深绿（`#255A41`）。三者用途不同（界面/品牌标/字标），但缺少明文映射规则，复刻时容易混用。

### 12.6 材质与纹理

| 材质 | 规范 | 使用场景 |
|---|---|---|
| `glass-light/dark` | 1024²，明暗互斥 | 语音 orb 光环（104/120px 两个尺寸） |
| 背景模糊 | `blur(24px)`，**仅浅色主题启用** | 玻璃拟态表面 |
| 纸纹 noise | 100²，仅 `forest-light` / `parchment-dark` 主题 | 屏幕背景噪点 |
| 金属字标 | `qoder-metal.svg`（68×24，5 组渐变） | 用户卡的"金属版"字标 |
| Holographic 用户卡 | `data-holographic-variant`（24 处）+ 13 个专用变量 | 用户卡的激光全息质感 |

### 12.7 品牌气质判断

综合证据（低存在感的灰色启动 logo、陪伴感鸭子、first-use 贴纸、语音 orb 序列帧、Desk Pet 界面），Qoder CN 的品牌策略是：**"专业工具的外壳 + 有生命感的 AI 伙伴内核"**——界面本身克制（系统字体、12px、灰阶），但把"有情绪、有存在感"的表达全部留给 AI 状态与引导时刻（鸭子、光晕、贴纸、灵动岛）。

## 13. 规范落地建议（如果要复刻/借鉴）

### 13.1 值得直接照搬的 6 条

1. **语义 token 三层架构**：raw → semantic → utility，业务代码只用中层。哈希变量名 + 语义类名的组合兼顾了防抄与可读。
2. **4 级表面 + 4 级文本 + 4 级边框/填充**的层级模型，足够覆盖 95% 的界面，不需要更多色。
3. **typeset 排版模式**：把"内容排版"从页面里抽出来，按场景（chat/compact/docs/reading）切换密度，是 AI 产品最该学的一条。
4. **一条主缓动 + 少量时长档**：`cubic-bezier(.2,.8,.2,1)` + 140–240ms，统一体感，开发成本极低。
5. **平台/效果开关**：`data-visual-effects`、`data-platform`、`data-font-size`、`data-ui-scale` 四件套，让设计规范具备"可降级"能力。
6. **AI 状态可视化**：把"思考中/在听/在忙/完成"设计成独立的 aura/orb/胶囊视觉，而不是转圈 loading。

### 13.2 不要照搬的 4 点

1. **12px 基准字号**：这是"专业工具"的取舍，普通产品用会显得字小；建议 13–14px 基准。
2. **对比度处理方式**：`text-quaternary`、浅色 `warning`、`mint-light` 主色按钮都不达 AA，复刻时必须重新校色。
3. **主题命名不规范**：`light-parchment` 与 `parchment-dark` 不对称，应在设计 token 文件里先统一（如 `parchment-light`）。
4. **焦点环分散**：没有全局基线，复刻时应先定义 `:focus-visible` 的统一 ring 规范，再让组件继承。

### 13.3 一页纸质检清单

- [ ] 所有颜色是否来自语义 token（无硬编码 hex）？
- [ ] 背景是否只在 base/container/elevated/layout 四层中选择？
- [ ] 文字是否使用 text/secondary/tertiary/quaternary 四档，且四级只用于非关键信息？
- [ ] 标题字号是否从 typeset 模式派生（base + 6/4/2/0）？
- [ ] 动效是否收敛到 1 条主缓动 + 140–240ms 主时长？
- [ ] 是否实现 `prefers-reduced-motion` 与"关闭视觉效果"开关？
- [ ] 是否有全局统一的 `:focus-visible` 规范？
- [ ] 是否对 10 套主题逐一跑过对比度检查？
- [ ] Windows 是否关闭了半透明/毛玻璃并改实色？
- [ ] 是否支持字号三档与 UI 缩放？

---

## 14. 附录

### 14.1 交付物清单

| 文件 | 说明 |
|---|---|
| `Qoder-CN-设计规范逆向分析.md` | 本报告（14 章） |
| `design-spec.html` | 可视化规范页（单文件自包含，支持 light/dark 切换） |
| `tokens/design-tokens.json` | 机器可读 token（68 色 + 尺度 + 动效 + 主题矩阵） |
| `tokens/semantic-tokens-raw.json` | 语义 token 原始解析（哈希变量名 / 工具类名 / CSS 属性） |
| `tokens/theme-matrix.json` | 10 套主题关键 token 矩阵 |
| `appendix/components.md` | 组件库规范原始分析（806 行，27 个组件族，逐条证据） |
| `appendix/surfaces.md` | 界面与信息架构原始分析（12 个 Surface、窗口尺寸、导航、流程） |
| `appendix/brand.md` | 品牌视觉原始分析（Logo 逐行取证、图标取样、插画、材质） |
| `assets/` | 提取的 logo、应用图标、吉祥物、材质与字体子集 |
| `preview-light.png` / `preview-dark.png` / `preview-full.png` | 可视化页截图 |

### 14.2 证据文件索引

| 证据 | 路径（解包后，相对 `app.asar`） |
|---|---|
| 启动屏 / CSP / 窗口壳 | `out/renderer/index.html` |
| 全局样式（含 @layer theme） | `out/renderer/assets/styles-eCOZTk0p.css`（396 KB，4,259 规则） |
| 设计系统组件样式 | `out/renderer/assets/index-BFGCOCH4.css`（80 KB，570 规则） |
| **设计系统组件定义（未深度混淆）** | `out/renderer/assets/S__Wc8-4.js`（3.2 MB，153 个 `displayName`、`cva()` 变体表） |
| 布局骨架与窗口控制 | `out/renderer/assets/S__Wc8-4.js`（`LayoutChrome`、`LAYOUT_*` 常量） |
| 渲染入口 / Surface 路由 | `out/renderer/assets/DuYyTcRQ.js`（`?surface=` → 动态 import 映射） |
| 主 UI 逻辑与导航/设置 | `out/renderer/assets/gtdG4YpP.js`（15.8 MB） |
| i18n 文案 | `out/renderer/assets/BkeoGa4m.js`（中/繁/英/韩四套） |
| 语音/aura 动效 | `out/renderer/assets/LiveVoiceOverlay-*.css`（30 个 keyframe） |
| 12 个 Surface 样式 | `DynamicIslandPanel-*`、`DesktopPetSurface-*`、`CompanionActivitySurface-*`、`LiveVoiceOverlay-*`、`QuickNoteWindow-*`、`FirstLaunchOnboardingSurface-*`、`OnboardingOverlayDemo-*`、`dataDirectoryProgress-*`、`hostedPresentationMenu-*`、`DynamicIslandSurface-*`（均为 `.css`） |
| 主进程窗口常量 | `out/main/electronMain.js`（尺寸 @23193、标题栏策略 @18819192、overlay 窗口 @4118106 等） |
| Surface 侧 API | `out/preload/index.cjs` |
| 产品清单 / 构建信息 | `resources/product.json`、`build-manifest.json` |
| Launcher 状态 | `%LOCALAPPDATA%\Qoder CN\Qoder CN Launcher\state.ini` |

### 14.3 待确认项

- Crimson Pro 的实际使用场景（CSS 中只有 @font-face，无直接引用，可能在 JS 内联样式或未启用功能中）。
- Dynamic Island 的 180×200 / 300×252 两档窗口尺寸归属（与 Desktop Pet 常量相邻但未拿到 Surface↔class 直接绑定，属推断）。
- 更新弹窗/更新页的具体布局与尺寸（渲染层更新文案未在本次抽取范围内定位）。
- Artifact Preview 独立窗的窗口尺寸。
- Button/Input 的 loading / 成功态（未发现对应 prop）。
- 通用 Dialog 的尺寸档（仅有 `max-h-[90vh]` + `w-[calc(100%-2rem)]`）。
- 数据表格的交互规范（产物中 Table 仅用于 Markdown 展示）。
- 组件层暗色主题的完整状态矩阵（本文组件色值以浅色主题为主）。
- 主题切换的完整效果依赖 Chromium View Transitions，旧版本 Electron 行为可能不同。
- Logo 最小使用尺寸 / 安全边距 / 栅格比例（无设计文档或注释证据）。
- `--q9592ea`（loader 基准时长）默认值、灰调鸭子 6 帧用途。

---

> 报告生成时间：2026-11-11；分析版本：Qoder CN 0.5.7（build 87859884，commit 73fe8d73）
