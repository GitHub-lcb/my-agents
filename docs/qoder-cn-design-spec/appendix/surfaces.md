# Qoder CN 0.5.7 — 产品界面与信息架构逆向报告

> 分析对象：`app.asar`（200.6 MB，6448 文件）→ `out/renderer/`、`out/main/`、`out/preload/`。
> 证据格式：`文件 @位置 / 选择器 / 字符串`。标注 **推断** 的结论 = 有间接证据但未直接命中；标注 **未确认** 的 = 本次无可靠证据。
> 备注：主进程 `electronMain.js`（21 MB）经 javascript-obfuscator 混淆（字符串表 + 解码函数），字段名与常量仍可读；渲染层 chunk 未混淆（注意：`data-surface` 相关逻辑在未抽取的 `DuYyTcRQ.js` 入口中）。

---

## 一、主窗口信息架构

### 1.1 窗口壳：「单 HTML + 多 Surface 路由」的自绘壳

| 事实 | 证据 |
|---|---|
| 全应用只有 3 个 HTML 入口：`index.html`、`dataDirectoryProgress.html`、`hostedPresentationMenu.html` | asar 内 `out/renderer/*.html` 全量清单（其余 Surface 复用 `index.html?surface=`） |
| 主壳为 frameless 自绘标题栏；`index.html` **刻意不写 `<title>`**（注释：一旦带标题 Electron 会忽略各窗口 title，所有产品/独立窗口会共用同一名字） | `index.html:11` 注释；`:188` 起样式 |
| 启动屏常驻最顶层（`z-index:2147483647`），整屏可拖拽（`-webkit-app-region:drag`），72px 蒙版 Logo + 扫光/呼吸动画（2.15s），`role="status" aria-label="正在恢复登录状态"`，隐藏时 120ms 淡出 | `index.html:36-51`、`:53-63`、`:148-168`、`:194` |
| 启动屏模板 Logo 资源 | `index.html:55` → `./assets/qoder-loading-line-Bq9ip4M2.svg`（268 KB） |
| CSP `frame-src` 白名单暴露内嵌 Surface 来源：`http://127.0.0.1:*`、`https://test.qoder.ai`、`qoder.sh`、`qoder.com`、`qoder.com.cn`（含子域）、`https://*.imm.aliyuncs.com`（阿里云 IMM WebOffice 预览） | `index.html:8` |
| 主窗口框架按平台分派：**win32** = `titleBarStyle:hidden + frame:false + thickFrame:true + titleBarOverlay:{color,height:40} + autoHideMenuBar`；**darwin** = `vibrancy + visualEffectState + titleBarStyle + trafficLightPosition {x:16,y:12} 或 {x:16,y:16}`；**linux** = 仅 titleBarStyle | `electronMain.js @18819192`（函数 `TYf(platform)`）；常量 `HMx=40` @18817954、`UV=backgroundColor` |
| ⇒ Windows 标题栏由应用自绘，高度 **40px**，右侧窗口按钮由系统 `titleBarOverlay` 绘制在同一 40px 带内 | 上两条交叉推断 |

### 1.2 主窗口尺寸（已确认常量）

```js
// electronMain.js @23193
QF = { login:    {width:690,  height:446, minWidth:690, minHeight:446},
       workbench:{width:1320, height:800, minWidth:720, minHeight:540} };
// electronMain.js @20748288（openCurrentViewInNewWindow 场景）
m1x = {width:900, height:700, minWidth:320, minHeight:400}
```

- 主工作台默认 **1320×800**，最小 **720×540**，可缩放（`resizable`）；登录态窗口 **690×446 固定**（min=max）。
- **推断**：`m1x`(900×700，min 320×400) 为 `openCurrentViewInNewWindow`（命令 `workbench.action.openCurrentViewInNewWindow`）打开的「当前视图独立窗口」。

### 1.3 一级区域划分（A/B 双区 + 三栏）

渲染层布局被显式命名为「layout region」，常量与 DOM 属性成套出现：

```js
// S__Wc8-4.js @1645464
LAYOUT_A1_HEADER_REGION  = "A1-HEADER";
LAYOUT_A1_CONTENT_REGION = "A1-CONTENT";
LAYOUT_B_HEADER_REGION   = "B-HEADER";
LAYOUT_B_CONTENT_REGION  = "B-CONTENT";
```

