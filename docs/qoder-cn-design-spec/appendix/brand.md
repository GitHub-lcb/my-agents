# Qoder CN 0.5.7 · 品牌视觉语言（Brand Visual Language）逆向分析

> 分析对象：Qoder CN 0.5.7（Electron + React），安装目录 `E:\develop-lcb\apps\Qoder CN\.qoder-versions\0.5.7\`
> 取证范围：`resources\app.asar`（6,448 文件；`out/renderer/` 1,871 文件：876 webp / 42 svg / 59 woff2 / 20 ttf / 12 css / 572 js）、`resources\application-icons\`、`resources\tray\tray.ico`、`resources\app-icon.ico`。
> 方法：CSS/JS 静态解析（正则 + 括号配对提取变量块）、Pillow 12 对 PNG/ICO/WebP 做 alpha 感知主色统计（量化 6–8 色，占比基于不透明像素）、asar 按需抽取代表性素材。
> 标注约定：**（证据）** = 有文件/行号可指；**（推断）** = 由证据推导但无直接声明；**未确认** = 未找到证据，不做臆测。

---

## 1. Logo 规范

### 1.1 启动屏 Logo 的 DOM 结构（三图层叠加）

证据：`out/renderer/index.html` L12–L169（内联 `<style>`）、L194–L200（DOM）。

| 图层 | class | 作用 | 关键属性 |
|---|---|---|---|
| 容器 | `.qoder-boot-logo` | 定义尺寸与遮罩源 | `--qoder-boot-logo-size: 72px`；`--qoder-boot-logo-mask: url("./assets/qoder-loading-line-Bq9ip4M2.svg")`；`color: var(--qoder-boot-logo-base)`；`opacity: 0.6` |
| ① 基础层 | `__base` | 实心线稿本体 | `background: currentColor` + mask；`filter: blur(0.18px)`；`animation: qoder-boot-logo-breath 2.15s linear infinite` |
| ② 底部辉光 | `__bottom-blur` | 向下扩散的柔和光晕 | `filter: blur(24px)`；`opacity: 0.58`；双层 mask 交集：Logo 线稿 × `linear-gradient(to bottom, transparent 70%, black 100%)`（`mask-composite: intersect` / `-webkit-mask-composite: source-in`） |
| ③ 扫光层 | `__sweep` | 自上而下的高光扫过 | 容器 `overflow: hidden`、`mix-blend-mode: multiply`（暗色 `screen`）；子元素 `span` 为径向渐变光带，`filter: blur(10px)`，`animation: qoder-boot-logo-sweep 2.15s cubic-bezier(0.28,0,0.62,1) infinite` |

启动屏容器：`#qoder-boot-splash` 固定 `inset: 0`、`z-index: 2147483647`、`display: grid; place-items: center`、`-webkit-app-region: drag`（启动期整屏可拖动窗口）；`background: var(--qoder-boot-bg)`。

### 1.2 尺寸与颜色混合比例（均为 CSS 实值）

| 项目 | 规格 | 证据 |
|---|---|---|
| Logo 画布尺寸 | **72 × 72 px**（mask `contain`、`center`） | `--qoder-boot-logo-size: 72px` |
| 整体不透明度 | **0.6** | `.qoder-boot-logo{opacity:.6}` |
| 本体颜色 | `color-mix(in srgb, var(--q175223) 72%, transparent)` = **text-quaternary 72%** | L15 |
| 扫光核心 | `color-mix(in srgb, var(--q2704ac) 54%, transparent)` = **text-tertiary 54%** | L16 |
| 扫光中段 | `text-quaternary 38%` | L17 |
| 扫光边缘 | `text-quaternary 18%` | L18 |
| 辉光强度 | `opacity: 0.58` | L95 |
| 线条锐化 | 本体/扫光 `blur(0.18px)`（≈尺寸的 0.25%，抗锯齿级微糊） | L89 / L110 |
| 辉光模糊 | `blur(24px)` = 画布的 **1/3** | L94 |
| 扫光模糊 | `blur(10px)` ≈ 画布的 **13.9%** | L141 |
| 扫光渐变 | `radial-gradient(ellipse 122% 96% at 50% 50%, transparent 0%, edge 18%, mid 38%, core 52%, mid 66%, transparent 86%)` | L132–L140 |
| 扫光初始位形 | `translateY(-120%) rotate(-24deg) scale(1.18)` | L142 |

> 颜色 token 实际取值（见 §5）：light `text-quaternary #AAA9A8` / `text-tertiary #838280`；dark `#585853` / `#7B7B74`。**Logo 在启动屏用中性灰阶呈现，不使用品牌绿**——这是刻意的"低存在感启动"，与 §7 的品牌气质判断一致。

### 1.3 动画时间线（两条动画同周期 2.15s）

| 动画 | 周期 | 缓动 | 关键帧 | 视觉结果 |
|---|---|---|---|---|
| `qoder-boot-logo-breath` | 2.15s | `linear` | `0%,100% → opacity 1`；`62% → opacity 0.86` | 呼吸：亮度在 62% 处轻微压暗，回弹缓慢（占周期后 38%） |
| `qoder-boot-logo-sweep` | 2.15s | `cubic-bezier(0.28, 0, 0.62, 1)` | `0% → translateY(-120%)`；`72% → translateY(120%)`；`100% → 保持 +120%` | 扫光在前 72% 走完全程，后 28% 静止（留出"停一拍"的节奏） |

两条动画**同周期同步启动**（均 2.15s infinite），形成"呼吸中的一道扫光"复合节奏；扫光每轮有 28% 的停顿，避免循环感过强。
（推断）2.15 是倍率而非绝对秒数：应用内 React loader 使用 `calc(var(--q9592ea) * 2.15)`，故启动屏等效基准节奏 `--q9592ea ≈ 1s`。

### 1.4 light / dark 差异

