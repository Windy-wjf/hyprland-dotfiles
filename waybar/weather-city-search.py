#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Waybar 天气城市搜索（GTK4 + gtk4-layer-shell）：风格与 popup.py 完全一致。"""
import os
import sys
import threading
import urllib.parse
import urllib.request

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
gi.require_version("Gtk4LayerShell", "1.0")
from gi.repository import Gdk, GLib, Gtk, Gtk4LayerShell

HOME = os.path.expanduser("~")
MARGIN_TOP = 42
PANEL_W = 320
CITY_FILE = os.path.join(HOME, ".config", "waybar", "weather.city")

CSS = """
window.popupwin, window.popupwin contents { background: transparent; }
window.popupwin { font-family: "JetBrainsMono Nerd Font", monospace; }
.panel {
    background-color: rgba(20, 20, 30, 0.55);
    border: none;
    border-radius: 16px;
    padding: 14px 16px;
}
.title { color: #e8e8d2; font-size: 13px; font-weight: bold; }
.sub { color: #9aa0a0; font-size: 11px; }
.rowtext { color: #e8e8e8; font-size: 12px; }
.val { color: #58d8ff; font-size: 13px; font-weight: bold; }
button.row {
    background: transparent;
    background-color: transparent;
    border: none;
    box-shadow: none;
    padding: 6px 8px;
    border-radius: 8px;
    min-height: 0;
}
button.row:hover { background-color: rgba(88, 216, 255, 0.1); }
.searchbox {
    background-color: rgba(40, 40, 55, 0.8);
    border: 1px solid rgba(88, 216, 255, 0.3);
    border-radius: 8px;
    padding: 8px 10px;
    color: #e8e8e8;
    font-size: 13px;
}
.searchbox:focus { border-color: rgba(88, 216, 255, 0.7); }
.sep { background-color: rgba(88, 216, 255, 0.15); min-height: 1px; }
"""

CITIES = [
    ("北京", "Beijing"), ("上海", "Shanghai"), ("成都", "Chengdu"),
    ("广州", "Guangzhou"), ("杭州", "Hangzhou"), ("深圳", "Shenzhen"),
    ("南京", "Nanjing"), ("武汉", "Wuhan"), ("西安", "Xi'an"), ("重庆", "Chongqing"),
]


def save_city(en_name):
    try:
        with open(CITY_FILE, "w") as f:
            f.write("# 天气地点：写城市名（中英文均可），留空或删除本文件则按 IP 自动定位\n")
            f.write("%s\n" % en_name)
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


def search_nominatim(query, limit=8):
    try:
        url = (
            "https://nominatim.openstreetmap.org/search"
            "?format=json&limit=%d&accept-language=zh&countrycodes=cn"
            "&q=%s" % (limit, urllib.parse.quote(query))
        )
        req = urllib.request.Request(url, headers={"User-Agent": "waybar-weather/1.0"})
        with urllib.request.urlopen(req, timeout=6) as resp:
            import json
            results = json.loads(resp.read().decode())
        out = []
        for r in results:
            name = r.get("display_name", "").split(",")[0]
            out.append((name, r.get("lat", ""), r.get("lon", "")))
        return out
    except Exception:
        return []


class WeatherCitySearch:
    def __init__(self):
        self._results_box = None
        self._entry = None

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

        click = Gtk.GestureClick()
        click.connect("pressed", self._on_press)
        self.root.add_controller(click)

        keys = Gtk.EventControllerKey()
        keys.connect("key-pressed", self._on_key)
        self.win.add_controller(keys)

        # 标题
        title = Gtk.Label(label="搜索城市", halign=Gtk.Align.START)
        title.add_css_class("title")
        self.panel.append(title)

        # 搜索框
        self._entry = Gtk.Entry()
        self._entry.set_placeholder_text("输入城市名…")
        self._entry.add_css_class("searchbox")
        self._entry.connect("changed", self._on_search)
        self._entry.connect("activate", self._on_enter)
        self.panel.append(self._entry)

        # 分隔线
        sep = Gtk.Box()
        sep.add_css_class("sep")
        self.panel.append(sep)

        # 结果列表
        self._results_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self._show_local("")
        self.panel.append(self._results_box)

    def _on_key(self, _controller, keyval, _keycode, _state):
        if keyval == Gdk.KEY_Escape:
            self._close()
            return True
        return False

    def _on_press(self, _gesture, _n_press, x, y):
        alloc = self.panel.get_allocation()
        if x < alloc.x or x >= alloc.x + alloc.width:
            self._close()

    def _show_local(self, query):
        for child in self._results_box.get_children():
            self._results_box.remove(child)
        for zh, en in CITIES:
            if query and query.lower() not in zh.lower() and query.lower() not in en.lower():
                continue
            self._add_row("%s  (%s)" % (zh, en), zh, en)
        if not self._results_box.get_children():
            lbl = Gtk.Label(label="无匹配，在线搜索中…", halign=Gtk.Align.START)
            lbl.add_css_class("sub")
            self._results_box.append(lbl)

    def _add_row(self, text, zh, en):
        btn = Gtk.Button(label=text)
        btn.add_css_class("row")
        btn.set_halign(Gtk.Align.FILL)
        btn.set_hexpand(True)
        btn.connect("clicked", lambda _b, z=zh, e=en: self._select(z, e))
        self._results_box.append(btn)

    def _on_search(self, entry):
        query = entry.get_text().strip()
        if not query:
            self._show_local("")
            return
        # 先显示本地匹配
        self._show_local(query)
        # 在线搜索（后台线程）
        threading.Thread(target=self._search_online, args=(query,), daemon=True).start()

    def _search_online(self, query):
        results = search_nominatim(query)
        if results:
            GLib.idle_add(self._show_online, results)

    def _show_online(self, results):
        for child in self._results_box.get_children():
            self._results_box.remove(child)
        for name, lat, lon in results:
            self._add_row(name, name, name)
        return False

    def _on_enter(self, _entry):
        children = self._results_box.get_children()
        if children:
            btn = children[0]
            btn.emit("clicked")

    def _select(self, zh, en):
        save_city(en)
        refresh_weather()
        self._close()

    def _close(self):
        self.win.destroy()
        loop = getattr(self, "loop", None)
        if loop:
            loop.quit()


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    Gtk.init()
    settings = Gtk.Settings.get_default()
    if settings:
        settings.set_property("gtk-application-prefer-dark-theme", True)

    provider = Gtk.CssProvider()
    provider.load_from_data(CSS.encode())
    display = Gdk.Display.get_default()
    Gtk.StyleContext.add_provider_for_display(
        display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )

    pop = WeatherCitySearch()
    pop.win.present()
    loop = GLib.MainLoop()
    pop.loop = loop
    loop.run()


if __name__ == "__main__":
    main()