```html
<!-- S__Wc8-4.js @1654441 / @1656640 -->
<aside data-layout-region="a" class="…flex size-full flex-col … rounded-md">   <!-- 左侧栏 -->
  <div data-layout-header="a" data-layout-region-part="A1-HEADER" class="flex h-10 …px-3"> ← 40px 头部
  <motion.div data-layout-sidebar-content data-layout-region-part="A1-CONTENT" style="width:N0">
</aside>
<main data-layout-region="b" class="…flex-1 flex-col …bg-bg-layout">              <!-- 主区 -->
  <header data-layout-header="b" data-layout-region-part="B-HEADER" class="flex h-10 …pl-2 pr-3">
  <div data-layout-content="b" data-layout-region-part="B-CONTENT">
</main>
```

```
┌────────────────────────────────────────────────────────────────────────────┐
│ 自绘标题栏 40px（h-10）：[← → 前进后退] [侧栏开关] …… 拖拽区 …… [窗口控制/账户] │
├───────────────┬──────────────────────────────────────────┬─────────────────┤
│ 区 A（aside） │ 区 B（main）                              │ 区 B2（右栏）    │
│ 左侧栏        │ ┌ B-HEADER 40px（工作区 Tab / 地址栏）┐   │ 可折叠           │
│ 默认 248px    │ ├ 会话时间线（max-w-820 / 768 居中）┤   │ 默认 280px       │
│ 最小 208px    │ ├ 产物预览 / 浏览器 / Review / 终端  ┤   │ 抽屉 620px       │
│ 可拖拽/可折叠  │ └ Composer（底部固定）              ┘   │ （Issue Drawer） │
└───────────────┴──────────────────────────────────────────┴─────────────────┘
```

| 区域 | 尺寸/规则 | 证据 |
|---|---|---|
| 标题栏 | 高 **40px**（`h-10`）；窗口控制区：native/preview 时预留 `w-[72px]`；Windows 用 `window-controls-overlay`（`env(titlebar-area-x/width)`）；macOS 预留 `reservedInlineStart:88`，Linux `reservedInlineEnd:104` | `S__Wc8-4.js @1646339`（`data-window-controls` + `w-[72px]`）、`@1551307`（`WINDOW_CONTROLS_OVERLAY_SAFE_LEFT/WIDTH`）、`gtdG4YpP.js @12012751`（平台 `mv2()`） |
| 左侧栏 | `ResizablePanel` 可折叠：`defaultSize`、`minSize`、`collapsedSize:0`、`collapsible:true`、`groupResizeBehavior:"preserve-pixel-size"`；业务参数 `minSidebarSize:208, defaultSidebarSize:248` | `S__Wc8-4.js @1654441`；`gtdG4YpP.js @15917500` |
| 左栏内容 | 顶部固定：新建任务（`nav.newChat` = 「新的任务」）、搜索、模式切换（编程/通用）；下面按「工作目录」分组挂「置顶/最近任务」；可自定义排序与拖放（`data-sidebar-layout-item`、`data-sidebar-placement="primary｜secondary｜more"`、`data-sidebar-drop-group`） | `gtdG4YpP.js @6871690`、`@7687725`；`BkeoGa4m.js @183901`（i18n） |
| 主区 B | `main[data-layout-region=b]`；会话内容限宽 `max-w-[820px]`（page 形态）或 `max-w-[768px]`（新任务）/`max-w-[924px]`（非空会话） | `i18n_ia.txt` 摘录：`max-w-[820px]`、`max-w-[768px]`、`max-w-[924px]` 上下文 |
| 右栏 B2 | 侧栏/高亮面板 **280px**（`animate:{width:280}` + `w-[280px]`）；Issue 抽屉 **620px**（`w-[620px] max-w-full`）；高亮浮层 `w-[280px]` | `S__Wc8-4.js`/`gtdG4YpP.js` 中 `data-chat-session-region` 与 `w-[280px]`、`w-[620px]` 上下文；`i18n_ia.txt` |
| 会话三栏 | 对话区 `flex-1` + 右侧 workspace 面板（文件预览/浏览器/Review/终端 Tab，`data-chat-session-workspace-kind`：terminal/preview…）；全屏态 `data-chat-session-workspace-fullscreen` | `gtdG4YpP.js` `data-chat-session-region` 上下文、`data-chat-session-workspace-tab-shell` |
| 窗口控制按钮 | `sm`：root `h-6 squircle-6`、regular `w-[46px]`、extended `w-[68px]` | `S__Wc8-4.js @1551442` |