| 维度 | light | dark | 证据 |
|---|---|---|---|
| 扫光混合模式 | `mix-blend-mode: multiply` | `mix-blend-mode: screen` | L119 / L122–L126（`@media (prefers-color-scheme: dark)`） |
| 底色 | `--qb0b99e`（bg-layout，light `#FFF`） | 同 token，dark `#111110` | L14 |
| 前景色 | text-quaternary `#AAA9A8` | `#585853` | 主题 token |
| `color-scheme` | 默认 | 声明 `dark`（原生控件/滚动条跟随） | L21–L25 |

> 同一套几何结构在明暗下只切换 **混合模式 + token 值**：亮色下扫光做"压暗叠色"（multiply），暗色下做"提亮叠色"（screen），保证两种背景下光感方向一致而不脏。

### 1.5 prefers-reduced-motion 降级策略

证据：`index.html` L159–L168。

```css
@media (prefers-reduced-motion: reduce) {
  .qoder-boot-logo__base,
  .qoder-boot-logo__sweep span { animation: none; }
  .qoder-boot-logo__sweep { display: none; }
}
```

- 关闭呼吸与扫光两条动画；
- **直接移除整个扫光层容器**（`display:none`），而非保留空转；
- 保留本体线稿 + 底部辉光（静态可辨识的 Logo），保证降级后品牌识别不丢失。

### 1.6 启动屏退出

`#qoder-boot-splash[data-hidden="true"]{ pointer-events:none; opacity:0; transition: opacity 120ms ease-out; }`（L47–L51）——120ms 淡出，与启动节奏一致地"快进快出"。
可访问性：容器 `role="status" aria-label="正在恢复登录状态"`，Logo 层 `aria-hidden="true"`（L194–L198）。

### 1.7 应用内 Loader：同一 Logo 语言的参数化版本

证据：`assets/S__Wc8-4.js` 中 `function LoaderStyles()` 注入 `.qoder-loader` 内联样式。

- 尺寸变量 `--q06a65a`（loader 尺寸）、节奏变量 `--q9592ea`（基准时长），全部按比例派生：
  - 底部辉光 `blur(calc(var(--q06a65a) * 0.34))`（≈ 72px × 0.333）
  - 扫光 `blur(calc(var(--q06a65a) * 0.14))`（≈ 72px × 0.139）
  - 呼吸/扫光周期 `calc(var(--q9592ea) * 2.15)`，扫光缓动同为 `cubic-bezier(0.28,0,0.62,1)`
- keyframes 命名带 `qoder-loader-` 前缀：`qoder-loader-spin`、`qoder-loader-qoder-logo-breath`、`qoder-loader-qoder-logo-sweep`（关键帧数值与启动屏**完全一致**：呼吸 62%→0.86；扫光 -120%→120% @72%）、`qoder-loader-dot`（`0/80/100% opacity .32 scale(.78)`，`40% opacity 1 translateY(-18%) scale(1)`）。
- 8 种 loader 变体（`data-loader-variant`）：`qoder-logo`、`ascii-line`、`ascii-bounce`、`percent`、`scramble`、`music`、`bird`、`fish`；非 Logo 变体按尺寸倍率加宽（`1.72×` ascii-line、`1.45×` ascii-bounce/percent/scramble、`1.2×` music/bird/fish）——即"品牌 Logo loader 打底，其余为等尺寸占位变体"。
- 暗色判定：`[data-theme$="-dark"]` 下扫光 `mix-blend-mode: screen`。
- `qoder-logo` 变体 `opacity: 0.6`，与启动屏一致；其本体额外叠一条 `linear-gradient(to bottom, black 70%, transparent 100%)` mask，使小尺寸下底部渐隐更自然。

### 1.8 Logo 资产清单（42 个 SVG 中与品牌标相关者）

| 文件 | viewBox | 大小 | 主填充色（SVG 内） | 结构 | 用途证据 |
|---|---|---|---|---|---|
| `qoder-loading-line-Bq9ip4M2.svg` | 72×72 | 268 KB | `#fff`（仅 mask 用，实际色由 `currentColor` 决定） | 5 path + 3 linearGradient + 1 mask | 启动屏 & 应用内 loader 的 mask 源（`index.html` L55；JS `qoderLoadingLineUrl`） |
| `qoderLogo-B1z0eOSP.svg` | 100×100 | 388 KB | `#0F0D0C` | 5 path + 1 mask | 主 Logo 图形；**渲染层 JS/CSS 中未检出直接引用**（可能用于外部/营销物料，未确认） |
| `qoderIdeLogo-CVF9SQtk.svg` | 242×242 | 17 KB | `#111113` + **`#2ADB5C`** | 5 path + 2 mask | IDE 产品标（JS 常量 `S4e`） |
| `qoderCnIdeLogo-D6M-8wQq.svg` | 206×206 | 17 KB | **`#2ADB5C`** | 2 path | 中国版 IDE 标（`rW2`） |
| `qoderworkLogo-bi1EWSMh.svg` / `qoderworkCnLogo-Q-LaC455.svg` / `qoderworklogo-DYLHYE-O.svg` | 1024×1024 | 9.5 KB 级 | **`#2ADB5C`** | 2–8 path | QoderWork 产品族标（`oW2` / `L4e`） |
| `qoderDoorLogo-DPEqsmiL.svg` | 21.32×21.32 | 39 KB | 渐变（1 linearGradient） | 1 path | 入口/门牌标（`sW2`） |
| `qoder-metal-DQnndy7r.svg` | 68×24 | 11 KB | 5 组渐变（金属质感字标） | 5 path | 用户卡"金属版"字标（JS 常量 `set`） |
| `qoder-mobile-status-bar-native-CXTtbAkX.svg` | 133×16 | 6.6 KB | `#141414` | 5 path | 移动端状态栏原生标 |
| 文字字标 | — | — | — | — | Dynamic Island 的 "Qoder" 字标为**文字实现**：`.dynamicIslandQoderWord{font-family:Instrument Sans,…}`（`DynamicIslandPanel-*.css`） |

**未确认**：Logo 最小使用尺寸、安全边距/清空区（clear space）、栅格比例与制图规范（无设计文档或注释证据）。

