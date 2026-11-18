# Hyprland 配置修改指南（面向本地 AI）

> 本文件写给"要帮你改 Hyprland 配置"的 AI（也给人看）。
> 目标机器上 Hyprland **正在运行**，改错会导致快捷键失灵、窗口行为异常。
> 请严格按本文件的流程做，不要凭记忆写 Hyprland 配置。

## 目录

| 节 | 内容 | 什么时候看 |
|---|---|---|
| §0 | 给 AI 的硬性规则 | **每次动手前必看** |
| §1 | 机器与版本事实、配置目录 | 了解环境 |
| §2 | "想改 X 该动哪里"决策表 | 定位要改哪段 |
| §3 | Lua 配置语法速成（选项/类型/颜色/API/事件/flags） | 写代码前 |
| §4 | 16 个常见修改配方（R1–R16） | 直接抄改 |
| §5 | 改完怎么验证（reload/configerrors/查询/回滚） | **每次改完必做** |
| §6 | 常见陷阱 16 条 | 出问题先查这里 |
| §7 | 老语法 → Lua 对照表 | 参考网上教程时 |
| §8 | 交付前自检清单 | 收尾 |
| §9 | 参考文献 | — |
| §10 | 附录：`hyprlock.conf` / `hypridle.conf`（hyprlang 语法） | 改锁屏/空闲时 |

配套文件（同目录，按需查阅，不要一次性全读进上下文）：

- `AI-HYPRLAND-OPTIONS.md`：`hl.config()` 能设置的全部选项（按 category 分组，含默认值/范围）+ 本机当前值基线。
- `AI-HYPRLAND-DISPATCHERS-RULES.md`：`hl.bind` flags、dispatchers 全表、窗口/图层/工作区规则、选择器语法、显示器与动画配置、`hyprctl` 手册。

---

## 0. 先读这一节：给 AI 的硬性规则

1. **这是 Lua 配置，不是 hyprland.conf。** 主配置文件是
   `~/.config/hypr/hyprland.lua`，使用 `hl.*` 的 Lua API（Hyprland 0.5x 新配置体系）。
   网上 90% 的 Hyprland 教程是旧的 hyprlang 语法（`bind = `、`windowrulev2 = `、
   `exec-once = `、`general { }` 大括号块），**在本机一律无效**。老语法对照见 §7。
2. **只改需要改的行。** 保留原有缩进（4 空格）、注释、中文注释、变量名和代码块顺序。
   不要重排整个文件，不要"顺手美化"。
3. **不确定的选项名必须查** `AI-HYPRLAND-OPTIONS.md`（同目录）。
   选项名是下划线风格：`tap_to_click`、`follow_mouse`、`natural_scroll`，
   **不是** `tap-to-click`。写错的选项会让整份配置加载失败。
4. **不确定的 dispatcher / 规则字段必须查** `AI-HYPRLAND-DISPATCHERS-RULES.md`（同目录）。
5. **不要动** `hyprpaper.conf`（由 `bing-wallpaper` 守护进程自动生成，改了会被覆盖）。
6. **不要删除启动段里的 `pgrep` / `flock` 防护**，否则 `hyprctl reload` 后会出现重复进程
   （多个 waybar、多个剪贴板监听）。
7. **一次只改一件事**，改完立即验证（§5）。多个改动一起上，出问题无法定位。
8. **改前备份**：`cp ~/.config/hypr/hyprland.lua ~/.config/hypr/hyprland.lua.bak.$(date +%s)`
9. **输出格式**：给出「改了哪几行（旧 → 新）+ 完整替换块 + 验证命令」，
   不要只给一句"已修改完成"。
10. **无法验证的事要说明**。Hyprland 没在运行（`HYPRLAND_INSTANCE_SIGNATURE` 未设置）时
    `hyprctl` 不可用，此时只能做静态检查（Lua 语法），要明确告知用户。

---

## 1. 机器与版本事实

| 项目 | 值 |
|---|---|
| 发行版 | Arch Linux |
| Hyprland | 0.57.2-1（2026-11-09 构建，commit 11cbc6c） |
| 配置体系 | **Lua**（`hl.config` / `hl.bind` / `hl.window_rule` …），配置文件 `hyprland.lua` |
| 显示器 | 单屏 `DP-1`，27" 4K，`scale = 2` → 逻辑分辨率 1920x1080 |
| 布局 | `dwindle`（另有 master / scrolling / monocle 可选） |
| 主修饰键 | `SUPER`（`local mainMod = "SUPER"`） |
| 终端 / 文件管理器 / 启动器 | `kitty` / `nautilus` / `rofi -show run` |

已安装的相关组件：`waybar`、`rofi`、`hyprlock`、`hypridle`、`hyprpaper`、`hyprsunset`、
`hyprpolkitagent`、`swaync`、`cliphist`、`fcitx5`、`xdg-desktop-portal-hyprland`、
`hyprcursor`、`aquamarine`、`kitty`、`nautilus`。

### 配置目录里有什么