> **未确认**：是否还存在「C 区」/底部全局状态栏（`statusBar` 标识符出现 26 次，但未定位到独立底部栏组件；底部区域内嵌于 Composer 的 `data-chat-composer-status-banner/status-shell`）。

---

## 二、Surface 清单

全部 Surface 的装配方式已在渲染入口中确认：`index.html?surface=<id>`，入口按 query 设置 `document.documentElement.dataset.surface=<id>`，再动态 import 对应 chunk：

```js
// out/renderer/assets/DuYyTcRQ.js @137327
const Tt = new URLSearchParams(window.location.search).get("surface");
Rr=Tt==="first-launch-onboarding-overlay", ma=Tt==="onboarding-role-reveal-demo",
xa=Tt==="quick-note-window", ya=Tt==="live-voice-overlay", va=Tt==="desktop-pet",
ba=Tt==="dynamic-island", wa=Tt==="companion-activity";
sr = !(Rr||ma||xa||ya||va||wa||ba);        // sr=true → 主工作台
… document.documentElement.dataset.surface = Tt;
```

Surface → 渲染 chunk 映射（`DuYyTcRQ.js @138339` `Bc()`）：

| # | Surface | 形态 | 唤起方式 | 关键尺寸/布局 | 层级 | 证据 |
|---|---|---|---|---|---|---|
| 1 | **Workbench 主窗口** | 主窗口（frameless+40px 自绘标题栏） | 应用启动 / 托盘「打开主窗」 | 1320×800，min 720×540；A(208/248) + B + B2(280) | 普通层 | `electronMain.js @23193`；layout 常量同上 |
| 2 | **登录（login）** | 独立窗口（推断，与主窗同壳） | 首次启动 / 未登录 / 账号失效 | 690×446，min=max（固定） | 普通层 | `QF.login` @23193；i18n `onboarding.login.*` |
| 3 | **Dynamic Island** | OS 级置顶悬浮条（透明、无边框） | 常驻（Agent 运行/待批准/待回答时展开）；偏好可开关 | 面板 `max-width:calc(100% - 24px)`；badge 高 22px；choice 最小高 48px；共用宠物锚点 20×20；两种模式 `island` / `notch` | `alwaysOnTop`、`skipTaskbar` | `index.html?surface=dynamic-island`；`DynamicIslandPanel-*.css`（`.dynamicIslandPanel[data-mode=notch]`、`.dynamicIslandBadge[data-status=…]`）；preload `getDynamicIslandPreferences/updateDynamicIslandPreferences` |
| 4 | **Desktop Pet** | OS 级桌面精灵窗（透明、无边框、可拖） | 设置开启（`desktopFeatures.desktopPet`）；常驻桌面 | 基准精灵 **128px × 尺寸百分比**（取偶）+ 48px 工具栏 → 默认 128×176；窗口默认锚点右下 `(屏宽-120, 屏高-48)`；语音态 `scale(.72)` 淡出 | `alwaysOnTop`+`skipTaskbar`+`focusable:false`+`type:'toolbar'`（Win） | `electronMain.js @7762689`（`t0f=128, Ryx=48`、`c0f(percent)`、`sf0/default`、`rR/s0f` 贴边）；`DesktopPetSurface-*.css`（`#desktop-pet-root`、`data-switching-to-voice`)；`DtgWMrtR.js` |
| 5 | **Live Voice Overlay** | 全屏透明浮层 | 语音会话开始（宠物/主窗触发） | 覆盖整屏；数据面 `phase/caption/muted/microphoneDisabled/captureActive/userSpeechActive/volume/placement` | `alwaysOnTop` + `focusable:false` + `skipTaskbar` + macOS `visibleOnFullScreen` | `electronMain.js @4118106`、`@11898270`（voiceSessionId/audioStopped/ending）；`LiveVoiceOverlay-*.css` |
| 6 | **Quick Note 窗口** | 竖版便签窗（透明、无边框、可缩放） | 全局快捷键 `openQuickNoteShortcut` / 菜单 | **400×720**，min **320×600**，max **480×800**；靠光标/编辑器右下贴边（右下 32px 边距）；头部 40px 自绘拖拽区；macOS 红绿灯 `{x:20,y:16}` | `alwaysOnTop` + `skipTaskbar` | `electronMain.js @18870608`（`f=400,a=720`、`TQ/kQ/Xv0/Rv0` 常量、`trafficLightPosition`）；`Br-_4iXE.js`（`data-quick-note-window-header` `h-10 … [-webkit-app-region:drag]`）；`QuickNoteWindow-*.css` |
| 7 | **Companion Activity** | 屏幕底部气泡栈浮层 | 宠物/AI 活动通知；回复或展开 | 根容器 `display:flex; flex-direction:column; justify-content:flex-end; gap:8px`；气泡折叠 **68px** / 展开 **188px** | 透明、置顶 | `index.html?surface=companion-activity`；`CompanionActivitySurface-*.css`（`#companion-activity-root`）；`S__Wc8-4.js @1675579`（`h-[188px]`/`h-[68px]`、`data-slot="desktop-pet-activity-bubble"`） |
| 8 | **First-launch Onboarding Overlay** | 覆盖主窗的引导浮层 | 首次启动（设置项 `firstLaunchOnboardingEnabled` 可复现） | 全窗透明；内容含信封/身份卡（卡 240×280；场景卡 430×180/244）；跳过按钮 `right:max(130px,…); top:60px` | 覆盖层，透明 | `index.html?surface=first-launch-onboarding-overlay`；`FirstLaunchOnboardingSurface-*.css`、`OnboardingOverlayDemo-*.css`（`[data-onboarding-envelope-body] left-48 top-104 h-280 w-240`、`[data-onboarding-table-card] w-[430px] h-[180px]`） |
| 9 | **Onboarding Role Reveal Demo** | 动效演示 Surface | 设置内「新用户角色引导动效 Demo」（i18n `demoLabel`） | 同信封/卡片动效；独立 chunk `5l2WzCbv.js` | 覆盖层 | `DuYyTcRQ.js @137327`；`BkeoGa4m.js @251117`（`onboarding.demoLabel:"新用户角色引导动效 Demo"`） |
| 10 | **Hosted Presentation Menu** | 独立 HTML 小窗（透明菜单锚点） | 托管演示（presentation）打开时的悬浮菜单 | 锚点 `position:fixed; left:16px; top:16px; width/height:2px`（菜单由锚点定位） | 透明、无滚动 | `hostedPresentationMenu.html:2`（`<html data-surface="hosted-presentation-menu">`）、`hostedPresentationMenu-*.css`；`BQNFh54O.js` |
| 11 | **Data Directory Progress** | 独立 HTML 迁移进度窗 | 更改数据目录 → 迁移 | 独立 CSP：`default-src 'self'; connect-src 'none'; frame-src 'none'`；展示 `preparing / stoppingTasks / completed / cleanup` 阶段 | 普通层（迁移期间主窗退出） | `dataDirectoryProgress.html:6`、`dataDirectoryProgress-*.css`（203 KB，独立 Tailwind 产物）、`dataDirectoryProgress-*.js` |
| 12 | **Artifact Preview（独立窗口）** | 产物预览窗（推断为独立 BrowserWindow） | 「新窗口查看」产物 | 标题动态设置 `document.title = t("chatSession.artifactPreview.windowTitle")`；内容 `data-slot="artifact-preview-*"`，头部 40px（`h-10`）；`body:has([data-artifact-preview-window])` 有专门样式 | 普通层，窗口尺寸 **未确认** | `gtdG4YpP.js @12012751`、`@3306806`（`data-slot":"artifact-preview-surface"`）；`FirstLaunchOnboardingSurface-*.css`（`body:has([data-artifact-preview-window])`） |