---

## 2. 应用图标体系

### 2.1 两套分辨率 + 双形态（qoder / qoduck）

| 位置 | 尺寸 | 形态 | 用途证据 |
|---|---|---|---|
| `out/renderer/application-icons/` | **192 × 192** | `qoder-light/dark.png`、`qoduck-light/dark.png` | 应用内展示：JS 以模板 `src="./application-icons/${e}-${t}.png"`（品牌-主题）加载，容器内 `size-[72%] object-contain`；容器底色 light `var(--q0110cf)=#F2F4F2` / dark `var(--qa81290)=#191B1A`，配 10px medium 标签（`gtdG4YpP.js`） |
| `resources/application-icons/` | **1024 × 1024** | 同上 + `-windows` 后缀共 8 个 | 操作系统/安装器图标 |

### 2.2 图标取样（Pillow，alpha 感知，占比 = 不透明像素内）

| 文件 | 尺寸 | 主色（占比） | 判读 |
|---|---|---|---|
| `qoder-light.png` | 1024×1024 | `#FFFFFF` 40.0%、`#0F0C0C` 18.4%、`#FAFAFA` 15.0%、`#EDEDED` 13.4% | 白底 + 近黑标，**纯黑白单色** |
| `qoder-dark.png` | 1024×1024 | `#0F0D0C` 47.0%、`#808080` 16.9%、`#100D0C` 13.1% | 近黑底 + 灰/白标 |
| `qoduck-light.png` | 1024×1024 | `#FFD966` 67.8%、`#F87926` 16.0%、`#FFFEFC` 11.5% | 黄鸭（白底） |
| `qoduck-dark.png` | 1024×1024 | `#FFD966` 67.6%、`#110E0C` 16.1%、`#F87825` 15.9% | 黄鸭（暗底） |
| （renderer 192px 版同源，数值一致：qoder 20,764 opaque px；qoduck 23,379 opaque px） | | | |

### 2.3 Windows 版与 macOS 版差异（量化）

| 文件对 | 不透明像素（1024²） | 差异 |
|---|---|---|
| `qoder-dark-windows.png` | 990,607 | Windows 版**满版方形**（背景铺满整格，无透明留白） |
| `qoder-dark.png` | 592,629 | macOS 版保留透明留白/圆角外形轮廓，透明面积约 43% |
| `qoduck-dark-windows.png` | 825,432 | 同上规律 |
| `qoduck-dark.png` | 666,516 | 同上规律 |

> 规律（证据）：`-windows` 变体不透明面积显著更大 → Windows 任务栏/开始菜单要求方形满版图标，macOS 采用带内边距的应用图标外形。形态差异不改变图形本身（同为黑白 Q / 黄鸭）。

### 2.4 托盘与安装器图标

| 资产 | 内含尺寸 | 取样主色 | 说明 |
|---|---|---|---|
| `resources/tray/tray.ico` | 16, 20, 24, 32, 40, 48, 64 | `#FFFFFF` 25–35% / `#2D2C2B`·`#32302F` 20–25% / 灰阶 `#B3B3B2`·`#EBEBEB` | **单色黑白**托盘图标，多尺寸适配菜单栏/Dock |
| `resources/app-icon.ico` | 16, 24, 32, 48, 64, 128, 256 | 同上（16px 与 tray 完全一致） | 安装器/文件关联图标，单色 |

### 2.5 favicon

`index.html` **未声明** `<link rel="icon">`，asar 内除 `application-icons` 外未发现其他 png/ico → **favicon 规范未确认**（Electron 窗口图标由主进程/OS 层指定，非渲染层 HTML）。

---

## 3. 字体系统

### 3.1 @font-face 实注册家族（排除 KaTeX 后的核心 4 族）

证据：`assets/styles-eCOZTk0p.css`、`DynamicIslandPanel-fKHMdK-y.css` 的 `@font-face` 块。

| 家族 | 字重 | 风格 | 子集 | woff2 数量 | 角色 |
|---|---|---|---|---|---|
| **Inter** | 400 / 500 / 600 | normal + 500 italic | latin, latin-ext, cyrillic, cyrillic-ext, greek, greek-ext, vietnamese | 28 | **UI 主字体**（界面正文/控件） |
| **Instrument Sans** | 400 / 500 | normal | latin, latin-ext | 4 | **品牌字体**（字标、用户卡、个人资料贴纸、营销数字） |
| **Crimson Pro** | 400 / 600 | normal | latin, latin-ext, vietnamese | 6 | **衬线阅读模式**（`data-font-style=serif` 时长文/对话正文） |
| **qoder-seti** | 400（单 woff，32.5 KB） | normal | — | 0（woff） | **文件图标字体**（Monaco 文件树图标 + 每语言配色） |
| Dynamic Island Inter | `100 900`（可变） | normal | latin, latin-ext | 2 | Dynamic Island 子窗口专用实例 |
| KaTeX_{AMS, Caligraphic, Fraktur, Main, Math, SansSerif, Script, Size1–4, Typewriter} | 400/700 | normal/italic | — | 12 族 | **数学公式**渲染 |

> `font-display: swap` 全局启用（证据：所有 @font-face 块）。Inter 仅到 **600**，无 700+ —— 界面强调上限为 semibold（与 `font-semibold` 语义一致，见 `gtdG4YpP.js`）。

### 3.2 Fallback 栈（CSS 变量实值）

