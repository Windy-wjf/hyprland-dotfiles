# Hyprland 快捷键 / 规则 / 选择器 / 显示器速查（AI 参考）

> 配套文件：`AI-HYPRLAND-GUIDE.md`（总流程与配方）、`AI-HYPRLAND-OPTIONS.md`（`hl.config` 选项全集）。
> 本文件回答的是：**键怎么绑、动作怎么发、窗口/图层/工作区规则怎么写、选择器怎么写、显示器怎么配、动画怎么配。**
> 对应本机 **Hyprland 0.57.2** 的 Lua 配置（`hl.*` API）。字段名/取值以官方 wiki（2026-11）为准，文档未提供的字段本文件不会编造。

## 使用顺序建议

1. 只知道"想干什么"（关窗口、切工作区、浮动…）→ 先看 §3 意图索引。
2. 知道 dispatcher 名、要查参数 → §2 全表。
3. 写窗口/图层/工作区规则 → §6 / §7 / §8。
4. 规则里要限定"哪个窗口/哪个工作区/哪块屏" → §9 选择器。
5. 改分辨率、缩放、屏幕排列、动画曲线 → §10。

## 目录

**第一部分：键位与动作**

- §1 `hl.bind` 语法、flags、回调约束
- §2 dispatchers 全表（含 `hl.dsp.exec_cmd` 的 rules 用法）
- §3 常用 dispatcher 意图索引
- §4 手势、submap、全局快捷键、键盘布局、设备开关、按设备配置
- §5 `hyprctl` 运行时手册（reload / configerrors / eval / repl / dispatch / 查询）

**第二部分：规则、选择器、显示器、动画**

- §6 窗口规则 `hl.window_rule`（match / 静态效果 / 动态效果 / 表达式 / group / border_color / tag）
- §7 图层规则 `hl.layer_rule`
- §8 工作区规则 `hl.workspace_rule`
- §9 选择器语法全表（窗口 / 工作区 / 显示器 / 方向）
- §10 显示器 `hl.monitor` 与动画 `hl.curve` / `hl.animation`

---

# 第一部分：键位与动作


面向本地 AI 检索的信息密集版。全部 API 为 Hyprland 0.57 的 Lua 配置接口（全局表 `hl.*`）。
示例保留文档原始写法；老式 `bind = ` / `bindm = ` 语法一律不给，只给 Lua 等价写法。

核心心智模型：

| 概念 | 说明 |
|----|----|
| `hl.bind(keys, dispatcher_or_fn, flags)` | 注册绑定。第二参可以是 `hl.dsp.*` 返回的表，也可以是 Lua 函数 |
| `hl.dsp.*` | **只返回描述动作的表，不执行任何东西**；必须交给 `hl.bind` 或包进 `hl.dispatch()` |
| `hl.dispatch(dsp)` | 立即执行一个 dispatcher，返回执行结果（可带 `ok` 字段） |
| `hl.unbind(keys)` | 按**字符串完全一致**注销 |

---

## 1. hl.bind 语法

### 1.1 签名

```lua
hl.bind("keys", dispatcher or function(), { bind_flags })
```

- `keys` 是 string（写法见 1.2）；第二参 = `hl.dsp.*` 表或 function；第三参 = flags 表（可选，见 1.3）；返回 handle（见 1.5）。
- 传 dispatcher 表 → 触发时直接执行；传函数 → 由 Hyprland 在触发时调用，函数体里的 `hl.dsp.*` **必须**包 `hl.dispatch()`，否则什么都不会发生（见 2.0）。
- 同一个键可以注册多个 bind，触发时**按书写顺序自上而下**全部执行（文档 Warning）——这是「一个键干多件事」的官方做法。
- 函数返回 `{ ok = false }` 只在 `auto_consuming` 标志下有额外含义（见 1.8）。

文档示例（原样）：

```lua
-- bind SUPER + SHIFT + Q to open Firefox
hl.bind("SUPER + SHIFT + Q", hl.dsp.exec_cmd("firefox"))

-- bind to an anonymous function with logic inside
hl.bind("SUPER + SHIFT + X", function()
    -- more logic...
    hl.dispatch(hl.dsp.window.float())
end)
```

### 1.2 key 字符串写法

| 写法 | 含义 | 文档示例 |
|----|----|----|
| `"SUPER + SHIFT + Q"` | 修饰键 + 键，用 ` + ` 连接（文档统一带空格） | `hl.bind("SUPER + SHIFT + Q", hl.dsp.exec_cmd("firefox"))` |
| `mainMod .. " + K"` | `mainMod` **不是内置量**，是用户配置里自定的变量（惯例 `local mainMod = "SUPER"`），用 Lua 字符串拼接 | `hl.bind(mainMod .. " + K", hl.dsp.exec_cmd("kitty"), { submap_universal = true })` |
| `"code:28"` | 用 evdev 键码绑定，前缀 `code:` | `hl.bind("SUPER + code:28", hl.dsp.exec_cmd("amongus"))` 绑的是 SUPER + T |
| `"Alt_L"` | 单独一个修饰键（keysym 全名，`_L` / `_R` 后缀） | `hl.bind("Alt_L", hl.dsp.exec_cmd("amongus"))` |
| `"Super_L + Alt_L"` | 纯修饰键组合。用 keysym 时按键**按下的顺序有意义**，因为它们不再被当作 modifier 处理 | `hl.bind("Super_L + Alt_L", hl.dsp.exec_cmd("kitty"))` |
| `"Ctrl_L + Ctrl_R"` | 左右同名修饰键也能组合 | `hl.bind("Ctrl_L + Ctrl_R", hl.dsp.exec_cmd("kitty"))` |
| `"XF86AudioRaiseVolume"` | 任意 keysym；名字取 `xkbcommon-keysyms.h` 里 `XKB_KEY_` 之后的那一段 | `hl.bind("XF86AudioMute", ..., { locked = true })` |
| `"mouse:272"` | 鼠标键，`mouse:` + 键码。左 272 / 右 273 / 中 274 | `hl.bind("SUPER + mouse:272", hl.dsp.window.drag(), { mouse = true })` |
| `"mouse_down"` / `"mouse_up"` / `"mouse_left"` / `"mouse_right"` | 滚轮方向 | `hl.bind("SUPER + mouse_down", hl.dsp.focus({ workspace = "e-1" }))` |
| `"switch:[name]"` | 开合类开关（笔记本 lid 等）状态变化 | 见 4.5 |
| `"switch:on:[name]"` / `"switch:off:[name]"` | 只在上/下沿触发 | 见 4.5 |
| `"catchall"` | submap 内任意未匹配键，仅 submap 内有效 | `hl.bind("catchall", hl.dsp.submap("reset"))` |

大小写与布局：`hl.unbind` 的键串**大小写敏感**，必须与 `hl.bind` 逐字符一致（见 1.6）；键名本身的大小写宽容度（文档未说明）；键名不确定时用 `wev` 抓真实 keysym/keycode。

非 QWERTY 约束（细节见 4.4）：`kb_layout` 的**第一个**布局决定 bind 键名（`us,ua` → `"SUPER + A"`，`ua,us` → `"SUPER + Cyrillic_ef"`）；键位必须无需修饰键即可打出，法语 AZERTY 的工作区绑定要写 `ampersand` 而不是 `1`；要按符号匹配就设 `resolve_binds_by_sym = 1`。

```lua
-- 法语布局：不要写 mainMod .. " + 1"
hl.bind(mainMod .. " + ampersand", hl.dsp.focus({ workspace = "1" }))
```

### 1.3 flags 参数表

```lua
hl.bind(keys, dispatcher, { flag1 = true, flag2 = true })
hl.bind(keys, hl.dsp.exec_cmd("amongus"), { release = true, locked = true })
```

| flag | 值类型 | 作用 | 何时用 |
|----|----|----|----|
| `locked` | bool | 输入抑制器（如锁屏）激活时**仍然生效** | 音量/媒体键、锁屏时仍要能用的键 |
| `release` | bool | 在**松开**按键时触发 | 需要「按下-松开」语义（push-to-talk、单击式启动器） |
| `click` | bool | 松开时触发，前提是鼠标指针仍在 `binds:drag_threshold` 内 | 与 `drag` 配合区分「点一下」和「拖一下」 |
| `drag` | bool | 松开时触发，前提是鼠标指针移出了 `binds:drag_threshold` | 拖拽类动作 |
| `long_press` | bool | 长按时触发 | 同一键「短按/长按」两套动作 |
| `repeating` | bool | 按住时连续重复 | 音量、亮度、resize 微调 |
| `non_consuming` | bool | 事件**同时**传给活动窗口，并执行 dispatcher | 既要动作又要应用收到键 |
| `auto_consuming` | bool | 仅当 dispatcher 失败（返回 `ok = false`）时才把事件传给活动窗口 | 条件绑定：命中就吃掉，没命中就透传 |
| `mouse` | bool | 标记为鼠标动作绑定 | `window.drag()` / `window.resize()` 必须加，见 4.7 |
| `transparent` | bool | 不能被其它 bind 遮蔽（shadow） | 保证该绑定优先级 |
| `ignore_mods` | bool | 忽略修饰键 | 只认主键 |
| `description` | string | 给绑定写描述；描述**总是放在 flags 表里** | 自文档化 + `hyprctl binds` 可查 |
| `dont_inhibit` | bool | 绕过应用对 keybind 的 inhibit 请求 | 应用抢了快捷键仍要生效 |
| `submap_universal` | bool | 任何 submap 下都生效 | 全局逃生键（如 `SUPER + K` 开终端） |
| `device` | table | 按设备限定，`{ inclusive = bool, list = {...} }` | 多键盘分别绑定，见 4.6 |
| `allow_input_capture` | bool | 客户端捕获输入时该 bind 仍会被处理 | 输入捕获场景下的逃生键 |

`description` 示例：

```lua
hl.bind("SUPER + Q", hl.dsp.exec_cmd("kitty"), { description = "Open my favourite terminal" })
```

读取描述：返回的 bind handle 的 `description` 字段，或 `hyprctl binds`。

### 1.4 回调函数的约束（原文警告要点）

文档 Warning 原文：

> **Keybind handlers must not block.** Lua callbacks run on the compositor event loop. Avoid `io.popen`, network I/O, clipboard tools (`wl-paste`, `xclip`), sleeps, and other long-running work inside bind functions. Prefer `hl.dsp.exec_cmd(...)` for external commands so they run outside the bind callback. If you must probe the system from Lua, bound the wait (for example with `timeout`). A hung or slow call freezes input and the entire desktop until it returns.

落地规则：

| 禁止/避免 | 替代 |
|----|----|
| `io.popen`、`sleep`、忙等 | `hl.dsp.exec_cmd("...")`；延时用 `hl.timer(fn, { timeout = ms, type = "oneshot" })` |
| 网络 I/O（curl 等） | 交给 `exec_cmd` 起的外部进程 |
| `wl-paste` / `xclip` 等剪贴板工具 | 外部脚本 |
| 任何长耗时 Lua 计算 | 拆分或移到外部进程；「A hung or slow call freezes input and the entire desktop until it returns.」 |

必须探测系统时：给等待加上界（例如命令里用 `timeout`）。

需要延时的正确写法（文档给 DPMS 的例子）：

```lua
hl.bind("...", function()
    hl.timer(function()
        hl.dispatch(hl.dsp.dpms({ action = "disable" }))
    end, {timeout = 500, type = "oneshot"})
end)
```

同理，`dpms` 与 `force_idle` **不要直接绑在键上**，否则可能产生未定义行为，要用 timer 包一层。

### 1.5 返回的 handle 与方法

`hl.bind` 返回一个 bind 对象，文档明确给出的成员：

| 成员 | 说明 |
|----|----|
| `:unbind()` | 注销该绑定 |
| `:remove()` | 同上，等价写法 |
| `.description` | flags 里写的描述字符串 |

```lua
local moveLeft = hl.bind("SUPER + L", hl.dsp.window.move({ direction = "left" }) )
moveLeft:unbind()
-- 或
moveLeft:remove()
```

关于 `:set_enabled()` / `:is_enabled()`：在文档里这两个方法出现在 `hl.window_rule()` 返回的规则 handle 和 `hl.timer()` 返回的 timer handle 上（`rule:set_enabled(false)` / `rule:is_enabled()`、`demoTimer:set_enabled(...)`）。**bind handle 是否也支持这两个方法，（文档未说明）**——请只用 `:unbind()` / `:remove()`。

### 1.6 hl.unbind 的注意点

```lua
hl.bind("SUPER + TAB", hl.dsp.focus({ workspace = "e+1" }))
hl.unbind("SUPER + Tab") -- this will NOT unbind
hl.unbind("SUPER + TAB") -- this will unbind
```

| 要点 | 说明 |
|----|----|
| 大小写 | 键串大小写敏感，必须与 `hl.bind` 时**逐字符一致** |
| 范围 | 会移除该键在调用点之前注册的**所有**同名绑定（"remove all occurrences of the key that were registered before it"） |
| 时机 | 只影响已经注册的绑定；之后再 `hl.bind` 同名键会重新生效 |

### 1.7 用 Lua 函数动态生成一组绑定

文档没有专门的批量示例，下面是等价于文档 API 的地道写法（全部只用 `hl.bind` / `hl.dsp.*`）：