> **推断（窗口尺寸归属）**：`electronMain.js @7762711` 定义 `sf0={width:180,height:200}` 与 `n0f={width:300,height:252}`，同一悬浮窗管理器按条件返回二者之一，并做「贴右下/贴底居中/贴光标」定位。该常量块与 Desktop Pet 的 `c0f()`（128px sprite）相邻但相互独立，**最可能属于 Dynamic Island 的收起/展开两档窗口尺寸**——但未拿到 Surface↔class 的直接绑定，故标为推断。

---

## 三、导航模型

### 3.1 一级导航（左侧栏，固定顺序 + 可自定义）

```js
// gtdG4YpP.js @6871690
Dx = {
  newChat:    {defaultOrder:0, placement:"primary",   customizable:false},                 // 新的任务
  chats:      {defaultOrder:1, placement:"primary",   customizable:true, requiresCloudCollaboration:true, requiresExperimentalAgentChat:true},
  myWork:     {defaultOrder:2, placement:"primary",   customizable:true, requiresDeveloperAttention:true}, // 需要我
  projects:   {defaultOrder:3, placement:"primary",   customizable:false, requiresIssues:true},
  discussion: {defaultOrder:4, placement:"primary",   customizable:false, requiresDiscussions:true},
  search:     {defaultOrder:5, placement:"primary",   customizable:true},
  automation: {defaultOrder:6, placement:"secondary", customizable:true},
  extensions: {defaultOrder:7, placement:"secondary", customizable:true},
}
```