| 变量 | 实值 | 使用场景 |
|---|---|---|
| `--qea5e5c` | `-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif` | 系统 UI 栈；**`html[data-font-style=serif]` 时整段替换为** `"Crimson Pro", Georgia, "Times New Roman", "Songti SC", STSong, "Noto Serif CJK SC", "Source Han Serif SC", SimSun, serif` |
| `--q316d97` | `"Instrument Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif` | 品牌字栈；在会话正文视口内覆写为 `var(--qea5e5c)` |
| `--qbb674b` | `ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace` | 等宽（代码） |
| `--font-sans` | `ui-sans-serif, system-ui, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji"` | Tailwind 默认栈（可视化 iframe 等） |
| 显式 Inter 栈 | `Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif` | 30 处 `font-family: Inter…` 声明 |
| JS 内联栈 | `"Instrument Sans", -apple-system, …` / `"Inter", -apple-system, …` | 导出图/海报/图表渲染（`gtdG4YpP.js` 的 `RJ2` / `_J2`） |
| 代码字体（两套并存） | `Fira Code, ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace`（JS 片段展示）；`IBM Plex Mono, ui-monospace, …`（CSS 3 处） | 代码块/差异视图；**未确认哪套为代码编辑器正式字体** |

### 3.3 字号与行高证据（实测量化）

按类名出现次数统计（CSS + JS 全量）：

| 字号 | 出现次数 | 定位 |
|---|---|---|
| **12px** | 346 | 正文/描述主档 |
| **13px** | 318 | 正文/会话内容主档 |
| **11px** | 257 | 辅助/元信息 |
| 10px | 75 | 标签、徽标 |
| 14px | 48 | 强调正文 |
| 20px | 31 | 区块标题 |
| 9 / 16 / 15 / 18 / 24 px | 10 / 9 / 7 / 3 / 3 | 极少数特例 |
| 40 / 44 px | 各 1–2 | 营销/分享卡大数字（Instrument Sans `fontSize:52` 亦见） |

| 行高 | 出现次数 | 配对关系 |
|---|---|---|
| **18px** | 199 | 12px 正文 → 18px（1.5×） |
| **22px** | 45 | 14px 正文 → 22px |
| 14px | 11 | 11px 辅助 → 14px |

其他实测：`body{font-size:11px!important}`（部分独立 surface）；可视化 iframe `body{font:13px/20px var(--font-sans,system-ui,sans-serif)}`；`h1:16px/24px/600`、`h2:14px/20px/600`、`h3:13px/20px/500`；Dynamic Island `font-size:12px; line-height:16px`；用户卡 email `font-size:7.826cqw; font-weight:500`（容器查询单位响应式排版）。

---

## 4. 插画与吉祥物系统

### 4.1 吉祥物 Qoduck 的视觉定义（实测色值）

| 部位 | 色值（多图交叉验证） | 占比区间 |
|---|---|---|
| 身体黄 | **`#FEDA6E` / `#FFD966` / `#FDDC65`** | 单图 55%–80%（Qoduck01 最高 78.1%） |
| 喙/脚橙 | **`#F87825` / `#F77124` / `#C67E47`**（暗底为 `#F77B27`） | 10%–17% |
| 描边/暗部 | **`#141210` / `#130F0D` / `#161412`** | 3%–20% |
| 高光 | `#FDE595` / `#FFE495` / `#FEF4D4` | 3%–12% |
| 应用图标黄 | `#FFD966`（qoduck-light/dark 图标 59–68%） | — |

> 交叉源：`Qoduck01-04.webp`（440×440）、`duck*.webp`（400×400）、`application-icons/qoduck-*.png`、`duckTail.svg`（`#FFDA6B`）、JS 内 `bg-[#FFDA6B]`（贪吃蛇游戏元素）。

### 4.2 命名规律与分类（876 webp → 701 个去哈希基名）

| 类别 | 命名规律 | 代表文件（尺寸） | 使用场景（证据） |
|---|---|---|---|
| **吉祥物拟人** | `QoduckNN` | Qoduck01–04（440×440） | **邀请卡片/邀请码插图（推断）**：`S__Wc8-4.js` 中 4 个 `Qoduck01~04` 常量紧随其后即 `createInvitation / copyInvitation / releaseInvitation` 邀请组件；具体渲染位置未逐处确认 |
| **鸭子头像** | `duck<Role>` | duckReading / duckMegaphone / duckSupport / duckTerminal / duckPainter（400×400） | **用户头像可选形象**：`profileAvatarImages:{duckReading:"阅读鸭",duckMegaphone:"喊话鸭",duckSupport:"客服鸭",duckTerminal:"终端鸭",duckPainter:"绘画鸭"}`（中/英双语） |
| **状态动画帧** | `<state>[-left/-right][-still]` | idle / jumping / waving / waiting / running / failed / review（256×277）+ `*-still` 静态帧 | 桌面宠物/陪伴态动画；`*-still` 为 reduced-motion 降级帧（`S__Wc8-4.js` 中 animated/still 成对声明） |
| **视线方向帧** | `look-<角度>` | look-000 / 022.5 / 045 … 337.5（16 向，256×277）+ still | 鸭子跟随鼠标/光标视线 |
| **语音序列帧** | `voice_<state>_<5 位序号>` | idle(75) / listening(120) / normal(105) / speaking(107) / speking(70，疑拼写变体) / thinking(114) = **591 个不同帧名**；对应 **743 个 webp 文件**（占 876 的 85%，同一帧存在多份不同哈希变体） | 语音球（LiveVoiceOverlay）逐帧动画；是素材量的绝对主体 |
| **首次使用引导贴纸** | `<Feature>FirstUse/First…Sticker` | automationFirstCreate、computerUseFirstUse、dataImportFirstSuccess、desktopPetFirstUse、discussionFirstStart、forkFirstUse、goalFirstUse、mobileMessageFirstReceive、sitesFirst、voiceFirstUse、workItemFirstCreate、snakeFirstPlay（均 400×400） | 功能首次触达的"成就/引导"贴纸；每个 sticker 在 JS 中各被引用 1 次（`gtdG4YpP.js`） |
| **徽章/纪念贴纸** | `activeDaysNSticker` / `qoder…Sticker` | activeDays7/30/100（400×400）、qoderAnniversary365、qoderPioneerForest（680×680） | 活跃天数、周年、先锋用户徽章 |
| **用户卡/分享** | `userCard*` / `stickerShare*` | userCardDuck/SilverDuck（140×140）、userCardRing（340×340）、userCardSignature、stickerShareHandFront/Back/Signature | 个人资料卡与分享海报（`S__Wc8-4.js` 用户卡渲染常量） |
| **动物形象** | `<animal>.svg` | duck / dog / gorilla / crocodile / bird（viewBox 1200–1320） | **个人资料卡贴纸装饰**：JS 中按 `{width: size/1140*100%, left, top}` 绝对定位（`Jb(1200,-30,94)` 等），属可旋转贴纸资产 |
| **首启动引导插画** | 纯序号 `01`–`10` | 01、02（两版：彩色 / 蓝）、03、04、05、08、10（440×440，最大 1.7 MB） | 首次启动 onboarding 人物场景板（SVG 内含 `Property 1=01..10` 分组与 `头发` 等图层名） |
| **空状态/情绪反馈** | `quickNoteEmptyState` / `failed(-still)` / `feedbackWatermark` / `thinking-dot-matrix` / `forest1024Still` | quickNoteEmptyState（1200×691）、thinking-dot-matrix（36×36）、feedbackWatermark（176×176） | 空状态、失败态、思考中、反馈水印 |
| **生态/第三方 logo** | 工具名 | vite / yarn / jest / github / kubernetes / openssh / antigravity / workbuddy | 集成与模型 provider 图标 |
| **运营物料** | 语义命名 | Login_poster_0810（672×896）、onboardingWallpaper（4608×2304）、project-Cover-1/3/4/5/6（80×80） | 登录海报、引导壁纸、项目封面渐变图（多色系） |