```lua
local mainMod = "SUPER"

-- 1) 工作区：数字键直绑，绑定表是「配置期」构造的
for i = 1, 9 do
    hl.bind(mainMod .. " + " .. i, hl.dsp.focus({ workspace = tostring(i) }))
end

-- 2) 把窗口移到工作区：用函数包住，动作在「触发时」才求值
for i = 1, 9 do
    hl.bind(mainMod .. " + SHIFT + " .. i, function()
        hl.dispatch(hl.dsp.window.move({ workspace = tostring(i) }))
    end)
end

-- 3) 应用表驱动：flags 也一起生成
local apps = {
    { key = "RETURN", cmd = "kitty" },
    { key = "B",      cmd = "firefox" },
    { key = "E",      cmd = "thunar" },
}
for _, app in ipairs(apps) do
    hl.bind(mainMod .. " + " .. app.key, hl.dsp.exec_cmd(app.cmd),
            { description = "launch " .. app.cmd })
end

-- 4) 工厂函数生成同族绑定（媒体键，锁屏时也生效）
local function media(key, arg)
    hl.bind(key, hl.dsp.exec_cmd("playerctl " .. arg), { locked = true })
end
media("XF86AudioPlay", "play-pause")
media("XF86AudioNext", "next")
```

注意第 1 组与第 2 组的区别：dispatcher 表在**配置加载时**就构造完成，所以里面不能放依赖当前窗口/当前状态的表达式（见 1.8）。

### 1.8 两个易踩的语义

**(a) 条件在 bind 时求值，而不是每次触发时。** 文档示例：

```lua
hl.bind("SUPER + L", hl.dsp.exec_cmd("foot", { float = not (hl.get_active_window().title == "foot") }) )
```

这会在配置加载时就被解析成 `{ float = false }` 或 `{ float = true }`，并**保持到下次 reload**。要每次触发都重新判断，必须包函数：

```lua
hl.bind("SUPER + L", function()
    local is_foot = hl.get_active_window().title == "foot"
    hl.dispatch( hl.dsp.exec_cmd("foot", { float = not is_foot }) )
end)
```

**(b) `auto_consuming` 依赖 dispatcher 的 `ok` 返回值。**

```lua
hl.bind("p", function()
    local window = hl.get_active_window()
    if window and window.title == "some cool app" then
        hl.dispatch(hl.dsp.exec_cmd("another_cool_app"))
    else
        return { ok = false }
    end
end, { auto_consuming = true })
```

活动窗口标题是 `"some cool app"` 时启动 `another_cool_app` 并吃掉按键；否则 `return { ok = false }`，`p` 透传给活动窗口。

### 1.9 与 systemd-logind 冲突的键（电源键、lid）

电源键 / lid 默认由 systemd-logind 处理。推荐只在 Hyprland 运行期间屏蔽它在用 `systemd-inhibit` 启动 Hyprland（`systemd-inhibit --what=handle-power-key Hyprland`），之后正常 `hl.bind("XF86PowerOff", ...)`；不要为此改 logind.conf（文档：「a better option is to block that handling specifically while Hyprland is running」）。

---

## 2. dispatchers 全表

### 2.0 执行模型（先看这段）

| 事实 | 说明 |
|----|----|
| `hl.dsp.*` 只返回表 | "They do not invoke any action immediately, and their contents are not guaranteed to be stable at all." 唯一用途是喂给 `hl.bind()` 或 `hl.dispatch()` |
| 裸调用无效 | "**Simply writing `hl.dsp.whatever()` on its own will do nothing.**" |
| 函数内必须包 `hl.dispatch()` | fragment 里每个 `hl.dsp.*` 都要 `hl.dispatch(...)` |
| 参数表不稳定 | dispatcher 返回的表结构不保证稳定，不要依赖其字段 |

反例（文档给的）——创建了 dispatcher 但没人执行，等于没写：

```lua
hl.bind("ALT + Tab", function()
    hl.dsp.window.cycle_next()
    hl.dsp.window.alter_zorder({ mode = "top" })
end)
```

正确：

```lua
hl.bind("ALT + Tab", function()
    hl.dispatch(hl.dsp.window.cycle_next())
    hl.dispatch(hl.dsp.window.alter_zorder({ mode = "top" }))
end)
```

通用参数语义（文档 "Parameter explanation"）：

| 参数 | 默认 | 取值 |
|----|----|----|
| `window` | `"activewindow"` | 任意 window selector（`class:...`、`title:...`、`address:...` 等） |
| `action` | `"toggle"` | `"toggle"`、`"enable"`/`"on"`、`"disable"`/`"off"` |
| `relative` | `false` | `false` / `true` |

表头说明：**window 列** = 是否需要 window 选择器（是 = 有 `window?` 参数，默认 activewindow；否 = 无此参数）。

### 2.1 General（`hl.dsp.` 顶层，17 个）

| dispatcher | 参数（名 / 类型 / 取值 / 默认） | 作用 | window | 最小示例 |
|----|----|----|----|----|
| `hl.dsp.dpms` | `monitor?`；`action?` = toggle/enable/disable，默认 toggle | 开关显示器（逻辑上的，非物理断电，类似 idle 屏保）。**不要直接绑键** | 否 | `hl.dispatch(hl.dsp.dpms({ action = "disable" }))` |
| `hl.dsp.event` | `string` | 往 socket2 发一个事件 | 否 | `hl.dsp.event(event_string)` |
| `hl.dsp.exec_cmd` | `cmd` string；`rules?` table（window rule 的 effects） | 用 `sh -c` 执行命令（可用 shell 语法、管道）；文档另有简写 `hl.exec_cmd(...)`（手势/autostart 示例里直接用） | 否 | `hl.dsp.exec_cmd("kitty", { float = true })` |
| `hl.dsp.exec_raw` | `cmd` string | 执行原始命令，**不经过 `sh -c`** | 否 | `hl.dsp.exec_raw("kitty --single-instance")` |
| `hl.dsp.exit` | 无 | 退出 Hyprland；推荐改用 `hyprshutdown` | 否 | `hl.dsp.exit()` |
| `hl.dsp.focus` | 见下方 6 种重载 | 移动焦点 | 否（window 重载除外） | `hl.dsp.focus({ workspace = "3" })` |
| `hl.dsp.force_idle` | `int`（秒） | 把所有 idle timer 的已过时间设为该值，忽略 idle inhibitor；下次活动后恢复正常。**不要直接绑键** | 否 | `hl.dsp.force_idle(300)` |
| `hl.dsp.force_renderer_reload` | 无 | 强制重载所有显示器的 renderer | 否 | `hl.dsp.force_renderer_reload()` |
| `hl.dsp.global` | `string`（shortcut id）；`activate?` bool | 触发 D-Bus 全局快捷键；第二参 true=activated / false=deactivated | 否 | `hl.dsp.global("coolApp:myToggle")` |
| `hl.dsp.layout` | `message` string | 给当前布局发一条布局消息（消息表见各布局页） | 否 | `hl.dsp.layout("togglesplit")` |
| `hl.dsp.no_op` | 无 | 什么都不做，用于条件绑定占位 | 否 | `hl.dsp.no_op()` |
| `hl.dsp.pass` | `window?` | 把快捷键（PRESS + RELEASE 都）透传给窗口 | 是 | `hl.dsp.pass({ window = "class:TeamSpeak 3" })` |
| `hl.dsp.release_input_capture` | 无 | 释放当前活动的 input capture 会话 | 否 | `hl.dsp.release_input_capture()` |
| `hl.dsp.reload_config` | 无 | 重载配置，等同 `hyprctl reload` | 否 | `hl.dsp.reload_config()` |
| `hl.dsp.send_key_state` | `window?`；`mods`；`key`；`state` = down/up | 同 `send_shortcut`，但可显式控制按下/松开 | 是 | `hl.dsp.send_key_state({ mods = "SUPER", key = "F4", state = "down" })` |
| `hl.dsp.send_shortcut` | `window?`；`mods`；`key` | 向窗口发送指定组合键 | 是 | `hl.dsp.send_shortcut({ mods = "SUPER", key = "F4" })` |
| `hl.dsp.submap` | `name` string（`"reset"` 回默认） | 进入/切换 submap | 否 | `hl.dsp.submap("resize")` |

`focus` 的 6 种重载：

| 重载 | 说明 | 示例 |
|----|----|----|
| `focus({ direction })` | 按方向移动焦点 | `hl.dsp.focus({ direction = "left" })` |
| `focus({ monitor })` | 焦点移到某显示器 | `hl.dsp.focus({ monitor = "DP-1" })` |
| `focus({ workspace, on_current_monitor? })` | 焦点移到工作区 | `hl.dsp.focus({ workspace = "3" })` |
| `focus({ window })` | 焦点移到窗口 | `hl.dsp.focus({ window = "class:firefox" })` |
| `focus({ urgent_or_last })` | 焦点给 urgent 窗口，没有则给最后一个 | `hl.dsp.focus({ urgent_or_last = true })` |
| `focus({ last })` | 焦点给上一个窗口 | `hl.dsp.focus({ last = true })` |

### 2.2 Window（`hl.dsp.window.`，20 个）

| dispatcher | 参数（名 / 类型 / 取值 / 默认） | 作用 | window | 最小示例 |
|----|----|----|----|----|
| `hl.dsp.window.alter_zorder` | `window?`；`mode` = `"top"` / `"bottom"` | 调整窗口叠放层级 | 是 | `hl.dsp.window.alter_zorder({ mode = "top" })` |
| `hl.dsp.window.center` | `window?` | 把窗口居中到屏幕 | 是 | `hl.dsp.window.center()` |
| `hl.dsp.window.clear_tags` | `window?` | 清空窗口所有 tag | 是 | `hl.dsp.window.clear_tags()` |
| `hl.dsp.window.close` | `window?` | 发**优雅关闭请求**（等同点 X） | 是 | `hl.dsp.window.close()` |
| `hl.dsp.window.cycle_next` | `window?`；`next?`；`tiled?`；`floating?` | 焦点切到下一个窗口 | 是 | `hl.dsp.window.cycle_next({ tiled = true })` |
| `hl.dsp.window.deny_from_group` | `action?` | 拒绝窗口加入组 | 否（对活动窗口） | `hl.dsp.window.deny_from_group({ action = "enable" })` |
| `hl.dsp.window.drag` | 无 | 进入交互式拖拽，**只能配鼠标绑定** | 否 | `hl.bind("ALT + mouse:272", hl.dsp.window.drag(), { mouse = true })` |
| `hl.dsp.window.float` | `window?`；`action?` | 设置浮动状态 | 是 | `hl.dsp.window.float({ action = "toggle" })` |
| `hl.dsp.window.fullscreen_state` | `window?`；`action?` = toggle/set/unset；`internal` int；`client` int；`layout_aware?` bool 默认 true | 分别设置「Hyprland 内部状态」和「告知客户端的状态」，取值见 2.7 | 是 | `hl.dsp.window.fullscreen_state({ internal = 2, client = 0 })` |
| `hl.dsp.window.fullscreen` | `window?`；`action?` = toggle/set/unset；`mode?` = `"maximized"`/`"fullscreen"`；`layout_aware?` bool 默认 true | 全屏/最大化开关 | 是 | `hl.dsp.window.fullscreen({ mode = "maximized" })` |
| `hl.dsp.window.kill` | `window?` | 向窗口所属进程发 `SIGKILL` | 是 | `hl.dsp.window.kill()` |
| `hl.dsp.window.move` | 见下方 7 种重载 | 移动窗口 | 是 | `hl.dsp.window.move({ workspace = "3" })` |
| `hl.dsp.window.pin` | `window?`；`action?` | 钉住窗口（所有工作区可见） | 是 | `hl.dsp.window.pin()` |
| `hl.dsp.window.pseudo` | `window?`；`action?` | 伪平铺开关 | 是 | `hl.dsp.window.pseudo()` |
| `hl.dsp.window.resize` | 重载 A：`keep_aspect_ratio?`；重载 B：`window?`；`x`；`y`；`relative?` | 重载 A 进入交互式缩放（配鼠标）；重载 B 按量/按坐标缩放 | A 否 / B 是 | `hl.dsp.window.resize({ x = 10, y = 0, relative = true })` |
| `hl.dsp.window.set_prop` | `window?`；`prop` string；`value` | 设置动态窗口属性，prop 名见 2.7 | 是 | `hl.dsp.window.set_prop({ prop = "no_anim", value = "1" })` |
| `hl.dsp.window.signal` | `window?`；`signal` | 给窗口所属进程发 POSIX 信号 | 是 | `hl.dsp.window.signal({ signal = "SIGTERM" })` |
| `hl.dsp.window.swap` | 4 种重载：`{ direction }`、`{ target }`、`{ next }`、`{ prev }` | 与另一个窗口交换位置 | 只对活动窗口 | `hl.dsp.window.swap({ direction = "right" })` |
| `hl.dsp.window.tag` | `window?`；`tag` | 给窗口打静态 tag；`+tag` 加、`-tag` 删、`tag` 切换 | 是 | `hl.dsp.window.tag({ tag = "+code" })` |
| `hl.dsp.window.toggle_swallow` | 无 | 切换被吞（swallow）窗口的可见性 | 否 | `hl.dsp.window.toggle_swallow()` |

`window.move` 的 7 种重载：