| 文件 | 作用 | 能不能改 |
|---|---|---|
| `~/.config/hypr/hyprland.lua` | **主配置**：显示器、启动项、环境变量、外观、动画、输入、快捷键、窗口/图层规则 | ✅ 主要改这个 |
| `~/.config/hypr/hyprlock.conf` | 锁屏界面（hyprlang 语法，独立程序） | ✅ 改锁屏外观/时间格式 |
| `~/.config/hypr/hypridle.conf` | 空闲行为（息屏/锁屏/挂起，hyprlang 语法） | ✅ 改超时时间 |
| `~/.config/hypr/hyprpaper.conf` | 壁纸，由 `bing-wallpaper` 自动写 | ❌ 不要手改 |
| `~/.config/hypr/bing-wallpaper` | 必应壁纸守护进程（Python） | ⚠️ 谨慎 |
| `~/.config/waybar/*` | 状态栏及其脚本：`wallpick` `screenshot` `clipmenu` `night` `record` `popup.py` `wsdaemon` `lockweather` | ✅ 快捷键调用的就是这些 |

> 注意：`hyprlock.conf` / `hypridle.conf` / `hyprpaper.conf` **不是 Lua**，
> 是各自的 hyprlang 配置，语法完全不同（`general { }`、`bindings { }`）。别混用。

---

## 2. 想改 X，该动哪里（决策表）

| 想改什么 | 改哪里 | 可 grep 的关键字 |
|---|---|---|
| 加快捷键 / 改快捷键 | `hyprland.lua` 的 `KEYBINDINGS` 段 | `hl.bind(` |
| 窗口浮动/固定工作区/去边框 | `WINDOWS AND WORKSPACES` 段 | `hl.window_rule(` |
| 状态栏/启动器模糊 | 同上的图层规则 | `hl.layer_rule(` |
| 间距、边框、圆角、透明度、阴影、模糊 | `LOOK AND FEEL` 段的 `hl.config({ general/decoration })` | `gaps_in` `rounding` `blur` |
| 动画快慢、弹性 | `hl.curve(` / `hl.animation(` | `spring` `bezier` |
| 键盘布局、鼠标灵敏度、触摸板 | `INPUT` 段 | `kb_layout` `hl.device(` |
| 开机启动的程序 | `AUTOSTART` 段的 `hl.on("hyprland.start", ...)` | `hl.exec_cmd(` |
| 显示器分辨率/缩放/位置 | `MONITORS` 段 | `hl.monitor(` |
| 环境变量（输入法、缩放、光标） | `ENVIRONMENT VARIABLES` 段 | `hl.env(` |
| 工作区专属行为（无边框/固定到屏） | 新增 `hl.workspace_rule(` | `workspace_rule` |
| 某个布局的参数 | `hl.config({ dwindle/master/scrolling })` | `preserve_split` `new_status` |
| 锁屏外观 | `hyprlock.conf` | `background {` `input-field {` |
| 多久自动锁屏/息屏 | `hypridle.conf` | `timeout` `on-timeout` |

---

## 3. Lua 配置语法速成

### 3.1 设置选项：`hl.config`

```lua
-- 写法 A：嵌套表（推荐，可读性好）
hl.config({
    general = {
        gaps_in  = 3,
        gaps_out = 6,
        col = {
            active_border = { colors = { "rgba(33ccffee)", "rgba(00ff99ee)" }, angle = 45 },
        },
    },
})

-- 写法 B：点号全名（适合只改一个值、或在函数里改）
hl.config({ ["general.gaps_in"] = 3 })
```

规则：

- 多次调用 `hl.config` 会**合并**，不是覆盖整份配置。
- 同一个选项被设置多次时，**后写的生效**（"latest wins"）。
  所以新增一个 `hl.config` 块去覆盖前面的值是可以的，但为了可读性，
  改已有选项时优先改原来的那一行。
- 运行时改（不写进文件）：`hyprctl eval 'hl.config({ ["general.gaps_in"] = 0 })'`，
  **reload 后会恢复默认值**，只适合临时试参数。

### 3.2 数据类型

| 类型 | 写法 | 例子 |
|---|---|---|
| int | 整数 | `border_size = 1` |
| float | 小数 | `inactive_opacity = 0.95` |
| bool | `true` / `false` | `resize_on_border = true` |
| string | `"..."` / `'...'` / `[[...]]` | `layout = "dwindle"` |
| vec2 | `{x, y}` | `{20, 20}` |
| css_gaps | 整数，或 `{ top?, left?, right?, bottom? }` | `gaps_in = 3` / `{ top = 2, bottom = 2 }` |
| color | 见下 | `"rgba(33ccffee)"` |
| gradient | 单色，或 `{ colors = { c1, c2 }, angle = float }` | 见上 |
| font_weight | 100–1000，或 `thin/light/normal/medium/bold/...` | `bold` |
| table | `{ }` | `points = { {0.23, 1}, {0.32, 1} }` |

### 3.3 颜色写法（4 种都合法）

```lua
"#FAFC32"                    -- web 风格 RGB
"#FA3D7BFF"                  -- web 风格 RGBA
"rgba(57BBFFEE)"             -- 十六进制
"rgba(87,187,255,0.933)"     -- 十进制（逗号之间不要有空格）
"rgb(FF4410)" / "rgb(255,68,16)"
"0xeeb3ff1a"                 -- 老式 ARGB
```

### 3.4 字符串与正则的坑