### 4.3 情绪表达策略（基于资产与用法）

- **情绪由姿态承载，不用色块**：idle（待机眨眼）、jumping（成功/兴奋）、waving（问候）、waiting（等待）、failed（失败）、review（审视）、running（执行中）——同一只黄鸭换姿态，保持单一形象记忆点。
- **失败态不"恐吓"**：failed 与 failed-still 仍为黄鸭（`#FFDA6A` 80.6%），不做红黑警示配色；错误语义交给 UI 语义色（`error #EC5B56`）。
- **降级完备**：每个动画都有 `-still` 静态帧；JS 成对声明 animated/still 常量，reduced-motion 下退化为静帧而非空白。
- **灰度变体存在但未启用**：另有 6 个灰调帧（如 `idle-still-pQaYwoLe` 主色 `#B9B7B9`、`failed-still-COqCfv4i` `#B3B0B4`、`look-180-337.5-BxPy1LC5`、`waving-still-daqnDblY`、`running-still-z2tKxgpY`、`waiting-still-FcYseAfq`）在全部 JS/CSS 中**检索不到引用** → 用途未确认（推测为浅色主题中性配色或历史遗留）。
- **小尺寸头像**：用户卡/邀请卡中鸭子以 `size-8`（32px）`object-contain` 渲染，底色 `color-mix(in srgb, var(--q4fa275) 36%, transparent)`。

---

## 5. 品牌配色（全部为真实取样 / 主题 token 实值）

### 5.1 核心品牌色（token 实值，非取样）

| 角色 | Light | Dark | 证据 |
|---|---|---|---|
| **主色 `primary`（`--q3f3223`）** | **`#4B6F5A`** | **`#5CB870`** | `styles-eCOZTk0p.css` 主题块 + `semantic_tokens.json` |
| primary-hover | `#436651` | `#9BE6B3` | 同上 |
| primary-active | `#3A5747` | `#73CD94` | 同上 |
| primary-bg | `#F2F4F2` | `#14261C` | 同上 |
| primary-border | `#D5DBD8` | `#335942` | 同上 |
| primary-text | `#4B6F5A` | `#8EE5A1` | 同上 |
| **吉祥物黄（鸭子）** | `#FFDA6B`（代码内 `bg-[#FFDA6B]`）/ `#FFD966`（图标）/ `#FEDA6E`（插画） | 同左 | JS + 取样 |
| 鸭子橙（喙） | `#F87825` | `#F77B27` | 取样 |
| **产品族标绿** | **`#2ADB5C`** | 同左 | `qoderIdeLogo` / `qoderCnIdeLogo` / `qoderwork*Logo` / `.mdq` 文件图标 |
| 内联字标绿 | `#255A41` | 同（被替换为 `currentColor`） | `gtdG4YpP.js`：`replaceAll('fill="#255A41"','fill="currentColor"')`，共 24 处 |
| 用户卡/签名绿 | `#316E50` / `#358E62` | — | `userCardRing` / `userCardDuck` / `userCardSignature` SVG |

**10 套主题的 primary 覆写值**（`semantic_tokens.json`）：light `#4B6F5A`、dark `#5CB870`、forest-light `#4B6F5A`、forest-dark `#4D9C61`、bee-light `#0D0D0D`、bee-dark `#E0C65C`、mint-light `#4FA98F`、mint-dark `#62C9A8`、light-parchment `#C96442`、parchment-dark `#E08A68`。

> **多绿并存（一致性风险，见 §7）**：UI 主色 `#4B6F5A`（低饱和森林绿）≠ 产品 Logo 绿 `#2ADB5C`（高饱和荧光绿）≠ 内联字标绿 `#255A41` ≠ 用户卡绿 `#316E50/#358E62`。四者未收敛到同一 token。

### 5.2 中性色阶（取样 + token 交叉）

| 角色 | Light | Dark | 用途 |
|---|---|---|---|
| text | `#141414` | `#EEEEEB` | 主文本 |
| text-secondary | `#636261` | `#B4B4AC` | 次级文本 |
| text-tertiary | `#838280` | `#7B7B74` | 说明文字（启动屏扫光核心源） |
| text-quaternary | `#AAA9A8` | `#585853` | 占位/元信息（**启动屏 Logo 本体源**） |
| bg-base | `#FFFFFF` | `#0E0E0E` | 最底层 |
| bg-layout | `#FFFFFF` | `#111110` | 窗口壳（**启动屏底色**） |
| bg-container | `#FFFFFF` | `#111110` | 面板/卡片 |
| bg-elevated | `#F9F9F9` | `#22221F` | 浮层 |
| border-secondary | `#DDDDDD` | `#31312D` | 描边 |
| fill | `#DFDFDF` | `#31312D` | 悬停填充 |
| fill-secondary | `#EFEFEF` | `#292926` | 次级填充 |