| 重载 | 说明 | 示例 |
|----|----|----|
| `move({ direction, group_aware? })` | 按方向移动；`group_aware = true` 会顺带把窗口移入/移出组 | `hl.dsp.window.move({ direction = "left" })` |
| `move({ workspace, follow? })` | 移到工作区 | `hl.dsp.window.move({ workspace = "special:magic" })` |
| `move({ monitor, follow? })` | 移到显示器 | `hl.dsp.window.move({ monitor = "DP-2" })` |
| `move({ x, y, relative? })` | 按相对量或绝对坐标移动 | `hl.dsp.window.move({ x = 50, y = 0, relative = true })` |
| `move({ into_group = direction })` | 移入某方向的组 | `hl.dsp.window.move({ into_group = "right" })` |
| `move({ into_or_create_group = direction })` | 移入该方向的组，没有组就新建 | `hl.dsp.window.move({ into_or_create_group = "right" })` |
| `move({ out_of_group })` | 移出组；`true` 表示无方向 | `hl.dsp.window.move({ out_of_group = true })` |

### 2.3 Workspace（`hl.dsp.workspace.`，6 个）

| dispatcher | 参数 | 作用 | window | 最小示例 |
|----|----|----|----|----|
| `hl.dsp.workspace.change_id` | `workspace`；`id` int（必须 > 0 且未被占用） | 改数字工作区的 ID | 否 | `hl.dsp.workspace.change_id({ workspace = "3", id = 30 })` |
| `hl.dsp.workspace.move` | `workspace?`；`monitor` | 把工作区移到显示器 | 否 | `hl.dsp.workspace.move({ monitor = "DP-1" })` |
| `hl.dsp.workspace.rename` | `workspace`；`name?` | 改显示名。**identity 不变**，配置动作仍按创建时的名字引用 | 否 | `hl.dsp.workspace.rename({ workspace = "3", name = "code" })` |
| `hl.dsp.workspace.swap_monitors` | `monitor1`；`monitor2` | 交换两个显示器当前的工作区 | 否 | `hl.dsp.workspace.swap_monitors({ monitor1 = "DP-1", monitor2 = "DP-2" })` |
| `hl.dsp.workspace.show` | `workspace` | 在所属显示器上显示该工作区，但**不给焦点** | 否 | `hl.dsp.workspace.show({ workspace = "3" })` |
| `hl.dsp.workspace.toggle_special` | `special_name` string | 开关 special 工作区 | 否 | `hl.dsp.workspace.toggle_special("magic")` |

special 前缀规则（极易错）：

| 场景 | 写法 |
|----|----|
| 只处理 special 的 dispatcher（`toggle_special`） | **不要**带 `special:` 前缀：`toggle_special("magic")` |
| 接受任意工作区的 dispatcher（`window.move`、`focus` 等） | **必须**带前缀才能命中：`{ workspace = "special:magic" }` |
| 数量限制 | 可定义多个具名 special，但同一时刻最多存在 97 个 |

```lua
hl.bind("SUPER + SHIFT + S", hl.dsp.window.move({ workspace = "special:magic" }))
hl.bind("SUPER + S", hl.dsp.workspace.toggle_special("magic"))
```

### 2.4 Group（`hl.dsp.group.`，6 个）

| dispatcher | 参数 | 作用 | window | 最小示例 |
|----|----|----|----|----|
| `hl.dsp.group.active` | `window?`；`index` int | 切到组内第 index 个窗口 | 是 | `hl.dsp.group.active({ index = 2 })` |
| `hl.dsp.group.lock` | `all?` bool / `window?`；`action?` | 锁定组，阻止新窗口进入 | 是 | `hl.dsp.group.lock({ all = true, action = "enable" })` |
| `hl.dsp.group.move_window` | `window?`；`forward?` bool | 在组顺序里前后移动窗口 | 是 | `hl.dsp.group.move_window({ forward = true })` |
| `hl.dsp.group.next` | `window?` | 组内下一个窗口 | 是 | `hl.dsp.group.next()` |
| `hl.dsp.group.prev` | `window?` | 组内上一个窗口 | 是 | `hl.dsp.group.prev()` |
| `hl.dsp.group.toggle` | `window?` | 开关组（把当前窗口变成组 / 拆组） | 是 | `hl.dsp.group.toggle()` |

组 = i3wm 的 tabbed container：占一个窗口的空间，内部切换；`lock` 阻止新窗口进入；`window.deny_from_group` 让指定窗口不进组。

### 2.5 Cursor（`hl.dsp.cursor.`，2 个）

| dispatcher | 参数 | 作用 | window | 最小示例 |
|----|----|----|----|----|
| `hl.dsp.cursor.move` | `x`；`y` | 把光标移到坐标 | 否 | `hl.dsp.cursor.move({ x = 100, y = 200 })` |
| `hl.dsp.cursor.move_to_corner` | `window?`；`corner` int `[0 - 3]` | 光标移到窗口某个角 | 是 | `hl.dsp.cursor.move_to_corner({ corner = 0 })` |

### 2.6 exec_cmd 的 rules（启动程序并给窗口套规则）

签名与文档原例：

```lua
hl.dsp.exec_cmd( cmd, { rules }? )
```

```lua
hl.bind("SUPER + E", hl.dsp.exec_cmd("kitty", { float = true, move = {0, 0} }))
```

`rules` 到底是什么：

| 问题 | 答案 |
|----|----|
| 类型 | 一张 **window rule 的 effects 表**（不是 match 表，也不是规则对象） |
| 有没有 `match` | 没有。匹配靠 `exec_cmd` **记录的 spawned 进程 PID**：启动后记住 PID，用这个 PID 认领新窗口，所以表里只写效果键 |
| 键名从哪来 | 与 `hl.window_rule()` 的 effects 同名同义：`float = true`、`move = {0, 0}`、`workspace = "1 silent"`、`opacity = "0.9"`、`no_blur = true`、`rounding = 10` … |
| 与 `hl.window_rule({ match = ..., <effect> })` 的关系 | 同一套 effects 词表；`hl.window_rule` 自己写 `match`（按 class/title 永久匹配），`exec_cmd` 的 rules 只对这次 spawn 出来的窗口生效 |
| 已知短板 | 文档明说「some windows might work better, some worse」：程序 fork 后由子进程开窗则 PID 对不上，规则不生效 |

```lua
-- A. 启动即套规则：只作用于这次启动的 kitty（按 PID）
hl.bind("SUPER + T", hl.dsp.exec_cmd("kitty", { float = true }))

-- B. 全局规则：所有 class=kitty 的窗口（按 match，永久生效）
hl.window_rule({ match = { class = "kitty" }, float = true })
```

### 2.7 set_prop 与 fullscreen_state 细节

`set_prop` 的 `prop` = window rules 里的任意 **dynamic effects**：`hl.dsp.window.set_prop({ prop = "no_anim", value = "1" })`，可加 `window = "class:abc"` 指向具体窗口。部分 prop **只读**：`border_color`（来自 `active_border_color` / `inactive_border_color`）、`opacity`（来自 `opacity*` 系列规则）。

`fullscreen_state` 的 `internal` / `client` 取值（内部状态 vs 告知客户端的状态解耦）：

| 值 | 状态 | 含义 |
|----|----|----|
| -1 | Current | 维持当前全屏状态 |
| 0 | None | 按当前布局分配空间 |
| 1 | Maximized | 占满工作区，保留 margins |
| 2 | Fullscreen | 占满整个屏幕 |

| 组合 | 效果 |
|----|----|
| `{ internal = 2, client = 0 }` | 实际全屏但骗客户端说没全屏（防 Chromium 系浏览器进演示模式） |
| `{ internal = 0, client = 2 }` | 实际不全屏但骗客户端说已全屏 |

`layout_aware`：默认 `true`，决定用布局自己的全屏处理还是默认处理（scrolling 等布局自带处理）。Lua 里可查 `hl.get_active_window().fullscreen_handler == "default"`。

### 2.8 运行时调用与引号转义

| 手段 | 行为 |
|----|----|
| `hl.dispatch(dsp)` | 在 Lua 里立即执行，返回结果（`ok` 字段供 `auto_consuming` 判断） |
| `hyprctl dispatch '<lua>'` | 等价于 `hyprctl eval 'hl.dispatch(<lua>)'`，是「包一层 dispatch」的语法糖 |
| `hyprctl eval '<lua>'` | 执行任意 Lua 字符串（可多语句） |

写法与引号（实战）：

```bash
# 外层单引号，内部双引号：最稳，不解释 $ 和反引号
hyprctl dispatch 'hl.dsp.focus({ workspace = "3" })'
hyprctl dispatch 'hl.dsp.submap("reset")'
hyprctl dispatch 'hl.dsp.window.tag({ tag = "+code" })'

# 必须用双引号包裹时，内部双引号要 shell 转义
hyprctl dispatch "hl.dsp.window.tag({ tag = \"+code\" })"

# 多语句用 eval
hyprctl eval 'hl.dispatch(hl.dsp.focus({ workspace = "3" }))'
```

`--batch` 时的**双重转义**要求（文档 Note）：批处理里各命令用 `;` 分隔，所以命令内部的 `;`（例如多语句 Lua）必须写成 `\;`，字面反斜杠也要转义，且这是在 shell 自身转义之外的额外一层。

被卡在 submap 里的逃生命令（没有终端时开一个新 TTY；只有一个实例时 `--instance` 为 0）：

```bash
hyprctl dispatch 'hl.dsp.submap("reset")'
hyprctl dispatch --instance 0 'hl.dsp.submap("reset")'
```

---

## 3. 常用 dispatcher 速查（按意图索引）

| 想做什么 | 用哪个 | 示例 |
|----|----|----|
| 切工作区 | `hl.dsp.focus({ workspace })` | `hl.dsp.focus({ workspace = "3" })`；相对：`{ workspace = "e+1" }` / `{ workspace = "e-1" }` |
| 移动窗口到工作区 | `hl.dsp.window.move({ workspace })` | `hl.dsp.window.move({ workspace = "3" })` |
| 切到 / 开关 special | `hl.dsp.workspace.toggle_special(name)` | `hl.dsp.workspace.toggle_special("magic")`（不带 `special:`） |
| 把窗口丢进 special | `hl.dsp.window.move({ workspace })` | `hl.dsp.window.move({ workspace = "special:magic" })`（必须带前缀） |
| 开关浮窗 | `hl.dsp.window.float()` | `hl.dsp.window.float({ action = "toggle" })` |
| 全屏 | `hl.dsp.window.fullscreen()` | `hl.dsp.window.fullscreen()`；最大化：`{ mode = "maximized" }` |
| 伪平铺 | `hl.dsp.window.pseudo()` | `hl.dsp.window.pseudo()` |
| 关闭窗口（优雅） | `hl.dsp.window.close()` | `hl.dsp.window.close()` |
| 杀进程（SIGKILL） | `hl.dsp.window.kill()` | `hl.dsp.window.kill()`；对指定窗口：`{ window = "class:foo" }` |
| 切换布局 | 无专用 dispatcher；改配置项 | `hl.config({ ["general.layout"] = "master" })`（在函数里调，或 `hyprctl eval`） |
| 调整 master 窗口数 | `hl.dsp.layout("addmaster"/"removemaster")` | `hl.dsp.layout("addmaster")` / `hl.dsp.layout("removemaster")` |
| 调整 master 分割比 | `hl.dsp.layout("mfact ...")` | 相对：`hl.dsp.layout("mfact -0.2")`；精确：`hl.dsp.layout("mfact exact 0.6")` |
| 调整 dwindle split | `hl.dsp.layout(...)` | 翻转：`hl.dsp.layout("togglesplit")`；比例：`hl.dsp.layout("splitratio 1.2 exact")` / `hl.dsp.layout("splitratio -0.4")` |
| 发送按键给窗口 | `hl.dsp.send_shortcut` / `send_key_state` / `pass` | `hl.dsp.send_shortcut({ mods = "SUPER", key = "F4", window = "class:OBS" })` |
| 执行命令 | `hl.dsp.exec_cmd`（`sh -c`）/ `exec_raw`（无 shell） | `hl.dsp.exec_cmd("kitty", { float = true })` |
| 退出 Hyprland | `hl.dsp.exit()` | `hl.dsp.exit()`（文档建议用 `hyprshutdown`） |
| 重载配置 | `hl.dsp.reload_config()` | `hl.dsp.reload_config()` |
| 打开 submap | `hl.dsp.submap(name)` | `hl.dsp.submap("resize")`，退出用 `hl.dsp.submap("reset")` |
| 下一个窗口 | `hl.dsp.window.cycle_next()` | `hl.dsp.window.cycle_next({ tiled = true })` |
| 方向焦点 | `hl.dsp.focus({ direction })` | `hl.dsp.focus({ direction = "left" })` |
| 切到上一窗口 | `hl.dsp.focus({ last })` | `hl.dsp.focus({ last = true })` |
| 窗口移到别的显示器 | `hl.dsp.window.move({ monitor })` | `hl.dsp.window.move({ monitor = "DP-2", follow = true })` |
| 焦点移到别的显示器 | `hl.dsp.focus({ monitor })` | `hl.dsp.focus({ monitor = "DP-2" })` |
| 交换两个窗口 | `hl.dsp.window.swap(...)` | `hl.dsp.window.swap({ direction = "right" })` |
| 置顶 / 置底 | `hl.dsp.window.alter_zorder({ mode })` | `hl.dsp.window.alter_zorder({ mode = "top" })` |
| 钉住窗口 | `hl.dsp.window.pin()` | `hl.dsp.window.pin()` |
| 打 / 去 tag | `hl.dsp.window.tag({ tag })` | `hl.dsp.window.tag({ tag = "+music" })`、`{ tag = "-music" }`、`{ tag = "music" }`（切换） |
| 组（tabbed）开关 | `hl.dsp.group.toggle()` | `hl.dsp.group.toggle()` |
| 组内切换 | `hl.dsp.group.next()` / `prev()` / `active({ index })` | `hl.dsp.group.next()` |
| 重命名工作区 | `hl.dsp.workspace.rename()` | `hl.dsp.workspace.rename({ workspace = "3", name = "code" })` |
| 鼠标拖窗口 / 缩放 | `window.drag()` / `window.resize()` | `hl.bind("ALT + mouse:272", hl.dsp.window.drag(), { mouse = true })` |
| 透传快捷键给应用 | `hl.dsp.pass({ window })` | `hl.dsp.pass({ window = "class:TeamSpeak 3" })` |
| 触发 D-Bus 全局快捷键 | `hl.dsp.global(id)` | `hl.dsp.global("coolApp:myToggle", true)` |