- Lua 字符串里 `\` 是转义符。写正则 `\d` 必须写成 `"\\d"`，
  或用 Lua 长字符串 `[[^\d+$]]` 避免转义（**推荐**）。
- 选项名带点号时，`general.gaps_in` 在表里必须写成 `["general.gaps_in"]`，
  否则会被解析成嵌套表 `general = { gaps_in = ... }`（两者其实等价，但混用易错）。
- 键名/取值区分大小写：`layout = "dwindle"` ✅，`"Dwindle"` ❌。

### 3.5 常用 API 一览

| API | 作用 | 备注 |
|---|---|---|
| `hl.config({...})` | 设置配置项 | 见 3.1 |
| `hl.env("名", "值")` | 设置环境变量 | 必须在启动早期，reload 不重设 |
| `hl.monitor({...})` | 显示器 | 见 §4 R7 |
| `hl.bind(键, dispatcher, flags?)` | 绑定快捷键 | 返回 handle |
| `hl.unbind(键)` | 解绑 | 参数必须与绑定时**完全一致** |
| `hl.dsp.*` | dispatcher 对象 | **单独写不会执行**，必须给 `hl.bind` 或 `hl.dispatch` |
| `hl.dispatch(hl.dsp...)` | 立即执行 dispatcher | 在 `function()` 里用 |
| `hl.exec_cmd("cmd")` | 异步启动进程 | 自动 `sh -c`，不需要 `&`；不阻塞 |
| `hl.window_rule({...})` | 窗口规则 | 见 §4 R3/R4 |
| `hl.layer_rule({...})` | 图层规则（waybar/rofi 等） | `match = { namespace = "..." }` |
| `hl.workspace_rule({...})` | 工作区规则 | 见 §4 R10 |
| `hl.curve(名, {...})` / `hl.animation({...})` | 动画 | 见 §4 R6 |
| `hl.gesture({...})` / `hl.device({...})` | 手势 / 按设备输入 | 见 §4 R8/R11 |
| `hl.define_submap(名, fn)` + `hl.dsp.submap("名")` | 键位子模式 | 见 §4 R12 |
| `hl.on("事件", fn)` | 事件回调 | 事件表见 §3.7 |
| `hl.timer(fn, { timeout = 毫秒, type = "repeat" })` | 定时器 | 返回 handle，可 `:set_enabled()` |
| `hl.notification.create({ text=..., timeout=..., icon=... })` | 桌面通知 | 调试很好用 |
| `hl.get_active_window()` / `hl.get_windows()` / `hl.get_config("名")` … | 查询 | 完整列表见文档 |

### 3.6 什么时候必须写 `function()` + `hl.dispatch`

`hl.dsp.xxx(...)` 只是构造一个"待执行动作"，直接写在文件里**不会发生任何事**。
两种正确用法：

```lua
-- ① 交给 hl.bind（最常见）
hl.bind("SUPER + Q", hl.dsp.window.close())

-- ② 需要条件判断时，用函数 + hl.dispatch
hl.bind("SUPER + X", function()
    local w = hl.get_active_window()
    if w ~= nil and w.class == "kitty" then
        hl.dispatch(hl.dsp.window.float({ action = "toggle" }))
    else
        hl.dispatch(hl.dsp.window.pseudo())
    end
end)
```

> ⚠️ **回调里严禁阻塞**：不能 `os.execute`、`io.popen`、`sleep`、读 `wl-paste`、
> 发网络请求。回调跑在合成器的事件循环里，阻塞会让整个桌面卡死。
> 要跑外部命令就用 `hl.exec_cmd()`（异步）。

### 3.7 常用事件（`hl.on`）

| 事件 | 何时触发 | 回调参数 |
|---|---|---|
| `hyprland.start` | Hyprland 启动完成 | — |
| `hyprland.shutdown` | 退出前 | — |
| `config.reloaded` | reload 并生效后 | — |
| `config.unload` | 卸载配置前（保存状态用） | — |
| `window.open` | 窗口完成初始化（规则已应用） | window |
| `window.open_early` | 窗口已映射、**规则还没应用** | window |
| `window.active` | 焦点窗口变化 | window, reason |
| `window.title` | 标题变化 | window |
| `window.class` | class 变化 | window |
| `window.close` / `window.destroy` | 关闭 / 真正销毁 | window |
| `window.fullscreen` / `window.pin` / `window.urgent` | 状态变化 | window |
| `window.move_to_workspace` | 移到别的工作区 | window, workspace |
| `workspace.active` | 当前工作区变化 | workspace |
| `workspace.created` / `workspace.removed` | 创建 / 删除 | workspace |
| `workspace.move_to_monitor` | 工作区换屏 | workspace, monitor |
| `monitor.added` / `monitor.removed` / `monitor.focused` | 显示器插拔/焦点 | monitor |
| `layer.opened` / `layer.closed` | 图层出现/消失 | layer |
| `keybinds.submap` | submap 切换 | 名称字符串 |
| `input.keyboard.key` | 任意按键 | keycode, 时间戳, 0/1/2 |

### 3.8 绑定 flags 全表（`hl.bind` 第三个参数）

```lua
hl.bind("SUPER + Q", hl.dsp.exec_cmd("kitty"), { description = "打开终端" })
hl.bind("XF86AudioRaiseVolume", hl.dsp.exec_cmd("wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%+"),
        { locked = true, repeating = true })
