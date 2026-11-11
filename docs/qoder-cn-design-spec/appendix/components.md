# Qoder CN 0.5.7 组件库设计规范（逆向产物）

> 分析对象：Qoder CN 0.5.7（Electron 43 + React 19 + Tailwind CSS v4）
> 分析范围：`out/renderer/assets/` 下的设计系统 chunk 与全量 CSS
> 产出人：component-miner（组件库规范线）
> 结论性质：**全部来自产物取证**；凡产物中无证据的项，均显式标注「未从产物中确认」，不做推测性补全。

---

## 0. 取证方法、证据源与置信度

### 0.1 证据源（只读）

| 文件 | 体积 | 内容定位 | 本文中的价值 |
|---|---|---|---|
| `S__Wc8-4.js` | 3.2 MB | **设计系统 bundle**，未深度混淆，`cva(...)`、`clsx(...)`、`displayName`、`data-slot` 均可读 | 组件变体/尺寸/状态的**第一手定义** |
| `index-BFGCOCH4.css` | 78 KB | 设计系统配套 CSS（`.qoder-*` 自研类、`@keyframes`、`.qoder-user-card`、`.qoder-empty-state` 等） | 复杂组件的 CSS 层规范、动效关键帧 |
| `styles-eCOZTk0p.css` | 387 KB | 全局 Tailwind v4 产物（`@layer theme/base/components/utilities`、`--spacing:.25rem`、`.squircle-*`、`.scroll-fade*`） | 工具类→hashed token 的解析基础 |
| `gtdG4YpP.js` | 15.8 MB | 主渲染 bundle（应用层组件：Chat Composer 应用壳、侧边栏、菜单面板） | 应用层拼装规范、`data-*` 行为约定 |

### 0.2 提取方法（可复现）

1. **CSS 规则解析**：自写小型 CSS tokenizer 解析 `@layer xxx { … }` 上下文 + 规则体（应对单行压缩 CSS）。
2. **组件定义定位**：以 `组件名.displayName="组件名"` 为锚点，反向定位 `X = reactExports.forwardRef(...)` 定义体，逐个导出（共 **153 个组件**）。
3. **变体矩阵提取**：直接读取 `cva("base", { variants, compoundVariants, defaultVariants })`；非 cva 组件读取 `const sizeClassNames={...}` / `variantStyles={...}` 常量表。
4. **类名归一**：`clsx(...)` 分支条件还原为「变体 × 状态」矩阵。
5. **Token 解析**：类名 → hashed 变量（`class_var.json`）→ 变量字面值（`styles-eCOZTk0p.css` 中 `--qXXXXXX: <literal>`）。
6. **应用层补充**：在 `gtdG4YpP.js` 中以 `data-chat-composer`、`data-*` 属性为锚点抓应用壳层类名。

### 0.3 置信度分级

- **A 级（高）**：直接来自设计系统 JS 定义或 CSS 规则原文，逐字可核对。
- **B 级（中）**：来自应用层 bundle 的类名拼装，受运行时分支影响，可能非穷尽。
- **C 级**：仅有属性/行为证据，视觉细节未取到 → 标注「未从产物中确认」。

---

## 1. 设计系统总体构成

### 1.1 三种组件实现形态

产物里组件并非"一套组件库"，而是**三层混合体系**：

| 层 | 形态 | 代表 | 证据 |
|---|---|---|---|
| L1 设计系统组件 | `S__Wc8-4.js` 中 PascalCase 组件，Radix primitive + `clsx`/`cva` 拼 Tailwind 类 | Button、IconButton、Input、Switch、Tabs、Select | `Button.displayName="Button"` 等 153 处 |
| L2 CSS 自研组件类 | `index-BFGCOCH4.css` 中手写 `.qoder-*` 类（keyframes、`data-state` 选择器） | `.qoder-drawer-*`、`.qoder-empty-state-*`、`.qoder-user-card`、`.qoder-inline-select-trigger` | CSS 规则全文 |
| L3 应用层组合 | `gtdG4YpP.js` 中用 L1 组件 + 工具类 + `data-*` 属性拼装 | Chat Composer、侧边栏、`+` 上下文菜单、建议面板 | `data-chat-composer`、`data-composer-suggestion-menu` 等 |

### 1.2 依赖栈（从产物符号推断）

- **Radix UI**：所有浮层/选择/菜单/滑块/进度均继承 Radix（`SelectPortal`、`DropdownMenuTrigger`、`SliderThumb`、`AlertDialogFooter`、`CheckboxBubbleInput`…）。
- **CVA（class-variance-authority）**：`cva` 在 bundle 中保留函数名；用于 Tag、Field、InputGroupAddon、PopoverButton 等。
- **motion（Framer Motion 系）**：浮层进入/退出动画 `initial/animate/exit/transition`；`useReducedMotion` 广泛使用。
- **sonner**：Toast 实现（注入式 CSS，见 §3.16）。
- **streamdown**：Markdown 渲染（`data-streamdown` 属性族）。
- **recharts / KaTeX**：图表与公式（`index` CSS 中 `.recharts*`、`.katex*`）。

### 1.3 组件清单规模

- `S__Wc8-4.js` 中带 `displayName` 的组件 **153 个**；`data-slot` 锚点 **58 处 / 56 个唯一值**；`role` 属性 **32 种**。
- 按用途分组见 **附录 A**。

---

## 2. 跨组件基础约定（先读这一节，再看组件族）

### 2.1 尺寸阶梯

产物中几乎所有交互控件共用同一个 **三档 + custom** 的高度体系（`--spacing: .25rem`，按 1rem=16px 折算）：

| 档位 | 高度类 | 折算 | 典型组件 |
|---|---|---|---|
| `sm` | `h-5` | 20px | Button(sm)、Input(sm)、Select(sm)、Tag(subtle sm 例外 h-4) |
| `md`（默认） | `h-7` | 28px | Button(md)、IconButton(md)、Input(md)、Select(md)、SendButton |
| `lg` | `h-9` | 36px | Button(lg)、IconButton(lg)、Input(lg)、Select(lg) |
| `custom` | `""` | 由调用方决定 | Button/IconButton/Input/Select 均保留 custom 空档 |

> **规律**：`sm=20 / md=28 / lg=36` 是设计系统硬约定，输入类、按钮类、选择类完全对齐。图标按钮单独有 `size-5/size-7/size-9`（=20/28/36px）与高度一致。
> **例外**：Tag 的 `subtle/plain + sm` 组合被 `compoundVariants` 压到 `h-4`(16px)；菜单项固定 `h-7`；Kbd 固定 `h-5`。

### 2.2 圆角体系：`squircle` 家族（重要特征）

设计系统**不用**普通 `rounded-*` 作为按钮/输入的主圆角，而是自研 `.squircle-*` 工具类（超椭圆圆角）：

```css
/* styles-eCOZTk0p.css */
.squircle-sm   { corner-shape:squircle; border-radius:.125rem }  /* 2px  */
.squircle-4    { corner-shape:squircle; border-radius:4px }
.squircle-6    { corner-shape:squircle; border-radius:6px }
.squircle-md   { corner-shape:squircle; border-radius:.375rem }  /* 6px  */
.squircle-lg   { corner-shape:squircle; border-radius:.5rem }    /* 8px  */
.squircle-xl   { corner-shape:squircle; border-radius:.75rem }   /* 12px */
.squircle-2xl  { corner-shape:squircle; border-radius:1rem }     /* 16px */
.squircle-full { corner-shape:squircle; border-radius:9999px }
```

| 语义档 | 类 | 半径 | 使用者 |
|---|---|---|---|
| 控件标准 | `squircle-2xl` | 16px | **Button（square 默认）**、**Input**、**Textarea**、SelectTrigger、Calendar 按钮 |
| 浮层/容器 | `squircle-xl` | 12px | ChatInput 外壳、Chat Composer 建议面板、TabsList(segmented) |
| 标签 | `squircle-4` / `rounded` | 4px | Tag(subtle/plain sm)、SourcePreviewSwitch 按钮 |
| 胶囊 | `squircle-full` | 9999px | Button(rounded="pill") |
| 小圆 | `rounded-sm/md/lg` | 2/6/8px（普通圆角） | 菜单项、Select 项、Tabs 触发器（`squircle-lg`） |

> **注意点**：`corner-shape` 是较新 CSS 特性；产物在 `.qoder-user-card` 等处以 `@supports (corner-shape: squircle)` 包裹并提供 `border-radius` 兜底。**部分组件混用普通 `rounded-*` 与 `squircle-*`**（见 §4.6 例外 E2）。

### 2.3 字号阶梯（实测使用值）

| token/任意值 | 折算 | 使用场景 |
|---|---|---|
| `text-[10px]` | 10px | Tag(subtle sm)、Avatar(compact/sm) |
| `text-[11px]` | 11px | Tag(sm)、Kbd、HoverCardList 计数 |
| `text-xs` | 12px | Button(sm)、Input(sm)、Select(sm)、Menu 描述、Breadcrumb、Tag(md) |
| `text-[12px]` / `text-[13px]` | 12/13px | UpdateNotificationCard 按钮、**Button(md)/Input(md)/Menu 项/Tabs 触发器主字号** |
| `text-sm` | 14px | Button(lg)、Input(lg)、ChatInput 输入区、Markdown 表格 |
| `text-[14px]` | 14px | Tabs(page)、PermissionCard 正文 |
| `text-base/lg` | 16/18px | IconButton 图标基准字号、Empty State 标题 |

> **结论**：存在 **12 / 13 / 14** 三个近邻字号被大量使用，其中 **13px 是"主 UI 字号"**（Button md、Input md、Menu、Tabs 默认、Select md 均 13px）。

### 2.4 语义 token 与实测色值（浅色主题）

类名 → hashed 变量 → 字面值（`styles-eCOZTk0p.css` 解析）：

| 语义类 | hashed 变量 | 实测值 | 用途 |
|---|---|---|---|
| `.text-text`（前景） | `--qf485f4` | `#141414` | 主文字 |
| `.text-text-secondary` | `--qea73d9` | `#636261` | 次级文字/图标 |
| `.text-text-tertiary` | `--q2704ac` | `#838280` | 三级文字、占位提示 |
| `.text-text-quaternary` | —（变量未取到） | — | 占位符、极弱文字、不可用 |
| `.text-text-on-primary` | `--qe315d9` | `#fdfdfd` | 主色上的反白文字 |
| `.text-primary` / `.bg-primary` | `--q3f3223` | `#4b6f5a` | **品牌主色（灰绿）** |
| `.text-success` | `--q0549cb` | `#579b6e` | 成功 |
| `.text-link` | `--q1250d9` | `#4d9868` | 链接 |
| `.bg-error` | `--q87e1c1` | `#ec5b56` | 危险主色 |
| `.bg-error-bg` | `--q427875` | `#fdf2f0` | 危险浅底 |
| `.bg-bg-base` | `--q4fa275` | `#fff` | 基础背景/浮层底 |
| `.bg-bg-container` | `--q71fecd` | `#fff` | 容器背景 |
| `.bg-bg-elevated` | `--qe7128e` | `#f9f9f9` | 抬升背景 |
| `.bg-bg-highlight` | `--qa80da2` | `#080807` | 高对比底（用于 secondary 按钮，反白方案） |
| `.bg-fill-secondary` | `--qa9633f` | `#efefef` | 悬停/次级填充 |
| `.bg-fill-tertiary` | `--q5ab60a` | `#f6f6f6` | 浅填充/表头 |
| `.border-border` | `--q2835bd` | `#bcbbba` | 强边框 |
| `.border-border-tertiary` | `--qecde42` | `#e6e6e6` | **控件默认边框** |

