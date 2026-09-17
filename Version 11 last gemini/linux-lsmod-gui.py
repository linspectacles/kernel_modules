#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ==============================================================================
# Linux Kernel Module Inspector (GUI) in python
# Copyright (C) 2026 AI Collaborator / brunonlinespace
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# linux-lsmod-gui.py
# Version: 11
# ==============================================================================

import json
import os
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk


class KernelModuleGUI:

  def __init__(self, root):
    self.root = root
    self.root.title("Linux Kernel Module Inspector (v11)")
    self.root.geometry("1100x700")
    self.root.minsize(800, 500)

    # Configuration file path for theme preference persistence
    self.config_file = os.path.expanduser("~/.config/kmod_inspector_config.json")

    # Load persistent preference, defaulting to False (light mode)
    self.dark_mode = self.load_theme_preference()
    self.modules_data = []

    self.setup_styles()
    self.setup_ui()
    self.load_modules()

  def load_theme_preference(self):
    """Loads the last saved dark mode preference from a local json config file."""
    try:
      if os.path.exists(self.config_file):
        with open(self.config_file, "r") as f:
          data = json.load(f)
          return data.get("dark_mode", False)
    except Exception:
      pass
    return False

  def save_theme_preference(self):
    """Saves the current dark mode preference to a local json config file."""
    try:
      os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
      with open(self.config_file, "w") as f:
        json.dump({"dark_mode": self.dark_mode}, f)
    except Exception as e:
      print(f"Warning: Could not save theme preference: {e}", file=sys.stderr)

  def setup_styles(self):
    self.style = ttk.Style()
    if "clam" in self.style.theme_names():
      self.style.theme_use("clam")

  def setup_ui(self):
    self.main_frame = ttk.Frame(self.root, padding=12)
    self.main_frame.pack(fill=tk.BOTH, expand=True)

    # --- Top Dashboard / Header Frame (Permanent Counter & Toggles) ---
    dash_frame = ttk.Frame(self.main_frame)
    dash_frame.pack(fill=tk.X, pady=(0, 10))

    self.stats_label = ttk.Label(
        dash_frame, text="📊 Total Loaded Modules: 0", font=("Segoe UI", 11, "bold")
    )
    self.stats_label.pack(side=tk.LEFT, padx=(0, 15))

    self.theme_btn = ttk.Button(
        dash_frame, text="🌙 Dark Mode", command=self.toggle_theme
    )
    self.theme_btn.pack(side=tk.RIGHT)

    self.refresh_btn = ttk.Button(
        dash_frame, text="🔄 Refresh List", command=self.load_modules
    )
    self.refresh_btn.pack(side=tk.RIGHT, padx=6)

    # --- Search Filter & Category Dropdown Bar ---
    filter_bar = ttk.Frame(self.main_frame)
    filter_bar.pack(fill=tk.X, pady=(0, 10))

    # Search Bar
    ttk.Label(filter_bar, text="🔍 Search:", font=("Segoe UI", 10, "bold")).pack(
        side=tk.LEFT, padx=(0, 6)
    )
    self.search_var = tk.StringVar()
    self.search_var.trace_add("write", self.filter_modules)
    self.search_entry = ttk.Entry(
        filter_bar, textvariable=self.search_var, width=22, font=("Segoe UI", 10)
    )
    self.search_entry.pack(side=tk.LEFT, padx=(0, 15))

    # Category Filter Dropdown
    ttk.Label(
        filter_bar, text="📂 Category:", font=("Segoe UI", 10, "bold")
    ).pack(side=tk.LEFT, padx=(0, 6))
    
    self.category_var = tk.StringVar(value="All Categories")
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
    self.category_dropdown = ttk.Combobox(
        filter_bar,
        textvariable=self.category_var,
        values=categories,
        state="readonly",
        width=20,
    )
    self.category_dropdown.pack(side=tk.LEFT, padx=(0, 10))
    self.category_dropdown.bind("<<ComboboxSelected>>", self.filter_modules)

    self.filter_status_lbl = ttk.Label(
        filter_bar, text="", font=("Segoe UI", 9, "italic")
    )
    self.filter_status_lbl.pack(side=tk.LEFT, padx=5)

    # --- Main Split Window (Resizable List + Details) ---
    self.paned_window = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
    self.paned_window.pack(fill=tk.BOTH, expand=True)

    # Left Pane: Module Table (Treeview)
    left_frame = ttk.Frame(self.paned_window)
    self.paned_window.add(left_frame, weight=1)

    columns = ("name", "category", "size", "used_by")
    self.tree = ttk.Treeview(
        left_frame, columns=columns, show="headings", selectmode="browse"
    )

    self.tree.heading(
        "name", text="Module Name", command=lambda: self.sort_by("name")
    )
    self.tree.heading(
        "category", text="Category", command=lambda: self.sort_by("category")
    )
    self.tree.heading(
        "size", text="Size", command=lambda: self.sort_by("size")
    )
    self.tree.heading(
        "used_by", text="Used By", command=lambda: self.sort_by("used_by")
    )

    self.tree.column("name", width=160, anchor=tk.W)
    self.tree.column("category", width=140, anchor=tk.W)
    self.tree.column("size", width=80, anchor=tk.E)
    self.tree.column("used_by", width=80, anchor=tk.W)

    tree_scroll = ttk.Scrollbar(
        left_frame, orient=tk.VERTICAL, command=self.tree.yview
    )
    self.tree.configure(yscroll=tree_scroll.set)

    self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    self.tree.bind("<<TreeviewSelect>>", self.on_module_select)

    # Right Pane: Module Metadata (modinfo)
    right_frame = ttk.Frame(self.paned_window)
    self.paned_window.add(right_frame, weight=2)

    self.detail_label = ttk.Label(
        right_frame,
        text="📌 Module Details (modinfo)",
        font=("Segoe UI", 11, "bold"),
    )
    self.detail_label.pack(anchor=tk.W, pady=(0, 6))

    self.info_text = scrolledtext.ScrolledText(
        right_frame, wrap=tk.WORD, font=("Consolas", 10), bd=1, relief=tk.SOLID
    )
    self.info_text.pack(fill=tk.BOTH, expand=True)

    self.info_text.tag_config("key", font=("Consolas", 10, "bold"))
    self.info_text.tag_config("value")

    # --- Bottom Status Bar ---
    self.status_var = tk.StringVar(value="Ready — Select a module to inspect properties.")
    self.status_lbl = ttk.Label(
        self.main_frame,
        textvariable=self.status_var,
        relief=tk.FLAT,
        anchor=tk.W,
        padding=4,
        font=("Segoe UI", 9, "italic"),
    )
    self.status_lbl.pack(fill=tk.X, pady=(8, 0))

    # Apply the initial theme matching saved preference
    self.apply_theme()

  def toggle_theme(self):
    self.dark_mode = not self.dark_mode
    self.save_theme_preference()
    self.apply_theme()

  def apply_theme(self):
    if self.dark_mode:
      bg_color = "#181818"
      fg_color = "#f0f0f0"
      accent_color = "#007acc"
      select_bg = "#004885"
      text_bg = "#1e1e1e"
      status_bg = "#252526"

      self.theme_btn.config(text="☀️ Light Mode")
      self.style.configure(
          ".", background=bg_color, foreground=fg_color, fieldbackground=text_bg
      )
      self.style.configure("TFrame", background=bg_color, foreground=fg_color)
      self.style.configure("TLabel", background=bg_color, foreground=fg_color)
      self.style.configure("TEntry", background=text_bg, foreground=fg_color)
      self.style.configure("TCombobox", background=text_bg, foreground=fg_color)
      self.style.configure(
          "TButton",
          background="#333333",
          foreground=fg_color,
          bordercolor="#555555",
      )
      self.style.map(
          "TButton",
          background=[("active", accent_color)],
          foreground=[("active", "#ffffff")],
      )

      self.style.configure(
          "Treeview",
          background=text_bg,
          foreground=fg_color,
          fieldbackground=text_bg,
          borderwidth=0,
          rowheight=24,
      )
      self.style.configure(
          "Treeview.Heading",
          background="#2d2d2d",
          foreground="#ffffff",
          font=("Segoe UI", 9, "bold"),
      )
      self.style.map(
          "Treeview",
          background=[("selected", select_bg)],
          foreground=[("selected", "#ffffff")],
      )

      self.info_text.config(
          bg=text_bg, fg="#9cdcfe", insertbackground="#ffffff"
      )
      self.info_text.tag_config("key", foreground="#4ec9b0", font=("Consolas", 10, "bold"))
      self.info_text.tag_config("value", foreground="#ce9178")

      self.status_lbl.config(background=status_bg, foreground="#b5cea8")
      self.root.configure(bg=bg_color)
    else:
      bg_color = "#f5f6f8"
      fg_color = "#111111"
      accent_color = "#0066cc"
      select_bg = "#0066cc"
      text_bg = "#ffffff"
      status_bg = "#e4e7eb"

      self.theme_btn.config(text="🌙 Dark Mode")
      self.style.configure(
          ".", background=bg_color, foreground=fg_color, fieldbackground=text_bg
      )
      self.style.configure("TFrame", background=bg_color, foreground=fg_color)
      self.style.configure("TLabel", background=bg_color, foreground=fg_color)
      self.style.configure(
          "TButton", background="#e2e8f0", foreground=fg_color
      )
      self.style.map(
          "TButton",
          background=[("active", accent_color)],
          foreground=[("active", "#ffffff")],
      )

      self.style.configure(
          "Treeview",
          background=text_bg,
          foreground=fg_color,
          fieldbackground=text_bg,
          borderwidth=1,
          rowheight=24,
      )
      self.style.configure(
          "Treeview.Heading",
          background="#e2e8f0",
          foreground="#1a202c",
          font=("Segoe UI", 9, "bold"),
      )
      self.style.map(
          "Treeview",
          background=[("selected", select_bg)],
          foreground=[("selected", "#ffffff")],
      )

      self.info_text.config(
          bg=text_bg, fg="#1f2937", insertbackground="#000000"
      )
      self.info_text.tag_config("key", foreground="#005fb8", font=("Consolas", 10, "bold"))
      self.info_text.tag_config("value", foreground="#222222")

      self.status_lbl.config(background=status_bg, foreground="#2d3748")
      self.root.configure(bg=bg_color)

  def classify_module(self, name):
    name_lower = name.lower()
    
    if any(k in name_lower for k in ["snd", "sound", "audio", "codec", "dsp"]):
      return "Audio / Sound"
    elif any(k in name_lower for k in ["net", "eth", "wifi", "wlan", "wireless", "bluetooth", "bt", "ipv", "nf_", "cfg80211"]):
      return "Network / Wireless"
    elif any(k in name_lower for k in ["drm", "gpu", "amdgpu", "i915", "nouveau", "nvidia", "display", "fb"]):
      return "Graphics / Display"
    elif any(k in name_lower for k in ["ext4", "btrfs", "xfs", "fat", "vfat", "fs_", "scsi", "nvme", "ata", "usb-storage", "sda"]):
      return "Storage / Filesystems"
    elif any(k in name_lower for k in ["usb", "hid", "input", "evdev", "keyboard", "mouse", "joy"]):
      return "USB / Input Devices"
    elif any(k in name_lower for k in ["cpu", "intel", "amd", "acpi", "thermal", "power", "sched", "core"]):
      return "CPU / Core / System"
    else:
      return "Other / Uncategorized"

  def load_modules(self):
    self.modules_data.clear()
    try:
      with open("/proc/modules", "r") as f:
        for line in f:
          parts = line.split()
          if parts:
            name = parts[0]
            size = int(parts[1])
            used_by = parts[3] if len(parts) > 3 else "-"
            category = self.classify_module(name)
            self.modules_data.append(
                {"name": name, "size": size, "used_by": used_by, "category": category}
            )

      total_count = len(self.modules_data)
      self.stats_label.config(text=f"📊 Total Loaded Modules: {total_count}")
      self.filter_modules()
      self.status_var.set(f"✨ Successfully refreshed and categorized modules.")
    except Exception as e:
      messagebox.showerror("Error", f"Failed to read /proc/modules:\n{e}")

  def filter_modules(self, *args):
    query = self.search_var.get().strip().lower()
    selected_category = self.category_var.get()

    # Clear tree
    for item in self.tree.get_children():
      self.tree.delete(item)

    count = 0
    for mod in self.modules_data:
      match_category = (selected_category == "All Categories" or mod["category"] == selected_category)
      match_query = (query in mod["name"].lower() or query in mod["used_by"].lower())

      if match_category and match_query:
        self.tree.insert(
            "",
            tk.END,
            values=(mod["name"], mod["category"], f"{mod['size']:,}", mod["used_by"]),
        )
        count += 1

    if query or selected_category != "All Categories":
      self.filter_status_lbl.config(text=f"(Showing {count} of {len(self.modules_data)} modules)")
    else:
      self.filter_status_lbl.config(text="")

  def on_module_select(self, event):
    selected_item = self.tree.selection()
    if not selected_item:
      return

    item_values = self.tree.item(selected_item[0])["values"]
    mod_name = item_values[0]

    self.info_text.config(state=tk.NORMAL)
    self.info_text.delete("1.0", tk.END)

    try:
      result = subprocess.run(
          ["modinfo", mod_name], capture_output=True, text=True, check=True
      )
      
      for line in result.stdout.splitlines():
        if ":" in line:
          key, val = line.split(":", 1)
          self.info_text.insert(tk.END, key + ":", "key")
          self.info_text.insert(tk.END, val + "\n", "value")
        else:
          self.info_text.insert(tk.END, line + "\n", "value")

      self.status_var.set(f"📌 Auditing metadata for module: [{mod_name}]")
    except subprocess.CalledProcessError as e:
      self.info_text.insert(
          tk.END, f"Error getting metadata for '{mod_name}':\n{e.stderr}"
      )
    except Exception as e:
      self.info_text.insert(tk.END, f"Unexpected error: {str(e)}")

  def sort_by(self, col):
    reverse = getattr(self, f"_sort_{col}_reverse", False)

    if col == "size":
      self.modules_data.sort(key=lambda x: x["size"], reverse=reverse)
    else:
      self.modules_data.sort(key=lambda x: x[col].lower(), reverse=reverse)

    setattr(self, f"_sort_{col}_reverse", not reverse)
    self.filter_modules()


if __name__ == "__main__":
  root = tk.Tk()
  app = KernelModuleGUI(root)
  root.mainloop()