### 5.3 语义色

| 角色 | Light | Dark |
|---|---|---|
| error | `#EC5B56` | `#FF4D4F` |
| success | `#579B6E` | `#73CD94` |
| warning | `#EFB041` | `#FAAD14` |
| info | `#3B81E9` | `#0B83F1` |
| link | `#4D9868` | `#8EE5A1` |
| diff-insert | `#AEC8BA` | `#73CD94` |
| lavender（辅助） | `#B49EF9` | `#C9B5FF` |
| mint（辅助） | `#7FBB7A` | `#8ED69A` |
| sage（辅助） | `#7CB196` | `#8FC9AE` |
| mauve（辅助） | `#8E8C98` | `#B3B0BD` |

### 5.4 图片实测取样表（Pillow，取样文件 → hex / 占比 / 判读）

| 取样文件 | 尺寸 | Top 色（hex 占比） | 可用于 |
|---|---|---|---|
| `application-icons/qoder-dark.png` | 1024² | `#0F0D0C` 47.0% / `#808080` 16.9% / `#100D0C` 13.1% | 图标黑 `#0F0D0C` |
| `application-icons/qoder-light.png` | 1024² | `#FFFFFF` 40.0% / `#0F0C0C` 18.4% / `#FAFAFA` 15.0% | 图标白/黑 |
| `application-icons/qoduck-light.png` | 1024² | `#FFD966` 67.8% / `#F87926` 16.0% / `#FFFEFC` 11.5% | 鸭子黄 `#FFD966` |
| `tray/tray.ico` @32 | 32² | `#FFFFFF` 35% / `#FCFCFC` 17% / `#F2F1F1` 16% / `#020202` 13% | 托盘黑白 |
| `Qoduck01.webp` | 440² | `#FEDB72` 78.1% / `#C67E47` 11.2% / `#141210` 10.6% | 鸭子黄/描边 |
| `Qoduck02.webp` | 440² | `#FEDA6E` 65.5% / `#161412` 20.2% / `#99643B` 14.4% | 鸭子色 |
| `duckTerminal.webp` | 400² | `#F1C43E` 47.8% / `#FEE253` 25.7% / `#060000` 20.6% | 鸭子暗底 |
| `duckReading.webp` | 400² | `#F5C847` 48.7% / `#556439` 29.1% / `#FCE57A` 19.2% | 鸭子+书绿 |
| `Login_poster_0810.webp` | 672×896 | `#011A15` 27.9% / `#010F0A` 20.2% / `#348F44` 19.1% / `#0F4627` 12.2% / `#A5C971` 11.9% | **登录海报深绿主调 `#348F44` + 黄绿 `#A5C971`** |
| `onboardingWallpaper.webp` | 4608×2304 | `#263021` 20.8% / `#60715C` 17.9% / `#4B5639` 17.1% / `#869B98` 16.5% / `#3A4A33` 16.0% | **引导壁纸暗森林绿灰** |
| `agent-team-creation-figure.webp` | 1536×1024 | `#BDCDC2` 47.4% / `#ECF0EA` 28.8% / `#7B958B` 23.8% | 功能插画低饱和鼠尾草绿 |
| `qoderPioneerForestSticker.webp` | 680² | `#E2EEE8` 58.7% / `#6B8C7B` 19.0% | 纪念贴纸薄荷白+森林绿 |
| `voiceFirstUseSticker.webp` | 400² | `#A8C9B9` 57.1% / `#E8F2ED` 42.7% | 品牌浅绿 `#A8C9B9` |
| `quickNoteOnboardingFirstNote.webp` | 2400×1600 | `#8AC4BF` 24.2% / `#397C51` 19.1% / `#62A994` 18.3% / `#639358` 15.7% | 青绿+森林绿渐变 |
| `project-Cover-1/3/4/5/6.webp` | 80² | `#2C6E4E` 绿 / `#4B80E8` 蓝 / `#90D3FD` 天蓝 / `#E0935F` 橙 / `#9AB683` 草绿 | 项目封面多色系 |
| `snakeFirstPlaySticker.webp` | 400² | `#FF494B` 64.5% / `#FFFFFF` 26.2% / `#5CC884` 6.3% | 小游戏高饱和红（与主品牌绿无关） |
| `activeDays30Sticker.svg` | 400² | `#358432` 6 path / `#98D76F` 2 path | 徽章绿 |
| `activeDays7Sticker.svg` | 400² | `#1E89EB` 5 path / `#EFF6FB` 1 path | 徽章蓝 |
| `qoderAnniversary365Sticker.svg` | 400² | `#814B54` 5 path / `#F6CBE0` 2 path | 周年粉棕 |
| `vite.svg` / `yarn.svg` / `jest.svg` / `kubernetes.webp` | — | `#7E14FF`/`#47BFFF`；`#FFFFFF`；`#99425B`；`#326DE6` | 第三方生态 logo 原色（不改品牌色） |
| `glass-light.webp` | 1024² | `#E3E3E3`（RGB 均值 `#CBCCCB`，alpha 0–255 均值 33.4） | 玻璃光斑（见 §6） |
| `glass-dark.webp` | 1024² | `#1C1C1D` 31.0% / `#525456` 20.5% / `#C2C3C5` 14.6%（alpha 均值 33.7） | 暗色玻璃光斑 |
| `noise.webp` | 100² | RGB `#000000`，alpha 0–138（均值 32.9） | 纸纹噪点（见 §6） |
| `thinking-dot-matrix.webp` | 36² | `#A2A2A2` 42.1% / `#A3A3A3` 37.7% | 思考态点阵灰 |

### 5.5 品牌原始调色板（` :root` 98 变量中的色族）