> 完整 token 体系（含暗色覆盖、palette 层）由 token 线负责；本节只列组件规则实际引用到的键。
> **命名层级清晰**：`bg-bg-*`（背景）、`bg-fill-*`（填充）、`text-text-*`（文字）、`border-border-*`（边框）、`{语义}-hover/active/-bg/-border`（状态后缀）。

### 2.5 状态表达惯例

| 状态 | 设计系统统一做法 | 证据样例 |
|---|---|---|
| hover | `hover:` 前缀，多为 `bg-fill-secondary/tertiary` 或 `text-text` | Button `hover:bg-fill-secondary hover:text-text` |
| focus | **不画 ring**：`focus:outline-none focus:ring-0`，改用**边框变色/底色变化** | Input `focus:border-border`；IconButton `focus-visible:bg-fill-tertiary` |
| focus-visible | 统一 `focus-visible:` 变体（键盘可见焦点） | Button `focus-visible:bg-primary-active` |
| active | `active:` 变体；raised 类按钮有 `active:scale-[0.96]` 按压反馈 | Button raised |
| disabled | **原生 `disabled` 属性 + `opacity-50 cursor-not-allowed`**（无独立 disabled token） | Button/Input/Select/Checkbox/Switch ICON... |
| loading/indeterminate | 组件内置分支：Progress `indeterminate`、Skeleton `animate-pulse`、`animate-indeterminate` | §3.19 |
| 状态型组件 | **`data-state` / `data-*` 属性** 驱动样式（Radix 约定） | Checkbox `data-[state=checked]:bg-primary`；Tabs `data-state=active`；Select `data-[highlighted]` |
| 移动指针焦点 | `data-pointer-focus` 区分鼠标/键盘焦点 | SelectTrigger `data-[pointer-focus]:focus-visible:border-border-tertiary` |
| 减少动效 | 统一 `motion-reduce:transition-none` / `motion-reduce:animate-none` | 几乎全部组件 |

### 2.6 动效约定

| 维度 | 约定 | 证据 |
|---|---|---|
| 基础时长 | `duration-150`（组件默认）、`duration-[120ms]`（raised/switch 等强调控件） | Button/Input/IconButton |
| 缓动 | `ease-out`；浮层用 `cubic-bezier(.16,1,.3,1)` / `(.2,.8,.2,1)` / `(.22,1,.36,1)` | SelectContent `transition:{duration:.15,ease:[.16,1,.3,1]}` |
| 浮层动画 | opacity 0→1 + scale 0.95~0.97→1 + 位移 4px，150ms | SelectContent、HoverCard、Tooltip |
| 抽屉 | 进入 .24s / 退出 .2s；reveal 变体 .35s | `.qoder-drawer-content` |
| 按压缩放 | `active:scale-[0.96]`（raised）、`hover:scale-[1.03]`（用户卡） | Button raised / user-card |
| 降级 | `prefers-reduced-motion` 全部关闭动画（含 `@media` 块） | `@media(prefers-reduced-motion:reduce)` 多处 |

### 2.7 图标尺寸约定

- 内联图标：`[&>svg]:size-3`（菜单项）、`size-3.5`（14px，Tag/Breadcrumb）、`size-4`（16px，Input addon/Button 图标）、`size-5`（20px，IconButton sm）。
- IconButton 图标字号随尺寸：`sm:text-xs / md:text-base / lg:text-lg`。
- 工具栏按钮统一 `[&_svg:not([class*="size-"])]:size-4`。

---

## 3. 组件族规范

> 每族固定四要素：**变体 / 尺寸档 / 状态 / 证据**；另附 anatomy、token、可访问性。
> 证据中 `S__Wc8-4.js` 简称 **DS**，`gtdG4YpP.js` 简称 **APP**，`index-BFGCOCH4.css` 简称 **IDX**，`styles-eCOZTk0p.css` 简称 **GLB**。

---

### 3.1 Button（按钮）

- **用途**：最基础的操作触发器，覆盖实心/描边/幽灵/文字/链接/抬升/危险等全场景。
- **Anatomy**：`<button>` = 可选 prefixIcon span + 文本 + 可选 suffixIcon span；图标 span 统一 `inline-flex shrink-0 items-center justify-center [&>*]:block [&>*]:leading-none`。
- **变体（`variant`，12 种，默认 `ghost`）**

| 变体 | 底色/文字 | hover | focus-visible |
|---|---|---|---|
| `primary` | `bg-primary text-text-on-primary` | `bg-primary-hover` | `bg-primary-active` |
| `secondary` | `bg-bg-highlight text-text-on-primary` | `bg-bg-highlight-hover` | `bg-bg-highlight-hover` |
| `tertiary` | `bg-fill-secondary text-text` | `bg-fill` | `bg-fill` |
| `tertiaryDestructive` | `bg-error-bg text-error` | `bg-error-bg-hover` | `bg-error-bg-hover` |
| `ghost`（默认） | `bg-transparent text-text-secondary` | `bg-fill-secondary text-text`（受 `ghostHoverFeedback` 开关） | `bg-fill-secondary text-text` |
| `text` | `bg-transparent text-text-secondary` | `text-text` | `text-primary` |
| `textPrimary` | `bg-transparent text-primary` | `text-primary-hover` | `text-primary-active` |
| `textSuccess` | `bg-transparent text-success` | `text-success-hover` | `text-success-hover` |
| `link` | `bg-transparent text-link underline-offset-2` | `underline` | `underline` |
| `outline` | `border border-border-tertiary bg-bg-base text-text` | `bg-fill-secondary text-text` | `border-primary-border bg-fill-secondary` |
| `raised` | `bg-button-raised-bg text-text shadow-button-raised` | `bg-button-raised-bg-hover` | `shadow-button-raised-focus` + `active:scale-[0.96]` |
| `destructive` | `bg-error text-text-on-primary` | `bg-error/90` | `bg-error-hover` |

- **尺寸档（`size`，默认 `md`）**——文字型变体（text/textPrimary/textSuccess/link）与实心型高度不同：

| size | 实心型 | 文字型 | 折算 |
|---|---|---|---|
| `sm` | `h-5 gap-1 px-2 py-0.5 text-xs font-medium leading-4` | `gap-1 py-0.5 text-xs font-medium leading-4` | 20px |
| `md` | `h-7 gap-1.5 text-[13px] font-medium leading-4` + `px-3`（有 prefixIcon 时 `pl-2.5 pr-3.5`） | `gap-1.5 py-1.5 text-[13px] leading-4` | 28px |
| `lg` | `h-9 gap-2 px-4 py-2 text-sm font-medium` | `gap-2 py-2 text-sm` | 36px |
| `custom` | `""`（完全交给调用方） | 同左 | — |

- **其他形态属性**：`rounded="square"(默认)→squircle-2xl` / `"pill"→squircle-full`；`textButton` 为 true 时强制走 `text` 变体；`ghostHoverFeedback=false` 可关闭 ghost 悬停反馈。
- **状态**：default / hover / focus-visible / active（raised 缩放）/ disabled（`opacity-50 cursor-not-allowed`，由各变体分支给出）；**loading 态未从产物中确认**（Button 无 loading prop）。
- **Token**：`primary*`、`text-text*`、`fill-*`、`error*`、`button-raised-*`、`border-border-tertiary`、`primary-border`。
- **可访问性**：原生 `<button>`；`disabled` 透传；无自定义 role/aria。
- **证据（A 级）**：
  - `S__Wc8-4.js`：`Button=reactExports.forwardRef(({variant:e="ghost",children:t,size:n="md",textButton:a=!1,prefixIcon:o,suffixIcon:l,rounded:me="square",disabled:mt=!1,ghostHoverFeedback:gt=!0,...})`
  - base 串：`"inline-flex items-center transition-[color,background-color,outline-color,text-decoration-color,fill,stroke] duration-150 motion-reduce:transition-none focus:outline-none"`，`me==="square"&&"squircle-2xl"`

---

### 3.2 IconButton（图标按钮 / 工具栏按钮）

- **用途**：纯图标操作；含 `toolbar` 玻璃拟态变体用于顶部工具条。
- **Anatomy**：`<button>` > `<span class="inline-flex items-center justify-center leading-none [&>*]:block [&>*]:leading-none">` > icon。
- **变体（`variant`，默认 `secondary`）**

| 变体 | 定义 |
|---|---|
| `primary` | `bg-primary text-text-on-primary hover:bg-primary-hover active:bg-primary-active focus-visible:bg-primary-active` |
| `secondary`（默认） | `border border-border-tertiary bg-bg-base hover:bg-fill-tertiary active:bg-fill-secondary focus-visible:border-primary-border focus-visible:bg-fill-tertiary` |
| `tertiaryDestructive` | `bg-error-bg text-error hover:bg-error-bg-hover focus-visible:bg-error-bg-hover` |
| `ghost` | `bg-transparent hover:bg-fill-tertiary active:bg-fill-secondary focus-visible:bg-fill-tertiary focus-visible:text-text`，并支持 **`aria-pressed:bg-fill-tertiary aria-pressed:text-text`**（可切换态） |
| `toolbar` | 玻璃控件：`box-border h-7 min-h-7 min-w-7 shrink-0 p-0` + `[&_svg:not([class*="size-"])]:size-4` + 径向渐变底 + `text-text-secondary` + `border border-border-tertiary` + 多层 inset 阴影；hover 有独立渐变/阴影/`active:shadow-[inset_0_2px_4px_...]` |

- **尺寸档（`size`，默认 `md`；`toolbar` 时 md 为空、由变体固定 h-7）**

| size | 类 | 折算 |
|---|---|---|
| `sm` | `size-5 p-1.5`，图标 `text-xs` | 20px |
| `md` | `size-7 p-1.5`，图标 `text-base` | 28px |
| `lg` | `size-9 p-2`，图标 `text-lg` | 36px |
| `custom` | `""` | — |