补充说明：**切换布局没有 dispatcher**，改 `general.layout` 配置项（`hl.config({ ["general.layout"] = "master" })`）；**`hl.dsp.layout()` 的消息是布局私有的**（master / dwindle / scrolling / monocle 各有自己的命令，传错只在该布局下无效），参数用**单个空格**分隔；Monocle 下 `window.cycle_next()` 不工作，要用 `hl.dsp.layout("cyclenext")` 或 `hl.dsp.window.cycle_next({ tiled = true })`。

---

## 4. 手势、submap、全局快捷键、键盘布局、开关设备、按设备配置

### 4.1 手势 `hl.gesture{...}`

```lua
hl.gesture({
    action = "...",
    direction = "...",
    fingers = int,
})
```

字段（`fingers` 范围 `[2 - 9]`，`scale` 范围 `[0.1 - 10.0]`，`mods` 如 `"SUPER"` / `"ALT SHIFT"`，`disable_inhibit` = true 时绕过快捷键抑制器）：

| 字段 | 说明 | 类型 |
|----|----|----|
| `action` | 要执行的动作 | string / function / table |
| `direction` | `swipe`（任意滑）/ `horizontal` / `vertical` / `left` / `right` / `up` / `down` / `pinch`（任意捏合）/ `pinchin` / `pinchout` | string |
| `fingers` | 手指数 | int |
| `mods` | 修饰键掩码 | string |
| `scale` | 手势增量倍率 | float |
| `disable_inhibit` | 绕过快捷键抑制器 | bool |

动作：

| action | 作用 | 附加参数 |
|----|----|----|
| Lua 函数 | 执行命名函数或 lambda | 无 |
| `close` | 关闭活动窗口 | 无 |
| `cursor_zoom` | 缩放光标处 | `zoom_level`；`mode` = `"mult"`（倍数）/ `"live"`（跟随捏合连续更新） |
| `float` | 浮动活动窗口 | `mode` = `"float"` / `"tile"` 强制方向 |
| `fullscreen` | 全屏 | `mode` = `"maximize"` 改为最大化 |
| `move` | 移动活动窗口 | 无 |
| `resize` | 缩放活动窗口 | 无 |
| `scroll_move` | 滚动 tape（仅 scrolling 布局） | 无 |
| `special` | 开关 special 工作区 | 工作区名（如 `workspace_name = "scratchpad"`） |
| `workspace` | 工作区滑动切换 | 无 |
| `unset` | 取消之前设置的手势；必须与原始手势的 direction/mods/fingers/scale **完全一致** | 无 |

基础示例（文档原样）：

```lua
hl.gesture({ fingers = 3, direction = "horizontal", action = "workspace" })
hl.gesture({ fingers = 3, direction = "down", mods = "ALT", action = "close" })
hl.gesture({ fingers = 3, direction = "up", mods = "SUPER", scale = 1.5, action = "fullscreen" })
hl.gesture({ fingers = 3, direction = "left", scale = 1.5, action = "float" })
```

cursor_zoom：

```lua
hl.gesture({ fingers = 2, direction = "pinch", action = "cursor_zoom", zoom_level = 2 })
hl.gesture({ fingers = 2, direction = "pinch", action = "cursor_zoom", zoom_level = 1.2, mode = "mult" })
hl.gesture({ fingers = 2, direction = "pinch", action = "cursor_zoom", zoom_level = 1, mode = "live" })
```

`cursor_zoom` 默认是**切换**；`mult` 乘当前缩放；`live` 连续跟随捏合，且锚定手势开始时的光标位置（`live` 下数值参数无用，写 `1` 占位）。

Lua 回调（lambda 或命名函数）：

```lua
local function swipe()
    hl.notification.create({ text = "I just swiped on my trackpad!", timeout = 5000, icon = "ok" })
end
hl.gesture({ fingers = 3, direction = "up", action = swipe })   -- 也可直接写 action = function() ... end
```

实时手势（live）：`action` 传表，含 `start` / `update` / `finish`。

`start` / `update` 收到的事件字段（`finish` 只收 `cancelled`（bool，后端异常终止为 true）、`time_ms`、`type`）：

| 字段 | 说明 | 类型 |
|----|----|----|
| `delta.x` / `delta.y` | 相对上次的水平/垂直位移，右、下为正 | float |
| `fingers` | 手指数 2–9 | int |
| `rotation` | 指形角度变化，顺时针为正；非 pinch 时为 nil | float |
| `scale` | 相对手势起点的指形尺寸变化，张开为正、捏合为负；非 pinch 时为 nil | float |
| `time_ms` | 事件时间戳（自系统启动的毫秒） | int |
| `type` | `swipe` 或 `pinch` | string |

```lua
-- 4 指上滑开终端
hl.gesture({ fingers = 4, direction = "up", action = function() hl.exec_cmd("kitty") end })

-- 4 指下滑 + SUPER 切 special，绕过抑制器
hl.gesture({ fingers = 4, direction = "down", mods = "SUPER", action = "special",
             workspace_name = "scratchpad", disable_inhibit = true })

-- 音量：用实时 delta 连续调节
local volume_gesture = function(change)
    hl.exec_cmd("wpctl set-volume @DEFAULT_AUDIO_SINK@ " .. math.abs(change) .. "%" .. (change < 0 and "-" or "+"))
end
hl.gesture({
    fingers = 3,
    direction = "vertical",
    action = {
        start  = function(e) volume_gesture(-0.25 * e.delta.y) end,
        update = function(e) volume_gesture(-0.25 * e.delta.y) end
    }
})
```

### 4.2 submap（`hl.define_submap`）

进入 / 退出：`hl.dsp.submap(name)`；`"reset"` 回全局。

| API / 关键字 | 说明 |
|----|----|
| `hl.define_submap(name, fn)` | 定义 submap 内的绑定集 |
| `hl.define_submap(name, next_name, fn)` | 按下其中任意键后自动切到 `next_name`（`"reset"` 表示退出） |
| `hl.dsp.submap("reset")` | 回全局 |
| `"catchall"` | submap 内任意未匹配的键（`hl.bind("catchall", hl.dsp.submap("reset"))` 可做任意键退出） |
| `{ submap_universal = true }` | 跨越所有 submap 生效（放在 bind flags 里） |

```lua
-- 进入 resize 模式
hl.bind("ALT + R", hl.dsp.submap("resize"))
hl.define_submap("resize", function()
    hl.bind("right", hl.dsp.window.resize({ x = 10, y = 0, relative = true }), { repeating = true })
    hl.bind("left",  hl.dsp.window.resize({ x = -10, y = 0, relative = true }), { repeating = true })
    hl.bind("up",    hl.dsp.window.resize({ x = 0, y = 10, relative = true }), { repeating = true })
    hl.bind("down",  hl.dsp.window.resize({ x = 0, y = -10, relative = true }), { repeating = true })
    hl.bind("escape", hl.dsp.submap("reset"))   -- 必须有逃生键

    -- 一绑多动作：resize 后立刻退出（用函数包多句 hl.dispatch）
    hl.bind("SHIFT + right", function()
        hl.dispatch(hl.dsp.window.resize({ x = 50, y = 0, relative = true }))
        hl.dispatch(hl.dsp.submap("reset"))
    end)
end)
```

**警告**：一定要留一个退出键（上例的 `escape`），否则会卡在 submap 里。

自动关闭 / 自动跳转（第二参）：

```lua
hl.bind("SUPER + a", hl.dsp.submap("submapA"))
hl.define_submap("submapA", "submapB", function()          -- 按任意键后切到 submapB
    hl.bind("a", hl.dsp.exec_cmd("someCoolThing.sh"))
end)
hl.define_submap("submapB", "reset", function()            -- 按任意键后回默认
    hl.bind("a", hl.dsp.exec_cmd("someOtherCoolThing.sh"))
end)

-- 一键禁用所有键位：进出同一个键
hl.bind(KEYS, hl.dsp.submap("clean"))
hl.define_submap("clean", function()
    hl.bind(KEYS, hl.dsp.submap("reset"))
end)
```

嵌套（示例里每层用 `escape` 回上层、`SHIFT + escape` 回全局；原文该例 `hl.define_submap(main_submap, ...)` 漏引号，按 Lua 语义应为字符串 `"main_submap"`）：

```lua
hl.bind(mainMod .. " + M", hl.dsp.submap("main_submap"))
hl.define_submap("main_submap", function()
    hl.bind("1", hl.dsp.submap("nested_one"))
    hl.define_submap("nested_one", function()
        hl.bind("SHIFT + escape", hl.dsp.submap("reset"))
        hl.bind("escape", hl.dsp.submap("main_submap"))
    end)
    hl.bind("escape", hl.dsp.submap("reset"))
end)
```

### 4.3 全局快捷键

两条路线：

| 路线 | 用法 | 适用 |
|----|----|----|
| `pass` / `send_shortcut`（经典） | 把真实按键事件透传给目标窗口 | 所有原生 Wayland 应用 |
| D-Bus GlobalShortcuts portal | `hl.dsp.global("app:id")` | 应用已支持 GlobalShortcuts portal，且**必须**有 xdg-desktop-portal-hyprland |

```lua
-- OBS 的 SUPER + F10 全局化
hl.bind("SUPER + F10", hl.dsp.pass({ window = [[class:com\.obsproject\.Studio]] }))

-- 把 MOUSE5 透传给 TeamSpeak 3（push-to-talk 场景）
hl.bind("mouse:276", hl.dsp.pass({ window = "class:TeamSpeak 3" }))

-- 按下 SUPER + F10 时向 OBS 发 SUPER + F4
hl.bind("SUPER + F10", hl.dsp.send_shortcut({ mods = "SUPER", key = "F4", window = "class:(TeamSpeak 3)" }))

-- D-Bus 全局快捷键：默认按触发它的按键事件类型发送，第二参 true = activated
hl.bind("SUPER + SHIFT + A", hl.dsp.global("coolApp:myToggle"))
hl.bind("SUPER + SHIFT + B", hl.dsp.global("coolApp:myToggle", true))
```

| 要点 | 说明 |
|----|----|
| `pass` 自带 PRESS + RELEASE | 不需要 `release` flag；push-to-talk 一个 `pass` 就够 |
| Xwayland | 原生 Wayland 完美；Xwayland「a bit wonky」，透传的必须是「global Xorg keybind」 |
| 找 shortcut id | 运行 `hyprctl globalshortcuts`，列出已注册快捷键及描述 |
| 事件方向 | `global` 默认按触发它的按键事件类型发送：`release` 绑定只会发 deactivated，应用可能不理 |
| 强制方向 | 第二参布尔：`true` = activated，`false` = deactivated |
| `send_key_state` | 需要精确控制 down/up 时用它（`state = "down"` / `"up"`） |

### 4.4 键盘布局

| 做法 | 写法 |
|----|----|
| XKB 选项（配置期） | `hl.config({ input = { kb_layout = "us,cz", kb_variant = ",qwerty", kb_options = "grp:alt_shift_toggle" } })` |
| 运行时切换 | `hyprctl switchxkblayout <DEVICE> <next/prev/ID>`，或绑键执行它 |
| 按设备设布局 | `hl.device({ name = "my-epic-keyboard-v1", kb_layout = "us,pl,de" })` |

约束与坑：

| 要点 | 说明 |
|----|----|
| bind 用哪个布局 | `input` 里**第一个**布局决定 bind 的键名（`us,ua` → `"SUPER + A"`；`ua,us` → `"SUPER + Cyrillic_ef"`） |
| 变体数量必须对齐 | `kb_variant` 按布局逐个对应，数量与顺序必须匹配；想留空就写空位（`"dvorak,,"`）；只写一个值则对全部布局生效 |
| 符号匹配模式 | `resolve_binds_by_sym = 1`（全局或按设备）：按打出的符号匹配 bind，跨布局一致 |
| 按设备布局不改 bind 键位 | 默认 per-device 布局不影响 keymap；要让 bind 跟随符号需 `resolve_binds_by_sym = 1` |
| 查可用布局/选项 | `cat /usr/share/X11/xkb/rules/base.lst`；`grep -i 'persian' ...`；`grep 'grp:.*toggle' ...` |
| 切布局命令 | `hyprctl switchxkblayout at-translated-set-2-keyboard next`；`DEVICE` 可为 `current` / `all`（current = devices 里的 main 键盘）；`CMD` 为 `next` / `prev` / 索引（`us`:0、`pl`:1、`de`:2） |

### 4.5 开关设备（switches，lid 等）

```lua
hl.bind("switch:[switch name]", hl.dsp.exec_cmd("swaylock"), { locked = true })
hl.bind("switch:on:[switch name]", hl.dsp.exec_cmd("notify-send 'yooo'"), { locked = true })
hl.bind("switch:off:[switch name]", hl.dsp.exec_cmd("notify-send 'among us'"), { locked = true })
```