| 色族 | 典型值 | 备注 |
|---|---|---|
| 森林绿 | `#316E50`、`#358E62`、`#477A61`、`#1C4432`、`#EDF5F1` | 主品牌色族来源 |
| 薄荷绿 | `#2CB879`、`#82E7BC`、`#DDF8EA`、`#4FA98F`、`#62C9A8` | mint 主题来源 |
| 羊皮纸/赤陶 | `#C96442`、`#E08A68`、`#E0C65C`、`#F3EFC7`、`#6F6D5D`、`#DFE3E8` | parchment 主题来源 |
| 灰绿中性 | `#191B1A`、`#252825`、`#4B765C`、`#949D96`、`#363C37` | 深色壳层 |
| 旧版强调色 | `#427DB5` 蓝、`#9870B4` 紫、`#BA7B37` 琥珀、`#B7647B` 玫瑰 | 辅助/历史遗留 |
| 文件图标色对 | 蓝 `#5A90EE/#89B4FF`、红 `#EA6D72/#FD7378`、紫 `#D17AF3/#D593EF`、黄 `#EFB041/#EEC857`、绿 `#3CC079/#94E98F`、青 `#18CED1/#79D5D7`、灰 `#757575/#9E9999` | qoder-seti 图标语法（light/dark 成对） |

---

## 6. 纹理与材质

### 6.1 玻璃（Glass）材质

| 项目 | 规格 | 证据 |
|---|---|---|
| 材质资产 | `glass-light.webp` / `glass-dark.webp`，1024×1024，预渲染玻璃光斑（alpha 0–255，均值 ≈33） | 取样 |
| 典型用法 | `LiveVoiceOverlay`：鸭子 `#qoduck-voice-frame` **104×104**，玻璃光晕 `#qoduck-voice-glass` **120×120**（鸭子外扩 8px 光环），层级 z-index 1 / 2 | `LiveVoiceOverlay-BaVnKw4v.css` |
| 明暗切换 | `@media (prefers-color-scheme: dark)` + `html[data-theme$="-dark"]` 双重判定，互斥显示 light/dark 两张 | 同上 |
| 玻璃底色 token | `--q36083d`：forest-light `#FFFFFF80`、mint-light `#C9E8DD8A`、light-parchment `#FFFFFFBD`、bee-light `#FFFFFF38`、parchment-dark `#0006` | 主题块 |
| 玻璃模糊 token | `--q5c5626`：默认 `0px`；**浅色主题族 = `24px`**（forest-light / bee-light / mint-light / light-parchment）；**暗色主题 = `0px`**（mint-dark / bee-dark / parchment-dark） | 主题块 → `.\[backdrop-filter\:blur\(var\(--q5c5626\)\)\]` |
| 亮度叠加（macOS） | `:root:not([data-platform=win32]){ --q46dd9a: blur(40px) saturate(150%); --qb6cac4: blur(2px) }` → 更强毛玻璃（Windows 关闭该增强） | `styles-eCOZTk0p.css` |
| 不支持 backdrop 的兜底 | `--q39d99e`：light `#FFF` / parchment-dark `#1C1B19` / mint-dark `#121A16` 等不透明底色 | 主题块 |

> 材质规则总结（证据）：**浅色主题启用 24px 背景模糊 + 半透明白；暗色主题模糊归零、改用纯色半透明壳**——避免暗色下模糊导致发灰。

### 6.2 噪点 / 纸纹（Noise）

| 项目 | 规格 | 证据 |
|---|---|---|
| 资产 | `noise-Bbnt96hm.webp`，100×100，黑色 RGB + alpha 0–138（均值 32.9） | 取样 |
| 主题开关 | `--qa8286b: url(./noise-Bbnt96hm.webp)` **仅在 forest-light 与 parchment-dark**；mint-dark / bee-dark 为 `none` | 主题块 |
| 使用方式 | `.loop-chrome-shell:before{ background-image: var(--qa8286b); background-repeat: repeat; background-size: var(--q4cdcad); opacity: var(--q2289a2); }`，其中 `--q4cdcad: 50px`（平铺 50px）、`--q2289a2: 0`（默认透明度 0，需主题/状态开启） | `styles-eCOZTk0p.css` |

> 即"纸纹"是可选材质层：只在羊皮纸/森林浅色语境铺设，且默认 opacity 0，由具体 surface 显式打开。

### 6.3 金属 / 银色（Metal）

- `qoder-metal.svg`（68×24，5 组线性渐变）用于个人资料卡的**金属质感字标**；`userCardSilverDuck`（`#CDCCCB`/`#838280`/`#F9F9F9`）、`userCardSilverSurface`（`#EFEFEF`–`#F7F7F7` 高密度灰阶）、`userCardStandardStamp`（`#6C6A6A`/`#8C8A88`/`#9D9A98`）构成"银卡/盖章"材质语言（`S__Wc8-4.js` 用户卡常量）。
- 金属感通过 **SVG 渐变 + 高密度中性灰阶** 模拟，非图片贴图（证据：`qoder-metal.svg` 含 5 个 gradient；银卡取样为连续灰阶）。

### 6.4 描边/阴影材质（token 化）

| 角色 | Light | Dark |
|---|---|---|
| `border`（`--q92c41c`） | `0 0 0 1px #0000000F, 0 1px 2px -1px #0000000F, 0 2px 4px 0 #0000000A`（用多层阴影模拟 1px 描边） | `0 0 0 1px #FFFFFF14` |
| `button-raised`（`--q9a8f94`） | `0 1px 3px …, inset 0 0 0 1px …, inset 0 -1px 0 …, inset 0 1px 0 …`（四层组合出微凸起） | 同结构，透明度换为暗色值 |
| 自然阴影 | `--q375abb: #0000000A` | 同 |
| 圆角 | Tailwind 阶梯：`--radius-xs 2px / sm 4 / md 6 / lg 8 / xl 12 / 2xl 16`；卡片 `border-radius:12px` + `corner-shape:squircle`（可视化 iframe）；玻璃/窗口级 `--q5c5626: 24px` | — |

### 6.5 其他材质线索