- **状态**：default / hover / active / focus-visible / disabled（`opacity-50 cursor-not-allowed`，toolbar 额外 `disabled:[&_svg]:opacity-50`）/ 可切换（`aria-pressed`）。
- **可访问性**：`aria-pressed` 用于 toggle 语义；图标本体通常 `aria-hidden`；按钮需调用方提供 `aria-label`（产物中调用处传入）。
- **证据（A 级）**：`S__Wc8-4.js`：`const yt=clsx("inline-flex items-center justify-center duration-150 ease-out focus:outline-none","transition-[color,background-color,border-color,box-shadow,opacity] motion-reduce:transition-none","focus-visible:outline-none",a==="square"&&"squircle-2xl")`；`t0={sm:"size-5 p-1.5",md:e==="toolbar"?"":"size-7 p-1.5",lg:"size-9 p-2",custom:""}`。

---

### 3.3 Input（单行输入框）

- **用途**：单行文本输入；含 `filled` 变体与三种聚焦反馈。
- **Anatomy**：原生 `<input>`。
- **变体（`variant`）**：`outline`（默认）`bg-bg-container`；`filled` `border-transparent bg-fill-tertiary hover:bg-fill-secondary focus:border-transparent focus:bg-fill-secondary`。
- **尺寸档（`size`，默认 `md`）**：`sm: h-5 px-2 text-xs leading-4` / `md: h-7 px-3 text-[13px] leading-4` / `lg: h-9 px-4 text-sm leading-5` / `custom: ""`。
- **状态**：
  - default：`border-border-tertiary`、`placeholder:text-text-quaternary`
  - focus：`focus:outline-none focus:ring-0` + 两种 `focusVariant`：`border`（默认）→ `focus:border-border`；`shadow` → `focus:border-transparent focus:shadow-input-focus`
  - error：`error` prop 或 `aria-invalid` → `border-error focus:border-error`
  - disabled：`disabled:cursor-not-allowed disabled:opacity-50`
  - 特殊 type：`search` 去除 WebKit 取消按钮、`file` 定制 `file:` 伪元素（`file:me-3 file:h-full file:border-r file:px-3 file:text-sm file:font-medium`）、`number` 去 spinner。
- **Token**：`bg-bg-container`、`fill-tertiary/secondary`、`border-border-tertiary`、`border-error`、`text-text`、`text-text-quaternary`、`squircle-2xl`。
- **可访问性**：`aria-invalid` 透传；`htmlSize` 映射原生 `size`。
- **证据（A 级）**：`S__Wc8-4.js`：`r0={sm:"h-5 px-2 text-xs leading-4",md:"h-7 px-3 text-[13px] leading-4",lg:"h-9 px-4 text-sm leading-5",custom:""}`；base `"flex w-full squircle-2xl border py-0 text-text transition-[...] duration-150 motion-reduce:transition-none"`。

---

### 3.4 Textarea（多行输入 / 自动增高输入）

- **用途**：多行文本；默认最小高度 80px，作为 ChatInput 的底层输入。
- **Anatomy**：原生 `<textarea>`，配套自定义细滚动条（`[&::-webkit-scrollbar]:size-1.5`、track `my-2`、thumb 仅 hover/focus 显示）。
- **变体**：仅 `focusVariant`（`border` 默认 / `shadow`）与 `disableFocusHighlight` 开关；**无 size 变体**（未从产物中确认多尺寸档）。
- **尺寸档**：固定 `px-3 py-2 text-[13px] font-normal leading-5`；`defaultMinHeight` 时 `min-h-[80px]`；`resize-none`。
- **状态**：default `border-border-tertiary` / error `border-error focus:border-error` / focus 同 Input / disabled `opacity-50 cursor-not-allowed` / 无高亮聚焦（`disableFocusHighlight` → `focus:border-0`）。
- **可访问性**：`aria-invalid` 透传。
- **证据（A 级）**：`S__Wc8-4.js`：`"flex w-full squircle-2xl border bg-bg-container px-3 py-2 text-[13px] font-normal leading-5 text-text transition-[...] duration-150 motion-reduce:transition-none"`，`n&&"min-h-[80px]"`。

---

### 3.5 表单组合族：Field / Label / Separator / InputGroup

- **用途**：表单语义容器 + 标签 + 分隔线 + 带前后缀的输入组合。
- **Anatomy / 变体**：
  - `Field`（`data-slot="field"`）：`group/field grid gap-2 has-aria-invalid:[&>[data-slot=label]]:text-error`，`orientation` 变体 `vertical`(默认)/`horizontal`/`responsive`（`@container (min-width:400px)` 切换两列）。
  - `FieldGroup`：`@container grid gap-6`。
  - `Label`（`data-slot="label"`）：`flex items-center gap-2 text-xs font-medium leading-[18px] text-text select-none` + `group-data-[disabled=true]/field:opacity-50` + `peer-disabled:opacity-50`。
  - `FieldLabel`：`data-[invalid=true]:text-error`。
  - `Separator`：`shrink-0 bg-border-tertiary`，horizontal `h-px w-full` / vertical `h-full w-px`，`role=none|separator`。
  - `InputGroupAddon`：`flex shrink-0 items-center text-text-tertiary [&>svg]:size-4`，`align` 变体 `inline-start: ps-3` / `inline-end: pe-3` / block。
  - `InputGroupButton`：`variant` `ghost|outline`，`size` `xs(h-5 gap-0.5 px-1.5 text-xs)|sm(h-7 gap-1 px-2 text-xs)|icon-xs(size-5)|icon-sm(size-5)`。
- **尺寸档**：Field 无尺寸；InputGroup Button 见上（xs/sm/icon-xs/icon-sm）。
- **状态**：错误态由 `has-aria-invalid` / `data-invalid` 联动；disabled 由 `group-data-[disabled=true]` 与 `peer-disabled` 联动。
- **可访问性**：`data-slot` 选择器作为样式钩子（`[&>[data-slot=label]]`），Label 为原生 label。
- **证据（A 级）**：`S__Wc8-4.js` 中 `fieldVariants=cva("group/field grid gap-2 has-aria-invalid:[&>[data-slot=label]]:text-error",{variants:{orientation:{...}},defaultVariants:{orientation:"vertical"}})`；`inputGroupAddonVariants=cva("flex shrink-0 items-center text-text-tertiary [&>svg]:size-4",...)`。

---

### 3.6 Chat Composer（对话输入框，旗舰组件）

- **用途**：对话框底部的复合输入区（文本 + 附件 + 模型/权限/文件夹/团队选择 + 发送/停止）。
- **Anatomy（设计系统 `ChatInput`）**
  1. **外壳**：`flex flex-col w-full bg-bg-container border border-border-tertiary squircle-xl transition-colors relative z-10 p-2 focus-within:border-primary-border`；disabled 时 `opacity-50 cursor-not-allowed`。
  2. **输入区**：`w-full resize-none outline-none bg-transparent text-sm font-normal leading-[24px] block h-auto min-h-[44px] p-1`；有内容 `text-text`，空 `text-text-quaternary`；`placeholder:text-text-quaternary`；细滚动条 `scrollbar-thin scrollbar-thumb-border scrollbar-track-transparent`。
  3. **footer**：`flex items-center w-full self-stretch gap-2 p-1`，内含 model 选择、permission 选择、`FolderButton`、`AgentTeamSelector`、发送/停止按钮等（均以 props 组合）。
  4. **自动增高**：按 `lineHeight × maxRows(默认 6)` 计算上限，超出转滚动。
  5. **键盘**：Enter 发送、Shift+Enter 换行、`isComposing` 时忽略（中文输入法保护）。
- **变体**：组件本身无 variant；**行为变体**通过 props 开关（`showFooter`、`showFolderButton`、`showMoreButton`、`enableFolderPermissionDialog`、`showAgentTeamSelector`、`sendButtonStatus`、`showGenerationStatus`）。
- **尺寸档**：单一尺寸（`min-h-[44px]`、`squircle-xl`、`p-2`、footer `gap-2 p-1`）；**未从产物中确认**多尺寸档。
- **状态**：default（border-tertiary）/ focus-within（border-primary-border）/ disabled（opacity-50）/ generating（footer 展示 generationStatus 与停止按钮）/ 附件态 / 目录权限弹窗（`AlertDialog` + Button `outline/pill` 与 `primary/pill`）。
- **应用层扩展（APP）**：
  - 组件根带 `data-chat-composer`；外层 `group/chat-composer`，用 `group-focus-within/chat-composer:opacity-100`、`group-hover/chat-composer:opacity-100` 控制操作区显隐。
  - `+` 上下文菜单（`DropdownMenu`）：`data-chat-composer-goal-mode`、`data-chat-composer-permission-mode="plan"`、`data-chat-composer-template-command`，配合 `aria-checked`/`data-state=checked`。
  - 建议面板（Popover）：`flex max-h-[min(480px,calc(var(--radix-popover-content-available-height,480px)-16px))] w-[min(560px,calc(100vw-32px))] flex-col overflow-hidden squircle-xl p-0 !py-0`，`side="top" align="start" sideOffset=8`，`data-chat-input-suggestion-menu`、`data-composer-suggestion-menu`。
  - 本地偏好键：`qoder:chat-composer:permission-mode`、`qoder:chat-composer:selected-model` 等。
- **可访问性**：`aria-label`/`aria-live="polite"`（发送按钮状态播报）、`role=button` 触发器等。
- **证据**：A 级（DS `ChatInput` 定义，见 `S__Wc8-4.js` @ChatInput）；B 级（APP 应用壳类名）。

---

### 3.7 Select / MultiSelect / Inline Select（下拉选择）

- **用途**：单选、多选（芯片）、以及内联"虚线下划线"选择（`inline`）。
- **Anatomy**：Trigger（`role=button`，含值 span + chevron）→ Content（Radix Portal）→ Item（文本 + 右侧 check 指示器）。
- **变体（`variant`）**：`default`（描边，`border bg-bg-base text-text`）/ `inline` / `inlineContinuation`（后两者 `qoder-inline-select-trigger border-0 bg-transparent text-purple`）。inline 变体有独立 hover 态：虚线下划线渐显（IDX `.qoder-inline-select-trigger:hover>span:after`）。
- **尺寸档（`size`，默认 `md`）**

| size | trigger | 内边距 | chevron | 多选 chip |
|---|---|---|---|---|
| `sm` | `min-h-5 gap-1 squircle-2xl py-0 text-xs font-medium leading-4` + `h-5` | `px-2` | `size-3.5` | `min-h-4 px-1.5 text-xs`，关闭 `size-3` |
| `md` | `min-h-7 gap-1.5 squircle-2xl py-0.5 text-[13px] font-medium leading-4` + `h-7 py-1.5` | `ps-3 pe-2.5`（有值时 `ps-1 pe-2.5`） | `size-4` | `min-h-5 px-2 text-[13px]`，关闭 `size-3.5` |
| `lg` | `min-h-9 gap-2 squircle-2xl py-1 text-sm font-medium leading-5` + `h-9 py-2` | `px-4` | `size-4` | `min-h-6 px-2 text-sm`，关闭 `size-4` |