| 前缀 | 触发时机 |
|----|----|
| `switch:[name]` | 开关状态变化（toggle） |
| `switch:on:[name]` | 只在上沿（打开） |
| `switch:off:[name]` | 只在下沿（关闭） |

| 要点 | 说明 |
|----|----|
| 查名字 | `hyprctl devices` |
| 与 logind 冲突 | `logind.conf` 的 `HandleLidSwitch` 可能与 Hyprland 的 lid 配置冲突 |
| 推荐隔离 | `systemd-inhibit --what=handle-lid-switch Hyprland`，只在 Hyprland 运行时让 logind 忽略该开关 |
| 常见搭配 | `{ locked = true }`，合盖锁屏在锁屏状态下也要生效 |

### 4.6 按设备绑定（per-device binds）

`device` flag 是一个表：`inclusive` + `list`。

| 字段 | 类型 | 默认 | 语义 |
|----|----|----|----|
| `inclusive` | bool | `true` | true = **只有** list 里的设备能触发；false = **除** list 外都能触发 |
| `list` | table of string | — | 设备名，或设备 tag（per-device 配置里设的 `tags`） |

```lua
-- 只有 example-keyboard-1 能用
hl.bind("SUPER + Q", hl.dsp.exec_cmd("kitty"), { device = { inclusive = true, list = { "example-keyboard-1" } } })

-- 除 razer / asus 外都能用
hl.bind("SUPER + Q", hl.dsp.exec_cmd("kitty"), { device = { inclusive = false, list = { "razer-keyboard", "asus-keyboard" } } })
```

查设备名：`hyprctl devices`。

### 4.7 按设备配置 `hl.device{...}` 与触摸板开关

```lua
hl.device({
    name = "my-epic-keyboard",
    sensitivity = -0.5
})
```

| 要点 | 说明 |
|----|----|
| `name` | 从 `hyprctl devices` 取 |
| 可设的键 | 任意 `input` 段配置项 |
| 不能设的键 | `force_no_accel`，以及窗口管理类选项（`follow_mouse`、`follow_mouse_threshold`、`float_switch_override_focus`、`mouse_refocus`、`special_fallthrough` 等） |
| 平板 | 可用 `output` 把平板绑到显示器；`name` 要用 `Tablet` 而不是 `Tablet Pad` / `Tablet Tool` |

仅 per-device 可用的属性：

| 属性 | 适用设备 | 说明 | 默认 |
|----|----|----|----|
| `enabled` | mice / touchpads / touchdevices / keyboards / tablets | 启用/禁用设备（是否参与屏幕光标） | `true` |
| `keybinds` | 会发按键事件的设备 | 该设备是否触发 keybind | `true` |
| `tags` | keyboards / pointers | 分组与别名，逗号分隔，供 per-device binds 的 `list` 使用 | `""` |

开关触摸板（`enabled = false`）：`hl.device({ name = "elan1203:00-04f3:2f4a-touchpad", enabled = false })`

鼠标拖拽/缩放绑定（`mouse` flag 必须为 true；鼠标绑定「behave like normal binds」，可先按修饰键再按鼠标键）：

```lua
hl.bind("SUPER + mouse:272", hl.dsp.window.drag(), { mouse = true })
hl.bind("SUPER + CTRL_L", hl.dsp.window.drag(), { mouse = true })     -- 键盘键也能触发
hl.bind("SUPER + mouse:273", hl.dsp.window.resize(), { mouse = true })
hl.bind("SUPER + ALT_L", hl.dsp.window.resize(), { mouse = true })

-- click 与 drag 的区分阈值（文档示例值 10px）
hl.config({ binds = { drag_threshold = 10 } })
hl.bind("ALT + mouse:272", hl.dsp.window.drag(), { mouse = true })
hl.bind("ALT + mouse:272", hl.dsp.window.float(), { click = true })
```

滚轮事件之间有冷却，由 `binds.scroll_event_delay` 控制。

---

## 5. hyprctl 运行时手册

前置警告（原文要点）：`hyprctl` 的调用由 compositor **同步**派发，频繁调用会造成卡顿。大量控制调用请用 `--batch`，信息查询也要限量。

### 5.1 核心命令

| 命令 | 用途 | 输出 / 要点 |
|----|----|----|
| `hyprctl reload` | 重载配置 | 无输出/ok。`reload full-reset` 会**重建整个 config context**（可在 Lua / hyprlang 之间切换），非必要不用 |
| `hyprctl configerrors` | 列出当前配置解析错误 | 排查语法/选项名错误的第一站；无错误则空列表 |
| `hyprctl eval '<lua>'` | 动态执行 Lua 字符串 | 返回 `ok`，或抛出的错误 |
| `hyprctl repl` | 交互式 Lua REPL（Ctrl+D 退出） | `hyprctl repl [code]` 执行并 `tostring()` 打印结果 |
| `hyprctl dispatch '<lua>'` | 等价于 `eval 'hl.dispatch(...)'` | 传入的是**裸 dispatcher 表达式**，不带 `hl.dispatch` |
| `hyprctl getprop <window> <property>` | 读窗口属性 | `property` 同 `set_prop`；`animationstyle` 未设返回 `(unset)`；`min_size` 默认 `20 20`；`max_size` 默认 `inf inf`（JSON 里 `[null,null]`） |
| `hyprctl getoption <section.option>` | 读配置选项当前值 | 见 5.3 |
| `hyprctl binds` | 列出所有已注册绑定 | 含 flags 与 `description` |
| `hyprctl devices` | 列出键盘/鼠标/开关 | 设备名、开关名都从这里取 |
| `hyprctl clients` | 列出所有窗口及属性 | 查窗口 tag 也用它 |
| `hyprctl activewindow` | 当前活动窗口名与属性 | — |
| `hyprctl monitors` | 活动输出及属性 | `monitors all` 含未激活输出 |
| `hyprctl workspaces` | 所有工作区及属性 | — |
| `hyprctl activeworkspace` | 当前工作区及属性 | — |
| `hyprctl layers` | 所有 layer | 状态栏/壁纸/启动器属 layer 不属 window |
| `hyprctl version` | 版本 + 编译 flags、commit、branch | 报 bug 必带 |
| `hyprctl globalshortcuts` | 已注册的 D-Bus 全局快捷键 | 拿 `app:id` 给 `hl.dsp.global` 用 |
| `hyprctl submap` | 当前 submap 名 | 卡在 submap 时先查这个 |
| `hyprctl instances` | 所有运行中的 Hyprland 实例 | 配合 `--instance` |
| `hyprctl layouts` | 可用布局（含插件） | — |
| `hyprctl descriptions` | 所有配置项的描述与类型（JSON） | 查选项名最全的来源 |
| `hyprctl rollinglog` | 日志尾部，支持 `-f`/`--follow` | 排错 |

### 5.2 eval 的持久性（重要）

- `hyprctl eval 'hl.config({...})'` 改的是**运行时状态**，只影响当前会话，不写回配置。
- `reload` 会重读配置文件（`reload full-reset` 更会重建整个 config context），所以 eval 临时设的选项 **reload 后回到配置文件里的值**；要长期生效必须写进配置。`hyprctl seterror` 设的字符串同理（「Will reset when Hyprland's config is reloaded」）。

需要「临时改一下再看看」时用 eval；需要持久就用 `hl.config(...)` 写进配置，再 `hyprctl reload`。

### 5.3 getoption 的写法与返回

选项名一律 `section.option`，嵌套段用点继续下钻：

```bash
hyprctl getoption general.border_size
hyprctl getoption input.touchpad.disable_while_typing
```

- 输出 = 该选项的当前值（"gets the config option status (values)"）；具体返回**字段名（文档未说明）**，要结构化就加 `-j` 走 JSON。
- 可用选项名见 Config options 页，`hyprctl descriptions` 也能列全部选项与类型；值类型与其底层类型一致（int / float / str / vec2 / 颜色等），脚本解析时别假设都是字符串。

### 5.4 其它常用子命令

| 命令 | 用途 |
|----|----|
| `hyprctl kill` | 进入 kill 模式，点谁杀谁，ESC 退出（类似 `xkill`） |
| `hyprctl setcursor <theme> <size>` | 设光标主题并重载；0.37.0 起只接受 hyprcursor 主题，旧 XCursor 用 `XCURSOR_THEME`/`XCURSOR_SIZE` |
| `hyprctl output create <backend> [name]` | 加虚拟输出；backend = `wayland`（嵌套会话）/ `headless`（VNC/RDP/Sunshine）/ `auto`；`create`/`remove` 可写作 `add`/`destroy` |
| `hyprctl switchxkblayout <DEVICE> <next|prev|ID>` | 切 XKB 布局；`DEVICE` 可为 `current` / `all` |
| `hyprctl seterror <color> <msg>` / `seterror disable` | 设/清 hyprctl 错误串（reload 后重置） |
| `hyprctl notify <ICON> <TIME_MS> <COLOR> <MSG>` | 内置通知；消息里加 `fontsize:<SIZE>` 调字号 |
| `hyprctl dismissnotify [N]` | 关闭全部（无参或 `-1`）或最旧的 N 条通知 |
| `hyprctl --batch 'cmd1 ; cmd2'` | 批量执行，减少同步往返 |

### 5.5 flags 与批量

| flag | 作用 |
|----|----|
| `-j` | 输出 JSON，如 `hyprctl -j monitors` |
| `-i` | 选择实例（id 或 `hyprctl instances` 里的索引） |
| `-r` | 命令执行后强制刷新状态（布局/规则变更后有用） |

批量转义（原文 Note）：`--batch` 里命令用 `;` 分隔，所以单条命令**内部**的分号（例如多语句 Lua）要写成 `\;`，字面反斜杠也要转义——这还没算 shell 自身那一层转义。

```bash
hyprctl --batch 'dispatch hl.dsp.submap("reset") ; reload'
```
---

# 第二部分：规则、选择器、显示器、动画


本文所有配置均为 Hyprland 0.57 的 Lua 配置（`hl.*` API）。字段名、取值、默认值均按官方文档原文整理，未列出的字段即文档未提供。

- 规则顺序：同类规则从**上到下**求值，**最后一个匹配者生效**。
- 所有选择器（window / workspace / monitor）既能用于 dispatcher，也能用于规则匹配。

## 6. 窗口规则 `hl.window_rule`

### 6.1 签名

```lua
hl.window_rule({
    name   = "my-rule",          -- 可选；只有命名规则才能被动态启停
    match  = { class = "kitty" },-- 匹配表
    effect = some_effect_value,  -- 效果字段直接平铺在同一层
})
```

效果字段与 `match` 平级，直接写在表里（如 `no_blur = true`），不是嵌套在 `effect = {}` 中。

### 6.2 `match` 可匹配字段（全表）

| 字段 | 类型 | 含义 |
|---|---|---|
| `class` | RegEx | 窗口 `class` 匹配该正则 |
| `initial_class` | RegEx | 窗口 `initialClass` 匹配该正则 |
| `title` | RegEx | 窗口 `title` 匹配该正则 |
| `initial_title` | RegEx | 窗口 `initialTitle` 匹配该正则 |
| `xdg_tag` | RegEx | 按窗口的 `xdgTag` 匹配 |
| `content` | string | 指定内容类型：`none` / `photo` / `video` / `game` |
| `focus` | bool | 当前是否聚焦 |
| `fullscreen` | bool | 是否全屏（覆盖式或非覆盖式都算） |
| `fullscreen_state_client` | int | 客户端视角的全屏状态：`0` 无、`1` 最大化、`2` 全屏、`3` 最大化+全屏 |
| `fullscreen_state_internal` | int | Hyprland 内部记录的全屏状态，取值同上 |
| `float` | bool | 是否浮动 |
| `group` | bool | 是否处于 group 中 |
| `modal` | bool | 是否模态窗口（如“你确定吗”弹窗） |
| `pin` | bool | 是否被 pin（显示在所有工作区；**对非浮动窗口无效**） |
| `tag` | string | 窗口带指定 tag（可匹配动态 tag） |
| `workspace` | workspace selector | 窗口位于指定工作区 |
| `xwayland` | bool | 是否 Xwayland 窗口 |

### 6.3 静态效果（打开时求值一次）

| 效果 | 类型 | 说明 |
|---|---|---|
| `center` | bool | 若窗口浮动，则居中到显示器 |
| `content` | string | 设置内容类型：`"none"` / `"photo"` / `"video"` / `"game"` |
| `float` | bool | 浮动窗口 |
| `fullscreen` | bool | 全屏窗口 |
| `fullscreen_state` | string | 设置内部客户端的全屏模式，如 `"1 2"`；取值 `0` 无、`1` 最大化、`2` 全屏、`3` 最大化+全屏 |
| `group` | string | 设置窗口 group 属性，见 1.6 |
| `maximize` | bool | 最大化窗口 |
| `monitor` | string | 指定窗口在哪个显示器打开（如 `"1"`、`"DP-1"`），可后缀 `" silent"` |
| `move` | table 或 string | 把浮动窗口移到显示器局部坐标，见 1.4 |
| `no_close_for` | int | 打开后若干毫秒内 `killactive` 无法关闭该窗口 |
| `no_initial_focus` | bool | 打开时不给予初始焦点 |
| `pin` | bool | pin 窗口（显示在所有工作区；对非浮动窗口无效，通常配合 `float = true`） |
| `pseudo` | bool | 伪平铺（pseudotile） |
| `scrolling_width` | float | 当窗口开在 scrolling 布局工作区时设置列宽 |
| `size` | table 或 string | 调整浮动窗口尺寸，见 1.4 |
| `suppress_event` | string | 忽略特定事件，空格分隔：`"fullscreen"`、`"maximize"`、`"activate"`、`"activatefocus"`、`"fullscreenoutput"`、`"x11configurerequest"` |
| `tile` | bool | 平铺窗口 |
| `workspace` | string | 指定窗口在哪个工作区打开；可为 `"unset"`，可后缀 `" silent"` |