- **窗口渐变**：bee-light 的 `--q350ea6: linear-gradient(180deg, #E6E6B6 0%, #C4D0DA 100%)`（黄→蓝空气感），light-parchment 为 `#FDFCFA` 实色。
- **玻璃态描边**：parchment-dark 的 border 覆写 `0 0 0 1px #FFFFFF14` / `#FFFFFF1F`。
- **holographic 全息**：**未确认** —— 全部资产与 CSS 中未检索到 `holographic`/`holo` 命名或彩虹渐变材质；最接近者为金属/银卡。
- **feedbackWatermark**（176×176，`#8C8A8A`/`#BAB9B8` 灰）为反馈截图水印材质。

---

## 7. 品牌一致性观察（视觉语言 ↔ 产品气质）

1. **克制的工具感 + 有温度的陪伴感，分工明确**
   UI 层（启动屏、图标、chrome）几乎全部是**中性灰阶 + 低饱和森林绿 `#4B6F5A`**；彩色只出现在"人格层"（黄鸭、头像、贴纸、徽章）。这符合 Agent 工作台的核心诉求：长时间注视不疲劳、界面不抢注意力，情绪由吉祥物瞬间点亮。

2. **启动屏是"品牌静默"的范本**
   Logo 用 `text-quaternary 72%`（灰）而非品牌绿，整体 opacity 0.6，动画周期 2.15s 且扫光每轮停 28%——传达"安静启动、快速让位"。同时 reduced-motion 直接移除扫光层、120ms 淡出退出，工程规范与品牌表达一致。

3. **自然意象贯穿材质系统**
   主题命名（forest / mint / parchment / bee）与材质（纸纹噪点、羊皮纸赤陶、薄荷绿、蜂蜜黄）形成完整的"自然手账"叙事；玻璃仅在语音陪伴场景出现，弱化"科技炫技"感。圆角 24px + squircle 进一步强化纸感/卡片感。

4. **吉祥物承担"情绪接口"，且工程上可降级**
   同一只黄鸭通过 idle/jumping/waving/waiting/failed/look-16向/语音四态覆盖全流程反馈；每个动画都有 `-still` 静帧，保证 reduced-motion 下仍有形象存在。鸭子颜色 `#FFDA6B` 被直接写进 JS（贪吃蛇游戏元素），说明它是**一等公民品牌色**，而非素材偶然。

5. **图标分层策略清晰**
   OS/托盘图标 = 黑白单色（`#0F0D0C` + `#FFFFFF`），不引入品牌绿；产品族 Logo = 高饱和 `#2ADB5C`；UI 交互色 = 低饱和 `#4B6F5A`。三层各司其职：系统层克制、产品层鲜明、界面层舒适。

6. **一致性风险 / 待收敛点（客观记录）**
   - 品牌绿存在 4 个未统一来源：`#4B6F5A`（UI primary）、`#2ADB5C`（产品 Logo）、`#255A41`（内联字标，被运行时替换为 `currentColor`）、`#316E50/#358E62`（用户卡/签名）。未见统一 brand token，是"产品族多形态"策略还是历史遗留无法从代码判断（未确认）。
   - 代码字体 Fira Code（JS 内联）与 IBM Plex Mono（CSS）并存，未见统一声明（未确认正式代码字体）。
   - 6 个灰调鸭子状态帧在渲染层无引用（疑似废弃或预留）。
   - bee 主题（`primary #0D0D0D` 纯黑）与品牌绿体系差异最大，属"高对比模式"取向，需产品侧确认定位（未确认）。

---

## 8. 证据缺口 / 未确认清单

| # | 事项 | 状态 |
|---|---|---|
| 1 | Logo 最小尺寸、安全边距（clear space）、栅格制图规范 | 未确认（无设计规范文件） |
| 2 | favicon 规范 | 未确认（`index.html` 无 icon 声明，asar 无 favicon） |
| 3 | `qoderLogo-B1z0eOSP.svg` 的实际使用位置 | 未确认（渲染层 JS/CSS 未检索到引用） |
| 4 | `--q9592ea`（loader 基准时长）/ `--q06a65a`（loader 尺寸）的默认值 | 未确认（运行时注入，未定位赋值点；启动屏等效 1s 为推断） |
| 5 | 灰调鸭子状态帧（6 个）的用途 | 未确认（无引用） |
| 6 | Fira Code 与 IBM Plex Mono 哪套为正式代码字体 | 未确认 |
| 7 | `#2ADB5C` 是否为官方品牌绿（无 token 化） | 未确认（仅于产品 Logo/SVG/`.mdq` 文件图标出现） |
| 8 | 插画动画帧率/总帧数（webp 序列） | 未确认（仅知 voice_* 各态帧数） |
| 9 | 字体授权/许可证 | 未确认（资产内无 license 文件检出） |
| 10 | glass-light.webp 的生成方式（预渲染 vs 程序纹理） | 未确认 |

---

## 附：复现方法（供复核）

```powershell
# 1) 启动屏 CSS（内联）
Get-Content "E:\develop-lcb\workspace-tools\ToolCove\.qoder-analyzer\extracted\out\renderer\index.html"

# 2) 列 asar 内资产（Asar 类）
C:\Users\chenbo.li\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe -c "import sys;sys.path.insert(0,r'E:\develop-lcb\workspace-tools\ToolCove\.qoder-analyzer');from asar_lib import Asar;a=Asar();print(len(a.files))"

# 3) 主题变量块 / @font-face / 语义 token
#    见 .qoder-analyzer\semantic_tokens.json、token_defs.json（既有产物，本报告引用其值并已用 CSS 原文交叉验证）

# 4) 图片取色（Pillow 12）
#    取样脚本输出：%TEMP%\qoder-brand\palette_report.txt（642 行，含全部 webp/PNG/ICO 主色与占比）
```

> 声明：本报告所有 hex 值均来自 ① CSS/JS 原文中的主题 token 实值，或 ② Pillow 对具体文件的像素统计；无凭感觉书写的颜色。所有"未确认"项均未做推测性填充。