- **浮层（Content）**：`relative z-50 max-h-96 min-w-[8rem] overflow-hidden rounded-lg border border-border-tertiary bg-bg-base p-1 text-text shadow-lg`；popper 模式带 `data-[side=*]:translate-*`、`min-w-[min(var(--radix-select-trigger-width),...)]`；上下滚动渐变按钮 `h-6 bg-gradient-to-b from-bg-base via-bg-base/80`；动画 `opacity/scale .95/y -4 → 1`，`duration:.15`。
- **菜单项（Item）**：`relative flex w-full min-w-0 cursor-pointer select-none items-center gap-2 whitespace-nowrap rounded-sm py-2 pl-2 pr-8 text-xs outline-none transition-colors`；选中指示 `absolute right-2 size-3.5` + `svg.size-4`。
- **状态**：default / hover / `focus` / `data-[highlighted]`（键盘高亮，均为 `bg-fill-secondary text-text`）/ `data-[disabled]`（`pointer-events-none opacity-50`）/ placeholder（`data-[placeholder]:text-text-tertiary`）/ open（chevron `rotate-180`）/ error（`border-error focus:border-error`）/ 键盘焦点区分（`data-pointer-focus`）。
- **可访问性**：Radix `listbox/option`；trigger `aria-invalid/aria-expanded`；多选芯片关闭按钮 `aria-label="Remove ..."`；`role=button tabIndex` 自定义触发。
- **证据（A 级）**：`S__Wc8-4.js`：`selectSizeStyles={sm:{trigger:"min-h-5 gap-1 squircle-2xl py-0 text-xs font-medium leading-4",...}}`；`selectTriggerBaseClassName="flex items-center justify-between whitespace-nowrap text-start cursor-pointer disabled:cursor-not-allowed disabled:opacity-50 [&>span]:min-w-0 [&>span]:truncate [&>span]:whitespace-nowrap"`。

---

### 3.8 DropdownMenu / 上下文菜单

- **用途**：`+` 上下文菜单、会话操作菜单、模型选择等。
- **Anatomy**：Radix `DropdownMenu` > Trigger > Content > Item / CheckboxItem / Separator / Sub。
- **变体**：无显式 variant；**按场景定制内容宽度/内边距**（见尺寸）。
- **尺寸档**：
  - Composer `+` 菜单内容：`w-[196px] p-1 shadow-lg`。
  - 通用菜单内容：`flex max-h-[min(360px,var(--radix-dropdown-menu-content-available-height,360px))] flex-col overflow-hidden p-1 shadow-lg`。
  - 菜单项（主）：`h-7 rounded-md px-2 py-0 text-[13px] font-normal leading-5 whitespace-nowrap [&_svg]:size-3`。
  - 菜单项（说明性/次级）：`h-7 rounded-md px-2 py-0 text-[13px] font-normal leading-5 text-text-tertiary`。
  - 面板阴影：`shadow-lg`；浮层圆角 `rounded-md/lg`（普通圆角，非 squircle）。
- **状态**：default / hover / focus（`bg-fill-secondary`）/ 选中（`bg-fill-tertiary text-text` + `aria-checked` + `data-state=checked`）/ disabled（`opacity-50` + Radix `data-disabled`）。
- **可访问性**：Radix `role=menu` + `aria-orientation=vertical`；方向键/Tab/typeahead 内建；`data-radix-menu-content` 属性。
- **证据**：`S__Wc8-4.js`（Radix 菜单基座）；`gtdG4YpP.js`：`const V5="h-7 rounded-md px-2 py-0 text-[13px] font-normal leading-5 whitespace-nowrap [&_svg]:size-3"`、`GD="flex max-h-[min(360px,...)] flex-col overflow-hidden p-1 shadow-lg"`、`ij0="w-[196px] p-1 shadow-lg"`。

---

### 3.9 Dialog / ContentDialog / AlertDialog（对话框）

- **用途**：通用内容弹窗、反馈弹窗、二次确认。
- **Anatomy**：Overlay + 居中容器 + Header（标题/描述）+ Body + Footer（右侧按钮组）。
- **变体**：
  - `ContentDialog`：基础容器 `fixed left-1/2 top-1/2 z-50 flex max-h-[90vh] w-[calc(100%-2rem)] -translate-x-1/2 -translate-y-1/2 flex-col overflow-hidden border border-border-quaternary text-text shadow-lg`；`variant="compact"` 由反馈弹窗使用。
  - `AgenticContentDialog`：`squircle-2xl flex h-full max-w-full shrink-0 flex-col overflow-hidden border border-border-quaternary bg-bg-elevated px-[6px] shadow-lg`；header `relative flex h-[46px] shrink-0 items-center px-2.5`；footer `flex h-10 shrink-0 items-center justify-end gap-1 px-1`。
  - `AlertDialog`（Radix）：Header/Footer 为纯布局容器；Footer 按钮组需 `flex flex-row justify-end gap-2`（调用处显式加）。
  - 反馈弹窗（`qoder-feedback-dialog-*`）：`padding:0; background-color:color-mix(in srgb,var(--q4fa275) 50%,transparent)` + `box-shadow` + 右上角 68px 水印贴纸 + `animation .2s 16ms cubic-bezier(.2,.8,.2,1)`。
- **尺寸档**：`ContentDialog` 宽度 `calc(100% - 2rem)`、`max-h-[90vh]`；反馈弹窗固定 `h-[min(calc(100vh-32px),536px)] max-w-[480px]`；**未从产物中确认**通用 sm/md/lg 尺寸档。
- **状态**：open/closed（Radix `data-state`，motion 进出场）；`closeOnEscape` 可配；遮罩点击关闭（由 ContentDialog 控制）。
- **可访问性**：Radix Dialog `role=dialog/alertdialog` + focus trap + `aria-labelledby/aria-describedby`（UpdateNotificationCard 使用）。
- **证据**：`S__Wc8-4.js` ContentDialog/AgenticContentDialog 定义；`IDX` `.qoder-feedback-dialog-content`。

---

### 3.10 Drawer（抽屉）

- **用途**：侧边抽屉（会话面板等），支持滑入与"揭示"两种动效。
- **Anatomy**：overlay + content（内部 header/body）。
- **变体（`data-drawer-*` 属性驱动）**：
  - side：`left` /（默认右）
  - motion：`slide` / `reveal`
- **尺寸档**：宽度由 CSS 变量 `--q3e07a8`（默认 `100%`）控制，content `max-w-full`；`rounded-l-lg`。
- **状态**：`data-state=open|closed`；slide 进入 `.24s cubic-bezier(.2,.8,.2,1)`、退出 `.2s`；reveal 进入 `.35s cubic-bezier(.22,1,.36,1)`（位移 94px + 模糊 2px → 0）；closed 时 `pointer-events:none`；`prefers-reduced-motion` 全关。
- **Token**：`bg-bg-container`、`border-border-tertiary`、`text-text`、`shadow-lg`；遮罩 `color-mix(in srgb,var(--q71fecd) 35%,transparent)` + `backdrop-filter:blur(2px)`；`data-visual-effects=off` 时去模糊。
- **可访问性**：Radix Dialog 基座（`role=dialog`、focus trap）；`data-drawer-side/motion` 暴露给样式层。
- **证据（A 级）**：`IDX`：`.qoder-drawer-content{--q3e07a8:100%;transition:width .32s cubic-bezier(.25,.1,.25,1)}`、`.qoder-drawer-content[data-drawer-motion=slide][data-state=open]{animation:qoder-drawer-enter .24s ...}`；`S__Wc8-4.js`：`"inset-y-0 z-40 flex max-w-full flex-col overflow-hidden rounded-l-lg border border-border-tertiary bg-bg-container text-text shadow-lg outline-none [-webkit-app-region:no-drag]"`。

---

### 3.11 Tooltip / HoverCard / Popover（浮层三件套）

- **用途**：提示（Tooltip）、富内容悬浮卡（HoverCard）、带交互的建议面板（Popover）。
- **Anatomy / 变体**：
  - **Tooltip**：`role="tooltip"`，`aria-describedby` 关联；`placement` top/bottom/left/right 且带**边界翻转**（越界自动换向）+ 位置夹取；支持 `interactive`、`delayDuration`、`disabled`；`open` 受控。
  - **HoverCard**：`z-50 w-64 overflow-hidden rounded-lg border border-border-tertiary bg-bg-base text-sm text-text shadow-lg`，动画 `opacity 0→1 / scale .97→1 / y 4→0`，`duration:.15 ease:[.16,1,.3,1]`；`HoverCardListContent` 追加 `w-max p-0`。
  - **Popover**（应用层）：建议面板 `squircle-xl p-0`，`max-h-[min(480px, calc(available-height-16px))]`、`w-[min(560px,calc(100vw-32px))]`。
- **尺寸档**：
  - Tooltip：`max-w-[240px] whitespace-normal break-words rounded-md px-2 py-1.5 text-xs leading-[14px] shadow-lg`；`fixed z-[1000] w-max`；内容滚动 `maxHeight=320`。
  - Tooltip 配色：亮底 `bg-bg-highlight text-text-on-primary`；可切 `bg-neutral-900 text-text border border-border-tertiary`（dark 风格）。
  - HoverCard：固定 `w-64`(256px)；Popover：宽 560px 上限。
- **状态**：default/hover-triggered/open/closed；Tooltip 关闭受滚动/窗口 resize/IntersectionObserver 影响（`useTooltipVisibility`）；进出场 150ms。
- **可访问性**：Tooltip `role=tooltip` + `aria-describedby`（仅显示时挂载）；HoverCard/Popover 由 Radix 提供。
- **证据（A 级）**：`S__Wc8-4.js`：`` className:`tooltip-content inline-block max-w-[240px] whitespace-normal break-words rounded-md px-2 py-1.5 text-xs leading-[14px] shadow-lg ${C0?"bg-neutral-900 text-text border border-border-tertiary":"bg-bg-highlight text-text-on-primary"}` ``；`role:"tooltip"`；HoverCardContent `"z-50 w-64 overflow-hidden rounded-lg border border-border-tertiary bg-bg-base text-sm text-text shadow-lg"`。

---

### 3.12 Tabs（标签页）

- **用途**：内容分区切换，覆盖分段、下划线、胶囊、页面级四种风格。
- **Anatomy**：`Tabs`（context）> `TabsList`(`role=tablist`) > `TabsTrigger`(`role=tab`) + `TabsContent`(`role=tabpanel`)；segmented+sliding 时额外渲染滑块指示器。
- **变体（`variant`，默认 `segmented`）**

