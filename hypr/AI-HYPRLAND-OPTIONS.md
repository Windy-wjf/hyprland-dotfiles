# Hyprland 配置选项全集（AI 速查）

> 本文件是 `hyprland.lua` 里 `hl.config()` 能设置的全部选项，按 category 分组。
> 数据来源：Hyprland 官方 wiki（wiki.hypr.land，2026-11 更新），对应本机 **Hyprland 0.57.2**。
> 配套文件：`AI-HYPRLAND-GUIDE.md`（怎么改、配方、验证）、`AI-HYPRLAND-DISPATCHERS-RULES.md`（快捷键/规则/选择器）。

## 怎么用

1. **先定位 category**：每个小节标题就是 category，例如 `### general（常规）` 表示
   `hl.config({ general = { ... } })`；`#### decoration.blur（模糊）` 表示
   `hl.config({ decoration = { blur = { ... } } })`（点号即嵌套层级）。
2. **选项名一律用下划线**：`tap_to_click`、`follow_mouse`、`natural_scroll`。
   写成连字符（`tap-to-click`）是**老 hyprlang 语法**，在 Lua 配置里无效。
3. **查找某个选项**：直接在本文件里搜选项名即可（例如搜 `preserve_split`）。
   不要凭记忆写选项名，写错会导致整份配置加载失败。
4. **写值**：`hl.config({ ["general.gaps_in"] = 4 })` 或嵌套表写法，两种等价。
   同一选项写多次时**最后一条生效**。
5. **类型/默认值/范围**见每行表格的 Type / Default / Limits 三列
   （`[[Empty]]` = 空字符串，`[[Auto]]` = 自动，Limits 为空 = 无限制）。

## 本机当前显式设置的值（基线，改之前先看这里）

| 选项 | 当前值 | 说明 |
|---|---|---|
| `general.gaps_in` | `3` | 窗口间距 |
| `general.gaps_out` | `6` | 屏幕边缘间距 |
| `general.border_size` | `1` | 边框粗细 |
| `general.col.active_border` | 渐变 `rgba(33ccffee) → rgba(00ff99ee)`，angle 45 | 活动窗口边框 |
| `general.col.inactive_border` | `rgba(595959aa)` | 非活动边框 |
| `general.resize_on_border` | `true` | 拖边框改大小 |
| `general.extend_border_grab_area` | `15` | 边框可拖动扩展区 |
| `general.allow_tearing` | `false` | 允许撕裂 |
| `general.layout` | `"dwindle"` | 平铺布局 |
| `decoration.rounding` | `10` | 圆角 |
| `decoration.rounding_power` | `2` | 圆角曲线 |
| `decoration.active_opacity` | `1.0` | 活动窗口不透明度 |
| `decoration.inactive_opacity` | `1.0` | 非活动窗口不透明度 |
| `decoration.shadow.enabled` | `true` | 阴影 |
| `decoration.shadow.range` | `4` | 阴影范围 |
| `decoration.shadow.render_power` | `3` | 阴影精度 |
| `decoration.shadow.color` | `0xee1a1a1a` | 阴影色 |
| `decoration.blur.enabled` | `true` | 模糊 |
| `decoration.blur.size` | `3` | 模糊尺寸 |
| `decoration.blur.passes` | `1` | 模糊迭代次数 |
| `decoration.blur.vibrancy` | `0.1696` | 取色增强 |
| `animations.enabled` | `true` | 动画总开关 |
| `dwindle.preserve_split` | `true` | 保持分割方向 |
| `master.new_status` | `"master"` | 新窗口成为主窗口 |
| `scrolling.fullscreen_on_one_column` | `true` | 单列时全屏 |
| `misc.force_default_wallpaper` | `-1` | 随机默认壁纸 |
| `misc.disable_hyprland_logo` | `false` | 显示 Hyprland logo |
| `layers.allow_new_top_layers_over_existing_fullscreen` | `true` | 新顶层覆盖全屏 |
| `input.kb_layout` | `"us"` | 键盘布局 |
| `input.follow_mouse` | `1` | 聚焦跟随鼠标 |
| `input.sensitivity` | `0` | 鼠标灵敏度 |
| `input.touchpad.natural_scroll` | `false` | 触摸板自然滚动 |

动画曲线：`easeOutQuint` `easeInOutCubic` `linear` `almostLinear` `quick`（bezier）+
`easy`（spring: mass 1 / stiffness 238.1191 / damping 24.21279333，ζ≈0.78）。

---

# 一、通用选项

### general（常规）

| Name | Description | Type | Default | Limits |
|----|----|----|----|----|
| allow_tearing | 允许发生撕裂的总开关。参见 Tearing page | bool | `false` |  |
| border_size | 窗口周围边框的大小 | int | `1` | \[0 - 20\] |
| extend_border_grab_area | 扩展边框周围可点击并拖拽的区域，仅在开启 `general.resize_on_border` 时使用 | int | `15` | \[0 - 100\] |
| float_gaps | 浮动窗口与窗口及显示器边缘之间的间隙，`-1` 表示使用默认值 | css_gaps | `0` |  |
| gaps_in | 窗口之间的间隙 | css_gaps | `5` |  |
| gaps_out | 窗口与显示器边缘之间的间隙 | css_gaps | `20` |  |
| gaps_workspaces | 工作区之间的间隙。与 gaps_out 叠加 | int | `0` | \[0 - 100\] |
| hover_icon_on_border | 悬停在边框上时显示光标图标，仅在开启 `general.resize_on_border` 时使用 | bool | `true` |  |
| layout | 使用哪种布局。可选值：`"dwindle"`/`"master"`/`"scrolling"`/`"monocle"` | string | `"dwindle"` |  |
| locale | 覆盖系统区域设置，例如 `"en_US"`、`"es"` | string | \[\[Empty\]\] |  |
| modal_parent_blocking | 模态窗口的父窗口是否可交互 | bool | `true` |  |
| no_focus_fallback | 若为 true，在某个方向移动焦点而未找到窗口时，不会回退到下一个可用窗口 | bool | `false` |  |
| resize_corner | 调整浮动窗口大小时强制使用指定角（从左上角开始顺时针 1-4，0 表示禁用） | int | `0` | \[0 - 4\] |
| resize_on_border | 允许通过点击并拖拽边框和间隙来调整窗口大小 | bool | `false` |  |

#### general.col（常规颜色）

| Name | Description | Type | Default | Limits |
|----|----|----|----|----|
| active_border | 活动窗口的边框颜色 | gradient | `0xffffffff` |  |
| inactive_border | 非活动窗口的边框颜色 | gradient | `0xff444444` |  |
| nogroup_border | 无法加入组的非活动窗口的边框颜色 | gradient | `0xffffaaff` |  |
| nogroup_border_active | 无法加入组的活动窗口的边框颜色 | gradient | `0xffff00ff` |  |

#### general.snap（吸附）

| Name | Description | Type | Default | Limits |
|----|----|----|----|----|
| enabled | 为浮动窗口启用吸附 | bool | `false` |  |
| border_overlap | 若启用，窗口吸附后彼此之间只间隔一条边框的宽度 | bool | `false` |  |
| respect_gaps | 若启用，吸附会遵循窗口之间的间隙（在 general:gaps_in 中设置） | bool | `false` |  |
| monitor_gap | 吸附前窗口与显示器边缘之间的最小间隙（像素） | int | `10` | \[0 - 100\] |
| window_gap | 吸附前窗口之间的最小间隙（像素） | int | `10` | \[0 - 100\] |

### decoration（装饰）

| Name | Description | Type | Default | Limits |
|----|----|----|----|----|
| active_opacity | 活动窗口的不透明度 | float | `1.0` | \[0.0 - 1.0\] |
| border_part_of_window | 窗口边框是否属于窗口的一部分 | bool | `true` |  |
| dim_around | `dim_around` 窗口规则应使窗口变暗的程度 | float | `0.4` | \[0.0 - 1.0\] |
| dim_inactive | 启用非活动窗口变暗 | bool | `false` |  |
| dim_modal | 启用模态窗口父窗口的变暗 | bool | `true` |  |
| dim_special | 打开特殊工作区时屏幕其余部分变暗的程度。\[0.0 - 1.0\] | float | `0.2` |  |
| dim_strength | 非活动窗口应被变暗的程度 | float | `0.5` | \[0.0 - 1.0\] |
| fullscreen_opacity | 全屏窗口的不透明度 | float | `1.0` | \[0.0 - 1.0\] |
| inactive_opacity | 非活动窗口的不透明度 | float | `1.0` | \[0.0 - 1.0\] |
| rounding | 圆角半径（以布局像素为单位） | int | `0` | \[0 - 100\] |
| rounding_power | 调整用于圆角的曲线，数值越大越平滑，1.0 为三角形角，2.0 为圆形，4.0 为方圆形 | float | `2.0` | \[1.0 - 10.0\] |
| screen_shader | 在渲染结束时应用的自定义着色器路径。示例参见 `examples/screenShader.frag` | string | \[\[Empty\]\] |  |

#### Opacity（不透明度）

不透明度是所有不透明度的**乘积**。在不透明度值后使用 `"override"`，可将其设为精确值而非乘数。

例如，将 `active_opacity` 设为 `0.5`、`opacity` 窗口规则设为 `0.5`，总结果为 `0.25`。

重要

允许使用超过 `1.0` 的不透明度，但任何超过 `1.0` 的乘积都会导致图形故障。

**示例**

```
-- Active 0.8, inactive 0.8, fullscreen 1.0 regardless of other rules:
hl.window_rule({
  match   = { class = "kitty" },
  opacity = "0.8 override 0.8 override 1.0 override",
})
```

#### decoration.blur（模糊）

