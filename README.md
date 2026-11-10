# Hyprland Config

A complete, self-contained Hyprland workspace built around **Hyprland + waybar**,
tuned for an AMD (RDNA4) laptop with a HiDPI display. This is the "core" of the
setup: the window manager, a custom waybar taskbar (Arch-logo app menu, dynamic
workspaces, GPU/CPU/battery monitors), a Python wallpaper picker, and Chinese
(fcitx5) input.

> **Status — portable.** Every path uses `$HOME` / `$XDG_RUNTIME_DIR` /
> `$XDG_CONFIG_HOME` (or `os.getuid()` in the scripts), so it installs for any user.
> One exception: the wallpaper path in `hypr/hyprpaper.conf` is an absolute path that
> `install.sh` rewrites for your home, because hyprpaper cannot expand `$HOME`.

## Layout

```
hypr/                 # Hyprland config (DPython Lua)
  hyprland.lua        #   main config — monitors, binds, autostart, window rules
  hyprpaper.conf      #   wallpaper (see "Customising")
  hyprlock.conf       #   lock screen
  hypridle.conf       #   auto-lock / power hooks
waybar/               # waybar bar: config + style + the Python modules
  config.jsonc        #   bar layout (taskbar, workspaces, cpu/vram/battery/clock…)
  style.css           #   bar styling
  popup.py            #   GTK4 popover menus (volume / brightness / network / clock)
  cpu vram sysmon     #   Python status scripts (read /proc + the GPU)
  weather city        #   Open-Meteo weather module + the city file
  wsdaemon wsbar …    #   dynamic-workspace daemons / scripts
  archmenu            #   Arch-logo app menu (fuzzel --dmenu)
kitty/                # kitty terminal config
fcitx5/               # fcitx5 input method (Pinyin) config
assets/
  wallpaper.jpg       #   default wallpaper (installed to ~/Pictures/)
```

## Dependencies

Core (Arch package names — adjust as needed):

- **Hyprland** — the window manager. The main config is DPython
  (`hypr/hyprland.lua`); Hyprland runs it natively when the file is named `*.lua`.
- **waybar** — the status/task bar.
- **Python 3** — the bar modules are Python. The *only* third-party import is `gi`
  (PyGObject); the rest is the standard library:
  - `python3-pygobject`
  - `gtk4-layer-shell` — provides `Gtk4LayerShell 1.0`, used by `popup.py`
  - `gtk4` — GTK 4, also required by `popup.py`

Used by the config / scripts:

- **fcitx5** — Chinese (Pinyin) input, driven by the `fcitx5/` config.
- **kitty** — the terminal (`$TERMINAL`).
- **hyprpaper** — applies the wallpaper at startup.
- **hyprlock** / **hypridle** — screen lock + auto-lock / power hooks.
- **fuzzel** — the Arch-logo app menu (`waybar/archmenu`). It reads
  `~/.config/fuzzel/fuzzel.ini`; ship your own or it uses fuzzel defaults.
- **rofi** — the generic app launcher (`Super+R`).
- **nautilus** — the file manager (`$FILE_MANAGER`).
- **playerctl**, **brightnessctl**, **wpctl** — XF86 media / brightness / volume binds.
- **Open-Meteo** (no API key) — the weather module calls `api.open-meteo.com`.

## Install

Option A — one script:

```sh
./install.sh
```

Option B — manually, copy each tree into `~/.config/`:

```sh
mkdir -p ~/.config
cp -a hypr/.     ~/.config/hypr/
cp -a waybar/.   ~/.config/waybar/
cp -a kitty/.    ~/.config/kitty/
cp -a fcitx5/.   ~/.config/fcitx5/
cp assets/wallpaper.jpg ~/Pictures/wallhaven-jev9xw.jpg
```

Then set the wallpaper path in `~/.config/hypr/hyprpaper.conf` to wherever you put
the image (hyprpaper needs an absolute path).

After installing, **log out and log back in** so the autostarts (waybar, the
workspace daemons, hyprpaper, fcitx5) start cleanly. A quick `hyprctl reload` plus a
manual (re)start of `waybar` works if you don't want to log out.

## Customising

- **Wallpaper** — replace `assets/wallpaper.jpg` and re-run `install.sh` (or just copy
  a new image to `~/Pictures/wallhaven-jev9xw.jpg` and edit `hyprpaper.conf`).
- **City** — edit `waybar/weather.city` (one city name; the weather module falls back
  to `Shanghai` if the file is missing).
- **Apps shown in the bar** — `waybar/apps.json`, toggled via `appadd` / `appdel` / `appsync`.
- **Binds / workspace / monitor tweaks** — `hypr/hyprland.lua`.

## Notes

- The bar and daemons write runtime state to `$XDG_RUNTIME_DIR` (`/run/user/<uid>/`),
  so nothing is pinned to a specific user id.
- Developed on **Arch Linux** with an AMD RX 9060 XT (RDNA4) dGPU and a 27" HiDPI
  display scaled 2×. Other monitors / GPUs should work; tweak the `monitor` and
  `vram` modules as needed.