| variant | List 容器 | 选中态 | 未选中 |
|---|---|---|---|
| `segmented` | `gap-0.5 overflow-hidden squircle-xl bg-fill-secondary p-0.5` | trigger `bg-bg-base shadow-sm` | `text-text-tertiary hover:text-text-secondary` |
| `line` | `overflow-x-auto`，`gap-3`（density=compact 时 `gap-4`） | `font-semibold` + focus `underline underline-offset-4` | 同左 |
| `pills` | `gap-1 overflow-x-auto`，trigger `px-3 py-1.5` | `bg-fill-secondary` | `text-text-secondary` |
| `page` | `gap-5 overflow-x-auto`，trigger `px-0 py-0 text-[14px] leading-6` | `text-text` | `text-text-quaternary hover:text-text-tertiary` |

- **尺寸档**：`size` `sm`（`text-xs font-normal`）/ `md`（默认，`text-[13px] leading-4 font-medium`）；`density` `default|compact`（compact 时 trigger `px-0`）；`fill` 让 trigger 平分（`flex-1`）；`motion` `none|sliding`（WAAPI FLIP，读 `--q138066` 时长与 `--q17be11` 缓动，默认 250ms `[.22,1,.36,1]`）。
- **状态**：`data-state=active|inactive`；disabled（`cursor-not-allowed pointer-events-none opacity-50`）；focus-visible 按 variant 分化（segmented 底色 / line&page 下划线）；键盘 Home/End/方向键 + RTL 感知 + 自动激活。
- **可访问性**：`role=tablist/tab/tabpanel`，`aria-selected`、`aria-controls`、`aria-orientation`、roving tabindex，`data-value` 用于指示器定位。
- **证据（A 级）**：`S__Wc8-4.js`：`TabsList=reactExports.forwardRef(function({variant:t="segmented",motion:n="none",size:a="md",density:o="default",fill:l,...})`；`TabsTrigger` base `"min-w-0 shrink cursor-pointer overflow-hidden text-ellipsis whitespace-nowrap squircle-lg px-2 py-1 text-center text-[13px] leading-4 font-medium outline-none transition-colors"`。

---

### 3.13 Table（表格）

- **用途**：Markdown 渲染表格 + 文档排版表格。
- **Anatomy**：`table > thead > tr > th` / `tbody > tr > td`；带 `data-streamdown` 属性族；表格外层可带复制/下载/全屏控件（由 MarkdownTable 的 controls 上下文控制）。
- **变体**：无 variant prop；两套样式来源：
  1. **消息内 Markdown 表格**（streamdown 组件类）：`th` = `whitespace-nowrap px-4 py-2 text-left font-semibold text-sm`；`td` = `px-4 py-2 text-sm`；`tr` = `border-border`；`thead` = `bg-muted/80`；`tbody` = `divide-y divide-border`。
  2. **排版域 `.typeset` 表格**（IDX）：`table{width:100%;border-collapse:collapse}`；`th{color:var(--qf485f4);font-weight:600;text-align:start}`；`thead{border-block-end:1px solid var(--qb002c5);background:var(--q5ab60a)}`；`tbody tr+tr{border-block-start:1px solid var(--qecde42)}`；`th,td{padding:8px 12px;vertical-align:top}`。
- **尺寸档**：单一档（`px-4 py-2` / `8px 12px`）；未发现紧凑/宽松变体。
- **状态**：无交互态（纯展示）；hover 行高亮未从产物中确认。
- **可访问性**：语义 `table/thead/tbody/th/td`；`data-streamdown="table-header-cell"` 等作为测试/样式钩子。
- **证据（A 级）**：`S__Wc8-4.js` MarkdownTh/Td/Tr/Thead/Tbody 定义；`IDX` `.typeset :where(...)` 规则。

---

### 3.14 Tag（标签 / Badge）

- **用途**：状态标记、分类、计数徽标；也用于上下文芯片（`ChatContextTag`）。
- **Anatomy**：`span` > 可选圆点(`size-1 rounded-full`) + 文本(`min-w-0 truncate`) + 可选关闭按钮(`size-4`, `aria-label`)；`closable` 时容器追加 `pr-1.5`。
- **变体（三正交维度，CVA）**
  - `appearance`：`filled`(默认) / `outline` / `subtle` / `plain`
  - `color`：`primary`(默认)/`success`/`error`/`warning`/`info`/`link`/`pink`/`purple`/`yellow`/`orange`/`teal`/`blue`/`mauve`/`slate`/`lavender`/`sage`/`mint`（17 个键；`filled` 的 `primary/info/link` 统映射到 blue 色系）
  - `size`：`sm` / `md`
  - **compoundVariants 规则**：`filled` → `bg-{color}-bg text-{color}`（`success/mint→mint`，`error→pink`，`warning→orange`）；`outline` → `border-{color}-border text-{color}`；`subtle/plain + sm` → `h-4 min-w-0 max-w-full squircle-4 gap-1 px-1.5 text-[10px] leading-3`。
- **尺寸档**

| size | 类 |
|---|---|
| `sm` | `gap-1 rounded px-2 py-0 text-[11px] leading-4` |
| `md`（默认） | `gap-1.5 rounded-md px-2.5 py-0.5 text-xs` |

- **状态**：静态为主；`closable` 有关闭按钮 hover 态；`subtle/plain` 且文本为 string 时自动挂 `title` 作截断提示。
- **Token**：`{color}-bg / {color} / {color}-border` 色彩组、`fill-quaternary`、`text-secondary`。
- **可访问性**：关闭按钮 `type=button` + `aria-label`（默认"关闭标签"）；圆点 `aria-hidden`。
- **证据（A 级）**：`S__Wc8-4.js`：`tagVariants=cva("inline-flex items-center justify-center whitespace-nowrap font-medium transition-colors group",{variants:{size:{sm:"gap-1 rounded px-2 py-0 text-[11px] leading-4",md:"gap-1.5 rounded-md px-2.5 py-0.5 text-xs"},appearance:{...},color:{...}},compoundVariants:[...],defaultVariants:{size:"md",appearance:"filled",color:"primary"}})`

---

### 3.15 Avatar（头像）

- **用途**：用户/Agent 头像、群组堆叠。
- **Anatomy**：`Avatar`（容器，`inline-grid place-items-center`）> `AvatarImage`(`size-full object-cover`) / `AvatarFallback`(`font-semibold leading-none`) + 可选 `AvatarBadge`(右下状态点)；`AvatarGroup` 负责堆叠、`AvatarGroupCount` 负责"+N"。
- **变体**：
  - `shape`：`circle`（默认，`rounded-full border border-border-tertiary` + inset 1px 高光环）/ `square`（`rounded-[50%] [corner-shape:squircle]` + 内层 inset 阴影）。
  - `AvatarBadge`：`absolute bottom-0 right-0 z-20 size-2 rounded-full border border-bg-container bg-success`。
  - `AvatarGroup`：`inline-flex items-center -space-x-1.5`；`AvatarGroupCount`：`size-5 rounded-full border border-border-tertiary bg-bg-elevated text-[10px] font-medium text-text-tertiary`。
- **尺寸档（`size`，默认 `default`）**

| size | 尺寸 | 字号 |
|---|---|---|
| `compact` | `size-[18px]` | `text-[10px]` |
| `sm` | `size-5`(20px) | `text-[10px]` |
| `md` | `size-6`(24px) | `text-[12px]` |
| `default` | `size-7`(28px) | `text-[12px]` |
| `lg` | `size-9`(36px) | `text-[14px]` |

- **状态**：静态；图片加载失败走 Fallback；badge 表达在线态。
- **可访问性**：`AvatarImage` 需 `alt`（默认空串）；装饰层 `aria-hidden`。
- **证据（A 级）**：`S__Wc8-4.js`：`const avatarSizeClassNames={compact:"size-[18px] text-[10px]",sm:"size-5 text-[10px]",md:"size-6 text-[12px]",default:"size-7 text-[12px]",lg:"size-9 text-[14px]"}`。

---

### 3.16 Toast / Notification / Alert（消息提示）

- **用途**：全局瞬时提示、更新通知卡、内联警示。
- **三种实现并存（重要例外）**：
  1. **Toast = sonner 库**（`S__Wc8-4.js` 内含完整 sonner）：`__insertCSS("[data-sonner-toaster]...")` 注入自有 CSS，使用自有 `--gray*` HSL 调色板与系统字体栈，**不走设计系统 token**；API 为 `toast.success/info/warning/error/custom/promise/loading`；`Loader` 为 sonner 的 12 条 bar spinner。
  2. **Notification = `UpdateNotificationCard`**（自研）：容器 `flex w-[280px] max-w-[calc(100vw-32px)] flex-col overflow-hidden rounded-xl border border-border-quaternary bg-bg-container p-2 text-text shadow-lg`；缩略图 `group relative h-40 w-full shrink-0 overflow-hidden rounded-[10px] bg-fill-tertiary`；右上关闭按钮 `absolute right-2 top-2 size-5 ... opacity-0 group-hover:opacity-100 focus-visible:opacity-100`；按钮 `h-7 ... px-2 text-[12px] font-medium leading-4`；`aria-labelledby/aria-describedby`。
  3. **Alert（内联警示，自研）**：`role="alert"`；容器 `rounded-lg px-3 py-2 flex items-center gap-2 w-full`；`variant`: `info`(默认)/`success`/`warning`/`error`；`size`: `sm`(`text-xs leading-[18px]`，icon `size-3.5`)/`md`(`text-sm leading-[22px]`，icon `size-4`)；`iconAlignment`: `center`/`firstLine`；`action` 插槽。
- **尺寸档**：见上（Alert sm/md；Notification 固定 280px 宽；Toast 由 sonner 默认 356px 宽——`--width` 变量）。
- **状态**：Toast：visible/loading/success/error/dismiss；Notification：默认/悬停显示关闭按钮；Alert：4 语义色 × 2 尺寸。
- **Token**：Notification/Alert 用 `bg-bg-container`、`border-border-quaternary`、`fill-tertiary`、`error-bg/error`、`success`、`warning` 等；**Toast 例外不使用 token**。
- **可访问性**：Alert `role=alert`；sonner 自带 `aria-live` 区域；Notification `aria-labelledby/describedby`。
- **证据（A 级/例外）**：`S__Wc8-4.js` 中 sonner `__insertCSS("[data-sonner-toaster]...")`、`variantStyles={info:"bg-[var(--qa51da0)] text-[var(--q619635)]",success:...,warning:...,error:...}`、`sizeStyles={sm:{text:"text-xs leading-[18px]",icon:"size-3.5",iconLine:"h-[18px]"},md:{...}}`；UpdateNotificationCard 定义。

---

### 3.17 Switch（开关）

- **用途**：即时生效的二元设置。
- **Anatomy**：`button[role=switch][aria-checked]` > thumb `span[data-switch-thumb]` > visual `span[data-switch-visual][aria-hidden]`（承载圆点与"吸引"动画类）。
- **变体**：无 variant prop；尺寸 `md`(默认)/`sm`；视觉上 checked/unchecked 两态。
- **尺寸档**

| size | root | thumb | visual | 选中位移 |
|---|---|---|---|---|
| `md` | `h-5 w-8`(20×32px) | `size-4` | `h-4` + 内部 vars | `translate-x-[13px]` |
| `sm` | `h-4 w-7`(16×28px) | `size-3` | `h-3` | `translate-x-[13px]` |

