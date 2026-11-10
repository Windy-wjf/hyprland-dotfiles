#!/usr/bin/env bash
#
# install.sh — install this Hyprland config onto your system.
#
# Copies the hypr/, waybar/, kitty/ and fcitx5/ trees into ~/.config/, installs the
# wallpaper, and rewrites the one absolute path hyprpaper needs. Overwrites any
# existing files with the same names (back up first if you care).
#
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CFG="$HOME/.config"
WALL_SRC="$SRC/assets/wallpaper.jpg"
WALL_DST="$HOME/Pictures/wallhaven-jev9xw.jpg"

echo "==> Installing from: $SRC"
echo "==> Target:          $CFG"

# 1) Copy each config tree into ~/.config/.
for d in hypr waybar kitty fcitx5; do
  mkdir -p "$CFG/$d"
  cp -a "$SRC/$d/." "$CFG/$d/"
  echo "    installed $CFG/$d"
done

# 2) Install the wallpaper and point hyprpaper at it.
#    hyprpaper cannot expand $HOME, so rewrite the absolute path to this home.
if [[ -f "$WALL_SRC" ]]; then
  mkdir -p "$HOME/Pictures"
  cp -a "$WALL_SRC" "$WALL_DST"
  sed -i "s|/home/wjf|$HOME|g" "$CFG/hypr/hyprpaper.conf"
  echo "    installed wallpaper -> $WALL_DST"
else
  echo "    (assets/wallpaper.jpg not found — skipping wallpaper install)"
fi

echo
echo "Done."
echo "  • Log out and log back in so waybar, the workspace daemons, hyprpaper and"
echo "    fcitx5 autostart cleanly. (Or: 'hyprctl reload' + manually restart waybar.)"