#### 警告：静态效果只求值一次

静态效果在**窗口打开时求值一次**，之后永不重新求值。这意味着用 `title` / `class` 匹配时，实际匹配到的是 `initialTitle` / `initialClass`。

因此**无法**根据窗口创建后 `title` 的变化去 `float`（或应用其它静态效果）。正确做法是用事件监听 + dispatch：

```lua
hl.on("window.title", function(w)
    if w ~= nil and w.title == "foo" then
        hl.dispatch(hl.dsp.window.float({ action = "set" }))
    end
end)
```

### 6.4 位置 / 尺寸与表达式

`move` / `size` / `min_size` / `max_size` 接受 Lua 表或字符串，值可以是数字或表达式。字符串在**第一个空白处**分割。

以下写法都是配置错误：单值、非恰好两个元素的表、用空白以外的分隔符（如 `"800,600"`、`"800x600"`）。

| 变量 | 含义 |
|---|---|
| `monitor_w` | 显示器宽度 |
| `monitor_h` | 显示器高度 |
| `window_x` | 窗口 x 坐标 |
| `window_y` | 窗口 y 坐标 |
| `window_w` | 窗口宽度 |
| `window_h` | 窗口高度 |
| `cursor_x` | 光标 x 坐标 |
| `cursor_y` | 光标 y 坐标 |

所有位置变量均为**显示器局部坐标**；写进字符串时不能含空格（否则会被当作分隔符）。

```lua
size = { 800, 600 }                        -- 表写法（数字）
size = "800 600"                           -- 字符串写法
move = { "cursor_x - (window_w * 0.5)", "cursor_y - (window_h * 0.5)" }  -- 窗口中心移到光标
move = { "window_w * 0.5", "(monitor_h / 2) + 17" }  -- 左缘贴屏左、垂直方向居中下 17px
max_size = "monitor_w*0.5 monitor_h*0.5"   -- 最大尺寸取显示器一半
```

### 6.5 动态效果（属性变化即重新求值）

| 效果 | 类型 | 说明 |
|---|---|---|
| `allows_input` | bool | 强制 Xwayland 窗口接收输入，即使它自己请求不接收 |
| `animation` | string | 强制指定窗口动画及样式（如 `"popin"`、`"popin 80%"`） |
| `border_color` | gradient | 边框颜色或渐变，见 1.7 |
| `border_size` | int | 边框宽度 |
| `confine_pointer` | bool | 把鼠标锁定在窗口内（游戏时锁在单屏常用） |
| `dim_around` | bool | 压暗窗口周围（为浮动窗口设计） |
| `decorate` | bool | 是否绘制窗口装饰（默认 `true`） |
| `focus_on_activate` | bool | 应用请求聚焦时是否真的聚焦它 |
| `idle_inhibit` | string | idle 抑制模式：`"none"`、`"always"`、`"focus"`、`"fullscreen"` |
| `immediate` | bool | 允许该窗口撕裂（tearing） |
| `keep_aspect_ratio` | bool | 鼠标缩放时保持宽高比 |
| `max_size` | table 或 string | 浮动窗口最大尺寸，见 1.4 |
| `min_size` | table 或 string | 浮动窗口最小尺寸，见 1.4 |
| `nearest_neighbor` | bool | 强制最近邻过滤（像素风） |
| `no_anim` | bool | 禁用该窗口动画 |
| `no_auto_hdr` | bool | 禁用该窗口 AutoHDR（如 `foot` 全屏时误触发） |
| `no_blur` | bool | 禁用模糊 |
| `no_dim` | bool | 禁用窗口变暗 |
| `no_focus` | bool | 禁止聚焦该窗口 |
| `no_follow_mouse` | bool | `input.follow_mouse=1` 时鼠标移入也不聚焦 |
| `no_glow` | bool | 禁用发光 |
| `no_max_size` | bool | 取消最大尺寸限制 |
| `no_screen_share` | bool | 屏幕共享时用黑块遮住该窗口及其弹窗 |
| `no_shadow` | bool | 禁用阴影 |
| `no_shortcuts_inhibit` | bool | 禁止应用抑制你的快捷键 |
| `no_vrr` | bool | 禁用该窗口 VRR；仅当 `misc.vrr` 为 `2` 或 `3` 时生效 |
| `no_wobble` | bool | 禁用摆动 |
| `no_xdg_drags` | bool | 禁用 XDG 拖拽（如拖 CSD 标题栏） |
| `opacity` | string | 透明度乘数：`"0.8"` 全局；`"0.9 0.7"` 活动/非活动；`"1.0 0.8 0.9"` 活动/非活动/全屏；每个值后加 `" override"` 表示设为绝对值而非相乘 |
| `opaque` | bool | 把该窗口的 `decoration.active/inactive/fullscreen_opacity` 设为 `1` |
| `force_rgbx` | bool | 禁用窗口自身的透明（与 `opaque` 相对，不影响 Hyprland 给的透明度） |
| `persistent_size` | bool | 浮动窗口内部记住尺寸；下次同 class+title 的新浮动窗口恢复该尺寸 |
| `render_unfocused` | bool | 让窗口以为自己正在被渲染（即使不可见） |
| `rounding` | int | 强制圆角像素数，忽略默认值 |
| `rounding_power` | float | 覆盖该窗口的圆角幂次 |
| `scroll_mouse` | float | 覆盖 `input.scroll_factor` |
| `scroll_touchpad` | float | 覆盖 `input.touchpad.scroll_factor` |
| `stay_focused` | bool | 只要可见就强制保持焦点 |
| `sync_fullscreen` | bool | 全屏模式是否始终与发给窗口的一致 |
| `tag` | string | 打 tag：前缀 `+` 设置、`-` 取消、无前缀切换（如 `"+myTag"`） |
| `tonemap` | string | 色调映射：`on`（默认）、`off` 关闭、`clamp` 把亮度裁剪到目标、`limited` 用动态曲线只压超出上限的部分 |
| `xray` | bool | 该窗口使用模糊 xray 模式 |

**所有动态效果都能用 `hl.dsp.window.set_prop` 修改**：

```lua
hl.dsp.window.set_prop({ prop = "no_anim", value = "1" })
hl.dsp.window.set_prop({ prop = "no_anim", value = "1", window = "class:abc" })
```

动态效果在匹配属性变化时重新求值：例如“浮动时改边框色”的规则，窗口重新平铺后颜色会恢复默认。

### 6.6 `group` 规则字符串选项

`group` 取一个空格分隔的选项字符串：

| 选项 | 含义 |
|---|---|
| `"barred"` | 不自动并入当前聚焦且未锁定的 group |
| `"deny"` | 禁止该窗口被切换成 group 或被加入 group |
| `"invade"` | 强制在已锁定的 group 中打开窗口 |
| `"lock"` [`"always"`] | 锁定 group；与 `"set"` 或 `"new"` 组合使用 |
| `"new"` | `"barred set"` 的简写 |
| `"override"` [其它选项] | 覆盖其它 `group` 规则 |
| `"set"` [`"always"`] | 以 group 形式打开窗口 |
| `"unset"` | 清除所有 `group` 规则 |

- 无选项的 `group` 等价于 `group = "set"`。
- 默认 `set` 与 `lock` 只对**新窗口生效一次**；加 `always` 限定后始终生效。

```lua
hl.window_rule({ match = { class = "kitty" }, group = "set" })
hl.window_rule({ match = { class = "code" },  group = "lock always" })
```

### 6.7 `border_color`：单色 / 渐变 / 按焦点分设

```lua
-- 单色
border_color = "rgb(FF0000)"

-- 渐变
border_color = { colors = { "rgba(33ccffee)", "rgba(00ff99ee)" }, angle = 45 }
```

`border_color` 可与 `focus` 匹配字段组合，分别设置活动 / 非活动边框色：

```lua
-- 把 Firefox 的非活动边框设为 品红→青 渐变
hl.window_rule({
    match        = { class = "firefox", focus = false },
    border_color = { colors = { "rgba(ffff00ee)", "rgba(00ffffee)" }, angle = 33 }
})
```

技巧：同一窗口写两条规则，一条 `focus = true`、一条 `focus = false`，即可分别指定活动/非活动边框色（等价于全局 `general.col.active_border` / `general.col.inactive_border` 的作用）。

也可用双色字符串（文档示例，左→右两色）：`border_color = "rgb(FF0000) rgb(880808)"`。

### 6.8 tag 规则 vs `hl.dsp.window.tag`

tag 分**静态**与**动态**，动态 tag 带 `*` 后缀。用 `hyprctl clients` 查看窗口 tag。

- 静态 tag：用 `hl.dsp.window.tag` dispatcher 添加。
- 动态 tag：用 `tag` 窗口规则添加。

两者互斥：**`tag` 规则只能操作动态 tag；`hl.dsp.window.tag` 只对静态 tag 生效，且调用时会清除该窗口的动态 tag。**

```bash
hyprctl dispatch 'hl.dsp.window.tag({ tag = "+code" })'    # 加；"-code" 去掉；"code" 切换
hyprctl dispatch 'hl.dsp.window.tag({ tag = "+music", window = "class:Celluloid" })'
```

规则写法（注意 `-` 前缀清除动态 tag，以及 `term*` 的精确匹配）：

```lua
hl.window_rule({ match = { class = "footclient" }, tag = "+term" })  -- 加动态 tag `term*`
hl.window_rule({ match = { class = "footclient" }, tag = "term" })   -- 切换 `term*`
hl.window_rule({ match = { tag = "cpp" },  tag = "+code" })          -- 给带 `cpp` 的窗口加 `code*`
hl.window_rule({ match = { tag = "code" }, opacity = "0.8" })        -- 匹配 `code` 或 `code*`
hl.window_rule({ match = { tag = "cpp" },  opacity = "0.7" })        -- 同时命中，后者胜出
hl.window_rule({ match = { tag = "term*" }, opacity = "0.6" })       -- 只匹配 `term*`，不匹配裸 `term`
hl.window_rule({ match = { tag = "term" }, tag = "-code" })          -- 从 `term`/`term*` 去掉 `code*`

-- 配合键位切换透明度（用 tag 承载状态）
hl.bind("SUPER + CTRL + 2", hl.dsp.window.tag({ tag = "alpha_0.2" }))
hl.bind("SUPER + CTRL + 4", hl.dsp.window.tag({ tag = "alpha_0.4" }))
hl.window_rule({ match = { tag = "alpha_0.2" }, opacity = "0.2 override" })
hl.window_rule({ match = { tag = "alpha_0.4" }, opacity = "0.4 override" })
```

### 6.9 规则顺序与命名规则启停

效果从上到下处理，**最后一个匹配者优先**。下例中：所有非全屏 kitty 为 `0.8`，但浮动 kitty 取 `0.5`；其它浮动窗口也是 `0.5`。

```lua
hl.window_rule({ match = { float = true },    opacity = "0.5 override 0.5 override" })
hl.window_rule({ match = { class = "kitty" }, opacity = "0.8 override 0.8 override" })
```

只有**命名规则**能被动态修改 / 启用 / 禁用。`hl.window_rule()` 返回一个句柄对象：

```lua
local myRule = hl.window_rule({
  name        = "my-rule",
  match       = { class = "kitty" },
  border_size = 5,
})

myRule:set_enabled(false)  -- 禁用
myRule:set_enabled(true)   -- 重新启用
myRule:is_enabled()        -- 查询状态
```

## 7. layer 规则 `hl.layer_rule`

Wayland 中启动器、状态栏、壁纸等不是窗口而是 layer，用 `hl.layer_rule()` 管理，语法与窗口规则一致。

```lua
hl.layer_rule({
    name? = string,
    match = {
        prop = some_prop_value,
    },
    effect = some_effect_value,
})
```

### 7.1 可匹配字段

| 字段 | 类型 | 含义 |
|---|---|---|
| `namespace` | RegEx | layer 的 namespace，用 `hyprctl layers` 查 |

### 7.2 效果字段（全表）

| 效果 | 类型 | 限制 | 说明 |
|---|---|---|---|
| `above_lock` | int | | 非 0 时把 layer 画在锁屏之上；`2` = 可在锁屏上交互 |
| `animation` | string | | 为该 layer 指定动画样式 |
| `blur` | bool | | 为该 layer 开启模糊 |
| `blur_popups` | bool | | 为弹窗开启模糊 |
| `dim_around` | bool | | 压暗该 layer 背后的所有内容 |
| `ignore_alpha` | float | 0.0 – 1.0 | 模糊时忽略不透明度小于等于该值的像素 |
| `no_anim` | bool | | 禁用动画 |
| `no_screen_share` | bool | | 屏幕共享时隐藏该 layer |
| `order` | int | 可为负 | 相对其它 layer 的空间预留顺序，order 高者在抢占空间时优先 |
| `xray` | bool | | 该 layer 使用模糊 xray 模式 |

> 若某些 layer 开了 `blur` 仍无模糊，可能是客户端自身设置控制（见 FAQ 的 blur 一节）。

### 7.3 示例

