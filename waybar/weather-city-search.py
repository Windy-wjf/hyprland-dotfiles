#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Waybar 天气城市搜索（GTK4 + gtk4-layer-shell）：风格与 popup.py 一致。

- 离线候选：主要城市 + 县级市/区
- 在线搜索：Nominatim（无 countrycodes 限制）
- 回车：直接将输入写入 weather.city（wttr.in 支持中文城市名）
- 点击外部 / Esc 关闭
"""
import sys
import json
import threading
import urllib.parse
import urllib.request

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
gi.require_version("Gtk4LayerShell", "1.0")
from gi.repository import Gdk, GLib, Gtk, Gtk4LayerShell

MARGIN_TOP = 42
PANEL_W = 340
CITY_FILE = "/home/wjf/.config/waybar/weather.city"

# 离线候选：(显示名, 写入 weather.city 的值)
# wttr.in 支持中文和英文，这里用英文更稳定
CITIES = [
    # 直辖市/省会
    ("北京", "Beijing"), ("上海", "Shanghai"), ("广州", "Guangzhou"),
    ("深圳", "Shenzhen"), ("成都", "Chengdu"), ("杭州", "Hangzhou"),
    ("南京", "Nanjing"), ("武汉", "Wuhan"), ("西安", "Xian"),
    ("重庆", "Chongqing"), ("天津", "Tianjin"), ("苏州", "Suzhou"),
    ("长沙", "Changsha"), ("郑州", "Zhengzhou"), ("青岛", "Qingdao"),
    ("大连", "Dalian"), ("沈阳", "Shenyang"), ("哈尔滨", "Harbin"),
    ("昆明", "Kunming"), ("贵阳", "Guiyang"), ("南宁", "Nanning"),
    ("海口", "Haikou"), ("福州", "Fuzhou"), ("厦门", "Xiamen"),
    ("济南", "Jinan"), ("合肥", "Hefei"), ("太原", "Taiyuan"),
    ("石家庄", "Shijiazhuang"), ("兰州", "Lanzhou"), ("银川", "Yinchuan"),
    ("乌鲁木齐", "Urumqi"), ("拉萨", "Lhasa"), ("西宁", "Xining"),
    ("呼和浩特", "Hohhot"), ("长春", "Changchun"), ("南昌", "Nanchang"),
    ("宁波", "Ningbo"), ("无锡", "Wuxi"), ("佛山", "Foshan"),
    ("东莞", "Dongguan"), ("珠海", "Zhuhai"), ("中山", "Zhongshan"),
    ("惠州", "Huizhou"), ("江门", "Jiangmen"), ("烟台", "Yantai"),
    ("潍坊", "Weifang"), ("泉州", "Quanzhou"), ("温州", "Wenzhou"),
    ("台州", "Taizhou"), ("金华", "Jinhua"), ("嘉兴", "Jiaxing"),
    ("绍兴", "Shaoxing"), ("湖州", "Huzhou"), ("常州", "Changzhou"),
    ("徐州", "Xuzhou"), ("扬州", "Yangzhou"), ("南通", "Nantong"),
    ("洛阳", "Luoyang"), ("襄阳", "Xiangyang"), ("宜昌", "Yichang"),
    ("桂林", "Guilin"), ("柳州", "Liuzhou"), ("三亚", "Sanya"),
    ("珠海", "Zhuhai"), ("湛江", "Zhanjiang"), ("汕头", "Shantou"),
    ("珠海", "Zhuhai"), ("威海", "Weihai"), ("泰安", "Tai'an"),
    ("临沂", "Linyi"), ("赣州", "Ganzhou"), ("遵义", "Zunyi"),
    ("绵阳", "Mianyang"), ("德阳", "Deyang"), ("乐山", "Leshan"),
    ("宜宾", "Yibin"), ("泸州", "Luzhou"), ("南充", "Nanchong"),
    ("达州", "Dazhou"), ("内江", "Neijiang"), ("自贡", "Zigong"),
    ("攀枝花", "Panzhihua"), ("六盘水", "Liupanshui"), ("毕节", "Bijie"),
    ("曲靖", "Qujing"), ("大理", "Dali"), ("丽江", "Lijiang"),
    ("延安", "Yan'an"), ("榆林", "Yulin"), ("渭南", "Weinan"),
    ("宝鸡", "Baoji"), ("咸阳", "Xianyang"), ("汉中", "Hanzhong"),
    ("商丘", "Shangqiu"), ("周口", "Zhoukou"), ("驻马店", "Zhumadian"),
    ("信阳", "Xinyang"), ("南阳", "Nanyang"), ("开封", "Kaifeng"),
    ("安阳", "Anyang"), ("新乡", "Xinxiang"), ("许昌", "Xuchang"),
    ("芜湖", "Wuhu"), ("蚌埠", "Bengbu"), ("阜阳", "Fuyang"),
    ("安庆", "Anqing"), ("马鞍山", "Maanshan"), ("铜陵", "Tongling"),
    ("黄山", "Huangshan"), ("池州", "Chizhou"), ("宣城", "Xuancheng"),
    ("九江", "Jiujiang"), ("上饶", "Shangrao"), ("宜春", "Yichun"),
    ("景德镇", "Jingdezhen"), ("赣州", "Ganzhou"), ("吉安", "Ji'an"),
    ("漳州", "Zhangzhou"), ("龙岩", "Longyan"), ("三明", "Sanming"),
    ("莆田", "Putian"), ("宁德", "Ningde"), ("南平", "Nanping"),
    ("柳州", "Liuzhou"), ("桂林", "Guilin"), ("北海", "Beihai"),
    ("玉林", "Yulin"), ("百色", "Baise"), ("梧州", "Wuzhou"),
    ("韶关", "Shaoguan"), ("清远", "Qingyuan"), ("梅州", "Meizhou"),
    ("河源", "Heyuan"), ("阳江", "Yangjiang"), ("茂名", "Maoming"),
    ("揭阳", "Jieyang"), ("潮州", "Chaozhou"), ("汕尾", "Shanwei"),
    ("梅州", "Meizhou"), ("云浮", "Yunfu"),
    # 区/县级示例
    ("北京·海淀", "Haidian, Beijing"), ("北京·朝阳", "Chaoyang, Beijing"),
    ("北京·西城", "Xicheng, Beijing"), ("北京·东城", "Dongcheng, Beijing"),
    ("北京·丰台", "Fengtai, Beijing"), ("北京·通州", "Tongzhou, Beijing"),
    ("上海·浦东", "Pudong, Shanghai"), ("上海·闵行", "Minhang, Shanghai"),
    ("上海·徐汇", "Xuhui, Shanghai"), ("上海·静安", "Jing'an, Shanghai"),
    ("上海·宝山", "Baoshan, Shanghai"), ("上海·嘉定", "Jiading, Shanghai"),
    ("深圳·南山", "Nanshan, Shenzhen"), ("深圳·福田", "Futian, Shenzhen"),
    ("深圳·宝安", "Bao'an, Shenzhen"), ("深圳·龙岗", "Longgang, Shenzhen"),
    ("杭州·西湖", "West Lake, Hangzhou"), ("杭州·滨江", "Binjiang, Hangzhou"),
    ("成都·武侯", "Wuhou, Chengdu"), ("成都·锦江", "Jinjiang, Chengdu"),
    ("广州·天河", "Tianhe, Guangzhou"), ("广州·越秀", "Yuexiu, Guangzhou"),
    ("广州·番禺", "Panyu, Guangzhou"), ("广州·花都", "Huadu, Guangzhou"),
    ("南京·鼓楼", "Gulou, Nanjing"), ("南京·建邺", "Jianye, Nanjing"),
    ("武汉·武昌", "Wuchang, Wuhan"), ("武汉·汉口", "Hankou, Wuhan"),
    ("武汉·光谷", "Optics Valley, Wuhan"),
]


def save_city(value):
    """写入 weather.city"""
    try:
        with open(CITY_FILE, "w") as f:
            f.write("# 天气地点：写城市名（中英文均可），留空或删除本文件则按 IP 自动定位\n")
            f.write("%s\n" % value)
    except OSError:
        pass


def refresh_weather():
    try:
        import subprocess
        subprocess.Popen(
            ["hyprctl", "reload"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except Exception:
        pass


def search_nominatim(query, limit=10):
    """Nominatim 搜索，不加 countrycodes 限制"""
    try:
        url = (
            "https://nominatim.openstreetmap.org/search"
            "?format=jsonv2&limit=%d&accept-language=zh&"
            "q=%s" % (limit, urllib.parse.quote(query))
        )
        req = urllib.request.Request(url, headers={
            "User-Agent": "waybar-weather-popup/1.0 (personal use)",
        })
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode())
        results = []
        for d in data:
            name = d.get("name") or d.get("display_name", "").split(",")[0]
            # 用 display_name 作为写入值（wttr.in 能识别）
            write_val = d.get("display_name", name)
            results.append((name[:30], write_val))
        return results
    except Exception as e:
        return [("搜索失败: %s" % type(e).__name__, "")]


class WeatherCitySearch:
    def __init__(self):
        self.win = Gtk.Window()
        self.win.add_css_class("popupwin")
        self.win.set_decorated(False)
        Gtk4LayerShell.init_for_window(self.win)
        Gtk4LayerShell.set_namespace(self.win, "waybar-weather-city")
        Gtk4LayerShell.set_layer(self.win, Gtk4LayerShell.Layer.OVERLAY)
        for edge in (
            Gtk4LayerShell.Edge.TOP,
            Gtk4LayerShell.Edge.BOTTOM,
            Gtk4LayerShell.Edge.LEFT,
            Gtk4LayerShell.Edge.RIGHT,
        ):
            Gtk4LayerShell.set_anchor(self.win, edge, True)
        Gtk4LayerShell.set_keyboard_mode(self.win, Gtk4LayerShell.KeyboardMode.EXCLUSIVE)
        Gtk4LayerShell.set_exclusive_zone(self.win, -1)

        self.root = Gtk.Box()
        self.root.set_hexpand(True)
        self.root.set_vexpand(True)

        self.panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.panel.add_css_class("panel")
        self.panel.set_halign(Gtk.Align.CENTER)
        self.panel.set_valign(Gtk.Align.START)
        self.panel.set_margin_top(MARGIN_TOP)
        self.panel.set_size_request(PANEL_W, -1)
        self.root.append(self.panel)
        self.win.set_child(self.root)

        # 点击外部关闭
        click = Gtk.GestureClick()
        click.connect("pressed", self._on_press)
        self.root.add_controller(click)

        # Esc 关闭
        keys = Gtk.EventControllerKey()
        keys.connect("key-pressed", self._on_key)
        self.win.add_controller(keys)

        # 标题
        title = Gtk.Label(label="🌤 搜索城市", halign=Gtk.Align.START)
        title.add_css_class("title")
        self.panel.append(title)

        # 搜索框
        self._entry = Gtk.Entry()
        self._entry.set_placeholder_text("输入城市/区/县…")
        self._entry.add_css_class("searchbox")
        self._entry.connect("changed", self._on_search)
        self._entry.connect("activate", self._on_enter)
        self.panel.append(self._entry)

        # 分隔线
        sep = Gtk.Box()
        sep.add_css_class("sep")
        self.panel.append(sep)

        # 结果列表（可滚动）
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_size_request(-1, 300)
        self._list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        scroll.set_child(self._list)
        self.panel.append(scroll)

        # 提示
        self._hint = Gtk.Label(label="↑↓ 选择 · 回车确认 · 也可直接输入后回车", halign=Gtk.Align.CENTER)
        self._hint.add_css_class("sub")
        self.panel.append(self._hint)

        self._show_local("")
        self._entry.grab_focus()

    def _on_key(self, _controller, keyval, _keycode, _state):
        if keyval == Gdk.KEY_Escape:
            self._close()
            return True
        return False

    def _on_press(self, _gesture, _n_press, x, y):
        alloc = self.panel.get_allocation()
        if x < alloc.x or x >= alloc.x + alloc.width:
            self._close()

    def _clear_list(self):
        for child in self._list.get_children():
            self._list.remove(child)

    def _add_row(self, display, write_val):
        btn = Gtk.Button(label=display)
        btn.add_css_class("row")
        btn.set_halign(Gtk.Align.FILL)
        btn.set_hexpand(True)
        btn.connect("clicked", lambda _b, v=write_val: self._select(v))
        self._list.append(btn)

    def _show_local(self, query):
        self._clear_list()
        matched = []
        for display, val in CITIES:
            if not query:
                matched.append((display, val))
            else:
                q = query.lower()
                if q in display.lower() or q in val.lower():
                    matched.append((display, val))
        if not matched:
            lbl = Gtk.Label(label="无本地匹配，尝试在线搜索…", halign=Gtk.Align.CENTER)
            lbl.add_css_class("sub")
            self._list.append(lbl)
        else:
            for display, val in matched[:15]:
                self._add_row(display, val)
            if len(matched) > 15:
                lbl = Gtk.Label(label="… 共 %d 个匹配" % len(matched), halign=Gtk.Align.CENTER)
                lbl.add_css_class("sub")
                self._list.append(lbl)

    def _on_search(self, entry):
        query = entry.get_text().strip()
        if not query:
            self._show_local("")
            return
        # 先显示本地匹配
        self._show_local(query)
        # 在线搜索（后台）
        threading.Thread(target=self._search_online, args=(query,), daemon=True).start()

    def _search_online(self, query):
        results = search_nominatim(query)
        GLib.idle_add(self._show_online, results)

    def _show_online(self, results):
        # 如果只有错误信息
        if len(results) == 1 and results[0][1] == "":
            err_label = Gtk.Label(label=results[0][0], halign=Gtk.Align.CENTER)
            err_label.add_css_class("sub")
            self._list.append(err_label)
            return False
        # 追加在线结果
        sep = Gtk.Box()
        sep.add_css_class("sep")
        self._list.append(sep)
        hdr = Gtk.Label(label="在线结果:", halign=Gtk.Align.START)
        hdr.add_css_class("sub")
        self._list.append(hdr)
        for display, val in results:
            self._add_row(display, val)
        return False

    def _on_enter(self, _entry):
        """回车：优先选择第一个结果，否则直接写入输入内容"""
        text = self._entry.get_text().strip()
        if not text:
            return
        # 如果有列表项，选第一个
        children = self._list.get_children()
        if children:
            first = children[0]
            if isinstance(first, Gtk.Button):
                first.emit("clicked")
                return
        # 没有匹配项 → 直接写入（wttr.in 可能识别）
        self._select(text)

    def _select(self, write_val):
        save_city(write_val)
        refresh_weather()
        self._close()

    def _close(self):
        self.win.destroy()
        loop = getattr(self, "loop", None)
        if loop:
            loop.quit()


CSS = """
window.popupwin { background: transparent; }
.panel {
    background: rgba(30, 32, 38, 0.92);
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
}
.title { font-size: 15px; font-weight: bold; color: #e8e8e8; }
.searchbox {
    background: rgba(50, 54, 62, 0.9);
    color: #e8e8e8;
    border: 1px solid rgba(100, 140, 200, 0.3);
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 14px;
}
.searchbox:focus { border-color: rgba(100, 160, 220, 0.8); }
.searchbox text { color: #e8e8e8; }
.searchbox placeholder { color: #888; }
button.row {
    background: transparent;
    color: #d0d8e0;
    border: none;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 13px;
    justify-content: start;
}
button.row:hover { background: rgba(80, 120, 180, 0.2); color: #fff; }
.sep { background: rgba(100, 140, 200, 0.15); min-height: 1px; margin: 4px 0; }
.sub { color: #889; font-size: 11px; }
"""


def main():
    Gtk.init()
    settings = Gtk.Settings.get_default()
    if settings:
        settings.set_property("gtk-application-prefer-dark-theme", True)

    provider = Gtk.CssProvider()
    provider.load_from_data(CSS.encode())
    display = Gdk.Display.get_default()
    Gtk.StyleContext.add_provider_for_display(
        display, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION, provider
    )

    pop = WeatherCitySearch()
    pop.win.present()
    loop = GLib.MainLoop()
    pop.loop = loop
    loop.run()


if __name__ == "__main__":
    main()
