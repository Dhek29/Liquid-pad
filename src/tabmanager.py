"""
Tab manager for LiquidPad.
Handles multiple editor tabs with add/close/switch functionality.

Two critical design rules:
  1. self.active_tab_id  →  always a tab's unique ID, NEVER a list index.
  2. TabManager is the SOLE owner of glass_container.pack() calls.
     Editor._build() must NOT call pack() on glass_container.
"""

import tkinter as tk
import os


class TabManager:
    """Manages multiple editor tabs."""

    def __init__(self, parent, app):
        self.parent        = parent
        self.app           = app
        self.tabs          = []     # list of tab dicts
        self.active_tab_id = None   # ID of the currently visible tab (never an index)
        self.tab_bar       = None
        self.editor_frame  = None
        self._next_id      = 0      # monotonically increasing ID counter
        self._build()

    # ------------------------------------------------------------------ #
    #  ID helpers                                                          #
    # ------------------------------------------------------------------ #

    def _new_id(self):
        uid = self._next_id
        self._next_id += 1
        return uid

    def _find_index_by_id(self, tab_id):
        for i, tab in enumerate(self.tabs):
            if tab['id'] == tab_id:
                return i
        return -1

    def _get_active_index(self):
        return self._find_index_by_id(self.active_tab_id)

    def _get_tab_by_id(self, tab_id):
        idx = self._find_index_by_id(tab_id)
        return self.tabs[idx] if idx >= 0 else None

    def _get_active_tab(self):
        return self._get_tab_by_id(self.active_tab_id)

    # ------------------------------------------------------------------ #
    #  Build                                                               #
    # ------------------------------------------------------------------ #

    def _build(self):
        t = self.app.current_theme

        self.tab_bar = tk.Frame(self.parent, bg=t["bg"], height=35)
        self.tab_bar.pack(fill=tk.X, padx=20, pady=(5, 0))
        self.tab_bar.pack_propagate(False)

        self.add_btn = tk.Button(
            self.tab_bar, text="+",
            bg=t["accent"], fg=t["fg"],
            font=('Segoe UI', 12, 'bold'),
            relief=tk.FLAT, bd=0, padx=10,
            cursor='hand2',
            command=self.add_tab,
        )
        self.add_btn.pack(side=tk.RIGHT, padx=(5, 0))

        self.editor_frame = tk.Frame(self.parent, bg=t["bg"])
        self.editor_frame.pack(fill=tk.BOTH, expand=True)

        self._add_first_tab()

        self.parent.bind('<Control-Tab>',       lambda e: self.next_tab())
        self.parent.bind('<Control-Shift-Tab>', lambda e: self.prev_tab())

    def _add_first_tab(self):
        from editor import Editor
        editor = Editor(self.editor_frame, self.app.current_theme)
        uid = self._new_id()
        tab = {
            'id':        uid,
            'editor':    editor,
            'file':      None,
            'title':     "Untitled",
            'modified':  False,
            'btn_frame': None,
        }
        self.tabs.append(tab)
        self.active_tab_id = uid
        # TabManager packs the first editor — editor._build() does NOT
        editor.glass_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 0))
        self._rebuild_tab_bar()

    # ------------------------------------------------------------------ #
    #  Public tab operations                                               #
    # ------------------------------------------------------------------ #

    def add_tab(self, filepath=None, content=None):
        """Open a new tab, optionally pre-loading content or a file."""
        from editor import Editor
        editor = Editor(self.editor_frame, self.app.current_theme)

        if content:
            editor.set_text(content)
        elif filepath and os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                editor.set_text(f.read())

        uid = self._new_id()
        tab = {
            'id':        uid,
            'editor':    editor,
            'file':      filepath,
            'title':     os.path.basename(filepath) if filepath else "Untitled",
            'modified':  False,
            'btn_frame': None,
        }
        self.tabs.append(tab)

        # Switch to newly added tab (it is the last one right now)
        self._switch_to_index(len(self.tabs) - 1)
        self._rebuild_tab_bar()

        if hasattr(self.app, '_update_status'):
            self.app._update_status()

        return tab

    def close_tab(self, tab_id):
        """Close the tab identified by tab_id."""
        index = self._find_index_by_id(tab_id)
        if index < 0:
            return

        if len(self.tabs) <= 1:
            return  # never close the last tab

        tab = self.tabs[index]

        # Offer to save unsaved changes
        if tab['modified'] and tab['editor'].get_text().strip():
            from tkinter import messagebox
            answer = messagebox.askyesnocancel(
                "LiquidPad", f"Save changes to {tab['title']}?"
            )
            if answer is None:
                return
            if answer and hasattr(self.app, 'menubar'):
                self.app.menubar._save_tab(tab)

        # Destroy editor widget and remove from list
        tab['editor'].glass_container.destroy()
        self.tabs.pop(index)

        # ALWAYS call _switch_to_index after any close so that
        # pack_forget + pack run and tkinter redraws the layout.
        # Without this, closing a background tab makes all editors invisible.
        if self.active_tab_id == tab_id:
            # Closed tab was active → move to nearest neighbour
            self._switch_to_index(min(index, len(self.tabs) - 1))
        else:
            # Closed tab was in background → re-assert the active editor
            self._switch_to_index(self._get_active_index())

        self._rebuild_tab_bar()

        if hasattr(self.app, '_update_status'):
            self.app._update_status()

    def next_tab(self):
        if len(self.tabs) <= 1:
            return
        idx = (self._get_active_index() + 1) % len(self.tabs)
        self._switch_to_index(idx)
        self._rebuild_tab_bar()
        if hasattr(self.app, '_update_status'):
            self.app._update_status()

    def prev_tab(self):
        if len(self.tabs) <= 1:
            return
        idx = (self._get_active_index() - 1) % len(self.tabs)
        self._switch_to_index(idx)
        self._rebuild_tab_bar()
        if hasattr(self.app, '_update_status'):
            self.app._update_status()

    # ------------------------------------------------------------------ #
    #  Internal switch / rebuild                                           #
    # ------------------------------------------------------------------ #

    def _switch_to_index(self, index):
        """
        Hide ALL editors, show the one at *index*, record its ID.
        Uses consistent padx=20 so geometry never conflicts.
        This is the ONLY place active_tab_id is written.
        """
        if index < 0 or index >= len(self.tabs):
            return

        # Hide every editor first
        for tab in self.tabs:
            tab['editor'].glass_container.pack_forget()

        # Show the chosen editor with consistent padding
        self.active_tab_id = self.tabs[index]['id']   # store ID, not index!
        self.tabs[index]['editor'].glass_container.pack(
            fill=tk.BOTH, expand=True, padx=20, pady=(0, 0)
        )
        self.tabs[index]['editor'].text_area.focus_set()

    def _on_tab_click(self, tab_id):
        index = self._find_index_by_id(tab_id)
        if index >= 0:
            self._switch_to_index(index)
            self._rebuild_tab_bar()
            if hasattr(self.app, '_update_status'):
                self.app._update_status()

    def _rebuild_tab_bar(self):
        t = self.app.current_theme

        # Destroy ALL children of tab_bar except add_btn (including orphaned
        # frames from closed tabs already popped from self.tabs)
        for widget in self.tab_bar.winfo_children():
            if widget is not self.add_btn:
                widget.destroy()

        # Clear btn_frame refs on remaining tabs since we just destroyed them
        for tab in self.tabs:
            tab['btn_frame'] = None

        # Build one button-pair per tab
        for tab in self.tabs:
            is_active = (tab['id'] == self.active_tab_id)  # compare IDs!
            bg     = t["text_bg"] if is_active else t["accent"]
            fg     = t["fg"]      if is_active else t.get("line_fg", "#888888")
            prefix = "● " if tab['modified'] else ""
            tid    = tab['id']   # captured in lambda

            btn_frame = tk.Frame(self.tab_bar, bg=t["bg"])
            btn_frame.pack(side=tk.LEFT, padx=(1, 0))

            tk.Button(
                btn_frame,
                text=f" {prefix}{tab['title']} ",
                bg=bg, fg=fg,
                font=('Segoe UI', 9),
                relief=tk.FLAT, bd=0,
                padx=6, pady=4,
                cursor='hand2',
                command=lambda tid=tid: self._on_tab_click(tid),
            ).pack(side=tk.LEFT)

            close_btn = tk.Button(
                btn_frame,
                text='×',
                bg=bg, fg=fg,
                font=('Segoe UI', 10, 'bold'),
                relief=tk.FLAT, bd=0,
                padx=4, pady=4,
                cursor='hand2',
                command=lambda tid=tid: self.close_tab(tid),
            )
            close_btn.pack(side=tk.LEFT)
            close_btn.bind('<Enter>', lambda e, b=close_btn: b.configure(fg='#ff4444'))
            close_btn.bind('<Leave>', lambda e, b=close_btn, c=fg: b.configure(fg=c))

            tab['btn_frame'] = btn_frame

        # Keep "+" at the far right
        self.add_btn.pack_forget()
        self.add_btn.pack(side=tk.RIGHT, padx=(5, 0))

    # ------------------------------------------------------------------ #
    #  Public accessors                                                    #
    # ------------------------------------------------------------------ #

    def get_active_editor(self):
        tab = self._get_active_tab()
        return tab['editor'] if tab else None

    def get_active_file(self):
        tab = self._get_active_tab()
        return tab['file'] if tab else None

    def set_active_file(self, filepath):
        tab = self._get_active_tab()
        if tab:
            tab['file']     = filepath
            tab['title']    = os.path.basename(filepath) if filepath else "Untitled"
            tab['modified'] = False
            self._rebuild_tab_bar()

    def set_active_modified(self, modified=True):
        tab = self._get_active_tab()
        if tab:
            tab['modified'] = modified
            self._rebuild_tab_bar()

    def get_filename(self):
        tab = self._get_active_tab()
        return tab['title'] if tab else "Untitled"

    def get_full_filename(self):
        tab = self._get_active_tab()
        return (tab['file'] or "Untitled") if tab else "Untitled"

    def get_all_editors(self):
        return [tab['editor'] for tab in self.tabs]

    # ------------------------------------------------------------------ #
    #  Theme update                                                        #
    # ------------------------------------------------------------------ #

    def update_theme(self, theme):
        self.tab_bar.configure(bg=theme["bg"])
        self.add_btn.configure(bg=theme["accent"], fg=theme["fg"])
        self.editor_frame.configure(bg=theme["bg"])
        self._rebuild_tab_bar()