```lua
-- 给 Waybar 开模糊
hl.layer_rule({ match = { namespace = "waybar" }, blur = true })


-- Rofi：开模糊并忽略低 alpha
hl.layer_rule({
  match        = { namespace = "rofi" },
  blur         = true,
  ignore_alpha = 0.5,
})

-- 命名规则同样返回句柄：myLayerRule:set_enabled(false)
```

查 namespace：`hyprctl layers` 会按显示器列出各 layer 的 namespace。

## 8. workspace 规则 `hl.workspace_rule`

用于给工作区设定专属行为，例如“所有窗口无边框、无间隙”的工作区。部分布局还有自己的规则（见各布局页面）。

### 8.1 签名

```lua
hl.workspace_rule({
    workspace = workspace_selector,
    rule1 = some_value,
    rule2 = other_value,
})
```

### 8.2 全部字段

| 字段 | 类型 | 限制 | 说明 |
|---|---|---|---|
| `animation` | string | | 该工作区使用的动画样式 |
| `border_size` | int | | 窗口边框宽度 |
| `decorate` | bool | | 是否绘制窗口装饰 |
| `default_name` | string | | 工作区默认名称 |
| `float_gaps` | css_gaps | | 浮动窗口间隙 |
| `gaps_in` | css_gaps | | 窗口之间的间隙 |
| `gaps_out` | css_gaps | | 窗口与显示器边缘之间的间隙 |
| `layout` | string | | 该工作区使用的布局 |
| `layout_opts` | table | | 布局专属选项表，键值取决于布局 |
| `monitor` | string | | 把工作区绑定到某个显示器 |
| `default` | bool | | 该工作区是否作为指定显示器的默认工作区 |
| `no_border` | bool | | 关闭边框 |
| `no_rounding` | bool | | 关闭窗口圆角 |
| `no_shadow` | bool | | 关闭阴影 |
| `persistent` | bool | | 即使为空且非活动也保持该工作区存在 |

### 8.3 示例

```lua
hl.workspace_rule({ workspace = "3", no_rounding = true, decorate = false })

hl.workspace_rule({
  workspace = "name:coding", no_rounding = true, decorate = false,
  gaps_in = 0, gaps_out = 0, no_border = true, monitor = "DP-1"
})

hl.workspace_rule({ workspace = "8", border_size = 8 })

hl.workspace_rule({ workspace = "name:Hello", monitor = "DP-1", default = true })

hl.workspace_rule({ workspace = "15", animation = "slidevert", default_name = "slider" })

-- 按工作区指定布局（布局名见各布局页）
hl.workspace_rule({ workspace = "2", layout = "scrolling" })
```

## 9. 选择器语法全表

任意 ID 都可以用两种方式选择：

- **相对选择**：`+` 或 `-`
- **绝对选择**：直接用 ID

### 9.1 正则与通用注意点

- Hyprland 使用 Google **RE2**，多项式时间复杂度不可接受的写法不支持（如回溯型正则）。
- 取反：正则前加 `negative:`，例如 `"negative:kitty"` 表示“不匹配 kitty 时通过”。
- Lua 长字符串 `[[...]]` 可避免转义地狱：写 `[[\b\w*apple\b]]` 而不是 `"\\b\\w*apple\\b"`。

### 9.2 窗口选择器

| 选择器 | 说明 |
|---|---|
| 窗口对象 | 直接传窗口对象 |
| `pid:...` | 精确匹配进程 PID |
| `stableid:...` | 精确匹配稳定 ID |
| `address:0x...` | 精确匹配窗口地址 |
| `class:...` | 正则匹配 class |
| `initialclass:...` | 正则匹配 initialClass |
| `title:...` | 正则匹配 title |
| `initialtitle:...` | 正则匹配 initialTitle |
| `tag:...` | 正则匹配 tag |
| `activewindow` | 当前活动窗口 |
| `floating` | 浮动窗口 |
| `tiled` | 平铺窗口 |

未提供 window 参数时，**默认作用于活动窗口**。

```lua
hl.dsp.window.close({ window = "class:firefox" })
hl.dsp.window.float({ window = "title:Picture-in-Picture", action = "enable" })
hl.dsp.window.close({ window = [[class:^(kitty|foot)$]] })   -- RE2 + Lua 长字符串
hl.dsp.window.close({ window = "class:negative:firefox" })    -- 取反：不匹配 firefox 的窗口
```

`window` 参数出现的位置：

| 位置 | 写法 |
|---|---|
| window dispatcher | `hl.dsp.window.close({ window = "class:firefox" })`、`hl.dsp.window.float({ window = "...", action = "set" })` |
| 属性修改 | `hl.dsp.window.set_prop({ window = "class:abc", prop = "no_anim", value = "1" })` |
| 窗口规则 | `match` 表里用 `class` / `title` / `tag` 等字段，而非 `window` |
| 省略时 | 一律回退到 `activewindow` |

dispatcher 的通用参数：

| 参数 | 说明 |
|---|---|
| `window` | 不设则默认 `"activewindow"`，可填任意窗口选择器 |
| `action` | 不设则默认 `"toggle"`；可为 `"toggle"`、`"enable"`/`"on"`、`"disable"`/`"off"` |
| `relative` | 不设则默认 `"false"`；可为 `"false"`、`"true"` |

### 9.3 工作区选择器

| 形式 | 说明 |
|---|---|
| 名称 | 如 `1`、`42`、`Web`、`Anime`、`Better anime` |
| `previous` | 上一个工作区 |
| `previous_per_monitor` | 当前显示器上的上一个工作区 |
| `special` | 特殊工作区 |
| `special:name` | 具名特殊工作区 |

> 只接受特殊工作区的上下文（如 `hl.dsp.toggle_special()` 的参数）里**不要**写 `special:` 前缀。`hl.dsp.toggle_special("foo")` 目标就是通常写作 `special:foo` 的工作区；前缀只在普通工作区也合法的场景需要。

#### 4.3.1 过滤器

只能作用于**已存在**的工作区；对不存在的工作区套规则（如 `persistent`）会失败。过滤器是一个或多个表达式，空格分隔，表达式内部不能有空格。示例：`r[2-4] w[t1]`。

| 表达式 | 含义 |
|---|---|
| `r[A-B]` | ID 范围 A 到 B（含端点） |
| `s[bool]` | 是否为特殊工作区 |
| `n[bool]` | 是否为具名工作区 |
| `n[s:string]` | 名称以 string 开头 |
| `n[e:string]` | 名称以 string 结尾 |
| `m[monitor]` | 位于指定显示器 |
| `w[(flags)A-B]` | 窗口数量在 A–B 之间 |
| `w[(flags)X]` | 窗口数量恰为 X |
| `f[-1]` `f[0]` `f[1]` `f[2]` | 工作区全屏状态：`-1` 无全屏、`0` 全屏、`1` 最大化、`2` 全屏但不把状态发给窗口；只匹配有覆盖式全屏窗口的工作区 |

`w[...]` 的 flags（可省略）：

| flag | 含义 |
|---|---|
| `t` | 只统计平铺窗口 |
| `f` | 只统计浮动窗口 |
| `g` | 统计 group 数而非窗口数 |
| `v` | 只统计可见窗口 |
| `p` | 只统计被 pin 的窗口 |

```lua
hl.workspace_rule({ workspace = "r[2-4] w[t1]", no_border = true })   -- 2~4 号、恰好 1 个平铺窗口
hl.workspace_rule({ workspace = "s[false] n[s:web]", gaps_in = 4 })   -- 非特殊、名称以 web 开头
hl.workspace_rule({ workspace = "m[DP-1] w[g2]", gaps_out = 0 })      -- DP-1 上、2 个 group
```

#### 4.3.2 相对查询

在工作区选择器后接带符号偏移 `+n` / `-n`，表示相对当前活动工作区；若要按绝对 1-based ID 查找，用 `~` 连接（例如 `m~3` 是当前显示器上第 3 个工作区）。

| 选择器 | 说明 | 限制 |
|---|---|---|
| `e` | 在所有显示器上找 | 越界时按方向回绕 |
| `m` | 只在当前显示器上找 | 越界时按方向回绕 |
| `r` | 只在当前显示器上找，**包含空/不存在**的工作区 | \[1 - …\] |
| `empty` | 找第一个空工作区；后缀 `m` 只找当前显示器，后缀 `n` 找**下一个**可用空工作区（如 `emptynm`） | 越过最后一个数字工作区（2147483647）时回绕 |

> 警告：接受 ID 的查询选择器**必须**带符号或 `~`。`m3` 会被当成工作区名称而不是查询选择器，除非真有个叫 `m3` 的工作区，否则什么也不做。

```lua
hl.dsp.workspace.move({ workspace = "e+1", monitor = "DP-2" })  -- 全局下一个工作区移到 DP-2
hl.dsp.focus({ workspace = "m-1" })                              -- 当前显示器上一个工作区
hl.dsp.focus({ workspace = "m~3" })                              -- 当前显示器第 3 个工作区
hl.dsp.focus({ workspace = "emptyn" })                           -- 下一个空工作区
```

### 9.4 显示器选择器

| 形式 | 说明 |
|---|---|
| 显示器对象 | 直接传对象 |
| 显示器 ID | 数字 ID |
| output 选择器 | 端口名或 `desc:` 描述 |
| 方向 | 左/右/上/下（见 4.5） |
| `current` | 当前显示器 |

```lua
hl.dsp.focus({ monitor = "DP-2" })                 -- 按端口名
hl.dsp.focus({ monitor = "desc:Chimei Innolux Corporation 0x150C" })  -- 按描述
hl.dsp.focus({ monitor = "current" })
hl.dsp.focus({ monitor = "l" })                    -- 左边那台
```

### 9.5 方向选择器

| 值 | 含义 |
|---|---|
| `l` / `left` | 左 |
| `r` / `right` | 右 |
| `u` / `up` | 上 |
| `d` / `down` | 下 |

```lua
hl.dsp.window.move({ window = "activewindow", direction = "l" })
hl.dsp.focus({ direction = "r" })
```

## 10. 显示器与动画配置

### 10.1 `hl.monitor` 字段

除 `output` 外全部可选，未写则取默认值。

| 字段 | 类型 | 默认 | 说明 |
|---|---|---|---|
| `output` | string | 必填 | 输出名，或 `desc:...` 描述前缀 |
| `disabled` | bool | `false` | 从布局中移除该显示器 |
| `mode` | string | `"preferred"` | 分辨率与刷新率（如 `"1920x1080@144"`），或 `"preferred"`/`"highres"`/`"highrr"`/`"maxwidth"` |
| `scale` | float/string | `"auto"` | 缩放；`"auto"` 按显示器 PPI 决定 |
| `transform` | int | `0` | 旋转/翻转，0–7，见 5.4 |
| `position` | string | `"auto"` | 虚拟布局中的位置（如 `"1920x0"`），见 5.4 |
| `mirror` | string | 空 | 要镜像的输出名 |
| `bitdepth` | int | `8` | 位深：`8` 或 `10` |
| `cm` | string | `"srgb"` | 色彩管理预设，见 5.5 |
| `sdr_eotf` | string | `"default"` | SDR 传输函数：`"default"`/`"gamma22"`/`"srgb"` |
| `vrr` | int | `0` | VRR 模式，见 5.3 |
| `icc` | string | 空 | ICC 配置文件**绝对路径** |
| `reserved_area` | css_gaps | `0` | 预留区：单个 int（四边）或按边的表 |
| `supports_wide_color` | int | `0` | 强制广色域：`-1` 关、`0` 自动、`1` 开 |
| `supports_hdr` | int | `0` | 强制 HDR 支持：`-1` 关、`0` 自动、`1` 开 |
| `sdrbrightness` | float | `1.0` | HDR 模式下的 SDR 亮度 |
| `sdrsaturation` | float | `1.0` | HDR 模式下的 SDR 饱和度 |
| `sdr_min_luminance` | float | `0.2` | SDR→HDR 映射的 SDR 最低亮度 |
| `sdr_max_luminance` | int | `80` | SDR 最高亮度 |
| `min_luminance` | float | `-1` | 显示器最低亮度 |
| `max_luminance` | int | `-1` | 显示器最大可能亮度 |
| `max_avg_luminance` | int | `-1` | 显示器最大平均亮度 |

`output` 留空即“兜底规则”：未被显式规则匹配的显示器都用它。

```lua
hl.monitor({ output = "", mode = "preferred", position = "auto", scale = 1 })
```

`reserved_area` 叠加在自动计算的预留区（如状态栏）之上，每台显示器只能写一条：`reserved_area = 10`（四边）或 `reserved_area = { top = 10, bottom = 10, left = 0, right = 0 }`。

### 10.2 常用示例

```lua
-- 4K 缩放：3840x2160 用 scale 2 → 逻辑 1920x1080
hl.monitor({ output = "DP-1", mode = "3840x2160@120", position = "0x0", scale = 2 })

-- 竖屏（90°）笔记本屏
hl.monitor({ output = "eDP-1", mode = "2880x1800@90", position = "0x0", scale = 1, transform = 1 })

-- 双屏：DP-2 在 DP-1 右侧
hl.monitor({ output = "DP-1", mode = "1920x1080@120Hz", position = "0x0",    scale = 1 })
hl.monitor({ output = "DP-2", mode = "1920x1080@120Hz", position = "1920x0", scale = 1 })

-- 镜像：DP-3 镜像 DP-2；其余（兜底）镜像 DP-1
hl.monitor({ output = "DP-3", mode = "1920x1080@60", position = "0x0", scale = 1, mirror = "DP-2" })
hl.monitor({ output = "", mode = "preferred", position = "auto", scale = 1, mirror = "DP-1" })

-- 关闭显示器：其窗口与工作区会挪到剩余显示器
hl.monitor({ output = "name", disabled = true })
```