```

| flag | 作用 |
|---|---|
| `locked` | 锁屏等 input inhibitor 生效时也触发（音量/亮度键常用） |
| `repeating` | 按住时重复触发 |
| `release` | 松开按键时触发 |
| `click` | 松开时若鼠标没移动超过 `binds:drag_threshold` 就触发 |
| `drag` | 松开时若鼠标移动超过阈值才触发 |
| `long_press` | 长按触发（可配合普通点击做两件事） |
| `mouse` | 鼠标绑定必须加 |
| `non_consuming` | 除了触发还继续把按键传给窗口 |
| `auto_consuming` | dispatcher 没成功时才把按键传给窗口 |
| `transparent` | 不会被其他绑定遮蔽 |
| `ignore_mods` | 忽略修饰键 |
| `description` | 给绑定写说明（`hyprctl binds` 可查） |
| `dont_inhibit` | 绕过应用对快捷键的抑制请求 |
| `submap_universal` | 在任何 submap 里都有效 |
| `device` | 按设备绑定（见 per-device 文档） |
| `allow_input_capture` | 客户端捕获输入时仍然生效 |

同一个键可以绑多条，**按书写顺序从上到下全部执行**（不是覆盖）。想停掉某条：
给 `hl.bind` 的返回值 `:set_enabled(false)`，或用 `hl.unbind(键)`——
`hl.unbind` 大小写敏感，会移除**它之前**注册的所有该键绑定。

---

## 4. 常见修改配方

> 所有示例都假设 `local mainMod = "SUPER"` 已经存在（`hyprland.lua` 第 289 行）。
> 新增的代码请**放在对应段落的末尾**，不要插进 `for` 循环或函数中间。

**改完之后请按这个格式回复用户**（示例：把终端快捷键从 kitty 换成 foot）：

```diff
--- a/hyprland.lua
+++ b/hyprland.lua
@@ -289,4 +289,4 @@
 local mainMod = "SUPER" -- Sets "Windows" key as main modifier

-hl.bind(mainMod .. " + Return", hl.dsp.exec_cmd(terminal))
+hl.bind(mainMod .. " + Return", hl.dsp.exec_cmd("foot"))
```

- **改了什么**：`SUPER + Return` 从启动 `kitty` 改为 `foot`（第 292 行）。
- **为什么**：用户要求默认终端换成 foot；没有动 `local terminal` 变量，避免影响其他引用。
  （若想全局换，应改 `local terminal = "kitty"` 那一行，而不是这条绑定。）
- **验证**：`hyprctl reload && hyprctl configerrors`（应为空）；按 `SUPER + Return` 看是否打开 foot。
- **回滚**：`cp hyprland.lua.bak.<时间戳> hyprland.lua && hyprctl reload`

### R1 加一个"启动程序"的快捷键

```lua
-- 放在 KEYBINDINGS 段
hl.bind(mainMod .. " + T", hl.dsp.exec_cmd("kitty -e btop"))
hl.bind(mainMod .. " + SHIFT + E", hl.dsp.exec_cmd("kitty -e yazi"))
```

注意：`hl.exec_cmd` 走 `sh -c`，所以 `~`、管道、`&&` 都能用。

### R2 改一个已有快捷键

直接把那一行的键名/dispatcher 改掉即可：

```lua
-- 旧：hl.bind(mainMod .. " + R", hl.dsp.exec_cmd(menu))
-- 新：
hl.bind(mainMod .. " + SPACE", hl.dsp.exec_cmd(menu))
```

如果不想删除原绑定（想保留但禁用），用返回的 handle：

```lua
local closeWindowBind = hl.bind(mainMod .. " + Q", hl.dsp.window.close())
closeWindowBind:set_enabled(false)   -- 禁用；true 恢复；:is_enabled() 查询
```

或者显式解绑（参数必须与绑定**逐字符一致**，含空格和大小写）：

```lua
hl.unbind(mainMod .. " + Q")
```

### R3 让某类窗口默认浮动 / 居中 / 指定大小

```lua
-- 放在 WINDOWS AND WORKSPACES 段
hl.window_rule({
    name  = "float-pavucontrol",
    match = { class = "^(pavucontrol|org.pulseaudio.pavucontrol)$" },
    float  = true,
    center = true,
    size   = { 900, 600 },
})
```

- `match.class` / `match.title` 是 **RE2 正则**，用 `^...$` 精确匹配最稳。
- 也可以用 `initial_class` / `initial_title`（窗口刚创建时的值）。
- 需要"每次打开都恢复上次大小"：加 `persistent_size = true`。

### R4 让窗口固定到某个工作区 / 不参与平铺

```lua
hl.window_rule({
    name      = "mpv-to-ws5",
    match     = { class = "^mpv$" },
    workspace = "5 silent",     -- silent = 不把镜头切过去
})

hl.window_rule({
    name      = "keep-on-screen",
    match     = { class = "^SomeApp$" },
    workspace = "special:magic silent",
})
```

### R5 调外观（间距/边框/圆角/透明/模糊/阴影）

改 `LOOK AND FEEL` 段里已有的 `hl.config` 块（**推荐**）：

```lua
hl.config({
    general = {
        gaps_in     = 4,        -- 窗口之间
        gaps_out    = 8,        -- 窗口与屏幕边缘
        border_size = 1,
        col = { … },            -- 保持不动
    },
    decoration = {
        rounding         = 8,
        active_opacity   = 1.0,
        inactive_opacity = 0.95,
        shadow = { enabled = true, range = 8, render_power = 3 },
        blur   = { enabled = true, size = 5, passes = 2, vibrancy = 0.2 },
    },
})
```

- 间距是 `css_gaps`：给整数就是四边相同，给表可以分开 `{ top=2, left=4 }`。
- 透明度是**乘法**：`0.95` 表示再乘 0.95。窗口规则里写 `"0.9 override"` 才是绝对值。
- 性能敏感：`blur.passes` 每 +1 都更吃 GPU，4K+scale2 下建议 ≤ 2。

### R6 调动画快慢 / 弹性

动画单位：`speed` 是**分秒（deciseconds，100ms）**，`speed = 5` 就是 0.5 秒。

```lua
-- 曲线（bezier：两个控制点；spring：质量/刚度/阻尼）
hl.curve("myFast",   { type = "bezier", points = { {0.15, 0}, {0.1, 1} } })
hl.curve("mySpring", { type = "spring", mass = 1, stiffness = 300, damping = 25 } })