| Name | Description | Type | Default | Limits |
|----|----|----|----|----|
| enabled | 启用 kawase 窗口背景模糊 | bool | `true` |  |
| brightness | 模糊的亮度调制 | float | `1` | \[0.0 - 2.0\] |
| contrast | 模糊的对比度调制 | float | `0.8916` | \[0.0 - 2.0\] |
| ignore_opacity | 让模糊层忽略窗口的不透明度 | bool | `true` |  |
| input_methods | 是否模糊输入法窗口，例如 `fcitx5` | bool | `false` |  |
| input_methods_ignorealpha | 作用类似图层规则中的 ignore_alpha。若像素不透明度低于设定值，则不进行模糊 | float | `0.2` | \[0.0 - 1.0\] |
| new_optimizations | 是否对模糊启用进一步优化。建议保持开启，可大幅提升性能 | bool | `true` |  |
| noise | 应用的噪点量 | float | `0.0117` | \[0.0 - 1.0\] |
| passes | 执行的遍数 | int | `1` | \[0 - 10\] |
| popups | 是否模糊弹出窗口，例如 `right-click menus` | bool | `false` |  |
| popups_ignorealpha | 作用类似图层规则中的 ignore_alpha。若像素不透明度低于设定值，则不进行模糊 | float | `0.2` | \[0.0 - 1.0\] |
| proportional | 若启用，模糊强度将与像素不透明度成正比。需要 `render:use_shader_blur_blend` | bool | `false` |  |
| size | 模糊大小（距离） | int | `8` |  |
| special | 是否在特殊工作区背后进行模糊（注意：开销较大） | bool | `false` |  |
| variant | 模糊图案变体。可能显著增加 GPU 和 CPU 占用 | string | `kawase` | see below |
| vibrancy | 提高模糊颜色的饱和度 | float | `0.1696` | \[0.0 - 1.0\] |
| vibrancy_darkness | `vibrancy` 对暗部区域的效果强度 | float | `0.0` | \[0.0 - 1.0\] |
| xray | 若启用，浮动窗口的模糊将忽略平铺窗口。可显著降低浮动模糊的开销。若 `new_optimizations = false` 则禁用 | bool | `false` |  |

注意

`blur.size` 和 `blur.passes` 必须至少为 1 才能应用模糊。

增大 `blur.passes` 是必要的，可避免在较高的 `blur.size` 值下模糊效果异常，但请记住更高的 `blur.passes` 会给 GPU 带来更大负担。

若启用后模糊在某些窗口中不起作用，它可能受客户端设置控制。参见 FAQ。

##### Blur variants（模糊变体）

部分选项可能被不同的模糊方法复用。

可用变体：

- `kawase` - 默认
- `acrylic` - 类似液态玻璃
- `aurora` - 类似极光的光带
- `drops` - 窗玻璃上的雨滴
- `fluid_jar` - 2D 流体模拟
- `frost` - 碎裂的冰
- `haze` - 另一种漫射效果
- `heat_shimmer` - 带色差的小幅闪光
- `prism` - 三角形折射遮罩
- `ripple` - 点击时的涟漪
- `water` - 使用高度图实现的涟漪

###### decoration.blur.acrylic（丙烯酸）

用于：`acrylic`

| Name | Description | Type | Default | Limits |
|----|----|----|----|----|
| aberration | 丙烯酸透镜中的相对色散 | float | `0.025` | \[0.0 - 0.25\] |
| bulb | 弯曲丙烯酸边缘的宽度（像素） | float | `48.0` | \[4.0 - 256.0\] |
| clarity | 穿过丙烯酸表面的清晰背景量 | float | `0.82` | \[0.0 - 1.0\] |
| refraction | 丙烯酸透镜的最大位移（像素） | float | `24.0` | \[0.0 - 48.0\] |
| tint | 丙烯酸色调颜色。Alpha 通道控制光学吸收 | color | `0x14EEF5FF` |  |

###### decoration.blur.aurora（极光）

用于：`aurora`

| Name | Description | Type | Default | Limits |
|----|----|----|----|----|
| color1 | 第一层极光光幕的颜色。Alpha 控制其贡献度 | color | `0x29F0A0FF` |  |
| color2 | 第二层极光光幕的颜色。Alpha 控制其贡献度 | color | `0x7A4DFFFF` |  |
| intensity | 极光颜色贡献的强度 | float | `0.35` | \[0.0 - 1.0\] |
| speed | 动画速度。0 会冻结动画 | float | `1.0` | \[0.0 - 10.0\] |

###### decoration.blur.drops（水滴）

用于：`drops`

| Name | Description | Type | Default | Limits |
|----|----|----|----|----|
| speed | 动画速度。0 会禁用动画 | float | `3.0` | \[0.0 - 10.0\] |

###### decoration.blur.fluid_jar（流体罐）

用于：`fluid_jar`

| Name | Description | Type | Default | Limits |
|----|----|----|----|----|
| color | 流体颜色 | color | `0xCC3399FF` |  |
| distortion | 流体折射畸变倍率 | float | `8.0` | \[0.0 - 10.0\] |
| fill_amount | 流体的填充高度 | float | `0.5` | \[0.0 - 1.0\] |
| mass | 流体的惯性质量 | float | `1.4` | \[0.1 - 10.0\] |
| precision | 流体模拟精度倍率。2x 是较好的折中，4x 开销较大，8x 极端且没有必要 | float | `2.0` | \[0.5 - 8.0\] |
| speed | 动画速度 | float | `3.7` | \[0.0 - 10.0\] |
| turbulence | 内部流体湍流倍率 | float | `1.2` | \[0.0 - 5.0\] |

###### decoration.blur.glass（玻璃）

用于：`aurora`、`drops`、`heat_shimmer`、`prism`

| Name | Description | Type | Default | Limits |
|----|----|----|----|----|
| refraction | 玻璃类模糊的最大折射位移（像素） | float | `20.0` | \[0.0 - 20.0\] |
| roughness | 玻璃浮雕明暗的强度 | float | `1.0` | \[0.0 - 1.0\] |
| size | 玻璃类模糊的图案大小（像素） | float | `40.0` | \[4.0 - 512.0\] |

###### decoration.blur.haze（薄雾）

用于：`haze`

| Name | Description | Type | Default | Limits |
|----|----|----|----|----|
| intensity | 薄雾珠光光泽的强度 | float | `0.35` | \[0.0 - 1.0\] |
| iridescence | 薄雾珠光色偏的强度 | float | `0.7` | \[0.0 - 1.0\] |

###### decoration.blur.heat_shimmer（热浪）

用于：`heat_shimmer`

| Name | Description | Type | Default | Limits |
|----|----|----|----|----|
| speed | 动画速度。0 会禁用动画 | float | `1.0` | \[0.0 - 10.0\] |

###### decoration.blur.ripple（涟漪）

用于：`ripple`

| Name | Description | Type | Default | Limits |
|----|----|----|----|----|
| duration | 持续时间（秒） | float | `0.45` | \[0.05 - 5.0\] |
| radius | 最大半径（像素） | float | `400.0` | \[1.0 - 1000.0\] |
| strength | 最大折射位移（像素） | float | `30.0` | \[0.0 - 32.0\] |
| width | 水波的宽度（像素） | float | `32.0` | \[1.0 - 200.0\] |

###### decoration.blur.water（水波）

用于：`water`

| Name | Description | Type | Default | Limits |
|----|----|----|----|----|
| damping | 衰减阻尼 | float | `0.95` | \[0.0 - 1.0\] |
| duration | 最长持续时间（秒） | float | `12.0` | \[0.5 - 60.0\] |
| radius | 指针半径（像素） | float | `20.0` | \[1.0 - 1000.0\] |
| speed | 传播速度 | float | `0.76` | \[0.0 - 10.0\] |
| strength | 最大折射位移与注入强度（像素） | float | `32.0` | \[0.0 - 32.0\] |

#### decoration.shadow（阴影）

| Name | Description | Type | Default | Limits |
|----|----|----|----|----|
| enabled | 为窗口启用投影 | bool | `true` |  |
| color | 活动窗口阴影的颜色。Alpha 决定不透明度 | color/gradient | `0xee1a1a1a` |  |
| color_inactive | 非活动窗口阴影的颜色。若未设置，将回退到 `color` | color/gradient | \[\[Empty\]\] |  |
| offset | 阴影的渲染偏移 | vec2 | `{0, 0}` |  |
| range | 阴影范围（大小），单位为像素 | int | `4` | \[0 - 100\] |
| render_power | 衰减的渲染幂次。幂次越大，衰减越快 | int | `3` | \[1 - 4\] |
| scale | 阴影的缩放 | float | `1.0` | \[0.05 - 2.0\] |
| sharp | 若启用，阴影会变得锐利，类似无限大的渲染幂次 | bool | `false` |  |

#### decoration.glow（发光）

| Name | Description | Type | Default | Limits |
|----|----|----|----|----|
| enabled | 为窗口启用内发光 | bool | `false` |  |
| color | 活动窗口发光的颜色。Alpha 决定不透明度 | gradient | `0xee1a1a1a` |  |
| color_inactive | 非活动窗口发光的颜色。若未设置，将回退到 `color` | gradient | \[\[Empty\]\] |  |
| range | 发光范围（大小），单位为像素 | int | `10` | \[0 - 100\] |
| render_power | 衰减的渲染幂次。幂次越大，衰减越快 | int | `3` | \[1 - 4\] |

#### decoration.motion_blur（动态模糊）

| Name | Description | Type | Default | Limits |
|----|----|----|----|----|
| enabled | 为移动或调整大小的窗口启用动态模糊 | bool | `false` |  |
| samples | 渲染的采样数量。数量越多模糊越清晰，但计算开销更大 | int | `7` | \[1 - 64\] |

#### decoration.wobble（晃动）

| Name | Description | Type | Default | Limits |
|----|----|----|----|----|
| enabled | 为移动或调整大小的窗口启用晃动 | bool | `false` |  |
| mesh | 每条边的晃动网格顶点数 | int | `12` | \[2 - 32\] |
| stiffness | 晃动形变的弹簧刚度 | float | `200` | \[0.0001 - 1000\] |
| damping | 晃动形变的弹簧阻尼 | float | `12` | \[0 - 1000\] |
| mass | 晃动形变的弹簧质量 | float | `1` | \[0.0001 - 1000\] |
| intensity | 晃动形变的冲量倍率 | float | `0.2` | \[0 - 2\] |
| value_epsilon | 位置 epsilon，低于该值时晃动视为稳定 | float | `0.25` | \[0 - 100\] |
| velocity_epsilon | 速度 epsilon，低于该值时晃动视为稳定 | float | `2` | \[0 - 1000\] |

### animations（动画）

| Name | Description | Type | Default | Limits |
|----|----|----|----|----|
| enabled | 启用动画 | bool | `true` |  |
| workspace_wraparound | 启用工作区环绕，使有方向性的工作区动画按首尾工作区彼此相邻的方式播放 | bool | `false` |  |

更多关于动画的内容可参阅 animations 页面。

### input（输入）