> 只想“像屏保一样关屏”请用 `dpms` dispatcher，不要 disable。

### 10.3 模式、modeline 与 VRR

预定义模式**不能组合**，只能选一个：`preferred`（显示器偏好）、`highres`（最高分辨率）、`highrr`（最高刷新率）、`maxwidth`（最宽分辨率）。可用模式见 `hyprctl monitors` 的 `availableModes`（按分辨率降序，可能有重复或刷新率略偏）。

```lua
hl.monitor({ output = "DP-1", mode = "modeline 1071.101 3840 3848 3880 3920 2160 2263 2271 2277 +hsync -vsync" })
```

VRR（`vrr = 3` 即全屏且内容为 `video`/`game`）：`-1` 跟随全局、`0` 关、`1` 开、`2` 仅全屏、`3` 全屏且内容类型为 `video` 或 `game`。

> 镜像不会重新渲染：1080p 镜像到 4K 屏仍是 1080p；宽高比不同（16:9 / 16:10）会被拉伸压缩。

### 10.4 位置与旋转

位置按**缩放（及旋转）后**的分辨率计算：4K（scale 2）在 1080p 左边时，1080p 屏写 `1920x0`（3840 / 2）；该 4K 屏若再转 90°，则写 `1080x0`。显示器**不能重叠**，重叠会告警且不注册。

| `position` 值 | 含义 |
|---|---|
| `auto` | Hyprland 决定；默认放已有显示器右侧，以左上角为基准 |
| `auto-right` / `auto-left` / `auto-up` / `auto-down` | 放到右/左/上/下，以左上角为基准 |
| `auto-center-right` / `auto-center-left` / `auto-center-up` / `auto-center-down` | 同上，但以显示器中心为基准 |

方向始终“由中心向外”；首个输出若给了方向会被忽略并放在 `(0,0)`；允许重复方向。

```lua
-- DP-2 在 DP-1 右侧（等价 position = "-1920x0"）；上一行/下一行同理
hl.monitor({ output = "DP-2", mode = "1920x1080@120Hz", position = "1920x0", scale = 1 })
hl.monitor({ output = "DP-2", mode = "1920x1080@120Hz", position = "0x-1080", scale = 1 })
hl.monitor({ output = "DP-2", mode = "1920x1080@120Hz", position = "0x1080",  scale = 1 })
```

`transform`：

| 值 | 含义 | 值 | 含义 |
|---|---|---|---|
| `0` | 正常 | `4` | 翻转 |
| `1` | 90° | `5` | 翻转 + 90° |
| `2` | 180° | `6` | 翻转 + 180° |
| `3` | 270° | `7` | 翻转 + 270° |

缩放必须能整除分辨率且无小数，否则告警：`1920×1080 / 1.5 = 1280×720` 合法；`/ 1.4 = 1371.4286×771.42857` 不合法。

### 10.5 颜色管理、10bit 与 ICC

`cm` 预设：`auto`（8bpc 用 `srgb`、10bpc 且支持时用 `wide`，推荐）、`srgb`（默认）、`dcip3`、`dp3`（Apple P3）、`adobe`、`wide`（BT2020）、`edid`（已知不准确）、`hdr`（广色域 + HDR PQ，实验性）、`hdredid`（同 hdr 但用 EDID 色域，实验性）。

```lua
hl.monitor({ output = "eDP-1", cm = "hdr", sdrbrightness = 1.2, sdrsaturation = 0.98 })
```

- 开启 `render:cm_auto_hdr` 时，不设 `cm = "hdr"` 也能全屏 HDR。
- `sdrbrightness` / `sdrsaturation` 默认 `1.0`，亮度常用 `1.0 – 2.0`。
- `sdr_eotf` 默认 `"default"`，跟随 `render:cm_sdr_eotf`；可改 `"srgb"`（分段）或 `"gamma22"`。
- 支持时推荐 `bitdepth = 10`：有些屏是 8bit+FRC 模拟，可能伤眼；Hyprland 自身颜色（如边框）不支持 10bit；部分应用在 10bit 下无法截屏。

```lua
hl.monitor({ output = "DP-1", bitdepth = 10 })
hl.monitor({ output = "DP-1", icc = "/path/to/icc.icm" })
```

ICC：路径必须绝对；会强制该屏 `sdr_eotf = sRGB`；会覆盖 CM 预设；与 HDR 游戏本质上不兼容。

### 10.6 动画：`hl.animation` 与 `hl.curve`

#### 5.6.1 语法

```lua
hl.animation({ leaf = string, enabled = bool, speed = float, curve = string, style? = string })
```

| 参数 | 说明 |
|---|---|
| `leaf` | 动画作用域，见 5.6.2 |
| `enabled` | `true` 启用 / `false` 禁用；为 `false` 时其余参数可省 |
| `speed` | **分秒**数（1 = 100ms），如 `speed = 1` 即 100ms |
| `curve` | 曲线名，见 5.6.3；文档示例中也可写 `bezier = "..."` / `spring = "..."` |
| `style` | 动画样式，取值见动画树 |

#### 5.6.2 动画树

未设置的节点继承父节点。

```text
global
  ↳ windows - styles: slide, popin, gnomed
    ↳ windowsIn（打开）/ windowsOut（关闭）- styles 同 windows
    ↳ windowsMove - 移动/拖拽/缩放等中间过程
  ↳ layers - styles: slide, popin, fade
    ↳ layersIn（打开）/ layersOut（关闭）
  ↳ fade
    ↳ fadeIn / fadeOut - 窗口打开/关闭
    ↳ fadeSwitch - 切换活动窗口及其透明度
    ↳ fadeShadow / fadeGlow - 切换活动窗口的阴影/发光
    ↳ fadeDim - 非活动窗口变暗缓动
    ↳ fadeLayers（fadeLayersIn / fadeLayersOut）
    ↳ fadePopups（fadePopupsIn / fadePopupsOut）- Wayland 弹窗
    ↳ fadeDpms - dpms 切换
  ↳ border - 边框颜色切换速度
  ↳ borderangle / shadowangle / glowangle - 渐变角度，styles: once（默认）, loop
  ↳ workspaces - styles: slide, slidevert, fade, slidefade, slidefadevert
    ↳ workspacesIn / workspacesOut - styles 同 workspaces
    ↳ specialWorkspace（specialWorkspaceIn / specialWorkspaceOut）
  ↳ zoomFactor - 屏幕缩放
  ↳ monitorAdded - 新增显示器缩放动画
```

> `*angle` 用 `loop` 会让 Hyprland 按刷新率持续渲染新帧（60Hz 屏即每秒 60 帧），即使动画关闭或装饰不可见也如此，费电。

#### 5.6.3 曲线

```lua
hl.curve( NAME, { type = "bezier", points = { {X0, Y0}, {X1, Y1} } })   -- 三次贝塞尔，中间两点可配
hl.curve(NAME, { type = "spring", mass = float, stiffness = float, damping = float })

hl.curve( "overshoot", { type = "bezier", points = { {0.5, 0.9}, {0.1, 1.1} } } )
hl.curve( "rubber",    { type = "spring", mass = 1, stiffness = 70, damping = 10 } )
```

- Spring 一般保持 `mass = 1`，只调 stiffness/damping：stiffness 越大越快，damping 越大回弹越少。
- 阻尼比 ζ = c / (2·√(k·m))：`ζ = 1` 临界阻尼（快速稳定、不过冲）；`ζ > 1` 过阻尼（缓慢回归、不振荡）；`ζ < 1` 欠阻尼（振荡、振幅指数衰减）。实用上 damping 取 `0.6 – 0.8` 比较跟手。

样式附加参数：

```lua
hl.animation({ leaf = "windows", enabled = true, speed = 8, curve = "default", style = "popin 80%" })    -- 从 80% 缩放
hl.animation({ leaf = "workspaces", enabled = true, speed = 8, curve = "default", style = "slidefade 20%" }) -- 移动 20% 屏宽
hl.animation({ leaf = "windows", enabled = true, speed = 8, curve = "default", style = "slide left" })   -- 强制方向 top/bottom/left/right
```

#### 5.6.4 两套完整示例

快（响应优先，100–200ms）：

```lua
hl.curve("sharp", { type = "bezier", points = { {0.2, 0.0}, {0.1, 1.0} } })

hl.animation({ leaf = "global",    enabled = true, speed = 3, curve = "sharp" })
hl.animation({ leaf = "windows",   enabled = true, speed = 2, curve = "sharp", style = "popin 85%" })
hl.animation({ leaf = "workspaces",enabled = true, speed = 2, curve = "sharp", style = "slidefade 15%" })
hl.animation({ leaf = "fade",      enabled = true, speed = 3, curve = "sharp" })
hl.animation({ leaf = "layers",    enabled = true, speed = 2, curve = "sharp", style = "fade" })
```

柔和（弹簧 + 淡入淡出，300ms 量级）：

```lua
hl.curve("soft",   { type = "spring", mass = 1, stiffness = 55, damping = 12 })
hl.curve("gentle", { type = "bezier", points = { {0.25, 0.1}, {0.25, 1.0} } })

hl.animation({ leaf = "global",     enabled = true, speed = 6, curve = "gentle" })
hl.animation({ leaf = "windows",    enabled = true, speed = 6, curve = "soft", style = "popin 80%" })
hl.animation({ leaf = "workspaces", enabled = true, speed = 6, curve = "gentle", style = "slidefade 20%" })
hl.animation({ leaf = "fade",       enabled = true, speed = 7, curve = "gentle" })
hl.animation({ leaf = "border",     enabled = true, speed = 4, curve = "gentle" })
hl.animation({ leaf = "layers",     enabled = true, speed = 4, curve = "gentle", style = "popin" })
```

### 10.7 环境变量与自启动

#### 5.7.1 `hl.env`

在显示服务器初始化**之前**设置环境变量；引用已有变量用 `os.getenv()`：

```lua
hl.env("GTK_THEME", "Nord")
hl.env("SSH_AUTH_SOCK", os.getenv("XDG_RUNTIME_DIR") .. "/ssh-agent.socket")
```

> 不要把 Wayland 专用变量写进 `/etc/environment`：传统发行版上所有会话（含 Xorg）都会继承，容易搞坏 Xorg 会话。

常用变量（文档列举）：

| 变量 | 作用 |
|---|---|
| `HYPRLAND_TRACE=1` | 更详细日志 |
| `HYPRLAND_NO_RT=1` | 禁止设置实时优先级 |
| `HYPRLAND_NO_SD_NOTIFY=1` | systemd 下不发 `sd_notify` |
| `HYPRLAND_NO_SD_VARS=1` | 不管理 systemd / D-Bus 激活环境中的变量 |
| `HYPRLAND_CONFIG=/path/to/hyprland.lua` | 指定配置文件位置 |
| `AQ_TRACE=1` | Aquamarine 详细日志（非常啰嗦） |
| `AQ_DRM_DEVICES=...` | DRM 设备（GPU）列表，冒号分隔，首个为主 GPU，如 `/dev/dri/card1:/dev/dri/card0` |
| `AQ_FORCE_LINEAR_BLIT=0` | 关闭多 GPU 缓冲的强制线性 modifier（可绕过部分 NVIDIA 问题） |
| `AQ_NO_KMS_REQUIREMENT=1` | 无头 GPU 启动不再要求 KMS |
| `AQ_NO_ATOMIC=1` | 关闭原子模式设置（**强烈不建议**） |
| `XCURSOR_THEME` / `XCURSOR_SIZE` | 光标主题 / 大小 |
| `HYPRCURSOR_THEME` / `HYPRCURSOR_SIZE` | hyprcursor 主题 / 大小 |
| `QT_QPA_PLATFORMTHEME=qt6ct` | Qt 从 qt6ct 取主题 |
| `QT_AUTO_SCREEN_SCALE_FACTOR=1` | 按像素密度自动缩放 |
| `QT_WAYLAND_DISABLE_WINDOWDECORATION=1` | 关闭 Qt 窗口装饰 |
| `GTK_THEME=...` | 手动指定 GTK 主题 |
| `GDK_BACKEND=wayland,x11,*` | GTK 后端优先级 |
| `QT_QPA_PLATFORM=wayland;xcb` | Qt 后端优先级 |
| `SDL_VIDEODRIVER=wayland` | SDL2 走 Wayland |
| `CLUTTER_BACKEND=wayland` | 强制 Clutter 用 Wayland 后端 |

#### 5.7.2 自启动：`hl.on("hyprland.start")`

文档用 `hyprland.start` 事件做自启动（`exec-once` 属旧 hyprlang，本套 Lua 文档不出现）：

```lua
hl.on("hyprland.start", function()
    hl.exec_cmd(terminal)
    hl.exec_cmd("nm-applet")
    hl.exec_cmd("waybar & hyprpaper & firefox") -- 一次启动 waybar、hyprpaper、firefox
end)

hl.on("hyprland.shutdown", function()           -- 退出时
    hl.exec_cmd("notify-send 'bye'")
end)
```

> `hyprland.start` 每个会话只触发一次，配置热重载不会重跑已注册的监听器。若在手动重载路径里再调启动逻辑，请自行保证幂等（如先 `pgrep` 判断再启动），避免出现两份状态栏。