中文文案（`BkeoGa4m.js @183901`，`nav` 命名空间）：**新的任务 / 任务 / 需要我 / 项目 / 讨论 / 搜索 / 自动化 / 扩展 / 设置**；`primary:"主导航"`、`secondary:"辅助导航"`；`collapseSidebar:"收起左侧栏"`、`goBack/Forward`。

- 入口可拖拽重排，分三档 placement：`primary`、`secondary`、`more`（更多），非 customizable 的（newChat/projects/discussion）锁定位置。
- 功能开关决定可见性：`requiresCloudCollaboration / requiresIssues / requiresDiscussions / requiresDeveloperAttention / requiresExperimentalAgentChat`。

### 3.2 路由与壳层（Workbench Surface Registry）

```js
// gtdG4YpP.js @14574337（collaboration surface 注册）
[{id:"attention",    routeKinds:["attention"],    shell:"framed"},
 {id:"clarification",routeKinds:["clarification"],shell:"framed"},
 {id:"projects",     routeKinds:["projects"],     shell:"framed"},
 {id:"project",      routeKinds:["project"],      shell:"framed"},
 {id:"issue",        routeKinds:["issue"],        shell:"framed"},
 {id:"discussions",  routeKinds:["discussions"],  shell:"framed"},
 {id:"discussion",   routeKinds:["discussion"],   shell:"framed"},
 {id:"automation",   routeKinds:["automation"],   shell:"framed"}]
// @14844245：extensions / app-plugin（framed）
// @15953342：settings（shell:"standalone"）、runtime-profiles、runtime-environment-create（framed）
```

⇒ 三类壳：`framed`（带 A/B 布局外壳）、`standalone`（设置类，独立壳，无左栏布局）、`chatSession`（会话，属于 framed 的一种）。

### 3.3 层级深度与返回/面包屑规则

| 层级 | 内容 | 证据 |
|---|---|---|
| L1 | 左侧栏 8 个入口（任务/需要我/项目/讨论/搜索/自动化/扩展/设置） | 3.1 |
| L2 | 列表页（任务列表、项目列表、讨论列表、归档列表） | `gtdG4YpP.js @15105739`（已归档：任务/项目/讨论 三个 Tab） |
| L3 | 详情（会话、项目详情、Issue 详情、讨论详情） | route kinds `chatSession/project/issue/discussion` |
| L4 | 详情内右栏 B2 Tab（文件预览/浏览器/Review/终端）+ 抽屉（Issue Drawer 620px） | `data-chat-session-workspace-kind`、`data-layout-region="b"`、`w-[620px]` |
| 返回 | 顶部 `LayoutChrome`：后退/前进按钮 + 快捷键 + `canGoBack/canGoForward`；路由栈与 lastRoute 持久化 | `S__Wc8-4.js @1646339`；`gtdG4YpP.js @3616063`（`workbench.navigation.route/historyState`、`persistLastRoute`） |
| 面包屑 | 会话头部地址栏（`data-chat-session-b2-content-header-address`）+ 工作区 Tab 溢出滚动；**未发现传统多级面包屑** | `i18n_ia.txt` 中 `data-chat-session-b2-content-header` 上下文 |

### 3.4 设置信息架构（standalone shell 内分组）

`gtdG4YpP.js @15905767` + `@15902056` 的设置项 id：`general`(account→profile、collaboration→general、collaboration-agent→agents)、`models`(BYOK)、`agents`(Beta)、`squads`(Beta)、`import`(数据导入)、`coding`、`installed`(扩展管理)、`connections`、`device-connections`、`hooks`、`memory`、`pet`、`git`、`worktrees`、`mobile`、`voice`、`browser-control`、`developer`、`runtimes`；设置页带搜索索引（`data-settings-search-id`）。

### 3.5 命令与快捷键模型