| Name | Description | Type | Default | Limits |
|----|----|----|----|----|
| accel_profile | 设置光标加速曲线。参见下方说明。留空则使用 `libinput` 针对你的输入设备的默认模式。参见 libinput#pointer-acceleration。可选项：`"adaptive"`/`"flat"`/`"custom"` | string | \[\[Empty\]\] |  |
| emulate_discrete_scroll | 由高分辨率滚动事件模拟离散滚动。`0` 禁用它，`1` 仅启用对非标准事件的处理，`2` 强制启用对所有滚轮事件的处理 | int | `1` | \[0 - 2\] |
| float_switch_override_focus | 若为 `1`/`2`，在平铺与浮动之间切换时焦点会转到光标下的窗口。若为 `2`，浮转到浮动的切换中焦点也会跟随鼠标。`0` 表示禁用 | int | `1` | \[0 - 2\] |
| focus_on_close | 控制窗口关闭时的焦点行为。设为 `0` 时，焦点会转到下一个候选窗口。设为 `1` 时，焦点会转到光标下的窗口。设为 `2` 时，焦点会转到最近使用/活动的窗口 | int | `0` | \[0 - 2\] |
| follow_mouse | 指定光标移动是否以及如何影响窗口焦点。参见下方说明 | int | `1` | \[0 - 3\] |
| follow_mouse_shrink | 按指定像素数缩小用于焦点检测的非活动窗口命中区域。这会在窗口之间的间隙中形成死区，移动光标不会改变焦点。仅在 `follow_mouse` 设为 `1` 时有效 | int | `0` | \[0 - 300\] |
| follow_mouse_threshold | 鼠标需要移动的最小逻辑像素距离，才会让其下的窗口获得焦点。仅在 `follow_mouse` 设为 `1` 时有效 | float | `0.0` |  |
| force_no_accel | 强制不进行光标加速。这会绕过你的大部分指针设置，以获得尽可能原始的输入信号。**不建议启用，因为可能导致光标不同步。** | bool | `false` |  |
| kb_file | 如果你愿意，可以使用指向自定义 .xkb 文件的路径 | string | \[\[Empty\]\] |  |
| kb_layout | 合适的 XKB keymap 参数 | string | `"us"` |  |
| kb_model | 合适的 XKB keymap 参数。参见下方说明 | string | \[\[Empty\]\] |  |
| kb_options | 合适的 XKB keymap 参数 | string | \[\[Empty\]\] |  |
| kb_rules | 合适的 XKB keymap 参数 | string | \[\[Empty\]\] |  |
| kb_variant | 合适的 XKB keymap 参数 | string | \[\[Empty\]\] |  |
| left_handed | 交换右键和左键 | bool | `false` |  |
| mouse_refocus | 若启用，指针越过窗口边界时鼠标焦点会切换到悬停的窗口。仅在 `follow_mouse` 设为 `1` 时有效 | bool | `true` |  |
| natural_scroll | 反转滚动方向。启用后，滚动会直接移动内容，而不是操纵滚动条 | bool | `false` |  |
| numlock_by_default | 默认启用 numlock | bool | `false` |  |
| off_window_axis_events | 处理聚焦窗口周边（平铺窗口为间隙/边框，浮动窗口为拖拽区/边框）的轴事件。`0` 忽略轴事件，`1` 发送越界坐标，`2` 将指针坐标伪造成窗口内最近的点，`3` 将光标 warp 到窗口内最近的点 | int | `1` | \[0 - 3\] |
| repeat_delay | 按住按键开始重复前的延迟，单位为毫秒 | int | `600` | \[0 - 2000\] |
| repeat_rate | 按住按键的重复速率，单位为每秒重复次数 | int | `25` | \[0 - 200\] |
| resolve_binds_by_sym | 决定使用多个布局时按键绑定的行为。若为 false，按键绑定始终按第一个指定布局处于活动状态来执行。若为 true，按符号指定的按键绑定会在你以当前布局输入相应符号时激活 | bool | `false` |  |
| rotation | 以度为单位设置设备相对于逻辑中性位置的顺时针旋转 | int | `0` | \[0 - 359\] |
| scroll_button | 设置滚动按钮。用 `wev` 查看 ID。`0` 表示默认 | int | `0` | \[0 - 300\] |
| scroll_button_lock | 若启用滚动按钮锁定，则无需一直按住该按钮。按下并释放按钮会切换按钮锁定，从逻辑上按住或释放该按钮。在按钮被逻辑按住期间，移动事件会被转换为滚动事件 | bool | `false` |  |
| scroll_points | 设置滚动加速曲线，需将 `accel_profile` 设为 `"custom"`。格式必须为 `"<step> <points>"`。留空则使用平坦的滚动曲线 | string | \[\[Empty\]\] |  |
| scroll_method | 设置滚动方式。附加信息：libinput#scrolling。可选项：`"2fg"`/`"edge"`/`"on_button_down"`/`"no_scroll"`（2fg 即双指） | string | \[\[Empty\]\] |  |
| scroll_factor | 为外接鼠标的滚动移动量增加的倍率。注意触摸板有单独的 scroll_factor 设置 | float | `1.0` | \[0 - 100\] |
| sensitivity | 设置鼠标输入灵敏度。附加信息：libinput#pointer-acceleration | float | `0.0` | \[-1.0 - 1.0\] |
| special_fallthrough | 若启用，特殊工作区中仅有浮动窗口时不会阻止聚焦常规工作区中的窗口 | bool | `false` |  |
| swallow_focus_click | 若启用，对未聚焦窗口的第一次点击只会使其聚焦，而不会转发点击动作。仅在鼠标焦点分离时相关，例如 `input.follow_mouse` 为 `0` 或 `2` | bool | `false` |  |

##### XKB keymap params（XKB 键位参数）

你可以在 `/usr/share/X11/xkb/rules/evdev.lst` 中找到模型、布局、变体和选项的列表。你也可以使用 `localectl` 命令查看你系统上可用的内容。

关于可切换的键盘配置，请参阅 binds 页面中对应的条目。

##### follow mouse（鼠标跟随）

- `0` - 光标移动不会改变焦点。
- `1` - 光标移动总会将焦点切换到光标下的窗口。
- `2` - 光标焦点与键盘焦点分离。点击窗口会将键盘焦点移到该窗口。
- `3` - 光标焦点与键盘焦点完全分离。点击窗口不会改变键盘焦点。

##### accel profile（加速曲线）

`custom <step> <points...>`

示例：`custom 200 0.0 0.5`

##### scroll points（滚动曲线）

`<step> <points...>`

示例：`0.2 0.0 0.5 1 1.2 1.5`

参见 libinput 文档以进一步了解其工作原理。

要模仿 Windows 的加速曲线，请参阅此脚本。

#### input.touchpad（触摸板）

| Name | Description | Type | Default | Limits |
|----|----|----|----|----|
| clickfinger_behavior | 用 1、2 或 3 根手指按键将分别映射为 LMB、RMB 和 MMB。这会禁用基于触摸板上点击位置的点击解释。附加信息：libinput#clickfinger-behavior | bool | `false` |  |
| disable_while_typing | 打字时禁用触摸板 | bool | `true` |  |
| drag_3fg | 启用三指拖拽。附加信息：libinput#drag-3fg | int | `0` | \[0 - 2\] |
| drag_lock | 启用后，拖拽时抬起手指不会放下被拖拽的项目。0 - 禁用，1 - 启用并带超时，2 - 启用粘滞。附加信息：libinput#tap-and-drag | int | `0` | \[0 - 2\] |
| flip_x | 反转触摸板的水平移动 | bool | `false` |  |
| flip_y | 反转触摸板的垂直移动 | bool | `false` |  |
| middle_button_emulation | 同时发送 LMB 和 RMB 将被解释为中键点击。这会禁用触摸板上原本会根据位置发送中键点击的任何区域。附加信息：libinput#middle-button-emulation | bool | `false` |  |
| natural_scroll | 反转滚动方向。启用后，滚动会直接移动内容，而不是操纵滚动条 | bool | `false` |  |
| scroll_factor | 应用于滚动移动量的倍率 | float | `1.0` | \[0.0 - 100\] |
| tap_and_drag | 设置触摸板的点按并拖拽模式 | bool | `true` |  |
| tap_button_map | 设置触摸板按键模拟的点按按钮映射。为空时默认为 `"lrm"`。L - 左，M - 中，R - 右 | string | \[\[Empty\]\] | “lrm”/“lmr” |
| tap_to_click | 用 1、2 或 3 根手指点按触摸板将分别发送 LMB、RMB 和 MMB | bool | `true` |  |

#### input.touchdevice（触摸设备）

| Name | Description | Type | Default | Limits |
|----|----|----|----|----|
| enabled | 是否为触摸设备启用输入 | bool | `true` |  |
| output | 绑定触摸设备的显示器。默认为自动检测。要停止自动检测，请使用空字符串 | string | \[\[Auto\]\] |  |
| transform | 变换来自触摸设备的输入。可用的变换与显示器的变换相同 | int | `0` | \[0 - 6\] |

#### input.virtualkeyboard（虚拟键盘）

| Name | Description | Type | Default | Limits |
|----|----|----|----|----|
| release_pressed_on_close | 关闭时释放虚拟键盘所有按下的按键 | bool | `false` |  |
| share_states | 与其他键盘统一按键按下状态和修饰键状态。0 - 否，1 - 是，2 - 是（IME 客户端除外） | int | `2` | \[0 - 2\] |

#### input.tablet（数位板）

| Name | Description | Type | Default | Limits |
|----|----|----|----|----|
| enabled | 是否为数位板启用输入 | bool | `true` |  |
| output | 绑定数位板的显示器。可以为 `"current"` 或显示器名称。留空则在所有显示器上映射 | string | \[\[Empty\]\] |  |
| transform | 变换来自数位板的输入。可用的变换与显示器的变换相同 | int | `0` | \[0 - 6\] |
| absolute_region_position | 是否将 `region_position` 视为显示器布局中的绝对位置。仅在 `output` 为空时适用 | bool | `false` |  |
| active_area_position | 活动区域的位置，单位为 mm | vec2 | `{0, 0}` | \[0 - 5000\] |
| active_area_size | 数位板活动区域的大小，单位为 mm | vec2 | `{0, 0}` | \[0 - 5000\] |
| left_handed | 若启用，数位板将旋转 180 度 | bool | `false` |  |
| region_position | 映射区域在显示器布局中的位置，相对于绑定的显示器或所有显示器的左上角 | vec2 | `{0, 0}` | \[-100000 - 100000\] |
| region_size | 映射区域的大小。设置此变量后，数位板输入将映射到该区域。`{0, 0}` 或无效大小表示未设置 | vec2 | `{0, 0}` | \[1 - 100000\] |
| relative_input | 输入是否应为相对坐标 | bool | `false` |  |

#### input.tablettool（数位板工具）

