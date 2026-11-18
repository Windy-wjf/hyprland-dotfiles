#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Waybar 天气城市搜索（GTK4 + gtk4-layer-shell）：风格与 popup.py 一致。

半透明面板居中于顶栏下方，点击外部或按 Esc 关闭。
支持离线候选城市 + Nominatim 在线搜索。
"""
import os
import sys
import threading
import urllib.parse
import urllib.request
import json

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
gi.require_version("Gtk4LayerShell", "1.0")
from gi.repository import Gdk, GLib, Gtk, Gtk4LayerShell

MARGIN_TOP = 42          # 顶栏高度 38 + 4
PANEL_W = 320

CITY_FILE = os.path.expanduser("~/.config/waybar/weather.city")

# 离线候选城市
CANDIDATES = [
    ("成都", "Chengdu", 30.5728, 104.0668),
    ("北京", "Beijing", 39.9042, 116.4074),
    ("上海", "Shanghai", 31.2304, 121.4737),
    ("广州", "Guangzhou", 23.1291, 113.2644),
    ("深圳", "Shenzhen", 22.5431, 114.0579),
    ("杭州", "Hangzhou", 30.2741, 120.1551),
    ("南京", "Nanjing", 32.0603, 118.7969),
    ("武汉", "Wuhan", 30.5928, 114.3055),
    ("西安", "Xi'an", 34.3416, 108.9398),
    ("青岛", "Qingdao", 36.0671, 120.3826),
    ("厦门", "Xiamen", 24.4798, 118.0894),
    ("长沙", "Changsha", 28.2282, 112.9388),
    ("重庆", "Chongqing", 29.5630, 106.5516),
    ("苏州", "Suzhou", 31.2989, 120.5853),
    ("天津", "Tianjin", 39.3434, 117.3616),
    ("沈阳", "Shenyang", 41.8057, 123.4315),
    ("大连", "Dalian", 38.9140, 121.6147),
    ("哈尔滨", "Harbin", 45.8038, 126.5350),
    ("昆明", "Kunming", 24.8801, 102.8329),
    ("贵阳", "Guiyang", 26.6470, 106.6302),
    ("南宁", "Nanning", 22.8170, 108.3665),
    ("海口", "Haikou", 20.0440, 110.3418),
    ("拉萨", "Lhasa", 29.6500, 91.1000),
    ("乌鲁木齐", "Urumqi", 43.8256, 87.6168),
    ("兰州", "Lanzhou", 36.0611, 103.8343),
    ("太原", "Taiyuan", 37.8706, 112.5489),
    ("郑州", "Zhengzhou", 34.7466, 113.6253),
    ("合肥", "Hefei", 31.8206, 117.2272),
    ("福州", "Fuzhou", 26.0745, 119.2965),
    ("济南", "Jinan", 36.6512, 117.1201),
    ("石家庄", "Shijiazhuang", 38.0428, 114.5149),
    ("无锡", "Wuxi", 31.4912, 120.3119),
    ("宁波", "Ningbo", 29.8683, 121.5440),
    ("温州", "Wenzhou", 28.0000, 120.7000),
    ("烟台", "Yantai", 37.4640, 121.4475),
    ("威海", "Weihai", 37.5128, 122.1206),
    ("珠海", "Zhuhai", 22.2710, 113.5767),
    ("泉州", "Quanzhou", 24.8741, 118.6757),
    ("洛阳", "Luoyang", 34.6197, 112.4540),
    ("桂林", "Guilin", 25.2740, 110.2900),
]

# Nominatim 结果缓存
_cache = {}

CSS = """
window.popupwin, window.popupwin contents { background: transparent; }
window.popupwin { font-family: "JetBrainsMono Nerd Font", monospace; }
.panel {
    background-color: rgba(20, 20, 30, 0.55);
    border: none;
    border-radius: 16px;
    padding: 14px 16px;
}
.title { color: #e8e8ee; font-size: 13px; font-weight: bold; }
.sub { color: #9aa0aa; font-size: 11px; }
.rowtext { color: #e8e8ee; font-size: 12px; }
.val { color: #58a6ff; font-size: 13px; font-weight: bold; }
button.row {
    background: transparent;
    background-color: transparent;
    border: none;
    box-shadow: none;
    padding: 6px 8px;
    border-radius: 8px;
    min-height: 0;
}
button.row:hover { background-color: rgba(35, 99, 230, 0.30); background-image: none; }
.sep { background-color: rgba(255, 255, 255, 0.10); min-height: 1px; margin: 6px 2px; }
entry {
    background-color: rgba(255, 255, 255, 0.08);
    color: #e8e8ee;
    border-radius: 8px;
    padding: 6px 10px;
    font-size: 12px;
}
entry:focus { box-shadow: 0 0 0 1px #2363e6; }
scrollbar { background: transparent; border: none; }
scrollbar slider { background-color: rgba(255, 255, 255, 0.24); border-radius: 999px; min-width: 5px; }
"""


def search_nominatim(query, limit=8):
    """调用 Nominatim 搜索城市，返回 [(display_name, lat, lon), ...]"""
    global _cache
    if query in _cache:
        return _cache[query]
    try:
        url = (
            "https://nominatim.openstreetmap.org/search"
            "?format=json&limit=%d&accept-language=zh&countrycodes=cn"
            "&q=%s" % (limit, urllib.parse.quote(query))
        )
        req = urllib.request.Request(url, headers={
            "User-Agent": "waybar-weather-popup/1.0",
        })
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        results = [
            (d.get("display_name", "")[:40], float(d.get("lat", 0)), float(d.get("lon", 0)))
            for d in data
        ]
        _cache[query] = results
        return results
    except Exception:
        return []


def save_city(name, en_name):
    """写入 weather.city 文件（写英文名供 wttr.in 使用）"""
    try:
        with open(CITY_FILE, "w") as f:
            f.write("# 天气地点：写城市名（中英文均可），留空或删除本文件则按 IP 自动定位\n")
            f.write("%s\n" % en_name)
    except OSError:
        pass


def refresh_weather():
    """触发 waybar 刷新天气模块（通过 reload）"""
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

        # 根容器：全透明
        self.root = Gtk.Box()
        self.root.set_hexpand(True)
        self.root.set_vexpand(True)

        # 面板：居中于顶栏下方
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
        title = Gtk.Label(label="搜索城市", halign=Gtk.Align.START)
        title.add_css_class("title")
        self.panel.append(title)

        # 搜索框
        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text("输入城市名搜索…")
        self.entry.connect("changed", self._on_search)
        self.entry.connect("activate", self._on_enter)
        self.panel.append(self.entry)

        # 分隔线
        sep = Gtk.Box()
        sep.add_css_class("sep")
        self.panel.append(sep)

        # 结果列表
        self.results_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self._show_candidates("")
        self.panel.append(self.results_box)

        # CSS
        prov = Gtk.CssProvider()
        prov.load_from_data(CSS.encode("utf-8"))
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(), prov, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def _on_key(self, _controller, keyval, _keycode, _state):
        if keyval == Gdk.KEY_Escape:
            self._close()
            return True
        return False

    def _on_press(self, _gesture, _n_press, x, y):
        # 点击面板外部关闭
        alloc = self.panel.get_allocation()
        if x < alloc.x or x >= alloc.x + alloc.width:
            self._close()
            return
        if y < alloc.y or y >= alloc.y + alloc.height:
            self._close()
            return

    def _close(self):
        self.win.destroy()

    def _on_search(self, _entry, text):
        text = (text or "").strip()
        if not text:
            self._show_candidates("")
            return
        # 先显示离线候选
        self._show_candidates(text)
        # 后台在线搜索
        threading.Thread(target=self._online_search, args=(text,), daemon=True).start()

    def _on_enter(self, _entry):
        """回车：选择第一个结果"""
        text = (self.entry.get_text() or "").strip()
        if not text:
            return
        # 找第一个离线候选
        for zh, en, lat, lon in CANDIDATES:
            if text in zh or text.lower() in en.lower():
                self._select_city(zh, en, lat, lon)
                return
        # 在线搜索第一个结果
        results = search_nominatim(text)
        if results:
            name, lat, lon = results[0]
            self._select_city(name, name, lat, lon)

    def _online_search(self, text):
        results = search_nominatim(text)
        GLib.idle_add(self._show_online_results, text, results)

    def _show_online_results(self, text, results):
        """显示在线搜索结果（合并到离线候选后面）"""
        self._clear_results_box()
        for zh, en, lat, lon in self._filter_candidates(text):
            self._append_result(zh + "  " + en, zh, en)
        # 分隔线
        if results:
            sep = Gtk.Box()
            sep.add_css_class("sep")
            self.results_box.append(sep)
        for name, lat, lon in results:
            self._append_result(name + "  ⌖", name, name)
        if not self._filter_candidates(text) and not results:
            label = Gtk.Label(label="未找到", halign=Gtk.Align.CENTER)
            label.add_css_class("sub")
            self.results_box.append(label)
        return False

    def _show_candidates(self, text):
        """显示离线候选城市列表"""
        self._clear_results_box()
        candidates = self._filter_candidates(text)
        if not candidates:
            label = Gtk.Label(label="输入关键词过滤", halign=Gtk.Align.CENTER)
            label.add_css_class("sub")
            self.results_box.append(label)
            return
        for zh, en, lat, lon in candidates[:10]:
            self._append_result(zh + "  " + en, zh, en)

    def _filter_candidates(self, text):
        if not text:
            return CANDIDATES
        text_lower = text.lower()
        return [
            (zh, en, lat, lon)
            for zh, en, lat, lon in CANDIDATES
            if text_lower in zh.lower() or text_lower in en.lower()
        ]

    def _clear_results_box(self):
        child = self.results_box.get_first_child()
        while child:
            self.results_box.remove(child)
            child = self.results_box.get_first_child()

    def _append_result(self, display, zh_name, en_name):
        btn = Gtk.Button(label=display)
        btn.add_css_class("row")
        btn.set_halign(Gtk.Align.FILL)
        btn.set_hexpand(True)
        # 用 rowtext 样式
        btn.set_label("")
        lbl = Gtk.Label(label=display, halign=Gtk.Align.START)
        lbl.add_css_class("rowtext")
        btn.set_child(lbl)
        btn.connect("clicked", lambda _b, z=zh_name, e=en_name: self._select_city(z, e, 0, 0))
        self.results_box.append(btn)

    def _select_city(self, zh, en, lat, lon):
        save_city(zh, en)
        refresh_weather()
        self._close()

    def run(self):
        self.win.present()
        loop = GLib.MainLoop()
        loop.run()


if __name__ == "__main__":
    app = WeatherCitySearch()
    app.run()