`gtdG4YpP.js @4783260` 的命令 id 命名空间 `workbench.action.*`：`newWindow / openCurrentViewInNewWindow / newChat / openSettings / navigateBack / navigateForward / toggleProductMode / switchChatSession / openFeedback / openQuickNote / findInConversation / togglePlanMode / toggleLeftSidebar / toggleRightSidebar / openRightSidebar / closeRightSidebar / openWorkspaceExplorer / openWorkspaceBrowser / openWorkspaceReview / openTerminal`。
主进程 i18n 键证实同一套全局快捷键存在：`openQuickNoteShortcut`、`toggleLeftSidebarShortcut`、`toggleRightSidebarShortcut`、`openChatSessionWorkspaceExplorer/Browser/Review/TerminalShortcut`、`toggleChatSessionWorkspaceFullscreen`（`electronMain.js @9293126`）。

---

## 四、关键流程界面

### 4.1 首次启动 Onboarding（已确认全链路）

**步骤模型**：`角色选择 → 数据导入 → 领取卡片`（`stepCarouselAriaLabel:"Onboarding 步骤"`、`roleStepLabel/importStepLabel/cardStepLabel`，`BkeoGa4m.js @251117`）。

1. **登录前置**：欢迎页 `欢迎你，我的朋友 👋🏻` + `新一代 Agentic Coding 平台 / 借助最先进的人工智能创造了不起的事物 / 你只需要 Qoder` + CTA `立即登录`；`restoring:"正在恢复登录状态..."`、`waiting:"等待浏览器确认"`、`copyLink:"无法登录? 复制登录链接"`、`close:"关闭登录弹窗"` → 浏览器 OAuth 回跳（preload `login / cancelLogin / releaseLoginWait / logout / updateAuthProfileOverlay / authStateChanged`）。
2. **演示场景**（登录弹窗背后播放）：GitHub 上下文卡、Figma 上下文卡、Plan 卡、生成结果预览、分析表格、文件卡、loader（`OnboardingOverlayDemo-*.css` 的 `[data-onboarding-*]` 选择器：`github-card / figma-card / plan-card / generated-preview-card / table-card / file-card / loader-icon / loader-bar / user-bubble`）；场景提示词 `在我们项目中实现` → `构建团队分析看板` → `现在，把它变成你的。`；配乐/音效 4 个 wav（`onboardingOpening/onboardingTyping/onboardingSend/onboardingFinalSend`）。
3. **角色选择**：`哪些角色最符合你的工作？`（`roleQuestion`）；完成态 `你的 {{role}} 工作区已准备好`。
4. **数据导入**：标题 `将你的工作带入 Qoder`，来源 = `任务记录`、`定时任务`、`Skill、MCP 连接器与插件`、`记忆`；提示 `数据会在后台静默导入，请不要关闭客户端。`；每项有 `暂不可用` 态；`上一步` 可回退。
5. **身份卡（情感化收尾）**：`限定身份卡` / `从现在开始 新的 Qoder 旅程` / `WELCOME QODER`、`BOARDING_PASS`、`JOINED TIME`、`身份：{{role}}`；信封开门 + 卡片前推动效（参数名外露：`doorAngle/hoverWobbleLift/cardLiftDistance/cardPushGap`）；可 `跳过/重置/继续`。
6. **跳过与重放**：`settings` 中 `getFirstLaunchOnboardingEnabled/setFirstLaunchOnboardingEnabled` 可重开引导；`onboarding-role-reveal-demo` Surface 用于单独演示动效。

### 4.2 登录

- 独立窗口 **690×446**（min=max），与主工作台分离；Splash 文案 `正在恢复登录状态`（`index.html:194`）→ 登录态恢复失败再进登录页。
- 登录中状态文案：`正在恢复登录状态...` / `等待浏览器确认` / `无法登录? 复制登录链接` / `登录链接已复制`。
- 账号体系入口在标题栏最右 `AccountMenuTrigger`（参数 `username/plan/avatarLetter/avatarImage/avatarNotification/avatarColors/showUpdateButton/showFilterButton/settingsButtonLabel`，`S__Wc8-4.js @1657932`）。

### 4.3 数据目录初始化与迁移

