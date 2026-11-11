# Hyprland Config

A complete, self-contained Hyprland desktop built around **Hyprland + waybar**, tuned
for an AMD (RDNA4) laptop with a HiDPI display. This is the "core" of the setup: the
window manager, a custom waybar taskbar (Arch-logo app menu, dynamic workspaces,
CPU/GPU/battery monitors, weather, clipboard, screenshot, night mode), a Python
wallpaper picker, a daily Bing wallpaper daemon, and Chinese (fcitx5) input.

> **Status — portable.** Scripts use `$HOME` / `$XDG_RUNTIME_DIR` / `$XDG_CONFIG_HOME`
> (or `os.getuid()`), so they install for any user. Three files carry absolute paths
> because the programs reading them cannot expand `$HOME` — `hypr/hyprland.lua`,
> `hypr/hyprlock.conf` and `hypr/hyprpaper.conf`. `install.sh` rewrites those for your
> home directory.

## Layout

```
hypr/                 # Hyprland config (DPython Lua)
  hyprland.lua        #   main config — monitors, binds, autostart, window rules
  hyprpaper.conf      #   wallpaper (see "Customising")
  hyprlock.conf       #   lock screen
  hypridle.conf       #   auto-lock / power hooks
  bing-wallpaper      #   daily Bing wallpaper daemon (Py; also a one-shot updater)
waybar/               # waybar bar: config + style + the Python modules
  config.jsonc        #   bar layout (taskbar, workspaces, cpu/vram/battery/clock…)
  style.css           #   bar styling
  popup.py            #   GTK4 popover menus (volume / brightness / network / clock)
  cpu vram sysmon     #   Python status scripts (read /proc + the GPU)
  weather city        #   Open-Meteo weather module + the city file
  updates notif       #   pacman update count / swaync notification count
  night brightadj     #   hyprsunset night-mode toggle, brightness (DDC/CI + backlight)
  screenshot record   #   grim/slurp screenshots, wf-recorder screen recording
  clipmenu            #   cliphist + fuzzel clipboard history
  lockweather         #   weather string for hyprlock
  wsdaemon wsbar …    #   dynamic-workspace daemons / scripts
  archmenu            #   Arch-logo app menu (fuzzel --dmenu)
  wallpick            #   GTK wallpaper picker
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
- **hyprpaper** / **hyprlock** / **hypridle** — wallpaper, lock screen, auto-lock.
- **hyprsunset** — night mode (`waybar/night`).
- **swaync** — notification daemon (`waybar/notif`, autostarted).
- **hyprpolkitagent** — polkit prompt agent (autostarted).
- **fuzzel** — Arch-logo app menu and clipboard picker. It reads
  `~/.config/fuzzel/fuzzel.ini`; ship your own or it uses fuzzel defaults.
- **rofi** — the generic app launcher (`Super+R`).
- **nautilus** — the file manager (`$FILE_MANAGER`).
- **cliphist** + **wl-clipboard** — clipboard history (`waybar/clipmenu`, autostarted
  `wl-paste --watch cliphist store`).
- **grim** + **slurp** — screenshots (`waybar/screenshot`).
- **wf-recorder** — screen recording (`waybar/record`).
- **brightnessctl** / **ddcutil** — brightness keys and `waybar/brightadj`.
- **playerctl**, **wpctl** — XF86 media / volume binds.
- **pacman-contrib** — `checkupdates` for the update counter.
- **Open-Meteo** (no API key) — the weather module calls `api.open-meteo.com`.
- **Bing** (no API key) — `hypr/bing-wallpaper` fetches the daily image.

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

Then fix the absolute paths the configs carry (`/home/wjf` here) to point at your own
home: `hypr/hyprland.lua`, `hypr/hyprlock.conf` and the wallpaper `path` in
`hypr/hyprpaper.conf`.

After installing, **log out and log back in** so the autostarts (waybar, the
workspace daemons, hyprpaper, fcitx5, swaync, hypridle) start cleanly. A quick
`hyprctl reload` plus a manual (re)start of `waybar` works if you don't want to log
out.

## Customising

- **Wallpaper** — replace `assets/wallpaper.jpg` and re-run `install.sh`, or run
  `hypr/bing-wallpaper --daemon` for a fresh Bing image every day at 07:30
  (state lives in `~/.cache/bing-wallpaper/`).
- **City** — edit `waybar/weather.city` (one city name; the weather module falls back
  to `Shanghai` if the file is missing).
- **Apps shown in the bar** — `waybar/apps.json`, toggled via `appadd` / `appdel` / `appsync`.
- **Binds / workspace / monitor tweaks** — `hypr/hyprland.lua`.

## Keybinds (short list)

| Bind | Action |
|---|---|
| `Super + Return` | terminal (kitty) |
| `Super + R` | rofi launcher (the Arch menu is the bar's left-hand icon) |
| `Super + E` | file manager |
| `Super + 1…0` / `Super + Shift + 1…0` | switch / move window to workspace |
| `Super + W` | wallpaper picker |
| `Super + F` / `Super + V` / `Super + P` | fullscreen / float toggle / pseudo |
| `Super + L` | lock screen |
| `Super + M` | exit Hyprland |
| `Super + S` / `Super + Shift + S` | toggle / move to special workspace |
| `Super + click` / `Super + right-click` | drag / resize window |
| `Super + N` | night mode toggle (`waybar/night`) |
| `Print` / `Shift + Print` | screenshot region / full screen |
| `Super + Shift + R` | screen recording toggle |
| `Super + Shift + V` | clipboard history |
| `Super + /` | keybind cheat sheet (`popup.py keys`)|

## Notes

- The bar and daemons write runtime state to `$XDG_RUNTIME_DIR` (`/run/user/<uid>/`),
  so nothing is pinned to a specific user id.
- Developed on **Arch Linux** with an AMD RX 9060 XT (RDNA4) dGPU and a 27" HiDPI
  display scaled 2×. Other monitors / GPUs should work; tweak the `monitor` and
  `vram` modules as needed.
- `fcitx5/conf/` ships the Pinyin setup only; fcitx5 rewrites `profile` and the
  per-layout caches on first start.