| Name | Description | Type | Default | Limits |
|----|----|----|----|----|
| eraser_button_mode | 更改工具上橡皮擦按钮的行为。设为 `0` 时使用工具的默认硬件行为。设为 `1` 时，工具上的橡皮擦按钮会改为发送按钮事件 | int | 0 | \[0 - 6\] |
| eraser_button_override | 当 eraser_button_mode 设为 `1` 时，设置某个按钮作为按钮事件。必须是有效的按钮（例如 BTN_STYLUS），排除虚拟按钮（例如 `BTN_TOOL\_\*`）和按键（KEY\_\*）。用 `wev` 查看 ID。`0` 表示默认 | int | 0 | \[0 - …\] |
| pressure_range_min | 设置该工具的最小压力范围。负值表示使用设备默认值。通常为 `0.0` | float | -1.0 | \[-1.0 - 1.0\] |
| pressure_range_max | 设置该工具的最大压力范围。负值表示使用设备默认值。通常为 `1.0` | float | -1.0 | \[-1.0 - 1.0\] |

### per-device input config（每设备输入配置）

详见 devices 页面。

### gestures（手势）

| Name | Description | Type | Default | Limits |
|----|----|----|----|----|
| close_max_timeout | 使用 1:1 手势时窗口关闭的超时时间，单位为 ms | int | `1000` | \[10 - 2000\] |
| workspace_swipe_cancel_ratio | 滑动需要达到多大比例才会开始切换。例如设为 `0.7` 时：若覆盖的距离超过 70% 则切换，否则取消手势 | float | `0.5` | \[0.0 - 1.0\] |
| workspace_swipe_create_new | 在最后一个工作区上向右滑动是否应创建新工作区 | bool | `true` |  |
| workspace_swipe_direction_lock | 若启用，当你滑过 `direction_lock_threshold` 后将锁定方向切换（仅触摸板） | bool | `true` |  |
| workspace_swipe_direction_lock_threshold | 以像素为单位，方向锁定激活前需要滑动的距离（仅触摸板） | int | `10` | \[0 - 200\] |
| workspace_swipe_distance | 以像素为单位，触摸板手势的距离 | int | `300` | \[0 - 2000\] |
| workspace_swipe_forever | 若启用，滑动不会在相邻工作区处钳制，而是继续到更远的工作区 | bool | `false` |  |
| workspace_swipe_invert | 反转滑动方向（仅触摸板） | bool | `true` |  |
| workspace_swipe_min_speed_to_force | 以每时间点像素为单位的最小速度，用于忽略 `cancel_ratio` 强制切换。`0` 表示禁用 | int | `30` | \[0 - 200\] |
| workspace_swipe_touch | 启用从触摸屏边缘进行工作区滑动 | bool | `false` |  |
| workspace_swipe_touch_invert | 反转滑动方向（仅触摸屏） | bool | `false` |  |
| workspace_swipe_use_r | 若启用，滑动将使用 `r` 前缀而不是 `m` 前缀来查找工作区 | bool | `false` |  |

#### gestures.scrolling（滚动）

| Name | Description | Type | Default | Limits |
|----|----|----|----|----|
| move_snap_to_grid | 释放滚动移动手势时，是否应尝试吸附到网格 | bool | `true` |  |
| move_snap_cursor | 释放滚动移动手势时，是否应将光标吸附到新聚焦的窗口 | bool | `true` |  |

### group（组）

| Name | Description | Type | Default | Limits |
|----|----|----|----|----|
| auto_group | 新窗口是否会自动归入聚焦的未锁定组。*注意：若只想对特定窗口禁用 auto_group，请改用“group barred”窗口规则* | bool | `true` |  |
| drag_into_group | 将窗口拖入未锁定组时是否合并它们。`0` - 禁用，`1` - 启用，`2` - 仅在拖入组栏时 | int | `1` | \[0 - 2\] |
| focus_removed_window | Hyprland 是否应聚焦刚刚被移出组的窗口 | bool | `true` |  |
| group_on_movetoworkspace | 使用 hl.dsp.window.move({ workspace }) 是否会将窗口合并到该工作区的唯一未锁定组中 | bool | `false` |  |
| insert_after_current | 组中的新窗口是在当前窗口之后生成，还是在组的末尾生成 | bool | `true` |  |
| merge_floated_into_tiled_on_groupbar | 将浮动窗口拖入平铺窗口的组栏时是否合并它们 | bool | `false` |  |
| merge_groups_on_drag | 窗口组是否可以被拖入其他组 | bool | `true` |  |
| merge_groups_on_groupbar | 将一个组拖入另一个组的组栏时是否合并。*注意：启用此选项仅在同时设置 `drag_into_group = 2` 和 `merge_groups_on_drag = true` 时有效* | bool | `true` |  |

#### group.col（组颜色）

| Name | Description | Type | Default | Limits |
|----|----|----|----|----|
| border_active | 活动组边框颜色 | gradient | `0x66ffff00` |  |
| border_inactive | 非活动组边框颜色 | gradient | `0x66777700` |  |
| border_locked_active | 活动锁定组边框颜色 | gradient | `0x66ff5500` |  |
| border_locked_inactive | 非活动锁定组边框颜色 | gradient | `0x66775500` |  |

#### group.groupbar（组栏）