- 设置入口文案（`dataDirectory` 命名空间）：`本地数据 / 数据位置 / 打开文件夹 / 更改位置… / 正在读取数据位置…`。
- 迁移确认弹窗（`variant:"compact", maxWidth:560`）：`迁移本地数据`，说明 `应用将保存状态并退出，完成数据复制和校验后重新启动。原位置保留恢复副本。`，字段 `迁移到` + `待迁移数据 {{size}} MB`，按钮 `取消迁移 / 迁移并重启`，前置条件 `先结束 App 中正在运行的任务…目标必须是本机 NTFS 磁盘上的空文件夹。`
- 迁移执行：**独立窗口 `dataDirectoryProgress.html`**（CSP `connect-src 'none'`，无网络能力），进度经文件/进程间通道上报（`out/main/dataDirectoryProcess.js`），阶段 `正在准备迁移…` → `正在停止任务并准备迁移…` → 完成后自动重启。
- 后置：`数据已迁移到新位置…` + `清理旧副本…（移至回收站）`；异常态：`上次迁移未完成，正在使用原位置的数据`、`应用未能完成任务收尾`、以及 `errors.unavailable/busy/invalidTarget/migrationFailed`。
- preload API：`getDataDirectory / selectDataDirectory / migrateDataDirectory / openDataDirectory / cleanupDataDirectory`。

### 4.4 更新

- 主进程存在完整增量更新链路：`autoUpdater`（Electron）、`prepareWindowsNsisUpdateCache`、`prepareWindowsFastUpdateCandidate`、`downloadWindowsFastUpdateArchive`、`finalizeWindowsFastUpdateCandidate`、`handoffWindowsFastUpdate`，并有 `fast-update` 资源目录（`electronMain.js @4117884` 附近 + `resources/fast-update`）。
- 账号菜单支持 `showUpdateButton/onUpdateClick`（标题栏更新按钮）。
- **未确认**：更新弹窗/更新页的具体布局与尺寸（渲染层 update 文案未在本次抽取范围内定位）。

### 4.5 空状态 / 错误态

- 空态家族（i18n 直接可证）：`暂无本地智能体`、`暂无智能体`、`暂无云端技能`、`暂无云端连接器`、`还没有已归档项目`、`暂无描述`、`未关联工作区`、`暂无来源`、`暂无关键成员` 等；通用空态组件为 `EmptyState`（`icon/title/description/bordered` 参数，`gtdG4YpP.js @14844245` 附近）。
- 错误态：`重试`（全量中文文案中出现 **111 次**，最高频）、`这轮回复失败`（23 次）、`连接失败/执行失败/任务执行失败`、`配额已用尽`、`外部模型服务暂不可用`、`文件不存在或无法访问`；错误边界属性 `data-render-error-boundary`（3 处）。
- 情绪化插画资源（876 个 `.webp`，文件名可反推场景）：`quickNoteEmptyState.webp`、`quickNoteOnboardingFirstNote.webp`、`voiceFirstUseSticker.webp`、`desktopPetFirstUseSticker.webp`、`onboardingWallpaper.webp`、`empty*.webp`、`failed*.webp`、`duck*.webp`、`dog/crocodile/gorilla/bird.webp`（宠物形象）、`voice_idle_00000..N.webp`（语音待机逐帧动画）；SVG 侧有成长/纪念体系：`activeDays7/30/100Sticker.svg`、`qoderAnniversary365Sticker.svg`、`profileSticker*.svg`、`userCardDuck.svg`、`userCardSilverDuck.svg`、`qoderPioneerSticker.svg`。⇒ 空态/失败态被系统性地「插画化」，而非纯文字。

---

## 五、设计意图观察

