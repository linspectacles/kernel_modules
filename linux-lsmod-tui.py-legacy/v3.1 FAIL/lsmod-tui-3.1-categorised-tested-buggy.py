#!/usr/bin/env python3
import curses
import os
import subprocess
import sys


def classify_module(name):
  name_lower = name.lower()
  if any(k in name_lower for k in ["snd", "sound", "audio", "codec", "dsp"]):
    return "Audio / Sound"
  elif any(
      k in name_lower
      for k in [
          "net",
          "eth",
          "wifi",
          "wlan",
          "wireless",
          "bluetooth",
          "bt",
          "ipv",
          "nf_",
          "cfg80211",
      ]
  ):
    return "Network / Wireless"
  elif any(
      k in name_lower
      for k in [
          "drm",
          "gpu",
          "amdgpu",
          "i915",
          "nouveau",
          "nvidia",
          "display",
          "fb",
      ]
  ):
    return "Graphics / Display"
  elif any(
      k in name_lower
      for k in [
          "ext4",
          "btrfs",
          "xfs",
          "fat",
          "vfat",
          "fs_",
          "scsi",
          "nvme",
          "ata",
          "usb-storage",
          "sda",
      ]
  ):
    return "Storage / Filesystems"
  elif any(
      k in name_lower
      for k in ["usb", "hid", "input", "evdev", "keyboard", "mouse", "joy"]
  ):
    return "USB / Input Devices"
  elif any(
      k in name_lower
      for k in [
          "cpu",
          "intel",
          "amd",
          "acpi",
          "thermal",
          "power",
          "sched",
          "core",
      ]
  ):
    return "CPU / Core / System"
  else:
    return "Other / Uncategorized"


def get_loaded_modules():
  modules = []
  try:
    with open("/proc/modules", "r") as f:
      for line in f:
        parts = line.split()
        if parts:
          name = parts[0]
          size = parts[1]
          instances = parts[2]
          used_by = parts[3] if len(parts) > 3 else ""
          category = classify_module(name)
          modules.append({
              "name": name,
              "size": size,
              "instances": instances,
              "used_by": used_by,
              "category": category,
          })
  except Exception as e:
    pass
  return sorted(modules, key=lambda x: x["name"])


def get_mod_info(mod_name):
  try:
    result = subprocess.run(
        ["modinfo", mod_name], capture_output=True, text=True, check=True
    )
    return result.stdout
  except subprocess.CalledProcessError:
    return "Details unavailable for this module."


def draw_menu(stdscr):
  curses.curs_set(0)
  stdscr.keypad(1)

  # Colors
  curses.start_color()
  curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)  # Highlight bar
  curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Headers
  curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Filter indicator

  all_modules = get_loaded_modules()
  categories = [
      "All Categories",
      "Audio / Sound",
      "Network / Wireless",
      "Graphics / Display",
      "Storage / Filesystems",
      "USB / Input Devices",
      "CPU / Core / System",
      "Other / Uncategorized",
  ]
  current_cat_idx = 0
  
  current_row = 0
  top_row = 0

  while True:
    # Filter modules based on selected category
    selected_cat = categories[current_cat_idx]
    if selected_cat == "All Categories":
      modules = all_modules
    else:
      modules = [m for m in all_modules if m["category"] == selected_cat]

    if current_row >= len(modules):
      current_row = max(0, len(modules) - 1)

    stdscr.erase()
    h, w = stdscr.getmaxyx()

    # Layout dimensions
    list_width = int(w * 0.40)
    info_width = w - list_width - 1

    if h < 10 or w < 50:
      stdscr.addstr(0, 0, "Terminal window is too small!")
      stdscr.refresh()
      if stdscr.getch() == ord("q"):
        break
      continue

    # Title Bar
    title_str = f" Linux Kernel Module Inspector [{selected_cat}] ({len(modules)}/{len(all_modules)}) "
    stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
    stdscr.addstr(0, 0, title_str.ljust(w - 1)[: w - 1])
    stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)

    # Draw Module List (Left Pane)
    max_display_rows = h - 4
    if current_row < top_row:
      top_row = current_row
    elif current_row >= top_row + max_display_rows:
      top_row = current_row - max_display_rows + 1

    for idx in range(top_row, min(top_row + max_display_rows, len(modules))):
      y_pos = 2 + (idx - top_row)
      mod_item = modules[idx]
      line_str = f" {mod_item['name']}".ljust(list_width - 1)

      if idx == current_row:
        stdscr.attron(curses.color_pair(1))
        stdscr.addstr(y_pos, 0, line_str[:list_width])
        stdscr.attroff(curses.color_pair(1))
      else:
        stdscr.addstr(y_pos, 0, line_str[:list_width])

    if not modules:
      stdscr.addstr(2, 2, "(No modules in category)")

    # Draw Module Details (Right Pane via modinfo)
    try:
      stdscr.vline(1, list_width, curses.ACS_VLINE, h - 2)
    except curses.error:
      pass

    stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
    stdscr.addstr(
        1,
        list_width + 2,
        " Module Metadata (modinfo): ".ljust(info_width - 2)[: info_width - 2],
    )
    stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)

    if modules:
      selected_mod = modules[current_row]["name"]
      info_text = get_mod_info(selected_mod)
      info_lines = info_text.split("\n")

      for i, line in enumerate(info_lines[: h - 5]):
        safe_line = line[: info_width - 3].ljust(info_width - 3)
        try:
          stdscr.addstr(2 + i, list_width + 2, safe_line)
        except curses.error:
          pass

    # Footer instructions safely clamped
    footer = " [Tab] Cycle Category | [↑/↓] Navigate | [r] Refresh | [q] Quit "
    stdscr.attron(curses.color_pair(3) | curses.A_BOLD)
    stdscr.addstr(h - 1, 0, footer.ljust(w - 1)[: w - 1])
    stdscr.attroff(curses.color_pair(3) | curses.A_BOLD)

    stdscr.refresh()

    key = stdscr.getch()
    if key == ord("q") or key == ord("Q"):
      break
    elif key == curses.KEY_UP and current_row > 0:
      current_row -= 1
    elif key == curses.KEY_DOWN and current_row < len(modules) - 1:
      current_row += 1
    elif key == 9:  # Tab key cycles through categories
      current_cat_idx = (current_cat_idx + 1) % len(categories)
      current_row = 0
      top_row = 0
    elif key == ord("r") or key == ord("R"):
      all_modules = get_loaded_modules()
      current_row = 0
      top_row = 0


if __name__ == "__main__":
  try:
    curses.wrapper(draw_menu)
  except KeyboardInterrupt:
    sys.exit(0)