hl.animation({ leaf = "windows",   enabled = true, speed = 4.79, spring = "mySpring" })
hl.animation({ leaf = "workspaces", enabled = true, speed = 2.5, bezier = "myFast", style = "slide" })
hl.animation({ leaf = "fade",      enabled = false })   -- 关掉淡入淡出
```

**弹性怎么调**：临界阻尼比 `ζ = damping / (2 * sqrt(stiffness * mass))`。

- 当前 `stiffness = 238.1191, mass = 1, damping = 24.21279333` → ζ ≈ **0.78**（轻微回弹）。
- 想要更"跟手"：调大 `stiffness`（更快）或 `damping`（更少弹）。推荐 ζ 在 0.6–0.8。
- `ζ > 1` 过阻尼（不弹但偏慢），`ζ < 1` 欠阻尼（会弹）。

可用的 `leaf` 是树形结构，常用的：`global`、`windows`、`windowsIn`、`windowsOut`、
`windowsMove`、`layers`、`layersIn`、`layersOut`、`fade`、`fadeIn`、`fadeOut`、
`border`、`workspaces`、`workspacesIn`、`workspacesOut`、`specialWorkspace`、`zoomFactor`。

### R7 多显示器

```lua
-- 主屏 4K 200% 缩放
hl.monitor({ output = "DP-1", mode = "preferred", position = "0x0", scale = 2 })

-- 副屏 2K，放在右边，原生缩放
hl.monitor({ output = "DP-2", mode = "2560x1440@165", position = "1920x0", scale = 1 })

-- 竖屏
hl.monitor({ output = "DP-2", mode = "preferred", position = "1920x0", scale = 1, transform = 1 })

-- 镜像
hl.monitor({ output = "DP-2", mirror = "DP-1" })

-- 临时禁用（会把窗口挤到别的屏；只想息屏请用 dpms 快捷键）
hl.monitor({ output = "DP-2", disabled = true })
```

要点：

- 用 `hyprctl monitors all` 查真实输出名；名字不稳定时用 `desc:` 前缀。
- 文件里最后那条 `output = ""` 的兜底规则会接管**没被列出**的显示器，别删。
- `transform`：0 正常、1 左转 90°、3 右转 90°、5 翻转等（0–7）。
- 缩放建议用整数（1 / 2），非整数（1.5）会让 XWayland 和部分 toolkit 变糊。

### R8 鼠标 / 触摸板 / 按设备调灵敏度

```lua
hl.config({
    input = {
        sensitivity = 0.0,                  -- 全局鼠标灵敏度，-1.0 ~ 1.0
        follow_mouse = 1,                   -- 0 不跟随、1 跟随、2/3 更激进的聚焦
        touchpad = {
            natural_scroll     = false,
            tap_to_click       = true,       -- 注意是下划线
            disable_while_typing = true,
            clickfinger_behavior = false,
        },
    },
})

-- 单个设备（名字用 `hyprctl devices` 查，别照抄示例）
hl.device({ name = "epic-mouse-v1", sensitivity = -0.5 })
hl.device({ name = "elan-touchpad", natural_scroll = true })
```

### R9 键盘布局与输入法

```lua
hl.config({
    input = {
        kb_layout  = "us,cn",                      -- 多布局用逗号分隔
        kb_options = "grp:alt_shift_toggle",       -- Alt+Shift 切换
    },
})

-- 中文输入法（fcitx5）常用环境变量：当前配置没设，输入法异常时再加
hl.env("GTK_IM_MODULE", "fcitx")
hl.env("QT_IM_MODULE", "fcitx")
hl.env("XMODIFIERS", "@im=fcitx")
```

`kb_layout` 改完要 `hyprctl reload`；如果切换键不生效，检查 `kb_options` 拼写。

### R10 工作区固定到显示器 / 每屏独立工作区

```lua
hl.workspace_rule({ workspace = "1", monitor = "DP-1", default = true })
hl.workspace_rule({ workspace = "2", monitor = "DP-1" })
hl.workspace_rule({ workspace = "3", monitor = "DP-2", default = true })

-- 无边框沉浸式工作区
hl.workspace_rule({ workspace = "name:game", no_rounding = true, no_border = true, gaps_in = 0, gaps_out = 0 })

-- 这个工作区换成别的布局
hl.workspace_rule({ workspace = "4", layout = "master" })
```

### R11 触控板手势

```lua
hl.gesture({ fingers = 3, direction = "horizontal", action = "workspace" })
hl.gesture({ fingers = 4, direction = "up",         action = "special" })
```

`direction`：`horizontal` / `vertical` / `up` / `down` / `left` / `right`；
`action`：`workspace` / `special` / `fullscreen` / `float` / `close` 等（以文档为准）。

### R12 键位子模式（submap，比如"调整窗口大小模式"）

```lua
hl.bind("ALT + R", hl.dsp.submap("resize"))