| Name | Description | Type | Default | Limits |
|----|----|----|----|----|
| enabled | 启用组栏 | bool | `true` |  |
| blur | 对组栏指示器和渐变应用模糊 | bool | `false` |  |
| disable_when_only | 若组栏仅包含一个窗口则禁用组栏 | bool | `false` |  |
| font_family | 用于显示组栏标题的字体，未指定时使用 `misc.font_family` | string | \[\[Empty\]\] |  |
| font_size | 组栏标题的字号 | int | `8` | \[2 - 64\] |
| font_weight_active | 活动组栏标题的字重 | font_weight | `"normal"` |  |
| font_weight_inactive | 非活动组栏标题的字重 | font_weight | `"normal"` |  |
| gaps_in | 渐变之间的间隙大小 | int | `2` | \[0 - 20\] |
| gaps_out | 渐变与窗口之间的间隙大小 | int | `2` | \[0 - 20\] |
| gradients | 启用渐变 | bool | `false` |  |
| gradient_round_only_edges | 仅对整条组栏的渐变边缘进行圆角处理 | bool | `true` |  |
| gradient_rounding | 渐变的圆角程度 | int | `2` | \[0 - 100\] |
| gradient_rounding_power | 调整用于渐变角圆角的曲线，越大越平滑，1.0 为三角角，2.0 为圆，4.0 为方圆形 | float | `2.0` | \[1.0 - 10.0\] |
| height | 组栏高度 | int | `14` | \[0 - 64\] |
| indicator_gap | 组栏指示器与标题之间间隙的高度 | int | `0` | \[0 - 64\] |
| indicator_height | 组栏指示器的高度 | int | `3` | \[0 - 64\] |
| keep_upper_gap | 添加或移除上方间隙 | bool | `true` |  |
| middle_click_close | 中键点击组栏是否会关闭被点击的窗口 | bool | `true` |  |
| priority | 设置组栏的装饰优先级 | int | `3` | \[0 - 6\] |
| render_titles | 是否在组栏装饰中渲染标题 | bool | `true` |  |
| round_only_edges | 仅对整条组栏的指示器边缘进行圆角处理 | bool | `true` |  |
| rounding | 指示器的圆角程度 | int | `1` | \[0 - 40\] |
| rounding_power | 调整用于组栏角圆角的曲线，越大越平滑，1.0 为三角角，2.0 为圆，4.0 为方圆形 | float | `2.0` | \[1.0 - 10.0\] |
| scrolling | 在组栏中滚动是否会改变组的活动窗口 | bool | `true` |  |
| stacked | 将组栏渲染为垂直堆叠 | bool | `false` |  |
| text_color | 组栏中窗口标题的颜色 | color | `0xffffffff` |  |
| text_color_inactive | 组栏中非活动窗口标题的颜色，未设置时默认为 text_color | color | \[\[Empty\]\] |  |
| text_color_locked_active | 锁定组中活动窗口标题的颜色，未设置时默认为 text_color | color | \[\[Empty\]\\ |  |
| text_color_locked_inactive | 锁定组中非活动窗口标题的颜色，未设置时默认为 text_color_inactive | color | \[\[Empty\]\\ |  |
| text_offset | 调整标题的垂直位置 | int | `0` | \[-20 - 20\] |
| text_padding | 设置标题的水平内边距 | int | `0` | \[0 - 22\] |

##### group.groupbar.col（组栏颜色）

| Name | Description | Type | Default | Limits |
|----|----|----|----|----|
| active | 活动组栏背景颜色 | gradient | `0x66ffff00` |  |
| inactive | 非活动（失焦）组栏背景颜色 | gradient | `0x66777700` |  |
| locked_active | 活动锁定组栏背景颜色 | gradient | `0x66ff5500` |  |
| locked_inactive | 非活动锁定组栏背景颜色 | gradient | `0x66775500` |  |

### misc（杂项）

| Name | Description | Type | Default | Limits |
|----|----|----|----|----|
| allow_session_lock_restore | 若为 true，允许在锁屏程序崩溃时重新启动它 | bool | `false` |  |
| always_follow_on_dnd | 拖放时让鼠标焦点跟随鼠标。建议保持启用，尤其是将 focus follows mouse 设为 0 的用户 | bool | `true` |  |
| animate_manual_resizes | 若为 true，将对手动调整窗口大小/移动进行动画 | bool | `false` |  |
| animate_mouse_windowdragging | 若为 true，将对鼠标拖动的窗口进行动画，注意在某些曲线上可能导致异常行为 | bool | `false` |  |
| anr_missed_pings | 显示 ANR 对话框前允许的未响应 ping 次数 | int | `5` | \[1 - 20\] |
| background_color | 更改背景颜色（需要启用 `disable_hyprland_logo`） | color | `0x111111` |  |
| bell_sound | 自定义 wav/ogg 系统铃声的路径。“none”或空字符串将静音。“default”使用系统当前的铃声 | string | `"default"` |  |
| close_special_on_empty | 当最后一个窗口被移除时关闭特殊工作区 | bool | `true` |  |
| disable_autoreload | 若为 true，配置在保存时不会自动重载，而需用 `hyprctl reload` 重载。可能省电 | bool | `false` |  |
| disable_hyprland_guiutils_check | 若未安装 hyprland-guiutils 则禁用警告 | bool | `false` |  |
| disable_hyprland_logo | 禁用随机的 Hyprland logo/动漫女孩背景。:( | bool | `false` |  |
| disable_scale_notification | 当显示器无法设置合适缩放比例时禁用通知弹窗 | bool | `false` |  |
| disable_splash_rendering | 禁用 Hyprland 启动画面渲染（背景上的一小段随机文字）。需要重载显示器才能生效。注意 hyprpaper 有自己的设置可禁用它 | bool | `false` |  |
| disable_watchdog_warning | 禁用未使用 start-hyprland 的警告 | bool | `false` |  |
| disable_xdg_env_checks | 若 XDG 环境由外部管理则禁用警告 | bool | `false` |  |
| enable_anr_dialog | 是否在应用挂起时启用 ANR（应用无响应）对话框 | bool | `true` |  |
| enable_swallow | 启用窗口吞并 | bool | `false` |  |
| exit_window_retains_fullscreen | 关闭全屏窗口是否使下一个聚焦窗口变为全屏。0 - 禁用，1 - 启用，2 - 仅关闭分组窗口时，3 - 仅关闭非分组窗口时 | int | `0` | \[0 - 3\] |
| float_force_onscreen | 已有浮动窗口应如何被约束以保持在屏幕内。0 - 无约束，1 - 必须部分在屏幕内，2 - 必须完全在屏幕内 | int | `0` | \[0 - 2\] |
| new_float_force_onscreen | 与 `float_force_onscreen` 相同，但专门针对新生成的浮动窗口 | int | `2` | \[0 - 2\] |
| focus_on_activate | Hyprland 是否应聚焦请求聚焦的应用（`activate` 请求） | bool | `false` |  |
| font_family | 设置用于渲染文本的全局默认字体 | string | `"Sans"` |  |
| force_default_wallpaper | 强制使用 3 张默认壁纸之一。0 - 禁用动漫背景，1 - 禁用动漫背景，2 - 启用动漫背景，-1 - 随机 | int | `-1` | \[-1 - 2\] |
| initial_workspace_token_timeout | 窗口在其被调用的工作区上打开、直到跟踪 token 过期的秒数。 | int | `10` | \[1 - 3600\] |
| initial_workspace_tracking | 若启用，窗口将在其被调用的工作区上打开。0 - 禁用，1 - 单次，2 - 持久（所有子窗口也是） | int | `1` |  |
| key_press_enables_dpms | 若 DPMS 已关闭，按键时唤醒显示器 | bool | `false` |  |
| lockdead_screen_delay | 锁屏程序未能覆盖所有输出时，“lockdead”屏幕出现的延迟（ms） | int | `1000` | \[0 - 5000\] |
| middle_click_paste | 是否启用中键粘贴（即 primary selection） | bool | `true` |  |
| mouse_move_enables_dpms | 若 DPMS 已关闭，鼠标移动时唤醒显示器 | bool | `false` |  |
| mouse_move_focuses_monitor | 鼠标移入不同显示器时是否聚焦该显示器 | bool | `true` |  |
| name_vk_after_proc | 以创建虚拟键盘的进程命名虚拟键盘，例如 `/usr/bin/fcitx5` 将命名为 hl-virtual-keyboard-fcitx5 | bool | `true` |  |
| on_focus_under_fullscreen | 若存在全屏或最大化窗口，决定请求聚焦的平铺窗口应替换它、留在其后还是退出全屏/最大化状态。0 - 忽略聚焦请求（保持聚焦全屏窗口），1 - 接管，2 - 取消全屏/最大化 | int | `2` | \[0 - 2\] |
| render_unfocused_fps | 后台 render_unfocused 窗口的最大 FPS 限制（另见 Window-Rules，例如 `render_unfocused`） | int | `15` | \[1 - 120\] |
| screencopy_force_8b | 强制 8 位屏幕复制 | bool | `true` |  |
| session_lock_blur | 为锁屏启用模糊。必须启用 `session_lock_xray` | bool | `false` |  |
| session_lock_xray | 若为 true，继续在锁屏下方渲染工作区 | bool | `false` |  |
| size_limits_tiled | 是否对平铺窗口应用 min_size 和 max_size 规则 | bool | `false` |  |
| splash_font_family | 更改用于渲染启动文字的字体，从系统字体中选择（需要重载显示器才能生效） | string | \[\[Empty\]\] |  |
| swallow_exception_regex | 用于不应被 swallow_regex 指定窗口吞并的窗口的 *title* 正则，例如 `wev`。正则匹配父窗口（例如 Kitty）的标题，假设其会变为正在运行的进程 | string | \[\[Empty\]\] |  |
| swallow_regex | 用于应被吞并的窗口（通常是终端）的 *class* 正则 | string | \[\[Empty\]\] |  |
| vrr | 控制显示器的 VRR（自适应同步）。0 - 关闭，1 - 开启，2 - 仅全屏，3 - 全屏且内容类型为 `video` 或 `game` | int | `0` | \[0 - 3\] |

#### misc.col（杂项颜色）

| Name | Description | Type | Default | Limits |
|----|----|----|----|----|
| splash | 更改启动文字的颜色（需要重载显示器才能生效） | color | `0x55ffffff` |  |

### layers（图层）

| Name | Description | Type | Default | Limits |
|----|----|----|----|----|
| allow_new_top_layers_over_existing_fullscreen | 若为 false，新映射的图层不允许渲染在现有全屏窗口之上。注意无论此设置如何，全屏都会隐藏所有先前存在的顶层图层 | bool | `true` |  |
| layers_hog_keyboard_focus | 若为 true，键盘交互图层在鼠标移动时保持焦点，例如 `wofi`、`bemenu` | bool | `true` |  |

### layout（布局）

| Name | Description | Type | Default | Limits |
|----|----|----|----|----|
| single_window_aspect_ratio | 当屏幕上仅显示单个窗口时，添加内边距使其符合指定宽高比。在 16:9 屏幕上设为 `4 3` 将使其成为居中的 4:3 窗口，两侧有内边距 | vec2 | `{0, 0}` |  |
| single_window_aspect_ratio_tolerance | 为 `single_window_aspect_ratio` 设置容差：若需添加的内边距小于屏幕高度或宽度的指定比例，则不尝试调整窗口大小 | float | `0.1` | \[0.0 - 1.0\] |

### binds（按键绑定）

| Name | Description | Type | Default | Limits |
|----|----|----|----|----|
| allow_pin_fullscreen | 若启用，允许已固定的窗口全屏，并在之后恢复其固定状态 | bool | `false` |  |
| client_requested_fs_uses_layout_handler | 若为 false，客户端请求的全屏将使用默认全屏处理器 | bool | `true` |  |
| allow_workspace_cycles | 若启用，工作区不会忘记之前的工作区，因此可通过切换到序列中的第一个工作区、再不断回到前一个工作区来形成循环 | bool | `false` |  |
| disable_keybind_grabbing | 若启用，请求禁用按键绑定的应用（例如 `VMs`）将无法做到 | bool | `false` |  |
| drag_threshold | 窗口拖动及 `click`/`drag` 绑定标志的移动阈值（像素）。`0` 表示禁用 | int | `0` | \[0 - …\] |
| drag_center_window | 是否将窗口居中于指针，或使用初始热点 | bool | true |  |
| focus_preferred_method | 设置使用 `hl.dsp.focus({ direction })`/`hl.dsp.window.move({ direction })`/等时的首选焦点查找方法。`0` - 最近活跃的窗口优先，`1` - 共享边更长的优先 | int | `0` | \[0 - 1\] |
| hide_special_on_workspace_change | 若启用，更改活动工作区（包括切换到自身）将隐藏新活动工作区所在显示器上的特殊工作区 | bool | `false` |  |
| ignore_group_lock | 若启用，`hl.dsp.window.move({ into_group })` 和 `hl.dsp.window.move({ out_of_group })` 等 dispatcher 将忽略每组锁定 | bool | `false` |  |
| movefocus_cycles_fullscreen | 若启用，当焦点在全屏窗口上时，允许 `hl.dsp.focus({ direction })` 寻找窗口。若禁用，则只寻找显示器。 | bool | `false` |  |
| movefocus_cycles_groupfirst | 若启用，在分组窗口中，`hl.dsp.focus({ direction })` 将先在组内循环窗口，到达标签两端后再移动到其他窗口/组 | bool | `false` |  |
| pass_mouse_when_bound | 若启用，触发按键绑定后会将鼠标事件传递给应用/拖动窗口 | bool | `false` |  |
| scroll_event_delay | 以 ms 计，滚动事件后等待多少 ms 才允许再传递一个给绑定 | int | `300` | \[0 - 2000\] |
| window_direction_monitor_fallback | 若启用，沿方向将窗口或焦点移出显示器边缘时，会将其移动到该方向的下一个显示器 | bool | `true` |  |
| workspace_back_and_forth | 尝试切换到当前聚焦的工作区时改为切换到上一个工作区，类似 i3 的 `_auto_back_and_forth_`。`0` - 禁用，`1` - 启用，`2` - 每显示器 | int | `0` | \[0 - 2\] |
| workspace_center_on | 切换工作区时光标应居中于工作区（0）还是该工作区最后活跃的窗口（1） | int | `1` | \[0 - 1\] |

### xwayland（Xwayland）

| Name | Description | Type | Default | Limits |
|----|----|----|----|----|
| enabled | 允许运行使用 X11 的应用程序 | bool | `true` |  |
| create_abstract_socket | 为 Xwayland 连接创建 abstract Unix domain socket。更改需重启 Xwayland 才能生效；仅限 Linux | bool | `false` |  |
| force_zero_scaling | 在缩放的显示器上强制 Xwayland 窗口缩放为 1 | bool | `false` |  |
| use_nearest_neighbor | 对 Xwayland 应用使用最近邻过滤，使其像素化而非模糊 | bool | `true` |  |

### opengl（OpenGL）

| Name | Description | Type | Default | Limits |
|----|----|----|----|----|
| nvidia_anti_flicker | 在 NVIDIA 上减少闪烁，代价是低端 GPU 可能掉帧。非 NVIDIA 上此项被忽略 | bool | `true` |  |

### render（渲染）

| Name | Description | Type | Default | Limits |
|----|----|----|----|----|
| async_commit | 尽可能异步发送 DRM commit，降低硬件光标延迟 | bool | `false` |  |
| cm_auto_hdr | 需要时在全屏自动切换到 HDR。`0` - 禁用，`1` - 切换到 `hdr`，`2` - 切换到 `hdredid` | int | `1` | \[0 - 2\] |
| cm_enabled | 是否启用色彩管理管线。需要重启 | bool | `true` |  |
| cm_sdr_eotf | 显示 SDR 应用的默认传输函数。`default` - 使用默认值（sRGB），`gamma22` - 将未指定视为 Gamma 2.2，`gamma22force` - 将未指定和 sRGB 都视为 Gamma 2.2，`srgb` - 将未指定视为 sRGB。可选值：`"default"`/`"gamma22"`/`"gamma22force"`/`"srgb"` | string | `"default"` |  |
| ctm_animation | 是否为 CTM 变化（hyprsunset）启用淡入淡出动画。2 表示“auto”，在 NVIDIA 上禁用这些动画 | int | `2` | \[0 - 2\] |
| commit_timing_enabled | 启用 commit timing 协议。需要重启 | bool | `true` |  |
| direct_scanout | 启用直接扫描输出。直接扫描输出可在屏幕上只有一个全屏应用（游戏）时减少延迟。若全屏应用出现图形故障，也建议将其设为 false。`0` - 禁用，`1` - 启用，`2` - 自动（内容类型为 'game' 时启用） | int | `0` | \[0 - 2\] |
| expand_undersized_textures | 是否沿边缘扩展尺寸不足的纹理，还是拉伸整个纹理 | bool | `true` |  |
| fp16_sdr_tf | SDR 模式下 fp16 的内部工作缓冲传输函数。0 - 跟随显示器，1 - 线性 | int | `0` | \[0 - 1\] |
| icc_vcgt_enabled | 启用随 ICC 配置向 KMS 发送 VCGT 渐变 | bool | `true` |  |
| keep_unmodified_copy | 为屏幕共享保留未修改的 SDR 帧副本。`0` - 禁用，`1` - 启用，`2` - 自动（HDR 且带 SDR 修饰时启用）。若截图透明请设为 1 | int | `2` | \[0 - 2\] |
| new_render_scheduling | 需要时自动使用三重缓冲，提升低性能设备上的 FPS | bool | `false` |  |
| not_shown_fifo_lock | 控制未显示表面的 fifo 锁定。always - 对任何表面使用 fifo 锁定，ignore_unfocused - 忽略 render_unfocused 窗口，never - 跳过对不可见表面的锁定 | int | `0` | \[0 - 2\] |
| non_shader_cm | 启用无着色器 CM。`0` - 禁用，`1` - 尽可能，`2` - 仅 DS 和 passthrough，`3` - 禁用并忽略 CM 问题。可选值：\[0 - 3\] | int | `2` | \[0 - 3\] |
| non_shader_cm_interop | `0` - 外部 ctm（hyprsunset 等）在全屏时禁用，`1` - 外部 ctm 在全屏时启用，`2` - 对全屏 photo/video/game 内容类型禁用外部 ctm | int | `2` | \[0 - 2\] |
| send_content_type | 报告内容类型以允许显示器配置文件自动切换（切换期间可能出现黑屏） | bool | `true` |  |
| use_fp16 | 内部使用 FP16 缓冲。`0` - 禁用，`1` - 启用，`2` - HDR 模式下启用 | int | `2` | \[0 - 2\] |
| use_shader_blur_blend | 使用实验性的模糊背景混合（旋转屏幕上会出现故障）。若 fp16 或 `keep_unmodified_copy` 下缺少模糊，请设为 `true` | bool | `false` |  |
| xp_mode | 禁用后缓冲区与底层渲染 | bool | `false` |  |

`cm_auto_hdr` 配合 mpv 版本高于 v0.40.0 使用，需要 mpv 选项 `--target-colorspace-hint-mode=source`。

### cursor（光标）

| Name | Description | Type | Default | Limits |
|----|----|----|----|----|
| default_monitor | 启动时设置光标的默认显示器名称（用 `hyprctl monitors` 查看名称） | string | `[[Empty]]` |  |
| enable_hyprcursor | 是否启用 hyprcursor 支持 | bool | `true` |  |
| hide_on_key_press | 按下任意键时隐藏光标，直到鼠标移动 | bool | `false` |  |
| hide_on_tablet | 最后一次输入为平板输入时隐藏光标，直到有鼠标输入 | bool | `false` |  |
| hide_on_touch | 最后一次输入为触摸输入时隐藏光标，直到有鼠标输入 | bool | `true` |  |
| hotspot_padding | 屏幕边缘与光标之间的内边距（逻辑像素） | int | `0` | \[0 - 20\] |
| inactive_timeout | 光标静止多少秒后隐藏。设为 `0` 表示永不 | float | `0` | \[0 - 20\] |
| invisible | 不渲染光标 | bool | `false` |  |
| min_refresh_rate | `no_break_fs_vrr` 生效时，光标移动的最低刷新率。设为支持的最低刷新率或更高 | int | `24` | \[10 - 500\] |
| no_break_fs_vrr | 对启用 VRR 的全屏应用禁用光标移动时调度新帧，以避免帧率尖峰（可能需要将 `no_hardware_cursors` 设为 `1`）。`0` - 禁用，`1` - 启用，`2` - 自动（内容类型为 'game' 时启用） | int | `2` | \[0 - 2\] |
| no_hardware_cursors | 禁用硬件光标。`0` - 尽可能使用硬件光标，`1` - 不使用硬件光标，`2` - 自动（撕裂时禁用） | int | `2` | \[0 - 2\] |
| no_warps | 若为 true，许多情况下不会移动（warp）光标（聚焦、按键绑定等） | bool | `false` |  |
| persistent_warps | 窗口重新聚焦时，光标回到其相对于该窗口的最后位置，而非中心 | bool | `false` |  |
| sync_gsettings_theme | 将 XCursor 主题与 GSettings 同步。在主题加载时将 cursor-theme 和 cursor-size 应用到 GSettings，使大多数基于 CSD GTK 的客户端使用相同的 XCursor 主题和大小 | bool | `true` |  |
| use_cpu_buffer | 使硬件光标使用 CPU 缓冲。NVIDIA 上必须如此才能使用硬件光标。`0` - 禁用，`1` - 启用，`2` - 自动（NVIDIA 时启用） | int | `2` | \[0 - 2\] |
| warp_back_after_non_mouse_input | 使用非鼠标输入移动光标后、再回到鼠标时，将光标移回原位 | bool | `false` |  |
| warp_on_change_workspace | 切换工作区后将光标移到最后一个聚焦的窗口。`0` - 禁用，`1` - 启用，`2` - 强制（忽略 cursor:no_warps 选项） | int | `0` | \[0 - 2\] |
| warp_on_monitor_change | 聚焦不同显示器时将光标移到最后一个聚焦的窗口。`-1` - 跟随 `cursor:warp_on_change_workspace` 的值，`0` - 禁用，`1` - 启用，`2` - 强制（即使 `cursor:no_warps` 也生效） | int | `-1` | \[-1 - 2\] |
| warp_on_toggle_special | 切换特殊工作区时将光标移到最后一个聚焦的窗口。`0` - 禁用，`1` - 启用，`2` - 强制（忽略 cursor:no_warps 选项） | int | `0` | \[0 - 2\] |
| zoom_detached_camera | 放大时将相机与鼠标分离，仅在鼠标超出屏幕边缘时才移动相机以保持鼠标可见 | bool | `true` |  |
| zoom_disable_aa | 缩放时禁用抗锯齿，即出现像素化而非模糊 | bool | `false` |  |
| zoom_factor | 围绕光标缩放的倍数。如同放大镜。最小 1.0（表示不缩放） | float | `1.0` | \[1 - 10\] |
| zoom_rigid | 缩放应刚性跟随光标（尽可能始终居中）还是松散跟随 | bool | `false` |  |

### ecosystem（生态集成）

| Name | Description | Type | Default | Limits |
|----|----|----|----|----|
| enforce_permissions | 是否启用权限控制 | bool | `false` |  |
| no_donation_nag | 禁用每年出现两次的鼓励捐赠弹窗 | bool | `false` |  |
| no_update_news | 禁用更新 Hyprland 到新版本时出现的弹窗 | bool | `false` |  |

### quirks（怪癖行为）

| Name | Description | Type | Default | Limits |
|----|----|----|----|----|
| prefer_hdr | 将 HDR 模式报告为首选。`0` - 禁用，`1` - 总是，`2` - 仅 gamescope | int | `0` | \[0 - 1\] |
| skip_non_kms_dmabuf_formats | 不报告无法导入 KMS 的 dmabuf 格式 | bool | `false` |  |

部分客户端期望在启动前显示器已处于 HDR 模式。这会破坏自动 HDR 激活，并可能导致白屏和闪烁。可用 `prefer_hdr` 修复。

### input-capture（输入捕获）

| Name | Description | Type | Default | Limits |
|----|----|----|----|----|
| capture_modifiers | 若启用，修饰键也会被捕获并发送给程序 | bool | `false` |  |
| enforce_barriers | 若启用，收到无效 barrier 时抛出 Wayland 错误 | bool | `true` |  |

### debug（调试）

警告

这些设置仅用于开发和测试。不应在正常配置中修改它们。

| Name | Description | Type | Default | Limits |
|----|----|----|----|----|
| colored_stdout_logs | 在 stdout 日志中启用颜色 | bool | `true` |  |
| damage_blink | （癫痫警告！）闪烁由 damage 追踪更新的区域 | bool | `false` |  |
| damage_tracking | 仅重绘显示中需要的部分。**不要**修改。None - 0，monitor - 1，full - 2 | int | `2` | \[0 - 2\] |
| disable_logs | 禁用日志写入文件 | bool | `true` |  |
| disable_scale_checks | 禁用缩放因子校验。会导致像素对齐和舍入误差 | bool | `false` |  |
| disable_time | 禁用时间日志 | bool | `true` |  |
| ds_handle_same_buffer | 未修改缓冲区直接扫描输出的特殊处理 | bool | `true` |  |
| ds_handle_same_buffer_fifo | 未修改缓冲区直接扫描输出时解锁 fifo 的特殊处理 | bool | `true` |  |
| enable_stdout_logs | 启用输出到 stdout 的日志 | bool | `false` |  |
| error_limit | 限制显示的配置文件解析错误数量 | int | `5` | \[0 - 20\] |
| error_position | 设置错误栏的位置。`0` - 顶部，`1` - 底部 | int | `0` | \[0 - 1\] |
| fifo_pending_workaround | 针对空 pending 列表的 fifo 规避方案 | bool | `false` |  |
| full_cm_proto | 声明支持所有 cm proto 特性（需要重启） | bool | `false` |  |
| gl_debugging | 使用 glGetError 和 EGL_KHR_debug 启用 OpenGL 调试，修改后需要重启 | bool | `false` |  |
| invalidate_buffers | 允许缓冲区失效（失效可提升性能，但在部分系统上会产生故障）。0 - 不允许，1 - 允许 | int | `1` | \[0 - 1\] |
| log_damage | 启用 damage 日志 | bool | `false` |  |
| manual_crash | 设为 1 再设回 0 可使 Hyprland 崩溃 | int | `0` | \[0 - 1\] |
| overlay | 打印调试性能覆盖层。为获得准确结果请禁用 VFR | bool | `false` |  |
| pass | 启用渲染通道调试 | bool | `false` |  |
| render_solitary_wo_damage | 以空 damage 渲染孤立窗口 | bool | `false` |  |
| suppress_errors | 若启用，Hyprland 不会显示配置文件解析错误 | bool | `false` |  |
| vfr | 控制 Hyprland 的 VFR 状态。强烈建议保持启用以节省资源 | bool | `true` |  |

### experimental（实验性）

| Name | Description | Type | Default | Limits |
|----|----|----|----|----|
| wp_cm_1_2 | 允许 wp-cm-v1 版本 2 | bool | `false` |  |

### more（更多）

更多配置选项在其他页面描述，这些选项与布局或具体场景相关。更多页面请参见侧边栏，尤其是布局相关的页面。

---

# 二、布局选项

## 布局（Layouts）参考

Hyprland 的四种内置布局：dwindle（平铺）、master（主副）、scrolling（滚动）、monocle（单窗口）。每个布局的配置项位于对应 category 下；布局消息通过 `hl.dsp.layout("msg args")` 分发。

### dwindle（平铺布局）

Dwindle 是类似 BSPWM 的布局：工作区上每个窗口都是二叉树的成员。

**Quirks / 特性**

- Dwindle 的 split **不是永久的**。split 由父节点的 W/H 比例动态决定：若 W > H 则左右并排，若 H > W 则上下堆叠。
- 启用 `preserve_split` 可让 split 变为永久。

| Name | Description | Type | Default | Limits |
|----|----|----|----|----|
| force_split | 0 - split 跟随鼠标，1 - 总是向左 split（新窗口在左或上），2 - 总是向右 split（新窗口在右或下） | int | `0` | \[0 - 2\] |
| preserve_split | 若启用，无论容器发生什么，split（side/top）都不会改变 | bool | `false` |  |
| smart_split | 若启用，依据光标位置更精确地控制 split 方向：窗口在概念上被划分为四个三角形，光标所在三角形决定 split 方向。此特性同时会打开 `preserve_split` | bool | `false` |  |
| smart_resizing | 若启用，调整尺寸的方向由鼠标在窗口上的位置（最接近哪个角）决定；否则依据窗口的平铺位置 | bool | `true` |  |
| permanent_direction_override | 若启用，使 preselect 方向持续有效，直到关闭该模式、指定另一个方向、或指定非方向（`l`、`r`、`u`/`t`、`d`/`b` 之外的任何值） | bool | `false` |  |
| special_scale_factor | 特殊工作区上窗口的缩放因子 | float | `1` | \[0 - 1\] |
| split_width_multiplier | 自动 split 的宽度倍数。在宽屏显示器上即使多次 split 后 W > H 时，放大窗口尺寸很有用 | float | `1.0` | \[0.1 - 3.0\] |
| use_active_for_splits | split 时优先使用活动窗口还是鼠标位置 | bool | `true` |  |
| default_split_ratio | 窗口打开时的默认 split 比例。1 表示均匀的 50/50 | float | `1.0` | \[0.1 - 1.9\] |
| split_bias | 指定哪个窗口获得该 split 比例。0 - 方向性的（上或左的窗口），1 - 当前窗口 | int | `0` | \[0 - 1\] |
| precise_mouse_move | 拖放窗口时会依据鼠标位置更精确地放置 | bool | `false` |  |

**Layout messages（布局消息）**

#### movetoroot
将指定窗口变为工作区上其最直接根节点的子节点；若该窗口已是根节点的直接子节点，则产生警告。默认行为是 "stable"，即焦点窗口保持在屏幕同一侧；把 `unstable` 作为第二个参数会交换根节点直接子节点的位置（即它们位于屏幕哪一侧）。注意 `movetoroot unstable` **无效**，正确写法是 `movetoroot active unstable`。参数：`window?`、`"unstable"?` ｜ 示例：`hl.dsp.layout("movetoroot class:imcool")`

#### preselect
一次性覆盖 split 方向，仅对下一个要打开的窗口有效，且只作用于平铺窗口。参数：`direction` ｜ 示例：`hl.dsp.layout("preselect l")`

#### rotatesplit
按可选角度旋转当前窗口的 split。角度必须是 90 的倍数，正数为顺时针，负数为逆时针。参数：`int? = 90` ｜ 示例：`hl.dsp.layout("rotatesplit 90")`

#### splitratio
修改 split 比例。默认使用 delta 值，在数值后加 `exact` 则改为直接设定；默认使用正 delta；在数值前加 `+` 或 `-` 指定方向。超出 \[0.1 - 1.9\] 范围的值会被钳制到最近的边界。参数：`float` ｜ 示例：`hl.dsp.layout("splitratio 1.2 exact")`

#### swapsplit
交换当前窗口 split 的两半。参数：`None` ｜ 示例：`hl.dsp.layout("swapsplit")`

#### togglesplit
切换当前窗口的 split（top/side）。必须启用 `preserve_split` 才能切换。参数：`None` ｜ 示例：`hl.dsp.layout("togglesplit")`

**专用 dispatcher**

| Dispatcher | Description | Params |
|----|----|----|
| window.pseudo | 切换指定窗口的 pseudo 模式 | 留空/`"active"` 表示当前窗口，或 `"window"` 表示特定窗口 |

### master（主副布局）

Master 布局让一个（或多个）窗口成为 "master"，默认占据屏幕左侧，其余窗口在右侧平铺。可按工作区修改方向，以使用左右分屏之外的排布。

| Name | Description | Type | Default | Limits |
|----|----|----|----|----|
| allow_small_split | 允许以水平 split 风格添加额外的 master 窗口 | bool | `false` |  |
| special_scale_factor | 特殊工作区窗口的缩放 | float | `1` | \[0 - 1\] |
| mfact | master 窗口的尺寸百分比，例如 `mfact = 0.70` 表示屏幕 70% 给 master、30% 给 slave | float | `0.55` | \[0 - 1\] |
| new_status | `"master"` - 新窗口成为 master，`"slave"` - 新窗口加入 slave 堆栈，`"inherit"` - 继承焦点窗口 | string | `"slave"` |  |
| new_on_top | 新打开的窗口是否应位于堆栈顶部 | bool | `false` |  |
| new_on_active | `"before"`、`"after"` - 相对焦点窗口放置新窗口，`"none"` - 依 `new_on_top` 的值放置 | string | `"none"` |  |
| orientation | master 区域的默认位置 | string | `"left"` | `"left"`, `"right"`, `"top"`, `"bottom"`, `"center"` |
| slave_count_for_center_master | 使用 orientation=center 时，仅在至少打开这么多 slave 窗口时才让 master 居中（设为 0 表示总是居中 master） | int | `2` | \[0 - 10\] |
| center_master_fallback | 当 slave 少于 `slave_count_for_center_master` 时为居中 master 设置回退 | string | `"left"` | `"left"`, `"right"`, `"top"`, `"bottom"` |
| smart_resizing | 若启用，调整尺寸的方向由鼠标在窗口上的位置（最接近哪个角）决定；否则依据窗口的平铺位置 | bool | `true` |  |
| drop_at_cursor | 若启用，拖放窗口会把它们放到光标位置；否则在拖放到堆栈一侧时，依 `new_on_top` 决定放到堆栈顶部或底部 | bool | `true` |  |
| always_keep_position | 没有 slave 窗口时是否让 master 窗口保持其配置位置 | bool | `false` |  |
| focus_master_on_close | 若启用，关闭窗口时会聚焦 master 窗口 | bool | `false` |  |

**Layout messages（布局消息）**

命令的参数以单个空格分隔。

#### addmaster
在 master 一侧添加一个 master。若当前窗口不是 master 则为当前窗口，否则为第一个非 master 窗口。参数：`none` ｜ 示例：`hl.dsp.layout("addmaster")`

#### cyclenext
聚焦下一个窗口（遵循布局）。参数：`loop`（允许从堆栈底部循环回 master）或 `noloop`（像 DWM 那样在堆栈底部强制停止），留空默认 `loop` ｜ 示例：`hl.dsp.layout("cyclenext")`

#### cycleprev
聚焦上一个窗口（遵循布局）。参数：`loop`（允许从 master 循环到堆栈底部）或 `noloop`（像 DWM 那样在 master 处强制停止），留空默认 `loop` ｜ 示例：`hl.dsp.layout("cycleprev noloop")`

#### focusmaster
聚焦 master 窗口。参数：`master`（焦点留在 master）、`auto`（默认；若已在 master 则聚焦第一个非 master 窗口）或 `previous`（聚焦 master 时记住当前窗口，若已在 master 则聚焦上一个窗口，否则回退到 `auto`） ｜ 示例：`hl.dsp.layout("focusmaster auto")`

#### mfact
修改 mfact，即 master 的 split 比例。参数：新的 split 比例，相对 float delta（如 `-0.2`、`+0.2`），或 `exact` 后跟 0.0 到 1.0 之间的值 ｜ 示例：`hl.dsp.layout("mfact exact 0.7")`

#### orientationbottom
将当前工作区方向设为 bottom（master 区在底部，slave 窗口在上方，水平堆叠）。参数：`none` ｜ 示例：`hl.dsp.layout("orientationbottom")`

#### orientationcenter
将当前工作区方向设为 center（master 区居中，slave 窗口在左右交替、垂直堆叠）。参数：`none` ｜ 示例：`hl.dsp.layout("orientationcenter")`

#### orientationcycle
从给定列表中循环切换到下一个方向（针对当前工作区）。参数：允许值 `left`、`top`、`right`、`bottom`、`center`，以空格分隔；留空则行为同 `orientationnext` ｜ 示例：`hl.dsp.layout("orientationcycle left top right")`

#### orientationleft
将当前工作区方向设为 left（master 区在左，slave 窗口在右，垂直堆叠）。参数：`none` ｜ 示例：`hl.dsp.layout("orientationleft")`

#### orientationnext
循环切换到当前工作区的下一个方向（顺时针）。参数：`none` ｜ 示例：`hl.dsp.layout("orientationnext")`

#### orientationprev
循环切换到当前工作区的上一个方向（逆时针）。参数：`none` ｜ 示例：`hl.dsp.layout("orientationprev")`

#### orientationright
将当前工作区方向设为 right（master 区在右，slave 窗口在左，垂直堆叠）。参数：`none` ｜ 示例：`hl.dsp.layout("orientationright")`

#### orientationtop
将当前工作区方向设为 top（master 区在顶部，slave 窗口在下方，水平堆叠）。参数：`none` ｜ 示例：`hl.dsp.layout("orientationtop")`

#### removemaster
从 master 一侧移除一个 master。若当前窗口是 master 则为当前窗口，否则为最后一个 master 窗口。参数：`none` ｜ 示例：`hl.dsp.layout("removemaster")`

#### rollnext
把堆栈中下一个窗口轮换为 master，同时保持焦点在 master 上。参数：`none` ｜ 示例：`hl.dsp.layout("rollnext")`

#### rollprev
把堆栈中上一个窗口轮换为 master，同时保持焦点在 master 上。参数：`none` ｜ 示例：`hl.dsp.layout("rollprev")`

#### swapnext
将焦点窗口与下一个窗口交换（遵循布局）。参数：`loop`（允许交换堆栈底部与 master）或 `noloop`（像 DWM 那样不允许），留空默认 `loop` ｜ 示例：`hl.dsp.layout("swapnext")`

#### swapprev
将焦点窗口与上一个窗口交换（遵循布局）。参数：`loop`（允许交换 master 与堆栈底部）或 `noloop`（像 DWM 那样不允许），留空默认 `loop` ｜ 示例：`hl.dsp.layout("swapprev noloop")`

#### swapwithmaster
将当前窗口与 master 交换；若当前窗口就是 master，则与第一个子窗口交换。参数：`master`（新焦点为新的 master 窗口）、`child`（新焦点为新的子窗口）或 `auto`（默认，保持先前焦点窗口的焦点）；再添加 `ignoremaster` 会在 master 已聚焦时忽略此 dispatcher ｜ 示例：`hl.dsp.layout("swapwithmaster master")`

**Workspace rules**

`layout_opts` 规则：

| rule | description | type |
|----|----|----|
| orientation = \[o\] | 设置工作区的方向，可用方向见 `orientation` 配置项 | string |

```lua
hl.workspace_rule({ workspace = "2", layout_opts = { orientation = "top" } })
```

### scrolling（滚动布局）

Scrolling 布局把窗口放在一条无限延伸的"磁带"上。

**Quirks / 特性**

- 可选的 layout-handled fullscreen：scrolling 使用自己的全屏处理器，允许从全屏窗口滚动离开而不取消其全屏状态。
- 在 scrolling 布局的工作区上，全屏 dispatch 使用 `layout_aware = true`（或完全不指定 `layout_aware`）即可启用；它也兼容现有的窗口/工作区全屏相关选择器。
- 注意：全屏窗口获得焦点时，`hl.dsp.focus({ direction })` 默认会在指定方向上寻找其他显示器，而不是在当前显示器上切换窗口。若要利用滚动离开全屏窗口的能力，可设置 `binds.movefocus_cycles_fullscreen = true` 恢复 focus dispatcher 的窗口寻找行为，或改用 scrolling 布局的 `focus` 布局消息。

| Name | Description | Type | Default | Limits |
|----|----|----|----|----|
| fullscreen_on_one_column | 若启用，工作区上的单个列总是横跨整个屏幕 | bool | `true` |  |
| column_width | 列的默认宽度 | float | `0.5` | \[0.1 - 1.0\] |
| focus_fit_method | 列被聚焦时，用何种方式将其带入视野。0 = center，1 = fit，2 = clamped_center | int | `1` | \[0 - 2\] |
| follow_focus | 窗口获得焦点时滚动磁带的行为。0：焦点不会引起磁带移动。1：焦点可能引起磁带移动，鼠标点击总是移动磁带。2：焦点可能引起磁带移动。 | int | `1` | \[0 - 2\] |
| follow_min_visible | 窗口被聚焦时，要求其至少有给定比例可见，焦点才跟随。硬输入（如按键绑定、点击）总是跟随 | float | `0.4` | \[0.0 - 1.0\] |
| explicit_column_widths | 供 `colresize +conf/-conf` 使用的预配置宽度列表，逗号分隔 | string | `"0.333, 0.5, 0.667, 1.0"` |  |
| wrap_focus | 若启用，`hl.dsp.layout("focus l/r")` 会在开头和结尾处环绕 | bool | `true` |  |
| wrap_swapcol | 若启用，`hl.dsp.layout("swapcol l/r")` 会在开头和结尾处环绕 | bool | `true` |  |
| direction | 新窗口出现及布局滚动的方向。`"left"`/`"right"`/`"down"`/`"up"` | string | `"right"` |  |

**Layout messages（布局消息）**

#### center
将当前聚焦的列居中。参数：`none` ｜ 示例：`hl.dsp.layout("center")`

#### colresize
调整当前列的宽度：可给绝对值或相对值（如 `0.5`、`+0.2`、`-0.2`），或用 `+conf`/`-conf` 循环预配置宽度；也可用 `all (number)` 把所有列调整到指定宽度。参数：相对 float / 相对 `conf` ｜ 示例：`hl.dsp.layout("colresize +conf")`

#### consume
将当前窗口移入前一列。参数：`none` ｜ 示例：`hl.dsp.layout("consume")`

#### consume_or_expel
不独处时 expel，独处一列时 consume。参数：`prev` 或 `next` ｜ 示例：`hl.dsp.layout("consume_or_expel next")`

#### expel
将当前窗口移入它自己的新列（若窗口位于屏幕上半部分则向后方向，否则向前方向）。参数：`none` ｜ 示例：`hl.dsp.layout("expel")`

#### fit
基于参数执行 fit 操作。可用：`active`、`visible`、`all`、`toend`、`tobeg`、`expand`。`expand` 会把当前窗口扩展到占据显示器上剩余的可用空间。参数：fit mode ｜ 示例：`hl.dsp.layout("fit visible")`

#### fit_into_view
将当前活动的列完整纳入视野。参数：`none` ｜ 示例：`hl.dsp.layout("fit_into_view")`

#### focus
移动焦点并居中布局，同时会环绕而不是移动到相邻显示器。参数：`direction` ｜ 示例：`hl.dsp.layout("focus l")`

#### inhibit_scroll
阻止当前活动工作区的滚动视图移动。该开关对每个工作区独立。参数：留空表示切换，或用 `bool` 显式启用/禁用 ｜ 示例：`hl.dsp.layout("inhibit_scroll true")`

#### move
水平移动布局：可用相对逻辑像素（`-200`、`+200`）或按列（`+col`、`-col`）。参数：move data ｜ 示例：`hl.dsp.layout("move +col")`

#### promote
将窗口移入它自己的新列（向前方向）。参数：`none` ｜ 示例：`hl.dsp.layout("promote")`

#### swapcol
将当前列与其左（`l`）或右（`r`）相邻列交换。交换会环绕（例如把第一列向左交换会移动到末尾）。参数：`l` 或 `r` ｜ 示例：`hl.dsp.layout("swapcol l")`

**Workspace / Window rules**

| name | description | type |
|----|----|----|
| direction | 同 `scrolling.direction` 配置项，但按工作区设置 | string |

```lua
hl.workspace_rule({ workspace = "2", layout_opts = { direction = "right" } })
```

静态规则 `scrolling_width` 可为窗口设置起始列宽：

```lua
hl.window_rule({ name = "kitty_starting_width", match = { class = "kitty" }, scrolling_width = 0.5 })
```

**Convenience functions**

| 函数 | 说明 |
|----|----|
| `hl.get_scrolling_offset()` | 获取滚动偏移 |
| `hl.set_scrolling_offset(double)` | 设置滚动偏移 |

返回值请使用 LSP（或自行查看 stubs）。编辑器中的 LSP 配置见编辑器自动补全相关文档。

### monocle（单窗口布局）

Monocle 布局中窗口总是占据工作区中全部未保留区域。

**Quirks / 特性**

- 由于布局的工作方式，`hl.dsp.window.cycle_next()` 在 Monocle 下不工作。要循环 monocle 窗口，请使用 `hl.dsp.layout("cyclenext")` 或 `hl.dsp.window.cycle_next({ tiled = true })`。

**Layout messages（布局消息）**

#### cyclenext
循环到下一个窗口。参数：`none` ｜ 示例：`hl.dsp.layout("cyclenext")`

#### cycleprev
循环到上一个窗口。参数：`none` ｜ 示例：`hl.dsp.layout("cycleprev")`
---

# 附：常见"想改 X"反查表

| 想改什么 | category | 关键选项 |
|---|---|---|
| 窗口间距 / 边缘间距 | `general` | `gaps_in` `gaps_out` `gaps_workspaces` |
| 边框粗细 / 颜色 | `general` / `general.col` | `border_size` `col.active_border` `col.inactive_border` |
| 圆角 | `decoration` | `rounding` `rounding_power` |
| 透明 / 变暗 | `decoration` | `active_opacity` `inactive_opacity` `dim_inactive` `dim_strength` |
| 阴影 | `decoration.shadow` | `enabled` `range` `render_power` `color` |
| 模糊 | `decoration.blur` | `enabled` `size` `passes` `vibrancy` `noise` |
| 动画开关/速度 | `animations` + `hl.curve` + `hl.animation` | `enabled` |
| 键盘布局 / 切换键 | `input` | `kb_layout` `kb_options` `kb_variant` |
| 鼠标灵敏度 / 加速 | `input` | `sensitivity` `accel_profile` `force_no_accel` `scroll_factor` |
| 触摸板 | `input.touchpad` | `natural_scroll` `tap_to_click` `tap_and_drag` `disable_while_typing` |
| 聚焦跟随鼠标 | `input` | `follow_mouse` `float_switch_override_focus` |
| 手势（滑动行为） | `gestures` | `workspace_swipe_distance` `workspace_swipe_cancel_ratio` `workspace_swipe_forever` `workspace_swipe_create_new` |
| 窗口分组 | `group` / `group.groupbar` | `auto_group` `insert_after_current` `groupbar.*` |
| 平铺布局参数 | `dwindle` / `master` / `scrolling` | 见"二、布局选项" |
| 双屏/缩放细节 | `hl.monitor`（不是 config 选项） | 见 DISPATCHERS-RULES 的显示器一节 |
| 快捷键相关 | `binds` | `workspace_back_and_forth` `workspace_center_on` `hide_special_on_workspace_change` `drag_threshold` |
| Xwayland | `xwayland` | `enabled` `force_zero_scaling` `use_nearest_neighbor` |
| 渲染/同步 | `render` | `new_render_scheduling` `direct_scanout` `ctm_animation` `use_fp16` `commit_timing_enabled` |
| 光标 | `cursor` | `zoom_factor` `no_hardware_cursors` `inactive_timeout` `sync_gsettings_theme` `hide_on_key_press` |
| 杂项/日志 | `misc` | `disable_hyprland_logo` `force_default_wallpaper` `font_family` `mouse_move_enables_dpms` |
| 会话/锁屏相关 | `misc` | `allow_session_lock_restore` `exit_window_retains_fullscreen` |
| 权限 | `ecosystem` | `enforce_permissions` |

> 注：完整清单以本文件上半部分的表格为准；这张表只是入口索引。
