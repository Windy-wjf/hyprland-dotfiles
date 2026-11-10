#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Waybar 二级菜单（GTK4 + gtk4-layer-shell）：音量 / 亮度 / 网络。

整块屏幕铺一层透明 layer-shell 表面（overlay 层，独占键盘）：
点面板以外的任何位置（包括状态栏图标）或按 Esc 立即关闭，
不会再出现“打开后关不掉”的问题。

用法：popup.py [volume|brightness|network|calendar]
"""
import calendar
import datetime
import os
import re
import signal
import subprocess
import sys
import threading
import time

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
gi.require_version("Gtk4LayerShell", "1.0")
from gi.repository import Gdk, GLib, Gtk, Gtk4LayerShell

HOME = os.path.expanduser("~")
CACHE = os.path.join(HOME, ".cache", "waybar-brightness")
PIDFILE = "/run/user/%d/waybar-popup.pid" % os.getuid()
MARGIN_TOP = 42          # 顶栏高度 38 + 4
MARGIN_END = 4
PANEL_W = 320

CSS = """
window.popupwin, window.popupwin contents { background: transparent; }
window.popupwin { font-family: "JetBrainsMono Nerd Font", monospace; }
.panel {
    background-color: #1c1c22;
    border: 1px solid rgba(255, 255, 255, 0.14);
    border-radius: 16px;
    padding: 14px 16px;
}
.icon { color: #e8e8ee; font-size: 15px; }
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
button.row.active .rowtext { color: #58a6ff; }
.sep { background-color: rgba(255, 255, 255, 0.10); min-height: 1px; margin: 6px 2px; }
scale { padding: 8px 2px 12px 2px; }
scale trough { background-color: rgba(255, 255, 255, 0.14); background-image: none; border-radius: 999px; min-height: 8px; }
scale trough highlight,
scale highlight,
scale > trough > highlight { background-color: #2363e6; background-image: none; border-radius: 999px; }
scale trough slider { background-color: #e8e8ee; background-image: none; border-radius: 999px; min-width: 16px; min-height: 16px; }
entry {
    background-color: rgba(255, 255, 255, 0.08);
    color: #e8e8ee;
    border-radius: 8px;
    padding: 6px 10px;
    font-size: 12px;
}
entry:focus { box-shadow: 0 0 0 1px #2363e6; }
switch { background-color: rgba(255, 255, 255, 0.16); background-image: none; border-radius: 999px; }
switch:checked { background-color: #2363e6; }
scrollbar { background: transparent; border: none; }
scrollbar slider { background-color: rgba(255, 255, 255, 0.24); border-radius: 999px; min-width: 5px; }
.calwd { color: #9aa0aa; font-size: 11px; padding: 3px 0; }
.calday { color: #e8e8ee; font-size: 12px; padding: 3px 0; border-radius: 6px; }
.calday.today { color: #ffffff; background-color: #2363e6; background-image: none; }
button.navbtn label { color: #c8c8d2; font-size: 14px; }
"""


# --------------------------------------------------------------------------- #
# 命令辅助
# --------------------------------------------------------------------------- #
def run(cmd, timeout=10):
    env = dict(os.environ)
    env["LC_ALL"] = "C"
    env["LANG"] = "C"
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
    except Exception:
        return None


def bg(cmd):
    try:
        subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except Exception:
        pass


def terse_split(line):
    """nmcli -t 输出按未转义的 ':' 切分。"""
    out, cur, esc = [], "", False
    for ch in line:
        if esc:
            cur += ch
            esc = False
        elif ch == "\\":
            esc = True
        elif ch == ":":
            out.append(cur)
            cur = ""
        else:
            cur += ch
    out.append(cur)
    return out


# --------------------------------------------------------------------------- #
# 音量
# --------------------------------------------------------------------------- #
def get_volume():
    r = run(["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"])
    if not r or r.returncode != 0:
        return 0, False
    m = re.search(r"Volume:\s+([0-9.]+)", r.stdout)
    vol = int(round(float(m.group(1)) * 100)) if m else 0
    return vol, "MUTED" in r.stdout


def list_sinks():
    r = run(["pactl", "list", "sinks"], timeout=8)
    sinks = []
    if not r or r.returncode != 0:
        return sinks
    cur_id, cur_name, cur_desc = None, None, None
    for line in r.stdout.splitlines():
        m = re.match(r"^Sink #(\d+)$", line.strip())
        if m:
            if cur_id is not None:
                sinks.append((cur_id, cur_name, cur_desc))
            cur_id, cur_name, cur_desc = int(m.group(1)), "", ""
            continue
        s = line.strip()
        if s.startswith("Name:") and cur_id is not None:
            cur_name = s[5:].strip()
        elif s.startswith("Description:") and cur_id is not None:
            cur_desc = s[12:].strip()
    if cur_id is not None:
        sinks.append((cur_id, cur_name, cur_desc))
    return sinks


def default_sink():
    r = run(["pactl", "get-default-sink"])
    return (r.stdout or "").strip() if r else ""


# --------------------------------------------------------------------------- #
# 亮度（外接显示器 DDC/CI）
# --------------------------------------------------------------------------- #
def get_brightness():
    r = run(["ddcutil", "getvcp", "10", "--terse"], timeout=6)
    m = re.search(r"VCP 10 C (\d+) (\d+)", (r.stdout or "") if r else "")
    return int(m.group(1)) if m else 50


def set_brightness(v):
    run(["ddcutil", "setvcp", "10", str(int(v))], timeout=6)
    try:
        os.makedirs(os.path.dirname(CACHE), exist_ok=True)
        with open(CACHE, "w") as f:
            f.write(str(int(v)))
    except OSError:
        pass


# --------------------------------------------------------------------------- #
# 网络
# --------------------------------------------------------------------------- #
def wifi_enabled():
    r = run(["nmcli", "radio", "wifi"], timeout=6)
    return (r.stdout or "").strip() == "enabled" if r else False


def current_ssid():
    r = run(["nmcli", "-t", "-f", "ACTIVE,SSID", "dev", "wifi"], timeout=10)
    if not r:
        return ""
    for line in r.stdout.splitlines():
        parts = terse_split(line)
        if len(parts) >= 2 and parts[0] == "yes":
            return parts[1]
    return ""


def scan_aps():
    r = run(["nmcli", "-t", "-f", "ACTIVE,SIGNAL,SECURITY,SSID", "dev", "wifi", "list"], timeout=20)
    aps, seen = [], {}
    if not r:
        return aps
    for line in r.stdout.splitlines():
        parts = terse_split(line)
        if len(parts) < 4:
            continue
        active, sig, sec, ssid = parts[0], parts[1], parts[2], ":".join(parts[3:])
        if not ssid:
            continue
        try:
            signal_pct = int(sig)
        except ValueError:
            signal_pct = 0
        if ssid in seen:
            if signal_pct > seen[ssid]["signal"]:
                seen[ssid]["signal"] = signal_pct
                seen[ssid]["active"] = seen[ssid]["active"] or (active == "yes")
            continue
        ap = {"ssid": ssid, "signal": signal_pct, "sec": sec, "active": active == "yes"}
        seen[ssid] = ap
        aps.append(ap)
    aps.sort(key=lambda a: (not a["active"], -a["signal"]))
    return aps[:14]


# --------------------------------------------------------------------------- #
# 弹窗
# --------------------------------------------------------------------------- #
class Popup:
    def __init__(self, mode):
        self.mode = mode
        self._sync = True
        self._vol_timer = 0
        self._bri_timer = 0

        self.win = Gtk.Window()
        self.win.add_css_class("popupwin")
        self.win.set_decorated(False)
        Gtk4LayerShell.init_for_window(self.win)
        Gtk4LayerShell.set_namespace(self.win, "waybar-popup")
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
        self.panel.set_halign(Gtk.Align.END)
        self.panel.set_valign(Gtk.Align.START)
        self.panel.set_margin_top(MARGIN_TOP)
        self.panel.set_margin_end(MARGIN_END)
        self.panel.set_size_request(PANEL_W, -1)
        self.root.append(self.panel)
        self.win.set_child(self.root)

        click = Gtk.GestureClick()
        click.connect("pressed", self._on_press)
        self.root.add_controller(click)

        keys = Gtk.EventControllerKey()
        keys.connect("key-pressed", self._on_key)
        self.win.add_controller(keys)

        if mode == "network":
            self.build_network()
        elif mode == "brightness":
            self.build_brightness()
        elif mode == "calendar":
            self.build_calendar()
        else:
            self.build_volume()

    # -- 基础组件 ----------------------------------------------------------
    def header(self, icon, title, value_text):
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        il = Gtk.Label(label=icon)
        il.add_css_class("icon")
        tl = Gtk.Label(label=title)
        tl.add_css_class("title")
        tl.set_xalign(0)
        tl.set_hexpand(True)
        vl = Gtk.Label(label=value_text)
        vl.add_css_class("val")
        box.append(il)
        box.append(tl)
        box.append(vl)
        return box, vl

    def make_row(self, text, icon="", cb=None, active=False, extra=""):
        btn = Gtk.Button()
        btn.add_css_class("row")
        if active:
            btn.add_css_class("active")
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        il = Gtk.Label(label=icon)
        il.add_css_class("icon")
        il.set_size_request(16, -1)
        box.append(il)
        tl = Gtk.Label(label=text)
        tl.add_css_class("rowtext")
        tl.set_xalign(0)
        tl.set_hexpand(True)
        tl.set_ellipsize(3)
        tl.set_max_width_chars(26)
        box.append(tl)
        if extra:
            el = Gtk.Label(label=extra)
            el.add_css_class("sub")
            box.append(el)
        btn.set_child(box)
        if cb is not None:
            btn.connect("clicked", cb)
        return btn, tl, il

    def sep(self):
        s = Gtk.Box()
        s.add_css_class("sep")
        s.set_size_request(-1, 1)
        return s

    def section(self, text):
        l = Gtk.Label(label=text)
        l.add_css_class("sub")
        l.set_xalign(0)
        l.set_margin_top(4)
        return l

    def clear(self):
        while self.panel.get_first_child() is not None:
            self.panel.remove(self.panel.get_first_child())

    # -- 事件 --------------------------------------------------------------
    def _on_press(self, gesture, n_press, x, y):
        try:
            pw, ph = self.panel.get_width(), self.panel.get_height()
            left = self.root.get_width() - pw - MARGIN_END
            if left - 2 <= x <= left + pw + 2 and MARGIN_TOP - 2 <= y <= MARGIN_TOP + ph + 2:
                return
        except Exception:
            pass
        self.close()

    def _on_key(self, ctrl, keyval, keycode, state):
        if keyval == Gdk.KEY_Escape:
            self.close()
            return True
        return False

    def close(self):
        try:
            self.win.destroy()
        except Exception:
            pass
        try:
            os.unlink(PIDFILE)
        except OSError:
            pass
        loop = getattr(self, "loop", None)
        if loop is not None:
            loop.quit()

    # -- 音量 --------------------------------------------------------------
    def build_volume(self):
        self._sync = True
        vol, muted = get_volume()
        head, self.val_lbl = self.header("", "音量", "%d%%" % vol)
        self.panel.append(head)

        self.scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        self.scale.set_draw_value(False)
        self.scale.set_value(vol)
        self.scale.set_hexpand(True)
        self.scale.connect("value-changed", self._on_vol_change)
        self.panel.append(self.scale)

        mb, self.mute_lbl, _ = self.make_row(
            "取消静音" if muted else "静音", "" if muted else " ", self._toggle_mute
        )
        self.panel.append(mb)

        self.panel.append(self.sep())
        self.panel.append(self.section("输出设备"))
        default = default_sink()
        for _sid, sname, desc in list_sinks():
            active = sname == default
            b, _l, _i = self.make_row(
                desc or sname,
                "✓" if active else " ",
                lambda _w, n=sname: self._set_default_sink(n),
                active=active,
            )
            self.panel.append(b)

        self.panel.append(self.sep())
        b, _l, _i = self.make_row("打开混音器", "", lambda _w: (bg(["pavucontrol"]), self.close()))
        self.panel.append(b)
        self._sync = False

    def _on_vol_change(self, scale):
        v = int(round(scale.get_value()))
        self.val_lbl.set_label("%d%%" % v)
        if self._sync:
            return
        if self._vol_timer:
            GLib.source_remove(self._vol_timer)
        self._vol_timer = GLib.timeout_add(70, self._apply_vol, v)

    def _apply_vol(self, v):
        self._vol_timer = 0
        bg(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", "%d%%" % v])
        return False

    def _toggle_mute(self, _btn):
        bg(["wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "toggle"])
        GLib.timeout_add(120, self._refresh_mute)

    def _refresh_mute(self):
        _vol, muted = get_volume()
        self.mute_lbl.set_label("取消静音" if muted else "静音")
        return False

    def _set_default_sink(self, name):
        bg(["pactl", "set-default-sink", name])
        self.clear()
        self.build_volume()

    # -- 亮度 --------------------------------------------------------------
    def build_brightness(self):
        self._sync = True
        val = get_brightness()
        head, self.val_lbl = self.header("", "显示器亮度", "%d%%" % val)
        self.panel.append(head)

        self.scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        self.scale.set_draw_value(False)
        self.scale.set_value(val)
        self.scale.set_hexpand(True)
        self.scale.connect("value-changed", self._on_bri_change)
        self.panel.append(self.scale)

        info = Gtk.Label(label="DDC/CI · DP-1 · HKC G27H7Pro")
        info.add_css_class("sub")
        info.set_xalign(0)
        self.panel.append(info)

        preset_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        preset_row.set_homogeneous(True)
        for pct in (25, 50, 75, 100):
            b, _l, _i = self.make_row(
                "%d%%" % pct, "", lambda _w, p=pct: self._preset_brightness(p)
            )
            b.set_hexpand(True)
            preset_row.append(b)
        self.panel.append(preset_row)
        self._sync = False

    def _on_bri_change(self, scale):
        v = int(round(scale.get_value()))
        self.val_lbl.set_label("%d%%" % v)
        if self._sync:
            return
        if self._bri_timer:
            GLib.source_remove(self._bri_timer)
        self._bri_timer = GLib.timeout_add(280, self._apply_bri, v)

    def _apply_bri(self, v):
        self._bri_timer = 0
        set_brightness(v)
        return False

    def _preset_brightness(self, pct):
        self._sync = True
        self.scale.set_value(pct)
        self.val_lbl.set_label("%d%%" % pct)
        self._sync = False
        set_brightness(pct)

    # -- 日历 --------------------------------------------------------------
    def build_calendar(self):
        today = datetime.date.today()
        self._cal_y, self._cal_m = today.year, today.month
        self.render_calendar()

    def render_calendar(self):
        self.clear()
        today = datetime.date.today()
        y, m = self._cal_y, self._cal_m

        nav = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        prev = Gtk.Button(label="\u2039")
        prev.add_css_class("row")
        prev.add_css_class("navbtn")
        prev.set_size_request(36, -1)
        prev.connect("clicked", lambda _b: self._cal_shift(-1))
        title = Gtk.Label(label="%d \u5e74 %d \u6708" % (y, m))
        title.add_css_class("title")
        title.set_hexpand(True)
        nxt = Gtk.Button(label="\u203a")
        nxt.add_css_class("row")
        nxt.add_css_class("navbtn")
        nxt.set_size_request(36, -1)
        nxt.connect("clicked", lambda _b: self._cal_shift(1))
        nav.append(prev)
        nav.append(title)
        nav.append(nxt)
        self.panel.append(nav)

        grid = Gtk.Grid(column_spacing=2, row_spacing=2)
        grid.set_halign(Gtk.Align.CENTER)
        for i, wd in enumerate(("\u4e00", "\u4e8c", "\u4e09", "\u56db", "\u4e94", "\u516d", "\u65e5")):
            l = Gtk.Label(label=wd)
            l.add_css_class("calwd")
            l.set_size_request(38, -1)
            grid.attach(l, i, 0, 1, 1)

        for r, week in enumerate(calendar.monthcalendar(y, m), start=1):
            for c, day in enumerate(week):
                if day == 0:
                    continue
                l = Gtk.Label(label=str(day))
                l.add_css_class("calday")
                if (y, m, day) == (today.year, today.month, today.day):
                    l.add_css_class("today")
                l.set_size_request(38, -1)
                grid.attach(l, c, r, 1, 1)
        self.panel.append(grid)

        foot = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        tl = Gtk.Label(label="\u4eca\u5929  %d/%02d/%02d" % (today.year, today.month, today.day))
        tl.add_css_class("sub")
        tl.set_xalign(0)
        tl.set_hexpand(True)
        tb = Gtk.Button(label="\u56de\u5230\u4eca\u5929")
        tb.add_css_class("row")
        tb.connect("clicked", lambda _b: self._cal_today())
        foot.append(tl)
        foot.append(tb)
        self.panel.append(foot)

    def _cal_shift(self, delta):
        m = self._cal_m - 1 + delta
        y = self._cal_y + m // 12
        m = m % 12 + 1
        self._cal_y, self._cal_m = y, m
        self.render_calendar()

    def _cal_today(self):
        t = datetime.date.today()
        self._cal_y, self._cal_m = t.year, t.month
        self.render_calendar()

    # -- 网络 --------------------------------------------------------------
    def build_network(self):
        wifi = wifi_enabled()
        ssid = current_ssid()

        head = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        il = Gtk.Label(label="")
        il.add_css_class("icon")
        tl = Gtk.Label(label="Wi-Fi")
        tl.add_css_class("title")
        tl.set_xalign(0)
        tl.set_hexpand(True)
        sw = Gtk.Switch()
        sw.set_active(wifi)
        sw.connect("state-set", self._on_wifi_switch)
        head.append(il)
        head.append(tl)
        head.append(sw)
        self.panel.append(head)

        status = "已连接 %s" % ssid if ssid else ("Wi-Fi 已开启" if wifi else "Wi-Fi 已关闭")
        sl = Gtk.Label(label=status)
        sl.add_css_class("sub")
        sl.set_xalign(0)
        self.panel.append(sl)

        if not wifi:
            b, _l, _i = self.make_row("打开 Wi-Fi", "", lambda _w: self._wifi_on())
            self.panel.append(b)
            self.panel.append(self.sep())
            b, _l, _i = self.make_row("打开 nmtui (终端)", "", lambda _w: (bg(["kitty", "-e", "nmtui"]), self.close()))
            self.panel.append(b)
            return

        self.ap_rows = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroller.set_max_content_height(360)
        scroller.set_propagate_natural_height(True)
        scroller.set_child(self.ap_rows)
        self.panel.append(scroller)
        loading = Gtk.Label(label="扫描中…")
        loading.add_css_class("sub")
        loading.set_xalign(0)
        self.ap_rows.append(loading)

        self.panel.append(self.sep())
        if ssid:
            b, _l, _i = self.make_row("断开 %s" % ssid, "", lambda _w: self._disconnect())
            self.panel.append(b)
        b, _l, _i = self.make_row("重新扫描", "", lambda _w: self.rebuild_network())
        self.panel.append(b)
        b, _l, _i = self.make_row("打开 nmtui (终端)", "", lambda _w: (bg(["kitty", "-e", "nmtui"]), self.close()))
        self.panel.append(b)

        threading.Thread(target=self._scan_thread, daemon=True).start()

    def _scan_thread(self):
        aps = scan_aps()
        GLib.idle_add(self._fill_aps, aps)

    def _fill_aps(self, aps):
        try:
            while self.ap_rows.get_first_child() is not None:
                self.ap_rows.remove(self.ap_rows.get_first_child())
        except Exception:
            return False
        if not aps:
            l = Gtk.Label(label="未发现可用的 Wi-Fi")
            l.add_css_class("sub")
            l.set_xalign(0)
            self.ap_rows.append(l)
            return False
        for ap in aps:
            sec = bool(ap["sec"] and ap["sec"] != "--")
            extra = "%d%%" % ap["signal"]
            icon = "✓" if ap["active"] else ("" if sec else "")
            b, _l, _i = self.make_row(
                ap["ssid"],
                "✓" if ap["active"] else icon,
                lambda _w, a=ap: self.connect_ap(a),
                active=ap["active"],
                extra=extra,
            )
            self.ap_rows.append(b)
        return False

    def rebuild_network(self):
        self.clear()
        self.build_network()

    def _on_wifi_switch(self, sw, state):
        bg(["nmcli", "radio", "wifi", "on" if state else "off"])
        GLib.timeout_add(900, self._rebuild_idle)
        return False

    def _rebuild_idle(self):
        self.rebuild_network()
        return False

    def _wifi_on(self):
        bg(["nmcli", "radio", "wifi", "on"])
        GLib.timeout_add(900, self._rebuild_idle)

    def _disconnect(self):
        bg(["nmcli", "dev", "disconnect", "wlan0"])
        GLib.timeout_add(900, self._rebuild_idle)

    def connect_ap(self, ap):
        if ap.get("active"):
            return
        ssid = ap["ssid"]
        self._set_status("正在连接 %s …" % ssid)
        threading.Thread(target=self._do_connect, args=(ssid, None), daemon=True).start()

    def _set_status(self, text):
        if getattr(self, "_status", None) is None:
            self._status = Gtk.Label(label=text)
            self._status.add_css_class("sub")
            self._status.set_xalign(0)
            self._status.set_wrap(True)
            self.panel.append(self._status)
        else:
            self._status.set_label(text)

    def _do_connect(self, ssid, password):
        cmd = ["nmcli", "dev", "wifi", "connect", ssid]
        if password:
            cmd += ["password", password]
        r = run(cmd, timeout=60)
        out = ((r.stdout or "") + (r.stderr or "")) if r else ""
        ok = bool(r and r.returncode == 0)
        low = out.lower()
        need_pw = ("secrets" in low) or ("password" in low) or ("密码" in out) or ("passphrase" in low)
        GLib.idle_add(self._after_connect, ssid, password, ok, need_pw, out)

    def _after_connect(self, ssid, password, ok, need_pw, out):
        if ok:
            self.rebuild_network()
            return False
        if need_pw and not password:
            self.ask_password(ssid)
            return False
        msg = out.strip().splitlines()[-1] if out.strip() else "连接失败"
        self._set_status("连接失败：%s" % msg)
        return False

    def ask_password(self, ssid):
        self.clear()
        head, _vl = self.header("", "连接到 %s" % ssid, "")
        self.panel.append(head)
        entry = Gtk.PasswordEntry()
        entry.set_show_peek_icon(True)
        entry.set_placeholder_text("Wi-Fi 密码")
        self.panel.append(entry)
        self.panel.append(self.sep())

        def submit(_w):
            pw = entry.get_text()
            if not pw:
                return
            self.clear()
            head2, _v = self.header("", "连接到 %s" % ssid, "")
            self.panel.append(head2)
            wait = Gtk.Label(label="正在连接…")
            wait.add_css_class("sub")
            wait.set_xalign(0)
            self.panel.append(wait)
            threading.Thread(target=self._do_connect, args=(ssid, pw), daemon=True).start()

        b, _l, _i = self.make_row("连接", "", submit, active=True)
        self.panel.append(b)
        b, _l, _i = self.make_row("返回", "", lambda _w: self.rebuild_network())
        self.panel.append(b)
        entry.grab_focus()

    @property
    def status_lbl(self):
        return getattr(self, "_status", None)


# --------------------------------------------------------------------------- #
def kill_existing():
    try:
        with open(PIDFILE) as f:
            pid = int(f.read().strip())
        os.kill(pid, signal.SIGTERM)
        time.sleep(0.06)
    except Exception:
        pass


def ensure_preload():
    """gtk4-layer-shell 必须先于 libwayland 载入，否则 layer 表面初始化失败。"""
    if os.environ.get("WAYBAR_POPUP_REEXEC") == "1":
        return
    if "libgtk4-layer-shell.so" in os.environ.get("LD_PRELOAD", ""):
        return
    env = dict(os.environ)
    old = env.get("LD_PRELOAD", "")
    env["LD_PRELOAD"] = "/usr/lib/libgtk4-layer-shell.so" + ((" " + old) if old else "")
    env["WAYBAR_POPUP_REEXEC"] = "1"
    os.execve(sys.executable, [sys.executable, os.path.realpath(__file__)] + sys.argv[1:], env)


def main():
    ensure_preload()
    mode = sys.argv[1] if len(sys.argv) > 1 else "volume"
    if mode not in ("volume", "brightness", "network", "calendar"):
        mode = "volume"

    kill_existing()
    try:
        with open(PIDFILE, "w") as f:
            f.write(str(os.getpid()))
    except OSError:
        pass

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

    pop = Popup(mode)
    pop.win.present()
    loop = GLib.MainLoop()
    pop.loop = loop
    loop.run()
    try:
        os.unlink(PIDFILE)
    except OSError:
        pass


if __name__ == "__main__":
    main()