- **状态**：unchecked（`border-[var(--q470f3e)] bg-[var(--qbe1635)]`）/ checked（`border-transparent bg-[var(--q3f3223)]` 即品牌主色 `#4b6f5a`）/ hover/press（`data-switch-motion=on|off` 触发 `qoder-switch-attract-on/off` 宽度吸引动画）/ focus（`focus-visible:border-primary-border`）/ disabled（`cursor-not-allowed opacity-50`）。
- **动效**：thumb `duration-150 ease-[cubic-bezier(0.4,0,0.2,1)]`；root 颜色 `duration-[120ms] ease-out`；reduced-motion 关闭。
- **可访问性**：原生 button + `role="switch"` + `aria-checked`；`disabled` 原生属性。
- **证据（A 级）**：`S__Wc8-4.js`：`const switchSizeClassNames={md:{root:"h-5 w-8",thumb:"size-4",visual:"h-4 [--q2088fc:16px] ...",checkedTranslate:"translate-x-[13px]",uncheckedTranslate:"translate-x-px"},sm:{...}}`；`role:"switch","aria-checked":e,"data-switch-motion":t0??void 0`。

---

### 3.18 Checkbox / Radio（勾选与单选）

- **Checkbox**
  - **Anatomy**：Radix `Checkbox` > `CheckboxIndicator` > 勾选 SVG（`pathLength 11`、`stroke-dasharray/offset` 动画）+ 不确定态横线 SVG。
  - **尺寸档（默认 `md`）**：`md` root `size-4`(16px) + indicator `size-[10px]`；`lg` root `size-5`(20px) `rounded-md` + indicator `size-3`。
  - **状态**：unchecked（`border-border-tertiary bg-bg-container`）/ checked（`border-primary bg-primary text-white`）/ indeterminate（同 checked 配色）/ focus-visible（`border-primary-border bg-primary-bg`，checked 时 `bg-primary-active`）/ disabled（`cursor-not-allowed`；未选中 `bg-fill-secondary`，选中/不确定 `opacity-50`）。
  - **动效**：勾 `transition-[stroke-dashoffset] duration-[100ms]`，选中时 `duration-200`，缓动 `cubic-bezier(.22,1,.36,1)`。
  - **可访问性**：Radix `role=checkbox`、`aria-checked`（含 `mixed`）、`data-state`；隐藏 input 参与表单。
- **Radio**
  - **RadioGroup**：`grid gap-2`；Radix `role=radiogroup` + `aria-required/aria-orientation/aria-disabled`。
  - **RadioGroupItem**：`size-4 shrink-0 rounded-full border border-[var(--q2835bd)] outline-offset-2 cursor-pointer`；checked `border-[var(--qf485f4)] bg-[var(--qf485f4)] text-[var(--q4fa275)]`（深色实心 + 反白圆点）；focus-visible `border-primary-border bg-primary-bg`（checked 时 `bg-primary-active`）；disabled `cursor-not-allowed opacity-50`。
- **证据（A 级）**：`S__Wc8-4.js`：`const checkboxSizeClassNames={md:{root:"size-4",indicator:"size-[10px]"},lg:{root:"size-5 rounded-md",indicator:"size-3"}}`；`RadioGroupItem` 类串（原文含 `var(--q2835bd)` / `var(--qf485f4)` / `var(--q4fa275)`）。

---

### 3.19 Progress / Loading / Skeleton（进度与加载）

- **Progress**
  - **变体（`variant`，默认 `bar`）**：`bar`（连续进度条）/ `block`（分块进度条）。
  - **bar**：根 `relative h-1 w-full overflow-hidden rounded-full bg-fill-secondary`（内联 `style.height=4px`）；指示器 `h-full rounded-full bg-text-quaternary transition-[width] duration-200 ease-out`；不确定态 `animate-indeterminate absolute left-0`（宽度 40%）。
  - **block**：根 `flex flex-row items-center gap-0.5 w-full min-w-0`；每块 `shrink-0 rounded-sm transition-colors duration-200`，宽 2px + 高 12px，块数按容器宽度动态计算；已完成 `bg-text-quaternary`，未完成 `bg-fill-tertiary`。
  - **可访问性**：`role="progressbar"` + `aria-valuenow/valuemin/valuemax/valuetext`；不确定态 `aria-valuenow` 省略。
- **Loading**：三条并存——sonner 12-bar spinner（`sonner-loading-wrapper` / `sonner-spinner` / `sonner-loading-bar`，`data-visible` 控制）；品牌 SVG `qoder-loading-line-Bq9ip4M2.svg`；文字 shimmer `.qoder-text-shimmer`（`animation 2s linear infinite`，reduced-motion 关闭）。
- **Skeleton**：`animate-pulse rounded-md bg-fill-tertiary motion-reduce:animate-none`；无尺寸 prop（由调用方给 `h-*/w-*`）。
- **证据（A 级）**：`S__Wc8-4.js` Progress 定义全文；`Skeleton` 定义；`IDX` `.qoder-text-shimmer`。

---

### 3.20 Empty State（空状态）

- **用途**：列表/会话为空时的占位引导（"卡片堆叠"视觉）。
- **Anatomy**：container > 堆叠图标（`:before` / `:after` / `-face`）> 标题 > 描述 > 操作组。
- **变体**：仅 `stacked` 一种（`.qoder-empty-state-stacked*`）；**未从产物中确认**其他空状态版式（如纯文字/插画型）。
- **尺寸档（固定值，来自 CSS）**：
  - 容器：`padding-block:32px`，`width:100%`
  - 图标堆：`48×48px`，内部面 `border:1px solid var(--qecde42)`、`border-radius:12px`、`corner-shape:squircle`，左右两片 `translate(±6px) rotate(±12deg)`，`box-shadow:var(--q9a0431)`
  - 标题：`16px/24px`、`font-weight:500`、`letter-spacing:-.025em`、`text-wrap:balance`，`@supports (background-clip:text)` 时用 100° 渐变文字（`--qf485f4→--q3f3223`）
  - 描述：`12px/16px`、`max-width:560px`、`margin-top:10px`
  - 操作组：`flex flex-wrap justify-center gap:8px margin-top:16px`
- **状态**：hover（`:before/:after` 旋转角扩大到 ±18°、面 `translateY(-2px)`，仅 `hover:hover && pointer:fine && prefers-reduced-motion:no-preference`）；forced-colors 下标题降级为 `CanvasText`。
- **可访问性**：装饰性伪元素不参与可访问树；标题/描述为真实文本。
- **证据（A 级）**：`IDX` `.qoder-empty-state-stacked-*`、`.qoder-empty-state-stack-*` 规则全文。

---

### 3.21 Card（卡片族）

产物中无通用 `Card` 组件，而是**按场景定制的卡片**（这是规范层的重要事实）：

| 卡片 | 用途 | 关键规格 | 证据 |
|---|---|---|---|
| `FileCard` | 文件/目录引用卡 | `group/file-card relative flex h-16 min-w-[180px] max-w-full items-center overflow-hidden rounded-lg border border-border-tertiary/60 bg-bg-base pr-4`；标题 `text-sm font-semibold leading-[22px]`，副标题 `text-xs leading-[18px] text-text-quaternary`；hover `border-border-secondary`；错误态 `border-border-error/50 opacity-60`；悬浮删除按钮 `absolute -top-1.5 -right-1.5 size-4 rounded-full` | DS |
| `PermissionCard` | 权限申请卡 | `overflow-hidden rounded-xl bg-bg-base px-5 pb-3 pt-4`；头部按钮 `h-7 px-5 text-[14px] leading-6`；正文 `text-[13px] leading-5`；骨架条 `h-3 w-[76%] rounded-[4px]` | DS |
| `UpdateNotificationCard` | 更新通知卡 | 见 §3.16：`rounded-xl w-[280px] p-2 shadow-lg` | DS |
| `SuggestionBanner` | 建议横幅 | `relative rounded-xl border border-border-tertiary bg-bg-base p-3`；关闭 `absolute right-3 top-3 size-4`；滚动正文 `max-h-[90px] text-[12px] leading-[18px] text-text-tertiary` | DS |
| `ContextCard` | 上下文卡壳 | `group/context-card-shell relative w-[200px] max-w-full` | DS |
| `AgenticContentDialog` | 智能体内容卡/弹层 | `squircle-2xl bg-bg-elevated px-[6px] shadow-lg` | DS |
| `UserCard` | 用户名片（复杂 CSS 组件） | `width:min(100%,460px); aspect-ratio:23/32; border-radius:16px; box-shadow:0 60px 120px`；`data-variant=silver|standard`；`data-border-style=default|stamp`；容器查询 `cqw` 排版 | IDX |

- **变体/尺寸**：各卡片独立；共同点为 `rounded-lg/xl`、`border-border-tertiary/quaternary`、`bg-bg-base/container`、`shadow-lg`、内部 `p-2~p-5`。
- **状态**：hover（边框加深/浮层阴影）、错误（FileCard）、可关闭（Notification/SuggestionBanner）。
- **结论**：**没有统一 Card 抽象**，建议规范层定义 `Card` 基座（圆角/边框/底色/阴影/内边距）以收敛上述实现。

---

### 3.22 Scrollbar / Scroll Fade（滚动条与滚动渐隐）

- **Scrollbar（自研组件，DS）**
  - 机制：运行时 `__insertCSS` 注入按类隔离的 `::-webkit-scrollbar` 规则（类名随机后缀），参数化 `width/height`、thumb 颜色、圆角 `max(width/2,2)`。
  - 属性：`overlay`（悬浮覆盖）、`overlayTrackInset`、`scrollbarVisibility`（`always` 等）、`scrollbarWidth`（如反馈弹窗用 6px）、`maxHeight`（Tooltip 用 320）。
  - 状态：hover/focus 显示 thumb，默认透明（见 Textarea 的 thumb 显隐策略）。
- **scroll-fade（工具类族，GLB）**
  - 基础：`.scroll-fade,.scroll-fade-y/.scroll-fade-x/.scroll-fade-t/-b/-l/-r/-s/-e`，变量 `--q506445:min(12%,40px)`，`--q1d9543:96px`，用 `mask-image` 线性渐变做边缘渐隐；`:dir(rtl)` 有左右镜像。
  - 尺寸档：`.scroll-fade-3/4/6/8`（`calc(var(--spacing)*n)`）与任意值 `.scroll-fade-[8px]/[20px]`。
  - 进阶：`@supports (animation-timeline:scroll(self y))` 时用**滚动驱动动画**（`scroll-fade-y-start/end`，`animation-range:0 96px`）实现"滚到顶/底自动收渐隐"。
  - 关闭：`.scroll-fade-none`。