1. **「Agent 工作台」而非「IDE」的信息架构**：左侧栏没有「文件树」，第一层是任务/项目/讨论（人的工作对象），工作区与文件树被降级到「任务内部的工作目录 + 右栏 workspace Tab」。证据：导航 8 项（`gtdG4YpP.js @6871690`）中无 explorer；`workspaceExplorer/Terminal/Review` 全部是 `chatSession.action.*`（会话内命令）。
2. **Dynamic Island = 把 Agent 状态提升到 OS 层**：形态刻意模仿系统灵动岛（`data-mode="island"` / `"notch"` 两套排版，notch 模式中间预留 192px 刘海位），状态用徽章色编码（permission/waiting=橙、failed/interrupted=红、completed=蓝、userQuestion=青、working=绿）；岛内可直接回答提问/批准权限/选择选项（`dynamicIslandChoice` 最小高 48px、`dynamicIslandAnswerField` 高 32px），让「人在别处」时也能处理 Agent 请求，避免切回主窗的心智成本。
3. **Desktop Pet = 拟人化陪伴 + 低摩擦入口**：128px 精灵 + 尺寸百分比可调（设置 `getDesktopPetSizePercent`）；双击 `openWorkbench`、右键弹上下文菜单、悬停出工具栏（语音/活动气泡开关）、语音时自动缩小让位（`transform:scale(.72)`）；还可在 Dynamic Island 内以 20px 小头像复用同一只宠物（`.dynamicIslandSharedPet`），形成「岛—桌面—主窗」三层同一人格。
4. **Companion Activity 把通知变成可回复对象**：气泡栈贴屏幕底部、`gap:8px`，折叠 68px/展开 188px，内嵌 reply 输入（`desktopPet.activity.replyInput`），把「通知」升级为「对话」。
5. **Quick Note 是打断成本最低的全局入口**：竖版 400×720 便签窗、置顶、贴光标/贴编辑器边、自定义窗口头（`data-quick-note-window-header` 40px + 三圆假红绿灯 `size-3`），配合 `openQuickNoteShortcut`，服务「随手记」而非长文写作。
6. **Onboarding 用「演示场景 + 身份卡」做价值前置与情感留存**：登录前先跑 GitHub/Figma/计划/生成表格的完整 Agent 演示（有音效、有壁纸），登录后领取限定身份卡（`WELCOME QODER / BOARDING_PASS / JOINED TIME`），把冷启动变成仪式感；卡片与个人资料页的成长徽章（activeDays 7/30/100、周年 365）构成同一套留存体系。
7. **布局规范稳定在「208/248 + 内容限宽 + 280 右栏」**：可拖拽宽度仅左栏与右栏，内容区用 `max-w-[768/820/924]` 保证长行可读；标题栏统一 40px 与 Windows `titleBarOverlay.height=40` 对齐，窗口按钮由 OS 绘制以避免自绘窗口控制的一致性问题。
8. **安全边界按 Surface 收敛**：主窗 CSP 仅放行受控内域与 Office 预览域名；独立 Surface 用更严 CSP（`dataDirectoryProgress` 甚至 `connect-src 'none'`），说明这些窗口按「最小权限」单独构建，而非共用主窗渲染进程。

---

## 附：证据文件索引

| 文件 | 用途 |
|---|---|
| `out/renderer/index.html` | 单页壳、CSP、启动屏 |
| `out/renderer/dataDirectoryProgress.html`、`hostedPresentationMenu.html` | 仅有的两个独立窗口 HTML |
| `out/renderer/assets/DuYyTcRQ.js` | 渲染入口：`?surface=` 路由 + Surface 动态 import 映射 |
| `out/renderer/assets/styles-eCOZTk0p.css`（396 KB）、`index-BFGCOCH4.css`（78 KB） | 全局设计系统 |
| `DynamicIslandPanel-*.css`、`DesktopPetSurface-*.css`、`CompanionActivitySurface-*.css`、`LiveVoiceOverlay-*.css`、`QuickNoteWindow-*.css`、`FirstLaunchOnboardingSurface-*.css`、`OnboardingOverlayDemo-*.css`、`dataDirectoryProgress-*.css`、`hostedPresentationMenu-*.css`、`DynamicIslandSurface-*.css` | 各 Surface 专属样式（`html[data-surface=…]` 前缀） |
| `out/main/electronMain.js` | 窗口尺寸常量（@23193）、标题栏策略（@18819192）、各 overlay 窗口配置（@4118106 / @11898270 / @18835872 / @18870608）、宠物尺寸算法（@7762689） |
| `out/preload/index.cjs` | Surface 侧 API：QuickNote / DesktopPet / DynamicIsland / 数据目录 / 登录 / 账号 |
| `out/renderer/assets/BkeoGa4m.js` | 中/繁/英/韩四套 i18n 字典（导航、Onboarding、DataDirectory 等） |
| `out/renderer/assets/gtdG4YpP.js` | 主 bundle：导航定义（@6871690）、路由注册（@14574337 等）、设置分组（@15905767）、命令 id（@4783260） |
| `out/renderer/assets/S__Wc8-4.js` | 布局骨架组件（`LayoutChrome`、`LAYOUT_*` 常量、标题栏安全区）、宠物/活动气泡 UI 组件 |
| `out/renderer/assets/*.webp`（876）、`*.svg` | 情绪/引导/成长类界面证据：空态、首次使用贴纸、宠物形象、身份卡、纪念徽章 |