hl.define_submap("resize", function()
    hl.bind("right", hl.dsp.window.resize({ x = 10,  y = 0, relative = true }), { repeating = true })
    hl.bind("left",  hl.dsp.window.resize({ x = -10, y = 0, relative = true }), { repeating = true })
    hl.bind("up",    hl.dsp.window.resize({ x = 0, y = 10,  relative = true }), { repeating = true })
    hl.bind("down",  hl.dsp.window.resize({ x = 0, y = -10, relative = true }), { repeating = true })
    hl.bind("escape", hl.dsp.submap("reset"))     -- 必须有出口，否则会"卡"在子模式里
end)
```

卡住时在终端里救：`hyprctl dispatch 'hl.dsp.submap("reset")'`。

### R13 特殊工作区（scratchpad）

```lua
hl.bind(mainMod .. " + grave", hl.dsp.workspace.toggle_special("magic"))          -- 注意不带 special: 前缀
hl.bind(mainMod .. " + SHIFT + grave", hl.dsp.window.move({ workspace = "special:magic" }))  -- move 要带前缀
```

### R14 规则要根据"标题变化"才生效时

静态规则（`float`/`size`/`monitor` 等）只在窗口打开时求值一次，
所以"等标题变成 xxx 再浮动"必须用事件 + dispatcher：

```lua
hl.on("window.title", function(w)
    if w ~= nil and w.title == "foo" then
        hl.dispatch(hl.dsp.window.float({ action = "set" }))
    end
end)
```

动态规则（`opacity`、`border_color`、`rounding`、`no_blur`、`tag`…）会在属性变化时重新求值，
可以直接按 `title` 写。

### R15 启动程序并顺手给它套规则

```lua
hl.bind(mainMod .. " + P", hl.dsp.exec_cmd("pavucontrol", { float = true, size = { 800, 600 } }))
hl.bind(mainMod .. " + SHIFT + M", hl.dsp.exec_cmd("mpv", { workspace = "5 silent" }))
```

注意：它靠记录进程 PID 工作；如果程序 fork 出子进程再开窗口（很多 GTK/Qt 程序），
规则可能不生效——那种情况请改用 `hl.window_rule`。

### R16 临时试参数（不改文件）

```bash
HYPRLAND_INSTANCE_SIGNATURE=...  # 在 Hyprland 会话内的终端里不用手动设
hyprctl eval 'hl.config({ ["general.gaps_in"] = 0 })'      # 立刻生效
hyprctl eval 'hl.config({ ["general.gaps_in"] = 3 })'      # 复原
hyprctl dispatch 'hl.dsp.window.float({ action = "toggle" })'
hyprctl repl 'hl.get_active_window().class'                # 查信息
```

满意后再写进 `hyprland.lua`。

---

## 5. 改完怎么验证

```bash
# 0) 先备份（改之前）
cp ~/.config/hypr/hyprland.lua ~/.config/hypr/hyprland.lua.bak.$(date +%s)

# 1) 静态检查 Lua 语法（不依赖 Hyprland 运行）
luac -p ~/.config/hypr/hyprland.lua    # 没装 luac 就用下面的 Lua 解释器
lua -e 'assert(loadfile("/home/wjf/.config/hypr/hyprland.lua"))'
# 或者: hyprctl reload 之后看报错

# 2) 加载并检查配置错误（最重要）
hyprctl reload
hyprctl configerrors        # 输出为空 = 没问题

# 3) 看实际效果/状态
hyprctl monitors            # 分辨率、缩放、位置对不对
hyprctl workspaces          # 工作区在不在对的屏
hyprctl clients             # 窗口 class/title/浮动状态（写规则前先查这个）
hyprctl activewindow        # 当前窗口详情
hyprctl layers              # layer 的 namespace（写 layer_rule 前查）
hyprctl devices             # 输入设备真实名字
hyprctl getoption general.gaps_in     # 查某选项当前值（点号分隔；-j 输出 JSON）
hyprctl version