- **证据（A 级）**：`S__Wc8-4.js` Scrollbar 定义（含注入 CSS 模板串）；`GLB` `.scroll-fade*`、`.scrollbar-thin{scrollbar-width:thin}`。

---

### 3.23 Slider（滑块）

- **用途**：数值区间选择（设置项等）。
- **Anatomy**：Slider > SliderTrack > SliderRange + 可选 marks > SliderThumb（可多 thumb）。
- **变体**：`size` `sm`(默认 `md`)；`emphasis` `default`/`subtle`；`orientation` horizontal/vertical；`inverted`。
- **尺寸档**：`sm`：track `h-1`(横)/`w-1`(竖)、thumb `size-3 border`；`md`：track `h-2`/`w-2`、thumb `size-5 border-2`。
- **状态**：default（track `bg-fill-secondary`，range `bg-primary`）/ subtle（range `bg-primary/30`，thumb `border-border-secondary` + focus `border-text-secondary`）/ hover / focus-visible（`border-primary-border bg-primary-bg`）/ disabled（`data-[disabled]:cursor-not-allowed data-[disabled]:opacity-50 data-[disabled]:pointer-events-none`（thumb））。
- **Token**：`bg-fill-secondary`、`bg-primary`、`bg-bg-base`、`shadow-natural-sm`、`border-border-secondary/primary`。
- **可访问性**：Radix Slider（`role=slider`，键盘方向键）；thumb 支持 `aria-label/aria-labelledby/aria-valuetext`。
- **证据（A 级）**：`S__Wc8-4.js` Slider 定义（`t==="sm"?"size-3 border":"size-5 border-2"`、marks `size-0.5`/`size-1`）。

---

### 3.24 Kbd（快捷键提示）

- **用途**：展示键盘快捷键。
- **Anatomy**：`span.kbd-key`（可组合 `KbdGroup`）。
- **变体（`variant`，默认 `default`）**：`default`（描边 + 立体阴影）/ `dark`（深色描边 + 深阴影）/ `light`（`bg-fill-secondary text-text` 无描边）。
- **尺寸档**：固定 `min-w-[1.25rem] h-5 px-1.5 rounded text-[11px] leading-4`；字体 `Geist, -apple-system, ...`（组件级硬编码字体族）。
- **状态**：静态（无交互态）。
- **可访问性**：纯文本语义（`span`）；无特殊 aria。
- **证据（A 级）**：`S__Wc8-4.js`：`Kbd=...clsx("kbd-key inline-flex items-center justify-center min-w-[1.25rem] h-5 px-1.5 rounded text-[11px] leading-4",t==="default"&&"border border-border-tertiary bg-bg-highlight text-text-on-primary shadow-[0_1px_0_0_var(--qecde42)]",...)`。

---

### 3.25 SegmentedControl（分段切换 / SourcePreviewSwitch）

- **用途**：2~3 项的紧凑互斥切换（如"源码 / 预览 / 可编辑预览"）。
- **Anatomy**：`div[role=radiogroup]` > 滑块 thumb(`data-slot=source-preview-switch-thumb`) + `button[role=radio]` × N。
- **变体**：尺寸 `md`(默认)/`sm`；值域 `source|preview`（基础）或加 `editablePreview`（扩展）。
- **尺寸档**：`md`：root `w-[54px]`（扩展 `w-20`）、button `size-6 squircle-4`、icon `size-4`、thumb `size-6 squircle-4`；`sm`：更小（具体值在 `sizeClassNames.sm`，A 级可见但本节未逐字列出）。
- **状态**：选中（`role=radio aria-checked=true` + `data-state=active`、`text-primary-active`）/ 未选中（`text-text-secondary hover:text-text`、`data-state=inactive`）/ focus-visible（`bg-fill-tertiary`）/ disabled（`aria-disabled` + `opacity-50 cursor-not-allowed`）；thumb 位移 `translate-x-[26px]`（preview）/ `translate-x-[52px]`（editablePreview）。
- **可访问性**：`role=radiogroup` + `aria-label`、`role=radio` + `aria-checked`、`aria-orientation=horizontal`、方向键/Home/End、`aria-description` 支持。
- **证据（A 级）**：`S__Wc8-4.js` SourcePreviewSwitch 定义（`data-size`、`data-slot="source-preview-switch-thumb"`）。

---

### 3.26 Breadcrumb（面包屑）

- **用途**：层级导航；也用于文件路径/上下文标签。
- **Anatomy**：`nav[aria-label=breadcrumb]` > `ol` > `li`(icon + link/page) > separator。
- **变体**：组件无 variant；link 支持 `asChild`；`BreadcrumbPage` 为当前页。
- **尺寸档**：列表 `flex flex-wrap items-center gap-1 break-words text-xs font-medium text-text-tertiary`；图标 `size-3.5`；分隔符 `text-text-quaternary`；省略号按钮 `size-5`。
- **状态**：link hover/focus-visible → `text-text`；当前页 `font-medium text-text` + `aria-current=page`。
- **可访问性**：`nav aria-label="breadcrumb"`、`aria-current="page"`、分隔符 `role=presentation aria-hidden`。
- **证据（A 级）**：`S__Wc8-4.js` Breadcrumb 系列定义。

---

### 3.27 SplitButton / FloatingButton（分裂按钮与浮动按钮）

- **SplitButton**：主操作 + 下拉触发分离；容器 `inline-flex shrink-0 items-stretch overflow-hidden`；子件 `SplitButtonAction/SplitButtonTrigger/SplitButtonSeparator`；`aria-label`/`aria-disabled` 透传。**变体/尺寸档未从产物中确认**（子件视觉类由调用方传入）。
- **FloatingButton**：浮动圆形/方形按钮；尺寸 `size-7 p-1.5` / `size-8 p-2`；动效 `transition-[color,background-color,transform] duration-200 ease-[cubic-bezier(0.34,1.56,0.64,1)]`（回弹曲线）；图标 `size-4`。
- **证据**：`S__Wc8-4.js` SplitButton/FloatingButton 定义。

---

## 4. 组件一致性观察

### 4.1 命名规范

| 对象 | 规范 | 证据 |
|---|---|---|
| React 组件 | PascalCase，`displayName` 与变量名一致（153/153） | `Button.displayName="Button"` |
| 设计系统 CSS 组件类 | `qoder-` 前缀 + kebab-case，BEM 风格修饰（`__`） | `.qoder-drawer-content`、`.qoder-empty-state-stack-face`、`.qoder-user-card__standard-name` |
| 状态属性 | kebab-case `data-*`：`data-state`、`data-drawer-side`、`data-drawer-motion`、`data-switch-motion`、`data-chat-composer-*`、`data-composer-suggestion-menu` | IDX / APP |
| 样式钩子 | `data-slot="kebab-case"`（56 个唯一值），用于 `[&>[data-slot=label]]` 组合选择器 | DS |
| CSS 变量 | 全部哈希为 `--qXXXXXX`（6 位十六进制），**无语义名**；仅在少量 `data-*` 局部作用域内出现"半语义"变量（如 `--q3e07a8` 抽屉宽度、`--q78a0a9` 日历单元 32px） | GLB / IDX |
| 动画 | `qoder-` 前缀 kebab：`qoder-drawer-enter/exit`、`qoder-switch-attract-on/off`、`qoder-text-shimmer`；streamdown 用 `sd-` 前缀（`sd-fadeIn/sd-blurIn/sd-slideUp`） | IDX |

### 4.2 变体命名规律（API 层）

产物中的变体 prop 命名高度模式化，可归纳为 8 个"正交轴"：

1. `variant`：语义角色（primary/secondary/tertiary/ghost/outline/link/destructive/raised/toolbar/inline/default）
2. `size`：`sm | md | lg | custom`（**所有组件统一四档**，Button/IconButton/Input/Textarea/Select/Tag/Tabs/Avatar 均遵守）
3. `appearance`：`filled | outline | subtle | plain | solid`（Tag、按钮类）
4. `color`：语义色（17 色键，Tag 最全）
5. `rounded`：`square | pill`（Button/IconButton）
6. `density`：`default | compact`（Tabs）
7. `motion`：`none | sliding | crossfade | overlap`（Tabs 等）
8. `shape / orientation / emphasis / fill / iconAlignment / focusVariant`：结构性轴

> **规律**：缺省值几乎都是 `size="md"` + 最中性变体（`ghost` 或 `secondary`），`custom` 档存在但类名为空串——说明设计系统预留了"完全自定义"逃生口。

### 4.3 Token 使用一致性

- **一致性好的部分**：
  - 颜色 100% 走语义类（`bg-primary`/`text-text-secondary`/`border-border-tertiary`），未发现直接 hex（组件层）。
  - 状态后缀统一：`-hover` / `-active` / `-bg` / `-border`。
  - 高度/间距统一走 `--spacing` 阶梯（h-5/7/9）。
  - 圆角统一走 `squircle-*`（按钮/输入/浮层除外见例外）。
- **不一致/例外（重要）**：
  1. **硬编码 hashed 变量**：Switch 的 checked/unchecked 色、Radio 的边框/选中色直接写 `bg-[var(--q3f3223)]`、`border-[var(--q470f3e)]`、`border-[var(--q2835bd)]`、`text-[var(--qe315d9)]`；Alert 的语义色 `bg-[var(--qa51da0)]` 等——**组件层直接绑定哈希变量**，可读性/可维护性差。
  2. **Sonner Toast 完全脱离 token**：自有 `--gray*` HSL 调色板 + 系统字体栈（`ui-sans-serif, system-ui...`），与设计系统语义层无关。
  3. **Markdown 表格使用旧别名**：`bg-muted/80`、`border-border`（`muted` 不在组件 token 体系内）。
  4. **任意值泛滥**：`text-[13px]`、`text-[12px]`、`text-[14px]`、`leading-[18px]/[22px]/[24px]` 等未收敛到字号 token（虽在产物中稳定复用，但属"事实标准"而非"token 标准"）。
  5. **字体硬编码**：Kbd 硬编码 `Geist` 字体族；`.qoder-user-card` 硬编码 `Inter / Roboto Mono / IBM Plex Mono`。

### 4.4 尺寸与间距一致性

- **高度三角对齐**：Button/Input/Select/IconButton 在 sm/md/lg 三档完全对齐（20/28/36px），这是设计系统最强的一致性约束。
- **内边距差异**：同为 md，Button `px-3`、Input `px-3`、Select `ps-3 pe-2.5`、Menu 项 `px-2`、Tag md `px-2.5`——按"控件含图标/含下拉箭头"做微调，属合理差异。
- **圆角差异**：Button/Input/SelectTrigger 用 `squircle-2xl`(16px)；Select 菜单项/Tabs 触发器用 `rounded-sm/squircle-lg`(2~8px)；浮层用 `rounded-lg`(8px)/`squircle-xl`(12px)。**同一控件族内圆角档位不统一**（如 SelectTrigger 16px vs SelectItem 2px）——这是刻意层级差，但规范文档应明示。
- **图标尺寸**：`size-3（菜单）/3.5（标签、面包屑）/4（输入、按钮内）/5（IconButton sm）`，按控件高度等比缩放，规律清晰。

