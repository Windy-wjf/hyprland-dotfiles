#!/usr/bin/env bash
#
# install.sh — install this Hyprland config onto your system.
#
# Copies the hypr/, waybar/, kitty/ and fcitx5/ trees into ~/.config/, rewrites the
# absolute paths the configs carry (they were captured from another machine, and
# Hyprland/waybar/hyprlock cannot expand $HOME themselves), installs the wallpaper
# and points hyprpaper at it. Overwrites any existing files with the same names
# (back up first if you care).
#
#   ./install.sh            install (asks nothing, overwrites)
#
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CFG="${XDG_CONFIG_HOME:-$HOME/.config}"
RT="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"
WALL_SRC="$SRC/assets/wallpaper.jpg"
WALL_DST="$HOME/Pictures/wallhaven-jev9xw.jpg"

# Paths baked into the configs when this repo was captured.
CAPTURED_HOME="/home/wjf"
CAPTURED_RUNTIME="/run/user/1000"

echo "==> Installing from: $SRC"
echo "==> Target:          $CFG"

# 0) Warn about missing commands instead of failing halfway through.
missing=()
for c in Hyprland waybar hyprpaper hyprlock hypridle python3 fuzzel kitty; do
  command -v "$c" >/dev/null 2>&1 || missing+=("$c")
done
if [[ ${#missing[@]} -gt 0 ]]; then
  echo "    !! not found: ${missing[*]} — the config will install but those parts won't run"
  echo "       (Arch: pacman -S hyprland waybar hyprpaper hyprlock hypridle python fuzzel kitty)"
fi
python3 -c 'import gi' 2>/dev/null || echo "    !! python-gobject missing — the waybar popups (popup.py) need it"
for c in grim slurp wf-recorder cliphist wl-copy brightnessctl playerctl ddcutil swaync-client hyprsunset; do
  command -v "$c" >/dev/null 2>&1 || echo "    !! optional tool missing: $c"
done

# 1) Copy each config tree into ~/.config/ (merging, not wiping).
for d in hypr waybar kitty fcitx5; do
  mkdir -p "$CFG/$d"
  cp -a "$SRC/$d/." "$CFG/$d/"
  echo "    installed $CFG/$d"
done
rm -rf "$CFG/waybar/__pycache__"

# 2) Re-home every absolute path the configs carry. Applies to all text files
#    under hypr/ and waybar/ — that includes waybar/config.jsonc, whose exec
#    strings call the scripts by absolute path (waybar has no variable expansion).
while IFS= read -r -d '' f; do
  sed -i -e "s|$CAPTURED_HOME|$HOME|g" -e "s|$CAPTURED_RUNTIME|$RT|g" "$f"
done < <(grep -rlIZ -e "$CAPTURED_HOME" -e "$CAPTURED_RUNTIME" "$CFG/hypr" "$CFG/waybar" "$CFG/kitty" "$CFG/fcitx5" 2>/dev/null || true)

# 3) Install the wallpaper and point hyprpaper at it (hyprpaper needs a literal
#    path). Swap it for anything you like, or let waybar/bing-wallpaper manage a
#    daily Bing image instead.
if [[ -f "$WALL_SRC" ]]; then
  mkdir -p "$HOME/Pictures"
  cp -a "$WALL_SRC" "$WALL_DST"
  sed -i -E "s|^([[:space:]]*path[[:space:]]*=).*|\1 $WALL_DST|" "$CFG/hypr/hyprpaper.conf"
  echo "    installed wallpaper -> $WALL_DST"
else
  echo "    (assets/wallpaper.jpg not found — leaving hyprpaper.conf alone)"
fi

# 4) Make the bar scripts executable even if the clone lost their mode bits.
chmod +x "$CFG"/waybar/* "$CFG"/hypr/bing-wallpaper 2>/dev/null || true

# 5) Sanity check: nothing should still point at the capture machine.
leftover="$(grep -rIl -e "$CAPTURED_HOME" -e "$CAPTURED_RUNTIME" "$CFG/hypr" "$CFG/waybar" 2>/dev/null || true)"
if [[ -n "$leftover" ]]; then
  echo "    !! still referencing $CAPTURED_HOME:"
  echo "$leftover" | sed 's|^|       |'
else
  echo "    paths rewritten for $HOME ($RT)"
fi

echo
echo "Done."
echo "  • Log out and log back in so waybar, the workspace daemons, hyprpaper,"
echo "    fcitx5, swaync and hypridle autostart cleanly."
echo "    (Or: 'hyprctl reload' + manually restart waybar.)"
echo "  • Optional: a Nerd Font (e.g. ttf-jetbrains-mono-nerd) for the bar icons,"
echo "    and 'hypr/bing-wallpaper --daemon' if you want the daily Bing image."