# 4) 看日志
tail -n 100 "$XDG_RUNTIME_DIR/hypr"/*/hyprland.log 2>/dev/null
journalctl --user -b -n 100 --no-pager | grep -i hypr
```

**判定标准**：

- `hyprctl configerrors` 非空 → 配置有错，按报错行号修。
- 快捷键没反应 → 键名拼写错 / 当前在 submap 里（`hyprctl repl 'hl.get_current_submap()'`）/
  被别的绑定抢先消费（`hyprctl binds` 查全部绑定）/ 窗口没有焦点。
- 规则没生效 → 先 `hyprctl clients` 看 `class` 与 `title` 实际值，再改正则。
- 桌面卡顿 → 检查是否在回调里写了阻塞调用，或 blur passes 过大。

**回滚**：

```bash
cp ~/.config/hypr/hyprland.lua.bak.<时间戳> ~/.config/hypr/hyprland.lua && hyprctl reload
```

---

## 6. 常见陷阱（都是本机真实踩过的）

1. **老语法混入**：`bind = SUPER, Q, killactive` 在 Lua 文件里是语法错误或静默失效。
   见 §7 对照表。
2. **选项名用连字符**：Lua 配置用下划线 `tap_to_click`、`follow_mouse`；
   老 hyprlang 才用 `tap-to-click`。
3. **静态规则不随标题变化**：`float`/`size`/`monitor` 只在打开时判断一次，见 R14。
4. **`toggle_special` 不带前缀，`move` 要带**：`toggle_special("magic")` 但
   `move({ workspace = "special:magic" })`。
5. **鼠标绑定要 `{ mouse = true }`**：`hl.bind(mainMod .. " + mouse:272", hl.dsp.window.drag(), { mouse = true })`。
6. **`unbind` 大小写敏感、必须逐字符一致**：`"SUPER + Q"` 和 `"SUPER+Q"` 不是同一个；
   文档自己的示例里就踩过这个坑（`hl.unbind("SUPER + Tab")` 对 `SUPER + TAB` 无效）。
   另外 `hl.unbind` 会移除它**之前**注册的所有该键绑定。
7. **重复设置以最后一条为准**：同一个选项写两次，前面那条等于没写。
8. **reload 会丢掉 `hyprctl eval` 的临时改动**，也会重建 Lua 状态（触发 `config.unload`）。
9. **回调里不能阻塞**（`sleep`/`io.popen`/`os.execute`/`wl-paste`），会把桌面卡死。
10. **非整数缩放**（1.25/1.5）会让 XWayland 程序模糊、部分程序尺寸错乱；本机用 2。
11. **`hyprpaper.conf` 是生成的**，改它没用，改壁纸请用 `SUPER+W`（wallpick）。
12. **不要删启动段的 `pgrep`/`flock`**，否则 reload 后进程翻倍。
13. **正则里的反斜杠**：用 `[[...]]` 长字符串，或写 `\\`。
14. **中文输入法**：fcitx5 由启动段拉起，但当前没设 `GTK_IM_MODULE`/`QT_IM_MODULE`，
    某些程序里打不出中文时按 R9 补环境变量。
15. **改显示器 scale 后要重新登录**（部分程序只在启动时读一次缩放）。
16. **文档里个别示例写成 `hl.focus.workspace(...)`**（binds 页 Unbind 一节的示例），
    那是笔误/旧别名，本机请统一用 `hl.dsp.focus({ workspace = "e+1" })`。

---

## 7. 老语法 → Lua 对照表（把网上教程翻译成本机写法）

| 老 hyprlang 写法 | 本机 Lua 写法 |
|---|---|
| `$mainMod = SUPER` | `local mainMod = "SUPER"` |
| `monitor=,preferred,auto,2` | `hl.monitor({ output = "", mode = "preferred", position = "auto", scale = 2 })` |
| `bind = SUPER, Q, killactive` | `hl.bind(mainMod .. " + Q", hl.dsp.window.close())` |
| `bind = SUPER, Return, exec, kitty` | `hl.bind(mainMod .. " + Return", hl.dsp.exec_cmd("kitty"))` |
| `bindm = SUPER, mouse:272, movewindow` | `hl.bind(mainMod .. " + mouse:272", hl.dsp.window.drag(), { mouse = true })` |
| `bindl = , XF86AudioMute, exec, wpctl …` | `hl.bind("XF86AudioMute", hl.dsp.exec_cmd("wpctl …"), { locked = true })` |
| `exec-once = waybar` | `hl.on("hyprland.start", function() hl.exec_cmd("waybar") end)` |
| `env = XCURSOR_SIZE,24` | `hl.env("XCURSOR_SIZE", "24")` |
| `general { gaps_in = 5 }` | `hl.config({ general = { gaps_in = 5 } })` |
| `decoration { rounding = 10 }` | `hl.config({ decoration = { rounding = 10 } })` |
| `windowrulev2 = float,class:^(QQ)$` | `hl.window_rule({ match = { class = "^QQ$" }, float = true })` |
| `windowrulev2 = opacity 0.9 0.8,class:^(kitty)$` | `hl.window_rule({ match = { class = "^kitty$" }, opacity = "0.9 0.8" })` |
| `layerrule = blur,waybar` | `hl.layer_rule({ match = { namespace = "^waybar$" }, blur = true })` |
| `workspace = 1, monitor:DP-1, default:true` | `hl.workspace_rule({ workspace = "1", monitor = "DP-1", default = true })` |
| `bezier = my, 0.23, 1, 0.32, 1` | `hl.curve("my", { type = "bezier", points = { {0.23, 1}, {0.32, 1} } })` |
| `animation = windows, 1, 4, my, popin 87%` | `hl.animation({ leaf = "windows", enabled = true, speed = 4, bezier = "my", style = "popin 87%" })` |
| `device { name = epic-mouse-v1, sensitivity = -0.5 }` | `hl.device({ name = "epic-mouse-v1", sensitivity = -0.5 })` |
| `gesture = 3, horizontal, workspace` | `hl.gesture({ fingers = 3, direction = "horizontal", action = "workspace" })` |
| `exec = hyprctl dispatch …` | `hl.dispatch(hl.dsp.…)` 或 `hl.exec_cmd("hyprctl dispatch '…'")` |
| `submap = resize` | `hl.define_submap("resize", function() … end)` + `hl.dsp.submap("resize")` |
| `bind = , escape, submap, reset` | `hl.bind("escape", hl.dsp.submap("reset"))` |

---

## 8. 交付前自检清单（AI 逐条打勾）

- [ ] 只改了 `~/.config/hypr/hyprland.lua`（要改锁屏/空闲才动 `hyprlock.conf`/`hypridle.conf`）
- [ ] 没有引入 `bind =` / `windowrulev2 =` / `exec-once =` 等老语法
- [ ] 所有选项名都在 `AI-HYPRLAND-OPTIONS.md` 里查过，用下划线写法
- [ ] 所有 dispatcher/字段都在 `AI-HYPRLAND-DISPATCHERS-RULES.md` 里查过
- [ ] 新增的 `hl.bind` 放在 `KEYBINDINGS` 段，没有插进 `for` 循环/函数内部
- [ ] 新增 `hl.window_rule`/`hl.layer_rule` 放在 `WINDOWS AND WORKSPACES` 段
- [ ] 键位没有和已有绑定冲突（冲突时后绑定的生效）
- [ ] 正则用 `[[...]]` 或正确转义
- [ ] 没有删除启动段的 `pgrep`/`flock` 防护
- [ ] `hyprctl reload && hyprctl configerrors` 输出为空（Hyprland 在运行时）
- [ ] 已告知用户：改了什么、为什么、怎么回滚、验证结果

## 9. 参考文献

- 官方 wiki（Lua 时代，2026-11 更新）：https://wiki.hypr.land/
- 配置项全集：https://wiki.hypr.land/configuring/core/config-options/
- Dispatchers：https://wiki.hypr.land/configuring/core/dispatchers/
- 窗口规则：https://wiki.hypr.land/configuring/core/rules/window-rules/
- 选择器：https://wiki.hypr.land/configuring/selectors/
- 本机版本：Hyprland 0.57.2（2026-11-09）

---

## 10. 附录：hyprlock.conf / hypridle.conf（不是 Lua！）

这两个文件是 **hyprlang 语法**（`段名 { 键 = 值 }`），跟 `hyprland.lua` 完全不同，别混。

### 10.1 hypridle.conf —— 空闲行为

当前配置（就是全部内容）：

```ini
general {
    lock_cmd = pidof hyprlock || hyprlock        # 避免重复锁定
    before_sleep_cmd = pidof hyprlock || hyprlock
    ignore_dbus_inhibit = false
    ignore_systemd_inhibit = false
}

listener {
    timeout = 600                                # 600 秒 = 10 分钟无输入
    on-timeout = pidof hyprlock || hyprlock      # 到点锁屏
}
```

常见改动：

| 想改 | 怎么改 |
|---|---|
| 多久自动锁屏 | 改 `timeout = 600`（单位**秒**；900 = 15 分钟，0 不锁） |
| 先息屏、再锁屏 | 加第二个 listener：`timeout = 300` + `on-timeout = hyprctl dispatch 'hl.dsp.dpms({ action = "disable" })'`，再在 `on-resume` 里 `enable` |
| 挂起前锁屏 | `before_sleep_cmd`（已有） |
| 到点直接挂起 | `on-timeout = systemctl suspend` |

改完必须重启进程才生效：

```bash
pkill hypridle; setsid hypridle >/tmp/hypridle.log 2>&1 &
```

> `hypridle` 是独立程序，`hyprctl reload` **不会**重载它。

### 10.2 hyprlock.conf —— 锁屏界面

同样是 hyprlang。当前配置要点：

- `$font = JetBrainsMono Nerd Font`：自定义变量，后面用 `$font` 引用
- `general { hide_cursor = false }`
- `animations { }`：`bezier = linear, 1, 1, 0, 0`、`animation = fadeIn, 1, 5, linear`（`1`=开关，`5`=速度，单位 100ms）
- `background { }`：`path = screenshot`（用当前屏幕截图做背景）、`blur_passes = 3`、`blur_size = 5`、`brightness = 0.62`、`noise = 0.02`
- `input-field { }`：密码框，`size = 20%, 5%`、`outer_color` 渐变、`placeholder_text = 请输入密码...`、`position = 0, -20`、`halign/valign = center`
- 三个 `label { }`：时间 `text = $TIME`（font_size 100）、日期 `text = cmd[update:60000] date +"%Y年%m月%d日  %A"`、天气 `text = cmd[update:600000] .../lockweather`

关键规则：

1. 每个 widget（`background`/`input-field`/`label`/`image`/`shape`）都以 `{ }` 块出现，**同名块可以写多个**（如三个 label）。
2. `monitor =` 留空 = 所有显示器；填 `DP-1` 之类 = 只在该屏显示。
3. `cmd[update:毫秒] 命令` 让文本定时执行命令取输出（天气/日期就是这么来的）。
4. 支持 pango 标记：`<b>`、`<i>`、`<span foreground="#fff">`。
5. 颜色写法与 Hyprland 相同（`rgba(...)` / `rgb(...)` / `$颜色变量`），渐变写成 `颜色1 颜色2 角度deg`。
6. `$PAMFAIL`、`$FPRINTFAIL`、`$TIME`、`$USER`、`$DESC` 是内置变量。
7. 改完**下次锁屏**生效（hyprlock 每次锁屏时读配置），不需要重启任何服务；想立刻看效果：`hyprlock`。

常见改动：

| 想改 | 怎么改 |
|---|---|
| 时间格式 | 把 `$TIME` 换成 `cmd[update:60000] date +"%H:%M"` |
| 换字体 | 改 `$font` 一行（字体必须已安装） |
| 背景更暗/更亮 | `background.brightness`（0–1，越大越亮） |
| 背景更模糊 | `background.blur_passes`（3→5 更模糊，更吃 GPU） |
| 密码框位置 | `input-field.position` + `halign/valign` |
| 用静态壁纸而不是截图 | `background.path` 改成图片绝对路径 |
