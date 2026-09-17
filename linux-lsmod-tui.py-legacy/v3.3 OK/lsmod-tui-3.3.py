#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Linux Kernel Module Inspector (TUI)
# Copyright (C) 2026 brunonlinespace
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but uden any warranty; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import curses
import os
import subprocess
import sys


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
          modules.append({
              "name": name,
              "size": size,
              "instances": instances,
              "used_by": used_by,
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

  modules = get_loaded_modules()
  current_row = 0
  top_row = 0

  while True:
    stdscr.clear()
    h, w = stdscr.getmaxyx()

    # Layout dimensions
    list_width = int(w * 0.35)
    info_width = w - list_width - 1

    if h < 10 or w < 40:
      stdscr.addstr(0, 0, "Terminal window is too small!")
      stdscr.refresh()
      if stdscr.getch() == ord("q"):
        break
      continue

    # Title Bar
    stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
    stdscr.addstr(
        0,
        0,
        f" Linux Kernel Module Inspector ({len(modules)} loaded)".ljust(
            w - 1
        )[: w - 1],
    )
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

    # Draw Module Details (Right Pane via modinfo)
    stdscr.vline(1, list_width, curses.ACS_VLINE, h - 2)
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
        stdscr.addstr(2 + i, list_width + 2, line[: info_width - 3])

    # Footer instructions safely clamped
    footer = " [↑/↓] Navigate | [r] Refresh | [q] Quit "
    stdscr.attron(curses.color_pair(2))
    stdscr.addstr(h - 1, 0, footer.ljust(w - 1)[: w - 1])
    stdscr.attroff(curses.color_pair(2))

    stdscr.refresh()

    key = stdscr.getch()
    if key == ord("q") or key == ord("Q"):
      break
    elif key == curses.KEY_UP and current_row > 0:
      current_row -= 1
    elif key == curses.KEY_DOWN and current_row < len(modules) - 1:
      current_row += 1
    elif key == ord("r") or key == ord("R"):
      modules = get_loaded_modules()
      if current_row >= len(modules):
        current_row = max(0, len(modules) - 1)


if __name__ == "__main__":
  try:
    curses.wrapper(draw_menu)
  except KeyboardInterrupt:
    sys.exit(0)
