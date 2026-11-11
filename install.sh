#!/usr/bin/env bash
#
# install.sh — install this Hyprland config onto your system.
#
# Copies the hypr/, waybar/, kitty/ and fcitx5/ trees into ~/.config/, installs the
# wallpaper and points hyprpaper at it, and rewrites the absolute source paths that
# hyprland.lua / hyprlock.conf / hyprpaper.conf carry. Overwrites any existing files
# with the same names (back up first if you care).
#
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CFG="$HOME/.config"
WALL_SRC="$SRC/assets/wallpaper.jpg"
WALL_DST="$HOME/Pictures/wallhaven-jev9xw.jpg"

# The repository was captured from a machine whose $HOME is /home/wjf. Every path
# in the configs below is absolute because the programs cannot expand $HOME, so
# they are rewritten here for the user doing the install.
CAPTURED_HOME="/home/wjf"

echo "==> Installing from: $SRC"
echo "==> Target:          $CFG"

# 1) Copy each config tree into ~/.config/.
for d in hypr waybar kitty fcitx5; do
  mkdir -p "$CFG/$d"
  cp -a "$SRC/$d/." "$CFG/$d/"
  echo "    installed $CFG/$d"
done

# 2) Re-home the configs that carry absolute paths.
for f in hypr/hyprland.lua hypr/hyprlock.conf hypr/hyprpaper.conf; do
  [[ -f "$CFG/$f" ]] && sed -i "s|$CAPTURED_HOME|$HOME|g" "$CFG/$f"
done

# 3) Install the wallpaper and point hyprpaper at it. hyprpaper cannot expand
#    $HOME, so the path has to be literal. (Swap it for anything you like, or let
#    waybar/bing-wallpaper manage a daily Bing wallpaper instead.)
if [[ -f "$WALL_SRC" ]]; then
  mkdir -p "$HOME/Pictures"
  cp -a "$WALL_SRC" "$WALL_DST"
  sed -i -E "s|^([[:space:]]*path[[:space:]]*=).*|\1 $WALL_DST|" "$CFG/hypr/hyprpaper.conf"
  echo "    installed wallpaper -> $WALL_DST (set in hyprpaper.conf)"
else
  echo "    (assets/wallpaper.jpg not found — skipping wallpaper install)"
fi

# 4) Drop runtime caches that must never be shipped.
rm -rf "$CFG/waybar/__pycache__"

echo
echo "Done."
echo "  • Log out and log back in so waybar, the workspace daemons, hyprpaper and"
echo "    fcitx5 autostart cleanly. (Or: 'hyprctl reload' + manually restart waybar.)"