### 4.5 状态与可访问性一致性

- **焦点风格**：全库统一"**边框变色 + 背景变化**"，不用 ring；`focus:ring-0` 在 Input/Textarea 明确写出。这是该设计系统的显著特征。
- **禁用风格**：统一 `opacity-50 + cursor-not-allowed`，未单独定义 disabled 颜色 token。
- **降级**：`motion-reduce:` 在几乎所有动效组件出现；`prefers-reduced-motion` 媒体块在 CSS 层同步兜底。
- **ARIA 覆盖**：Radix 基座保证 `role/aria-*` 完整（32 种 role），自定义组件（Tabs、Segmented、Tag 关闭、ChatInput）也补齐了 `role/aria-*`，整体可访问性水平较高。
- **数据属性驱动的状态机**：`data-state` 是跨组件通用约定（Radix + 自研同构），是规范中应固化的接口。

### 4.6 例外与风险清单

| # | 例外 | 风险 | 建议 |
|---|---|---|---|
| E1 | Toast 用 sonner 自有样式，不接 token | 深浅主题/品牌色不一致 | 覆写 sonner CSS 变量接入语义层，或替换为自研 Notification |
| E2 | `squircle-*` 与 `rounded-*` 混用（且部分组件两种都用） | 圆角语义不统一 | 规范层定义"控件/浮层/标签"三档圆角映射表 |
| E3 | 组件层直接写 `var(--qXXXXXX)` | token 语义丢失、暗色适配风险 | 在 design-system 增加语义别名层 |
| E4 | 字号大量 `text-[13px]` 等任意值 | 排版阶梯漂移 | 收敛为 `text-ui(13px)` 等语义 token |
| E5 | 无统一 Card 抽象（6+ 种定制卡） | 间距/圆角/阴影碎片化 | 定义 Card 基座 + 变体 |
| E6 | Button 无 loading 态 | 各业务自行实现转圈 | 增加 `loading` prop 规范 |
| E7 | Tooltip 存在双配色（`bg-bg-highlight` / `bg-neutral-900`） | 主题判断散落 | 收敛为 `tone` 变体 |
| E8 | 字号/行高/图标在 Tag compoundVariants 中大幅偏离主阶梯（10px/16px） | 小尺寸可读性 | 明确"小标签"专用档位 |
| E9 | 同一语义不同实现（Notification 三套：sonner / UpdateNotificationCard / Alert） | 使用选择成本高 | 规范明确三者的使用边界（全局瞬态 / 持久通知卡 / 内联提示） |
| E10 | `ChatInput` 内文案为中文硬编码 + i18n key 混用（`composer.actions.addContext`） | 国际化一致性 | 组件层禁止硬编码文案 |

### 4.7 未从产物中确认的项（明确清单）

1. **暗色主题的具体色值**：本文色值均为浅色主题（`--q4fa275=#fff` 等）；暗色覆盖块未与组件类逐项对照。
2. **Button/Input 的 loading / 成功态**：未发现对应 prop。
3. **通用 Dialog 的尺寸档（sm/md/lg）**：仅有 `max-h-[90vh] + w-[calc(100%-2rem)]` 与反馈弹窗的固定尺寸。
4. **Table 的行 hover/选中态、排序/筛选交互**：产物中表格为 Markdown 展示用途，未发现数据表格交互规范。
5. **Empty State 的非 stacked 形态**：仅取到 `.qoder-empty-state-stacked*`。
6. **SplitButton 子件的视觉类**：仅取到容器结构类。
7. **Tooltip 的 dark 模式触发条件**：`C0` 变量来源未溯源（可能为主题或场景判断）。
8. **各组件在暗色/高对比模式下的完整状态矩阵**：仅确认 `forced-colors` 在空状态标题有降级处理。
9. **Tag `outline` 在 17 色中 `lavender/sage` 的完整覆盖**：compoundVariants 已完整取到（含 lavender/sage），但 `mint` 的 outline 映射为 `border-mint-border` 而 `primary` 映射到 blue —— 属命名历史包袱，非缺失。
10. **动效时长 token 化**：产物中时长为字面值（150ms/120ms/200ms/240ms/320ms/350ms），未见时长 token 变量名。

---

## 5. 附录

### 附录 A：设计系统组件清单（153 个 `displayName`，按域分组）

- **按钮/操作（9）**：Button、IconButton、FloatingButton、SplitButton、SplitButtonAction、SplitButtonTrigger、SplitButtonSeparator、SendButton、DrawerContent
- **表单/输入（14）**：Input、Textarea、InputGroup、InputGroupAddon、InputGroupButton、InputGroupInput、InputGroupTextarea、Label、Field、FieldGroup、FieldLabel、FieldTitle、FieldDescription、FieldError
- **选择/菜单（5）**：SelectContentFragment、SelectItemText、MultiSelect、OptionList、DropdownMenuShortcut
- **浮层（6）**：Tooltip、HoverCardList、HoverCardListContent、HoverCardListItem、ContentDialog、AlertDialogHeader/Footer
- **布局/容器（10）**：Panel、ResizablePanel、ResizablePanelGroup、ResizableHandle、Separator、Scrollbar、GradualBlur、Skeleton、Progress、Breadcrumb（`Breadcrumb*` 系列 6 个）
- **数据展示（12）**：Tag、Avatar（`Avatar*` 系列）、FileCard、ContextCard、PermissionCard、PlanConfirmationCard、ToolInvocationCard、FileChangesSummary、ThinkingSummaryPreview、TurnStatusBar、ChatQueue、ChatRequest
- **Markdown/排版（30+）**：MarkdownBody、MarkdownH1~H6、MarkdownParagraph、MarkdownCode、MarkdownCodeBlock、MarkdownTable/Th/Td/Tr/Thead/Tbody、MarkdownUl/Ol/Li、MarkdownBlockquote、MarkdownA、MarkdownImg、MarkdownHr、MarkdownStrong/Sub/Sup、MarkdownSection、MarkdownStreamBlock、MarkdownExternalLinkCard、Typeset、Streamdown、MermaidDiagram、MarkdownText、EllipsisText、ChatInput
- **对话（9）**：Bubble、BubbleContent、DiscussionOwnBubble、DiscussionOtherBubble、Message、MessageAvatar、MessageContent、MessageHeader、MessageFooter、MessageScroller（含 Button/Content/Item/Viewport）、ChatContextTag、ChatInput、PromptSuggestions、UserQuestion、UserQuestionAnswer
- **通知/反馈（8）**：Alert、UpdateNotificationCard、SuggestionBanner、FeedbackDialogSurface、FeedbackDialogScrollArea、FeedbackDialogSubmitButton、AgenticContentDialog、FullAccessPermissionDialog
- **业务卡（8）**：AccountMenuTrigger、AccountUsageOverview、AgentTeamSelector、ProjectInviteCard、LarkAuthCard、DwsPatCard、Presence、UserCard
- **日期/时间（5）**：Calendar、DatePicker、TimePicker、SourcePreviewSwitch（`data-slot` 定位）、Slider
- **图标/装饰（6+）**：BellIcon、BrainIcon、FeatherIcon、CompressionAnimationIcon、ContentBlockedIcon、ModelOverloadedIcon、SmartphoneChargingIcon、LaptopMinimalCheckIcon、Loader、LiveWaveform、ImageGenerationGrid
- **其他**：Kbd、KbdGroup、Group、DesktopPet（及其 Sprite/LookSprite/ActivityBubble/ActivityReply/ActivityStack）、Switch、Checkbox、RadioGroup、Progress、Skeleton

> 完整名单可通过 `S__Wc8-4.js` 的全部 `*.displayName="..."` 抽取复现（153 条）。

### 附录 B：自研 CSS 组件类（`index-BFGCOCH4.css` 为主）

| 类族 | 代表类 | 用途 |
|---|---|---|
| 抽屉 | `.qoder-drawer-content/overlay/expanded-backdrop` | 侧滑抽屉（`data-drawer-side/motion/state`） |
| 空状态 | `.qoder-empty-state-stacked/-stack/-stack-face/-title/-description/-action` | 空态堆叠卡 |
| 用户卡 | `.qoder-user-card` + `__surface/__frame/__holographic/__text-layer/__badge-anchor/__standard-*` | 用户名片（容器查询 + 3D） |
| 内联选择 | `.qoder-inline-select-trigger` | 虚线下划线选择器（hover/focus/open 显示） |
| 开关 | `.qoder-switch`、`.qoder-switch-attract-on/off` | Switch 动画 |
| 反馈弹窗 | `.qoder-feedback-dialog-*` | 反馈弹窗玻璃底 + 水印 |
| 文本动效 | `.qoder-text-shimmer`、`.qoder-thinking-dot-matrix` | 流式文本/思考动画 |
| 图表 | `.qoder-chart-*` | 图表容器 |
| 滚动 | `.scroll-fade*`（GLB）、`.scrollbar-thin` | 边缘渐隐/细滚动条 |
| 其他 | `.markdown-body`、`.typeset`、`.katex*`、`.cm-editor` | 文档排版/公式/代码编辑器 |

### 附录 C：证据文件索引

| 主题 | 文件 | 定位方式 |
|---|---|---|
| 组件变体矩阵 | `S__Wc8-4.js` | `tagVariants=cva(`、`switchSizeClassNames=`、`selectSizeStyles=`、`avatarSizeClassNames=`、`checkboxSizeClassNames=`、`Alert` 常量表 |
| 组件定义体 | `S__Wc8-4.js` | `X=reactExports.forwardRef(...)` + `X.displayName="X"` |
| 自研 CSS 组件 | `index-BFGCOCH4.css` | `.qoder-*` 规则、`@keyframes` |
| 工具类→token | `styles-eCOZTk0p.css` | `.squircle-*`、`.scroll-fade*`、`--qXXXXXX: <literal>` |
| 应用层壳 | `gtdG4YpP.js` | `data-chat-composer`、`data-composer-suggestion-menu`、`const V5=` 等菜单常量 |

---

### 结论摘要（给规范报告并入用）

1. **尺寸与高度高度收敛**：`20/28/36px`（h-5/h-7/h-9）+ `sm/md/lg/custom` 四档是全库最强约束，可直接固化为设计 token。
2. **圆角是超椭圆 slop 体系**：`corner-shape:squircle` + 16px 控件主圆角，是该产品最具辨识度的视觉特征，必写进规范。
3. **状态一律"边框/底色变色 + opacity-50 禁用"**，无 ring 焦点环；浮层统一 150ms `opacity+scale+位移` 动画。
4. **Token 语义化只在类名层完成**，组件实现层仍有大量 `var(--qXXXXXX)` 直引；Toast(sonner)、Markdown 表格(`bg-muted`)是明显的体系外例外。
